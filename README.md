# Việc 1 — Input & thiết lập bài toán

```
Viec-1/
├── core.py                    # nạp đề + kiểm lời giải + registry thuật toán
├── inputs/
│   ├── star_battle/           # 25 file sb-*.txt
│   └── light_up/              # 23 file lu-*.txt
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
| `cạnh` | `5x5` … `14x14`, và `17x17`, `21x21`, `25x25`, `30x30`, `30x40`, `40x50` | `10x10` |
| `loại` | `easy` · `normal` · `hard` · `shapeless` · `daily` · `weekly` · `monthly` | `normal` |
| `số` | `01`, `02`, … đánh từ 1; `sample` cho đề mẫu | `02` |

Ví dụ: `star_battle/sb-10x10-normal-01.txt`, `light_up/lu-14x14-hard-02.txt`, `star_battle/sb-6x6-shapeless-sample.txt`, `light_up/lu-40x50-monthly-01.txt`.

Với lưới chữ nhật, `cạnh` ghi **cột × dòng** (như site): `lu-30x40-weekly-01.txt` là 30 cột, 40 dòng.

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

Lưới không nhất thiết vuông: dòng `size` nhận 1 số (vuông) hoặc 2 số **số dòng rồi số cột**.

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
- `LightUp`: `rows`, `cols`, `grid`, `is_black(r, c)`, `clue(r, c)` (trả `None` nếu không phải ô số)

### Vẽ hình (dùng cho báo cáo)

`viz.py` vẽ đề ra ảnh, tự động vẽ luôn lời giải nếu có file `.sol.txt` cạnh đó. Cần `matplotlib` — chỉ script này cần, `core.py` vẫn chạy không thư viện.

```bash
python3 viz.py inputs/star_battle/sb-5x5-normal-sample.txt   # -> figs/sb-5x5-normal-sample.png
python3 viz.py inputs/light_up/lu-7x7-normal-01.txt -o hinh.png --dpi 300
python3 viz.py inputs/star_battle -o figs        # vẽ cả thư mục, tự tìm .sol.txt
python3 viz.py inputs/light_up -o hinh.svg                  # SVG/PDF cũng được
```

Star Battle tô màu từng vùng; bản Shapeless tô ô tường đen. Light Up tô ô đen, in số gợi ý màu trắng, bóng đèn màu vàng.

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

### Bộ đặc biệt

Ba bộ này **đổi đề theo ngày/tuần/tháng**, nên file dưới đây chỉ là bản chụp ngày **22/10/2026** — muốn tái lập số liệu thì dùng đúng file này, đừng lấy lại từ site.

| Bài | File | Cỡ | Số sao |
|---|---|---|---|
| Star Battle | `sb-17x17-daily-01.txt` | 17×17 | 4★ |
| Star Battle | `sb-21x21-weekly-01.txt` | 21×21 | 5★ |
| Star Battle | `sb-25x25-monthly-01.txt` | 25×25 | 6★ |
| Light Up | `lu-30x30-daily-01.txt` | 30×30 | — |
| Light Up | `lu-30x40-weekly-01.txt` | 30 cột × 40 dòng | — |
| Light Up | `lu-40x50-monthly-01.txt` | 40 cột × 50 dòng | — |

Nguồn: Star Battle `?size=9/10/11`, Light Up `?size=13/12/14`.

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
- [x] 36 đề chính thức (easy/normal/hard) + 6 đề đặc biệt daily/weekly/monthly
- [ ] Shapeless 8×8 và 10×10 nếu báo cáo cần
- [ ] 25×25 Light Up: site chỉ có bản đặc biệt (30×30 trở lên), không có 25×25

> [!warning] Phát hành input là chốt hạ
> V2 và V3 phải chạy **đúng bộ file này**. Thêm/bớt/đổi tên file sau 22/10 là cả hai phải chạy lại từ đầu.

---

*Liên quan: [[03 - Ví dụ & Bài tập/BTL1/Phan-cong.md]] · [[03 - Ví dụ & Bài tập/BTL1/V3-Heuristic.md]]*
