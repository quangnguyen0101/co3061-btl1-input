"""Ve hinh puzzle tu file input (dung cho bao cao).

    python3 viz.py INPUT.txt                 # -> INPUT.png
    python3 viz.py INPUT.txt -o hinh.png
    python3 viz.py INPUT.txt --sol INPUT.sol.txt
    python3 viz.py inputs/star_battle         # ve ca thu muc
    python3 viz.py INPUT.txt -o hinh.svg --dpi 300

Can matplotlib (chi de ve, core.py van khong can gi).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import core

CELL = 0.4
GRID = "#8a8a8a"
INK = "#1a1a1a"


def _palette(n: int) -> list[tuple[float, float, float]]:
    from matplotlib.colors import hsv_to_rgb

    out = []
    for i in range(max(n, 1)):
        h = (i * 0.6180339887498949) % 1.0
        s = 0.45 if i % 2 else 0.75
        out.append(tuple(hsv_to_rgb((h, s, 0.98))))
    return out


def _figure(problem):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = problem.rows if isinstance(problem, core.LightUp) else problem.size
    cols = problem.cols if isinstance(problem, core.LightUp) else problem.size
    fig, ax = plt.subplots(figsize=(cols * CELL, rows * CELL))
    ax.set_xlim(0, cols)
    ax.set_ylim(rows, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax, plt


def _grid(ax, rows: int, cols: int, lw: float = 0.8) -> None:
    from matplotlib.patches import Rectangle

    for r in range(rows):
        for c in range(cols):
            ax.add_patch(
                Rectangle((c, r), 1, 1, fill=False, lw=lw, edgecolor=GRID, zorder=3)
            )


def _bulb(ax, r: int, c: int, size: float = 0.30) -> None:
    from matplotlib.patches import Circle

    ax.add_patch(Circle((c + 0.5, r + 0.5), size, color="#f4c430", zorder=4))
    ax.add_patch(
        Circle((c + 0.5, r + 0.5), size, fill=False, lw=0.8, edgecolor="#8a6d00", zorder=5)
    )


def _star(ax, r: int, c: int) -> None:
    ax.text(
        c + 0.5, r + 0.5, "*", ha="center", va="center_baseline",
        fontsize=17, color=INK, zorder=4,
    )


def draw(problem, solution=None, path: str | Path = "out.png", dpi: int = 150):
    from matplotlib.patches import Rectangle

    fig, ax, plt = _figure(problem)
    rows = problem.rows if isinstance(problem, core.LightUp) else problem.size
    cols = problem.cols if isinstance(problem, core.LightUp) else problem.size

    if isinstance(problem, core.StarBattle):
        if problem.walls:
            for r, c in problem.walls:
                ax.add_patch(Rectangle((c, r), 1, 1, color=INK, zorder=1))
        else:
            colors = _palette(problem.region_count)
            for r in range(rows):
                for c in range(cols):
                    ax.add_patch(
                        Rectangle((c, r), 1, 1, color=colors[problem.regions[r][c] - 1], zorder=1)
                    )
    else:
        for r in range(rows):
            for c in range(cols):
                if problem.is_black(r, c):
                    ax.add_patch(Rectangle((c, r), 1, 1, color="#3b3b3b", zorder=1))
                    clue = problem.clue(r, c)
                    if clue is not None:
                        ax.text(
                            c + 0.5, r + 0.5, str(clue), ha="center", va="center",
                            fontsize=13, color="white", fontweight="bold", zorder=4,
                        )

    _grid(ax, rows, cols)

    if solution:
        if isinstance(problem, core.LightUp):
            for r, c in solution:
                _bulb(ax, r, c)
        else:
            for r, c in solution:
                _star(ax, r, c)

    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(fig)
    return Path(path)


def _selftest() -> int:
    import tempfile

    from PIL import Image

    root = Path(__file__).parent
    inp = root / "inputs/star_battle/sb-5x5-normal-sample.txt"
    out = Path(tempfile.gettempdir()) / "viz-selftest.png"
    draw(core.load(inp), core.load_solution(inp.with_suffix(".sol.txt")), out, dpi=60)
    im = Image.open(out).convert("RGB")
    px = list(im.get_flattened_data())
    assert len(set(px)) > 10, "anh chi co mot mau"
    assert sum(1 for c in px if sum(c) < 200) > 20, "khong thay sao"
    print("OK", out, im.size)
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Ve puzzle tu file input")
    ap.add_argument("input", nargs="?", help="file .txt hoac thu muc chua cac file .txt")
    ap.add_argument("--selftest", action="store_true", help="tu kiem tra roi thoat")
    ap.add_argument("-o", "--out", help="file anh ra (.png/.svg/.pdf); mac dinh ten file input")
    ap.add_argument("--sol", help="file loi giai (.sol.txt) de ve sao / bong den")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.input:
        ap.error("thieu file hoac thu muc input")
    if args.sol and Path(args.input).is_dir():
        ap.error("--sol chi dung voi mot file; voi thu muc, dat file .sol.txt canh file de")

    src = Path(args.input)
    files = sorted(src.glob("*.txt")) if src.is_dir() else [src]
    if not files:
        print(f"khong co file .txt trong {src}")
        return 1

    if len(files) == 1 and args.out:
        outs = [args.out]
    else:
        out_dir = Path(args.out) if args.out else Path("figs")
        out_dir.mkdir(parents=True, exist_ok=True)
        outs = [out_dir / f"{f.stem}.png" for f in files]

    for f, out in zip(files, outs):
        if f.name.endswith(".sol.txt"):
            continue
        sol = None
        if args.sol:
            sol = core.load_solution(args.sol)
        elif f.with_suffix(".sol.txt").exists():
            sol = core.load_solution(f.with_suffix(".sol.txt"))
        print("ve", draw(core.load(f), sol, out, args.dpi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
