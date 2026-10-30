"""Write-scope ownership guard (host-evidence dialect)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping, Sequence


class OwnershipError(RuntimeError):
    """Write outside declared scope or overlapping scopes."""


@dataclass(frozen=True)
class WriteScope:
    agent: str
    sub_fev: str
    roots: tuple[str, ...]

    def covers(self, relative_path: str) -> bool:
        rel = _norm(relative_path)
        for root in self.roots:
            prefix = _norm(root)
            if rel == prefix or rel.startswith(prefix + "/"):
                return True
        return False


class OwnershipGuard:
    """Detect overlapping write scopes and unauthorized path changes."""

    def __init__(self, scopes: Sequence[WriteScope]) -> None:
        self.scopes = tuple(scopes)
        self._check_no_overlap()

    def _check_no_overlap(self) -> None:
        for i, left in enumerate(self.scopes):
            for right in self.scopes[i + 1 :]:
                for a in left.roots:
                    for b in right.roots:
                        if _overlaps(a, b):
                            raise OwnershipError(
                                f"overlapping write scopes: {left.agent}:{a} vs {right.agent}:{b}"
                            )

    def owner_for(self, relative_path: str) -> WriteScope | None:
        for scope in self.scopes:
            if scope.covers(relative_path):
                return scope
        return None

    def assert_allowed(self, agent: str, relative_paths: Iterable[str]) -> None:
        for path in relative_paths:
            owner = self.owner_for(path)
            if owner is None:
                raise OwnershipError(f"path not in any write_scope: {path}")
            if owner.agent != agent:
                raise OwnershipError(
                    f"unauthorized write by {agent} on {path} (owned by {owner.agent})"
                )

    def detect_unauthorized_changes(
        self,
        agent: str,
        changed_paths: Iterable[str],
    ) -> list[str]:
        bad: list[str] = []
        for path in changed_paths:
            owner = self.owner_for(path)
            if owner is None or owner.agent != agent:
                bad.append(_norm(path))
        return bad

    def refuse_integration(self, agent: str, changed_paths: Iterable[str]) -> None:
        bad = self.detect_unauthorized_changes(agent, changed_paths)
        if bad:
            raise OwnershipError(
                "refuse integration: unauthorized paths "
                + ", ".join(sorted(bad))
            )

    def to_dict(self) -> list[dict[str, object]]:
        return [
            {"agent": s.agent, "sub_fev": s.sub_fev, "roots": list(s.roots)}
            for s in self.scopes
        ]

    @classmethod
    def from_mapping(cls, items: Sequence[Mapping[str, object]]) -> OwnershipGuard:
        scopes = [
            WriteScope(
                agent=str(item["agent"]),
                sub_fev=str(item["sub_fev"]),
                roots=tuple(str(r) for r in item["roots"]),  # type: ignore[arg-type]
            )
            for item in items
        ]
        return cls(scopes)

    def dump(self, path: str | Path) -> Path:
        p = Path(path)
        p.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return p


def snapshot_paths(root: str | Path, relative_roots: Sequence[str]) -> dict[str, str]:
    """Map relative file path -> sha256 for files under given roots."""
    from .provenance import sha256_file

    base = Path(root)
    out: dict[str, str] = {}
    for rel_root in relative_roots:
        target = base / rel_root
        if not target.exists():
            continue
        if target.is_file():
            key = _norm(rel_root)
            out[key] = sha256_file(target)
            continue
        for file_path in target.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(base).as_posix()
                out[rel] = sha256_file(file_path)
    return out


def diff_snapshots(
    before: Mapping[str, str],
    after: Mapping[str, str],
) -> list[str]:
    changed: list[str] = []
    keys = set(before) | set(after)
    for key in sorted(keys):
        if before.get(key) != after.get(key):
            changed.append(key)
    return changed


def _norm(path: str) -> str:
    text = path.replace("\\", "/").strip("/")
    return str(PurePosixPath(text))


def _overlaps(a: str, b: str) -> bool:
    left = _norm(a)
    right = _norm(b)
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")
