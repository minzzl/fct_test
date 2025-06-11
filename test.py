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

# ────────── 실행 위치(스크립트 vs 패키징 exe) ──────────
if getattr(sys, 'frozen', False):                   # PyInstaller onefile/onedir
    BASE_DIR = pathlib.Path(sys.executable).parent
else:                                               # python lg_fct_gui.py
    BASE_DIR = pathlib.Path(__file__).resolve().parent

# ────────── LG 컬러 팔레트 ─────────────────────────────
LG_RED      = "#A50034"
LG_GRAY_BG  = "#F2F2F2"
LG_DARKTEXT = "#333333"

# ────────── GUI-↔스레드 통신용 큐 & 헬퍼 ──────────────
log_q: queue.Queue[str] = queue.Queue()
abort_event = threading.Event()            # ★ 추가: 강제 종료 플래그
def log(msg: str): log_q.put(msg)

def ask_input(title: str, prompt: str) -> str:
    holder = queue.Queue()
    def _ask():
        res = simpledialog.askstring(title, prompt, parent=root)
        holder.put("" if res is None else res)
    root.after(0, _ask)
    return holder.get()

# ────────── (y/n(/r)) 버튼 다이얼로그 ────────────────
def ask_choice(prompt: str) -> str:
    """(y/n) 또는 (y/n/r) 프롬프트를 버튼으로 처리, 반환 'y'|'n'|'r'."""
    result = tk.StringVar()

    def _ask():
        win = tk.Toplevel(root); win.title("FCT")
        ttk.Label(win, text=prompt, wraplength=320).pack(padx=25, pady=18)
        frm = ttk.Frame(win); frm.pack(pady=(0,18))
        def done(val): result.set(val); win.destroy()
        ttk.Button(frm, text="확인", width=9, command=lambda: done('y')).pack(side="left", padx=6)
        ttk.Button(frm, text="취소", width=9, command=lambda: done('n')).pack(side="left", padx=6)
        if ' r' in prompt.lower():
            ttk.Button(frm, text="다시", width=9, command=lambda: done('r')).pack(side="left", padx=6)

        win.update_idletasks()          # ★ 빈창 방지
        win.wait_visibility(win)        # ★
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", lambda: done('n'))
    root.after(0, _ask)
    root.wait_variable(result)
    return result.get()

# ────────── FCT 로직에 쓰이는 전역 상수 ───────────────
EXCEL_FILE   = BASE_DIR / "local_file.xlsx"
CFG_TEMPLATE = BASE_DIR / "new_cfg.yml"
current_row_index = 0

# ────────── 유틸 함수들 (원본과 동일) ────────────────
def remove_known_host(path, ip):
    if os.path.exists(path):
        with open(path) as f:
            if any(ip in l for l in f):
                subprocess.run(f"ssh-keygen -R {ip}", shell=True)
    return True

# (find_next_row_index, read_sn_mac_from_file, update_check_column,
#  check_ssh_connection, execute_cmd, write_sn_mac_to_board,
#  write_cfg_to_board, write_pc_launcher_to_board, send_time_now
#  내용은 원본 그대로 – 생략)

# ────────── 테스트 루프 (abort 체크) ───────────────────
def start_fct_test(ip, user, ask_cb, pwd="allnewb2b^^"):
    log("[...] Start FCT")
    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=10)
        chan = c.get_transport().open_session(); chan.get_pty()
        chan.exec_command("python3 /lg_rw/fct_test/test_start_dq1.py")

        while not abort_event.is_set():
            if chan.recv_ready():
                out = chan.recv(4096).decode("utf-8", errors="replace")
                for line in out.splitlines():
                    log(line)
                    if line.startswith("[Q]"):
                        txt = line.replace("[Q]", "", 1).strip()
                        ans = ask_choice(txt) if "(y/n" in txt.lower() else ask_input("FCT", txt)
                        chan.send((ans or "") + "\n")
            if chan.exit_status_ready(): break

        status = chan.recv_exit_status(); chan.close(); c.close()
        return status == 0
    except Exception as e:
        log(f"[x] FCT err: {e}"); return False

# ────────── FCT 핵심 흐름 (abort 체크) ────────────────
def run_fct(host_ip: str, spec_mode: bool):
    username = "root"
    try:
        # 초기 Excel/SSH 준비 (중간 코드 동일)
        # abort_event 체크 예시
        while not check_ssh_connection(host_ip, username):
            if abort_event.is_set(): return
            log("[*] Retry in 60s"); time.sleep(60)
        log("================ Connection OK ================")

        # … 중간 과정에도 abort_event.is_set() 체크 가능 …

        if abort_event.is_set(): return
        start_fct_test(host_ip, username, ask_input)
    finally:
        root.after(0, reset_ui)

# ────────── Tkinter GUI 설정 (원본 그대로) ─────────────
root = tk.Tk()
root.title("ACP-i FCT Tool"); root.configure(bg=LG_GRAY_BG); root.geometry("860x650")
default_font=("맑은 고딕",10) if "맑은 고딕" in tkfont.families() else None
if default_font: root.option_add("*Font", default_font)

# … Style, 헤더, 로그창 등 원본 UI 코드 그대로 …

# ────────── 버튼 이벤트 / 종료 처리 ────────────────
def on_start():
    btn_start.config(state="disabled"); set_led("#FFC107")
    pbar.place(x=270,y=85); pbar.start(12)
    threading.Thread(target=run_fct,
                     args=(entry_ip.get().strip(), var_spec.get()),
                     daemon=True).start()
btn_start.config(command=on_start)

def on_close():
    if messagebox.askokcancel("Exit","Quit FCT Tool?"):
        abort_event.set()         # ★ 루프 탈출 신호
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)

warnings.filterwarnings("ignore",category=UserWarning)
root.mainloop()
