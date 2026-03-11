from __future__ import annotations

import torch


def constant(value: float, *, device: torch.device | str = "cpu", dtype: torch.dtype = torch.float32) -> torch.Tensor:
    return torch.as_tensor(value, device=device, dtype=dtype)
