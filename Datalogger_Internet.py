import network
import socket
import urequests
import time
import machine

SSID = "monSSID"
PASSWORD = "monPWD"

# LED interne du Pico W
led = machine.Pin("LED", machine.Pin.OUT)

# Connexion WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connexion au WiFi...")
    while not wlan.isconnected():
        time.sleep(1)

    print("Connecté :", wlan.ifconfig())
    return wlan

# Synchronisation NTP
def sync_time():
    ntp_host = "pool.ntp.org"

    try:
        print("Synchronisation NTP...")
        addr = socket.getaddrinfo(ntp_host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)

        msg = b'\x1b' + 47 * b'\0'
        s.sendto(msg, addr)
        msg = s.recv(48)
        s.close()

        ntp_time = int.from_bytes(msg[40:44], 'big') - 2208988800
        tm = time.localtime(ntp_time)

        machine.RTC().datetime((
            tm[0], tm[1], tm[2], 0, tm[3], tm[4], tm[5], 0
        ))

        print("Heure synchronisée :", time.localtime())
        return True

    except Exception as e:
        print("Erreur NTP :", e)
        return False

# Vérification Internet
def check_internet():
    try:
        r = urequests.get("https://1.1.1.1")
        r.close()
        return True
    except:
        return False

# LED clignotement si FAIL
def blink_error():
    for _ in range(30):  # clignote 30 fois
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)

# Log dans fichier .txt
def log_status(status):
    timestamp = time.localtime()
    date_str = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        timestamp[0], timestamp[1], timestamp[2],
        timestamp[3], timestamp[4], timestamp[5]
    )

    with open("internet_log.txt", "a") as f:
        f.write(f"{date_str} - {'OK' if status else 'FAIL'}\n")

# Programme principal
def main():
    connect_wifi()
    sync_time()

    while True:
        status = check_internet()
        log_status(status)

        if status:
            print("Internet : OK")
            led.off()
        else:
            print("Internet : FAIL")
            blink_error()

        time.sleep(60)

main()