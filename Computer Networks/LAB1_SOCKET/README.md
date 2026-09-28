HUONG DAN CHAY VA KIEM TRA - CHAT QUA LAN DUNG SOCKET
======================================================

MO HINH: 1 may SERVER + 2 may CLIENT (A va B), ca 3 may cung mot mang
Wi-Fi/LAN. A va B khong noi truc tiep voi nhau, ma chat qua trung gian
la SERVER (server nhan tin tu 1 client roi chuyen tiep cho client con lai).

FILE CAN CO:
  - server.py   -> chay tren MAY SERVER
  - client.py   -> chay tren MAY A va MAY B (dung chung 1 file)

YEU CAU TRUOC KHI CHAY
-----------------------
1. Ca 3 may deu da cai Python 3 (kiem tra bang lenh: python --version
   hoac python3 --version).
2. Ca 3 may PHAI cung mot mang Wi-Fi/LAN (vi du cung ket noi vao 1 router,
   hoac cung 1 diem phat Hotspot).
3. Copy file server.py sang may Server; copy file client.py sang may A
   va may B.

BUOC 1: TIM DIA CHI IP CUA MAY SERVER
--------------------------------------
Tren MAY SERVER, mo Command Prompt / Terminal va go:
  - Windows:      ipconfig
                  -> tim dong "IPv4 Address" trong phan Wi-Fi, vi du 192.168.0.104
  - macOS:        ifconfig | grep "inet "
                  -> tim dia chi dang 192.168.x.x (bo qua 127.0.0.1)
  - Linux:        ip addr
                  -> tim dia chi dang 192.168.x.x hoac 10.x.x.x

  Ghi lai dia chi IP nay (vi du: 192.168.1.12). Day la IP ma 2 may
  client se can nhap vao khi ket noi.

BUOC 2: CHAY SERVER
---------------------
Tren MAY SERVER:
  python server.py

Man hinh se hien:
  === SERVER dang chay tai 0.0.0.0:5000 ===

  -> KHONG TAT cua so nay trong suot buoi chat.

BUOC 3: CHAY CLIENT A
------------------------
Tren MAY A:
  python client.py

Chuong trinh se hoi lan luot:
  Nhap dia chi IP cua may server: 192.168.1.12   (IP ghi o Buoc 1)
  Nhap port (Enter de dung mac dinh 5000): (Enter)
  Nhap ten cua ban: An

Neu ket noi thanh cong se thay:
  Da ket noi toi server 192.168.1.12:5000. Go tin nhan va Enter de gui.

  Ben cua so Server cung se hien:
  [+] An (192.168.1.xx:xxxxx) da vao phong chat

BUOC 4: CHAY CLIENT B
------------------------
Tren MAY B, lam giong het Buoc 3 nhung nhap ten la Binh.

KIEM TRA HOAT DONG (TEST)
----------------------------
1. Test A gui, B nhan:
   - Tren may A, go: "Chao Binh, minh la An" roi Enter
   - Ket qua mong doi:
       + Man hinh Server hien: [An] Chao Binh, minh la An
       + Man hinh B hien:      [An] Chao Binh, minh la An
       + Man hinh A KHONG hien lai tin cua chinh minh (dung, vi server
         khong gui nguoc lai cho nguoi vua gui)

2. Test B gui, A nhan:
   - Tren may B, go: "Chao An, minh la Binh" roi Enter
   - Ket qua mong doi: man hinh A va Server deu hien tin nay.

3. Test nhan biet vao/roi phong:
   - Dong client A (go /exit hoac Ctrl+C)
   - Man hinh B va Server se hien: *** An da roi phong chat ***
   - Mo lai client A (chay python client.py, nhap lai IP + ten An)
   - Man hinh B va Server se hien: *** An da vao phong chat ***

4. Test gui lien tuc nhieu tin:
   - Go nhieu dong tin nhan lien tiep tu ca A va B xen ke nhau, kiem tra
     thu tu hien thi tren tung may co dung khong.

KET THUC BUOI CHAT
---------------------
  - Tren A va B: go /exit (hoac Ctrl+C) de dong ket noi
  - Tren Server: nhan Ctrl+C de dung server

XU LY LOI THUONG GAP
------------------------
Loi "Khong the ket noi toi ... -> [Errno ...] Connection refused"
  -> Server chua chay, hoac go sai IP/port. Kiem tra lai Buoc 1 va 2.

Loi ket noi bi "timeout" / treo may khong ket noi duoc
  -> Kha nang do FIREWALL tren may Server chan cong 5000.
     Windows: vao Windows Defender Firewall -> Allow an app through
     firewall -> cho phep Python (hoac tam thoi tat firewall de test).
  -> Kiem tra lai ca 3 may co THAT SU cung mang Wi-Fi khong (vi du mang
     cong ty/truong co the chan giao tiep giua cac thiet bi trong mang).

Doi IP server (vi du chuyen mang khac)
  -> Chi can chay lai Buoc 1 de lay IP moi, nhap IP moi nay khi chay lai
     client.py o A va B. Khong can sua code.

Port 5000 bi chiem (loi "Address already in use")
  -> Mo file server.py, doi PORT = 5000 thanh so khac (vi du 5050).
     Khi chay client.py, o buoc nhap port thi go dung so do (5050).

GHI CHU
---------
- Neu 3 may deu la may that (khong dung Hotspot dien thoai/laptop nhu
  trong ban demo cu), cach lam nay van dung y het, chi can dam bao cung
  1 mang va biet dung IP cua may lam server.
- File client.py dung chung cho ca A va B; diem khac nhau duy nhat la
  cai TEN ban nhap luc chay chuong trinh.

  
