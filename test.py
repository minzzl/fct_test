minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ journalctl -f | grep vsclient
Aug 26 11:28:39 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 7580 has named itself "citrix-vsclient".
Aug 26 11:34:48 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 7996 has named itself "citrix-vsclient".
Aug 26 11:35:55 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 8283 has named itself "citrix-vsclient".
Aug 26 11:39:24 minzzl-HP-Z6-G5-Workstation-Desktop-PC sudo[8564]:   minzzl : TTY=pts/1 ; PWD=/home/minzzl/Downloads ; USER=root ; COMMAND=/usr/bin/dpkg -i vsclient-linux.deb
Aug 26 11:39:37 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 8868 has named itself "citrix-vsclient".
Aug 26 11:40:05 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 8884 has named itself "citrix-vsclient".
Aug 26 11:40:13 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 8892 has named itself "citrix-vsclient".
Aug 26 11:40:13 minzzl-HP-Z6-G5-Workstation-Desktop-PC systemd[2609]: Started app-gnome-vsclient-8892.scope - Application launched by gnome-shell.
Aug 26 11:40:20 minzzl-HP-Z6-G5-Workstation-Desktop-PC citrix-ctxcwalogd[1480]: Process 9173 has named itself "citrix-vsclient".

minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~/Downloads$ sudo dpkg -i vsclient-linux.deb
[sudo] password for minzzl: 
(Reading database ... 301320 files and directories currently installed.)
Preparing to unpack vsclient-linux.deb ...
Unpacking vsclient-linux (1.4.131.27756) over (1.4.131.27756) ...
Setting up vsclient-linux (1.4.131.27756) ...
Processing triggers for gnome-menus (3.36.0-1.1ubuntu3) ...
Processing triggers for desktop-file-utils (0.27-2build1) ...

                   이렇게 다운도 잘 받았는데 왜 안되지
