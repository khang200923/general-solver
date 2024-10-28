from dataclasses import dataclass
import random
from typing import Any, Dict
from pathlib import Path

def create_storage(storage: str):
    path = Path("storages") / storage
    if not path.exists():
        path.mkdir(parents=True)

@dataclass
class App:
    storage: str

    def create(self, name: str) -> str:
        id = str(random.randrange(2**64))
        with (Path("storages") / self.storage / f"{id}.md").open("wt", encoding="utf-16") as f:
            f.write(f"- Problem: {name}")
        return id

    def edit(self, problem: str, val: str):
        with (Path("storages") / self.storage / f"{problem}.md").open("wt", encoding="utf-16") as f:
            f.write(val)

    def read(self, problem: str) -> str:
        with (Path("storages") / self.storage / f"{problem}.md").open("rt", encoding="utf-16") as f:
            return f.read()
