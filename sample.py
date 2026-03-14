from __future__ import annotations

import torch

from sampler_protocol import SamplerOutput, edm_num_steps_for_heun, finalize_images


RESEARCH_ALPHA = 0.9
RESEARCH_FRONTIER_RHO = 7.0
RESEARCH_STANDARD_RHO = 6.5
RESEARCH_STANDARD_STEP_THRESHOLD = 12
RESEARCH_STANDARD_STEP_PIVOT = 0.55
RESEARCH_STANDARD_SIGMA_PIVOT = 0.50
RESEARCH_STANDARD_ALPHA_SIGMA_START = 0.5
RESEARCH_STANDARD_MAX_ALPHA = 0.96
RESEARCH_STANDARD_PREDICTOR_START = 0.30
RESEARCH_STANDARD_MAX_PREDICTOR_MOMENTUM = 0.18
RESEARCH_STANDARD_PREDICTOR_EXTRAPOLATION_SCALE = 0.75
RESEARCH_STANDARD_CORRECTOR_MEMORY_SCALE = 0.5
RESEARCH_STANDARD_TERMINAL_HEUN_STAGES = 2
RESEARCH_STANDARD_TERMINAL_EXACT_HEUN_STAGES = 2
RESEARCH_STANDARD_LOCAL_UNIPC_STEPS_LEFT = (3, 4)
RESEARCH_STANDARD_LOCAL_RX_BLOCK_START_STEPS_LEFT = (6,)
RESEARCH_STANDARD_LOCAL_RX_BLOCK_END_STEPS_LEFT = (5,)
RESEARCH_STANDARD_LOCAL_RX_ORDER = 3.0
RESEARCH_STANDARD_BLEND_START = 0.75
RESEARCH_STANDARD_MAX_CORRECTION_RELAX = 0.08


def research_num_steps_from_nfe(nfe: int) -> int:
    return edm_num_steps_for_heun(nfe)


def research_supports_target(target: str) -> bool:
    return target == "uncond"


def research_rho_for_num_steps(num_steps: int) -> float:
    if num_steps >= RESEARCH_STANDARD_STEP_THRESHOLD:
        return RESEARCH_STANDARD_RHO
    return RESEARCH_FRONTIER_RHO


def research_step_fractions(num_steps: int, device: torch.device) -> torch.Tensor:
    step_fraction = torch.linspace(0.0, 1.0, num_steps, dtype=torch.float64, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_fraction
    early = step_fraction <= RESEARCH_STANDARD_STEP_PIVOT
    early_scale = RESEARCH_STANDARD_SIGMA_PIVOT / RESEARCH_STANDARD_STEP_PIVOT
    late_scale = (1.0 - RESEARCH_STANDARD_SIGMA_PIVOT) / (1.0 - RESEARCH_STANDARD_STEP_PIVOT)
    return torch.where(
        early,
        step_fraction * early_scale,
        RESEARCH_STANDARD_SIGMA_PIVOT + (step_fraction - RESEARCH_STANDARD_STEP_PIVOT) * late_scale,
    )


def research_t_steps(
    *,
    num_steps: int,
    sigma_min: float,
    sigma_max: float,
    rho: float,
    device: torch.device,
    round_sigma,
) -> torch.Tensor:
    step_fraction = research_step_fractions(num_steps, device)
    t_steps = (
        sigma_max ** (1 / rho) + step_fraction * (sigma_min ** (1 / rho) - sigma_max ** (1 / rho))
    ) ** rho
    return torch.cat([round_sigma(t_steps), torch.zeros(1, dtype=torch.float64, device=device)])


def research_step_predictor_mix(num_steps: int, device: torch.device) -> torch.Tensor:
    step_fraction = torch.linspace(0.0, 1.0, num_steps, dtype=torch.float64, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return torch.zeros_like(step_fraction)
    late_mix = ((step_fraction - RESEARCH_STANDARD_PREDICTOR_START) / (1.0 - RESEARCH_STANDARD_PREDICTOR_START)).clamp(0.0, 1.0)
    return RESEARCH_STANDARD_MAX_PREDICTOR_MOMENTUM * late_mix


def research_step_predictor_extrapolation(num_steps: int, device: torch.device) -> torch.Tensor:
    step_predictor_extrapolation = RESEARCH_STANDARD_PREDICTOR_EXTRAPOLATION_SCALE * research_step_predictor_mix(num_steps, device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_predictor_extrapolation
    terminal_end = num_steps - 1
    terminal_start = max(0, terminal_end - RESEARCH_STANDARD_TERMINAL_EXACT_HEUN_STAGES)
    step_predictor_extrapolation = step_predictor_extrapolation.clone()
    step_predictor_extrapolation[terminal_start:terminal_end] = 0
    return step_predictor_extrapolation


def research_step_correction_relax(num_steps: int, device: torch.device) -> torch.Tensor:
    step_fraction = torch.linspace(0.0, 1.0, num_steps, dtype=torch.float64, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return torch.zeros_like(step_fraction)
    late_mix = ((step_fraction - RESEARCH_STANDARD_BLEND_START) / (1.0 - RESEARCH_STANDARD_BLEND_START)).clamp(0.0, 1.0)
    return RESEARCH_STANDARD_MAX_CORRECTION_RELAX * late_mix


def research_step_corrector_memory(num_steps: int, device: torch.device) -> torch.Tensor:
    step_corrector_memory = RESEARCH_STANDARD_CORRECTOR_MEMORY_SCALE * research_step_predictor_mix(num_steps, device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_corrector_memory
    terminal_end = num_steps - 1
    terminal_start = max(0, terminal_end - RESEARCH_STANDARD_TERMINAL_HEUN_STAGES)
    step_corrector_memory = step_corrector_memory.clone()
    step_corrector_memory[terminal_start:terminal_end] = 0
    return step_corrector_memory


def research_step_terminal_exact_heun(num_steps: int, device: torch.device) -> torch.Tensor:
    step_terminal_exact_heun = torch.zeros(num_steps, dtype=torch.bool, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_terminal_exact_heun
    terminal_end = num_steps - 1
    terminal_start = max(0, terminal_end - RESEARCH_STANDARD_TERMINAL_EXACT_HEUN_STAGES)
    step_terminal_exact_heun[terminal_start:terminal_end] = True
    return step_terminal_exact_heun


def research_step_local_unipc_corrector(num_steps: int, device: torch.device) -> torch.Tensor:
    step_local_unipc_corrector = torch.zeros(num_steps, dtype=torch.bool, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_local_unipc_corrector
    terminal_end = num_steps - 1
    for steps_left in RESEARCH_STANDARD_LOCAL_UNIPC_STEPS_LEFT:
        step_index = terminal_end - steps_left
        if 0 <= step_index < terminal_end:
            step_local_unipc_corrector[step_index] = True
    return step_local_unipc_corrector


def research_step_local_rx_block_start(num_steps: int, device: torch.device) -> torch.Tensor:
    step_local_rx_block_start = torch.zeros(num_steps, dtype=torch.bool, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_local_rx_block_start
    terminal_end = num_steps - 1
    for steps_left in RESEARCH_STANDARD_LOCAL_RX_BLOCK_START_STEPS_LEFT:
        step_index = terminal_end - steps_left
        if 0 <= step_index < terminal_end:
            step_local_rx_block_start[step_index] = True
    return step_local_rx_block_start


def research_step_local_rx_block_end(num_steps: int, device: torch.device) -> torch.Tensor:
    step_local_rx_block_end = torch.zeros(num_steps, dtype=torch.bool, device=device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return step_local_rx_block_end
    terminal_end = num_steps - 1
    for steps_left in RESEARCH_STANDARD_LOCAL_RX_BLOCK_END_STEPS_LEFT:
        step_index = terminal_end - steps_left
        if 0 <= step_index < terminal_end:
            step_local_rx_block_end[step_index] = True
    return step_local_rx_block_end


def research_alpha_growth_gate(d_cur: torch.Tensor, prev_d_cur: torch.Tensor) -> torch.Tensor:
    d_norm = d_cur.flatten(1).norm(dim=1)
    prev_norm = prev_d_cur.flatten(1).norm(dim=1)
    ratio = (prev_norm / d_norm.clamp_min(1e-12)).clamp(0.0, 1.0)
    return ratio.sqrt()


def research_step_alpha(num_steps: int, device: torch.device) -> torch.Tensor:
    step_fraction = research_step_fractions(num_steps, device)
    if num_steps < RESEARCH_STANDARD_STEP_THRESHOLD:
        return torch.full_like(step_fraction, RESEARCH_ALPHA)
    late_mix = ((step_fraction - RESEARCH_STANDARD_ALPHA_SIGMA_START) / (1.0 - RESEARCH_STANDARD_ALPHA_SIGMA_START)).clamp(0.0, 1.0)
    return RESEARCH_ALPHA + late_mix * (RESEARCH_STANDARD_MAX_ALPHA - RESEARCH_ALPHA)


def research_local_unipc_corrector_slope(
    d_prev: torch.Tensor,
    d_cur: torch.Tensor,
    d_prime: torch.Tensor,
    step_ratio: torch.Tensor,
) -> torch.Tensor:
    denom = 6.0 * (step_ratio + 1.0)
    return (
        ((2.0 * step_ratio + 3.0) / denom) * d_prime
        + ((step_ratio + 3.0) / 6.0) * d_cur
        - (step_ratio.square() / denom) * d_prev
    )


def research_local_rxdpm_block_state(
    x_start: torch.Tensor,
    d_start: torch.Tensor,
    d_mid: torch.Tensor,
    h_start: torch.Tensor,
    h_mid: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    start_span = h_start.abs()
    mid_span = h_mid.abs()
    total_span = (start_span + mid_span).clamp_min(1e-12)
    start_ratio = start_span / total_span
    mid_ratio = mid_span / total_span
    midpoint_weight = 0.5 / start_ratio.clamp_min(1e-12)
    start_weight = 1.0 - midpoint_weight
    coarse_state = x_start + (h_start + h_mid) * (start_weight * d_start + midpoint_weight * d_mid)
    ratio_power_sum = start_ratio.pow(RESEARCH_STANDARD_LOCAL_RX_ORDER) + mid_ratio.pow(RESEARCH_STANDARD_LOCAL_RX_ORDER)
    return coarse_state, ratio_power_sum


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
    sigma_min = max(sigma_min, net.sigma_min)
    sigma_max = min(sigma_max, net.sigma_max)
    t_steps = research_t_steps(
        num_steps=num_steps,
        sigma_min=sigma_min,
        sigma_max=sigma_max,
        rho=rho,
        device=latents.device,
        round_sigma=net.round_sigma,
    )
    step_alpha = research_step_alpha(num_steps, latents.device)
    step_predictor_mix = research_step_predictor_mix(num_steps, latents.device)
    step_predictor_extrapolation = research_step_predictor_extrapolation(num_steps, latents.device)
    step_corrector_memory = research_step_corrector_memory(num_steps, latents.device)
    step_terminal_exact_heun = research_step_terminal_exact_heun(num_steps, latents.device)
    step_local_unipc_corrector = research_step_local_unipc_corrector(num_steps, latents.device)
    step_local_rx_block_start = research_step_local_rx_block_start(num_steps, latents.device)
    step_local_rx_block_end = research_step_local_rx_block_end(num_steps, latents.device)
    step_correction_relax = research_step_correction_relax(num_steps, latents.device)
    prev_d_cur = None
    prev_d_prime = None
    prev_h = None
    rx_block_start_x = None
    rx_block_start_d = None
    rx_block_start_h = None

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
        x_euler = x_hat + h * d_cur
        if bool(step_local_rx_block_start[i]):
            rx_block_start_x = x_hat.detach()
            rx_block_start_d = d_cur.detach()
            rx_block_start_h = h.detach()

        if i == num_steps - 1:
            x_next = x_euler
            continue

        predictor_d = d_cur
        alpha_flat = torch.full((d_cur.shape[0],), float(step_alpha[i]), dtype=torch.float64, device=d_cur.device)
        predictor_beta_flat = torch.zeros_like(alpha_flat)
        memory_flat = torch.zeros_like(alpha_flat)
        relax_flat = torch.zeros_like(alpha_flat)
        local_unipc = False
        if prev_d_cur is not None:
            growth_gate = research_alpha_growth_gate(d_cur, prev_d_cur)
            predictor_beta_flat = torch.full_like(alpha_flat, float(step_predictor_extrapolation[i]))
            predictor_beta = predictor_beta_flat.view(-1, *([1] * (d_cur.ndim - 1)))
            predictor_d = d_cur + predictor_beta * (d_cur - prev_d_cur)
            alpha_flat = RESEARCH_ALPHA + growth_gate * (step_alpha[i] - RESEARCH_ALPHA)
            memory_flat = torch.full_like(alpha_flat, float(step_corrector_memory[i]))
            relax_flat = step_correction_relax[i] * (1.0 - growth_gate)
            if bool(step_terminal_exact_heun[i]):
                alpha_flat = torch.ones_like(alpha_flat)
                relax_flat = torch.zeros_like(relax_flat)
            elif float(step_corrector_memory[i]) == 0.0:
                relax_flat = torch.zeros_like(relax_flat)
            local_unipc = bool(step_local_unipc_corrector[i]) and prev_h is not None
            if local_unipc:
                alpha_flat = torch.ones_like(alpha_flat)
                memory_flat = torch.zeros_like(memory_flat)
                relax_flat = torch.zeros_like(relax_flat)
        alpha = alpha_flat.view(-1, *([1] * (d_cur.ndim - 1)))
        x_prime = x_hat + alpha * h * predictor_d
        t_prime_input = t_hat + alpha_flat * h
        denoised = net(x_prime, t_prime_input, class_labels).to(torch.float64)
        t_prime = t_prime_input.view(-1, *([1] * (d_cur.ndim - 1)))
        d_prime = (x_prime - denoised) / t_prime
        if local_unipc:
            step_ratio = (h / prev_h).to(dtype=torch.float64)
            corrected_slope = research_local_unipc_corrector_slope(prev_d_cur, d_cur, d_prime, step_ratio)
        else:
            corrected_slope = (1 - 0.5 / alpha) * d_cur + 0.5 / alpha * d_prime
            if prev_d_prime is not None:
                memory = memory_flat.view(-1, *([1] * (d_cur.ndim - 1)))
                corrected_slope = corrected_slope + memory * (d_prime - prev_d_prime)
        x_heun = x_hat + h * corrected_slope
        relax = relax_flat.view(-1, *([1] * (x_heun.ndim - 1)))
        x_next = x_heun + relax * (x_euler - x_heun)
        # Reuse the two approach steps as one localized RX-style block before the UniPC tail begins.
        if bool(step_local_rx_block_end[i]) and rx_block_start_x is not None and rx_block_start_d is not None and rx_block_start_h is not None:
            coarse_state, ratio_power_sum = research_local_rxdpm_block_state(
                rx_block_start_x,
                rx_block_start_d,
                d_cur.detach(),
                rx_block_start_h,
                h.detach(),
            )
            x_next = (x_next - ratio_power_sum * coarse_state) / (1.0 - ratio_power_sum).clamp_min(1e-12)
            rx_block_start_x = None
            rx_block_start_d = None
            rx_block_start_h = None
        prev_d_cur = d_cur.detach()
        prev_d_prime = d_prime.detach()
        prev_h = h.detach()

    return x_next


class ResearchSampler:
    name = "research"

    def sample(self, adapter, z: torch.Tensor, cfg):
        num_steps = research_num_steps_from_nfe(cfg.nfe)
        rho = research_rho_for_num_steps(num_steps)
        schedule = research_t_steps(
            num_steps=num_steps,
            sigma_min=cfg.sigma_min,
            sigma_max=cfg.sigma_max,
            rho=rho,
            device=z.device,
            round_sigma=adapter.round_sigma,
        )
        images = research_sampler(
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
            aux={"schedule": schedule.detach().cpu(), "sampler": self.name, "num_steps": num_steps},
        )
