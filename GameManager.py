import asyncio as asy
import random as rdm
import sys
import time


try:
	from . import cfg
	from .master import ad
	from . import PlayerControler as pl
	from . import BotControler as bc
	from .Ping import Ping
	from .Pong import Pong
	from .Pingest import Pingest
except ImportError:
	import cfg
	from master import ad
	import PlayerControler as pl
	import BotControler as bc
	from Ping import Ping
	from Pong import Pong
	from Pingest import Pingest



if cfg.DEBUG_MODE:
	import pygame as pg

#from Pi import Pi
#from Po import Po
# from .Ping import Ping
# from .Pong import Pong


#from .Pinger import Pinger
#from Ponger import Ponger
# from .Pingest import Pingest
#from Pongest import Pongest

class GameManager:

	gameTypeCount = 8

	windowID = 0 #							NOTE : DEBUG

	def __init__( self, messenger, _debugMode = False ):
		''' messenger should be an instance of GameConnector '''
		print("GameManager constructor called")

		#if not messenger:
		#	raise ValueError ('GameManager needs a messenger object to send updates and events to players.')
		self.messenger = messenger
		self.debugMode = _debugMode #		NOTE : DEBUG

		#self.gameCount = 0
		self.maxGameCount = 0
		self.runGames = False

		self.lock = asy.Lock()
		self.t0 = None
		self.t1 = None
		self.sleep_loss = 0.001# Rough estimate. Will adjust over time

		self.gameDict = dict()

	def __del__(self):
		print("GameManager destructor called")
		self.runGames = False
		games_dump = [self.gameDict.pop(k) for k in tuple(self.gameDict.keys())]
		for game in games_dump:
			game.close()		
		games_dump.clear()		



	@property
	def gameCount(self):
		return len(self.gameDict)

	async def addGame( self, gameType, gameID):

		Initialiser = self.getInitialiser( gameType )

		if (Initialiser == None):
			raise ValueError("Could not add game of type " + gameType)
			#return 0
		if gameID in self.gameDict:
			#raise ValueError(f"Game with ID {gameID} already in GameManager")
			raise ValueError(f"Game with ID {gameID} already in GameManager.")

		newGame = Initialiser( gameID, self.debugMode ) # 	TODO : detach from pygame
		#if self.debugMode:
		#	newGame.setWindow(self.win)
		async with self.lock:
			self.gameDict[gameID] = newGame
		#self.gameCount += 1
		#if self.gameCount > self.maxGameCount:
		#	self.maxGameCount = self.gameCount

		#if self.debugMode:
			#self.addPlayerToGame( GameID, "Tester " + str( GameID ), GameID ) #		NOTE : DEBUG
		if not self.runGames:
			print('Calling asyncio.run on self.mainloop()')
			self.runGames = True
			#asy.run(self.mainloop)
			self.t0 = time.monotonic()
			asy.get_event_loop().create_task(self.mainloop())

		print('Print after asyncio.')

		return gameID


	async def addPlayerToGame( self, playerID, name, key ):
		async with self.lock:
			if ( self.gameDict.get(key)):
				self.gameDict.get(key).addPlayer( name, playerID )
			else:
				print ("could not add player #" + str( playerID ) + " to game #" + str( key ))


	async def startGame( self, gameID ):
		async with self.lock:
			if gameID not in self.gameDict:
				raise ValueError(f"No game exists with ID {gameID} in GameManager.")
			print('GameManager startGame called')
			game = self.gameDict.get(gameID)
			if game:
				game.start()
			#self.gameDict.get(gameID).start()


	async def removePlayerFromGame( self, _playerID, gameID ):
		async with self.lock:
			game = self.gameDict.get(gameID)
			if not game:
				raise ValueError(f"No game exists with ID {gameID} in GameManager.")
			if not game.hasPlayer(_playerID):
				raise ValueError ("player #" + str( _playerID ) + " is absent from game #" + str( key ))
			
			if game.state == ad.ENDING:
				# A player is leaving a game after it was ended normaly. The player should be sent the final game state and states.
				pass
			elif game.state == ad.PLAYING or game.state == ad.STARTING:
				# A player is leaving a game either after everyone has joined the game but before officially starting
				# or after the game was started and playing. The game is canceled and stats aren't compiled for it.
				# All remaining players should receive a final game state message indicating the game was stopped early.
				# and how left early.
				pass
			
			game.removePlayer( _playerID )


	async def removeGame( self, gameID ):
		async with self.lock:			
			if gameID not in self.gameDict:
				raise ValueError(f"No game exists with ID {gameID} in GameManager.")
			#self.gameDict.get(gameID).close()
			game = self.gameDict.get(gameID)
			game.close()		
			self.gameDict.pop(gameID)
			#self.gameCount -= 1
			self.runGames = (self.gameCount > 0)


	def runGameStep( self, game ):
		if game.state == ad.PLAYING:
			game.step()
			#game.moveObjects()
			#game.makeBotsPlay()
			#game.clock.tick (game.framerate) # 	TODO : detach from pygame

		else:
			ValueError (" This game is not currently running ")



	async def tickGames(self):
		deleteList = []
		#try: #		 NOTE : ineloquent but ffs why the fuck can't you edit a dict while itterating in it...
			 #				like isn't that the whole fucking point of not using a different type of container
		async with self.lock:
			for key, game in self.gameDict.items():
				#game = self.gameDict.get( key )

				if game.state == ad.STARTING:
					pass #								send player info packet from here

				elif game.state == ad.PLAYING:
					game.step()
					#self.runGameStep( game )

					#if self.debugMode: #				NOTE : DEBUG
					#	if key == self.windowID:
					#		self.displayGame( game )

				elif game.state == ad.ENDING:
					if self.debugMode and self.windowID == key:
						print ("this game no longer exists")
						print ("please select a valid game (1-8)")
						self.windowID = 0
						self.emptyDisplay()

					else: #								send closing info packet from here
						pass

					deleteList.append(key)

			for key in deleteList:
				self.removeGame( key )
		#except:
			#print("Warning : GameManager.tickGames() : removed item while iterating over gameDict")

	def getNextSleepDelay(self):
		self.t1 = time.monotonic()
		dt = self.t1 - self.t0
		self.t0 = self.t1

		diversion = dt - cfg.FRAME_DELAY

		# Sleep diversion correction. Learns its optimal delay over time
		# to try and make shure the actual real life framerate converges
		# to the frame rate chosen in cfg, and ajusts itself based on the
		# current load on the server. We can imagine the diversion between
		# desired framerate and actual framerate getting widder as the number
		# of games to handle and the number of players to update increases.
		# This formula will change a time correction value over time by moving 
		# this delay gradualy towards the real life delay required to have
		# a framerate as close to the desired one and that auto adjusts
		# based on current load on server. The convergence rate is set
		# at 10% every frame. Meaning the delay adjustment will move 10%
		# towards the real divergence required to have a perfect, real life
		# sleep to keep the exact fps count chosen.
		correction = (diversion - self.sleep_loss) * 0.1
		self.sleep_loss += correction#(diversion - self.sleep_loss) * 0.1
		#print("delta time: ", dt, "diversion: ", diversion, "sleep loss: ", self.sleep_loss, "correction: ", correction)
		#print('next sleep delay: ', cfg.FRAME_DELAY - self.sleep_loss)
		return cfg.FRAME_DELAY - self.sleep_loss

	async def mainloop(self):
		
		await asy.sleep(cfg.FRAME_DELAY - self.sleep_loss)# Accelerates the self.sleep_loss accurate adjustment.
		#self.getNextSleepDelay()
		#self.sleep_loss = self.getTimeDelta() - cfg.FRAME_DELAY

		while self.runGames:
			#print('Async while running games')
			#t0 = time.monotonic()
			await self.tickGames()
			
			# Print all game states DEBUG(): 
			#for game in self.gameDict.values():
			#	print(game)
			#print('Async event loop has ticked all games.')
			#t1 = time.monotonic()
			#exe_time_correction = t1 - t0
			# Possibly adjust the sleep time based on real time passed since last frame.
			# to regulate game speed through time and for all players.

			sleep_time = self.getNextSleepDelay()
			#diversion = delta_time - cfg.FRAME_DELAY
			#self.sleep_loss += (diversion - self.sleep_loss) * 0.2
			#next_delay = 2 * cfg.FRAME_DELAY - exe_time_correction
			#print('dt: ', str(delta_time), "diversion: ", diversion)
			#print("exec time : ", exe_time_correction, " Corrected delay : ", cfg.FRAME_DELAY - exe_time_correction, 'next delay : ', next_delay)
			#if exe_time_correction < cfg.FRAME_DELAY:
			#await asy.sleep(cfg.FRAME_DELAY + exe_time_correction)
			#await asy.sleep(next_delay)
			await asy.sleep(sleep_time)
			#await asy.sleep(cfg.FRAME_DELAY - diversion * 0.5 )
		
		print('MAINLOOP EXIT !')



	''' ALL DEBUG PASSED THIS POINT EXCEPT FROM @staticmethod  '''

	def takePlayerInputs( self ): # 					NOTE : DEBUG
		# read local player inputs
		for event in pg.event.get():
			print("Pressed key : ", event.type)

			if event.type == pg.KEYDOWN:
				k = event.key

				if self.debugMode:
					initialID = self.windowID

					# closes the game
					if k == pg.K_ESCAPE:
						for game in self.gameDict.values():
							game.close()
						self.runGames = False
						sys.exit()

					# respawns the ball
					elif k == ad.RETURN:
						if self.windowID != 0:
							if self.gameDict.get(self.windowID) != None:
								game = self.gameDict.get(self.windowID)
								game.respawnAllBalls()
								print ( "respawning the ball(s)" )
							else:
								print ( "coud not respawn the ball(s)" )
						else:
							print ( "please select a valid game (1-8)" )
						return

					# rotate game to view
					elif k == pg.K_q or k == pg.K_e:
						if k == pg.K_e:
							self.windowID += 1
						else:
							self.windowID -= 1

						if self.windowID <= 0:
							self.windowID = self.maxGameCount
						elif self.windowID > self.maxGameCount:
							self.windowID = 1

					# select game to view
					elif k == pg.K_0:
						self.windowID = 0
					elif k == pg.K_1:
						self.windowID = 1
					elif k == pg.K_2:
						self.windowID = 2
					elif k == pg.K_3:
						self.windowID = 3
					elif k == pg.K_4:
						self.windowID = 4
					elif k == pg.K_5:
						self.windowID = 5
					elif k == pg.K_6:
						self.windowID = 6
					elif k == pg.K_7:
						self.windowID = 7
					elif k == pg.K_8:
						self.windowID = 8
					elif k == pg.K_9:
						self.windowID = 9

					# checks if viewed game changed
					if initialID != self.windowID:
						if self.gameDict.get(self.windowID) == None:
							print( "could not switch to game #" + str( self.windowID ) )
							print( "please select a valid game (1-8)" )
							self.emptyDisplay()
						else:
							print( "now playing in game #" + str( self.windowID ) )
							pg.display.set_caption( self.gameDict.get(self.windowID).name )
						return

				# handling movement keys presses
				if self.gameDict.get(self.windowID) == None:
					if self.windowID != 0:
						print( "game #" + str( self.windowID ) + " no longer exists" )
					print( "please select a valid game (1-8)" )
				else:
					controler = self.gameDict.get(self.windowID).controlers[0]
					if controler.mode != ad.PLAYER:
						print ( "cannot move a bot's racket" )
					else:
						controler.handleKeyInput(k)



	def displayGame( self, game ): # 						NOTE : DEBUG
		if game.state == ad.PLAYING:
			if game.width != self.win.get_width() or game.height != self.win.get_height():
				self.win = pg.display.set_mode( (game.width, game.height) )
				pg.display.set_caption( game.name ) #

			game.refreshScreen()


	def emptyDisplay( self ): # 							NOTE : DEBUG
		pg.display.set_caption("Game Manager")
		self.win = pg.display.set_mode((2048, 1280))
		self.win.fill( pg.Color('black') )


	@staticmethod
	def getMaxPlayerCount( gameType ):
		#if gameType == "Pi":
		#	return Pi.maxPlayerCount
		if gameType == "Ping":
			#return Ping.maxPlayerCount
			return Ping.racketCount
		#elif gameType == "Pinger":
		#	return Pinger.maxPlayerCount
		elif gameType == "Pingest":
			return Pingest.racketCount
		#elif gameType == "Po":
		#	return Po.maxPlayerCount
		elif gameType == "Pong":
			return Pong.racketCount
		#elif gameType == "Ponger":
		#	return Ponger.maxPlayerCount
		#elif gameType == "Pongest":
		#	return Pongest.maxPlayerCount
		else:
			print ( "Error : GameManager.getMaxPlayerCount() : invalid game type" )
			return 0


	@staticmethod
	def getInitialiser( gameType, rdmStart = 4 ):
		if gameType == "Pi":
			return Pi
		elif gameType == "Ping":
			return Ping
		elif gameType == "Pinger":
			return Pinger
		elif gameType == "Pingest":
			return Pingest
		elif gameType == "Po":
			return Po
		elif gameType == "Pong":
			return Pong
		elif gameType == "Ponger":
			return Ponger
		elif gameType == "Pongest":
			return Pongest
		elif gameType == "Random":
			return GameManager.getRandomGameType(rdmStart)
		else:
			print ( "Error : GameManager.getInitialiser() : invalid game type" )
			return None


	@staticmethod
	def getRandomGameType(playerCount = 1):
		if playerCount == 1:
			start = 0
		elif playerCount == 2:
			start = 2
		elif playerCount == 4:
			start = 4
		else:
			print( "Error : GameManager.getRandomGameType() : invalid player count" )
			return None

		value = rdm.randint(start, GameManager.gameTypeCount - 1 )
		if value == 0:
			return "Pi"
		elif value == 2:
			return "Ping"
		elif value == 4:
			return "Pinger"
		elif value == 6:
			return "Pingest"
		elif value == 1:
			return "Po"
		elif value == 3:
			return "Pong"
		elif value == 5:
			return "Ponger"
		elif value == 7:
			return "Pongest"


async def main():  # ASYNC IS HERE

	gm = GameManager(True)

	if (gm.debugMode):
		pg.init()
		gm.emptyDisplay()

	addAllGames( gm )

	while gm.runGames:

		if gm.debugMode:
			gm.takePlayerInputs()

		gm.tickGames()

	if gm.debugMode:
		await asy.sleep(0)
	else: # 											NOTE : put game ticks here if not in debugMode
		pass


def addAllGames( gm ): #								NOTE : DEBUG
	gameID = 1

	gm.startGame( gm.addGame( "Pi", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Po", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Ping", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Pong", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Pinger", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Ponger", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Pingest", gameID ))
	gameID += 1
	gm.startGame( gm.addGame( "Pongest", gameID ))
	gameID += 1

	print ("select a player (1-8)")


if __name__ == '__main__':
	#funny_tricks = 1
	#gm = GameManager(funny_tricks, False)
	#gm.addGame('Pong', 1)
	#gm.removeGame(1)
	#asy.run( main())

	def test_create_destroy_gamemanager():
		funny_tricks = 1
		gm = GameManager(funny_tricks, False)

	async def test_add_remove_game():
		funny_tricks = 1
		gm = GameManager(funny_tricks, False)
		gm.addGame('Pong', 1)
		await asy.sleep(2)
		#time.sleep(2)# FAILS ! This does sync sleep on the main thead
		gm.removeGame(1)
		print("Post removeGame sleep 1" )
		await asy.sleep(1)

	async def test_add_start_game():
		funny_tricks = 1
		gm = GameManager(funny_tricks, False)
		gm.addGame('Pong', 1)
		gm.startGame(1)
		await asy.sleep(1)


		#...
		gm.stopGame(1)
		print("Post removeGame sleep 1" )
		await asy.sleep(1)

	async def test_add_two_games_start_and_stop_desynced():
		funny_tricks = 1
		gm = GameManager(funny_tricks, False)
		await gm.addGame('Pong', 1)
		await gm.addGame('Pong', 2)
		print("Start game 1" )
		await gm.startGame(1)
		await asy.sleep(1)
		print("Start game 2" )
		await gm.startGame(2)
		await asy.sleep(1)
		print("Stop game 1" )
		await gm.removeGame(1)
		await asy.sleep(1)
		print("Stop game 2" )
		await gm.removeGame(2)
		#...
		print("Post removeGame sleep 1" )
		await asy.sleep(1)


	#test_create_destroy_gamemanager()
	asy.run(test_add_two_games_start_and_stop_desynced())



