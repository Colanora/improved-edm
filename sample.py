from __future__ import annotations

import torch

from sampler_protocol import edm_num_steps_for_heun
from samplers.common import sample_with_local_budget
from samplers.official_backend import official_ablation_sampler


RESEARCH_ALPHA = 0.9
RESEARCH_FRONTIER_RHO = 7.0
RESEARCH_STANDARD_RHO = 6.5
RESEARCH_STANDARD_STEP_THRESHOLD = 12
RESEARCH_STANDARD_LATE_ALPHA = 0.84
RESEARCH_STANDARD_LATE_START = 0.65


def research_num_steps_from_nfe(nfe: int) -> int:
    return edm_num_steps_for_heun(nfe)


def research_supports_target(target: str) -> bool:
    return target == "uncond"


def research_rho_for_num_steps(num_steps: int) -> float:
    if num_steps >= RESEARCH_STANDARD_STEP_THRESHOLD:
        return RESEARCH_STANDARD_RHO
    return RESEARCH_FRONTIER_RHO


def research_alpha_schedule(num_steps: int, device: torch.device) -> torch.Tensor | None:
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return None
    step_indices = torch.arange(num_steps, dtype=torch.float64, device=device)
    step_fraction = step_indices / max(num_steps - 1, 1)
    late_mix = ((step_fraction - RESEARCH_STANDARD_LATE_START) / (1.0 - RESEARCH_STANDARD_LATE_START)).clamp(0.0, 1.0)
    return RESEARCH_ALPHA + late_mix * (RESEARCH_STANDARD_LATE_ALPHA - RESEARCH_ALPHA)


def research_step_aware_sampler(
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
    alpha_steps = research_alpha_schedule(num_steps, latents.device)

    x_next = latents.to(torch.float64) * t_steps[0]
    for i, (t_cur, t_next) in enumerate(zip(t_steps[:-1], t_steps[1:])):
        x_cur = x_next

        gamma = min(S_churn / num_steps, 2**0.5 - 1) if S_min <= t_cur <= S_max else 0
        t_hat = net.round_sigma(t_cur + gamma * t_cur)
        noise_scale = (t_hat.square() - t_cur.square()).clamp_min(0).sqrt()
        x_hat = x_cur + noise_scale * S_noise * randn_like(x_cur)

        denoised = net(x_hat, t_hat, class_labels).to(torch.float64)
        d_cur = (x_hat - denoised) / t_hat
        h = t_next - t_hat

        if i == num_steps - 1:
            x_next = x_hat + h * d_cur
            continue

        alpha = alpha_steps[i]
        x_prime = x_hat + alpha * h * d_cur
        t_prime = t_hat + alpha * h
        denoised = net(x_prime, t_prime, class_labels).to(torch.float64)
        d_prime = (x_prime - denoised) / t_prime
        x_next = x_hat + h * ((1 - 0.5 / alpha) * d_cur + 0.5 / alpha * d_prime)

    return x_next


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
    alpha_steps = research_alpha_schedule(num_steps, latents.device)
    if alpha_steps is not None:
        return research_step_aware_sampler(
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
