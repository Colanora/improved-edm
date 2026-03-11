from __future__ import annotations

import os
import pickle
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy import linalg

REPO_ROOT = Path(__file__).resolve().parents[3]
EDM_ROOT = REPO_ROOT / "third_party" / "edm"
DETECTOR_URL = (
    "https://api.ngc.nvidia.com/v2/models/nvidia/research/stylegan3/"
    "versions/1/files/metrics/inception-2015-12-05.pkl"
)
DETECTOR_PATH_ENV = "EDM_INCEPTION_PATH"
APPROX_FID_ENV = "SAMPLER_AUTORESEARCH_ALLOW_APPROX_FID"


def _allow_approx() -> bool:
    return os.environ.get(APPROX_FID_ENV, "").lower() in {"1", "true", "yes", "on"}


def _ensure_edm_imports() -> None:
    edm_root = str(EDM_ROOT)
    if edm_root not in sys.path:
        sys.path.insert(0, edm_root)
    import dnnlib  # noqa: F401
    from torch_utils import persistence  # noqa: F401


@lru_cache(maxsize=4)
def _load_detector(device_name: str) -> torch.nn.Module:
    _ensure_edm_imports()
    import dnnlib

    source = os.environ.get(DETECTOR_PATH_ENV, DETECTOR_URL)
    device = torch.device(device_name)
    with dnnlib.open_url(source) as handle:
        detector = pickle.load(handle).to(device)
    detector.eval()
    detector.requires_grad_(False)
    return detector


def _to_detector_input(images: torch.Tensor, device: torch.device) -> torch.Tensor:
    batch = images.detach()
    if batch.ndim != 4:
        raise ValueError(f"Expected NCHW images, got shape {tuple(batch.shape)}")
    if batch.shape[1] == 1:
        batch = batch.repeat(1, 3, 1, 1)
    if batch.dtype != torch.uint8:
        if batch.min().item() < 0.0:
            batch = (batch + 1.0) * 127.5
        else:
            batch = batch * 255.0
        batch = batch.clamp(0.0, 255.0).round().to(torch.uint8)
    return batch.to(device)


def _extract_approx_features(images: torch.Tensor) -> torch.Tensor:
    batch = images.detach().to(dtype=torch.float32)
    if batch.min().item() < 0.0:
        batch = (batch + 1.0) / 2.0
    batch = batch.clamp(0.0, 1.0)
    pooled = F.adaptive_avg_pool2d(batch, output_size=(8, 8))
    return pooled.flatten(start_dim=1)


def detector_backend() -> str:
    return "approx_pool" if _allow_approx() else "edm_inception"


def extract_features(images: torch.Tensor) -> torch.Tensor:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        detector = _load_detector(str(device))
        batch = _to_detector_input(images, device)
        with torch.inference_mode():
            features = detector(batch, return_features=True)
        return features.detach().to(device="cpu", dtype=torch.float32)
    except Exception as exc:
        if not _allow_approx():
            raise RuntimeError(
                "Unable to load the EDM Inception detector for FID evaluation. "
                f"Set {APPROX_FID_ENV}=1 only for offline tests or local smoke runs."
            ) from exc
        return _extract_approx_features(images)


def compute_feature_stats(images: torch.Tensor) -> dict[str, int | str]:
    features = extract_features(images)
    return {
        "feature_dim": int(features.shape[1]),
        "backend": detector_backend(),
    }


def frechet_distance(
    mu1: np.ndarray,
    sigma1: np.ndarray,
    mu2: np.ndarray,
    sigma2: np.ndarray,
    eps: float = 1e-6,
) -> float:
    mu1 = np.atleast_1d(mu1)
    mu2 = np.atleast_1d(mu2)
    sigma1 = np.atleast_2d(sigma1)
    sigma2 = np.atleast_2d(sigma2)

    covmean = linalg.sqrtm(
        (sigma1 + eps * np.eye(sigma1.shape[0])) @ (sigma2 + eps * np.eye(sigma2.shape[0]))
    )
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    diff = mu1 - mu2
    trace = np.trace(sigma1) + np.trace(sigma2) - 2.0 * np.trace(covmean)
    return float(diff @ diff + trace)


def compute_feature_stats_from_images(images: torch.Tensor) -> tuple[np.ndarray, np.ndarray]:
    features = extract_features(images).cpu().numpy()
    mu = features.mean(axis=0)
    sigma = np.cov(features, rowvar=False)
    return mu, sigma
