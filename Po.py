try:
	from . import cfg
	from .master import ad
	from .master import gi
except ImportError:
	import cfg
	from master import ad
	from master import gi

if cfg.DEBUG_MODE:
	import pygame as pg


class Po(gi.Game):
	name = "Po"

	width = 1280
	height = 1280

	factor_rack = 1.2
	factor_wall = 0.9

	score_mode = gi.ad.HITS


if __name__ == '__main__': #		NOTE : DEBUG

	pg.init()
	g = Po(1, True)

	g.setWindow(pg.display.set_mode((Po.width, Po.height)))
	pg.display.set_caption(g.name)

	#g.addPlayer( "Player 1", 1 )

	g.start()
	g.run()