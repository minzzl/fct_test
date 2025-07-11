def board_reboot(hostIp, username, password="allnewb2b^^"):
    print(f"[...] Rebooting board {hostIp}")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username, password=password, timeout=10)
        
        # Reboot command with sudo
        print(f"[...] Executing reboot command ...")
        stdin, stdout, stderr = client.exec_command("reboot")
        
        # Read stderr for any error messages
        error_output = stderr.read().decode().strip()
        if error_output:
            print(f"[x] Error during reboot: {error_output}")
        
        # Wait for the command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("[v] Board rebooted successfully")
            return True
        else:
            print(f"[x] Board reboot failed with exit status {exit_status}")
            return False
    except paramiko.AuthenticationException:
        print(f"[x] Authentication failed for user {username}")
    except paramiko.SSHException as ssh_ex:
        print(f"[x] SSH connection error: {ssh_ex}")
    except Exception as e:
        print(f"[x] Board reboot error: {e}")
    finally:
        client.close()  # Ensure the SSH connection is closed
        
    return False

이렇게 코드를 짜면 다음과 같이 오류가 나고, 재부팅이 되지 않아..
나는 root 계정으로 로그인을 했는데도 말이지 ..

...] Executing reboot command ...
[x] Error during reboot: sh: reboot: not found
[x] Board reboot failed with exit status 127
[v] Board reboot OK



C:\Users\USER>ssh root@192.168.1.101
The authenticity of host '192.168.1.101 (192.168.1.101)' can't be established.
RSA key fingerprint is SHA256:1jyoWJD1Zt31OWhZpd7jK83naA87fDDsRDxMqC5T+Ls.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.1.101' (RSA) to the list of known hosts.
root@192.168.1.101's password:
[root@webOSNano-unofficial ~]# reboot
Connection to 192.168.1.101 closed by remote host.
Connection to 192.168.1.101 closed.
