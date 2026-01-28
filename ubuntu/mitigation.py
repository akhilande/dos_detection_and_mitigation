#!/usr/bin/env python3
import signal
import sys
import time
import subprocess
from collections import defaultdict

LOG_FILE = 'request_log.txt'
THRESHOLD = 50         
TIME_WINDOW = 5        
INTERVAL = 2           
BLOCK_TIME = 60        
blocked_ips = {}       
running = True

def cleanup(sig=None, frame=None):
    print("\n[!] Cleaning up iptables...")
    for ip in list(blocked_ips.keys()):
        unblock_ip(ip)
    print("All rules removed. Clean exit.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def block_ip(ip):
    cmd = f"iptables -A INPUT -s {ip} -j DROP"
    subprocess.run(cmd, shell=True)
    blocked_ips[ip] = time.time() + BLOCK_TIME
    print(f"BLOCKED: {ip} for {BLOCK_TIME}s")

def unblock_ip(ip):
    cmd = f"iptables -D INPUT -s {ip} -j DROP"
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
    if ip in blocked_ips:
        del blocked_ips[ip]
    print(f" UNBLOCKED: {ip}")

def check_unblock():
    current = time.time()
    for ip in list(blocked_ips.keys()):
        if current >= blocked_ips[ip]:
            unblock_ip(ip)

def count_requests():
    counts = defaultdict(int)
    current = time.time()
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if '|' in line:
                    parts = line.strip().split('|')
                    ts, ip = float(parts[0]), parts[1]
                    if current - ts <= TIME_WINDOW:
                        counts[ip] += 1
    except:
        pass
    return counts

def monitor():
    print("=" * 50)
    print("   DoS MITIGATION SYSTEM")
    print("=" * 50)
    print(f"[*] Threshold: {THRESHOLD} req/{TIME_WINDOW}s")
    print(f"[*] Block time: {BLOCK_TIME}s")
    print("[*] Press CTRL+C to stop\n")
    
    while running:
        check_unblock()
        counts = count_requests()
        ts = time.strftime('%H:%M:%S')
        print(f"\n[{ts}] Monitoring...")
        
        if not counts:
            print("    No requests")
        
        for ip, count in counts.items():
            if ip in blocked_ips:
                remain = int(blocked_ips[ip] - time.time())
                print(f"    {ip} -> BLOCKED ({remain}s left)")
            elif count >= THRESHOLD:
                print(f"     ATTACK: {ip} -> {count} requests")
                block_ip(ip)
            else:
                print(f"    ✓ {ip} -> {count} requests")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    monitor()
