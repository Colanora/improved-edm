from __future__ import annotations

from pathlib import Path

from paper_eval import (
    SeedBlock,
    build_fid_command,
    build_generate_command,
    distributed_prefix,
    parse_fid,
    seed_blocks,
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
        upstream_root=Path("/tmp/upstream"),
        outdir=Path("/tmp/out"),
        block=SeedBlock(start=0, end=49_999),
        checkpoint="https://example.com/model.pkl",
        steps=18,
        batch_size=64,
    )
    assert command[-12:] == [
        "/tmp/upstream/generate.py",
        "--outdir",
        "/tmp/out",
        "--seeds",
        "0-49999",
        "--subdirs",
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
