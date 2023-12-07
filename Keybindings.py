debugKeys = False
try:
	import cfg
	if cfg.DEBUG_MODE:
		import pygame as pg
		debugKeys = True

except ModuleNotFoundError:
	import game.PingPongRebound.cfg as cfg


if debugKeys:
	# keyboard keys
	UP		= pg.K_UP
	DOWN 	= pg.K_DOWN
	LEFT	= pg.K_LEFT
	RIGHT	= pg.K_RIGHT
	SPACE	= pg.K_SPACE

	# keypad keys
	KW		= pg.K_w
	KS		= pg.K_s
	KA		= pg.K_a
	KD		= pg.K_d
	NZERO	= pg.K_KP0

	START		= pg.K_p
	CLOSE		= pg.QUIT
	KEYPRESS	= pg.KEYDOWN
	ESCAPE		= pg.K_ESCAPE
	RETURN		= pg.K_RETURN

else: #				TODO: Change them to whatever connector.getEvent()outputs
	# keyboard keys
	UP		= 'up'
	DOWN	= 'dn'
	LEFT	= 'lf'
	RIGHT	= 'rt'
	SPACE	= ' '

	# keypad keys
	KW		= 'w'
	KS		= 's'
	KA		= 'a'
	KD		= 'd'
	NZERO	= '0'

	START		= 'start_game'
	CLOSE		= 'end_game'
	KEYPRESS	= 'key_press'
	ESCAPE		= None
	RETURN		= None
