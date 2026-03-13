from __future__ import annotations

import argparse
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import torch

from evaluate import SPLIT_SIZES, calc_frontier, frechet_distance, load_ref_stats, save_preview_grid, write_diagnostics
from model_adapter import EDMAdapter
from sampler_protocol import SamplerConfig, latent_batch_from_seeds, parse_nfe_list
from samplers.registry import BUILTIN_SAMPLERS
from third_party.edm.minimal_fid import compute_feature_stats, extract_features

REPO_ROOT = Path(__file__).resolve().parent
RESULTS_PATH = REPO_ROOT / "results.tsv"
DEFAULT_CHECKPOINT = REPO_ROOT / "assets" / "checkpoints" / "edm-cifar10-32x32-uncond-vp.pkl"
DEFAULT_REF = REPO_ROOT / "assets" / "fid_refs" / "cifar10-32x32.npz"
DEFAULT_SEEDS = REPO_ROOT / "assets" / "eval_cache"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a frozen-model sampler evaluation bundle.")
    parser.add_argument("--sampler", default="research", choices=sorted(BUILTIN_SAMPLERS))
    parser.add_argument("--split", default="proxy", choices=sorted(SPLIT_SIZES))
    parser.add_argument("--nfe", default="", help="Comma-separated NFE frontier override.")
    parser.add_argument("--device", default="", help="Execution device. Defaults to cuda if available.")
    parser.add_argument("--checkpoint", default=str(DEFAULT_CHECKPOINT))
    parser.add_argument("--ref-stats", default=str(DEFAULT_REF))
    parser.add_argument("--seed-file", default="", help="Override the default seed file for the split.")
    parser.add_argument("--num-images", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--status", default="keep", choices=("keep", "discard", "crash"))
    parser.add_argument("--notes", default="")
    parser.add_argument("--save-previews", action="store_true")
    parser.add_argument("--save-diagnostics", action="store_true")
    return parser.parse_args()


def resolve_device(value: str) -> torch.device:
    if value:
        return torch.device(value)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def log_field(name: str, value: object) -> None:
    print(f"{name}: {value}", flush=True)


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


def load_seeds(path: Path, limit: int) -> list[int]:
    values = [int(line.strip()) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(values) < limit:
        raise ValueError(f"Seed file {path} only has {len(values)} seeds but {limit} are required.")
    return values[:limit]


def batched(items: list[int], batch_size: int) -> Iterable[list[int]]:
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]


def evaluate_sampler(
    sampler_name: str,
    split: str,
    nfes: tuple[int, ...],
    device: torch.device,
    checkpoint_path: Path,
    ref_path: Path,
    seed_path: Path,
    num_images: int,
    batch_size: int,
    save_previews: bool,
    save_diagnostics: bool,
) -> tuple[dict[int, float], float]:
    seeds = load_seeds(seed_path, num_images)
    adapter = EDMAdapter(str(checkpoint_path), device=device)
    ref_mu, ref_sigma = load_ref_stats(str(ref_path))
    fid_by_nfe: dict[int, float] = {}
    commit = current_commit()
    total_images = len(seeds)
    total_batches = max((total_images + batch_size - 1) // batch_size, 1)
    progress_interval = max(total_batches // 4, 1)

    for nfe in nfes:
        nfe_start = time.perf_counter()
        log_field(f"nfe_{nfe}_start_time_utc", utc_now_iso())
        sampler = BUILTIN_SAMPLERS[sampler_name]()
        feature_sum = None
        feature_sum_outer = None
        feature_count = 0
        last_trace = None
        preview_images = None

        for batch_index, batch_seeds in enumerate(batched(seeds, batch_size), start=1):
            latents = latent_batch_from_seeds(batch_seeds, adapter.image_shape(), device=device)
            cfg = SamplerConfig(
                nfe=nfe,
                sigma_min=adapter.sigma_min(),
                sigma_max=adapter.sigma_max(),
                seed=batch_seeds[0],
                device=str(device),
                batch_size=len(batch_seeds),
                image_shape=adapter.image_shape(),
                extra={"split": split},
            )
            output = sampler.sample(adapter, latents, cfg)
            if output.nfe_used != nfe:
                raise RuntimeError(
                    f"Sampler {sampler_name} reported nfe_used={output.nfe_used} for requested budget {nfe}."
                )
            images = output.images.detach()
            features = extract_features(images).to(dtype=torch.float64, device="cpu")
            if feature_sum is None:
                feature_sum = torch.zeros(features.shape[1], dtype=torch.float64)
                feature_sum_outer = torch.zeros((features.shape[1], features.shape[1]), dtype=torch.float64)
            feature_sum += features.sum(dim=0)
            feature_sum_outer += features.T @ features
            feature_count += features.shape[0]
            if preview_images is None:
                preview_images = images[:64].cpu()
            last_trace = output.trace
            if (
                batch_index == 1
                or batch_index == total_batches
                or batch_index % progress_interval == 0
            ):
                processed_images = min(batch_index * batch_size, total_images)
                elapsed_s = time.perf_counter() - nfe_start
                log_field(
                    f"nfe_{nfe}_progress",
                    f"{processed_images}/{total_images} images ({batch_index}/{total_batches} batches) elapsed_s={elapsed_s:.1f}",
                )

        mu = feature_sum / feature_count
        sigma = (feature_sum_outer - feature_count * torch.outer(mu, mu)) / max(feature_count - 1, 1)
        fid = frechet_distance(mu.numpy(), sigma.numpy(), ref_mu, ref_sigma)
        fid_by_nfe[nfe] = float(fid)
        log_field(f"fid_N{nfe}", f"{fid_by_nfe[nfe]:.4f}")
        log_field(f"nfe_{nfe}_end_time_utc", utc_now_iso())
        log_field(f"nfe_{nfe}_runtime_s", f"{time.perf_counter() - nfe_start:.1f}")

        if save_previews and preview_images is not None:
            save_preview_grid(
                preview_images,
                REPO_ROOT / "artifacts" / "samples" / commit / sampler_name / split / f"nfe_{nfe}.png",
            )
        if save_diagnostics:
            diagnostics = {
                "sampler": sampler_name,
                "split": split,
                "nfe": nfe,
                "feature_backend": compute_feature_stats(preview_images if preview_images is not None else images),
                "trace_keys": sorted(list(last_trace.keys())) if last_trace else [],
            }
            write_diagnostics(
                REPO_ROOT / "artifacts" / "diagnostics" / commit / sampler_name / split / f"nfe_{nfe}.json",
                diagnostics,
            )

    return fid_by_nfe, calc_frontier(fid_by_nfe)


def append_result_row(
    *,
    commit: str,
    sampler: str,
    split: str,
    frontier_score: float,
    fid_by_nfe: dict[int, float],
    peak_vram_mb: float,
    status: str,
    notes: str,
) -> None:
    if not RESULTS_PATH.exists():
        RESULTS_PATH.write_text(
            "commit\tsampler\tsplit\tfrontier_score\tfid_N5\tfid_N9\tfid_N11\tfid_N13\tpeak_vram_mb\tstatus\tnotes\n",
            encoding="utf-8",
        )
    row = [
        commit,
        sampler,
        split,
        f"{frontier_score:.6f}",
        f"{fid_by_nfe.get(5, 0.0):.4f}",
        f"{fid_by_nfe.get(9, 0.0):.4f}",
        f"{fid_by_nfe.get(11, 0.0):.4f}",
        f"{fid_by_nfe.get(13, 0.0):.4f}",
        f"{peak_vram_mb:.1f}",
        status,
        notes.replace("\t", " ").replace("\n", " "),
    ]
    with RESULTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\t".join(row) + "\n")


def print_summary(
    *,
    sampler: str,
    split: str,
    frontier_score: float,
    fid_by_nfe: dict[int, float],
    runtime_s: float,
    peak_vram_mb: float,
) -> None:
    print(f"sampler: {sampler}", flush=True)
    print(f"split: {split}", flush=True)
    print(f"frontier_score: {frontier_score:.6f}", flush=True)
    for nfe in sorted(fid_by_nfe):
        print(f"fid_N{nfe}: {fid_by_nfe[nfe]:.4f}", flush=True)
    print(f"runtime_s: {runtime_s:.1f}", flush=True)
    print(f"peak_vram_mb: {peak_vram_mb:.1f}", flush=True)


def main() -> int:
    args = parse_args()
    split_size = args.num_images or SPLIT_SIZES[args.split]
    device = resolve_device(args.device)
    nfes = parse_nfe_list(args.nfe)
    checkpoint_path = Path(args.checkpoint)
    ref_path = Path(args.ref_stats)
    seed_path = Path(args.seed_file) if args.seed_file else DEFAULT_SEEDS / f"seeds_{args.split}.txt"
    commit = current_commit()

    start = time.perf_counter()
    log_field("start_time_utc", utc_now_iso())
    log_field("commit", commit)
    log_field("sampler", args.sampler)
    log_field("split", args.split)
    log_field("nfes", ",".join(str(nfe) for nfe in nfes))
    log_field("num_images", split_size)
    log_field("batch_size", args.batch_size)
    log_field("device", str(device))
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    try:
        fid_by_nfe, frontier_score = evaluate_sampler(
            sampler_name=args.sampler,
            split=args.split,
            nfes=nfes,
            device=device,
            checkpoint_path=checkpoint_path,
            ref_path=ref_path,
            seed_path=seed_path,
            num_images=split_size,
            batch_size=args.batch_size,
            save_previews=args.save_previews,
            save_diagnostics=args.save_diagnostics,
        )
        runtime_s = time.perf_counter() - start
        peak_vram_mb = (
            float(torch.cuda.max_memory_allocated(device)) / (1024 * 1024)
            if device.type == "cuda"
            else 0.0
        )
        append_result_row(
            commit=commit,
            sampler=args.sampler,
            split=args.split,
            frontier_score=frontier_score,
            fid_by_nfe=fid_by_nfe,
            peak_vram_mb=peak_vram_mb,
            status=args.status,
            notes=args.notes,
        )
        log_field("end_time_utc", utc_now_iso())
        print_summary(
            sampler=args.sampler,
            split=args.split,
            frontier_score=frontier_score,
            fid_by_nfe=fid_by_nfe,
            runtime_s=runtime_s,
            peak_vram_mb=peak_vram_mb,
        )
        return 0
    except Exception as exc:
        log_field("end_time_utc", utc_now_iso())
        log_field("runtime_s", f"{time.perf_counter() - start:.1f}")
        append_result_row(
            commit=commit,
            sampler=args.sampler,
            split=args.split,
            frontier_score=0.0,
            fid_by_nfe={5: 0.0, 9: 0.0, 11: 0.0, 13: 0.0},
            peak_vram_mb=0.0,
            status="crash",
            notes=f"{args.notes} {exc}".strip(),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
