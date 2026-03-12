from __future__ import annotations

import math

import torch

from sampler_protocol import edm_num_steps_for_heun
from samplers.common import sample_with_local_budget


RESEARCH_ALPHA_EARLY = 0.9
RESEARCH_ALPHA_LATE = 1.0
RESEARCH_ALPHA_MID_SIGMA = 1.0
RESEARCH_ALPHA_STEEPNESS = 2.0


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
    sigma_min = max(sigma_min, net.sigma_min)
    sigma_max = min(sigma_max, net.sigma_max)

    step_indices = torch.arange(num_steps, dtype=torch.float64, device=latents.device)
    t_steps = (
        sigma_max ** (1 / rho)
        + step_indices / (num_steps - 1) * (sigma_min ** (1 / rho) - sigma_max ** (1 / rho))
    ) ** rho
    t_steps = torch.cat([net.round_sigma(t_steps), torch.zeros_like(t_steps[:1])])

    x_next = latents.to(torch.float64) * t_steps[0]
    for i, (t_cur, t_next) in enumerate(zip(t_steps[:-1], t_steps[1:])):
        x_cur = x_next

        gamma = min(S_churn / num_steps, math.sqrt(2) - 1) if S_min <= t_cur <= S_max else 0
        t_hat = net.round_sigma(t_cur + gamma * t_cur)
        noise_scale = (t_hat.square() - t_cur.square()).clamp_min(0).sqrt()
        x_hat = x_cur + noise_scale * S_noise * randn_like(x_cur)

        denoised = net(x_hat, t_hat, class_labels).to(torch.float64)
        d_cur = (x_hat - denoised) / t_hat
        h = t_next - t_hat

        if i == num_steps - 1:
            x_next = x_hat + h * d_cur
            continue

        alpha = _research_alpha(t_hat)
        x_prime = x_hat + alpha * h * d_cur
        t_prime = t_hat + alpha * h
        denoised = net(x_prime, t_prime, class_labels).to(torch.float64)
        d_prime = (x_prime - denoised) / t_prime
        x_next = x_hat + h * ((1 - 0.5 / alpha) * d_cur + 0.5 / alpha * d_prime)

    return x_next


def _research_alpha(sigma: torch.Tensor) -> torch.Tensor:
    log_sigma = sigma.clamp_min(1e-12).log()
    log_mid_sigma = math.log(RESEARCH_ALPHA_MID_SIGMA)
    mix = torch.sigmoid(RESEARCH_ALPHA_STEEPNESS * (log_sigma - log_mid_sigma))
    alpha = RESEARCH_ALPHA_LATE + (RESEARCH_ALPHA_EARLY - RESEARCH_ALPHA_LATE) * mix
    return alpha.clamp(min=min(RESEARCH_ALPHA_EARLY, RESEARCH_ALPHA_LATE), max=max(RESEARCH_ALPHA_EARLY, RESEARCH_ALPHA_LATE))


class ResearchSampler:
    name = "research"
    rho = 7.0

    def sample(self, adapter, z: torch.Tensor, cfg):
        return sample_with_local_budget(self.name, adapter, z, cfg, rho=self.rho)
