from __future__ import annotations

import pickle

import numpy as np
import torch

import prepare
import run
from tests.fakes import ToyEDMNet
from third_party.edm.minimal_fid import extract_features


def write_ref_stats(path, images: torch.Tensor) -> None:
    features = extract_features(images).cpu().numpy()
    mu = features.mean(axis=0)
    sigma = np.cov(features, rowvar=False)
    np.savez(path, mu=mu, sigma=sigma)


def test_prepare_manifest_fallback() -> None:
    text = """
checkpoint_uncond:
  filename: edm.pkl
  sha256: ""
  primary_url: https://example.com/edm.pkl
  mirror_repo: your-org/assets
checkpoint_cond:
  filename: edm-cond.pkl
  sha256: ""
  primary_url: https://example.com/edm-cond.pkl
  mirror_repo: your-org/assets
fid_ref:
  filename: cifar10.npz
  sha256: ""
  primary_url: https://example.com/cifar10.npz
  mirror_repo: your-org/assets
""".strip()
    parsed = prepare._load_manifest_fallback(text)
    assert parsed["checkpoint_uncond"]["filename"] == "edm.pkl"
    assert parsed["checkpoint_cond"]["filename"] == "edm-cond.pkl"
    assert parsed["fid_ref"]["primary_url"].endswith("cifar10.npz")


def test_evaluate_sampler_smoke(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SAMPLER_AUTORESEARCH_ALLOW_APPROX_FID", "1")
    checkpoint = tmp_path / "toy.pkl"
    with checkpoint.open("wb") as handle:
        pickle.dump({"ema": ToyEDMNet()}, handle)

    ref_path = tmp_path / "ref.npz"
    ref_images = torch.randn(8, 3, 32, 32)
    write_ref_stats(ref_path, ref_images)

    seed_path = tmp_path / "seeds_proxy.txt"
    seed_path.write_text("\n".join(str(i) for i in range(8)) + "\n", encoding="utf-8")

    fid_by_nfe, frontier_score = run.evaluate_sampler(
        sampler_name="heun",
        split="proxy",
        nfes=(5, 9, 11, 13),
        device=torch.device("cpu"),
        checkpoint_path=checkpoint,
        ref_path=ref_path,
        seed_path=seed_path,
        num_images=8,
        batch_size=4,
        save_previews=False,
        save_diagnostics=False,
    )

    assert set(fid_by_nfe) == {5, 9, 11, 13}
    assert np.isfinite(frontier_score)


def test_resolve_process_count_uses_all_visible_cuda_gpus_by_default(monkeypatch) -> None:
    monkeypatch.setattr(run.torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(run.torch.cuda, "device_count", lambda: 4)
    assert run.resolve_process_count(torch.device("cuda"), requested_gpus=0) == 4


def test_resolve_process_count_keeps_cpu_single_process() -> None:
    assert run.resolve_process_count(torch.device("cpu"), requested_gpus=8) == 1


def test_shard_seed_batches_distributes_one_seed_set_across_ranks() -> None:
    seeds = list(range(10))
    all_batches, rank_batches, prefix_counts = run.shard_seed_batches(seeds, batch_size=2, world_size=3, rank=1)
    assert all_batches == [[0, 1], [2, 3], [4, 5], [6, 7], [8], [9]]
    assert rank_batches == [[2, 3], [8]]
    assert prefix_counts == [0, 2, 4, 6, 8, 9, 10]
