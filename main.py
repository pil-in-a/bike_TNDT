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
from scipy.io import savemat  # pro ukládání matláku
# další dependency zde je PyQt6 - pip install pyqt6 (pro linux)

# -----------------
# DEFINICE FUNKCÍ A CLASSŮ
# ------------------


class CustomMainWindow(QMainWindow):
    # třída, pomocí které si zavádim okno, které se dá zavřít pomocí Q
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q:  # corrected to `Qt.Key.Key_Q`
            self.close()  # Close the window


class Camera:
    # třída Camera, při iniciaci provedfe cv.Videocapture()
    # obsahuje už nějaký funkce, který se s ní prováděj
    def __init__(self, ser, device_index):
        self.ser = ser
        self.device = cv.VideoCapture(device_index, cv.CAP_V4L2)

    def send_command(self, command):
        ser.write(bytes.fromhex(i_c[command]))

    def read_frame(self):
        return self.device.read()

    def setup_raw_mode(self):
        self.device.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('Y', '1', '6', ''))
        self.device.set(cv.CAP_PROP_CONVERT_RGB, 0)

    def release_camera(self):
        self.device.release()


def create_thumbnail(device):
    _, image = device.read_frame()
    return image


def create_filename(start, stop, n):
    fps = str(n / (stop - start))
    filename = f'{time.strftime("%H%M%S")}FPS{fps[0:2]}_{fps[3:6]}'
    return filename, fps


def pre_measure_view(device, resize_factor=1.9):
    cv.namedWindow('live-view', cv.WINDOW_NORMAL)
    cv.resizeWindow('live-view', 1200, 1000)

    while True:
        pohoda, frame_live = device.read_frame()
        if not pohoda:
            break

        frame_live = cv.resize(frame_live, (int(640 * resize_factor), int(512 * resize_factor)))
        cv.imshow('live-view', frame_live)
        key = cv.waitKey(1)

        if key == ord('q'):
            break

    cv.destroyAllWindows()


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

camera = Camera(ser, device_index)

# OVLADANI KAMERY po serial portu
# kdoví proč to tu zároven i cvakne :D
camera.send_command('DVI - BT.1120')
camera.send_command('PLT - Lava')
camera.send_command('IF - horizontal')

# -----------------
# LIVE VIEW
# ------------------

pre_measure_view(camera, resize_factor=1.9)

# po zaostření a před záznamem (tam už mám nastavenou úpravu RAW formátu na Y16)
thumbnail = create_thumbnail(camera)

# -------------------
# ZAZNAM
# ----------------------
# nastavení správného raw formátu
camera.setup_raw_mode()

# vypocet intervalu pro QtTimer
cas_ms = 1000 // set_fps  # 1000 ms děleno (// pro integer) fpskama

# Nastavení zobrazovacího okna pyqtgraph a QtMainWindow
# mainwindow je instance CustomMainWindow, která se dá zavřít klávesou
app = pg.mkQApp("Záznam")
win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples", size=(1200, 1000))
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
    success, frame = camera.read_frame()  # shape je (512, 640, 2) - 8bit obrázek a 8bit registr

    frame = frame.astype('int16')  # vic mista
    frame = frame[:, :, 0] + (frame[:, :, 1] << 8)  # prvni frame + druhej * 256

    # data do grafu
    data_bod.append(frame[y_watch, x_watch])
    graf.setData(data_bod)

    # update obrazku do okna
    img.setImage(frame)

    # ukladani dat
    data.append(frame)
    casy.append(time.time())


# Shutter před náběrem
camera.send_command('DVI - LVCMOS')
camera.send_command('DVS - NUC')
camera.send_command('Auto NUC off')
camera.send_command('NUC - Shutter')
time.sleep(2)  # dvě sekundy prodleva aby shutter nezasáhnul do záznamu

# spouštění funkce update
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(cas_ms)

# spuštění celýho Qt molochu
app.exec()

camera.release_camera()  # Release the camera
# ------------------------
# ZPRACOVÁNÍ A UKLÁDÁNÍ DAT
# --------------------------
print('Probíhá ukládání dat')
# data dostavam z funkce jako list of 3D arrays (512,640) a dělám z toho (N, 512,640) int16
data = np.stack(data, axis=0, dtype='int16')

folder_name, real_fps = create_filename(casy[0], casy[-1], data.shape[0])
# vytvoření folderu s názvem čas měření, FPS
makedirs(folder_name, exist_ok=True)

# uložení dat
np.save(file=f'{folder_name}/data.npy', arr=data)
print(f'Byl vytvořen folder s názvem {folder_name}. Data mají {data.shape[0]} snímků a {real_fps[0:6]} FPS.')

# uložení timestampu
with open(f'{folder_name}/timestamps.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(casy)

# uložení thumbnailu
cv.imwrite(f"{folder_name}/thumb.png", thumbnail)

# uložení matlabu
savemat(f'{folder_name}/{folder_name}.mat', {f'{folder_name}': data})

# vyslání příkazu na NUC shutter
camera.send_command('NUC - Shutter')
camera.send_command('Factory defaults')
