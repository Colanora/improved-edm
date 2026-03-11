from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from torchvision.utils import make_grid, save_image

from third_party.edm.minimal_fid import compute_feature_stats, extract_features, frechet_distance

FRONTIER_WEIGHTS = {5: 0.35, 9: 0.30, 11: 0.20, 13: 0.15}
SPLIT_SIZES = {"proxy": 5_000, "confirm": 10_000, "final": 50_000}


@dataclass
class FeatureAccumulator:
    feature_dim: int

    def __post_init__(self) -> None:
        self.count = 0
        self.sum = torch.zeros(self.feature_dim, dtype=torch.float64)
        self.sum_outer = torch.zeros((self.feature_dim, self.feature_dim), dtype=torch.float64)

    def update(self, images: torch.Tensor) -> None:
        features = extract_features(images).to(dtype=torch.float64, device="cpu")
        self.count += features.shape[0]
        self.sum += features.sum(dim=0)
        self.sum_outer += features.T @ features

    def finalize(self) -> tuple[np.ndarray, np.ndarray]:
        if self.count < 2:
            raise ValueError("At least two samples are required to compute covariance.")
        mu = self.sum / self.count
        centered_outer = self.sum_outer - self.count * torch.outer(mu, mu)
        sigma = centered_outer / max(self.count - 1, 1)
        return mu.numpy(), sigma.numpy()


def load_ref_stats(ref_npz_path: str) -> tuple[np.ndarray, np.ndarray]:
    stats = np.load(ref_npz_path)
    if "mu" in stats and "sigma" in stats:
        return stats["mu"], stats["sigma"]
    if "mean" in stats and "cov" in stats:
        return stats["mean"], stats["cov"]
    raise KeyError(f"Reference stats at {ref_npz_path} must contain mu/sigma or mean/cov.")


def calc_fid(images: torch.Tensor, ref_npz_path: str) -> float:
    accumulator = FeatureAccumulator(feature_dim=extract_features(images[:1]).shape[1])
    accumulator.update(images)
    mu, sigma = accumulator.finalize()
    ref_mu, ref_sigma = load_ref_stats(ref_npz_path)
    return frechet_distance(mu, sigma, ref_mu, ref_sigma)


def calc_frontier(fid_by_nfe: dict[int, float]) -> float:
    score = 0.0
    for nfe, weight in FRONTIER_WEIGHTS.items():
        score += weight * np.log(float(fid_by_nfe[nfe]) + 1e-8)
    return float(score)


def save_preview_grid(images: torch.Tensor, destination: Path, max_images: int = 64) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    preview = images[:max_images]
    grid = make_grid((preview + 1.0) / 2.0, nrow=8)
    save_image(grid, destination)


def write_diagnostics(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def stats_from_batches(batches: Iterable[torch.Tensor]) -> tuple[np.ndarray, np.ndarray]:
    accumulator: FeatureAccumulator | None = None
    for batch in batches:
        features = extract_features(batch)
        if accumulator is None:
            accumulator = FeatureAccumulator(feature_dim=features.shape[1])
        accumulator.update(batch)
    if accumulator is None:
        raise ValueError("No batches were provided.")
    return accumulator.finalize()


def compute_feature_backend(images: torch.Tensor) -> dict[str, int]:
    return compute_feature_stats(images)
