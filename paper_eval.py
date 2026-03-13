from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
UPSTREAM_ROOT = REPO_ROOT / "third_party" / "upstream-edm"
PAPER_GENERATE_PATH = REPO_ROOT / "paper_generate.py"
PAPER_RESULTS_PATH = REPO_ROOT / "paper_results.tsv"
LOCAL_REF_PATH = REPO_ROOT / "assets" / "fid_refs" / "cifar10-32x32.npz"
REMOTE_REF_URL = "https://nvlabs-fi-cdn.nvidia.com/edm/fid-refs/cifar10-32x32.npz"
LOCAL_TARGETS = {
    "cond": REPO_ROOT / "assets" / "checkpoints" / "edm-cifar10-32x32-cond-vp.pkl",
    "uncond": REPO_ROOT / "assets" / "checkpoints" / "edm-cifar10-32x32-uncond-vp.pkl",
}
REMOTE_TARGETS = {
    "cond": "https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/edm-cifar10-32x32-cond-vp.pkl",
    "uncond": "https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/edm-cifar10-32x32-uncond-vp.pkl",
}
LEGACY_RESULTS_HEADER = (
    "commit\ttarget\tsteps\tgpus\tseed_block_0\tseed_block_1\tseed_block_2\tfid_min\truntime_s\tcheckpoint\tref\n"
)
RESULTS_HEADER = (
    "commit\tsampler\ttarget\tsteps\tgpus\tseed_block_0\tseed_block_1\tseed_block_2\tfid_min\truntime_s\tcheckpoint\tref\n"
)


@dataclass(frozen=True)
class SeedBlock:
    start: int
    end: int

    def as_cli_value(self) -> str:
        return f"{self.start}-{self.end}"

    def as_label(self) -> str:
        return f"{self.start}_{self.end}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a paper-comparable EDM evaluation via the local paper generator and upstream FID.")
    parser.add_argument("--target", choices=sorted(REMOTE_TARGETS), required=True)
    parser.add_argument("--sampler", choices=("heun", "euler", "research"), default="research")
    parser.add_argument("--steps", type=int, default=18, help="Official EDM paper setting uses 18 steps.")
    parser.add_argument("--gpus", type=int, default=1, help="Number of GPUs for torch.distributed.run.")
    parser.add_argument("--batch-size", type=int, default=64, help="Per-process batch size passed to upstream scripts.")
    parser.add_argument("--repeats", type=int, default=3, help="Number of 50K seed blocks. Paper protocol uses 3.")
    parser.add_argument("--block-size", type=int, default=50_000, help="Images per seed block. Paper protocol uses 50000.")
    parser.add_argument("--seed-start", type=int, default=0, help="First seed for the first block.")
    parser.add_argument("--checkpoint", default="", help="Override the default checkpoint path or URL.")
    parser.add_argument("--ref", default="", help="Override the default reference stats path or URL.")
    parser.add_argument(
        "--outdir",
        default=str(REPO_ROOT / "artifacts" / "paper_eval"),
        help="Root directory for generated images and summaries.",
    )
    parser.add_argument("--python", default=sys.executable, help="Python executable used to launch upstream scripts.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    return parser.parse_args()


def current_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "nogit"
    commit = completed.stdout.strip()
    return commit or "nogit"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def log_field(name: str, value: object) -> None:
    print(f"{name}: {value}", flush=True)


def seed_blocks(*, seed_start: int, repeats: int, block_size: int) -> list[SeedBlock]:
    blocks = []
    for index in range(repeats):
        start = seed_start + index * block_size
        end = start + block_size - 1
        blocks.append(SeedBlock(start=start, end=end))
    return blocks


def distributed_prefix(python_executable: str, gpus: int) -> list[str]:
    if gpus < 1:
        raise ValueError("gpus must be at least 1")
    return [
        python_executable,
        "-m",
        "torch.distributed.run",
        "--standalone",
        "--nproc_per_node",
        str(gpus),
    ]


def default_checkpoint_for_target(target: str) -> str:
    local_path = LOCAL_TARGETS[target]
    if local_path.exists():
        return str(local_path)
    return REMOTE_TARGETS[target]


def default_ref() -> str:
    if LOCAL_REF_PATH.exists():
        return str(LOCAL_REF_PATH)
    return REMOTE_REF_URL


def build_generate_command(
    *,
    python_executable: str,
    gpus: int,
    sampler: str,
    outdir: Path,
    block: SeedBlock,
    checkpoint: str,
    steps: int,
    batch_size: int,
) -> list[str]:
    return distributed_prefix(python_executable, gpus) + [
        str(PAPER_GENERATE_PATH),
        "--outdir",
        str(outdir),
        "--seeds",
        block.as_cli_value(),
        "--subdirs",
        "--sampler",
        sampler,
        "--steps",
        str(steps),
        "--batch",
        str(batch_size),
        "--network",
        checkpoint,
    ]


def build_fid_command(
    *,
    python_executable: str,
    gpus: int,
    upstream_root: Path,
    images_path: Path,
    ref: str,
    batch_size: int,
    num_expected: int,
) -> list[str]:
    return distributed_prefix(python_executable, gpus) + [
        str(upstream_root / "fid.py"),
        "calc",
        "--images",
        str(images_path),
        "--ref",
        ref,
        "--num",
        str(num_expected),
        "--batch",
        str(batch_size),
    ]


def run_command(
    command: list[str],
    *,
    dry_run: bool,
    label: str,
) -> subprocess.CompletedProcess[str] | None:
    log_field(f"{label}_command", " ".join(command))
    log_field(f"{label}_start_time_utc", utc_now_iso())
    if dry_run:
        return None
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    log_field(f"{label}_end_time_utc", utc_now_iso())
    log_field(f"{label}_runtime_s", f"{time.perf_counter() - start:.1f}")
    return completed


def parse_fid(stdout: str) -> float:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if re.fullmatch(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", candidate):
            return float(candidate)
    raise ValueError(f"Unable to parse FID from stdout:\n{stdout}")


def ensure_upstream_repo() -> None:
    if not PAPER_GENERATE_PATH.exists():
        raise FileNotFoundError(f"Local paper generator not found at {PAPER_GENERATE_PATH}")
    if not (UPSTREAM_ROOT / "fid.py").exists() or not (UPSTREAM_ROOT / "generate.py").exists():
        raise FileNotFoundError(f"Upstream EDM repo not found at {UPSTREAM_ROOT}")


def ensure_results_file() -> None:
    if not PAPER_RESULTS_PATH.exists():
        PAPER_RESULTS_PATH.write_text(RESULTS_HEADER, encoding="utf-8")
        return

    lines = PAPER_RESULTS_PATH.read_text(encoding="utf-8").splitlines()
    if not lines:
        PAPER_RESULTS_PATH.write_text(RESULTS_HEADER, encoding="utf-8")
        return

    header = lines[0] + "\n"
    if header == RESULTS_HEADER:
        return
    if header != LEGACY_RESULTS_HEADER:
        raise ValueError(f"Unexpected paper_results.tsv header: {header.rstrip()}")

    migrated = [RESULTS_HEADER]
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 11:
            raise ValueError(f"Unexpected legacy paper_results.tsv row: {line}")
        parts.insert(1, "heun")
        migrated.append("\t".join(parts) + "\n")
    PAPER_RESULTS_PATH.write_text("".join(migrated), encoding="utf-8")


def validate_sampler_target(*, sampler: str, target: str) -> None:
    if sampler != "research":
        return
    from sample import research_supports_target

    if not research_supports_target(target):
        raise ValueError(f"Sampler {sampler} is not enabled for target {target}.")


def append_result_row(
    *,
    commit: str,
    sampler: str,
    target: str,
    steps: int,
    gpus: int,
    block_fids: list[float],
    runtime_s: float,
    checkpoint: str,
    ref: str,
) -> None:
    ensure_results_file()
    row = [
        commit,
        sampler,
        target,
        str(steps),
        str(gpus),
        *(f"{value:.4f}" for value in block_fids),
        f"{min(block_fids):.4f}",
        f"{runtime_s:.1f}",
        checkpoint,
        ref,
    ]
    with PAPER_RESULTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\t".join(row) + "\n")


def main() -> int:
    args = parse_args()
    ensure_upstream_repo()
    validate_sampler_target(sampler=args.sampler, target=args.target)
    if args.repeats != 3:
        raise ValueError("paper_eval.py currently records the official 3-run protocol only.")
    checkpoint = args.checkpoint or default_checkpoint_for_target(args.target)
    ref = args.ref or default_ref()
    output_root = Path(args.outdir) / args.sampler / args.target / f"steps_{args.steps}"
    output_root.mkdir(parents=True, exist_ok=True)
    blocks = seed_blocks(seed_start=args.seed_start, repeats=args.repeats, block_size=args.block_size)
    block_fids: list[float] = []
    start = time.perf_counter()
    log_field("start_time_utc", utc_now_iso())
    log_field("commit", current_commit())
    log_field("sampler", args.sampler)
    log_field("target", args.target)
    log_field("steps", args.steps)
    log_field("gpus", args.gpus)

    for index, block in enumerate(blocks):
        block_label = f"block_{index}"
        block_start = time.perf_counter()
        log_field(f"{block_label}_start_time_utc", utc_now_iso())
        log_field(f"{block_label}_seeds", block.as_cli_value())
        block_dir = output_root / f"seeds_{block.as_label()}"
        generate_command = build_generate_command(
            python_executable=args.python,
            gpus=args.gpus,
            sampler=args.sampler,
            outdir=block_dir,
            block=block,
            checkpoint=checkpoint,
            steps=args.steps,
            batch_size=args.batch_size,
        )
        fid_command = build_fid_command(
            python_executable=args.python,
            gpus=args.gpus,
            upstream_root=UPSTREAM_ROOT,
            images_path=block_dir,
            ref=ref,
            batch_size=args.batch_size,
            num_expected=args.block_size,
        )
        generate_result = run_command(generate_command, dry_run=args.dry_run, label=f"{block_label}_generate")
        fid_result = run_command(fid_command, dry_run=args.dry_run, label=f"{block_label}_fid")
        if args.dry_run:
            continue
        if generate_result is not None and generate_result.stdout.strip():
            print(generate_result.stdout.strip(), flush=True)
        if fid_result is not None and fid_result.stdout.strip():
            print(fid_result.stdout.strip(), flush=True)
            fid_value = parse_fid(fid_result.stdout)
            block_fids.append(fid_value)
            log_field(f"fid_block_{index}", f"{fid_value:.4f}")
        log_field(f"{block_label}_end_time_utc", utc_now_iso())
        log_field(f"{block_label}_runtime_s", f"{time.perf_counter() - block_start:.1f}")

    if args.dry_run:
        return 0

    runtime_s = time.perf_counter() - start
    append_result_row(
        commit=current_commit(),
        sampler=args.sampler,
        target=args.target,
        steps=args.steps,
        gpus=args.gpus,
        block_fids=block_fids,
        runtime_s=runtime_s,
        checkpoint=checkpoint,
        ref=ref,
    )
    log_field("end_time_utc", utc_now_iso())
    print(f"sampler: {args.sampler}", flush=True)
    print(f"target: {args.target}", flush=True)
    print(f"steps: {args.steps}", flush=True)
    for index, fid in enumerate(block_fids):
        print(f"fid_block_{index}: {fid:.4f}", flush=True)
    print(f"fid_min: {min(block_fids):.4f}", flush=True)
    print(f"runtime_s: {runtime_s:.1f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
