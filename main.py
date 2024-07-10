import csv  # kvuli ukladaní timestamp
import os  # kvuli vytvoření folderu
import cv2 as cv  # kvuli kameře - obraz
import serial  # kvůli posílání hex commandů do kamery
import numpy as np  # kvuli praci s arrays
import time  # kvuli delay a pojmenovani souboru
import matplotlib.pyplot as plt  # kvuli vykreslovani grafu a obrazku
from matplotlib.animation import FuncAnimation  # funkce obstarávající zobrazení a záznam
from commands import iray_commands as i_c  # dictionary s hex příkazama
# další dependency zde je PyQt6 - pip install pyqt6 (pro linux)

# -----------------
# DEFINICE FUNKCÍ
# ------------------


def send_cmd(prikaz):
    # převod hex stringu na byt
    prikaz = i_c[prikaz]
    prikaz_hex = bytes.fromhex(prikaz)
    ser.write(prikaz_hex)
    # tady by to chtělo zase zavřít port
    # return žádnej nepotřebuju I guess


def kamera_raw_nastaveni(kamera):
    kamera.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('Y', '1', '6', ''))
    kamera.set(cv.CAP_PROP_CONVERT_RGB, 0.0)  # opencv to nepřevádí na RGB -> 540, 512, 2


def vytvor_thumbnail(kamera):
    kamera_jede, obrazek = kamera.read()
    return obrazek

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
    filename = f'{time.strftime("%H%M%S")}FPS{fps[0:2]}_{fps[3:6]}'
    return filename, fps


# KONSTANTY
device_index = 2  # /dev/videoX
cols, rows = 640, 512  # velikost snimku
set_fps = 15  # nastavena fps pro zaznam
x_watch = 320 # souradnice bodu, kde sleduju hodnotu
y_watch = 256

# definice seriového portu
ser = serial.Serial('/dev/ttyUSB0')
ser.baudrate = 115200

# TODO: najít tady nějaký možnosti aby se to vzpamatovalo lépe ... furt to nefunguje
time.sleep(2)  # dvě sekundy aby se všechno vzpamatovalo - hlavně serial

# OVLADANI KAMERY po serial portu
send_cmd('Auto NUC on')
send_cmd('NUC - Shutter')
send_cmd('DVI - BT.1120')
send_cmd('PLT - Lava')
# send_cmd('IF - horizontal') #horizontal flip

# otevření opencv streamu pomocí V4L2 (jine moznosti jsou treba DIVX apod.)
iray = cv.VideoCapture(device_index, cv.CAP_V4L2)

# -----------------
# LIVE VIEW
# ------------------
# nastavení okna pro live-view
cv.namedWindow('live-view', cv.WINDOW_NORMAL)
cv.resizeWindow('live-view', 1000, 800)

# loop zobrazující liveview
while True:
    # Capture frame-by-frame
    ret, frame = iray.read()
    if not ret:  # ret je return boolean, True když v pohodě vysílá
        break

    # Display the resulting frame
    resized_frame = cv.resize(frame, (int(640*1.5),int(512*1.5)))
    cv.imshow('live-view', frame)
    key = cv.waitKey(1)
    if key == ord('q'):  # exit on q ... if key == 27 je pro ESC
        break

cv.destroyAllWindows()

# pozaostření a před měřením (tam už mám nastavenou úpravu RAW formátu na Y16)
thumbnail = vytvor_thumbnail(iray)

# -------------------
# ZAZNAM
# ----------------------
# nastavení správného raw formátu
kamera_raw_nastaveni(iray)

# vypocet intervalu pro FuncAnimation
# je upraven konstantou abych dostal cca FPS, co potřebuju
cas_ms = int((1 / ((26/16)*set_fps)) * 1000)

# NASTAVEVNI ZOBRAZENI
fig_rec, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Axes pro zobrazeni cam view
img_obj = ax1.imshow(np.zeros((512, 640), dtype=np.uint8))
img_obj.set_clim(0, 255)
ax1.set_title('Meření')

# Axes pro zobrazeni vybraneho bodu v čase
plot_obj, = ax2.plot([], [], lw=1)
ax2.set_xlim(0, 2000)
ax2.set_ylim(0, 255)
ax2.set_title(f'Data v bodě ({x_watch},{y_watch})')

data, casy, data_bod = [], [], []


def zaznam(index):
    # data z kamery - (512,640,2) má frame
    ret, frame = iray.read()
    # záznam dat a timestampů
    data.append(frame)
    casy.append(time.time())
    # TODO: potřebuju si ty časy nějak ukládat

    # update obrazku pro prvni subplot
    img_obj.set_data(frame[:, :, 0])

    # update dat pro line chart
    data_bod.append(frame[y_watch, x_watch, 0])
    plot_obj.set_data(np.arange(index+2), data_bod)
    # index + něco je tady kvůli tomu, že data_bod mají v první iteraci už nějakou velikost z nějakýho důvodu

    return img_obj, plot_obj


# Shutter před náběrem
send_cmd('DVI - LVCMOS')
send_cmd('DVS - NUC')
send_cmd('NUC - Shutter')
time.sleep(2)  # dvě sekundy prodleva aby shutter nezasáhnul do záznamu

timer_pro_fps_start = time.time()  # timestamp pro fps
# funkce, ktera se stara o animaci a dostava data z funkce live_view, kterou si to samo spousti
ani = FuncAnimation(fig_rec, zaznam, frames=2000, interval=cas_ms, blit=False)
plt.show(block=True)  # zobrazeni dat z iniciovanych subplotu a z funkce ani, block=true je kvuli ukonceni pomoci "q"
timer_pro_fps_konec = time.time()  # timestamp pro fps
iray.release()  # Release the camera
plt.close(fig_rec)

# ------------------------
# ZPRACOVÁNÍ A UKLÁDÁNÍ DAT
# --------------------------
# data dostavam z funkce jako list of 3D arrays (512,640,2) a dělám z toho (N, 512,640,2)
data = np.stack(data, axis=0)
print(data.shape)

folder_name, real_fps = vytvor_filename(timer_pro_fps_start, timer_pro_fps_konec, data.shape[0])
os.makedirs(folder_name, exist_ok=True)

# uložení dat
np.save(file=f'{folder_name}/data.npy', arr=data)
print(f'Byl vytvořen folder s názvem {folder_name[:-1]}. Data mají {data.shape[0]} snímků a {real_fps[0:6]} FPS.')

# uložení timestampu
with open(f'{folder_name}/timestamps.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(casy)

# uložení thumbnailu
cv.imwrite(f"{folder_name}/thumb.png", thumbnail)

# vyslání příkazu na NUC shutter
send_cmd('NUC - Shutter')

time.sleep(2)  # dvě sekundy prodleva aby shutter nezasáhnul do záznamu
send_cmd('Factory defaults')
