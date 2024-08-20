import marimo

__generated_with = "0.7.20"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import scipy
    import csv
    import platform
    import os
    return csv, mo, np, os, platform, plt, scipy


@app.cell
def __(__file__, os):
    script_location = os.path.dirname(os.path.abspath(__file__))
    folder_list = ['---']

    # Iterate through all entries in the script's directory
    for entry in os.listdir(script_location):
        full_path = os.path.join(script_location, entry)
        props_path = os.path.join(full_path, 'props.csv')
        # Check if the entry is a directory
        if os.path.isdir(full_path) and os.path.exists(props_path):
            folder_list.append(entry)

    folder_list.sort()
    return entry, folder_list, full_path, props_path, script_location


@app.cell
def __(folder_list, mo):
    form_file = mo.ui.dropdown(options=folder_list, value="---", label='Vyber folder s daty:').form(submit_button_label='Zobraz')
    form_file
    return form_file,


@app.cell
def __(csv, form_file, mo, os, platform):
    mo.stop(form_file.value is None, mo.md('Vyber soubor z nabídky!'))

    if platform.system() == 'Windows':
        folder = f"{form_file.value}" + "\\"
    else:
        folder = f"{form_file.value}" + "/"

    filename = f"{folder}data.npy"

    if os.path.isfile(f'{folder}props.csv'):
        props_dict = {}
        with open(f'{folder}props.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                key = row[0]
                value = row[1]
                props_dict[key] = value
    else:
        props_dict = None
    return csv_reader, file, filename, folder, key, props_dict, row, value


@app.cell
def __(filename, np):
    # načtení souboru
    data = np.load(filename)
    return data,


@app.cell
def __(data, mo):
    x_slider = mo.ui.number(start=0, stop=639, step=1, value=319, label='X')
    y_slider = mo.ui.number(start=0, stop=511, step=1, value=255, label='Y')
    n_slider = mo.ui.slider(start=0, stop=(data.shape[0]-1), step=1, show_value=True, label='N', full_width=True)
    return n_slider, x_slider, y_slider


@app.cell
def __(mo, n_slider, x_slider, y_slider):
    mo.vstack([
        mo.hstack([
            x_slider,
            y_slider
        ]),
        n_slider
    ])
    return


@app.cell
def __(n_slider, x_slider, y_slider):
    x_poi = x_slider.value
    y_poi = y_slider.value
    snimek = n_slider.value
    return snimek, x_poi, y_poi


@app.cell
def __(data, np, plt, snimek, x_poi, y_poi):
    fig1 = plt.figure(figsize=(20,5))
    ax1 = plt.subplot2grid((1,3),(0,0))
    ax3 = plt.subplot2grid((1,3),(0,1), colspan=2)

    ax1.imshow(data[snimek,:,:], cmap='jet')
    ax1.plot([0,639], [y_poi, y_poi], 'r-')
    ax1.plot([x_poi, x_poi], [0,511], 'r-')
    ax3.plot(data[:, y_poi, x_poi])
    ax3.plot([snimek,snimek],[np.min(data[:, y_poi, x_poi]), np.max(data[:, y_poi, x_poi])])
    return ax1, ax3, fig1


@app.cell
def __(mo, props_dict):
    mo.stop(props_dict is None, mo.md('Neexistuje soubor props.csv'))

    tabulenka = mo.ui.table(data=[props_dict])
    tabulenka
    return tabulenka,


if __name__ == "__main__":
    app.run()
