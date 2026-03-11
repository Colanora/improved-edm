from __future__ import annotations

import torch

from sampler_protocol import edm_num_steps_for_heun
from samplers.common import sample_with_local_budget
from samplers.official_backend import official_edm_sampler


def research_num_steps_from_nfe(nfe: int) -> int:
    return edm_num_steps_for_heun(nfe)


def research_supports_target(target: str) -> bool:
    return target == "uncond"


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
    return official_edm_sampler(
        net=net,
        latents=latents,
        class_labels=class_labels,
        randn_like=randn_like,
        num_steps=num_steps,
        sigma_min=sigma_min,
        sigma_max=sigma_max,
        rho=rho,
        S_churn=S_churn,
        S_min=S_min,
        S_max=S_max,
        S_noise=S_noise,
    )


class ResearchSampler:
    name = "research"
    rho = 7.0

    def sample(self, adapter, z: torch.Tensor, cfg):
        return sample_with_local_budget(self.name, adapter, z, cfg, rho=self.rho)
