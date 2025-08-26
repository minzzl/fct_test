minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Downloads$ journalctl -f | grep vsclient
Aug 26 11:54:02 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1464]: Process 7408 has named itself "citrix-vsclient".
^C
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Downloads$ GDK_BACKEND=x11 QT_QPA_PLATFORM=xcb /opt/*/vsclient 2>&1 | tee /tmp/vsclient.x11.log
bash: /opt/*/vsclient: No such file or directory
