import sys
import numpy as np
from main import calculate_fft
import csv
import platform

def update_csv_value(file_path, new_value, target_key="Index FFT pro danou frekvenci světel"):
    # Read the CSV file into memory
    with open(file_path, mode='r', newline='') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    # Modify the value for the specified key
    for row in rows:
        if row[0] == target_key:
            row[1] = new_value
            break  # Assuming keys are unique, so break once the key is found
    else:
        rows.append(['Index FFT pro danou frekvenci světel', new_value])

    # Write the updated data back to the CSV file
    with open(file_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)


# DATA INPUT

folder = input('Zadej název folderu s daty:    ')
print("""Pro jako frekvenci nebo periodu ohřevu bude počítána FFT?
zadej např 0.1, 0.083, ... pro frekvenci v Hz
nebo p10, p12, ... pro periodu v sekundách
""")
frequency = (input('(default = 0.1Hz):    ') or '0.1')

if 'p' in frequency:
    frequency = 1/float(frequency[1:])
else:
    frequency = float(frequency)

# platform specific folder s lomítkem
if platform.system() == 'Windows':
    folder = f'{folder}' + '\\'
else:
    folder = f'{folder}' + '/'

# načtení naměřených dat
data = np.load(f'{folder}data.npy')

# načtení souboru props.csv jako dictionary, ze kterého si budu brát jednotlivé
#  argumenty pro calculate_fft
props_path = f'{folder}props.csv'
props_dict = {}
try:
    with open(props_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            key = row[0]
            value = row[1]
            props_dict[key] = value
except FileNotFoundError:
    print(f"nemám props.csv")
    sys.exit()


# přečtení realné FPS z props.csv
real_fps = float(props_dict['Realná FPS'])

# přepočet FFT
frequency_index = calculate_fft(data=data, frequency=frequency, folder_path=folder, fps=real_fps)

# zápis FFT indexu do props.csv
update_csv_value(file_path=props_path, new_value=frequency_index)
