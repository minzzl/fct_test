#!/usr/bin/env python3
# lg_fct_gui.py  ―  ACP-i FCT Tool (LG 테마 GUI)

import os, sys, time, queue, threading, warnings, subprocess, pathlib
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext, simpledialog, messagebox
from datetime import datetime
import pandas as pd
import yaml
import paramiko

# ────────── 실행 위치 ───────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = pathlib.Path(sys.executable).parent
else:
    BASE_DIR = pathlib.Path(__file__).resolve().parent

# ────────── LG 팔레트 ───────────────────────────────────
LG_RED, LG_GRAY_BG, LG_DARKTEXT = "#A50034", "#F2F2F2", "#333333"

# ────────── GUI↔스레드 큐 ───────────────────────────────
log_q: queue.Queue[str] = queue.Queue()
def log(msg: str): log_q.put(msg)

# ────────── 다이얼로그 함수들 ───────────────────────────
def ask_input(title: str, prompt: str) -> str:
    holder = queue.Queue()
    def _ask():
        res = simpledialog.askstring(title, prompt, parent=root)
        holder.put("" if res is None else res)
    root.after(0, _ask)
    return holder.get()

def ask_choice(prompt: str) -> str:
    """(y/n) 또는 (y/n/r) 프롬프트를 버튼으로 처리, 반환값 'y'|'n'|'r'"""
    result = tk.StringVar()
    def _ask():
        win = tk.Toplevel(root); win.title("FCT")
        win.geometry("+{}+{}".format(root.winfo_rootx()+250, root.winfo_rooty()+200))
        win.resizable(False, False); win.attributes("-topmost", True)
        ttk.Label(win, text=prompt, wraplength=320).pack(padx=25, pady=18)
        frm = ttk.Frame(win); frm.pack(pady=(0,18))

        def done(val): result.set(val); win.destroy()
        ttk.Button(frm, text="확인", width=9, command=lambda: done('y')).pack(side="left", padx=6)
        ttk.Button(frm, text="취소", width=9, command=lambda: done('n')).pack(side="left", padx=6)
        if ' r' in prompt.lower():    # r 옵션 포함되면 “다시” 버튼
            ttk.Button(frm, text="다시", width=9, command=lambda: done('r')).pack(side="left", padx=6)
        win.grab_set(); win.protocol("WM_DELETE_WINDOW", lambda: done('n'))
    root.after(0, _ask)
    root.wait_variable(result)
    return result.get()

# ────────── 전역 상수 ──────────────────────────────────
EXCEL_FILE   = BASE_DIR / "local_file.xlsx"
CFG_TEMPLATE = BASE_DIR / "new_cfg.yml"
current_row_index = 0

# ────────── 유틸 함수들 (SSH·Excel 등) ────────────────
def remove_known_host(path, ip):
    if os.path.exists(path):
        with open(path) as f:
            if any(ip in l for l in f):
                subprocess.run(f"ssh-keygen -R {ip}", shell=True)
    return True

def find_next_row_index():
    global current_row_index
    try:
        df = pd.read_excel(EXCEL_FILE)
        for idx, row in df.iterrows():
            if pd.isna(row["Check"]) or row["Check"] == "X":
                current_row_index = idx; return True
        log("[x] No available rows"); return False
    except Exception as e:
        log(f"[x] Excel error: {e}"); return False

def read_sn_mac_from_file():
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty or current_row_index >= len(df):
            log("[x] Excel empty"); return False, None, None
        sn  = str(df.at[current_row_index,"Serial Number"]).strip()
        mac = str(df.at[current_row_index,"Eth Address"]).strip()
        return True, sn, mac
    except Exception as e:
        log(f"[x] Excel read err: {e}"); return False, None, None

def update_check_column():
    try:
        df = pd.read_excel(EXCEL_FILE, dtype={"Check": str})
        df.at[current_row_index,"Check"]="O"; df.to_excel(EXCEL_FILE,index=False)
        log("[v] Excel Check OK"); return True
    except Exception as e:
        log(f"[x] Excel write err: {e}"); return False

def check_ssh_connection(ip, user, pwd="allnewb2b^^"):
    log(f"[...] SSH connect {ip}")
    try:
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=60)
        c.close(); log("[v] SSH OK"); return True
    except Exception:
        log("[x] SSH FAIL"); return False

def execute_cmd(ip, user, cmd, pwd="allnewb2b^^"):
    try:
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=10)
        _, stdout, _ = c.exec_command(cmd)
        out = stdout.read().decode().strip(); c.close(); return out
    except Exception as e:
        log(f"[x] SSH cmd err: {e}"); return None

def write_sn_mac_to_board(sn, mac, ip, user, pwd="allnewb2b^^"):
    log("[...] Write SN/MAC")
    write = (f"echo {sn} > /persist/serial_number && "
             f"/usr/bin/misc-util ETH_MAC {mac} && "
             "echo PACPIA000.AKM > /persist/model_number")
    check = ("cat /persist/serial_number && "
             "/usr/bin/misc-util ETH_MAC && "
             "cat /persist/model_number")
    execute_cmd(ip,user,write,pwd); out=execute_cmd(ip,user,check,pwd)
    if not out: return False
    l=out.splitlines(); ok=(l[0].strip()==sn and l[1].strip()==mac and l[2].strip()=="PACPIA000.AKM")
    log("[v] SN/MAC OK" if ok else "[x] SN/MAC mismatch"); return ok

def write_cfg_to_board(mac, sn, ip, user, pwd="allnewb2b^^"):
    log("[...] Write cfg.yml")
    try:
        with open(CFG_TEMPLATE) as f: cfg=yaml.safe_load(f)
        cfg["ETH"]["mac"], cfg["VERSION"]["serial"]=mac, sn
        tmp=BASE_DIR/"_tmp_cfg.yml"; yaml.dump(cfg, open(tmp,"w"))
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd)
        with open(tmp,"rb") as f:
            stdin,_,_=c.exec_command("cat > /lg_rw/fct_test/cfg.yml")
            stdin.write(f.read()); stdin.close()
        c.close(); tmp.unlink(); log("[v] cfg OK"); return True
    except Exception as e:
        log(f"[x] cfg err: {e}"); return False

def write_pc_launcher_to_board(ip,user,pwd="allnewb2b^^"):
    log("[...] Write launcher files")
    try:
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd)
        c.exec_command("mkdir -p /lg_rw/b2b-platform/http")
        for local,remote in [("index.html","index.html"),("launcher.exe","launcher.exe")]:
            with open(BASE_DIR/local, "rb") as f:
                stdin,_,_=c.exec_command(f"cat > /lg_rw/b2b-platform/http/{remote}")
                stdin.write(f.read()); stdin.close()
        c.close(); log("[v] launcher OK"); return True
    except Exception as e:
        log(f"[x] launcher err: {e}"); return False

def send_time_now(ip,user,pwd="allnewb2b^^"):
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"[...] Send time {now}")
    try:
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd)
        c.exec_command(f"echo '{now}' > /home/root/current_time"); time.sleep(0.5)
        _,stdout,_=c.exec_command("cat /home/root/current_time")
        ok = stdout.read().decode().strip()==now
        c.close(); log("[v] Time OK" if ok else "[x] Time FAIL"); return ok
    except Exception as e:
        log(f"[x] Time err: {e}"); return False

def start_fct_test(ip,user,ask_cb,pwd="allnewb2b^^"):
    log("[...] Start FCT")
    try:
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=10)
        chan=c.get_transport().open_session(); chan.get_pty()
        chan.exec_command("python3 /lg_rw/fct_test/test_start_dq1.py")

        while True:
            if chan.recv_ready():
                out = chan.recv(4096).decode("utf-8", errors="replace")
                for line in out.splitlines():
                    log(line)
                    if line.startswith("[Q]"):
                        text = line.replace("[Q]", "", 1).strip()
                        if "(y/n" in text.lower():          # 버튼 다이얼로그
                            ans = ask_choice(text)
                        else:                               # 자유 입력
                            ans = ask_input("FCT", text)
                        chan.send((ans or "") + "\n"); continue
            if chan.exit_status_ready(): break

        status=chan.recv_exit_status(); chan.close(); c.close()
        if status==0: log("[v] FCT done"); return True
        log(f"[x] FCT fail ({status})"); return False
    except Exception as e:
        log(f"[x] FCT err: {e}"); return False

# run_fct() ─── (변경 없음) ───────────────────────────
# Tkinter UI 구성 ── (변경 없음, 기존 코드 유지) ────
