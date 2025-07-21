"""Favorite color storage utilities."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import json


@dataclass
class ColorFavorite:
    """Named RGB color favorite."""

    name: str
    r: int
    g: int
    b: int

    def as_tuple(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b


class FavoritesManager:
    """Manage persistence of color favorites in a JSON file."""

    def __init__(self, path: str | Path = "favorites.json") -> None:
        self.path = Path(path)
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.favorites: Dict[str, ColorFavorite] = {
                item["name"]: ColorFavorite(**item) for item in data
            }
        else:
            self.favorites = {}

    def _save(self) -> None:
        data = [asdict(fav) for fav in self.favorites.values()]
        self.path.write_text(json.dumps(data))

    def add(self, name: str, r: int, g: int, b: int) -> None:
        self.favorites[name] = ColorFavorite(name, r, g, b)
        self._save()

    def remove(self, name: str) -> None:
        if name in self.favorites:
            del self.favorites[name]
            self._save()

    def list(self) -> List[ColorFavorite]:
        return list(self.favorites.values())

    def get(self, name: str) -> ColorFavorite | None:
        return self.favorites.get(name)
