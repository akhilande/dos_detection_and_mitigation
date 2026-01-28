#!/usr/bin/env python3
import socket
import signal
import sys
import os
import time

HOST = '0.0.0.0'
PORT = 8080
LOG_FILE = 'request_log.txt'
server_socket = None

def cleanup(sig=None, frame=None):
    print("\n[!] Shutting down server...")
    if server_socket:
        server_socket.close()
    print("[+] Port released. Clean exit.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def load_html():
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except:
        return "<h1>DoS Lab Server</h1>"

def log_request(ip):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{time.time()}|{ip}\n")

def start_server():
    global server_socket
    html = load_html()
    
    # Clear old log
    open(LOG_FILE, 'w').close()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    
    print(f"[*] WEAK server on http://192.168.56.101:{PORT}")
    print("[*] Logging requests to request_log.txt")
    print("[*] Press CTRL+C to stop\n")
    
    while True:
        try:
            client, addr = server_socket.accept()
            ip = addr[0]
            print(f"[+] {ip}")
            log_request(ip)  # Log every request
            time.sleep(0.05)
            data = client.recv(512)
            resp = f"HTTP/1.1 200 OK\r\nContent-Length: {len(html)}\r\n\r\n{html}"
            client.sendall(resp.encode())
            client.close()
        except:
            pass

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    start_server()
