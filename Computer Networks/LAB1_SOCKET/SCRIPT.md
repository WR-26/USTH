D
## PHẦN 1: GIẢI THÍCH MÃ NGUỒN `SERVER.PY`

Server có nhiệm vụ làm **trung gian nhận và phát lại (broadcast) tin nhắn** cho các Client.

### 1. Khởi tạo và Quản lý Đa luồng (Multi-threading)

```python
HOST = "0.0.0.0"   #[cite: 9]
PORT = 5000        #[cite: 9]

clients = {}            #[cite: 9]
clients_lock = threading.Lock()  #[cite: 9]

```

* **`HOST = "0.0.0.0"`**: Lắng nghe trên mọi card mạng của máy (Wi-Fi, dây LAN, Hotspot). Giúp các máy khác kết nối vào thông qua IP mạng cục bộ (ví dụ `192.168.1.12`).


* **`clients = {}`**: Dictionary dạng `{ socket_connection: "Tên_User" }` để lưu danh sách các client đang online.


* **`clients_lock = threading.Lock()`**: Tạo một **khoá an toàn**. Vì có nhiều luồng cùng lúc đọc/xóa dữ liệu trong `clients` khi có người vào/ra, khoá này ngăn ngừa lỗi xung đột dữ liệu (Race Condition).



---

### 2. Hàm Gửi Tin Nhắn Hàng Loạt (`broadcast`)

```python
def broadcast(message, exclude_conn=None): #[cite: 9]
    with clients_lock: #[cite: 9]
        targets = list(clients.items()) #[cite: 9]
    for conn, name in targets: #[cite: 9]
        if conn is exclude_conn: #[cite: 9]
            continue #[cite: 9]
        try: #[cite: 9]
            conn.sendall(message.encode("utf-8")) #[cite: 9]
        except OSError: #[cite: 9]
            pass #[cite: 9]

```

* **`with clients_lock:`**: Khóa dictionary lại trước khi copy danh sách client để gửi tin.


* **`if conn is exclude_conn: continue`**: **Không gửi ngược lại cho chính người vừa nhắn**. Lý do: Phía Client tự vẽ tin nhắn của chính mình ra màn hình ngay khi bấm Enter để đạt độ trễ 0ms.


* **`conn.sendall(...)`**: Chuyển chuỗi văn bản thành dạng byte (`encode("utf-8")`) và gửi qua giao thức TCP.



---

### 3. Xử lý Kết nối Riêng biệt (`handle_client`)

```python
def handle_client(conn, addr): #[cite: 9]
    try: #[cite: 9]
        with conn.makefile("r", encoding="utf-8", newline="\n") as reader: #[cite: 9]
            first_line = reader.readline() #[cite: 9]
            name = first_line.strip() or f"Khach_{addr[1]}" #[cite: 9]

```

* **`conn.makefile("r", ...)`**: Chuyển đổi dữ liệu thô (raw bytes) của Socket thành một luồng đọc văn bản theo dòng.


* **`reader.readline()`**: Đọc dữ liệu đến khi gặp ký tự xuống dòng `\n`. Dòng đầu tiên Client gửi lên sau khi kết nối mặc định được quy ước là **Tên người dùng**.



```python
            while True: #[cite: 9]
                line = reader.readline() #[cite: 9]
                if not line: #[cite: 9]
                    break  # Client đóng kết nối[cite: 9]
                text = line.rstrip("\n") #[cite: 9]
                print(f"[{name}] {text}") #[cite: 9]
                broadcast(f"[{name}] {text}\n", exclude_conn=conn) #[cite: 9]

```

* **Vòng lặp `while True**`: Đọc tin nhắn liên tục từ Client. Nếu người dùng tắt ứng dụng, `readline()` trả về chuỗi rỗng (`not line`), vòng lặp ngắt để tiến hành dọn dẹp.



---

### 4. Khởi chạy Server (`main`)

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #[cite: 9]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #[cite: 9]
server.bind((HOST, PORT)) #[cite: 9]
server.listen() #[cite: 9]

```

* **`AF_INET` & `SOCK_STREAM**`: Khởi tạo Socket dùng IPv4 và giao thức **TCP** (đảm bảo truyền nhận dữ liệu chính xác, đúng thứ tự).


* **`SO_REUSEADDR, 1`**: Cho phép Server sử dụng lại Port `5000` ngay lập tức nếu vừa bị tắt đột ngột (tránh lỗi *"Address already in use"*).



```python
while True: #[cite: 9]
    conn, addr = server.accept() #[cite: 9]
    t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True) #[cite: 9]
    t.start() #[cite: 9]

```

* **`server.accept()`**: Đứng chờ có Client kết nối vào. Khi có Client mới, lập tức tạo ra một luồng phụ (`threading.Thread`) để phục vụ riêng cho Client đó, giữ cho Server tiếp tục quay lại vòng lặp chờ Client tiếp theo.



---

## PHẦN 2: GIẢI THÍCH MÃ NGUỒN `CLIENT.PY`

Client chịu trách nhiệm xử lý **Giao diện Terminal (UI/UX)**, định dạng màu sắc và điều hướng văn bản.

### 1. Thuật toán Băm Màu Cố định (`color_for`)

```python
OTHER_PALETTE = ["\033[94m", "\033[93m", "\033[95m", ...] #[cite: 10]

def color_for(name): #[cite: 10]
    idx = sum(ord(c) for c in name) % len(OTHER_PALETTE) #[cite: 10]
    return OTHER_PALETTE[idx] #[cite: 10]

```

* **Mục đích**: Mỗi người trong phòng chat sẽ có 1 màu hiển thị riêng biệt.


* **Cách hoạt động**: Cộng tổng mã ASCII các ký tự trong tên (`sum(ord(c)...)`) rồi chia lấy dư (`%`) cho số lượng màu.


* **Tác dụng**: Giúp tên "An" hay "Bình" luôn giữ nguyên đúng một màu cố định suốt buổi chat dù tắt đi bật lại.



---

### 2. Thuật toán Căn Lề & Tính Kích Thước Terminal

```python
def get_width(): #[cite: 10]
    return shutil.get_terminal_size((80, 20)).columns #[cite: 10]

def render_right(text): #[cite: 10]
    width = get_width() #[cite: 10]
    return text.rjust(width) #[cite: 10]

```

* **`shutil.get_terminal_size()`**: Lấy độ rộng thực tế (số cột) của cửa sổ Terminal hiện tại.


* **`text.rjust(width)`**: Thêm các khoảng trắng vào bên trái chuỗi để đẩy nội dung tin nhắn của chính mình về **căn sát lề phải**.


* **`render_center(text)`**: Thêm khoảng trắng cân bằng hai bên để đưa thông báo hệ thống vào **chính giữa màn hình**.



---

### 3. Căn Thẳng Lề Con Trỏ Gõ (`input_indent`)

```python
def input_indent(last_msg_len=None): #[cite: 10]
    width = get_width() #[cite: 10]
    if last_msg_len is not None: #[cite: 10]
        pad = max(0, width - last_msg_len) #[cite: 10]
    return " " * pad #[cite: 10]

```

* Tính toán khoảng trống dựa trên độ dài tin nhắn vừa gửi (`last_msg_len`). Giúp dòng nhắc gõ `[Tên_Bạn]` tự động nhảy sang bên phải, **nằm thẳng hàng với mép bắt đầu của khung tin nhắn căn phải**.



---

### 4. Luồng Nhận Tin Nhắn Ngầm (`receive_messages`)

```python
def receive_messages(sock): #[cite: 10]
    with sock.makefile("r", encoding="utf-8", newline="\n") as reader: #[cite: 10]
        while True: #[cite: 10]
            line = reader.readline() #[cite: 10]
            ...
            if text.startswith("***"): #[cite: 10]
                print_formatted_text(ANSI(f"{DIM}{render_center(text)}{RESET}")) #[cite: 10]
            elif text.startswith("["): #[cite: 10]
                # Tách tên người gửi, gán màu và in căn trái[cite: 10]
                color = color_for(sender) #[cite: 10]
                print_formatted_text(ANSI(f"{color}{sender} ({now}): {msg}{RESET}")) #[cite: 10]

```

* Chạy trên một **Thread phụ** liên tục lắng nghe dữ liệu từ Server.


* Tự động phân loại tin nhắn:
* Nếu chứa `***`: Là thông báo Vào/Rời phòng $\rightarrow$ In căn giữa, chữ mờ (`DIM`).


* Nếu chứa `[...]`: Là tin nhắn người khác $\rightarrow$ Bốc tách tên, tra mã màu bằng `color_for()` và in căn trái.





---

### 5. Khắc phục Vỡ Màn Hình với `patch_stdout()`

```python
session = PromptSession(erase_when_done=True) #[cite: 10]

with patch_stdout(): #[cite: 10]
    while True: #[cite: 10]
        text = session.prompt(...) #[cite: 10]
        sock.sendall((text + "\n").encode("utf-8")) #[cite: 10]
        print_formatted_text(ANSI(f"{OWN_COLOR}{render_right(msg_str)}{RESET}")) #[cite: 10]

```

* **`PromptSession(erase_when_done=True)`**: Quản lý ô nhập tin nhắn. Tự động xóa dòng gõ thô sau khi ấn Enter để tránh bị lặp đôi dòng chữ.


* **`with patch_stdout():`** *(Kỹ thuật quan trọng nhất)*: Nếu không có hàm này, khi bạn đang gõ dở một câu mà có tin nhắn từ người khác tới, dòng tin mới sẽ đè làm rách/nát câu bạn đang gõ. `patch_stdout()` sẽ **tạm ẩn con trỏ bạn đang gõ, in tin nhắn mới nhận lên trên, rồi khôi phục lại nguyên vẹn câu chữ bạn đang gõ dở** ở bên dưới.