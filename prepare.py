from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised in environments without PyYAML.
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = REPO_ROOT / "assets"
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
RESULTS_PATH = REPO_ROOT / "results.tsv"
MANIFEST_PATH = ASSETS_DIR / "manifest.yaml"
DEFAULT_CHECKPOINT = ASSETS_DIR / "checkpoints" / "edm-cifar10-32x32-uncond-vp.pkl"

DIRECTORIES = (
    ASSETS_DIR / "checkpoints",
    ASSETS_DIR / "fid_refs",
    ASSETS_DIR / "previews",
    ASSETS_DIR / "eval_cache",
    ARTIFACTS_DIR / "logs",
    ARTIFACTS_DIR / "diagnostics",
    ARTIFACTS_DIR / "samples",
    REPO_ROOT / "papers" / "raw",
    REPO_ROOT / "papers" / "notes",
    REPO_ROOT / "samplers",
)

RESULTS_HEADER = (
    "commit\tsampler\tsplit\tfrontier_score\tfid_N5\tfid_N9\tfid_N11\tfid_N13\t"
    "peak_vram_mb\tstatus\tnotes\n"
)

SEED_SPECS = {
    "proxy": (5_000, 0),
    "confirm": (10_000, 100_000),
    "final": (50_000, 200_000),
}


@dataclass(frozen=True)
class AssetSpec:
    name: str
    filename: str
    sha256: str
    primary_url: str
    mirror_repo: str
    destination: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap the sampler autoresearch repo.")
    parser.add_argument("--check", action="store_true", help="Verify runtime and asset presence.")
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="Create the scaffold and fetch assets without running any sampling work.",
    )
    return parser.parse_args()


def load_manifest() -> list[AssetSpec]:
    if yaml is not None:
        raw = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        raw = _load_manifest_fallback(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [
        AssetSpec(
            name="checkpoint",
            filename=raw["checkpoint"]["filename"],
            sha256=str(raw["checkpoint"].get("sha256", "")),
            primary_url=raw["checkpoint"]["primary_url"],
            mirror_repo=str(raw["checkpoint"].get("mirror_repo", "")),
            destination=ASSETS_DIR / "checkpoints" / raw["checkpoint"]["filename"],
        ),
        AssetSpec(
            name="fid_ref",
            filename=raw["fid_ref"]["filename"],
            sha256=str(raw["fid_ref"].get("sha256", "")),
            primary_url=raw["fid_ref"]["primary_url"],
            mirror_repo=str(raw["fid_ref"].get("mirror_repo", "")),
            destination=ASSETS_DIR / "fid_refs" / raw["fid_ref"]["filename"],
        ),
    ]


def _load_manifest_fallback(text: str) -> dict[str, dict[str, str]]:
    current = None
    raw: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" "):
            current = line.rstrip(":")
            raw[current] = {}
            continue
        if current is None:
            raise ValueError("Invalid manifest structure.")
        key, value = line.strip().split(":", maxsplit=1)
        raw[current][key.strip()] = value.strip().strip('"')
    return raw


def ensure_directories() -> None:
    for path in DIRECTORIES:
        path.mkdir(parents=True, exist_ok=True)


def ensure_keep_files() -> None:
    keep_paths = [
        ASSETS_DIR / "checkpoints" / ".gitkeep",
        ASSETS_DIR / "fid_refs" / ".gitkeep",
        ASSETS_DIR / "previews" / ".gitkeep",
        ARTIFACTS_DIR / "logs" / ".gitkeep",
        ARTIFACTS_DIR / "diagnostics" / ".gitkeep",
        ARTIFACTS_DIR / "samples" / ".gitkeep",
    ]
    for keep_path in keep_paths:
        keep_path.touch(exist_ok=True)


def ensure_results_file() -> None:
    if not RESULTS_PATH.exists():
        RESULTS_PATH.write_text(RESULTS_HEADER, encoding="utf-8")


def seed_path(name: str) -> Path:
    return ASSETS_DIR / "eval_cache" / f"seeds_{name}.txt"


def write_seed_file(path: Path, count: int, start: int) -> None:
    values = "\n".join(str(start + index) for index in range(count)) + "\n"
    path.write_text(values, encoding="utf-8")


def ensure_seed_files() -> None:
    for split_name, (count, start) in SEED_SPECS.items():
        path = seed_path(split_name)
        if not path.exists():
            write_seed_file(path, count, start)


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def runtime_report() -> dict[str, Any]:
    cuda_available = torch.cuda.is_available()
    return {
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "cuda_available": cuda_available,
        "cuda_device_count": torch.cuda.device_count() if cuda_available else 0,
        "uv_index_url": os.environ.get("UV_INDEX_URL", ""),
        "hf_endpoint": os.environ.get("HF_ENDPOINT", ""),
    }


def print_report(report: dict[str, Any]) -> None:
    print("prepare_report:")
    for key, value in report.items():
        print(f"  {key}: {value}")
    if not report["uv_index_url"]:
        print("  note: export UV_INDEX_URL=https://mirrors.ustc.edu.cn/pypi/web/simple")
    if not report["hf_endpoint"]:
        print("  note: export HF_ENDPOINT=https://hf-mirror.com")


def should_try_hf(spec: AssetSpec) -> bool:
    return bool(os.environ.get("HF_ENDPOINT")) and spec.mirror_repo and not spec.mirror_repo.startswith("your-org/")


def download_to_path(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = destination.with_suffix(destination.suffix + ".tmp")
    with urllib.request.urlopen(url) as response, tmp_path.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    tmp_path.replace(destination)


def download_from_hf(spec: AssetSpec) -> None:
    from huggingface_hub import hf_hub_download

    downloaded = hf_hub_download(repo_id=spec.mirror_repo, filename=spec.filename)
    Path(downloaded).replace(spec.destination)


def ensure_asset(spec: AssetSpec, *, check_only: bool) -> tuple[bool, str]:
    if spec.destination.exists():
        if spec.sha256 and sha256sum(spec.destination) != spec.sha256:
            return False, f"{spec.name}: sha256 mismatch at {spec.destination}"
        return True, f"{spec.name}: present"

    if check_only:
        return False, f"{spec.name}: missing at {spec.destination}"

    try:
        if should_try_hf(spec):
            download_from_hf(spec)
        else:
            download_to_path(spec.primary_url, spec.destination)
    except (urllib.error.URLError, OSError) as exc:
        return False, f"{spec.name}: download failed ({exc})"

    if spec.sha256 and sha256sum(spec.destination) != spec.sha256:
        return False, f"{spec.name}: sha256 mismatch after download"
    return True, f"{spec.name}: downloaded"


def verify_assets(check_only: bool) -> list[str]:
    messages = []
    failures = 0
    for spec in load_manifest():
        ok, message = ensure_asset(spec, check_only=check_only)
        messages.append(message)
        if not ok:
            failures += 1
    if failures:
        raise RuntimeError("\n".join(messages))
    return messages


def main() -> int:
    args = parse_args()
    ensure_directories()
    ensure_keep_files()
    ensure_results_file()
    ensure_seed_files()

    report = runtime_report()
    print_report(report)

    try:
        messages = verify_assets(check_only=args.check)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for message in messages:
        print(message)

    if not args.download_only:
        print("prepare: EDM-only repo, no extra cache build required")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
