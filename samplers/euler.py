from __future__ import annotations

import torch

from sampler_protocol import SamplerConfig
from samplers.common import sample_with_local_budget


class EulerSampler:
    name = "euler"
    rho = 7.0

    def sample(self, adapter, z: torch.Tensor, cfg: SamplerConfig):
        return sample_with_local_budget(self.name, adapter, z, cfg, rho=self.rho)
