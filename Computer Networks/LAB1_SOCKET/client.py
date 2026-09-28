"""
CLIENT - ung dung chat qua LAN dung socket (giao dien terminal)
Chay file nay tren MAY CLIENT (dung chung 1 file cho tat ca moi nguoi trong
nhom, chi khac ten nhap luc chay).

Giao dien mo phong chat app:
    - Tin nhan CUA BAN     -> can PHAI man hinh, mau xanh la, kem gio gui
    - Tin nhan NGUOI KHAC  -> can TRAI man hinh, MOI NGUOI MOT MAU RIENG
      (mau duoc tinh co dinh tu ten, ai ten do luon giu dung mau do suot
      buoi chat, giup phan biet nhanh khi phong co nhieu nguoi cung nhan)
    - Thong bao vao/roi phong -> can GIUA, chu mo (dim)

CAI DAT (chi can lam 1 lan tren moi may client, KHONG can tren may server):
    pip install prompt_toolkit

Cach chay:
    python client.py
"""

import socket
import threading
import sys
import shutil
from datetime import datetime, timezone, timedelta

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.patch_stdout import patch_stdout


# ===== Mui gio Viet Nam (UTC+7) =====
VN_TZ = timezone(timedelta(hours=7))


def get_now_str():
    """Lay gio hien tai theo mui gio Viet Nam (UTC+7), khong phu thuoc gio he thong."""
    return datetime.now(VN_TZ).strftime("%H:%M")


# ===== Mau sac (ANSI) =====
RESET = "\033[0m"
DIM = "\033[2m"
OWN_COLOR = "\033[92m"  # xanh la sang, rieng cho tin nhan cua chinh minh
# Bang mau cho nguoi khac - moi ten se luon roi vao dung 1 mau co dinh
OTHER_PALETTE = [
    "\033[94m",  # xanh duong
    "\033[93m",  # vang
    "\033[95m",  # hong tim (magenta)
    "\033[96m",  # xanh ngoc (cyan)
    "\033[91m",  # do nhat
    "\033[33m",  # cam/vang dam
    "\033[35m",  # tim
    "\033[36m",  # xanh ngoc dam
]


def color_for(name):
    """Tinh mau co dinh cho 1 cai ten - cung 1 ten luon ra cung 1 mau."""
    idx = sum(ord(c) for c in name) % len(OTHER_PALETTE)
    return OTHER_PALETTE[idx]


def get_width():
    """Lay be rong hien tai cua terminal (so ky tu), mac dinh 80 neu khong doc duoc."""
    return shutil.get_terminal_size((80, 20)).columns


def render_right(text):
    """Tra ve chuoi da can phai theo be rong terminal hien tai."""
    width = get_width()
    return text if len(text) >= width else text.rjust(width)


def render_center(text):
    """Tra ve chuoi da can giua theo be rong terminal hien tai."""
    width = get_width()
    if len(text) >= width:
        return text
    pad = (width - len(text)) // 2
    return " " * pad + text


def input_indent(last_msg_len=None):
    """Khoang trang dem truoc prompt.
    Neu da gui tin nhan, canh [name] thang theo dung vi tri bat dau cua tin nhan vừa gui."""
    width = get_width()
    if last_msg_len is not None:
        pad = max(0, width - last_msg_len)
    else:
        pad = max(0, width // 2 - 6)
    return " " * pad


def receive_messages(sock):
    """Chay nen: lien tuc nhan tin tu server, can trai, to mau theo nguoi gui.
    Nho co patch_stdout() bao ngoai vong lap chinh, cac lenh print() o day
    se KHONG lam roi dong ban dang go, du dang chay o thread khac."""
    try:
        with sock.makefile("r", encoding="utf-8", newline="\n") as reader:
            while True:
                line = reader.readline()
                if not line:
                    print_formatted_text(ANSI(f"{DIM}{render_center('*** Mat ket noi toi server ***')}{RESET}"))
                    break
                text = line.rstrip("\n")
                now = get_now_str()

                if text.startswith("***"):
                    print_formatted_text(ANSI(f"{DIM}{render_center(f'{text}  ({now})')}{RESET}"))
                    continue

                if text.startswith("["):
                    end = text.find("]")
                    if end != -1:
                        sender = text[1:end]
                        msg = text[end + 2:] if text[end + 1:end + 2] == " " else text[end + 1:]
                        color = color_for(sender)
                        print_formatted_text(ANSI(f"{color}{sender} ({now}): {msg}{RESET}"))
                        continue

                print(text)
    except OSError:
        pass


def main():
    server_ip = input("Nhap dia chi IP cua may server: ").strip()
    port_str = input("Nhap port (Enter de dung mac dinh 5000): ").strip()
    port = int(port_str) if port_str else 5000
    name = input("Nhap ten cua ban: ").strip() or "Khach"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((server_ip, port))
    except OSError as e:
        print(f"Khong the ket noi toi {server_ip}:{port} -> {e}")
        print("Kiem tra lai: server da chay chua? IP dung chua? cung mang Wi-Fi/LAN chua?")
        sys.exit(1)
    sock.settimeout(None)

    sock.sendall((name + "\n").encode("utf-8"))
    print(f"Da ket noi toi server {server_ip}:{port}. Go tin nhan va Enter de gui. Go /exit de thoat.\n")

    t = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    t.start()

    # erase_when_done=True: sau khi Enter, dong vua go se duoc XOA thay vi
    # in de nguyen (tranh bi lap 2 dong cho cung 1 tin nhan cua chinh minh)
    session = PromptSession(erase_when_done=True)
    last_msg_len = None

    try:
        with patch_stdout():
            while True:
                text = session.prompt(input_indent(last_msg_len) + f"[{name}] ")
                if text.strip() == "/exit":
                    break
                if text == "":
                    continue
                sock.sendall((text + "\n").encode("utf-8"))
                now = get_now_str()
                msg_str = f"{name} ({now}): {text}"
                last_msg_len = len(msg_str)
                print_formatted_text(ANSI(f"{OWN_COLOR}{render_right(msg_str)}{RESET}"))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()
        print("Da dong ket noi.")


if __name__ == "__main__":
    main()