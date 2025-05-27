def start_fct_test(hostIp, username, password="allnewb2b^^"):
    print("[...] Starting FCT Test")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=hostIp, username=username,
                       password=password, timeout=10)

        transport = client.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        channel.exec_command("python3 /lg_rw/fct_test/test_start_dq1.py")

        while True:
            if channel.recv_ready():
                output = channel.recv(1024).decode("utf-8")
                sys.stdout.write(output)          # 원격 출력 그대로 보여주기
                sys.stdout.flush()

                low = output.lower()              # 소문자 비교용

                if 'y/n' in low:                  # (1) y/n 응답
                    user_input = input('Enter y or n: ')
                    channel.send(user_input + '\n')

                elif 'input serial' in low:       # (2) “Input serial :” 응답  ### <--- ADDED
                    user_input = input(output.strip() + ' ')  # 원격 프롬프트 그대로 보여줌  ### <--- ADDED
                    channel.send(user_input + '\n')           ### <--- ADDED

            if channel.exit_status_ready():
                break

        exit_status = channel.recv_exit_status()
        channel.close()
        client.close()

        if exit_status == 0:
            print("[v] FCT Test Completed")
            return True
        else:
            print(f"[x] FCT Test failed with exit status {exit_status}")
            return False

    except Exception as e:
        print(f"Err: {e}")
        return False
