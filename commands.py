iray_commands = {
	'NUC - Background' : 'AA 05 01 11 02 00 C3 EB AA',
	'NUC - Shutter' : 'AA 05 01 11 02 01 C4 EB AA',
	'Auto NUC on' : 'AA 05 01 01 01 01 B3 EB AA',
	'Auto NUC off' : 'AA 05 01 01 01 00 B2 EB AA',
	'Save Settings' : 'AA 04 01 7F 02 30 EB AA',
	'Factory defaults' : 'AA 05 01 82 02 00 34 EB AA',
	# Palletes are for CVBS and BT656 video formats
	'PLT - White Hot' : 'AA 05 01 42 02 00 F4 EB AA',
	'PLT - Black Hot' : 'AA 05 01 42 02 01 F5 EB AA',
	'PLT - Rainbow' : 'AA 05 01 42 02 02 F6 EB AA',
	'PLT - Rainbow HC' : 'AA 05 01 42 02 03 F7 EB AA',
	'PLT - Iron' : 'AA 05 01 42 02 04 F8 EB AA',
	'PLT - Lava' : 'AA 05 01 42 02 05 F9 EB AA',
	'PLT - Sky' : 'AA 05 01 42 02 06 FA EB AA',
	'PLT - Medium Gray' : 'AA 05 01 42 02 07 FB EB AA',
	'PLT - Gray-red' : 'AA 05 01 42 02 09 FD ED AA',
	'PLT - Special 1' : 'AA 05 01 42 02 0A FE EB AA',
	'PLT - Warning red' : 'AA 05 01 42 02 0B FF EB AA',
	'PLT - Ice fire' : 'AA 05 01 42 02 0C 00 EB AA',
	'PLT - Cyan-red' : 'AA 05 01 42 02 0D 01 EB AA',
	'PLT - Special 2' : 'AA 05 01 42 02 0E 02 EB AA',
	'PLT - Gradient red' : 'AA 05 01 42 02 0F 03 EB AA',
	'PLT - Gradient green' : 'AA 05 01 01 01 10 04 EB AA',
	'PLT - Gradient blue' : 'AA 05 01 01 01 11 05 EB AA',
	'PLT - Alarm green' : 'AA 05 01 42 02 12 06 EB AA',
	'PLT - Alarm blue' : 'AA 05 01 42 02 13 07 EB AA',
	# Digital video source
	'DVS - ORG' : 'AA 05 01 5C 01 00 0D EB AA',
	'DVS - NUC' : 'AA 05 01 5C 01 01 0E EB AA',
	'DVS - DRC' : 'AA 05 01 5C 01 02 0F EB AA',
	'DVS - DNS' : 'AA 05 01 5C 01 05 12 EB AA',
	# Digital Video Interface - BT565, BT1120 a CDS-2 only supports DRC DVS
	'DVI - LVDS' : 'AA 06 01 5D 02 03 00 13 EB AA',
	'DVI - LVCMOS' : 'AA 06 01 5D 02 02 00 12 EB AA',
	'DVI - BT.656' : 'AA 06 01 5D 02 04 00 14 EB AA',
	'DVI - BT.1120' : 'AA 06 01 5D 02 05 00 15 EB AA',
	'DVI - CDS_2' : 'AA 06 01 5D 02 05 80 95 EB AA',
	'DVI - disable' : 'AA 06 01 5D 02 00 00 10 EB AA', # analog only?
	# image flip
	'IF - off' : 'AA 05 01 4C 01 01 FE EB AA',
	'IF - horizontal' : 'AA 05 01 4C 01 02 FF EB AA',
	'IF - vertical' : 'AA 05 01 4C 01 04 01 EB AA',
	'IF - mirror' : 'AA 05 01 4C 01 08 05 EB AA',
	# CVBS video
	'CVBS - on' : 'AA 05 01 3D 02 01 F0 EB AA',
	'CVBS - off' : 'AA 05 01 3D 02 00 EF EB AA',
	# NUC data
	'NUC - Clear' : 'AA 05 01 A1 01 02 54 EB AA',
	'NUC - Acquire' : 'AA 05 01 A1 01 00 52 EB AA',
	'NUC - Save' : 'AA 05 01 A1 01 01 53 EB AA',
	# DDE, DDE mode, AGC, Contrast, Brighthness
}