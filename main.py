import cv2 as cv  # kvuli kameře - obraz
import serial  # kvuli posilani prikazu
import numpy as np  # kvuli praci s arrays
import time  # kvuli delay a pojmenovani souboru
import matplotlib.pyplot as plt  # kvuli vykreslovani grafu a obrazku
from matplotlib.animation import FuncAnimation  # funkce obstarávající zobrazení a záznam

# -----------------
# DEFINICE FUNKCÍ
# ------------------


def send_cmd(prikaz):
    # převod hex stringu na byt
    prikaz_hex = bytes.fromhex(prikaz)
    ser.write(prikaz_hex)
    # tady by to chtělo zase zavřít port
    # return žádnej nepotřebuju I guess


def kamera_raw_nastaveni(kamera):
    kamera.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('Y', '1', '6', ''))
    kamera.set(cv.CAP_PROP_CONVERT_RGB, 0.0)  # opencv to nepřevádí na RGB -> 540, 512, 2


def uprava_snimku(frame):
    # Udela z (512, 640, 2) udela (512, 1280) - nejsou to dva obrzaky vedle sebe, ale na střídačku sloupce
    frame = frame.reshape(rows, cols * 2)
    frame = frame.astype(np.uint16)  # Convert uint8 elements to uint16 elements
    # každej sudej sloupec to znásobí 256 a pak k tomu přičte každej lichej sloupec - výsledek je (512, 640)
    frame = (frame[:, 0::2] << 8) + frame[:, 1::2]
    # frame = frame.view(np.int16)  # The data is actually signed 16 bits - view it as int16 (16 bits singed).
    return frame


def vytvor_filename(zacatek, konec, n):
    fps = str(n / (konec - zacatek))
    filename = time.strftime("%H%M%S") + 'FPS' + fps[0:2] + '_' + fps[3:6] + '.npy'
    return filename, fps


# KONSTANTY
device_index = 2  # /dev/videoX
cols, rows = 640, 512  # velikost snimku
set_fps = 10  # nastavena fps pro zaznam
cas_ms = int((1 / set_fps) * 1000)  # cas v milisekundach pro FuncAnimate

# navázání seriové komunikace na daném portu
ser = serial.Serial('/dev/ttyUSB0')
ser.baudrate = 115200

# TODO: najít tady nějaký možnosti aby se to vzpamatovalo lépe ... furt to nefunguje
time.sleep(2)  # dvě sekundy aby se všechno vzpamatovalo - hlavně serial

# OVLADANI KAMERY po serial portu
# vyslání příkazu na NUC shutter
send_cmd('AA 05 01 01 01 00 B2 EB AA')  # auto NUC off
send_cmd('AA 05 01 11 02 01 C4 EB AA')

# další příkazy - auto NU            C off, BT NUC data
send_cmd('AA 06 01 5D 02 02 00 12 EB AA')  # LVCMOS
send_cmd('AA 05 01 5C 01 01 0E EB AA')  # NUC data
send_cmd('AA 05 01 01 01 00 B2 EB AA')  # auto NUC off
# send_cmd('AA 05 01 4C 01 02 FF EB AA') #horizontal flip

# -----------------
# LIVE VIEW
# ------------------
# otevření opencv streamu pomocí V4L2 (jine moznosti jsou treba DIVX apod.)
iray = cv.VideoCapture(device_index, cv.CAP_V4L2)

# nastavení správného raw formátu
kamera_raw_nastaveni(iray)

# NASTAVEVNI ZOBRAZENI
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# zobrazeni cam view
img_obj = ax1.imshow(np.zeros((512, 640), dtype=np.uint8))
img_obj.set_clim(0, 255)
ax1.set_title('Live Camera Feed')

# zobrazeni doplnkovych dat
plot_obj, = ax2.plot([], [], lw=2)
ax2.set_xlim(0, 640)
ax2.set_ylim(0, 255)
ax2.set_title('Pixel Intensity Plot')

data, casy, data_bod, i = [], [], [], 0


# Define the animation function
# TODO: udělat opravdovou live_view funkci a tohle předělat na tu správnou záznamovou
def live_view(index):
    # data z kamery - (512,640,2) má frame
    ret, frame = iray.read()
    # záznam dat a timestampů
    data.append(frame)
    casy.append(time.time())
    # TODO: potřebuju si ty časy nějak ukládat

    # update obrazku pro prvni subplot
    img_obj.set_data(frame[:, :, 0])

    # TODO: tady je potřeba přijít na to proč mám ten shape mismatch
    data_bod.append(frame[256, 320, 0])
    plot_obj.set_data(np.arange(index), data_bod)

    return img_obj, plot_obj


timer_pro_fps_start = time.time()  # timestamp pro fps

# funkce, ktera se stara o animaci a dostava data z funkce live_view, kterou si to samo spousti
ani = FuncAnimation(fig, live_view, frames=2000, interval=cas_ms, blit=True)
plt.show(block=True)  # zobrazeni dat z iniciovanych subplotu a z funkce ani, block=true je kvuli ukonceni pomoci "q"

timer_pro_fps_konec = time.time()  # timestamp pro fps

# Release the camera
iray.release()

# data dostavam z funkce jako list of 3D arrays (512,640,2) a dělám z toho (N, 512,640,2)
data = np.stack(data, axis=0)
print(data.shape)

real_fps = data.shape[0] / (timer_pro_fps_konec - timer_pro_fps_start)  # vypocet realnyho fps
print(real_fps)

# vyslání příkazu na NUC shutter
send_cmd('AA 05 01 11 02 01 C4 EB AA')

time.sleep(2)  # dvě sekundy prodleva aby shutter nezasáhnul do záznamu

send_cmd('AA 05 01 82 02 00 34 EB AA')  # factory reset
