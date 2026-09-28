HƯỚNG DẪN CHẠY VÀ KIỂM TRA - CHAT QUA LAN DÙNG SOCKET 
======================================================
### make by: Nguyễn Hữu Dũng -2410234

MÔ HÌNH: 1 máy SERVER + 2 máy CLIENT (A và B), cả 3 máy cùng một mạng
Wi-Fi/LAN. A và B không nối trực tiếp với nhau, mà chat qua trung gian
là SERVER (server nhận tin từ 1 client rồi chuyển tiếp cho client còn lại).

FILE CẦN CÓ:
  - server.py   -> chạy trên MÁY SERVER
  - client.py   -> chạy trên MÁY A và MÁY B (dùng chung 1 file)

YÊU CẦU TRƯỚC KHI CHẠY
-----------------------
1. Cả 3 máy đều đã cài Python 3 (kiểm tra bằng lệnh: python --version
   hoặc python3 --version).
2. Cả 3 máy PHẢI cùng một mạng Wi-Fi/LAN (ví dụ cùng kết nối vào 1 router,
   hoặc cùng 1 điểm phát Hotspot).
3. Copy file server.py sang máy Server; copy file client.py sang máy A
   và máy B.

BƯỚC 1: TÌM ĐỊA CHỈ IP CỦA MÁY SERVER
--------------------------------------
Trên MÁY SERVER, mở Command Prompt / Terminal và gõ:
  - Windows:      ipconfig
                  -> tìm dòng "IPv4 Address" trong phần Wi-Fi, ví dụ 192.168.0.104
  - macOS:        ifconfig | grep "inet "
                  -> tìm địa chỉ dạng 192.168.x.x (bỏ qua 127.0.0.1)
  - Linux:        ip addr
                  -> tìm địa chỉ dạng 192.168.x.x hoặc 10.x.x.x

  Ghi lại địa chỉ IP này (ví dụ: 192.168.1.12). Đây là IP mà 2 máy
  client sẽ cần nhập vào khi kết nối.

BƯỚC 2: CHẠY SERVER
---------------------
Trên MÁY SERVER:
  python server.py

Màn hình sẽ hiện:
  === SERVER dang chay tai 0.0.0.0:5000 ===

  -> KHÔNG TẮT cửa sổ này trong suốt buổi chat.

BƯỚC 3: CHẠY CLIENT A
------------------------
Trên MÁY A:
  python client.py

Chương trình sẽ hỏi lần lượt:
  Nhap dia chi IP cua may server: 192.168.1.12   (IP ghi ở Bước 1)
  Nhap port (Enter de dung mac dinh 5000): (Enter)
  Nhap ten cua ban: An

Nếu kết nối thành công sẽ thấy:
  Da ket noi toi server 192.168.1.12:5000. Go tin nhan va Enter de gui.

  Bên cửa sổ Server cũng sẽ hiện:
  [+] An (192.168.1.xx:xxxxx) da vao phong chat

BƯỚC 4: CHẠY CLIENT B
------------------------
Trên MÁY B, làm giống hệt Bước 3 nhưng nhập tên là Bình.

KIỂM TRA HOẠT ĐỘNG (TEST)
----------------------------
1. Test A gửi, B nhận:
   - Trên máy A, gõ: "Chào Bình, mình là An" rồi Enter
   - Kết quả mong đợi:
       + Màn hình Server hiện: [An] Chào Bình, mình là An
       + Màn hình B hiện:      [An] Chào Bình, mình là An
       + Màn hình A KHÔNG hiện lại tin của chính mình (đúng, vì server
         không gửi ngược lại cho người vừa gửi)

2. Test B gửi, A nhận:
   - Trên máy B, gõ: "Chào An, mình là Bình" rồi Enter
   - Kết quả mong đợi: màn hình A và Server đều hiện tin này.

3. Test nhận biết vào/rời phòng:
   - Đóng client A (gõ /exit hoặc Ctrl+C)
   - Màn hình B và Server sẽ hiện: *** An da roi phong chat ***
   - Mở lại client A (chạy python client.py, nhập lại IP + tên An)
   - Màn hình B và Server sẽ hiện: *** An da vao phong chat ***

4. Test gửi liên tục nhiều tin:
   - Gõ nhiều dòng tin nhắn liên tiếp từ cả A và B xen kẽ nhau, kiểm tra
     thứ tự hiển thị trên từng máy có đúng không.

KẾT THÚC BUỔI CHAT
---------------------
  - Trên A và B: gõ /exit (hoặc Ctrl+C) để đóng kết nối
  - Trên Server: nhấn Ctrl+C để dừng server

XỬ LÝ LỖI THƯỜNG GẶP
------------------------
Lỗi "Khong the ket noi toi ... -> [Errno ...] Connection refused"
  -> Server chưa chạy, hoặc gõ sai IP/port. Kiểm tra lại Bước 1 và 2.

Lỗi kết nối bị "timeout" / treo máy không kết nối được
  -> Khả năng do FIREWALL trên máy Server chặn cổng 5000.
     Windows: vào Windows Defender Firewall -> Allow an app through
     firewall -> cho phép Python (hoặc tạm thời tắt firewall để test).
  -> Kiểm tra lại cả 3 máy có THẬT SỰ cùng mạng Wi-Fi không (ví dụ mạng
     công ty/trường có thể chặn giao tiếp giữa các thiết bị trong mạng).

Đổi IP server (ví dụ chuyển mạng khác)
  -> Chỉ cần chạy lại Bước 1 để lấy IP mới, nhập IP mới này khi chạy lại
     client.py ở A và B. Không cần sửa code.

Port 5000 bị chiếm (lỗi "Address already in use")
  -> Mở file server.py, đổi PORT = 5000 thành số khác (ví dụ 5050).
     Khi chạy client.py, ở bước nhập port thì gõ đúng số đó (5050).

GHI CHÚ
---------
- Nếu 3 máy đều là máy thật (không dùng Hotspot điện thoại/laptop như
  trong bản demo cũ), cách làm này vẫn đúng y hệt, chỉ cần đảm bảo cùng
  1 mạng và biết đúng IP của máy làm server.
- File client.py dùng chung cho cả A và B; điểm khác nhau duy nhất là
  cái TÊN bạn nhập lúc chạy chương trình.
- Các dòng thông báo do chương trình in ra (ví dụ "Da ket noi toi server...",
  "*** An da vao phong chat ***") được giữ nguyên không dấu, đúng như code
  hiển thị.
