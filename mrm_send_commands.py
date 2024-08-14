import marimo

__generated_with = "0.7.20"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    import serial
    from commands import iray_commands as i_c
    import platform
    return i_c, mo, platform, serial


@app.cell
def __(platform):
    if platform.system() == 'Windows':
        default_port = 'COM4'
    else:
        default_port = '/dev/ttyUSB0'
    return default_port,


@app.cell
def __(default_port, mo):
    form_device = mo.md(
        '''
        - Serial port: {serial_port} --- (COM\*, nebo /dev/ttyUSB\*)
        - baudrate: {baudrate} --- (hodnota 115200 je daná kamerou, není třeba měnit)
        '''
    ).batch(serial_port=mo.ui.text(value=default_port), baudrate=mo.ui.text(value='115200')).form(submit_button_label='Vyber')
    form_device
    return form_device,


@app.cell
def __(form_device, mo, serial):
    mo.stop(form_device.value is None, mo.md('Vyber zařízení'))

    ser = serial.Serial(form_device.value['serial_port'])
    ser.baudrate = int(form_device.value['baudrate'])
    return ser,


@app.cell
def __(i_c, mo, ser):
    mo.stop(ser is None, mo.md('Není vybráno zařízení'))
    form_command = mo.ui.dropdown(list(i_c.keys())).form(submit_button_label='Pošli příkaz')
    mo.vstack([
        mo.md('''
        Vyber z příkazů v seznamu:\n
        NUC - Non Uniformity Correction \n
        PLT - barevné palety \n
        DVI - Digital Video Interface (fungují jen LVCMOS, BT1120 a CDS-2 only supports DRC DVS) \n
        DVS - Digital Video Source \n
        IF - Image Flip \n
        CVBS - ?
        '''
    ),
        form_command
    ])
    return form_command,


@app.cell
def __(form_command, i_c, mo, ser):
    mo.stop(form_command.value is None, mo.md('Není vybrán příkaz'))

    ser.write(bytes.fromhex(i_c[form_command.value]))
    mo.md(f'Zapsán příkaz {form_command.value}!')
    return


if __name__ == "__main__":
    app.run()
