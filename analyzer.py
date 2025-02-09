import json
import os
import sys

import numpy as np
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QMainWindow, QApplication, QTreeWidgetItem, QMessageBox
from ui_analyzerWindow import Ui_analyzerWindow
import pyqtgraph as pg
from pyqtgraph import exporters

class AnalyzerWindow(QMainWindow, Ui_analyzerWindow):
    # konstanty
    GRADIENTS_LIST = [
        'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
        'cyclic', 'greyclip', 'grey', 'viridis', 'inferno',
        'plasma', 'magma', 'turbo'
    ]
    CROSSHAIR_OFFSET = 15


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # načtení UI z importovaného souboru
        # soubor byl vytvořen pomocí Qt Designer 6 jako .ui file a následně převeden pomocí pyside6-uic
        # pyside6-uic analyzerWindow.ui -o ui_analyzerWindow.py
        self.ui = Ui_analyzerWindow()
        self.ui.setupUi(self)

        # iniciace proměnných, které používám globálně - není stropro nutné
        self.id_picker = {} # to bude dictionary, která bude obsahovat ID ke každýmu stringu z ui.combo_filepicker
        self.image_item = None # pg.ImageItem
        self.histogram = None # pg.HistogramLUTItem
        self.fft_data = None # kompletní (Y,X,20) array fft dat se všemi indexy
        self.cross_x = None # pozice Xhair X
        self.cross_y = None # pozice Xhair Y

        # dodatečná definice obsahu GraphicsLayoutWidget, protože to Qt Designer neumí
        self.custom_pyqtgraph_widget()

        # -------------------------------
        # spojení signálů a slotů v ui
        # --------------------------------

        # připojení signálu od comboboxu k id_pickeru a pak do populate_widget
        self.ui.combo_filepicker.currentTextChanged.connect(self.on_filepicker_selection)

        # colormap
        # načte si GRADIENTS_LIST do comboboxu a nastaví default
        # při změně se mastaví gradient preset pro histogram
        # list vychází z pg.GradientEditorItem, který je obsažen v pg.HistogramLUTItem
        self.ui.combo_colormap.addItems(self.GRADIENTS_LIST)
        self.ui.combo_colormap.setCurrentText('thermal')
        self.ui.combo_colormap.currentTextChanged.connect(self.histogram.gradient.loadPreset)

        # index FFT - připojení k labelu a k load_image_data
        # defaultní hodnoty nastaví populate_widgets
        self.ui.slider_fft_index.valueChanged.connect(self.on_fft_index_change)

        # Snapshot button
        self.ui.button_snapshot.clicked.connect(self.save_snapshot)

        #--------------
        # BĚH PROGRAMU
        # -------------
        # první program zkontroluje, jestli nebyl skript spuštěnej s argumentem ID a kdyžtak ihned populuje widgety

        if len(sys.argv) > 1:
            self.id = sys.argv[1]
            self.populate_widgets(self.id)

        # dále co program udělá bude, že si vygeneruje seznam relevantních měření
        # dělá to ale ve svym threadu, aby zbytek okna šlapal, když třeba dostane konkrétní měření jako argument
        my_threadpool = QThreadPool()
        my_threadpool.start(self.file_picker_build)

    def custom_pyqtgraph_widget(self):
        """
        Jednoduchá funkce, která veme self.ui.graphics_layout a nastrká do něj ViewBox, ImageItem a HistogramLUTItem
        Protože to QtDesigner neumí.
        :return:
        """
        my_pg_graphics_layout = self.ui.graphics_layout

        # Add a ViewBox
        view_box = my_pg_graphics_layout.addViewBox(row=0, col=0)  # Add a view in the first slot
        view_box.setAspectLocked(True)
        view_box.invertY()
        view_box.invertX()

        # Create an ImageItem (to attach to the ViewBox later, if needed)
        self.image_item = pg.ImageItem()
        view_box.addItem(self.image_item)  # Add ImageItem into the ViewBox

        # Add a HistogramLUTItem next to the ViewBox
        self.histogram = pg.HistogramLUTItem(orientation='horizontal')
        my_pg_graphics_layout.addItem(self.histogram, row=1, col=0)  # Add it next to the ViewBox

        # Link the HistogramLUTItem to the ImageItem
        self.histogram.setImageItem(self.image_item)

        # Customize as needed
        self.histogram.gradient.loadPreset('thermal')

    def file_picker_build(self):
        """
        Funkce která při iniciaci okna projede všechny subfoldery s měřením,
        otevře si properties.json a podívá se, jestli měl spočítanou FFT
        pokud ano, poskládá string a ten nasype do listu. Zároveň nasype id do dictionary id_picker

        string bude mít tvar = Date | Name

        Až projede všechny foldery, tak ten list dá do self.ui.combo_filepicker

        :return:
        """
        measurements_location = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measurements')
        folder_list = ['---Vyber měření---'] # iniciace folder listu do combo boxu

        self.ui.statusbar.showMessage('Načítám měření')
        # tenhle loop projede každej folder f /measurements, přečte jestli má properties.json
        # pokud ano podívá se jestli je v něm FFT_Calculated == True (a jestli existuje)

        for entry in os.listdir(measurements_location):
            full_path = os.path.join(measurements_location, entry)
            props_path = os.path.join(full_path, 'properties.json')
            if os.path.isfile(props_path):
                with open(props_path, 'r') as json_file:
                    props_data = json.load(json_file)
                    print(props_data) # DEBUG
                    if props_data['FFT_calculated']:
                        entry_string = f"{props_data['Name']} | {props_data['date_and_time']} | {props_data['notes']}"
                        folder_list.append(entry_string)
                        self.id_picker[entry_string] = entry

        self.ui.combo_filepicker.addItems(folder_list)
        self.ui.statusbar.showMessage('Načítání dokončeno')
        print(self.id_picker)

    def load_data(self, measurement_id):
        """
            Loads data for the selected measurement ID.
            Once data is loaded, it calls populate_widgets() to populate the UI.
            :param measurement_id: ID of the measurement being loaded
            """
        try:
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measurements', measurement_id)

            properties_path = os.path.join(folder_path, 'properties.json')
            with open(properties_path, 'r') as json_file:
                props_data = json.load(json_file)

            if "crosshair_position" not in props_data:
                props_data["crosshair_position"] = {"x": 320, "y": 240}

            self.cross_x = props_data["crosshair_position"]["x"]
            self.cross_y = props_data["crosshair_position"]["y"]

            # načtení dat jako globální proměnná, abych mohl případně změnit index fft
            fft_data_path = os.path.join(folder_path, 'uhel.npy')
            self.fft_data = np.load(fft_data_path)

            # fft_data dávám globálně, ale props_data potřebuju jen v populate widgets (kromě Xhair)
            self.populate_widgets(props_data)

        except Exception as e:
            self.ui.statusbar.showMessage(f"Chyba při načítání dat: {e}")
            raise

    def populate_widgets(self, props_data):
        """
            Funkce populuje všechny widgety v okně.
            Data bere z props_data, který jí dám parametrem
            a fft_data, který jsou v AnalyzerWindow globální
            :param props_data: data z properties.json
            """

        def add_tree_items(parent, dictionary):
            """
            GPT Written
            Recursively adds items to the QTreeWidget for a dictionary.
            :param parent: QTreeWidgetItem or QTreeWidget to add children to
            :param dictionary: Dictionary to populate the tree with
            """
            for key, value in dictionary.items():
                # Create a new tree widget item with key as the first column
                if isinstance(value, dict):
                    # If the value is another dictionary, recursively process it
                    item = QTreeWidgetItem([key, ""])
                    parent.addChild(item)
                    add_tree_items(item, value)
                else:
                    # If the value is not a dictionary, add key-value pair
                    item = QTreeWidgetItem([key, str(value)])
                    parent.addChild(item)

        # populace QTreeWidgets
        self.ui.tree_json.clear()
        add_tree_items(self.ui.tree_json.invisibleRootItem(), props_data)

        # defaultní hodnoty fft_index z props
        self.ui.label_fft_index_value.setText(f'{props_data["FFT_index"]}')
        self.ui.slider_fft_index.setValue(props_data["FFT_index"])
        # přes daný signál spustí on_fft_index_change a z něj load_image_data, kterej hodí obrázek do image_item
        self.ui.slider_fft_index.setMaximum(len(self.fft_data) - 1)

        # nakonec se spustí celé okno
        self.ui.container_graphics_control.setEnabled(True)

    def load_image_data(self, fft_index):
        """
        funkce, která při změně indexu FFT (default, nebo slider) načte správnej obrázek
        určí z něj minima a maxima pro defaultní škálování histogramu (podle crosshair_position)
        fft_data bere z globalu
        :param fft_index: (int) bere index FFT ze slideru nebo z props_data
        :return:
        """
        # výber samotneho obrazu
        image_data = self.fft_data[fft_index]
        print(image_data.shape)
        # slice obdélníku +- OFFSET kolem crosshairu
        slice_for_range = image_data[
                          self.cross_x-self.CROSSHAIR_OFFSET:self.cross_x+self.CROSSHAIR_OFFSET,
                          self.cross_y-self.CROSSHAIR_OFFSET:self.cross_y+self.CROSSHAIR_OFFSET
                          ]
        default_min = np.min(slice_for_range)
        default_max = np.max(slice_for_range)
        print(default_min, default_max)
        # nasype obrázek do self.image_item aby ho mohl zobrazit
        self.image_item.setImage(image_data)
        # nastavení škálování - musí být i pro ImageItem i histogram
        self.image_item.setLevels([default_min, default_max])
        self.histogram.setLevels(default_min, default_max)

    def on_filepicker_selection(self, measurement_string):
        """
        Jednoduchá funkce, která podle stringu z comboboxu vybere správný ID a pomocí něj spustí funkci populate_widgets
        :param measurement_string: string z comboboxu
        :return:
        """
        self.ui.slider_fft_index.setValue(0)
        # pokud zůstane stejná hodnota slideru, tak se nespustí load_image_data
        # jelikož iniciační string v combobnoxu není id ...
        if measurement_string != '---Vyber měření---':
            selected_id = self.id_picker[measurement_string]
            self.load_data(selected_id)
            self.ui.statusbar.showMessage(f'Vybráno měření {selected_id}.')
        else:
            print('není vybráno měření')
            pass

    def on_fft_index_change(self, fft_index):
        """
        Jednoduchej slot pro zmenu hodnoty slideru.
        Převádí signál na integer aby ho mohl přiřadit do labelu a
        spouští funkci load_image_data s indexem FFT.
        :param fft_index: (int) bere index FFT ze slideru
        :return:
        """
        self.load_image_data(fft_index)
        self.ui.label_fft_index_value.setText(f'{fft_index}')

    def save_snapshot(self):
        """
        Saves the current view of the ImageItem as a PNG snapshot in
        the measurement folder of the current ID. The filename will
        be determined by checking the existing snapshots and
        incrementing the highest x in 'snapshot_x.png'.
        """
        try:
            # jelikož self.id nemám, když pouštim analyzer bez argumentu, skládám to celý znova pomocí dostupnejch hodnot
            id_for_snapshot = self.id_picker[self.ui.combo_filepicker.currentText()]
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'measurements', id_for_snapshot)

            if not os.path.exists(folder_path):
                self.ui.statusbar.showMessage(self, "No measurement folder found for the current ID!", 5000)
                return

            # Get all existing snapshot files in the folder
            existing_snapshots = [
                f for f in os.listdir(folder_path)
                if f.startswith("snapshot_") and f.endswith(".png")
            ]

            # Find the current highest snapshot number
            highest_number = 0
            for file in existing_snapshots:
                try:
                    number = int(file.replace("snapshot_", "").replace(".png", ""))
                    highest_number = max(highest_number, number)
                except ValueError:
                    continue

            # Increment to determine the next snapshot number
            next_snapshot_number = highest_number + 1
            snapshot_filename = f"snapshot_{next_snapshot_number}.png"
            snapshot_path = os.path.join(folder_path, snapshot_filename)

            # Export the current image as a PNG file using ImageExporter
            exporter = pg.exporters.ImageExporter(self.image_item)
            exporter.export(snapshot_path)

            # Notify the user
            self.ui.statusbar.showMessage(f"Snapshot saved as: {snapshot_filename}", 5000)

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred while saving the snapshot: {e}")
            raise


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyzerWindow()
    window.show()
    sys.exit(app.exec())