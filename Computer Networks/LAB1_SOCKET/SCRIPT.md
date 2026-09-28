# PHÂN TÍCH MÃ NGUỒN ỨNG DỤNG CHAT LAN BẰNG SOCKET

Tài liệu phân tích hai phiên bản của ứng dụng chat nhiều người trong mạng LAN, viết bằng Python (`socket`, `threading`):

| Phiên bản | Thành phần | Cách chạy |
|---|---|---|
| **Phiên bản 1 (Tự nâng cấp từ code base ): Terminal** | `server.py`, `client.py` | Chạy file bằng `python`, giao diện trên terminal |
| **Phiên bản codebase : Notebook** | `00_Server.ipynb`, `01_Client_A.ipynb`, `02_Client_B.ipynb`, `HUONG_DAN.txt` | Chạy từng ô code (Shift+Enter) trên 3 máy qua Wi-Fi |

---

## 1. KIẾN TRÚC VÀ NGUYÊN LÝ CHUNG

### 1.1. Mô hình Client – Server (hub)

```
 Client A ─┐
 Client B ─┼── TCP : 5000 ──►  SERVER  ── chuyển tiếp (broadcast) ──► các client
 Client C ─┘
```

Các client không giao tiếp trực tiếp với nhau. Toàn bộ tin nhắn đi qua server, server chuyển tiếp cho các client còn lại. Server không lưu lịch sử và không có tài khoản hay mật khẩu.

### 1.2. Đặc điểm kỹ thuật dùng chung cho cả hai phiên bản

| Đặc điểm | Mô tả |
|---|---|
| Giao thức tầng giao vận | **TCP** (`AF_INET` + `SOCK_STREAM`): tin cậy, đúng thứ tự, có khái niệm kết nối |
| Giao thức ứng dụng | **Văn bản theo dòng**: mỗi tin nhắn là một dòng kết thúc bằng `\n` |
| Mã hoá ký tự | **UTF-8** (gửi được tiếng Việt có dấu) |
| Mô hình xử lý đồng thời | **Thread-per-client**: mỗi client được phục vụ bởi một luồng riêng |
| Đọc dữ liệu | `conn.makefile(...)` + `readline()` để đọc từng dòng |
| Luồng nền | Các luồng phục vụ đặt `daemon=True` |
| Địa chỉ nghe của server | `0.0.0.0:5000` (mọi card mạng) |
| Timeout khi kết nối (client) | `settimeout(...)` khi `connect`, sau đó trả về chế độ chặn |
| Tín hiệu đóng kết nối | `readline()` trả về rỗng (EOF) → thoát vòng lặp và dọn dẹp |

**Vì sao cần giao thức theo dòng:** TCP là luồng byte, không giữ ranh giới giữa các lần gửi. Hai lần `sendall` có thể đến trong một lần đọc, hoặc một tin có thể bị tách thành nhiều phần. Việc dùng `\n` làm dấu ngăn cách kết hợp `readline()` cho phép tách chính xác từng tin.

---

## 2. PHIÊN BẢN 1 : TERMINAL (`server.py` + `client.py`)

### 2.1. Giao thức

| Chiều | Nội dung | Ví dụ |
|---|---|---|
| Client → Server, dòng đầu tiên | Tên người dùng | `An\n` |
| Client → Server, các dòng sau | Nội dung tin | `xin chào\n` |
| Server → Client, tin của người khác | `[Tên] nội dung` | `[An] xin chào\n` |
| Server → Client, thông báo hệ thống | `*** ... ***` | `*** An da vao phong chat ***\n` |

### 2.2. Phân tích `server.py`

#### a) Dữ liệu dùng chung và đồng bộ hoá

```python
HOST = "0.0.0.0"
PORT = 5000
clients = {}                      # conn -> tên
clients_lock = threading.Lock()
```

* `clients` lưu danh sách client đang online, được nhiều luồng cùng truy cập (thêm khi vào, xoá khi ra, duyệt khi broadcast).
* `clients_lock` ngăn **race condition** (ví dụ dictionary đổi kích thước trong lúc đang duyệt).

#### b) Hàm `broadcast(message, exclude_conn=None)`

```python
def broadcast(message, exclude_conn=None):
    with clients_lock:
        targets = list(clients.items())
    for conn, name in targets:
        if conn is exclude_conn:
            continue
        try:
            conn.sendall(message.encode("utf-8"))
        except OSError:
            pass
```

| Kỹ thuật | Tác dụng |
|---|---|
| Sao chép danh sách (`list(clients.items())`) rồi mới gửi | Chỉ giữ khoá trong thời gian ngắn, **không giữ khoá khi thực hiện I/O mạng**; tránh một client chậm làm kẹt toàn bộ server |
| Tham số `exclude_conn` | Không gửi lại tin cho người vừa gửi (client tự hiển thị tin của mình ngay) |
| `sendall` | Đảm bảo gửi hết dữ liệu (khác `send` có thể gửi thiếu) |
| `except OSError: pass` | Client đã mất kết nối thì bỏ qua; việc dọn dẹp do luồng của client đó thực hiện |

#### c) Hàm `handle_client(conn, addr)`: chạy riêng cho từng client

| Giai đoạn | Xử lý |
|---|---|
| 1. Bắt tay | `makefile("r")` để đọc theo dòng; dòng đầu tiên là tên. Tên rỗng thì đặt `Khach_<cổng nguồn>` |
| 2. Đăng ký | Thêm `conn → name` vào `clients` (trong khoá), ghi log `[+]`, broadcast thông báo vào phòng (gửi cho **tất cả**) |
| 3. Vòng lặp nhận tin | `readline()` (hàm chặn); rỗng → client đóng kết nối; bỏ qua dòng trống; in log; `broadcast(..., exclude_conn=conn)` |
| 4. Dọn dẹp (`finally`) | Xoá khỏi `clients`, `conn.close()`, ghi log `[-]`, broadcast thông báo rời phòng (chỉ nếu đã có tên) |

Các ngoại lệ `ConnectionResetError` và `OSError` được bắt. Khối `finally` chạy trong mọi trường hợp thoát nên danh sách client luôn được dọn sạch. `with ... makefile(...)` chỉ đóng đối tượng file bọc ngoài, không đóng socket, do đó vẫn cần `conn.close()` thủ công.

#### d) Hàm `main()`

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
```

* Trình tự: **tạo socket → bind → listen → accept**.
* `SO_REUSEADDR`: cho phép mở lại cổng ngay sau khi tắt server (tránh lỗi "Address already in use").
* `accept()` là hàm chặn, chạy ở luồng chính; mỗi client mới được giao một luồng.
* `KeyboardInterrupt` (Ctrl+C) được bắt để dừng server; `finally` đóng socket lắng nghe.

### 2.3. Phân tích `client.py`

#### a) Thư viện và múi giờ

| Thành phần | Vai trò |
|---|---|
| `prompt_toolkit` (`PromptSession`, `print_formatted_text`, `ANSI`, `patch_stdout`) | Ô nhập liệu và in có màu mà không làm rách dòng đang gõ |
| `shutil.get_terminal_size` | Lấy độ rộng terminal để căn lề |
| `timezone(timedelta(hours=7))` | Giờ Việt Nam (UTC+7), không phụ thuộc cấu hình máy |

#### b) Màu sắc theo người gửi

```python
def color_for(name):
    idx = sum(ord(c) for c in name) % len(OTHER_PALETTE)
    return OTHER_PALETTE[idx]
```

* Bảng màu 8 phần tử dùng mã **ANSI escape** (`\033[..m`); `RESET` trả về mặc định, `DIM` làm chữ mờ.
* Màu được tính từ **tổng mã ký tự của tên chia lấy dư 8**, nên cùng một tên luôn ra cùng một màu và mọi client tự tính ra kết quả giống nhau mà server không cần lưu.
* Đây là phép ánh xạ đơn giản, không phải hàm băm mật mã. Hai tên khác nhau có thể trùng màu.

#### c) Căn lề

| Hàm | Chức năng |
|---|---|
| `get_width()` | Số cột hiện tại của terminal (mặc định 80) |
| `render_right(text)` | `rjust(width)` để căn sát mép phải (dùng cho tin của chính mình) |
| `render_center(text)` | Chèn `(width - len) // 2` khoảng trắng để căn giữa (thông báo hệ thống) |
| `input_indent(last_msg_len)` | Sau khi đã gửi tin: đệm `width - last_msg_len` để ô nhập `[Tên]` thẳng cột với khối tin căn phải; chưa gửi tin thì đặt ở khoảng giữa (`width // 2 - 6`) |

Các hàm căn lề đều có điều kiện `len(text) >= width`: dòng quá dài được giữ nguyên để terminal tự xuống dòng.

#### d) Luồng nhận `receive_messages(sock)`

Chạy ở luồng phụ. Phân loại dòng nhận được theo tiền tố:

| Điều kiện | Xử lý hiển thị |
|---|---|
| Bắt đầu bằng `***` | Thông báo vào/rời phòng: căn giữa, chữ mờ, kèm giờ |
| Bắt đầu bằng `[` | Tách `sender` (giữa `[` và `]` đầu tiên) và `msg`; tô màu theo `color_for(sender)`; căn trái, kèm giờ |
| Khác | In nguyên văn |
| `readline()` trả rỗng | In "Mất kết nối tới server" rồi thoát |

Giờ hiển thị cạnh tin người khác là giờ **lúc client nhận**, không phải giờ lúc gửi (server không gắn timestamp).

#### e) `main()`: kết nối và vòng lặp gửi

* Nhập IP, cổng (mặc định 5000), tên (mặc định `Khach`).
* `settimeout(5)` cho `connect`; lỗi `OSError` thì in gợi ý kiểm tra và `sys.exit(1)`; sau khi kết nối thì `settimeout(None)`.
* Việc đầu tiên: gửi dòng **tên** lên server.
* `PromptSession(erase_when_done=True)`: sau khi Enter, dòng vừa gõ bị xoá để in lại phiên bản đã căn phải và tô màu, tránh một tin hiện hai lần.
* `patch_stdout()`: hai luồng cùng ghi ra màn hình (luồng nhận và luồng nhập). `patch_stdout` chuyển hướng `print` để tin mới hiện **phía trên** ô nhập, sau đó vẽ lại ô nhập nguyên vẹn, nên dòng đang gõ không bị rách.
* Lệnh `/exit` thoát; dòng rỗng bị bỏ qua; `Ctrl+C`/`Ctrl+D` cũng thoát êm.
* Tin của chính mình được **in ngay tại client** (kèm `last_msg_len` để căn ô nhập).
* `finally`: `shutdown(SHUT_RDWR)` rồi `close()` để server nhận EOF ngay và thông báo rời phòng.

### 2.4. Các luồng trong phiên bản 1

| Nơi | Luồng | Nhiệm vụ |
|---|---|---|
| Server | Luồng chính | `accept()` |
| Server | N luồng `handle_client` | Đọc tin của từng client và broadcast |
| Client | Luồng chính | Nhập liệu và gửi tin |
| Client | 1 luồng `receive_messages` | Nhận và hiển thị tin |

---

## 3. PHIÊN BẢN CODEBASE: NOTEBOOK (`00_Server`, `01_Client_A`, `02_Client_B`)

### 3.1. Mô hình triển khai

```
 Máy A (172.20.10.45) ─┐
                       ├── Wi-Fi ──► Máy Server (172.20.10.12 : 5000)
 Máy B (172.20.10.99) ─┘
```

* Server: `HOST = '0.0.0.0'`, `PORT = 5000`. Hai client: `HOST = '172.20.10.12'`, `PORT = 5000`.
* **Cổng của client do hệ điều hành tự chọn.**
* Một ô code phải kết thúc thì mới chạy được ô kế tiếp, nên chương trình được thiết kế để mọi thành phần chạy **nền** (luồng), không có vòng lặp chặn ở luồng chính.

### 3.2. Giao thức

| Chiều | Nội dung |
|---|---|
| Client → Server | `nội dung\n` (tối đa 4096 byte, kể cả `\n`) |
| Server → tất cả client (**kể cả người gửi**) | `[cổng của người gửi] nội dung\n` |

Không còn bước gửi tên. Server lấy **số cổng của client** (`address[1]`) làm nhãn người gửi và tự gắn vào đầu tin. Nhãn do server tạo nên người gửi không thể tự đặt nhãn để giả danh người khác.

### 3.3. Phân tích `00_Server.ipynb`

#### a) Ô 1: khởi tạo

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.settimeout(0.5)
clients = {}                     # conn -> khoá ghi riêng của conn
clients_lock = threading.Lock()
workers = []
stop = threading.Event()
```

| Thành phần | Vai trò |
|---|---|
| `settimeout(0.5)` | `accept()` không chờ vô hạn; cứ 0,5 giây nhả ra để kiểm tra cờ dừng |
| `stop = threading.Event()` | Cờ dừng dùng chung giữa các luồng |
| `clients` (`conn → Lock`) | Danh sách client, mỗi client có **khoá ghi riêng** |
| `clients_lock` | Bảo vệ chính dictionary `clients` |
| `workers` | Danh sách luồng phục vụ, dùng để `join` khi dừng server |

Ghi chú: phiên bản này **không dùng `SO_REUSEADDR`**, nên khởi động lại nhanh trên Linux/macOS có thể gặp lỗi "Address already in use" (cách xử lý trong hướng dẫn: Restart Kernel hoặc đổi cổng).

#### b) Ô 2: `handle_client`

```python
with conn.makefile('rb') as reader:
    while True:
        raw = reader.readline(4097)
        if not raw:
            break
        if len(raw) > 4096 or not raw.endswith(b'\n'):
            break
        text = raw[:-1].decode('utf-8')
        message = f'[{address[1]}] {text}\n'.encode('utf-8')
        print(message.decode('utf-8').rstrip())
        with clients_lock:
            targets = list(clients.items())
        for target, write_lock in targets:
            try:
                with write_lock:
                    target.sendall(message)
            except OSError:
                pass
```

| Cơ chế | Giải thích |
|---|---|
| Đọc nhị phân `makefile('rb')` + `readline(4097)` | Giới hạn số byte đọc trong một dòng, chặn việc client gửi dòng cực dài không có `\n` làm phình bộ nhớ. Đọc dư 1 byte (4097) để **phát hiện** dòng vượt giới hạn 4096 |
| `len(raw) > 4096 or not raw.endswith(b'\n')` | Dòng quá dài, hoặc kết thúc không có `\n` (ví dụ client đóng giữa chừng) → `break` và đóng kết nối đó |
| `decode('utf-8')` bên trong `try` | Dữ liệu không phải UTF-8 hợp lệ gây `UnicodeError`, được bắt cùng `OSError`: chỉ ngắt client vi phạm, server vẫn chạy |
| Nhãn `[address[1]]` do server gắn | Định danh theo cổng, không thể giả mạo bằng nội dung tin |
| Gửi cho **tất cả kể cả người gửi** | Không cần `exclude_conn`; người gửi thấy tin đã đi qua server |
| Snapshot danh sách rồi thả `clients_lock` | Không giữ khoá chung khi gửi qua mạng |
| **`write_lock` riêng cho từng kết nối** | Nhiều luồng có thể gửi tới cùng một socket đích; khoá riêng ngăn hai tin xen kẽ nhau, còn các socket khác nhau vẫn gửi song song |
| `finally` | Xoá khỏi `clients`, `conn.close()` |

**Hai loại khoá trong phiên bản này:**

| Khoá | Bảo vệ |
|---|---|
| `clients_lock` | Cấu trúc dữ liệu `clients` (thêm, xoá, duyệt) |
| `write_lock` của từng kết nối | Thao tác ghi vào một socket cụ thể |

#### c) Ô 2: `accept_clients` và luồng chấp nhận kết nối

```python
def accept_clients():
    while not stop.is_set():
        try:
            conn, address = server.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        with clients_lock:
            clients[conn] = threading.Lock()
        worker = threading.Thread(target=handle_client, args=(conn, address), daemon=True)
        workers.append(worker)
        worker.start()

accept_thread = threading.Thread(target=accept_clients, daemon=True)
accept_thread.start()
```

* Vòng lặp `accept` được đưa vào **luồng nền** (`accept_thread`) để ô code kết thúc ngay, server tiếp tục chạy ngầm (khác phiên bản 1, nơi `accept` chạy ở luồng chính).
* `socket.timeout` → `continue` để kiểm tra lại cờ `stop`; `OSError` (socket đã đóng) → thoát vòng lặp.
* Kết nối mới được **đăng ký vào `clients` trước khi** khởi động luồng phục vụ, tránh trường hợp tin đến khi client chưa có trong danh sách.

#### d) Ô 3: dừng server

```python
stop.set()
server.close()
accept_thread.join(2)
# shutdown + close từng kết nối còn lại
for worker in workers:
    worker.join(2)
```

Trình tự tắt có trật tự: bật cờ dừng → đóng socket lắng nghe → chờ luồng accept → `shutdown` và đóng các kết nối còn lại (các luồng đang chờ `readline()` nhận EOF và thoát) → `join` từng luồng phục vụ (tối đa 2 giây mỗi luồng).

### 3.4. Phân tích `01_Client_A.ipynb` / `02_Client_B.ipynb`

Hai notebook giống nhau hoàn toàn, chỉ khác nội dung tin mẫu ở ô gửi.

#### a) Ô 1: kết nối

```python
client.settimeout(3)
client.connect((HOST, PORT))
client.settimeout(None)
inbox = queue.Queue()
print('Client:', client.getsockname(), '->', client.getpeername())
```

`getsockname()` cho biết cổng cục bộ của chính client, đây cũng là số xuất hiện trong nhãn `[cổng]` ở các tin của client này. `inbox` là hàng đợi an toàn giữa các luồng.

#### b) Ô 2: luồng nhận, hàm gửi và xem tin

| Thành phần | Chức năng |
|---|---|
| `receive_forever()` (luồng nền) | Đọc nhị phân bằng `readline(8193)`; vượt 8192 byte hoặc thiếu `\n` thì dừng; giải mã UTF-8 rồi `inbox.put(...)`. Khi kết thúc (mọi trường hợp), thêm dòng `[Kết nối đã đóng]` vào `inbox` |
| `send(text)` | Kiểm tra: không rỗng, **không chứa `\n` hoặc `\r`**, `len(payload) <= 4096`; vi phạm thì ném `ValueError`; hợp lệ thì `sendall` |
| `read_messages()` | Rút hết `inbox` bằng `get_nowait()` vào `history`, in **toàn bộ lịch sử** của phiên (hoặc "Chưa có tin nhắn") |

Giải thích các quyết định thiết kế:

* **Dùng `queue.Queue` thay vì in trực tiếp:** trong notebook, in từ luồng nền không đảm bảo hiển thị đúng vị trí và không có `patch_stdout` như phiên bản terminal. Luồng nhận đưa tin vào hàng đợi, người dùng chủ động chạy ô "xem tin" để đọc.
* **Cấm `\n` và `\r` trong tin:** `\n` là dấu ngăn cách tin trong giao thức; nếu cho phép trong nội dung, một tin có thể bị tách thành nhiều tin (line injection).
* **Giới hạn nhận (8192) lớn hơn giới hạn gửi (4096):** vì server thêm nhãn `[cổng] ` vào đầu mỗi tin.

#### c) Ô 3–5

Ô gửi tin mẫu, ô xem tin, ô đóng kết nối (`shutdown` + `close` + `receiver.join(2)`).

### 3.5. Quy trình chạy và lưu ý (theo `HUONG_DAN.txt`)

1. Máy server: chạy 2 ô code đầu của `00_Server.ipynb`.
2. Máy A, máy B: chạy 2 ô code đầu của notebook client tương ứng.
3. Lặp lại ô gửi và ô xem tin tuỳ ý.
4. Kết thúc: đóng A → đóng B → dừng server.

Lưu ý: **không dùng Run All** (ô cuối đóng kết nối); **không chạy lại ô chuẩn bị gửi/nhận** (tạo thêm luồng đọc thứ hai và xoá `history`); cần reset thì Restart Kernel rồi chạy lại từ đầu. Nếu không kết nối được, kiểm tra IP server, cùng mạng Wi-Fi và tường lửa cho phép TCP vào cổng đã chọn.

---

## 4. SO SÁNH HAI PHIÊN BẢN

### 4.1. Bảng so sánh chi tiết

| Tiêu chí | Phiên bản 1: Terminal | Phiên bản 2: Notebook |
|---|---|---|
| **Cách chạy** | Chạy file, tiến trình chạy liên tục | Chạy từng ô, thành phần chạy nền |
| **Vòng lặp `accept`** | Luồng chính | Luồng nền riêng (`accept_thread`) |
| **Định danh người gửi** | Tên do người dùng tự nhập, gửi ở dòng đầu | Số cổng của client, do server gắn |
| **Thông báo vào/rời phòng** | Có (`*** ... ***`) | Không |
| **Người gửi có nhận lại tin của mình** | Không (`exclude_conn`); client tự in | Có (server gửi cho tất cả) |
| **Giao diện** | Màu theo người gửi, canh trái/phải/giữa, giờ VN | Chỉ in văn bản thuần |
| **Thư viện giao diện** | `prompt_toolkit`, `shutil`, ANSI | Không dùng thư viện ngoài |
| **Nhận và hiển thị tin** | Luồng nhận in trực tiếp (nhờ `patch_stdout`) | Luồng nhận đưa vào `queue.Queue`, người dùng chạy ô xem tin |
| **Chế độ đọc** | `makefile("r")` (văn bản) | `makefile("rb")` (nhị phân, tự `decode`) |
| **Giới hạn độ dài dòng** | Không | 4096 byte (server nhận), 8192 byte (client nhận) |
| **Xử lý dữ liệu sai** | Không xử lý riêng lỗi giải mã UTF-8 | Bắt `UnicodeError`; dòng quá dài hoặc thiếu `\n` bị ngắt kết nối |
| **Kiểm tra đầu vào ở client** | Bỏ qua dòng rỗng | Cấm rỗng, `\n`, `\r`, tin > 4096 byte (`ValueError`) |
| **Đồng bộ hoá** | Một khoá `clients_lock` | `clients_lock` **và** khoá ghi riêng cho từng kết nối |
| **Dừng server** | `Ctrl+C` (`KeyboardInterrupt`) | `Event` + `settimeout` + `shutdown` + `join` |
| **`SO_REUSEADDR`** | Có | Không |
| **Tên mặc định** | `Khach_<cổng>` (server) / `Khach` (client) | Không có tên |
| **Lệnh thoát** | `/exit`, `Ctrl+C`, `Ctrl+D` | Chạy ô đóng kết nối |
| **Số máy triển khai** | Linh hoạt, mỗi máy chạy `client.py` | 1 server + 2 client (Client_A, Client_B) |

### 4.2. Nhận xét tổng hợp

* **Phiên bản 1 tập trung vào trải nghiệm người dùng:** giao diện giống ứng dụng chat, có tên, màu, giờ, thông báo vào/rời phòng, xử lý hiển thị đồng thời bằng `patch_stdout`.
* **Phiên bản codebase tập trung vào tính chặt chẽ của giao thức và điều khiển luồng:** giới hạn kích thước, kiểm tra dữ liệu, khoá ghi riêng, tắt server có trật tự, phù hợp để minh hoạ từng bước hoạt động của socket. Đổi lại, giao diện giản lược và định danh người gửi kém rõ ràng hơn (số cổng thay cho tên).

---

## 5. CÁC KỸ THUẬT CHÍNH ĐƯỢC SỬ DỤNG

| Kỹ thuật | Nơi dùng | Giải thích ngắn |
|---|---|---|
| Socket TCP (`bind`, `listen`, `accept`, `connect`) | Cả hai | Thiết lập kết nối tin cậy, có thứ tự |
| Giao thức theo dòng (`\n`) | Cả hai | Xác định ranh giới tin trên luồng byte |
| Thread-per-client | Cả hai | Mỗi client một luồng, `accept` không bị chặn bởi việc phục vụ |
| `threading.Lock` | Cả hai | Loại trừ tương hỗ khi truy cập dữ liệu dùng chung |
| Sao chép danh sách trước khi gửi (snapshot) | Cả hai | Giữ khoá ngắn, tránh I/O trong vùng khoá |
| `daemon=True` | Cả hai | Luồng nền tự dừng khi chương trình chính kết thúc |
| `SO_REUSEADDR` | Terminal | Mở lại cổng ngay sau khi tắt server |
| `settimeout` | Cả hai | Timeout khi `connect` (client), chu kỳ thoát `accept` (server notebook) |
| `threading.Event` | Notebook | Cờ dừng dùng chung giữa các luồng |
| Khoá ghi riêng theo kết nối | Notebook | Tránh hai luồng ghi xen kẽ vào cùng một socket |
| `queue.Queue` | Notebook | Truyền dữ liệu an toàn giữa luồng nhận và luồng chính |
| `readline(limit)` | Notebook | Giới hạn kích thước dòng, chống dòng vô hạn |
| `shutdown(SHUT_RDWR)` + `close()` | Cả hai | Báo đóng kết nối cho đầu bên kia (EOF) rồi giải phóng socket |
| `join(timeout)` | Notebook | Chờ luồng kết thúc có giới hạn thời gian |
| Mã ANSI, `ANSI()`, `print_formatted_text` | Terminal | Màu sắc và định dạng chữ trong terminal |
| `PromptSession(erase_when_done=True)` | Terminal | Xoá dòng vừa gõ để in lại bản đã định dạng |
| `patch_stdout()` | Terminal | Cho phép luồng nền in mà không làm rách dòng đang nhập |
| `shutil.get_terminal_size` + `rjust`/căn giữa thủ công | Terminal | Canh lề theo độ rộng terminal |

---

## 6. ĐÁNH GIÁ: HẠN CHẾ VÀ HƯỚNG CẢI THIỆN ( SẼ CẢI THIỆN SAU ) 

### 6.1. Hạn chế chung của cả hai phiên bản

| Hạn chế | Hướng cải thiện |
|---|---|
| Dữ liệu truyền dạng văn bản thường (không mã hoá) | Bọc TLS bằng module `ssl` |
| Không xác thực: ai biết IP và cổng đều tham gia được | Mật khẩu hoặc token khi bắt tay |
| Không giới hạn số kết nối, không có timeout cho kết nối im lặng | Giới hạn số client, đặt timeout không hoạt động |
| Không có tin nhắn riêng, danh sách người online, lưu lịch sử | Bổ sung lệnh `/list`, `/w`, lưu file hoặc CSDL |
| Mỗi client một luồng: khó mở rộng lên số lượng rất lớn | Chuyển sang `asyncio` hoặc `selectors` |
| Gửi tới client nhận chậm là thao tác chặn | Hàng đợi gửi riêng cho từng client |

### 6.2. Hạn chế riêng của phiên bản 1

| Hạn chế | Hướng cải thiện |
|---|---|
| Không giới hạn độ dài dòng (`readline()` không tham số) | Dùng `readline(limit)` như phiên bản 2 |
| Không bắt `UnicodeDecodeError` trong luồng phục vụ | Bắt thêm ngoại lệ hoặc đọc chế độ nhị phân rồi `decode` có kiểm soát |
| Không có khoá ghi riêng cho từng socket | Thêm khoá ghi theo kết nối |
| Tên tự khai, không kiểm tra trùng; tên chứa `]` làm client tách sai `sender` (dùng `find("]")` đầu tiên) | Kiểm tra và chuẩn hoá tên ở server, hoặc dùng định dạng có cấu trúc (JSON) |
| Nội dung và tên được in thẳng vào `ANSI(...)`, chưa lọc ký tự điều khiển | Lọc ký tự điều khiển (`\x1b`, ký tự < 0x20) trước khi hiển thị |
| Giờ hiển thị là giờ nhận, không phải giờ gửi | Server gắn timestamp khi nhận tin |
| Đo độ rộng bằng `len()`, lệch với emoji/chữ rộng; không vẽ lại khi đổi kích thước cửa sổ | Dùng thư viện `wcwidth` |
| Nhập cổng không phải số làm `int()` ném `ValueError` | Bắt lỗi và cho nhập lại |

### 6.3. Hạn chế riêng của phiên bản 2

| Hạn chế | Hướng cải thiện |
|---|---|
| Nhãn bằng số cổng: khó biết là ai; hai máy khác nhau vẫn có thể trùng số cổng | Dùng `IP:cổng` hoặc thêm bước nhập tên |
| Việc cấm `\n`, `\r` chỉ thực hiện ở **client**; server chỉ kiểm tra độ dài và UTF-8 | Kiểm tra lại ở server (đây là ranh giới tin cậy), ví dụ loại bỏ ký tự điều khiển |
| Server ngắt kết nối khi vi phạm nhưng **không báo lý do** | Gửi thông báo lỗi trước khi đóng |
| `workers` chỉ thêm, không bao giờ dọn luồng đã kết thúc | Loại bỏ luồng đã xong khỏi danh sách |
| Không có `SO_REUSEADDR` | Thêm `setsockopt` |
| Chạy lại ô khởi động server/luồng accept sẽ tạo thêm luồng thứ hai | Thêm cờ chặn khởi động lặp |
| `read_messages` in lại toàn bộ lịch sử mỗi lần | Chỉ in tin mới hoặc đánh dấu vị trí đã đọc |
| `history` và `inbox` không giới hạn kích thước | Giới hạn số tin lưu |
| Không có thông báo vào/rời phòng, không có tên | Thêm lại bước bắt tay và thông báo như phiên bản 1 |

---

## 7. KẾT LUẬN

Hai phiên bản cùng dựa trên một nền tảng: TCP, giao thức văn bản theo dòng, UTF-8, mô hình thread-per-client và đồng bộ hoá bằng khoá. Phiên bản 1 hoàn thiện về giao diện và trải nghiệm chat trên terminal. Phiên bản 2 cải tiến về giao thức và độ an toàn của luồng dữ liệu (giới hạn kích thước, kiểm tra đầu vào, khoá ghi riêng, tắt server có trật tự) và chuyển cấu trúc chương trình sang chạy nền để phù hợp với môi trường notebook. Cả hai phiên bản vẫn ở mức minh hoạ kỹ thuật: để dùng trong môi trường thực tế cần bổ sung mã hoá (TLS), xác thực, kiểm tra dữ liệu ở phía server và giới hạn tài nguyên.
