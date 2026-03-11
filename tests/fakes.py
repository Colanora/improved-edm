from __future__ import annotations

import torch
from torch import nn


class ToyEDMNet(nn.Module):
    img_channels = 3
    img_resolution = 32
    sigma_min = 0.002
    sigma_max = 80.0

    def round_sigma(self, sigma: torch.Tensor) -> torch.Tensor:
        return sigma.clamp_min(self.sigma_min)

    def forward(self, x: torch.Tensor, sigma: torch.Tensor, class_labels=None) -> torch.Tensor:
        x = x.to(torch.float32)
        sigma = sigma.to(torch.float32)
        while sigma.ndim < x.ndim:
            sigma = sigma.view(*sigma.shape, 1)
        return x / (1.0 + sigma)


class InfiniteRangeToyEDMNet(ToyEDMNet):
    sigma_min = 0.0
    sigma_max = float("inf")
