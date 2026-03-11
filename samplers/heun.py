from __future__ import annotations

import torch

from sampler_protocol import SamplerConfig
from samplers.common import denoise_direction, edm_heun_sigmas, sampler_output, step_trace


class HeunSampler:
    name = "heun"
    rho = 7.0

    def sample(self, adapter, z: torch.Tensor, cfg: SamplerConfig):
        sigmas, num_steps = edm_heun_sigmas(adapter, cfg, rho=self.rho)
        x_next = z.to(device=cfg.device, dtype=torch.float64) * sigmas[0]
        x = x_next
        trace_x = [x.detach().cpu()]
        trace_sigmas = [sigmas[0].detach().cpu()]
        nfe_used = 0

        for index, (sigma, sigma_next) in enumerate(zip(sigmas[:-1], sigmas[1:])):
            x_hat = x_next
            _, direction = denoise_direction(adapter, x_hat, sigma)
            nfe_used += 1
            x_next = x_hat + (sigma_next - sigma) * direction
            if index == num_steps - 1:
                x = x_next
            else:
                _, direction_next = denoise_direction(adapter, x_next, sigma_next)
                nfe_used += 1
                x_next = x_hat + (sigma_next - sigma) * (0.5 * direction + 0.5 * direction_next)
                x = x_next
            step_trace(trace_x, trace_sigmas, x, sigma_next)

        if nfe_used != cfg.nfe:
            raise RuntimeError(f"HeunSampler used {nfe_used} NFE for budget {cfg.nfe}.")

        return sampler_output(
            x=x,
            nfe_used=nfe_used,
            trace_x=trace_x,
            trace_sigmas=trace_sigmas,
            aux={"schedule": sigmas.detach().cpu(), "sampler": self.name, "num_steps": num_steps},
        )
