from __future__ import annotations

import importlib.util
import pickle
import sys
from pathlib import Path

import pytest
import torch

from paper_generate import sample_images_for_paper
from tests.fakes import ToyEDMNet

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_GENERATE = REPO_ROOT / "third_party" / "upstream-edm" / "generate.py"


def _load_upstream_generate():
    if not UPSTREAM_GENERATE.exists():
        pytest.skip("third_party/upstream-edm is not present")
    upstream_root = str(UPSTREAM_GENERATE.parent)
    if upstream_root not in sys.path:
        sys.path.insert(0, upstream_root)
    spec = importlib.util.spec_from_file_location("upstream_edm_generate_paper", UPSTREAM_GENERATE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {UPSTREAM_GENERATE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("sampler_name", "num_steps"),
    [
        ("euler", 5),
        ("heun", 3),
        ("research", 3),
    ],
)
def test_paper_sampler_matches_upstream(tmp_path, sampler_name: str, num_steps: int) -> None:
    upstream = _load_upstream_generate()
    checkpoint = tmp_path / "toy.pkl"
    net = ToyEDMNet().eval()
    with checkpoint.open("wb") as handle:
        pickle.dump({"ema": net}, handle)

    latents = torch.randn(2, 3, 32, 32)
    local = sample_images_for_paper(
        sampler=sampler_name,
        net=net,
        latents=latents,
        class_labels=None,
        randn_like=torch.randn_like,
        num_steps=num_steps,
        sigma_min=0.002,
        sigma_max=80.0,
        rho=7,
        S_churn=0,
        S_min=0,
        S_max=float("inf"),
        S_noise=1,
    )

    if sampler_name == "euler":
        reference = upstream.ablation_sampler(
            net=net,
            latents=latents,
            num_steps=num_steps,
            sigma_min=0.002,
            sigma_max=80.0,
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
            num_steps=num_steps,
            sigma_min=0.002,
            sigma_max=80.0,
            rho=7,
            S_churn=0,
        )

    assert torch.equal(local, reference)
