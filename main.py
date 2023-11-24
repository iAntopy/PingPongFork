from Pi import Pi
from Po import Po
from Ping import Ping
from Pong import Pong
from Pinger import Pinger
from Ponger import Ponger
from Pingest import Pingest
from Pongest import Pongest
from GameInterface import Game
from GameManager import main

import asyncio as asy
import pygame as pg

# MASTER LIST
# TODO : allow removing players from games via GameManager
# TODO : implement gamesToEnd queue to avoid issue with deleting games while iterating over gameDict
# TODO : add game state dicts in gameManager or gameInterface to be return with getInfo
# TODO : add queues for gameManager to receive/send messages (gamesToStart, gameStartInfo, gamesToEnd, gameEndInfo, playerEvents)

# FUNCTION LIST
# TODO : implement get/sendUpdateInfo()
# TODO : implement get/sendPlayerInfo()
# TODO : implement get/sendEndInfo()
# TODO : implement get/sendStartInfo()

# DEBUG LIST
# TODO : make sure to always put player 1 and 2 in oposite teams
# TODO : add a "mode" argument to game.respawnBall() and use it when initializing the ball
# TODO : rework the ball respawn trajectory everywhere

# MINOR LIST
# TODO : add double-sided gravity to 4 player ping games (so they're actual ping game lol)
# TODO : add sound effects to collisions (in GameObject class)
# TODO : make an 'asteroids' game (solo)
# TODO : make obstacles type GameObjects in the base class (and use them in pongester)

async def debugTester( Initialiser ):

	pg.init()
	g = Initialiser(1, True)

	print ( g.getInitInfo() )

	g.setWindow(pg.display.set_mode((g.width, g.height)))
	pg.display.set_caption(g.name)

	g.printControlers()
	g.addPlayer( "Player 1", 1 )
	g.printControlers()
	g.start()
	g.printControlers()
	g.run()

	print ( g.getEndInfo() )


if __name__ == '__main__':
	asy.run(debugTester( Pong ))
