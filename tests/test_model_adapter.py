from __future__ import annotations

import importlib
import pickle
import sys
from pathlib import Path

import torch

from model_adapter import EDMAdapter
from tests.fakes import InfiniteRangeToyEDMNet, ToyEDMNet


def test_adapter_loads_dummy_checkpoint(tmp_path) -> None:
    checkpoint = tmp_path / "toy.pkl"
    with checkpoint.open("wb") as handle:
        pickle.dump({"ema": ToyEDMNet()}, handle)

    adapter = EDMAdapter(str(checkpoint), device="cpu")
    x = torch.randn(2, 3, 32, 32)
    sigma = torch.full((2,), 1.5)

    denoised = adapter.denoise(x, sigma)
    score = adapter.score(x, sigma)
    velocity = adapter.velocity(x, sigma)

    assert denoised.shape == x.shape
    assert score.shape == x.shape
    assert velocity.shape == x.shape
    assert torch.isfinite(denoised).all()


def test_adapter_loads_persistent_checkpoint(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(repo_root / "third_party" / "edm"))
    monkeypatch.syspath_prepend(str(tmp_path))

    module_path = tmp_path / "persistent_toy.py"
    module_path.write_text(
        "\n".join(
            [
                "import torch",
                "from torch import nn",
                "from torch_utils import persistence",
                "",
                "@persistence.persistent_class",
                "class PersistentToyNet(nn.Module):",
                "    img_channels = 3",
                "    img_resolution = 32",
                "    sigma_min = 0.002",
                "    sigma_max = 80.0",
                "",
                "    def round_sigma(self, sigma: torch.Tensor) -> torch.Tensor:",
                "        return sigma.clamp_min(self.sigma_min)",
                "",
                "    def forward(self, x: torch.Tensor, sigma: torch.Tensor, class_labels=None) -> torch.Tensor:",
                "        while sigma.ndim < x.ndim:",
                "            sigma = sigma.view(*sigma.shape, 1)",
                "        return x / (1.0 + sigma)",
            ]
        ),
        encoding="utf-8",
    )

    persistent_toy = importlib.import_module("persistent_toy")
    checkpoint = tmp_path / "persistent.pkl"
    with checkpoint.open("wb") as handle:
        pickle.dump({"ema": persistent_toy.PersistentToyNet()}, handle)
    del sys.modules["persistent_toy"]

    adapter = EDMAdapter(str(checkpoint), device="cpu")
    x = torch.randn(1, 3, 32, 32)
    sigma = torch.ones(1)

    denoised = adapter.denoise(x, sigma)
    assert denoised.shape == x.shape


def test_adapter_falls_back_to_edm_sampler_sigma_defaults(tmp_path) -> None:
    checkpoint = tmp_path / "inf.pkl"
    with checkpoint.open("wb") as handle:
        pickle.dump({"ema": InfiniteRangeToyEDMNet()}, handle)

    adapter = EDMAdapter(str(checkpoint), device="cpu")
    assert adapter.sigma_min() == 0.002
    assert adapter.sigma_max() == 80.0
