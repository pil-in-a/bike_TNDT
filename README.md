# Bike_TNDT

`main.py` - hlavní program pro náběr dat výpočet FFT\
`mrm_watch_fft` - marimo program pro prohlížení FFT\
`mrm_watch_raw` - marimo porohlížečka nabrané sekvence\
`mrm_send_commands` - marimo GUI pro posílání hex příkazů do kamery\
`recalculate_fft.py` - skript, který znovu vypočte fft z naměřených dat pro zadanou frekvenci ohřevu\
    - použije se v případě, že se do hlavního skriptu chybně zadá frekvence oheřvu\
`analyzer.py` - prohlížečka FFT dat napsaná v Qt\
`ui_analyzerwindow.py` - definice ui prohlížečky - není potřeba interakce\

dále je potřeba lokálně uložený `commands.py` a `device_defaults.csv`

Have fun!
