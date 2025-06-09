# ────────── 변경된 질문 처리 포함 ─────────────────────
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
                        txt = line.replace("[Q]", "", 1).strip()
                        if "(y/n" in txt.lower():
                            ans = ask_choice(txt)
                        else:
                            ans = ask_input("FCT", txt)
                        chan.send((ans or "") + "\n"); continue
            if chan.exit_status_ready(): break

        status=chan.recv_exit_status(); chan.close(); c.close()
        if status==0: log("[v] FCT done"); return True
        log(f"[x] FCT fail ({status})"); return False
    except Exception as e:
        log(f"[x] FCT err: {e}"); return False

# ────────── FCT 핵심 흐름 / GUI 구성 (원본
