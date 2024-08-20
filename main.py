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
import math  # používání math.floor()
from scipy.io import savemat  # pro ukládání matláku
import platform  # pro nastavování platform specific podmínek
import sys  # programové ukončení skriptu funkcí sys.exit()
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
            self.device = cv.VideoCapture(device_index, cv.CAP_MSMF)  # For Windows

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
    """
    Funkce spočítá FFT z nabraných dat. Uloží soubor uhel npy s prvními dvaceti snímky fft a vrátí vypočtený index odpovídající frekvenci ohřevu.

    :param data: Nabraná data.
    :type data: np.array()
    :param fps: Reálná vypočtená FPS
    :type fps: float
    :param frequency: Nastavená frekvence ohřevu
    :type frequency: float
    :param folder_path: Název adresáře pro uložení dat s lomítkem na konci
    :type folder_path: str
    :return: Index snímku odpovídajícímu frekvenci ohřevu
    :rtype frequency_index: int
    """
    # TODO: tahle funkce je celkově dost rozsháhlá a možná by chtěla trochu zredukovat
    rows = data.shape[1]
    cols = data.shape[2]
    frames = data.shape[0]
    fps = round(fps,1)
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
            fft_data = np.fft.fft(data[-fft_window:, y, x])  # beru okno od konce - ustálenější data
            angle_image[:, x, y] = np.angle(fft_data)

    angle_image = angle_image[0:20, :, :]

    np.save(f'{folder_path}uhel.npy', angle_image)

    # zobrazení výsledku
    print('Zobrazení fft obrazu pro danou frekvenci světel')
    rotated_angle_image = np.rot90(angle_image[frequency_index, :, :])
    cv.imshow("FFT - zmackni Q pro ukonceni", rotated_angle_image)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return frequency_index


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
    cv.namedWindow('live-view - zmackni Q pro pokracovani', cv.WINDOW_NORMAL)
    cv.resizeWindow('live-view - zmackni Q pro pokracovani', 1200, 1000)

    while True:
        pohoda, frame_live = device.read_frame()
        if not pohoda:
            break

        frame_live = cv.resize(frame_live, (int(640 * resize_factor), int(512 * resize_factor)))
        cv.imshow('live-view - zmackni Q pro pokracovani', frame_live)
        key = cv.waitKey(1)

        if key == ord('q'):
            break

    cv.destroyAllWindows()


def write_props(folder_name, real_fps, set_fps, lights_frequency, data, frequency_index, notes):
    # funkce zapisující vybrané parametry do props.csv
    props_filename = f'{folder_name}props.csv'

    props_data = [
        ['Realna FPS', real_fps],
        ['Nastavená FPS', set_fps],
        ['Frekvence svetel', lights_frequency],
        ['Tvar dat', data.shape],
        ['Index FFT pro danou frekvenci svetel', frequency_index],
        ['Poznamky', notes]
    ]

    with open(props_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(props_data)

def read_device_and_defaults_csv():
    """
    Funkce čte soubor device.txt a vrací hodnoty potřebné pro inicializaci kamery. \n
    soubor device.txt vypadá např: \n
        Device index,2
        serial port,0
        default fps,10
        default heat freq,p10

    Pro Linux:
        Device index - /dev/video*X* termokamery \n
        serial port - /dev/ttyUSB*X* termokamery \n
    Pro Windows:
        Device index - prostě index kamery - nejčastějc 0, pokud není integrovaná kamera \n
        serial port - COM*X* \n

    :return: Dictionary s hodnotami pro skript.
    :rtype: dict
    """
    device_defaults_dict = {}
    try:
        with open('device_default.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                key = row[0]
                value = row[1]
                device_defaults_dict[key] = value
    except FileNotFoundError:
        print(f"nemám device_default.csv")
        sys.exit()
    return device_defaults_dict

if __name__ == "__main__":
    # KONSTANTY
    device_default_dict = read_device_and_defaults_csv()

    device_index = int(device_default_dict['Device index'])
    port = int(device_default_dict['serial port'])
    default_fps = str(device_default_dict['default fps'])
    default_freq = str(device_default_dict['default freq'])

    cols, rows = 640, 512  # velikost snimku
    # nastaveni fps pro zaznam
    set_fps = int(input(f"Zadej FPS pro snímání [1/s] (Enter pro default = {default_fps}):   ") or default_fps)
    # zadani frekvence svetel pro následný výpočet FFT
    # TODO: error handling - while loop
    print("""Pro jako frekvenci nebo periodu ohřevu bude počítána FFT?
    zadej např 0.1, 0.083, ... pro frekvenci v Hz
    nebo p10, p12, ... pro periodu v sekundách
    """)
    lights_frequency = (input(f'(default = {default_freq}):    ') or default_freq)

    if 'p' in lights_frequency:
        lights_frequency = 1 / float(lights_frequency[1:])
    else:
        lights_frequency = float(lights_frequency)

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
    # při IF provádí NUC shutter, 2x IF je tam, kdyby byl nějakej špatnej výchozí stav
    camera.send_command('DVI - BT.1120')
    camera.send_command('PLT - Lava')
    camera.send_command('IF - off')
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
    # nová inicializace kamery, protože MSMF měl nějakej problém
    if platform.system() == "Windows":
        camera = Camera(ser, device_index)
    else:
        pass
    # nastavení správného raw formátu
    camera.setup_raw_mode()
    # vypocet intervalu pro QtTimer
    frame_time = 1000 // set_fps  # 1000 ms děleno (// pro integer) fpskama
    # NASTAVENÍ ZOBRAZOVACÍHO OKNA pyqtgraph a QtMainWindow
    # mainwindow je instance CustomMainWindow, která se dá zavřít klávesou
    app = pg.mkQApp("Záznam - stiskni Q pro ukončení záznamu")
    win = pg.GraphicsLayoutWidget(show=True, title="Záznam - stiskni Q pro pokračování", size=(1200, 1000))
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
    # -------------------------------
    # iniciace dat pro záznam
    data, casy, data_bod = [], [], []


    def update():
        # funkce updatující data pro zobrazení a záznam
        success, frame = camera.read_frame()  # shape je (512, 640, 2) - 8bit obrázek a 8bit registr - pro V4L2 backend
        # volá to update funkci i úplně na konci, když má ukázat výsledek calculate_fft()
        # pak to hází chyby, že nemá frame
        if frame is None:
            print("Nesprávně volaná update() funkce!")
            return
        if platform.system() == 'Windows':  # protože MSMF plive RAW data ve formátu (1, 655360)
            frame = frame.reshape(512, 640, 2)
        else:
            pass
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
    # spouštění funkce update - samotný běh loopu
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
    print(
        f'Byl vytvořen folder s názvem {folder_name[0:-1]}. Data mají {data.shape[0]} snímků a {round(real_fps, 3)} FPS.')

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

    # vyslání příkazu na NUC shutter
    camera.send_command('NUC - Shutter')
    camera.send_command('Factory defaults')

    # definice proměnné frequency_index, který spustí výpočet FPS
    frequency_index = calculate_fft(data, real_fps, lights_frequency, folder_name)
    print('Měření ukončeno.')

    # Zápis poznámek
    notes = input('Nějaké poznámky? (Enter -> Default = nic):    ') or ' '

    # uložení props
    print('Ukládání souboru s parametry měření - props.csv')
    write_props(folder_name, real_fps, set_fps, lights_frequency, data, frequency_index, notes)
