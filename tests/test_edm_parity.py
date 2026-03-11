from __future__ import annotations

import importlib.util
import pickle
import sys
from pathlib import Path

import pytest
import torch

from model_adapter import EDMAdapter
from sampler_protocol import SamplerConfig, latent_batch_from_seeds
from samplers.euler import EulerSampler
from samplers.heun import HeunSampler
from tests.fakes import ToyEDMNet

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_GENERATE = REPO_ROOT / "third_party" / "upstream-edm" / "generate.py"


def _load_upstream_generate():
    if not UPSTREAM_GENERATE.exists():
        pytest.skip("third_party/upstream-edm is not present")
    upstream_root = str(UPSTREAM_GENERATE.parent)
    if upstream_root not in sys.path:
        sys.path.insert(0, upstream_root)
    spec = importlib.util.spec_from_file_location("upstream_edm_generate", UPSTREAM_GENERATE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {UPSTREAM_GENERATE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("sampler_cls", "nfe"),
    [
        (EulerSampler, 5),
        (EulerSampler, 9),
        (HeunSampler, 5),
        (HeunSampler, 9),
    ],
)
def test_sampler_matches_upstream_edm(tmp_path, sampler_cls, nfe) -> None:
    upstream = _load_upstream_generate()
    checkpoint = tmp_path / "toy.pkl"
    net = ToyEDMNet().eval()
    with checkpoint.open("wb") as handle:
        pickle.dump({"ema": net}, handle)

    latents = latent_batch_from_seeds([0, 1], (3, 32, 32), device="cpu", dtype=torch.float32)
    adapter = EDMAdapter(str(checkpoint), device="cpu")
    cfg = SamplerConfig(
        nfe=nfe,
        sigma_min=adapter.sigma_min(),
        sigma_max=adapter.sigma_max(),
        seed=0,
        device="cpu",
        batch_size=latents.shape[0],
        image_shape=adapter.image_shape(),
    )
    local = sampler_cls().sample(adapter, latents, cfg)

    if sampler_cls is EulerSampler:
        reference = upstream.ablation_sampler(
            net=net,
            latents=latents,
            num_steps=nfe,
            sigma_min=adapter.sigma_min(),
            sigma_max=adapter.sigma_max(),
            rho=7,
            solver="euler",
            discretization="edm",
            schedule="linear",
            scaling="none",
            S_churn=0,
        )
    else:
        reference = upstream.edm_sampler(
            net=net,
            latents=latents,
            num_steps=(nfe + 1) // 2,
            sigma_min=adapter.sigma_min(),
            sigma_max=adapter.sigma_max(),
            rho=7,
            S_churn=0,
        )

    expected = reference.clamp(-1.0, 1.0).to(torch.float32)
    assert local.nfe_used == nfe
    assert torch.equal(local.images, expected)
