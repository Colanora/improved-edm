from __future__ import annotations

from pathlib import Path

import pytest

import paper_eval
from paper_eval import (
    LEGACY_RESULTS_HEADER,
    LOCAL_REF_PATH,
    LOCAL_TARGETS,
    REMOTE_REF_URL,
    REMOTE_TARGETS,
    RESULTS_HEADER,
    SeedBlock,
    build_fid_command,
    build_generate_command,
    distributed_prefix,
    default_checkpoint_for_target,
    default_ref,
    ensure_results_file,
    parse_fid,
    seed_blocks,
    validate_sampler_target,
)


def test_seed_blocks_follow_official_layout() -> None:
    blocks = seed_blocks(seed_start=0, repeats=3, block_size=50_000)
    assert blocks == [
        SeedBlock(start=0, end=49_999),
        SeedBlock(start=50_000, end=99_999),
        SeedBlock(start=100_000, end=149_999),
    ]


def test_distributed_prefix_uses_torchrun_module() -> None:
    prefix = distributed_prefix("python3", 2)
    assert prefix == ["python3", "-m", "torch.distributed.run", "--standalone", "--nproc_per_node", "2"]


def test_build_generate_command_matches_upstream_cli() -> None:
    command = build_generate_command(
        python_executable="python3",
        gpus=1,
        sampler="research",
        outdir=Path("/tmp/out"),
        block=SeedBlock(start=0, end=49_999),
        checkpoint="https://example.com/model.pkl",
        steps=18,
        batch_size=64,
    )
    assert command[-14:] == [
        str(paper_eval.PAPER_GENERATE_PATH),
        "--outdir",
        "/tmp/out",
        "--seeds",
        "0-49999",
        "--subdirs",
        "--sampler",
        "research",
        "--steps",
        "18",
        "--batch",
        "64",
        "--network",
        "https://example.com/model.pkl",
    ]


def test_build_fid_command_matches_upstream_cli() -> None:
    command = build_fid_command(
        python_executable="python3",
        gpus=1,
        upstream_root=Path("/tmp/upstream"),
        images_path=Path("/tmp/out"),
        ref="https://example.com/ref.npz",
        batch_size=64,
        num_expected=50_000,
    )
    assert command[-10:] == [
        "/tmp/upstream/fid.py",
        "calc",
        "--images",
        "/tmp/out",
        "--ref",
        "https://example.com/ref.npz",
        "--num",
        "50000",
        "--batch",
        "64",
    ]


def test_parse_fid_reads_last_numeric_line() -> None:
    stdout = "Loading dataset reference statistics...\nCalculating FID...\n1.79\n"
    assert parse_fid(stdout) == 1.79


def test_default_checkpoint_prefers_local_asset(tmp_path, monkeypatch) -> None:
    local_path = tmp_path / "edm-uncond.pkl"
    local_path.write_bytes(b"test")
    monkeypatch.setitem(LOCAL_TARGETS, "uncond", local_path)
    assert default_checkpoint_for_target("uncond") == str(local_path)


def test_default_checkpoint_falls_back_to_remote(monkeypatch, tmp_path) -> None:
    missing_path = tmp_path / "missing-cond.pkl"
    monkeypatch.setitem(LOCAL_TARGETS, "cond", missing_path)
    assert default_checkpoint_for_target("cond") == REMOTE_TARGETS["cond"]


def test_default_ref_prefers_local_asset(tmp_path, monkeypatch) -> None:
    local_ref = tmp_path / "cifar10-32x32.npz"
    local_ref.write_bytes(b"test")
    monkeypatch.setattr(paper_eval, "LOCAL_REF_PATH", local_ref)
    assert default_ref() == str(local_ref)


def test_default_ref_falls_back_to_remote(monkeypatch, tmp_path) -> None:
    missing_ref = tmp_path / "missing.npz"
    monkeypatch.setattr(paper_eval, "LOCAL_REF_PATH", missing_ref)
    assert default_ref() == REMOTE_REF_URL


def test_ensure_results_file_migrates_legacy_rows(tmp_path, monkeypatch) -> None:
    results_path = tmp_path / "paper_results.tsv"
    results_path.write_text(
        LEGACY_RESULTS_HEADER + "abc123\tuncond\t18\t1\t1.8\t1.7\t1.9\t1.7\t12.3\tcheckpoint\tref\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(paper_eval, "PAPER_RESULTS_PATH", results_path)
    ensure_results_file()
    rows = results_path.read_text(encoding="utf-8").splitlines()
    assert rows[0] == RESULTS_HEADER.rstrip("\n")
    assert rows[1].split("\t")[1] == "heun"


def test_validate_sampler_target_rejects_conditional_research() -> None:
    with pytest.raises(ValueError, match="not enabled"):
        validate_sampler_target(sampler="research", target="cond")
