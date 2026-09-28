"""
SERVER - ung dung chat qua LAN dung socket
Chay file nay tren MAY SERVER (may con lai se ket noi toi may nay).

Cach chay:
    python server.py

Server se lang nghe tren tat ca cac card mang (0.0.0.0) o cong PORT ben duoi.
Moi client ket noi vao se gui ten cua minh len dau tien, sau do moi tin nhan
client gui len se duoc SERVER CHUYEN TIEP (broadcast) cho tat ca client khac.
"""

import socket
import threading

HOST = "0.0.0.0"   # nghe tren moi card mang cua may nay
PORT = 5000         # neu port nay bi chiem, doi sang so khac (vd 5001) va sua lai trong client.py

clients = {}            # dict: conn -> ten nguoi dung
clients_lock = threading.Lock()


def broadcast(message, exclude_conn=None):
    """Gui 'message' toi tat ca client dang ket noi, tru client 'exclude_conn' (thuong la nguoi vua gui)."""
    with clients_lock:
        targets = list(clients.items())
    for conn, name in targets:
        if conn is exclude_conn:
            continue
        try:
            conn.sendall(message.encode("utf-8"))
        except OSError:
            pass  # client do co the da mat ket noi, se duoc don dep sau


def handle_client(conn, addr):
    """Chay rieng cho tung client, doc tin nhan lien tuc va chuyen tiep cho nguoi khac."""
    name = None
    try:
        with conn.makefile("r", encoding="utf-8", newline="\n") as reader:
            # Dong dau tien client gui len la TEN cua ho
            first_line = reader.readline()
            if not first_line:
                return
            name = first_line.strip() or f"Khach_{addr[1]}"

            with clients_lock:
                clients[conn] = name
            print(f"[+] {name} ({addr[0]}:{addr[1]}) da vao phong chat")
            broadcast(f"*** {name} da vao phong chat ***\n")

            while True:
                line = reader.readline()
                if not line:
                    break  # client dong ket noi
                text = line.rstrip("\n")
                if text == "":
                    continue
                print(f"[{name}] {text}")
                broadcast(f"[{name}] {text}\n", exclude_conn=conn)
    except (ConnectionResetError, OSError):
        pass
    finally:
        with clients_lock:
            clients.pop(conn, None)
        conn.close()
        if name:
            print(f"[-] {name} da roi phong chat")
            broadcast(f"*** {name} da roi phong chat ***\n")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"=== SERVER dang chay tai {HOST}:{PORT} ===")
    print("De client ket noi duoc, hay xem IP thuc cua may nay (vd 192.168.x.x) bang lenh:")
    print("  Windows: ipconfig      |      Mac/Linux: ifconfig hoac ip addr")
    print("Nhan Ctrl+C de dung server.\n")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nDang dung server...")
    finally:
        server.close()
        print("Server da dong.")


if __name__ == "__main__":
    main()
