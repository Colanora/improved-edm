from __future__ import annotations

import math
import pickle
import sys
from pathlib import Path
from typing import Any

import torch
from torch import nn

REPO_ROOT = Path(__file__).resolve().parent
EDM_ROOT = REPO_ROOT / "third_party" / "edm"
DEFAULT_SIGMA_MIN = 0.002
DEFAULT_SIGMA_MAX = 80.0


def _broadcast_sigma(sigma: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
    sigma = sigma.to(device=x.device, dtype=x.dtype)
    while sigma.ndim < x.ndim:
        sigma = sigma.view(*sigma.shape, 1)
    return sigma


def _ensure_edm_imports() -> None:
    edm_root = str(EDM_ROOT)
    if edm_root not in sys.path:
        sys.path.insert(0, edm_root)
    import dnnlib  # noqa: F401
    from torch_utils import persistence  # noqa: F401


def _open_checkpoint(path: Path) -> Any:
    _ensure_edm_imports()
    with path.open("rb") as handle:
        return pickle.load(handle)


def _unwrap_network(payload: Any) -> nn.Module:
    if isinstance(payload, nn.Module):
        return payload
    if isinstance(payload, dict):
        for key in ("ema", "model", "net", "module", "generator"):
            candidate = payload.get(key)
            if isinstance(candidate, nn.Module):
                return candidate
    raise TypeError("Unsupported checkpoint payload. Expected an nn.Module or dict containing one.")


def _resolve_sampler_sigma_bounds(net: nn.Module) -> tuple[float, float]:
    raw_sigma_min = float(getattr(net, "sigma_min", DEFAULT_SIGMA_MIN))
    raw_sigma_max = float(getattr(net, "sigma_max", DEFAULT_SIGMA_MAX))
    sigma_min = raw_sigma_min if math.isfinite(raw_sigma_min) and raw_sigma_min > 0.0 else DEFAULT_SIGMA_MIN
    sigma_max = raw_sigma_max if math.isfinite(raw_sigma_max) and raw_sigma_max > 0.0 else DEFAULT_SIGMA_MAX
    if sigma_min >= sigma_max:
        return DEFAULT_SIGMA_MIN, DEFAULT_SIGMA_MAX
    return sigma_min, sigma_max


class EDMAdapter:
    def __init__(self, checkpoint_path: str, device: torch.device | str):
        self.checkpoint_path = Path(checkpoint_path)
        self.device = torch.device(device)
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")

        payload = _open_checkpoint(self.checkpoint_path)
        self.net = _unwrap_network(payload).to(self.device)
        self.net.eval()
        self.net.requires_grad_(False)
        self.channels = int(getattr(self.net, "img_channels", 3))
        self.resolution = int(getattr(self.net, "img_resolution", 32))
        self._sigma_min, self._sigma_max = _resolve_sampler_sigma_bounds(self.net)
        self._checkpoint_id: str | None = None

    def image_shape(self) -> tuple[int, int, int]:
        return (self.channels, self.resolution, self.resolution)

    def sigma_min(self) -> float:
        return self._sigma_min

    def sigma_max(self) -> float:
        return self._sigma_max

    def round_sigma(self, sigma: torch.Tensor) -> torch.Tensor:
        if hasattr(self.net, "round_sigma"):
            return self.net.round_sigma(sigma)
        return sigma

    def checkpoint_id(self) -> str:
        if self._checkpoint_id is None:
            import hashlib

            digest = hashlib.sha256()
            with self.checkpoint_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            self._checkpoint_id = digest.hexdigest()[:12]
        return self._checkpoint_id

    def _call_net(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        x_model = x.to(device=self.device)
        sigma_model = sigma.to(device=self.device)
        call_variants = (
            lambda: self.net(x_model, sigma_model),
            lambda: self.net(x_model, sigma_model, None),
            lambda: self.net(x_model, sigma_model, class_labels=None),
        )
        last_exc: Exception | None = None
        for variant in call_variants:
            try:
                return variant().to(device=x.device, dtype=x.dtype)
            except TypeError as exc:
                last_exc = exc
        raise RuntimeError("Unable to call checkpoint network with an EDM-style signature.") from last_exc

    @torch.inference_mode()
    def denoise(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        return self._call_net(x, sigma)

    @torch.inference_mode()
    def score(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        sigma_view = _broadcast_sigma(sigma, x)
        denoised = self.denoise(x, sigma)
        return (denoised - x) / sigma_view.square().clamp_min(1e-12)

    @torch.inference_mode()
    def x0(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        return self.denoise(x, sigma)

    @torch.inference_mode()
    def velocity(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        sigma_view = _broadcast_sigma(sigma, x)
        return (x - self.denoise(x, sigma)) / sigma_view.clamp_min(1e-12)
