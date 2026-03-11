from __future__ import annotations

import io
import urllib.request
from dataclasses import dataclass
from pathlib import Path


class EasyDict(dict):
    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def open_url(path_or_url: str):
    path = Path(path_or_url)
    if path.exists():
        return path.open("rb")
    response = urllib.request.urlopen(path_or_url)
    return io.BytesIO(response.read())
