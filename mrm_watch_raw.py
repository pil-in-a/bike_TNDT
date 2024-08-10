import marimo

__generated_with = "0.7.19"
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    return mo, np, plt


@app.cell
def __(mo):
    text_field = mo.ui.text(value="08102127FPS25")
    return text_field,


@app.cell
def __(data, mo):
    x_slider = mo.ui.slider(start=0, stop=639, step=1, value=319, show_value=True, label='X')
    y_slider = mo.ui.slider(start=0, stop=511, step=1, value=255, show_value=True, label='Y')
    n_slider = mo.ui.slider(start=0, stop=(data.shape[0]-1), step=1, show_value=True, label='N')
    return n_slider, x_slider, y_slider


@app.cell
def __(mo, n_slider, text_field, x_slider, y_slider):
    mo.hstack([
        text_field,
        x_slider,
        y_slider,
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
def __(text_field):
    folder = text_field.value
    return folder,


@app.cell
def __(folder, np):
    # načtení souboru
    data = np.load(f'{folder}/data.npy')
    print(data.shape)
    return data,


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


if __name__ == "__main__":
    app.run()
