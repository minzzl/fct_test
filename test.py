# ────────── (y/n(/r)) 버튼 다이얼로그 ────────────────
def ask_choice(prompt: str) -> str:
    """(y/n) 또는 (y/n/r) 프롬프트를 버튼으로 처리, 반환 'y'|'n'|'r'."""
    result = tk.StringVar()
    def _ask():
        win = tk.Toplevel(root); win.title("FCT")
        win.geometry("+{}+{}".format(root.winfo_rootx()+250, root.winfo_rooty()+200))
        win.resizable(False, False); win.attributes("-topmost", True)
        ttk.Label(win, text=prompt, wraplength=320).pack(padx=25, pady=18)
        frm = ttk.Frame(win); frm.pack(pady=(0,18))
        def done(val): result.set(val); win.destroy()
        ttk.Button(frm, text="확인",  width=9, command=lambda: done('y')).pack(side="left", padx=6)
        ttk.Button(frm, text="취소",  width=9, command=lambda: done('n')).pack(side="left", padx=6)
        if ' r' in prompt.lower():
            ttk.Button(frm, text="다시", width=9, command=lambda: done('r')).pack(side="left", padx=6)
        win.grab_set(); win.protocol("WM_DELETE_WINDOW", lambda: done('n'))
    root.after(0, _ask)
    root.wait_variable(result)
    return result.get()
