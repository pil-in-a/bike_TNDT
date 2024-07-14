import csv  # kvuli ukladaní timestamp
from os import makedirs  # kvuli vytvoření folderu
import cv2 as cv  # kvuli kameře - obraz
import serial  # kvůli posílání hex commandů do kamery
import numpy as np  # kvuli praci s arrays
import time  # kvuli delay a pojmenovani souboru
import pyqtgraph as pg  # Nejrůznější Qt a pyqtgraph stuff pro zobrazování dat
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow
from commands import iray_commands as i_c  # dictionary s hex příkazama
# další dependency zde je PyQt6 - pip install pyqt6 (pro linux)

# -----------------
# DEFINICE FUNKCÍ A CLASSŮ
# ------------------


class CustomMainWindow(QMainWindow):
    # třída, pomocí které si zavádim okno, které se dá zavřít pomocí Q
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q:  # corrected to `Qt.Key.Key_Q`
            self.close()  # Close the window


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


def vytvor_filename(zacatek, konec, n):
    fps = str(n / (konec - zacatek))
    filename = f'{time.strftime("%H%M%S")}FPS{fps[0:2]}_{fps[3:6]}'
    return filename, fps


# KONSTANTY
device_index = 2  # /dev/videoX
port = 0  # /dev/ttyUSBX
cols, rows = 640, 512  # velikost snimku
set_fps = 25  # nastavena fps pro zaznam
x_watch = 320  # souradnice bodu, kde sleduju hodnotu
y_watch = 256

# definice seriového portu
ser = serial.Serial(f'/dev/ttyUSB{port}')
ser.baudrate = 115200

time.sleep(2)  # dvě sekundy aby se všechno vzpamatovalo - hlavně serial

# OVLADANI KAMERY po serial portu
send_cmd('Auto NUC off')
send_cmd('NUC - Shutter')
send_cmd('DVI - BT.1120')
send_cmd('PLT - Iron')
send_cmd('IF - horizontal')
# TODO: tady to cvaká 2x ... tak se podívat, co to dělá

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
    pohoda, frame_live = iray.read()
    if not pohoda:  # ret je return boolean, True když v pohodě vysílá
        break

    # Display the resulting frame
    resized_obrazek = cv.resize(frame_live, (int(640*1.5), int(512*1.5)))
    cv.imshow('live-view', resized_obrazek)
    key = cv.waitKey(1)
    if key == ord('q'):  # exit on q ... if key == 27 je pro ESC
        break

cv.destroyAllWindows()

# po zaostření a před záznamem (tam už mám nastavenou úpravu RAW formátu na Y16)
thumbnail = vytvor_thumbnail(iray)

# -------------------
# ZAZNAM
# ----------------------
# nastavení správného raw formátu
kamera_raw_nastaveni(iray)

# vypocet intervalu pro QtTimer
cas_ms = 1000 // set_fps  # 1000 ms děleno (// pro integer) fpskama

# Nastavení zobrazovacího okna pyqtgraph a QtMainWindow
# mainwindow je instance CustomMainWindow, která se dá zavřít klávesou
app = pg.mkQApp("Záznam")
win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples", size=(800, 1000))
mainwindow = CustomMainWindow()
mainwindow.setCentralWidget(win)
mainwindow.show()

pg.setConfigOptions(antialias=True)

# Viewbox ve win widgetu pro zobrazení obrázku (ImageItem)
p1 = win.addViewBox()
p1.setAspectLocked()  # zanechává pixely čtvercové
p1.invertY()  # obrátí obrázek vzhůru nohma -> správně

# conatiner pro obrázek
img = pg.ImageItem(axisOrder='row-major')  # axis order dává obrázek správně
img.setColorMap('magma')
p1.addItem(img)

# Watch bod crosshair 40px
# Vertical Line
x_line = pg.PlotDataItem([x_watch, x_watch], [y_watch - 20, y_watch + 20], pen='g')
p1.addItem(x_line)

# Horizontal Line
y_line = pg.PlotDataItem([x_watch - 20, x_watch + 20], [y_watch, y_watch], pen='g')
p1.addItem(y_line)

win.nextRow()

p2 = win.addPlot(title=f'Hodnoty v bodě ({x_watch}, {y_watch}')
graf = p2.plot(pen='r')

# iniciace dat pro záznam
data, casy, data_bod = [], [], []


def update():
    # funkce updatující data pro zobrazení a záznam
    ret, frame = iray.read()
    data.append(frame)
    casy.append(time.time())
    # data v grafu chci zobrazit jako 16bit aby se "nepřetejkali"
    data_do_grafu = frame[y_watch, x_watch, :].astype('int16')
    data_do_grafu = int(data_do_grafu[0] + (data_do_grafu[1] << 8))
    data_bod.append(data_do_grafu)
    graf.setData(data_bod)

    img.setImage(frame[:, :, 0])


# Shutter před náběrem
send_cmd('DVI - LVCMOS')
send_cmd('DVS - NUC')
send_cmd('NUC - Shutter')
send_cmd('Auto NUC off')
time.sleep(2)  # dvě sekundy prodleva aby shutter nezasáhnul do záznamu

# spouštění funkce update
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(cas_ms)

# spuštění celýho Qt molochu
app.exec()

iray.release()  # Release the camera
# ------------------------
# ZPRACOVÁNÍ A UKLÁDÁNÍ DAT
# --------------------------
print('Probíhá ukládání dat')
# data dostavam z funkce jako list of 3D arrays (512,640,2) a dělám z toho (N, 512,640,2) int16
data = np.stack(data, axis=0, dtype='int16')
# stacking - druhej * 256 + prvni
data = data[:, :, :, 0] + (data[:, :, :, 1] << 8)

folder_name, real_fps = vytvor_filename(casy[0], casy[-1], data.shape[0])
# vytvoření folderu s názvem čas měření, FPS
makedirs(folder_name, exist_ok=True)

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
