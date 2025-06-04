#!/usr/bin/env python3
# lg_fct_gui.py  ―  ACP-i FCT Tool (LG 테마 GUI)

import os, sys, time, queue, threading, warnings, subprocess, argparse
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext, simpledialog, messagebox
from datetime import datetime
import pandas as pd
import yaml
import paramiko

# ────────── LG 컬러 팔레트 ─────────────────────────────────────
LG_RED, LG_GRAY_BG, LG_DARKTEXT = "#A50034", "#F2F2F2", "#333333"

# ────────── CLI 옵션 파싱 ─────────────────────────────────────
parser = argparse.ArgumentParser(description="ACP-i FCT Tool")
parser.add_argument("--spec", "-s", action="store_true",
                    help="spec mode: skip Excel and use default SN/MAC")
args = parser.parse_args()

# ────────── GUI-↔스레드 통신용 큐 & 헬퍼 ──────────────────────
log_q: queue.Queue[str] = queue.Queue()
def log(msg: str):
    """백그라운드 스레드 → GUI 로그창"""
    log_q.put(msg)

def ask_input(title: str, prompt: str) -> str:
    """백그라운드 스레드에서도 안전한 모달 입력창"""
    result = tk.StringVar()

    def _ask():
        res = simpledialog.askstring(title, prompt, parent=root)
        result.set("" if res is None else res)

    root.after(0, _ask)        # 메인 스레드에서 다이얼로그 호출
    root.wait_variable(result) # 입력 완료까지 대기
    return result.get()

# ────────── FCT 로직에 쓰이는 전역 상수 ───────────────────────
EXCEL_FILE = "local_file.xlsx"
current_row_index = 0

# ────────── 유틸 함수들 ────────────────────────────────────────
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
                current_row_index = idx
                return True
        log("[x] No available rows")
        return False
    except Exception as e:
        log(f"[x] Excel error: {e}")
        return False

def read_sn_mac_from_file():
    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty or current_row_index >= len(df):
            log("[x] Excel empty")
            return False, None, None
        sn  = str(df.at[current_row_index, "Serial Number"]).strip()
        mac = str(df.at[current_row_index, "Eth Address"]).strip()
        return True, sn, mac
    except Exception as e:
        log(f"[x] Excel read err: {e}")
        return False, None, None

def update_check_column():
    try:
        df = pd.read_excel(EXCEL_FILE, dtype={"Check": str})
        df.at[current_row_index, "Check"] = "O"
        df.to_excel(EXCEL_FILE, index=False)
        log("[v] Excel Check OK")
        return True
    except Exception as e:
        log(f"[x] Excel write err: {e}")
        return False

def check_ssh_connection(ip, user, pwd="allnewb2b^^"):
    log(f"[...] SSH connect {ip}")
    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=60)
        c.close()
        log("[v] SSH OK")
        return True
    except Exception:
        log("[x] SSH FAIL")
        return False

def execute_cmd(ip, user, cmd, pwd="allnewb2b^^"):
    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=10)
        _, stdout, _ = c.exec_command(cmd)
        out = stdout.read().decode().strip()
        c.close()
        return out
    except Exception as e:
        log(f"[x] SSH cmd err: {e}")
        return None

def write_sn_mac_to_board(sn, mac, ip, user, pwd="allnewb2b^^"):
    log("[...] Write SN/MAC")
    write  = (f"echo {sn} > /persist/serial_number && "
              f"/usr/bin/misc-util ETH_MAC {mac} && "
              "echo PACPIA000.AKM > /persist/model_number")
    check  = ("cat /persist/serial_number && "
              "/usr/bin/misc-util ETH_MAC && "
              "cat /persist/model_number")
    execute_cmd(ip, user, write, pwd)
    out = execute_cmd(ip, user, check, pwd)
    if not out: return False
    l = out.splitlines()
    ok = (l[0].strip() == sn and l[1].strip() == mac and l[2].strip() == "PACPIA000.AKM")
    log("[v] SN/MAC OK" if ok else "[x] SN/MAC mismatch")
    return ok

def write_cfg_to_board(mac, sn, ip, user, pwd="allnewb2b^^"):
    log("[...] Write cfg.yml")
    try:
        with open("new_cfg.yml") as f: cfg = yaml.safe_load(f)
        cfg["ETH"]["mac"], cfg["VERSION"]["serial"] = mac, sn
        with open("new_cfg.yml", "w") as f: yaml.dump(cfg, f)
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd)
        with open("new_cfg.yml", "rb") as f:
            stdin, _, _ = c.exec_command("cat > /lg_rw/fct_test/cfg.yml")
            stdin.write(f.read()); stdin.close()
        c.close(); log("[v] cfg OK"); return True
    except Exception as e:
        log(f"[x] cfg err: {e}"); return False

def write_pc_launcher_to_board(ip, user, pwd="allnewb2b^^"):
    log("[...] Write launcher files")
    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd)
        c.exec_command("mkdir -p /lg_rw/b2b-platform/http")
        for local, remote in [("index.html", "index.html"), ("launcher.exe", "launcher.exe")]:
            with open(local, "rb") as f:
                stdin, _, _ = c.exec_command(f"cat > /lg_rw/b2b-platform/http/{remote}")
                stdin.write(f.read()); stdin.close()
        c.close(); log("[v] launcher OK"); return True
    except Exception as e:
        log(f"[x] launcher err: {e}"); return False

def send_time_now(ip, user, pwd="allnewb2b^^"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"[...] Send time {now}")
    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd)
        c.exec_command(f"echo '{now}' > /home/root/current_time"); time.sleep(0.5)
        _, stdout, _ = c.exec_command("cat /home/root/current_time")
        ok = stdout.read().decode().strip() == now
        c.close(); log("[v] Time OK" if ok else "[x] Time FAIL"); return ok
    except Exception as e:
        log(f"[x] Time err: {e}"); return False

def start_fct_test(ip, user, ask_cb, pwd="allnewb2b^^"):
    log("[...] Start FCT")
    try:
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=10)
        chan = c.get_transport().open_session(); chan.get_pty()
        chan.exec_command("python3 /lg_rw/fct_test/test_start_dq1.py")

        while True:
            if chan.recv_ready():
                raw = chan.recv(4096)
                out = raw.decode("utf-8", errors="replace")

                for line in out.splitlines():
                    log(line)

                    # ── [Q] 프롬프트(한글 포함) 처리 ─────────────────
                    if line.startswith("[Q]"):
                        prompt = line[3:].lstrip()
                        ans = ask_cb("FCT", prompt)
                        chan.send((ans or "") + "\n")
                        continue

                    # ── y/n 질문 처리 ────────────────────────────────
                    if "y/n" in line.lower():
                        ans = ask_cb("FCT", line.strip())
                        chan.send((ans or "") + "\n")

            if chan.exit_status_ready():
                break

        status = chan.recv_exit_status(); chan.close(); c.close()
        if status == 0:
            log("[v] FCT done"); return True
        log(f"[x] FCT fail ({status})"); return False

    except Exception as e:
        log(f"[x] FCT err: {e}"); return False

# ────────── FCT 핵심 흐름 (백그라운드 스레드) ────────────────
def run_fct(host_ip: str, spec_mode: bool):
    username = "root"
    try:
        remove_known_host(os.path.expanduser("~/.ssh/known_hosts"), host_ip)

        if not spec_mode and not find_next_row_index():
            return

        while not check_ssh_connection(host_ip, username):
            log("[*] Retry in 60s"); time.sleep(60)
        log("================ Connection OK ================")

        if not spec_mode:
            ok, sn, mac = read_sn_mac_from_file()
            if not ok: return
            mac_clean = mac.replace(":", "")
            if not write_sn_mac_to_board(sn, mac_clean, host_ip, username): return
            if not update_check_column(): return
            if not write_pc_launcher_to_board(host_ip, username): return
        else:
            sn, mac_clean = "DEFAULT_SN", "00:00:00:00:00:00"

        if not write_cfg_to_board(mac_clean, sn, host_ip, username): return
        if not send_time_now(host_ip, username): return
        if not start_fct_test(host_ip, username, ask_input): return
        log("[v] ALL OK – replace board")

    finally:
        root.after(0, reset_ui)

# ────────── Tkinter GUI 레이아웃 ─────────────────────────────
root = tk.Tk()
root.title("ACP-i FCT Tool")
root.configure(bg=LG_GRAY_BG)
root.geometry("860x650")

default_font = ("맑은 고딕", 10) if "맑은 고딕" in tkfont.families() else None
if default_font:
    root.option_add("*Font", default_font)

style = ttk.Style(root); style.theme_use("default")
style.configure("LG.TButton", background=LG_RED, foreground="white",
                relief="flat", padding=(15, 8))
style.map("LG.TButton", background=[("active", "#c31245"), ("disabled", "#D4A1AF")])
style.configure("Card.TFrame", background="white", relief="ridge", borderwidth=2)
style.configure("LG.Horizontal.TProgressbar", troughcolor=LG_GRAY_BG,
                bordercolor=LG_GRAY_BG, background=LG_RED,
                lightcolor=LG_RED, darkcolor=LG_RED)

# 헤더
hdr = ttk.Frame(root, style="Card.TFrame"); hdr.place(x=20, y=20, width=820, height=70)
ttk.Label(hdr, text="ACP-i FCT", foreground=LG_RED,
          font=(default_font[0], 20, "bold") if default_font else ("", 20, "bold")
          ).pack(side="left", padx=20)

canvas_led = tk.Canvas(hdr, width=20, height=20, highlightthickness=0); canvas_led.pack(side="right", padx=25)
led = canvas_led.create_oval(2, 2, 18, 18, fill="#A0A0A0", outline="")
def set_led(col): canvas_led.itemconfig(led, fill=col)

# 설정 카드
cfg = ttk.Frame(root, style="Card.TFrame"); cfg.place(x=20, y=110, width=820, height=100)
tk.Label(cfg, text="Host IP", bg="white", fg=LG_DARKTEXT).grid(row=0, column=0, padx=(20, 5), pady=15, sticky="e")
entry_ip = ttk.Entry(cfg, width=18); entry_ip.insert(0, "192.168.1.101")
entry_ip.grid(row=0, column=1, pady=15, sticky="w")

var_spec = tk.BooleanVar(value=args.spec)
chk_spec = ttk.Checkbutton(cfg, text="spec mode", variable=var_spec)
chk_spec.grid(row=0, column=2, padx=40)

btn_start = ttk.Button(cfg, text="Start FCT", style="LG.TButton")
btn_start.grid(row=0, column=3, padx=(40, 0))

# 프로그레스바
pbar = ttk.Progressbar(root, style="LG.Horizontal.TProgressbar",
                       mode="indeterminate", length=300)

# 로그 카드
log_frame = ttk.Frame(root, style="Card.TFrame"); log_frame.place(x=20, y=230, width=820, height=400)
txt_log = scrolledtext.ScrolledText(log_frame, width=97, height=22, bg="white",
                                    fg=LG_DARKTEXT,
                                    font=(default_font[0], 9) if default_font else None,
                                    state="disabled", bd=0, relief="flat")
txt_log.pack(padx=15, pady=15, fill="both", expand=True)

def pump_log():
    while not log_q.empty():
        line = log_q.get_nowait()
        txt_log.config(state="normal"); txt_log.insert("end", line + "\n")
        txt_log.see("end"); txt_log.config(state="disabled")

        if line.startswith("[v]"): set_led("#0BB04B")
        if line.startswith("[x]"): set_led(LG_RED)
    root.after(120, pump_log)
pump_log()

def reset_ui():
    pbar.stop(); pbar.place_forget()
    btn_start.config(state="normal")
    set_led("#A0A0A0")

def on_start():
    btn_start.config(state="disabled")
    set_led("#FFC107")
    pbar.place(x=270, y=85); pbar.start(12)
    threading.Thread(target=run_fct,
                     args=(entry_ip.get().strip(), var_spec.get()),
                     daemon=True).start()
btn_start.config(command=on_start)

root.protocol("WM_DELETE_WINDOW",
              lambda: root.destroy() if messagebox.askokcancel("Exit", "Quit FCT Tool?") else None)

warnings.filterwarnings("ignore", category=UserWarning)
root.mainloop()



# 파티션이 마운트돼 있다면 먼저 해제
sudo umount /dev/mmcblk0p2

# /mnt/nfs/ext4g 이미지를 SD카드 2번 파티션에 기록
sudo dd if=/mnt/nfs/ext4g of=/dev/mmcblk0p2 bs=4M conv=fsync status=progress
# 1. 부트 아규먼트 갱신
setenv bootargs 'console=ttyS0,115200 root=/dev/mmcblk0p2 rootfstype=ext4 rw rootwait'

# 2. 부트 명령에서 ext2img.gz 부분 삭제
setenv bootcmd 'fatload mmc 0:1 0x80000 Image; \
                fatload mmc 0:1 0x3100000 my2837.dtb; \
                booti 0x80000 - 0x3100000'

# 3. (선택) rootfs 업데이트용 함수 새로 정의
#  p2 시작 LBA = 0x8200  (예: 532480 / 512 = 0x8200)
#  p2 블록수    = 0x2C800 (예: 363520 / 512 = 0x2C800)
setenv RFS 'tftp ${loadaddr} rootfs.ext4; mmc dev 0; mmc write ${loadaddr} 0x8200 0x2C800'

saveenv      # 변경사항 영구 저장
reset        # 재부팅해서 정상 마운트 확인
