# Mô hình hoá — Star Battle & Light Up

Cả hai bài đều là bài toán *gán dần* (incremental assignment): trạng thái chỉ lớn thêm, không bao giờ bỏ bớt một quân/bóng đã đặt. Nhờ vậy một trạng thái chỉ cần ghi **tập ô đã đặt**; mọi con số đếm khác đều suy ra được.

Ký hiệu chung: $V$ là tập ô của bàn cờ, $n$ là cạnh (Star Battle luôn vuông), $k$ là số sao mỗi hàng.

---

## 1. Star Battle

### 1.1. Trạng thái tổng quát

Bàn cờ được cố định bởi bộ ba $(n, k, R)$: cạnh $n$, số sao mỗi hàng $k$, và cách chia vùng $R : V \to \{1, \dots, n\}$ (bản Shapeless thay $R$ bằng tập tường $W \subset V$).

Trạng thái tại một thời điểm là tập sao đã đặt:

$$S = A, \qquad A \subseteq V, \quad |A| \le nk$$

Ba đại lượng đếm suy ra từ $A$ (không cần lưu riêng):

$$\mathrm{row}(r) = |\{v \in A : v_r = r\}|, \quad
\mathrm{col}(c) = |\{v \in A : v_c = c\}|, \quad
\mathrm{reg}(g) = |\{v \in A : R(v) = g\}|$$

> Trong code: `A` chính là tập `(row, col)` mà thuật toán trả về; `StarBattle.regions[r][c]` cho $R$, `StarBattle.walls` cho $W$.

### 1.2. Ràng buộc an toàn

$A$ là **trạng thái hợp lệ** khi và chỉ khi:

1. Không có hai sao kề nhau, kể cả kề chéo — với mọi $u, v \in A$, $u \ne v$:
$$\max\big(|u_r - v_r|,\ |u_c - v_c|\big) \ge 2$$
2. Không hàng, cột, vùng nào vượt quá $k$ sao: $\mathrm{row}(r) \le k$, $\mathrm{col}(c) \le k$, $\mathrm{reg}(g) \le k$.
3. Không đặt sao lên tường (bản Shapeless): $A \cap W = \varnothing$.

Điều kiện 1 và 2 đúng ở **mọi bước**, không chỉ ở đích — đây là cơ sở để cắt nhánh.

### 1.3. Trạng thái khởi đầu

$$S_0 = \varnothing \qquad (\text{bàn cờ trống})$$

### 1.4. Trạng thái mục tiêu

$S_g = A$ sao cho:

$$|A| = nk \quad \text{và} \quad \mathrm{row}(r) = \mathrm{col}(c) = \mathrm{reg}(g) = k \ \ \forall r, c, g$$

Tức là đủ $nk$ sao **và** mọi hàng/cột/vùng đạt đúng $k$. Hai điều kiện này không thay thế nhau: đủ số sao vẫn có thể lệch hàng.

### 1.5. Luật di chuyển hợp lệ

Một nước đi là **đặt thêm đúng một sao** vào ô $v$:

$$A' = A \cup \{v\}$$

Nước đi hợp lệ khi và chỉ khi:

1. $v \in V \setminus A$ và $v \notin W$ (ô trống, không phải tường).
2. $v$ không kề (kể cả chéo) bất kỳ sao nào trong $A$.
3. Sau khi thêm: $\mathrm{row}(v_r) \le k$, $\mathrm{col}(v_c) \le k$, $\mathrm{reg}(v) \le k$.

Mỗi nước đi làm $|A|$ tăng 1, nên **độ sâu tối đa của cây tìm kiếm là $nk$** — đây là lý do bài này hợp với DFS/BFS có giới hạn độ sâu, và là chỗ heuristic $h$ phát huy tác dụng.

*Khử trùng lặp (tuỳ chọn):* vì tập sao không có thứ tự, đặt cùng một tập theo thứ tự khác nhau sẽ sinh ra nhiều nhánh cho cùng một trạng thái. Có thể chỉ cho phép chọn $v$ lớn hơn ô cuối cùng đã đặt theo thứ tự $(r, c)$ — vẫn đủ nghiệm, giảm mạnh số nhánh. Nếu dùng, phải ghi rõ trong báo cáo vì nó làm thay đổi số node.

---

## 2. Light Up

### 2.1. Trạng thái tổng quát

Bàn cờ cố định: $R \times C$ ô, mỗi ô là trắng, đen không số, hoặc đen có số $c \in \{0,\dots,4\}$. Gọi $B_0$ là tập ô đen (kể cả ô có số) — không bao giờ đặt bóng lên đó.

Trạng thái là tập bóng đèn đã đặt:

$$S = L, \qquad L \subseteq V \setminus B_0$$

Đại lượng suy ra: tập ô được chiếu sáng $\mathrm{lit}(L)$ — hợp của các tia ngang/dọc từ mỗi bóng, dừng ở ô đen đầu tiên.

### 2.2. Ràng buộc an toàn

$L$ hợp lệ khi và chỉ khi:

1. Không có hai bóng "nhìn thấy nhau" — trên cùng hàng hoặc cùng cột, giữa chúng không có ô đen:
$$\nexists\, u, v \in L,\ u \ne v:\ u, v \text{ cùng hàng/cột và không ô đen nào nằm giữa}$$
2. Với mỗi ô đen có số $c$: số bóng kề cạnh **không vượt quá** $c$.

Điều kiện 2 chỉ chặn *vượt*, chưa bắt *đủ*: đủ $c$ bóng chỉ bắt buộc ở trạng thái đích, vì trong lúc tìm ta chưa biết các ô xung quanh sẽ nhận bóng hay không.

### 2.3. Trạng thái khởi đầu

$$S_0 = \varnothing$$

### 2.4. Trạng thái mục tiêu

$S_g = L$ sao cho đồng thời:

1. Mọi ô trắng đều được chiếu sáng: $V \setminus B_0 \subseteq \mathrm{lit}(L)$.
2. Mọi ô đen có số $c$ có **đúng** $c$ bóng kề cạnh.
3. Không có hai bóng chiếu nhau (đã đúng ở mọi bước).

Lưu ý: điều kiện 1 nói *mọi ô trắng*, kể cả ô đang có bóng — bóng đèn cũng phải được chiếu sáng, nhưng bởi chính nó hoặc bóng khác.

### 2.5. Luật di chuyển hợp lệ

Một nước đi là **đặt thêm đúng một bóng** vào ô trắng $v$:

$$L' = L \cup \{v\}$$

Nước đi hợp lệ khi và chỉ khi:

1. $v \in V \setminus B_0$ và $v \notin L$.
2. $v$ không "nhìn thấy" bóng nào trong $L$ (cùng hàng/cột, không ô đen chắn giữa).
3. Mọi ô đen có số kề cạnh $v$ vẫn thoả: nếu ô đó ghi $c$ thì số bóng kề sau khi thêm $\le c$.

Mỗi nước đi tăng $|L|$ thêm 1. Khác Star Battle, **không có chặn trên cho $|L|$** ($|L| \le RC$), nên cây tìm kiếm sâu hơn nhiều và số node lớn hơn hẳn — đây là điểm sẽ lộ ra trong bảng số liệu.

---

## 3. Đối chiếu hai bài

| | Star Battle | Light Up |
|---|---|---|
| Trạng thái | tập sao $A$ | tập bóng $L$ |
| Khởi đầu | $\varnothing$ | $\varnothing$ |
| Nước đi | thêm 1 sao | thêm 1 bóng |
| Ràng buộc cứng ở mọi bước | không kề (kể cả chéo), không vượt $k$ mỗi hàng/cột/vùng | không hai bóng chiếu nhau, không vượt số ghi trên ô đen |
| Điều kiện đích | đủ $nk$ **và** mọi hàng/cột/vùng $=k$ | mọi ô trắng được chiếu **và** mọi ô số đủ đúng |
| Độ sâu tối đa | $nk$ (hữu hạn, biết trước) | $\le$ số ô trắng (lớn hơn nhiều) |
| Kích thước không gian | $\binom{n^2}{nk}$ trừ phần vi phạm | $2^{|V \setminus B_0|}$ trừ phần vi phạm |

Điểm chung: cùng dạng "thêm dần trên lưới", cùng một bộ khung `core.py` (`load` → `check` → `register`/`solve`), nên bốn thuật toán dùng chung được phần sinh trạng thái con và phần log bước.

---

## 4. Liên hệ với code

| Khái niệm | Trong `core.py` |
|---|---|
| $V$, $n$, $k$ | `StarBattle.size`, `.stars` |
| $R$, $W$ | `StarBattle.regions`, `.walls` (`regions is None` khi có tường) |
| $A$ hợp lệ | `core.check(sb, A) == []` |
| $B_0$, ô trắng | `LightUp.is_black(r, c)`, `.rows`, `.cols` |
| số ghi trên ô đen | `LightUp.clue(r, c)` (`None` nếu không phải ô số) |
| $L$ hợp lệ | `core.check(lu, L) == []` |

`core.check` kiểm **trạng thái đích**, không kiểm từng bước — nghĩa là nó xác nhận lời giải cuối cùng, còn việc giữ ràng buộc cứng ở mọi bước là trách nhiệm của hàm sinh trạng thái con trong từng thuật toán.

---

*Liên quan: [[03 - Ví dụ & Bài tập/BTL1/Viec-1/README.md]] · [[03 - Ví dụ & Bài tập/BTL1/V3-Heuristic.md]]*
