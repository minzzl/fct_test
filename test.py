#!/usr/bin/env python3
# lg_fct_gui.py  ―  ACP-i FCT Tool (LG 테마 GUI)
import os, sys, time, queue, threading, warnings, subprocess, pathlib          # pathlib 추가
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext, simpledialog, messagebox
from datetime import datetime
import pandas as pd
import yaml
import paramiko
# ────────── 실행 위치(스크립트 vs 패키징 exe) ──────────
BASE_DIR = pathlib.Path(sys.executable).parent if getattr(sys, 'frozen', False) \
           else pathlib.Path(__file__).resolve().parent

# ────────── LG 팔레트 ────────────────────────────────
LG_RED, LG_GRAY_BG, LG_DARKTEXT = "#A50034", "#F2F2F2", "#333333"

# ────────── 전역 큐·플래그 ───────────────────────────
log_q: queue.Queue[str] = queue.Queue()
abort_event = threading.Event()          # ★ 강제 종료 플래그

def log(msg: str): log_q.put(msg)

# ────────── 기본 텍스트 입력 다이얼로그 ───────────────
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
        win = tk.Toplevel(root); win.title("FCT"); win.transient(root)
        ttk.Label(win, text=prompt, wraplength=320).pack(padx=25, pady=18)
        frm = ttk.Frame(win); frm.pack(pady=(0,18))
        def done(val): result.set(val); win.destroy()
        
        if ' r' in prompt.lower():
            ttk.Button(frm, text="성공", width=9, command=lambda: done('y')).pack(side="left", padx=6)
            ttk.Button(frm, text="실패", width=9, command=lambda: done('n')).pack(side="left", padx=6)
            ttk.Button(frm, text="다시", width=9, command=lambda: done('r')).pack(side="left", padx=6)
        else:
            ttk.Button(frm, text="확인", width=9, command=lambda: done('y')).pack(side="left", padx=6)
            ttk.Button(frm, text="취소", width=9, command=lambda: done('n')).pack(side="left", padx=6)
        win.update_idletasks()          # ★ 빈 창 방지
        win.wait_visibility(win)        # ★

        # ─── 중앙 정렬 ───
        w, h = win.winfo_width(), win.winfo_height()
        rx, ry = root.winfo_rootx(), root.winfo_rooty()
        rw, rh = root.winfo_width(), root.winfo_height()
        x = rx + (rw - w)//2
        y = ry + (rh - h)//2
        win.geometry(f"+{x}+{y}")

        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", lambda: done('n'))
    root.after(0, _ask)
    root.wait_variable(result)
    return result.get()
EXCEL_FILE   = BASE_DIR / "local_file.xlsx"   # 수정
CFG_TEMPLATE = BASE_DIR / "new_cfg.yml"       # 신규
current_row_index = 0
# ────────── 유틸 함수들 ───────────────────────────────
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
    write=(f"echo {sn} > /persist/serial_number && /usr/bin/misc-util ETH_MAC {mac} "
           "&& echo PACPIA000.AKM > /persist/model_number")
    check=("cat /persist/serial_number && /usr/bin/misc-util ETH_MAC && cat /persist/model_number")
    execute_cmd(ip,user,write,pwd); out=execute_cmd(ip,user,check,pwd)
    if not out: return False
    l=out.splitlines(); ok=(l[0].strip()==sn and l[1].strip()==mac and l[2].strip()=="PACPIA000.AKM")
    log("[v] SN/MAC OK" if ok else "[x] SN/MAC mismatch"); return ok

def write_cfg_to_board(mac,sn,ip,user,pwd="allnewb2b^^"):
    log("[...] Write cfg.yml")
    try:
        cfg=yaml.safe_load(open(CFG_TEMPLATE))
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
        for local, remote in [("index.html","index.html"),("launcher.exe","launcher.exe")]:
            with open(BASE_DIR/local,"rb") as f:
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

# ────────── 테스트 루프 (abort 체크) ───────────────────
def start_fct_test(ip,user,ask_cb,pwd="allnewb2b^^"):
    log("[...] Start FCT")
    try:
        c=paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=ip, username=user, password=pwd, timeout=10)
        chan=c.get_transport().open_session(); chan.get_pty()
        chan.exec_command("python3 /lg_rw/fct_test/test_start_dq1.py")

        while not abort_event.is_set():
            if chan.recv_ready():
                out=chan.recv(4096).decode("utf-8", errors="replace")
                for line in out.splitlines():
                    log(line)
                    if line.startswith("[Q]"):
                        txt=line.replace("[Q]","",1).strip()
                        ans=ask_choice(txt) if "(y/n" in txt.lower() else ask_input("FCT", txt)
                        chan.send((ans or "")+"\n")
            if chan.exit_status_ready(): break

        status=chan.recv_exit_status(); chan.close(); c.close()
        return status==0
    except Exception as e:
        log(f"[x] FCT err: {e}"); return False

# ────────── FCT 전체 흐름 (abort 체크) ────────────────
def run_fct(host_ip:str, spec_mode:bool):
    username="root"
    try:
        remove_known_host(os.path.expanduser("~/.ssh/known_hosts"), host_ip)
        if not spec_mode and not find_next_row_index(): return
        while not check_ssh_connection(host_ip, username):
            if abort_event.is_set(): return
            log("[*] Retry in 60s"); time.sleep(60)
        log("================ Connection OK ================")

        if not spec_mode:
            ok,sn,mac=read_sn_mac_from_file()
            if not ok or abort_event.is_set(): return
            mac_clean=mac.replace(":","")
            if not write_sn_mac_to_board(sn,mac_clean,host_ip,username): return
            if not update_check_column() or abort_event.is_set(): return
            if not write_pc_launcher_to_board(host_ip,username): return
        else:
            sn,mac_clean="DEFAULT_SN","00:00:00:00:00:00"

        if abort_event.is_set(): return
        if not write_cfg_to_board(mac_clean,sn,host_ip,username): return
        if abort_event.is_set(): return
        if not send_time_now(host_ip,username): return
        if abort_event.is_set(): return
        start_fct_test(host_ip,username,ask_input)
    finally:
        root.after(0, reset_ui)

# ────────── Tkinter GUI 설정 ─────────────────────────
root = tk.Tk()
root.title("ACP-i FCT Tool"); root.configure(bg=LG_GRAY_BG); root.geometry("860x650")
default_font=("맑은 고딕",10) if "맑은 고딕" in tkfont.families() else None
if default_font: root.option_add("*Font", default_font)

style=ttk.Style(root); style.theme_use("default")
style.configure("LG.TButton", background=LG_RED, foreground="white", relief="flat", padding=(15,8))
style.map("LG.TButton", background=[("active","#c31245"),("disabled","#D4A1AF")])
style.configure("Card.TFrame", background="white", relief="ridge", borderwidth=2)
style.configure("LG.Horizontal.TProgressbar", troughcolor=LG_GRAY_BG, bordercolor=LG_GRAY_BG,
                background=LG_RED, lightcolor=LG_RED, darkcolor=LG_RED)

# 헤더 & LED
hdr=ttk.Frame(root, style="Card.TFrame"); hdr.place(x=20,y=20,width=820,height=70)
ttk.Label(hdr, text="ACP-i FCT", foreground=LG_RED,
          font=(default_font[0],20,"bold") if default_font else ("",20,"bold")).pack(side="left", padx=20)
canvas_led=tk.Canvas(hdr,width=20,height=20,highlightthickness=0); canvas_led.pack(side="right", padx=25)
led=canvas_led.create_oval(2,2,18,18,fill="#A0A0A0",outline="")
def set_led(col): canvas_led.itemconfig(led, fill=col)

# 설정 카드
cfg=ttk.Frame(root, style="Card.TFrame"); cfg.place(x=20,y=110,width=820,height=100)
tk.Label(cfg,text="Host IP",bg="white",fg=LG_DARKTEXT).grid(row=0,column=0,padx=(20,5),pady=15,sticky="e")
entry_ip=ttk.Entry(cfg,width=18); entry_ip.insert(0,"192.168.1.101"); entry_ip.grid(row=0,column=1,pady=15,sticky="w")
var_spec=tk.BooleanVar(); chk_spec=ttk.Checkbutton(cfg,text="spec mode",variable=var_spec); chk_spec.grid(row=0,column=2,padx=40)
btn_start=ttk.Button(cfg,text="Start FCT",style="LG.TButton"); btn_start.grid(row=0,column=3,padx=(40,0))

# 프로그레스바
pbar=ttk.Progressbar(root,style="LG.Horizontal.TProgressbar",mode="indeterminate",length=300)

# 로그 카드
log_frame=ttk.Frame(root,style="Card.TFrame"); log_frame.place(x=20,y=230,width=820,height=400)
txt_log=scrolledtext.ScrolledText(log_frame,width=97,height=22,bg="white",fg=LG_DARKTEXT,
                                  font=(default_font[0],9) if default_font else None,
                                  state="disabled",bd=0,relief="flat")
txt_log.pack(padx=15,pady=15,fill="both",expand=True)

def pump_log():
    while not log_q.empty():
        line=log_q.get_nowait()
        txt_log.config(state="normal"); txt_log.insert("end", line+"\n")
        txt_log.see("end"); txt_log.config(state="disabled")
        if line.startswith("[v]"): set_led("#0BB04B")
        if line.startswith("[x]"): set_led(LG_RED)
    root.after(120, pump_log)
pump_log()

def reset_ui():
    pbar.stop(); pbar.place_forget(); btn_start.config(state="normal"); set_led("#A0A0A0")

def on_start():
    btn_start.config(state="disabled"); set_led("#FFC107")
    pbar.place(x=270,y=85); pbar.start(12)
    threading.Thread(target=run_fct,args=(entry_ip.get().strip(),var_spec.get()),daemon=True).start()
btn_start.config(command=on_start)

def on_close():
    if messagebox.askokcancel("Exit","Quit FCT Tool?"):
        abort_event.set()       # ★ 강제 종료
        root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)

warnings.filterwarnings("ignore", category=UserWarning)
root.mainloop()
