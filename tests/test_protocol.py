from __future__ import annotations

import torch

from sampler_protocol import build_karras_schedule, latent_batch_from_seeds, parse_nfe_list


def test_parse_nfe_list_defaults() -> None:
    assert parse_nfe_list("") == (5, 9, 11, 13)


def test_build_karras_schedule_has_terminal_zero() -> None:
    sigmas = build_karras_schedule(nfe=5, sigma_min=0.002, sigma_max=80.0, device="cpu")
    assert sigmas.shape[0] == 6
    assert sigmas[-1].item() == 0.0
    assert torch.all(sigmas[:-1] > 0)


def test_latent_batch_from_seeds_is_deterministic() -> None:
    batch_a = latent_batch_from_seeds([1, 2, 3], (3, 32, 32), device="cpu")
    batch_b = latent_batch_from_seeds([1, 2, 3], (3, 32, 32), device="cpu")
    assert torch.equal(batch_a, batch_b)
