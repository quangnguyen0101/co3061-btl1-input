"""Doc de va kiem tra loi giai cho Star Battle va Light Up.

Khong chua thuat toan tim kiem. Moi nguoi them file vao solvers/.
Chay thu: python3 -m core
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


class ParseError(ValueError):
    """File input sai dinh dang."""


WALL = frozenset()


@dataclass(frozen=True)
class StarBattle:
    size: int
    stars: int
    regions: tuple[tuple[int, ...], ...] | None = None
    walls: frozenset[tuple[int, int]] = WALL

    @property
    def shapeless(self) -> bool:
        return self.regions is None

    @property
    def region_count(self) -> int:
        if self.regions is None:
            return 0
        return max(max(row) for row in self.regions)

    def is_cell(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size and (r, c) not in self.walls

    def cells(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.is_cell(r, c)]


@dataclass(frozen=True)
class LightUp:
    size: int
    grid: tuple[str, ...]

    def is_black(self, r: int, c: int) -> bool:
        return self.grid[r][c] != "."

    def clue(self, r: int, c: int) -> int | None:
        ch = self.grid[r][c]
        return int(ch) if ch.isdigit() else None

    def is_cell(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size


def _sections(path: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    key = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        head = line.split()
        if len(head) == 1 and head[0].isalpha():
            key = head[0]
            out[key] = []
        elif len(head) == 2 and head[0] == "size":
            out["size"] = [head[1]]
        elif len(head) == 2 and head[0] == "stars":
            out["stars"] = [head[1]]
        elif key is None:
            raise ParseError(f"{path}: dong khong hop le: {raw!r}")
        else:
            out[key].append(line)
    return out


def _int(sections: dict[str, list[str]], key: str, path: Path) -> int:
    if key not in sections:
        raise ParseError(f"{path}: thieu dong '{key}'")
    try:
        return int(sections[key][0])
    except ValueError:
        raise ParseError(f"{path}: '{key}' phai la so nguyen") from None


def load(path: str | Path) -> StarBattle | LightUp:
    path = Path(path)
    sections = _sections(path)
    size = _int(sections, "size", path)

    if "grid" in sections:
        rows = sections["grid"]
        if len(rows) != size:
            raise ParseError(f"{path}: can {size} dong grid, co {len(rows)}")
        for i, row in enumerate(rows):
            if len(row) != size:
                raise ParseError(f"{path}: dong grid {i + 1} phai dai {size}")
            if any(ch not in ".#0123456789" for ch in row):
                raise ParseError(f"{path}: dong grid {i + 1} co ky tu la")
        return LightUp(size=size, grid=tuple(rows))

    stars = _int(sections, "stars", path)
    if "regions" in sections:
        rows = sections["regions"]
        if len(rows) != size:
            raise ParseError(f"{path}: can {size} dong regions, co {len(rows)}")
        regions = tuple(tuple(int(x) for x in row.split()) for row in rows)
        for row in regions:
            if len(row) != size:
                raise ParseError(f"{path}: moi dong regions phai co {size} so")
        return StarBattle(size=size, stars=stars, regions=regions)

    if "walls" in sections:
        walls = frozenset(
            (r, c)
            for r, row in enumerate(sections["walls"])
            for c, ch in enumerate(row.split())
            if ch in ("X", "x")
        )
        if len(sections["walls"]) != size:
            raise ParseError(f"{path}: can {size} dong walls")
        return StarBattle(size=size, stars=stars, walls=walls)

    raise ParseError(f"{path}: thieu section 'regions', 'walls' hoac 'grid'")


def load_solution(path: str | Path) -> set[tuple[int, int]]:
    """Doc file loi giai: moi o co '*' la mot quan (sao hoac bong den)."""
    path = Path(path)
    return {
        (r, c)
        for r, line in enumerate(path.read_text(encoding="utf-8").splitlines())
        for c, ch in enumerate(line.split())
        if ch == "*"
    }


def check(problem: StarBattle | LightUp, placements) -> list[str]:
    """Tra ve danh sach loi. Rong = loi giai hop le."""
    if isinstance(problem, StarBattle):
        return check_star_battle(problem, placements)
    return check_light_up(problem, placements)


def _king_neighbours(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= 1


def check_star_battle(p: StarBattle, stars) -> list[str]:
    stars = set(stars)
    errors: list[str] = []
    need = p.size * p.stars

    if len(stars) != need:
        errors.append(f"can {need} sao, co {len(stars)}")

    for cell in stars:
        if not p.is_cell(*cell):
            errors.append(f"sao nam ngoai ban co hoac trong tuong: {cell}")

    stars = {s for s in stars if p.is_cell(*s)}
    ordered = sorted(stars)
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if _king_neighbours(a, b):
                errors.append(f"hai sao ke nhau (ke ca cheo): {a} va {b}")

    for r in range(p.size):
        got = sum(1 for s in stars if s[0] == r)
        if got != p.stars:
            errors.append(f"hang {r + 1} co {got} sao, can {p.stars}")

    for c in range(p.size):
        got = sum(1 for s in stars if s[1] == c)
        if got != p.stars:
            errors.append(f"cot {c + 1} co {got} sao, can {p.stars}")

    if p.regions is not None:
        for region in range(1, p.region_count + 1):
            got = sum(1 for s in stars if p.regions[s[0]][s[1]] == region)
            if got != p.stars:
                errors.append(f"vung {region} co {got} sao, can {p.stars}")

    return errors


def _ray(p: LightUp, r: int, c: int, dr: int, dc: int):
    r += dr
    c += dc
    while p.is_cell(r, c):
        yield r, c
        if p.is_black(r, c):
            return
        r += dr
        c += dc


def check_light_up(p: LightUp, bulbs) -> list[str]:
    bulbs = set(bulbs)
    errors: list[str] = []

    for cell in bulbs:
        r, c = cell
        if not p.is_cell(r, c):
            errors.append(f"bong den ngoai ban co: {cell}")
        elif p.is_black(r, c):
            errors.append(f"bong den dat tren o den: {cell}")

    for r, c in sorted(bulbs):
        if not p.is_cell(r, c) or p.is_black(r, c):
            continue
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for rr, cc in _ray(p, r, c, dr, dc):
                if (rr, cc) in bulbs:
                    errors.append(f"hai bong den chieu nhau: {(r, c)} va {(rr, cc)}")
                    break
                if p.is_black(rr, cc):
                    break

    for r in range(p.size):
        for c in range(p.size):
            clue = p.clue(r, c)
            if clue is None:
                continue
            around = sum(1 for d in ((-1, 0), (1, 0), (0, -1), (0, 1)) if (r + d[0], c + d[1]) in bulbs)
            if around != clue:
                errors.append(f"o so ({r + 1},{c + 1}) can {clue} bong, co {around}")

    lit = set(bulbs)
    for r, c in bulbs:
        if not p.is_cell(r, c) or p.is_black(r, c):
            continue
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for rr, cc in _ray(p, r, c, dr, dc):
                if p.is_black(rr, cc):
                    break
                lit.add((rr, cc))

    for r in range(p.size):
        for c in range(p.size):
            if not p.is_black(r, c) and (r, c) not in lit:
                errors.append(f"o trang ({r + 1},{c + 1}) chua duoc chieu sang")

    return errors


# --- dang ky thuat toan -----------------------------------------------------

_SOLVERS: dict[str, Callable[..., object]] = {}


def register(name: str):
    """Dung lam decorator: @register('dfs') tren ham solve(problem, **kw)."""

    def wrap(fn):
        if name in _SOLVERS:
            raise ValueError(f"thuat toan '{name}' da duoc dang ky")
        _SOLVERS[name] = fn
        return fn

    return wrap


def solvers() -> list[str]:
    return sorted(_SOLVERS)


def solve(problem: StarBattle | LightUp, algo: str, **kwargs):
    if algo not in _SOLVERS:
        raise KeyError(f"khong co thuat toan '{algo}'. Dang co: {solvers()}")
    return _SOLVERS[algo](problem, **kwargs)


if __name__ == "__main__":
    root = Path(__file__).parent
    pairs = [
        ("inputs/star_battle/5x5-normal-sample.txt", "inputs/star_battle/5x5-normal-sample.sol.txt"),
        ("inputs/star_battle/6x6-shapeless-sample.txt", "inputs/star_battle/6x6-shapeless-sample.sol.txt"),
        ("inputs/light_up/7x7-normal-sample.txt", "inputs/light_up/7x7-normal-sample.sol.txt"),
    ]
    for inp, sol in pairs:
        problem = load(root / inp)
        placements = load_solution(root / sol)
        errors = check(problem, placements)
        assert not errors, f"{inp}: {errors}"
        print(f"OK {inp} ({type(problem).__name__}, {len(placements)} quan)")
