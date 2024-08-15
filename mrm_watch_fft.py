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
def __(form_file, mo, platform):
    mo.stop(form_file.value is None, mo.md('Vyber soubor z nabídky!'))

    if platform.system() == 'Windows':
        folder = f"{form_file.value}" + "\\"
    else:
        folder = f"{form_file.value}" + "/"

    filename = f"{folder}uhel.npy"
    return filename, folder


@app.cell
def __(csv, folder):
    props_dict = {}
    with open(f'{folder}props.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            key = row[0]
            value = row[1]
            props_dict[key] = value

    freq_index = int(props_dict['Index FFT pro danou frekvenci světel'])
    return csv_reader, file, freq_index, key, props_dict, row, value


@app.cell
def __(freq_index, mo):
    frame_slider = mo.ui.number(start=0, stop=20, step=1, value=freq_index, label='frame')
    rotace_slider = mo.ui.number(start=0, stop=359, step=0.5, value=270, label='rotation')
    roi_checkbox = mo.ui.checkbox(value=True, label='Show ROI')
    colormap = mo.ui.dropdown(['jet', 'plasma', 'gnuplot', 'grey', 'hot', 'copper'], value='jet', label='ROI colormap')
    return colormap, frame_slider, roi_checkbox, rotace_slider


@app.cell
def __(filename, frame_slider, np, rotace_slider, scipy):
    uhel = np.load(filename)
    uhel_show = scipy.ndimage.rotate(uhel[frame_slider.value,:,:],rotace_slider.value)
    return uhel, uhel_show


@app.cell
def __(mo, np, uhel_show):
    range_slider = mo.ui.range_slider(start=np.min(uhel_show), stop=np.max(uhel_show), step=0.01, show_value=True, label='range', full_width=True)
    return range_slider,


@app.cell
def __(mo, uhel_show):
    roi_bod_1y = mo.ui.number(start=0, stop=uhel_show.shape[0], step=1, value=280, label='bod 1 Y')
    roi_bod_2y = mo.ui.number(start=0, stop=uhel_show.shape[0], step=1, value=330, label='bod 2 Y')
    roi_bod_1x = mo.ui.number(start=0, stop=uhel_show.shape[1], step=1, value=100, label='bod 1 X')
    roi_bod_2x = mo.ui.number(start=0, stop=uhel_show.shape[1], step=1, value=630, label='bod 2 X')
    return roi_bod_1x, roi_bod_1y, roi_bod_2x, roi_bod_2y


@app.cell
def __(roi_bod_1x, roi_bod_1y, roi_bod_2x, roi_bod_2y):
    roi_coordinates = [roi_bod_1y.value, roi_bod_1x.value, roi_bod_2y.value, roi_bod_2x.value]
    print(roi_coordinates)
    return roi_coordinates,


@app.cell
def __(
    colormap,
    frame_slider,
    mo,
    range_slider,
    roi_bod_1x,
    roi_bod_1y,
    roi_bod_2x,
    roi_bod_2y,
    roi_checkbox,
    rotace_slider,
):
    mo.vstack(
        [
            mo.hstack([frame_slider, rotace_slider, roi_checkbox, colormap]),
            range_slider,
            mo.hstack([roi_bod_1x, roi_bod_1y, roi_bod_2x, roi_bod_2y])
        ],
        align='stretch'
        )
    return


@app.cell
def __(mo, np, roi_coordinates, uhel_show):
    uhel_show_roi = uhel_show[roi_coordinates[0]:roi_coordinates[2],roi_coordinates[1]:roi_coordinates[3]]
    mo.md(f'minimum a maximum ve výřezu: {np.min(uhel_show_roi)}, {np.max(uhel_show_roi)}')
    return uhel_show_roi,


@app.cell
def __(
    colormap,
    plt,
    range_slider,
    roi_checkbox,
    roi_coordinates,
    uhel_show,
    uhel_show_roi,
):
    fig1 = plt.figure(figsize=(20,8))
    ax1 = plt.subplot2grid((1,2),(0,0))
    ax2 = plt.subplot2grid((1,2),(0,1))
    ax1.imshow(uhel_show, vmin=range_slider.value[0], vmax=range_slider.value[1], norm='linear', cmap='plasma')
    if roi_checkbox.value:
        ax1.plot([roi_coordinates[1], roi_coordinates[3]], [roi_coordinates[0],roi_coordinates[0]], 'g-')
        ax1.plot([roi_coordinates[1], roi_coordinates[3]], [roi_coordinates[2],roi_coordinates[2]], 'g-')
        ax1.plot([roi_coordinates[1], roi_coordinates[1]], [roi_coordinates[0],roi_coordinates[2]], 'g-')
        ax1.plot([roi_coordinates[3], roi_coordinates[3]], [roi_coordinates[0],roi_coordinates[2]], 'g-')
    ax2.imshow(uhel_show_roi, cmap=colormap.value, norm='symlog')
    return ax1, ax2, fig1


if __name__ == "__main__":
    app.run()
