
# BÁO CÁO THỰC HÀNH LAB MẠNG CCNA (PACKET TRACER)

## THÔNG TIN SINH VIÊN
* **Họ và tên:** Nguyễn Hữu Dũng  
* **Mã sinh viên (Student ID):** 2410234  
* **Môn học:** Mạng máy tính / CCNA  

---

## TỔNG QUAN THAM SỐ CẤU HÌNH

### 1. Tham số Câu 1 (7.0 điểm)
* **$X$ (Mã trung tâm/Định danh):** `111`
* **$Y$ (Số octet IP):** `234` *(Rút gọn từ MSSV 2410234 để đảm bảo giới hạn 8-bit octet)*
* **Dải mạng nội bộ (LAN):** `111.234.x.x/24`
  * VLAN 10 (IT): `111.234.10.0/24` - Gateway: `111.234.10.254`
  * VLAN 20 (HR): `111.234.20.0/24` - Gateway: `111.234.20.254`
  * VLAN 30 (Sales): `111.234.30.0/24` - Gateway: `111.234.30.254`
* **Dải mạng kết nối R1 - Sw_Core:** `20.20.20.0/30`
* **Máy chủ Internet (Server0):** `86.0.188.2/24`

### 2. Tham số Câu 2 (3.0 điểm)
* **$X$ (Ngày sinh):** `30`
* **$Y$ (Tháng sinh):** `4`
* **Phân vùng bên trái (Domain_Left):** Dải IP `172.30.4.0/24`
* **Phân vùng bên phải (Domain_Right):** Dải IP `174.30.4.0/24`

---

## NỘI DUNG VÀ KẾT QUẢ CẤU HÌNH

---

### CÂU 1: MÔ HÌNH MẠNG DOANH NGHIỆP TỔNG HỢP (7.0 ĐIỂM)

#### 1. Cấu hình VTP & VLAN
* **VTP Domain:** `ccna.com` | **Password:** `admin`
* **Sw_Core:** Cấu hình VTP Mode `Server`, khởi tạo VLAN 10, 20, 30.
* **SW_01 & SW_02:** Cấu hình VTP Mode `Client`, đồng bộ VLAN từ Sw_Core.
* **Cổng Trunk:** Thiết lập IEEE 802.1Q trên tất cả các đường liên kết giữa Sw_Core, SW_01 và SW_02.

#### 2. Dịch vụ DHCP Server (trên Sw_Core)
* Khởi tạo các Sub-interface Vlan10, Vlan20, Vlan30 làm Default Gateway.
* Cấu hình 3 DHCP Pool cấp phát tự động IP, Subnet Mask và Gateway cho các thiết bị PC thuộc VLAN 10, 20, 30.
* **Kết quả:** PC1, PC2, PC3, PC4 xin thành công địa chỉ IP dạng `111.234.x.x`.

#### 3. Định tuyến RIPv2 & Default Route
* Cấu hình RIPv2 trao đổi routing table giữa **Sw_Core** và **Router R1**.
* Cấu hình Default Route trên Sw_Core trỏ về IP WAN của R1 (`20.20.20.2`).

#### 4. Ánh xạ địa chỉ NAT Overload / PAT (trên Router R1)
* Cấu hình ACL 1 cho phép dải IP nội bộ `111.234.0.0/16`.
* Gán `ip nat inside` trên cổng đấu nối nội bộ (Gig0/0) và `ip nat outside` trên cổng ra Server (Gig0/1).
* Kích hoạt PAT bằng lệnh:
  ```cisco
  ip nat inside source list 1 interface Gig0/1 overload
  ```
* **Kết quả Kiểm tra Ping & NAT:**
  * Từ PC1 (`111.234.10.1`) ping thành công tới Server0 (`86.0.188.2`) với tỷ lệ 100%.
  * Lệnh `show ip nat translations` trên R1 hiển thị chi tiết các bản ghi dịch địa chỉ IP nội bộ sang IP công cộng.

#### 5. Cấu hình SPAN Port (Port Mirroring)
* Cấu hình giám sát lưu lượng truy cập của toàn bộ VLAN 10, 20, 30 đẩy log về Server_Giamsat qua cổng `Fa0/4`:
  ```cisco
  monitor session 1 source vlan 10 , 20 , 30
  monitor session 1 destination interface Fa0/4
  ```
* **Kết quả:** Kiểm tra bằng lệnh `show monitor` trên Sw_Core xác nhận Session 1 hoạt động đúng thiết kế.

#### 6. Quản trị từ xa SSH & Telnet
* Khởi tạo SSH Version 2 với độ dài khóa RSA 1024-bit, domain `ccna.com`.
* Tạo tài khoản quản trị: `admin` / `cisco123` với quyền `privilege 15`.
* **Kết quả:** Từ Command Prompt trên PC1, truy cập quản trị thành công qua lệnh:
  ```bash
  ssh -l admin 111.234.10.254
  ```

---

### CÂU 2: CẤU HÌNH ĐỊNH TUYẾN PHÂN VÙNG VTP (3.0 ĐIỂM)

#### 1. Quy hoạch địa chỉ IP ($X=30, Y=4$)
* **Router0:**
  * Cổng `Gig0/0`: `172.30.4.254/24`
  * Cổng `Gig0/1`: `174.30.4.254/24`
* **Switch 0 (Server Left):** IP Vlan1 `172.30.4.110/24` | Default Gateway: `172.30.4.254`
* **Switch 2 (Client Left):** IP Vlan1 `172.30.4.120/24` | Default Gateway: `172.30.4.254`
* **Switch 1 (Server Right):** IP Vlan1 `174.30.4.130/24` | Default Gateway: `174.30.4.254`
* **Switch 3 (Client Right):** IP Vlan1 `174.30.4.140/24` | Default Gateway: `174.30.4.254`
* **PC0:** `172.30.4.10/24` | Gateway: `172.30.4.254`
* **PC1:** `174.30.4.10/24` | Gateway: `174.30.4.254`

#### 2. Cấu hình VTP Phân vùng
* **Nhánh trái:** VTP Domain `Domain_Left` (Switch 0 là Server tạo VLAN 10, 20; Switch 2 là Client).
* **Nhánh phải:** VTP Domain `Domain_Right` (Switch 1 là Server tạo VLAN 110, 120; Switch 3 là Client).

#### 3. Kết quả Kiểm tra
* **Kiểm tra kết nối Ping (1.0 điểm):**
  * Từ **PC0** ping thành công tới Router0 (`172.30.4.254`), Switch0 (`172.30.4.110`), Switch2 (`172.30.4.120`) và PC1 (`174.30.4.10`).
* **Kiểm tra quản trị SSH (1.0 điểm):**
  * Từ **PC0** SSH thành công tới Switch0 (`172.30.4.110`) và Router0 (`172.30.4.254`).
  * Từ **PC1** SSH thành công tới Switch1 (`174.30.4.130`) và Router0 (`174.30.4.254`).

---


## POC cho các câu trong đề 


### Câu 1 (7 điểm) Cho mô hình sau:

<img width="967" height="597" alt="image" src="https://github.com/user-attachments/assets/84f26979-bc78-43fe-b03f-f53b2a480bbb" />


#### 1. Cấu hình Hostname, Enable Password và IP Interface
   
Trên Router R1:

<img width="950" height="1011" alt="image" src="https://github.com/user-attachments/assets/be376cd9-58f1-414d-9dee-c6c7eec7f80d" />

Trên Sw_Core (Switch 3560):

<img width="961" height="1008" alt="image" src="https://github.com/user-attachments/assets/e0af90ef-aa06-4a95-8481-2ae67ec04042" />

Trên SW_01:

<img width="955" height="993" alt="image" src="https://github.com/user-attachments/assets/53d31415-12e4-4564-8c3b-e3fda933ffa1" />

Trên SW_02:

<img width="938" height="1000" alt="image" src="https://github.com/user-attachments/assets/eae92dbe-1bf7-4924-bc17-987dee0da70f" />


#### 2. Cấu hình Trunking, VTP Domain và Khởi tạo VLAN

Cấu hình đường Trunk kết nối giữa các Switch:

SW_Core:

<img width="943" height="976" alt="image" src="https://github.com/user-attachments/assets/7be91cfb-94cb-4f16-9cbd-e99141f21e96" />

SW_01:

<img width="933" height="958" alt="image" src="https://github.com/user-attachments/assets/3452288a-61a2-4acb-a6c8-646f13062f6f" />


SW_02:

<img width="925" height="992" alt="image" src="https://github.com/user-attachments/assets/039837ea-e547-4f14-a90d-6c2f175bb9ce" />


Cấu hình VTP Domain ccna.com và Mật khẩu admin:

Sw_Core (VTP Server):



SW_01 (VTP Client):

<img width="557" height="143" alt="image" src="https://github.com/user-attachments/assets/054437b6-afb9-4d86-a2b3-5532fea8ce7f" />

SW_02 (VTP Client):

<img width="873" height="123" alt="image" src="https://github.com/user-attachments/assets/6361a8b1-11cd-4012-b188-625c506dfa37" />


#### 3. Cấu hình Interface VLAN & Gán cổng Access
   
Trong đó:

X tương ứng là đơn vị Trung tâm , tôi chọn 111

Y là số báo danh tương ứng . Nhưng quy tắc địa chỉ IPv4: Địa chỉ IP gồm 4 số phân cách bởi dấu chấm, mỗi số chỉ được nằm trong khoảng từ 0 đến 255. Do đó, Số báo danh $Y = 2410234$ (7 chữ số) không thể điền nguyên văn vào 1 octet IP. Vì vậy , tôi chọn Y là 234 


Trên Sw_Core (Tạo Gateway cho các VLAN):

<img width="892" height="521" alt="image" src="https://github.com/user-attachments/assets/665bfc90-fb9d-4e1d-84c8-d2ddcbabe73a" />


#### 4. Cấu hình để SW_Core làm DHCP Server cấp địa chỉ động cho các máy tính thuộc Vlan 10, 20, 30.

<img width="932" height="282" alt="image" src="https://github.com/user-attachments/assets/2edf4edb-2811-44b6-b8d1-a41c52dbcb18" />


#### 5. Cấu hình giao thức định tuyến RIPv2 giữa SW_Core và Router R1 (chỉ trên các dải đại chỉ 20.20.20.0/24 và các dải đại chỉ Vlan 10,20,30).

Trên Sw_Core:

<img width="545" height="145" alt="image" src="https://github.com/user-attachments/assets/d7105daa-b2f8-44a8-8c6b-c4cc6a082204" />

Trên R1:

<img width="721" height="202" alt="image" src="https://github.com/user-attachments/assets/812c11d5-54b2-4852-8b38-e302abd45b2f" />

#### 6. Cấu hình định tuyến và ánh xạ địa chỉ IP NAT (PAT) trên Router R1 để sao cho các User từ vlan 10,20,30 ping được đến máy chủ 86.0.188.2/24

<img width="712" height="172" alt="image" src="https://github.com/user-attachments/assets/c2768d64-7321-4427-94e6-6793423c19e5" />

<img width="952" height="920" alt="image" src="https://github.com/user-attachments/assets/ca6d7e8b-1dd1-478f-9612-5c38968ee03a" />

Lỗi DHCP request failed. trên PC2, PC3, PC4 xảy ra do chưa gán đúng cổng Access cho VLAN 20 và 30 trên SW_01, SW_02, hoặc đường Trunk nối từ Sw_Core sang SW_02 chưa bật.

Bước 1: Cấu hình cổng trên SW_01 (cho PC2 - VLAN 20)

Mở CLI của SW_01

<img width="933" height="957" alt="image" src="https://github.com/user-attachments/assets/94f929ca-0c76-4d9d-9a3a-8f29c979d59a" />

Bước 2: Cấu hình cổng trên SW_02 (cho PC3 - VLAN 20 & PC4 - VLAN 30)

Mở CLI của SW_02

<img width="945" height="998" alt="image" src="https://github.com/user-attachments/assets/a4a35504-1182-413b-9e31-0ce7e6d65237" />

Bước 3: Đảm bảo cổng Fa0/2 trên Sw_Core đã bật Trunk

Mở CLI của Sw_Core

<img width="538" height="102" alt="image" src="https://github.com/user-attachments/assets/fb02353b-4af6-4f51-9be1-e41b2424e3bc" />

Check lại Ip các máy trước khi test :

<img width="1820" height="913" alt="image" src="https://github.com/user-attachments/assets/3853adeb-b585-427b-b4c8-e78b65cfa855" />

Test Ping tới Server0

<img width="706" height="376" alt="image" src="https://github.com/user-attachments/assets/6383a1c3-4b59-4448-ac65-3ac61ff19069" />

Test SSH quản trị Sw_Core từ PC1:

<img width="546" height="166" alt="image" src="https://github.com/user-attachments/assets/03c180c4-ca72-4fc5-b851-8b33359fdc13" />


#### 7. Cấu hình Span port trên Switch_Core, với cổng đón nhận log giám sát là Fa0/4 để đẩy log về Server_Giamsat, sao cho giám sát được các vlan 10,20,30 

Sw_Core

<img width="727" height="307" alt="image" src="https://github.com/user-attachments/assets/e4819cf2-2d0b-4daa-9e07-9b5aa5af237c" />


#### 8. Cấu hình quản trị SSH, Telnet, với PC1 là máy tính quản trị có thể quản trị từ xa qua giao thức SSH đối với thiết bị Switch_Core 

Cấu hình SSH và Telnet trên Sw_Core và cấu hình tài khoản và cổng VTY:

<img width="607" height="257" alt="image" src="https://github.com/user-attachments/assets/832a9da6-c0e5-4f51-8419-e34e9ee94276" />

Bước 2: Kiểm tra kết nối SSH từ PC1 (Test thực tế)

<img width="481" height="121" alt="image" src="https://github.com/user-attachments/assets/e515febc-71d0-4c7c-9e8c-233478688aac" />


### Câu 2 (3 điểm) Cho mô hình mạng được mô tả như hình vẽ dưới:

<img width="1126" height="641" alt="image" src="https://github.com/user-attachments/assets/677a7d24-e849-4988-abdf-bb9056e0f6af" />

### a. Cấu hình cơ bản Router, Switch (Đặt tên, cấu hình quản trị địa chỉ IP cho từng thiết bị theo mô tả) 

 Mở CLI trên Router0 :

#### 1. CẤU HÌNH CƠ BẢN, IP & SSH TRÊN ROUTER0

#####  Cấu hình IP các cổng

<img width="852" height="387" alt="image" src="https://github.com/user-attachments/assets/5f910d64-34d6-41bf-b2a1-06fc5d4ea695" />

#####  Cấu hình SSH quản trị

<img width="751" height="260" alt="image" src="https://github.com/user-attachments/assets/1f104040-117d-4771-a4a8-40368c0b9c76" />

#### 2. CẤU HÌNH NHÁNH TRÁI (SWITCH 0 & SWITCH 2)

##### Trên Switch 0 (VTP Server, VLAN 10, 20):

<img width="837" height="826" alt="image" src="https://github.com/user-attachments/assets/2c48fd9e-fbe8-4988-af8e-2013d39a9caf" />

##### Trên Switch 2 (VTP Client):

<img width="811" height="525" alt="image" src="https://github.com/user-attachments/assets/266fc89c-5ff4-4ac6-8b69-e2d10a918141" />

#### 3. CẤU HÌNH NHÁNH PHẢI (SWITCH 1 & SWITCH 3)

##### Trên Switch 1 (VTP Server, VLAN 110, 120):

<img width="792" height="805" alt="image" src="https://github.com/user-attachments/assets/0c24caac-df8b-4dd9-92d1-7c09d111d1e2" />

##### Trên Switch 3 (VTP Client):

<img width="898" height="552" alt="image" src="https://github.com/user-attachments/assets/898773ce-eeee-427a-b0b6-5a0f5176ba4c" />


#### 4. CẤU HÌNH THIẾT BỊ ĐẦU CUỐI (PC0, PC1)

##### PC0

<img width="941" height="676" alt="image" src="https://github.com/user-attachments/assets/907204d0-5f77-45c2-be9b-b28829d1aa22" />


##### PC1

<img width="947" height="776" alt="image" src="https://github.com/user-attachments/assets/a88b46b3-9333-4015-af50-5c58513cbd2a" />



### b. Từ PC0 ping đến PC1, đến được Router, Switch 

##### Router0

<img width="577" height="208" alt="image" src="https://github.com/user-attachments/assets/2c94545e-293a-46aa-83a3-752a108ad97e" />


##### Switch0

<img width="537" height="417" alt="image" src="https://github.com/user-attachments/assets/9e7eb601-4e93-4a8b-a8da-3c28e46fd5fd" />


##### Switch2

<img width="507" height="410" alt="image" src="https://github.com/user-attachments/assets/b02b9365-bc5e-4601-ba39-256dbb9fac93" />


##### PC1

<img width="505" height="403" alt="image" src="https://github.com/user-attachments/assets/4dfe2fc0-7291-4471-8ca5-d9edb9054f29" />


### c. PC0 thực hiện SSH đến Switch0, Router0;  kết nối và quản trị qua giao thức SSH đến Switch1, Router0

#### Từ PC0

##### SSH tới Switch0

<img width="383" height="223" alt="image" src="https://github.com/user-attachments/assets/6cdb6bc7-c23e-47b8-bde9-20e6d7e19b69" />

##### SSH tới Router0

<img width="308" height="110" alt="image" src="https://github.com/user-attachments/assets/ede3537a-e68a-44d7-a063-49cfb9fd9336" />

#### Từ PC1

##### SSH tới Switch1

<img width="377" height="128" alt="image" src="https://github.com/user-attachments/assets/c5411a6e-2f04-418e-9747-25b287a3df18" />

##### SSH tới Router0

<img width="287" height="137" alt="image" src="https://github.com/user-attachments/assets/fd56d216-72ea-442a-bdd5-274c9979a16e" />


## KẾT LUẬN
Toàn bộ các yêu cầu bài thi về cấu hình thiết bị mạng Cisco (Router, Layer 3 Switch, Layer 2 Switch), phân chia VLAN, VTP, cấp phát IP động DHCP, định tuyến RIPv2, NAT Overload (PAT), SPAN port giám sát và bảo mật SSH đã được triển khai chính xác, kiểm thử thông suốt và đáp ứng đầy đủ tiêu chí đề bài.
