from __future__ import annotations

import os
import pickle
import sys
from pathlib import Path

import click
import PIL.Image
import torch
import tqdm

from samplers.official_backend import StackedRandomGenerator, parse_int_list, sample_images
from third_party.edm import dnnlib

REPO_ROOT = Path(__file__).resolve().parent
EDM_ROOT = REPO_ROOT / "third_party" / "edm"
UPSTREAM_EDM_ROOT = REPO_ROOT / "third_party" / "upstream-edm"


def _ensure_checkpoint_imports() -> None:
    for root in (UPSTREAM_EDM_ROOT, EDM_ROOT):
        root_str = str(root)
        if root.exists() and root_str not in sys.path:
            sys.path.insert(0, root_str)

    import dnnlib  # noqa: F401
    from torch_utils import persistence  # noqa: F401


def _dist_init() -> None:
    if "MASTER_ADDR" not in os.environ:
        os.environ["MASTER_ADDR"] = "localhost"
    if "MASTER_PORT" not in os.environ:
        os.environ["MASTER_PORT"] = "29500"
    if "RANK" not in os.environ:
        os.environ["RANK"] = "0"
    if "LOCAL_RANK" not in os.environ:
        os.environ["LOCAL_RANK"] = "0"
    if "WORLD_SIZE" not in os.environ:
        os.environ["WORLD_SIZE"] = "1"

    local_rank = int(os.environ.get("LOCAL_RANK", "0"))
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank)

    backend = os.environ.get("EDM_DIST_BACKEND", "")
    if not backend:
        backend = "gloo" if os.name == "nt" else "nccl"
    torch.distributed.init_process_group(backend=backend, init_method="env://")


def _dist_rank() -> int:
    return torch.distributed.get_rank() if torch.distributed.is_initialized() else 0


def _dist_world_size() -> int:
    return torch.distributed.get_world_size() if torch.distributed.is_initialized() else 1


def _dist_print0(*args, **kwargs) -> None:
    if _dist_rank() == 0:
        print(*args, **kwargs)


def sample_images_for_paper(
    *,
    sampler: str,
    net,
    latents: torch.Tensor,
    class_labels=None,
    randn_like=torch.randn_like,
    num_steps: int,
    sigma_min: float | None = None,
    sigma_max: float | None = None,
    rho: float = 7,
    S_churn: float = 0,
    S_min: float = 0,
    S_max: float = float("inf"),
    S_noise: float = 1,
) -> torch.Tensor:
    return sample_images(
        sampler_name=sampler,
        net=net,
        latents=latents,
        class_labels=class_labels,
        randn_like=randn_like,
        num_steps=num_steps,
        sigma_min=sigma_min,
        sigma_max=sigma_max,
        rho=rho,
        S_churn=S_churn,
        S_min=S_min,
        S_max=S_max,
        S_noise=S_noise,
    )


@click.command()
@click.option("--network", "network_pkl", help="Network pickle filename", metavar="PATH|URL", type=str, required=True)
@click.option("--outdir", help="Where to save the output images", metavar="DIR", type=str, required=True)
@click.option("--seeds", help="Random seeds (e.g. 1,2,5-10)", metavar="LIST", type=parse_int_list, default="0-63", show_default=True)
@click.option("--subdirs", help="Create subdirectory for every 1000 seeds", is_flag=True)
@click.option("--class", "class_idx", help="Class label  [default: random]", metavar="INT", type=click.IntRange(min=0), default=None)
@click.option("--batch", "max_batch_size", help="Maximum batch size", metavar="INT", type=click.IntRange(min=1), default=64, show_default=True)
@click.option("--sampler", "sampler_name", help="Sampler to use", metavar="heun|euler|research", type=click.Choice(["heun", "euler", "research"]), default="research", show_default=True)
@click.option("--steps", "num_steps", help="Number of sampling steps", metavar="INT", type=click.IntRange(min=1), default=18, show_default=True)
@click.option("--sigma_min", help="Lowest noise level  [default: varies]", metavar="FLOAT", type=click.FloatRange(min=0, min_open=True))
@click.option("--sigma_max", help="Highest noise level  [default: varies]", metavar="FLOAT", type=click.FloatRange(min=0, min_open=True))
@click.option("--rho", help="Time step exponent", metavar="FLOAT", type=click.FloatRange(min=0, min_open=True), default=7, show_default=True)
@click.option("--S_churn", "S_churn", help="Stochasticity strength", metavar="FLOAT", type=click.FloatRange(min=0), default=0, show_default=True)
@click.option("--S_min", "S_min", help="Stoch. min noise level", metavar="FLOAT", type=click.FloatRange(min=0), default=0, show_default=True)
@click.option("--S_max", "S_max", help="Stoch. max noise level", metavar="FLOAT", type=click.FloatRange(min=0), default="inf", show_default=True)
@click.option("--S_noise", "S_noise", help="Stoch. noise inflation", metavar="FLOAT", type=float, default=1, show_default=True)
def main(network_pkl, outdir, seeds, subdirs, class_idx, max_batch_size, sampler_name, device=torch.device("cuda"), **sampler_kwargs):
    _dist_init()
    num_batches = ((len(seeds) - 1) // (max_batch_size * _dist_world_size()) + 1) * _dist_world_size()
    all_batches = torch.as_tensor(seeds).tensor_split(num_batches)
    rank_batches = all_batches[_dist_rank() :: _dist_world_size()]

    if _dist_rank() != 0:
        torch.distributed.barrier()

    _dist_print0(f'Loading network from "{network_pkl}"...')
    _ensure_checkpoint_imports()
    with dnnlib.open_url(network_pkl) as handle:
        net = pickle.load(handle)["ema"].to(device)

    if _dist_rank() == 0:
        torch.distributed.barrier()

    _dist_print0(f'Generating {len(seeds)} images to "{outdir}"...')
    for batch_seeds in tqdm.tqdm(rank_batches, unit="batch", disable=(_dist_rank() != 0)):
        torch.distributed.barrier()
        batch_size = len(batch_seeds)
        if batch_size == 0:
            continue

        rnd = StackedRandomGenerator(device, batch_seeds)
        latents = rnd.randn([batch_size, net.img_channels, net.img_resolution, net.img_resolution], device=device)
        class_labels = None
        if net.label_dim:
            class_labels = torch.eye(net.label_dim, device=device)[rnd.randint(net.label_dim, size=[batch_size], device=device)]
        if class_idx is not None:
            class_labels[:, :] = 0
            class_labels[:, class_idx] = 1

        sampler_kwargs = {key: value for key, value in sampler_kwargs.items() if value is not None}
        images = sample_images_for_paper(
            sampler=sampler_name,
            net=net,
            latents=latents,
            class_labels=class_labels,
            randn_like=rnd.randn_like,
            **sampler_kwargs,
        )

        images_np = (images * 127.5 + 128).clip(0, 255).to(torch.uint8).permute(0, 2, 3, 1).cpu().numpy()
        for seed, image_np in zip(batch_seeds, images_np):
            image_dir = os.path.join(outdir, f"{seed - seed % 1000:06d}") if subdirs else outdir
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, f"{seed:06d}.png")
            if image_np.shape[2] == 1:
                PIL.Image.fromarray(image_np[:, :, 0], "L").save(image_path)
            else:
                PIL.Image.fromarray(image_np, "RGB").save(image_path)

    torch.distributed.barrier()
    _dist_print0("Done.")


if __name__ == "__main__":
    main()
