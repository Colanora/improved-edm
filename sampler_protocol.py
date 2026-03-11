from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

import torch


@dataclass(slots=True)
class SamplerConfig:
    nfe: int
    sigma_min: float
    sigma_max: float
    seed: int
    device: str
    batch_size: int = 1
    image_shape: tuple[int, int, int] = (3, 32, 32)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SamplerContext:
    split: str
    save_trace: bool = False
    trace_stride: int = 1
    artifact_dir: Optional[str] = None


@dataclass(slots=True)
class SamplerOutput:
    images: torch.Tensor
    nfe_used: int
    trace: Optional[dict[str, torch.Tensor]]
    aux: dict[str, Any]


class BaseSampler(Protocol):
    name: str

    def sample(self, adapter: Any, z: torch.Tensor, cfg: SamplerConfig) -> SamplerOutput:
        ...


def _terminal_sigma(device: torch.device | str, *, dtype: torch.dtype) -> torch.Tensor:
    return torch.zeros(1, device=device, dtype=dtype)


def build_polynomial_sigmas(
    *,
    num_steps: int,
    sigma_min: float,
    sigma_max: float,
    device: torch.device | str,
    rho: float = 7.0,
    dtype: torch.dtype = torch.float64,
    round_sigma=None,
    terminal_zero: bool = True,
) -> torch.Tensor:
    if num_steps < 1:
        raise ValueError("num_steps must be positive.")
    ramp = torch.linspace(0.0, 1.0, num_steps, device=device, dtype=dtype)
    min_inv_rho = sigma_min ** (1.0 / rho)
    max_inv_rho = sigma_max ** (1.0 / rho)
    sigmas = (max_inv_rho + ramp * (min_inv_rho - max_inv_rho)) ** rho
    if round_sigma is not None:
        rounded = round_sigma(sigmas)
        sigmas = rounded.to(device=device, dtype=dtype)
    if terminal_zero:
        sigmas = torch.cat([sigmas, _terminal_sigma(device, dtype=dtype)])
    return sigmas


def build_karras_schedule(
    nfe: int,
    sigma_min: float,
    sigma_max: float,
    device: torch.device | str,
    rho: float = 7.0,
) -> torch.Tensor:
    return build_polynomial_sigmas(
        num_steps=nfe,
        sigma_min=sigma_min,
        sigma_max=sigma_max,
        device=device,
        rho=rho,
        dtype=torch.float32,
        terminal_zero=True,
    )


def edm_num_steps_for_euler(nfe: int) -> int:
    if nfe < 1:
        raise ValueError("EDM Euler requires at least 1 NFE.")
    return nfe


def edm_num_steps_for_heun(nfe: int) -> int:
    if nfe < 3 or nfe % 2 == 0:
        raise ValueError("EDM Heun requires an odd NFE of at least 3 because upstream EDM uses 2 * num_steps - 1 evaluations.")
    return (nfe + 1) // 2


def parse_nfe_list(value: str | None) -> tuple[int, ...]:
    if not value:
        return (5, 9, 11, 13)
    items = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not items:
        raise ValueError("No NFE values were provided.")
    return items


def latent_batch_from_seeds(
    seeds: list[int],
    image_shape: tuple[int, int, int],
    device: torch.device | str,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    latents = []
    channels, height, width = image_shape
    for seed in seeds:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(seed)
        latent = torch.randn((channels, height, width), generator=generator, dtype=dtype)
        latents.append(latent)
    batch = torch.stack(latents, dim=0)
    return batch.to(device=device, dtype=dtype)


def finalize_images(x: torch.Tensor) -> torch.Tensor:
    return x.clamp(-1.0, 1.0)
