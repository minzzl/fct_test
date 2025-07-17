[root@webOSNano-unofficial ~]# which ifconfig
/sbin/ifconfig


def reload_driver():  # [ADDED]
    log("[driver] Reloading WiFi driver...")
    env = os.environ.copy()
    env["PATH"] += os.pathsep + "/sbin" 
    subprocess.run ( 'ifconfig wlan0 down', shell = True)
    subprocess.run ( 'ifconfig mlan0 down', shell = True)
    subprocess.run ( 'ifconfig uap0 down', shell = True)
    subprocess.run ( 'killall hciattach', shell = True)
    subprocess.run('rmmod moal', shell=True)
    time.sleep(2)
    subprocess.run('rmmod mlan', shell=True)
    time.sleep(5)
    subprocess.run('insmod /lib/modules/iw61x/extra/mlan.ko', shell=True, env=env)
    time.sleep(5)
    subprocess.run('insmod /lib/modules/iw61x/extra/moal.ko mod_para=nxp/wifi_mod_para.conf', shell=True, env=env)
    time.sleep(15)
