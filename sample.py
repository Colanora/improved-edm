from __future__ import annotations

import torch

from sampler_protocol import edm_num_steps_for_heun
from samplers.common import sample_with_local_budget
from samplers.official_backend import official_ablation_sampler


RESEARCH_ALPHA = 0.9
RESEARCH_FRONTIER_RHO = 7.0
RESEARCH_STANDARD_RHO = 6.5
RESEARCH_STANDARD_STEP_THRESHOLD = 12


def research_num_steps_from_nfe(nfe: int) -> int:
    return edm_num_steps_for_heun(nfe)


def research_supports_target(target: str) -> bool:
    return target == "uncond"


def research_rho_for_num_steps(num_steps: int) -> float:
    if num_steps >= RESEARCH_STANDARD_STEP_THRESHOLD:
        return RESEARCH_STANDARD_RHO
    return RESEARCH_FRONTIER_RHO


def research_sampler(
    net,
    latents,
    class_labels=None,
    randn_like=torch.randn_like,
    num_steps=18,
    sigma_min=0.002,
    sigma_max=80,
    rho=7,
    S_churn=0,
    S_min=0,
    S_max=float("inf"),
    S_noise=1,
):
    rho = research_rho_for_num_steps(num_steps)
    return official_ablation_sampler(
        net=net,
        latents=latents,
        class_labels=class_labels,
        randn_like=randn_like,
        num_steps=num_steps,
        sigma_min=sigma_min,
        sigma_max=sigma_max,
        rho=rho,
        solver="heun",
        discretization="edm",
        schedule="linear",
        scaling="none",
        alpha=RESEARCH_ALPHA,
        S_churn=S_churn,
        S_min=S_min,
        S_max=S_max,
        S_noise=S_noise,
    )


class ResearchSampler:
    name = "research"

    def sample(self, adapter, z: torch.Tensor, cfg):
        rho = research_rho_for_num_steps(research_num_steps_from_nfe(cfg.nfe))
        return sample_with_local_budget(self.name, adapter, z, cfg, rho=rho)
