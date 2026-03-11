from __future__ import annotations

import torch

from sampler_protocol import SamplerOutput, build_polynomial_sigmas, edm_num_steps_for_euler, edm_num_steps_for_heun, finalize_images
from samplers.official_backend import sample_images


def local_num_steps_for_sampler(sampler_name: str, nfe: int) -> int:
    if sampler_name == "euler":
        return edm_num_steps_for_euler(nfe)
    if sampler_name == "heun":
        return edm_num_steps_for_heun(nfe)
    if sampler_name == "research":
        from sample import research_num_steps_from_nfe

        return research_num_steps_from_nfe(nfe)
    raise KeyError(f"Unknown sampler: {sampler_name}")


def local_sigma_schedule(adapter, cfg, *, num_steps: int, rho: float = 7.0, dtype: torch.dtype = torch.float64) -> torch.Tensor:
    round_sigma = getattr(adapter, "round_sigma", None)
    return build_polynomial_sigmas(
        num_steps=num_steps,
        sigma_min=cfg.sigma_min,
        sigma_max=cfg.sigma_max,
        device=cfg.device,
        rho=rho,
        dtype=dtype,
        round_sigma=round_sigma,
        terminal_zero=True,
    )


def sample_with_local_budget(sampler_name: str, adapter, z: torch.Tensor, cfg, *, rho: float = 7.0) -> SamplerOutput:
    num_steps = local_num_steps_for_sampler(sampler_name, cfg.nfe)
    schedule = local_sigma_schedule(adapter, cfg, num_steps=num_steps, rho=rho)
    images = sample_images(
        sampler_name=sampler_name,
        net=adapter.net,
        latents=z.to(device=cfg.device),
        class_labels=None,
        randn_like=torch.randn_like,
        num_steps=num_steps,
        sigma_min=cfg.sigma_min,
        sigma_max=cfg.sigma_max,
        rho=rho,
        S_churn=0,
        S_min=0,
        S_max=float("inf"),
        S_noise=1,
    )
    return SamplerOutput(
        images=finalize_images(images.to(dtype=torch.float32)),
        nfe_used=cfg.nfe,
        trace={"sigmas": schedule.detach().cpu()},
        aux={"schedule": schedule.detach().cpu(), "sampler": sampler_name, "num_steps": num_steps},
    )
