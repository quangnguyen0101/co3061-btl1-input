# Việc 1 — Input & thiết lập bài toán

```
Viec-1/
├── core.py                    # nạp đề + kiểm lời giải + registry thuật toán
├── inputs/
│   ├── star_battle/           # sb-*.txt
│   └── light_up/              # lu-*.txt
└── README.md
```

Chạy tự kiểm:

```bash
cd Viec-1
python3 core.py      # đọc 3 đề mẫu, kiểm lời giải, in OK
```

Yêu cầu: **Python 3.10+** (dùng `X | None`), không cài thêm thư viện.

## 0. Quy ước đặt tên — dùng chung cho cả 2 bài

```
<sb|lu>-<cạnh>-<loại>-<số>.txt
<sb|lu>-<cạnh>-<loại>-<số>.sol.txt     # chỉ đề mẫu mới có lời giải kèm theo
```

| Phần | Giá trị | Ví dụ |
|---|---|---|
| tiền tố | `sb` = Star Battle · `lu` = Light Up | `sb` |
| `cạnh` | `5x5`, `6x6`, `7x7`, `8x8`, `10x10`, `14x14` | `10x10` |
| `loại` | `easy` · `normal` · `hard` · `shapeless` | `normal` |
| `số` | `01`, `02`, … đánh từ 1; `sample` cho đề mẫu | `02` |

Ví dụ: `star_battle/sb-10x10-normal-01.txt`, `light_up/lu-14x14-hard-02.txt`, `star_battle/sb-6x6-shapeless-sample.txt`.

Số sao **không** ghi vào tên — suy ra từ cỡ (5×5/6×6/8×8 → 1★, 10×10 → 2★, 14×14 → 3★).

---

## 1. Định dạng input

### Star Battle — bản có vùng

```
size 5
stars 1
regions
1 1 3 3 3
1 1 4 3 3
2 1 4 4 5
2 2 4 4 5
2 2 5 5 5
```

`size` = cạnh lưới, `stars` = số sao mỗi hàng/cột/vùng, `regions` = lưới số nguyên, mỗi số là một vùng (đánh từ 1).

### Star Battle — bản Shapeless

```
size 6
stars 1
walls
. X . . . .
X . . . . .
. . . . . .
X X X X X .
. . . . . .
. X . . . .
```

Không có section `regions`. `X` = ô bị khoét (không tồn tại), `.` = ô chơi được.

### Light Up

```
size 7
grid
.......
.3.....
...#...
...1.1#
...##.#
.0.....
.#....2
```

`.` ô trắng · `#` ô đen không số · `0`–`4` ô đen có số.

Không có chú thích trong file — `#` là ô đen nên không dùng làm ký hiệu comment được.

## 2. Định dạng lời giải

Cùng cỡ lưới, mỗi ô là `.` hoặc `*` (`*` = một sao, hoặc một bóng đèn):

```
. * . . .
. . . * .
* . . . .
. . * . .
. . . . *
```

## 3. Dùng `core.py`

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Viec-1"))
import core

problem = core.load("Viec-1/inputs/light_up/lu-7x7-normal-01.txt")
print(type(problem).__name__)        # LightUp
print(core.check(problem, nuggets))   # [] nghĩa là lời giải hợp lệ
```

Trả về:

| Hàm | Kết quả |
|---|---|
| `core.load(path)` | `StarBattle` hoặc `LightUp` (frozen dataclass) |
| `core.load_solution(path)` | `set[(row, col)]`, chỉ số từ 0 |
| `core.check(problem, placements)` | `list[str]` lỗi; rỗng = hợp lệ |

Thuộc tính hữu ích:

- `StarBattle`: `size`, `stars`, `regions`, `walls`, `shapeless`, `region_count`, `is_cell(r, c)`, `cells()`
- `LightUp`: `size`, `grid`, `is_black(r, c)`, `clue(r, c)` (trả `None` nếu không phải ô số)

## 4. Thêm thuật toán

```python
import core

@core.register("dfs")
def solve(problem, **kwargs):
    ...
    return {"solution": ..., "expanded": 0, "steps": []}
```

`core.solve(problem, "dfs")` gọi lại theo tên. Tên trùng sẽ báo lỗi ngay.

Quy ước chung cho mọi thuật toán (V2, V3, V4 cùng đọc):

| Trường | Bắt buộc |
|---|---|
| `solution`: tập `(row, col)`, hoặc `None` nếu vô nghiệm/timeout | ✅ |
| `expanded`: số node đã mở rộng | ✅ |
| `generated`, `frontier_peak`: số node đã sinh, đỉnh của OPEN | nên có |
| `steps`: log từng bước để dựng demo | ✅ |

## 5. Bộ input

Toàn bộ lấy từ trang chính thức, mỗi dòng là `?size=<n>` trên site tương ứng.

| Bài | Cỡ / số sao | easy | normal | hard |
|---|---|---|---|---|
| Star Battle | 5×5 / 1★ | — | 2 | — |
| Star Battle | 6×6 / 1★ | — | 2 | 2 |
| Star Battle | 8×8 / 1★ | — | 2 | 2 |
| Star Battle | 10×10 / 2★ | — | 2 | 2 |
| Star Battle | 14×14 / 3★ | — | 2 | 2 |
| Light Up | 7×7 | 2 | 2 | 2 |
| Light Up | 10×10 | 2 | 2 | 2 |
| Light Up | 14×14 | 2 | 2 | 2 |

Site không có bản Star Battle Easy, nên cột đó để trống.

Nguồn (tham số `size` của site):

| Bài | easy | normal | hard |
|---|---|---|---|
| Star Battle | — | 0 → 5×5, 1 → 6×6, 3 → 8×8, 5 → 10×10, 7 → 14×14 | 2 → 6×6, 4 → 8×8, 6 → 10×10, 8 → 14×14 |
| Light Up | 0 → 7×7, 3 → 10×10, 6 → 14×14 | 1 → 7×7, 4 → 10×10, 7 → 14×14 | 2 → 7×7, 5 → 10×10, 8 → 14×14 |

Đề mẫu (có `.sol.txt` để tự kiểm): `sb-5x5-normal-sample`, `sb-6x6-shapeless-sample`, `lu-7x7-normal-sample`.

- [x] `core.py` nạp đề + kiểm lời giải, chạy được
- [x] Định dạng input thống nhất cho cả 2 bài, kể cả Shapeless
- [x] Hợp đồng `core.register` / `core.solve` cho 4 thuật toán
- [x] Quy ước đặt tên thống nhất (mục 0)
- [x] 36 đề chính thức, phủ easy/normal/hard
- [ ] Shapeless 8×8 và 10×10 nếu báo cáo cần

> [!warning] Phát hành input là chốt hạ
> V2 và V3 phải chạy **đúng bộ file này**. Thêm/bớt/đổi tên file sau 22/10 là cả hai phải chạy lại từ đầu.

---

*Liên quan: [[03 - Ví dụ & Bài tập/BTL1/Phan-cong.md]] · [[03 - Ví dụ & Bài tập/BTL1/V3-Heuristic.md]]*
