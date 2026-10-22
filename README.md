# Việc 1 — Input & thiết lập bài toán

Người nhận: **Nguyễn Đức Tiến** (hạn 22/10). Folder này là phần dùng chung: nạp đề, kiểm tra lời giải, đăng ký thuật toán.

```
Viec-1/
├── core.py                       # nạp đề + kiểm lời giải + registry thuật toán
├── inputs/
│   ├── star_battle/              # 5x5, 6x6, 8x8, 10x10 + 1 bản shapeless mẫu
│   └── light_up/                 # 7x7, 10x10, 14x14
└── README.md
```

Chạy tự kiểm:

```bash
cd Viec-1
python3 core.py      # đọc 3 puzzle mẫu, kiểm lời giải, in OK
```

Yêu cầu: **Python 3.10+** (dùng `X | None`), không cài thêm thư viện.

## 0. Quy ước đặt tên — dùng chung cho cả 2 bài

```
<cạnh>-<loại>-<số>.txt
<cạnh>-<loại>-<số>.sol.txt     # chỉ file mẫu mới có lời giải kèm theo
```

| Phần | Giá trị | Ví dụ |
|---|---|---|
| `cạnh` | `5x5`, `6x6`, `7x7`, `8x8`, `10x10`, `14x14` | `10x10` |
| `loại` | `easy` · `normal` · `hard` · `shapeless` | `normal` |
| `số` | `01`, `02`, … đánh từ 1; `sample` cho đề mẫu | `02` |

Ví dụ: `star_battle/10x10-normal-01.txt`, `light_up/14x14-normal-02.txt`, `star_battle/6x6-shapeless-sample.txt`.

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

problem = core.load("Viec-1/inputs/light_up/7x7-normal-01.txt")
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

## 5. Trạng thái

- [x] `core.py` nạp đề + kiểm lời giải, chạy được
- [x] 3 puzzle mẫu kèm lời giải: 5×5, 6×6 Shapeless, Light Up 7×7
- [x] Định dạng input thống nhất cho cả 2 bài, kể cả Shapeless
- [x] Hợp đồng `core.register` / `core.solve` cho 4 thuật toán
- [x] Quy ước đặt tên thống nhất (mục 0)
- [x] Bộ input chính thức: 2 đề mỗi cỡ

| Bài | Cỡ | Số đề | Ghi chú |
|---|---|---|---|
| Star Battle | 5×5 / 1★ | 2 | Normal |
| Star Battle | 6×6 / 1★ | 2 | Normal |
| Star Battle | 8×8 / 1★ | 2 | Normal |
| Star Battle | 10×10 / 2★ | 2 | Normal |
| Star Battle | 6×6 / 1★ Shapeless | 1 | chỉ là mẫu |
| Light Up | 7×7 | 2 | Normal |
| Light Up | 10×10 | 2 | Normal |
| Light Up | 14×14 | 2 | Normal |

- [ ] Mỗi cỡ 3 đề (hiện 2) — thêm khi cần cho bảng số liệu dày hơn
- [ ] Bổ sung Shapeless 8×8 và 10×10 nếu báo cáo cần

> [!warning] Phát hành input là chốt hạ
> V2 và V3 phải chạy **đúng bộ file này**. Thêm/bớt/đổi tên file sau 22/10 là cả hai phải chạy lại từ đầu.

---

*Liên quan: [[03 - Ví dụ & Bài tập/BTL1/Phan-cong.md]] · [[03 - Ví dụ & Bài tập/BTL1/V3-Heuristic.md]]*
