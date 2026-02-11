"""Helpers orientados a objetos para manejar la configuracion del proyecto."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, MutableMapping, Union

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = _REPO_ROOT / "config" / "settings.json"
PathLike = Union[str, Path]


def _resolve_path(path: PathLike) -> Path:
    return Path(path).expanduser().resolve()


def _deep_merge(base: MutableMapping[str, Any], updates: MutableMapping[str, Any]) -> None:
    for key, value in updates.items():
        if (
            key in base
            and isinstance(base[key], MutableMapping)
            and isinstance(value, MutableMapping)
        ):
            _deep_merge(base[key], value)
        else:
            base[key] = value


class Config:

    def __init__(self, path: PathLike = DEFAULT_CONFIG_PATH, auto_load: bool = True):
        self.path = _resolve_path(path)
        self._data: Dict[str, Any] = {}
        if auto_load and self.path.exists():
            self.load()

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            raise FileNotFoundError(
                f"No existe el archivo de configuracion: {self.path}."
            )
        with self.path.open("r", encoding="utf-8") as fh:
            self._data = json.load(fh)
        return self._data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        self._data[key] = value
        if auto_save:
            self.save()

    def update(self, updates: Dict[str, Any], auto_save: bool = True) -> Dict[str, Any]:
        if not isinstance(updates, MutableMapping):
            raise TypeError("updates debe ser un diccionario")
        _deep_merge(self._data, updates)
        if auto_save:
            self.save()
        return self._data
