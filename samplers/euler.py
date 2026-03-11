from __future__ import annotations

import torch

from sampler_protocol import SamplerConfig
from samplers.common import denoise_direction, edm_euler_sigmas, sampler_output, step_trace


class EulerSampler:
    name = "euler"
    rho = 7.0

    def sample(self, adapter, z: torch.Tensor, cfg: SamplerConfig):
        sigmas = edm_euler_sigmas(adapter, cfg, rho=self.rho)
        x = z.to(device=cfg.device, dtype=torch.float64) * sigmas[0]
        trace_x = [x.detach().cpu()]
        trace_sigmas = [sigmas[0].detach().cpu()]
        nfe_used = 0

        for sigma, sigma_next in zip(sigmas[:-1], sigmas[1:]):
            _, direction = denoise_direction(adapter, x, sigma)
            nfe_used += 1
            x = x + (sigma_next - sigma) * direction
            step_trace(trace_x, trace_sigmas, x, sigma_next)

        if nfe_used != cfg.nfe:
            raise RuntimeError(f"EulerSampler used {nfe_used} NFE for budget {cfg.nfe}.")

        return sampler_output(
            x=x,
            nfe_used=nfe_used,
            trace_x=trace_x,
            trace_sigmas=trace_sigmas,
            aux={"schedule": sigmas.detach().cpu(), "sampler": self.name, "num_steps": cfg.nfe},
        )
