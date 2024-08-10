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
import math
from scipy.io import savemat  # pro ukládání matláku
import platform
# další dependency zde je PyQt6 - pip install pyqt6 (pro linux)

# TODO: PySide místo PyQT6?
# TODO: komprese dat - používám uint16 pro data s rozsahem kolem 2000
# TODO: Pyqtgraph pro zobrazení preview i s crosshairem
# TODO: správné používání PyQT

# -----------------
# DEFINICE FUNKCÍ A CLASSŮ
# ------------------


class CustomMainWindow(QMainWindow):
    # třída, pomocí které si zavádim okno, které se dá zavřít pomocí Q
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q:  # corrected to `Qt.Key.Key_Q`
            self.close()  # Close the window


class Camera:
    # třída Camera, při iniciaci provede cv.Videocapture()
    # obsahuje už nějaký funkce, který se s ní prováděj
    def __init__(self, ser, device_index):
        self.ser = ser
        if platform.system() == 'Linux':
            self.device = cv.VideoCapture(device_index, cv.CAP_V4L2)  # For Linux
        else:
            self.device = cv.VideoCapture(device_index)  # For Windows

    def send_command(self, command):
        ser.write(bytes.fromhex(i_c[command]))

    def read_frame(self):
        return self.device.read()

    def setup_raw_mode(self):
        self.device.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('Y', '1', '6', ''))
        self.device.set(cv.CAP_PROP_CONVERT_RGB, 0)

    def release_camera(self):
        self.device.release()


def calculate_fft(data, fps, frequency, folder_path):
    # TODO: tahle funkce je celkově dost rozsháhlá a možná by chtěla trochu zredukovat
    rows = data.shape[1]
    cols = data.shape[2]
    frames = data.shape[0]
    fps = round(fps)
    # TODO: pokud zaokrouhluje moc, vzniká velká nepřesnost a obraz na frequency_index nebude vypovídající -> nějak
    #  vyhezkat

    # nachazim window pro fft a index pro danou freq
    print('Hledání indexu pro danou frekvenci světel')
    for fft_window in range(frames, 0, -1):  # hledá nějvětší okno -> počítá odzadu a zmenšuje
        frequency_index = (frequency * fft_window) / fps
        if fft_window <= 20:
            print('Okno je příliš malé, FFT nelze vypočítat')
            fft_window, frequency_index = None, None
            break
        if frequency_index - math.floor(frequency_index) == 0:
            frequency_index = int(frequency_index)  # nějaká ta +1 nebo tak nějak?
            print(f'Index pro frekvenci {frequency} Hz je {frequency_index}, FFT počítána v okně {fft_window}')
            break

    print('výpočet FFT')
    angle_image = np.zeros((fft_window, cols, rows), dtype='float')
    for x in range(cols):
        for y in range(rows):
            fft_data = np.fft.fft(data[:fft_window, y, x])
            angle_image[:, x, y] = np.angle(fft_data)

    angle_image = angle_image[0:20, :, :]

    np.save(f'{folder_path}uhel_{str(frequency_index)}.npy', angle_image)

    # zobrazení výsledku
    print('Zobrazení fft obrazu pro danou frekvenci světel')
    rotated_angle_image = np.rot90(angle_image[frequency_index, :, :])
    cv.imshow("FFT", rotated_angle_image)
    cv.waitKey(0)
    cv.destroyAllWindows()


def create_thumbnail(device):
    """
    Vytvoří numpy array jednoho snímku z kamery, ketrý je možné následně uložit jako thumbnail.

    :param device: Kamera, ze které dělá snímek
    :type device: class 'cv2.VideoCapture'
    :return: None
    :rtype: None
    """
    _, image = device.read_frame()
    return image


def create_filename_and_fps(start, stop, n):
    """
    Funkce vytváří název adresáře pro uložení naměřených dat a dalších souborů.
    Dále vypořítá reálnou FPS, která je součástí onoho názvu.

    :param start: Cas začátku měření vytvořený funkcí time.time()
    :type start: float
    :param stop: Cas konce měření vytvořený funkcí time.time()
    :type stop: float
    :param n: Počet snímků naměřených v sekvenci
    :type n: int
    :return: Tuple obsahující název adresáře pro uložení dat obsahující správné lomítko na konci (Linux, Windows) a vypočtenou FPS
    :rtype filename: tuple (str, float)
    """
    fps = n / (stop - start)
    string_fps = str(fps)
    if platform.system() == 'Windows':
        filename = f'{time.strftime("%m%d%H%M")}FPS{string_fps[0:2]}' + '\\'
    else:
        filename = f'{time.strftime("%m%d%H%M")}FPS{string_fps[0:2]}' + '/'
    return filename, fps


def pre_measure_view(device, resize_factor=1.9):
    # TODO: předělat na PyQt a dát tam ten crosshair
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


def write_props(folder_name, real_fps, set_fps, lights_frequency, data):
    # funkce zapisující vybrané parametry do props.csv
    props_filename = f'{folder_name}props.csv'

    props_data = [
        ['Realná FPS', real_fps],
        ['Nastavená FPS', set_fps],
        ['Frekvence světel', lights_frequency],
        ['Tvar dat', data.shape]
    ]

    with open(props_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(props_data)

def read_device_txt():
    """
    Funkce čte soubor device.txt a vrací hodnoty potřebné pro inicializaci kamery. \n
    soubor device.txt vypadá např: \n
        Device index 2 , serial port 0

    Pro Linux:
        Device index - /dev/video*X* termokamery \n
        serial port - /dev/ttyUSB*X* termokamery \n
    Pro Windows:
        Device index - prostě index kamery - nejčastějc 0, pokud není integrovaná kamera \n
        serial port - COM*X* \n

    :return: Tuple obsahující index kamery a číslo seriového portu.
    :rtype: tuple (int, int)
    """
    with open('device.txt', 'r') as file:
        data = file.read()
        device_index, port = [int(s) for s in data.split() if s.isdigit()]
        # rozseká string a když je to číslo, tak si to zapíše
    return device_index, port


# KONSTANTY
device_index, port = read_device_txt()
cols, rows = 640, 512  # velikost snimku
set_fps = int(input('Zadej FPS pro snímání [1/s] (Enter pro default = 10):   ') or '10')  # nastaveni fps pro zaznam
# zadani frekvence svetel pro následný výpočet FFT
# winlin ? problém s desetinou čárkou?
lights_frequency = float(input('Zadej frekvenci světel [Hz] (Enter pro default = 0.1):   ') or '0.1')
x_watch = 320  # souradnice bodu, kde sleduju hodnotu a je tam křížek
y_watch = 256

# definice seriového portu
if platform.system() == 'Windows':
    ser = serial.Serial(f'COM{port}')  # For Windows
else:
    ser = serial.Serial(f'/dev/ttyUSB{port}')  # For Linux
ser.baudrate = 115200

# inicializace kamery
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
frame_time = 1000 // set_fps  # 1000 ms děleno (// pro integer) fpskama

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

    # volá to update funkci i úplně na konci, když má ukázat výsledek calculate_fft()
    # pak to hází chyby, že nemá frame
    if frame is None:
        print("Nesprávně volaná update() funkce!")
        return

    frame = frame.astype('uint16')  # vic mista
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
timer.start(frame_time)

# spuštění celýho Qt molochu
app.exec()

timer.stop()
camera.release_camera()  # Release the camera
# ------------------------
# ZPRACOVÁNÍ A UKLÁDÁNÍ DAT
# --------------------------
print('Probíhá ukládání dat')
# data dostavam z funkce jako list of 3D arrays (512,640) a dělám z toho (N, 512,640) uint16
data = np.stack(data, axis=0, dtype='uint16')

folder_name, real_fps = create_filename_and_fps(casy[0], casy[-1], data.shape[0])
# vytvoření folderu s názvem čas měření, FPS
makedirs(folder_name[0:-1], exist_ok=True)

# uložení dat
print('Ukládání dat - data.npy')
np.save(file=f'{folder_name}data.npy', arr=data)
print(f'Byl vytvořen folder s názvem {folder_name[0:-1]}. Data mají {data.shape[0]} snímků a {round(real_fps, 3)} FPS.')

# uložení timestampu
print('Ukládání timestampů - timestamps.csv')
with open(f'{folder_name}timestamps.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(casy)

# uložení thumbnailu
print('Ukládání thumbnailu - thumb.png')
cv.imwrite(f"{folder_name}thumb.png", thumbnail)

# uložení matlabu
print('Ukládání matlabových dat - .mat')
savemat(f'{folder_name}{folder_name[0:-1]}.mat', {'data': data})

# uložení props
print('Ukládání souboru s parametry měření - props.csv')
write_props(folder_name, real_fps, set_fps, lights_frequency, data)

# vyslání příkazu na NUC shutter
camera.send_command('NUC - Shutter')
camera.send_command('Factory defaults')

# vypocet FFT
calculate_fft(data, real_fps, lights_frequency, folder_name)
print('Měření ukončeno.')
