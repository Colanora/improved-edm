from __future__ import annotations

import torch
import pytest

from sample import ResearchSampler
from sampler_protocol import SamplerConfig
from samplers.euler import EulerSampler
from samplers.heun import HeunSampler
from tests.fakes import ToyEDMNet


class FakeAdapter:
    def __init__(self) -> None:
        self.net = ToyEDMNet().eval()

    def sigma_min(self) -> float:
        return 0.002

    def sigma_max(self) -> float:
        return 80.0

    def image_shape(self) -> tuple[int, int, int]:
        return (3, 32, 32)

    def round_sigma(self, sigma: torch.Tensor) -> torch.Tensor:
        return sigma.clamp_min(self.sigma_min())

    def denoise(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        return self.net(x, sigma)

    def velocity(self, x: torch.Tensor, sigma: torch.Tensor) -> torch.Tensor:
        while sigma.ndim < x.ndim:
            sigma = sigma.view(*sigma.shape, 1)
        return x / (1.0 + sigma)


@pytest.mark.parametrize(
    "sampler_cls",
    [
        EulerSampler,
        HeunSampler,
        ResearchSampler,
    ],
)
@pytest.mark.parametrize("nfe", [5, 9])
def test_sampler_outputs_are_finite(sampler_cls, nfe) -> None:
    sampler = sampler_cls()
    adapter = FakeAdapter()
    latents = torch.randn(2, 3, 32, 32)
    cfg = SamplerConfig(
        nfe=nfe,
        sigma_min=adapter.sigma_min(),
        sigma_max=adapter.sigma_max(),
        seed=0,
        device="cpu",
        batch_size=2,
        image_shape=adapter.image_shape(),
    )
    output = sampler.sample(adapter, latents, cfg)

    assert output.images.shape == latents.shape
    assert output.nfe_used == nfe
    assert torch.isfinite(output.images).all()
    assert output.trace is not None
    assert "sigmas" in output.trace


def test_heun_rejects_even_nfe() -> None:
    sampler = HeunSampler()
    adapter = FakeAdapter()
    latents = torch.randn(2, 3, 32, 32)
    cfg = SamplerConfig(
        nfe=8,
        sigma_min=adapter.sigma_min(),
        sigma_max=adapter.sigma_max(),
        seed=0,
        device="cpu",
        batch_size=2,
        image_shape=adapter.image_shape(),
    )
    with pytest.raises(ValueError, match="odd NFE"):
        sampler.sample(adapter, latents, cfg)
