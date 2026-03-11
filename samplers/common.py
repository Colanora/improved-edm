from __future__ import annotations

import hashlib
from pathlib import Path

import torch

from sampler_protocol import (
    SamplerOutput,
    build_polynomial_sigmas,
    edm_num_steps_for_euler,
    edm_num_steps_for_heun,
    finalize_images,
)


def broadcast_sigma(sigma: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
    sigma = sigma.to(device=x.device, dtype=x.dtype)
    while sigma.ndim < x.ndim:
        sigma = sigma.view(*sigma.shape, 1)
    return sigma


def sigma_batch(sigma: torch.Tensor, batch_size: int, *, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    return torch.full((batch_size,), float(sigma.item()), device=device, dtype=dtype)


def adapter_denoise(adapter, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
    return adapter.denoise(x, sigma_batch(sigma, x.shape[0], device=x.device, dtype=x.dtype))


def denoise_direction(adapter, x: torch.Tensor, sigma: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    denoised = adapter_denoise(adapter, x, sigma)
    direction = (x - denoised) / broadcast_sigma(sigma, x).clamp_min(1e-12)
    return denoised, direction


def polynomial_sigmas(
    adapter,
    *,
    num_steps: int,
    cfg,
    rho: float = 7.0,
    dtype: torch.dtype = torch.float64,
    terminal_zero: bool = False,
) -> torch.Tensor:
    round_sigma = getattr(adapter, "round_sigma", None)
    return build_polynomial_sigmas(
        num_steps=num_steps,
        sigma_min=cfg.sigma_min,
        sigma_max=cfg.sigma_max,
        device=cfg.device,
        rho=rho,
        dtype=dtype,
        round_sigma=round_sigma,
        terminal_zero=terminal_zero,
    )


def edm_euler_sigmas(adapter, cfg, *, rho: float = 7.0, dtype: torch.dtype = torch.float64) -> torch.Tensor:
    num_steps = edm_num_steps_for_euler(cfg.nfe)
    sigmas = polynomial_sigmas(
        adapter,
        num_steps=num_steps,
        cfg=cfg,
        rho=rho,
        dtype=dtype,
        terminal_zero=True,
    )
    return sigmas


def edm_heun_sigmas(adapter, cfg, *, rho: float = 7.0, dtype: torch.dtype = torch.float64) -> tuple[torch.Tensor, int]:
    num_steps = edm_num_steps_for_heun(cfg.nfe)
    sigmas = polynomial_sigmas(
        adapter,
        num_steps=num_steps,
        cfg=cfg,
        rho=rho,
        dtype=dtype,
        terminal_zero=True,
    )
    return sigmas, num_steps


def step_trace(trace_x: list[torch.Tensor], trace_sigmas: list[torch.Tensor], x: torch.Tensor, sigma: torch.Tensor) -> None:
    trace_x.append(x.detach().cpu())
    trace_sigmas.append(sigma.detach().cpu())


def build_trace(trace_x: list[torch.Tensor], trace_sigmas: list[torch.Tensor]) -> dict[str, torch.Tensor]:
    return {
        "sigmas": torch.stack(trace_sigmas),
        "x_mean": torch.stack([value.mean(dim=(1, 2, 3)) for value in trace_x]),
    }


def sampler_output(
    *,
    x: torch.Tensor,
    nfe_used: int,
    trace_x: list[torch.Tensor],
    trace_sigmas: list[torch.Tensor],
    aux: dict[str, object],
) -> SamplerOutput:
    return SamplerOutput(
        images=finalize_images(x.to(dtype=torch.float32)),
        nfe_used=nfe_used,
        trace=build_trace(trace_x, trace_sigmas),
        aux=aux,
    )


def checkpoint_identity(checkpoint_path: str | Path) -> str:
    path = Path(checkpoint_path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]
