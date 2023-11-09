import pygame as pg
import GameObject as go
import GameInterface as gi

class Pong(gi.Game):
	name = "Ping"

	width = 2048
	height = 1024

	racketCount = 2
	scoreCount = 2

	speed_b = 10

	factor_rack = 1.10
	gravity = 0

	def initRackets(self):
		self.rackets.append( go.GameObject( 1, self, self.size_b, self.height * (1 / 2), self.size_b, self.size_r ))
		self.rackets[0].setSpeeds( 0, self.speed_r )

		self.rackets.append( go.GameObject( 2, self, self.width - self.size_b, self.height  * (1 / 2), self.size_b, self.size_r ))
		self.rackets[1].setSpeeds( 0, self.speed_r )


	def initBalls(self):
		self.balls.append( go.GameObject( 1, self, self.width * (1 / 4), self.height * (1 / 2) , self.size_b, self.size_b ))
		self.balls[0].setSpeeds( self.speed_b, self.speed_b )
		self.balls[0].setDirs( 1, 1 )


	def initScores(self):
		self.scores.append( 0 )
		self.scores.append( 0 )


	def handleInputs(self, key):
		# player 1
		if key == pg.K_a:
			self.makeMove( 1, "STOP" )
		elif key == pg.K_w:
			self.makeMove( 1, "UP" )
		elif key == pg.K_s:
			self.makeMove( 1, "DOWN" )

		# player 2
		if key == pg.K_LEFT:
			self.makeMove( 2, "STOP" )
		elif key == pg.K_UP:
			self.makeMove( 2, "UP" )
		elif key == pg.K_DOWN:
			self.makeMove( 2, "DOWN" )


	# bouncing off the rackets
	def checkRackets(self, ball):
		for i in range(len(self.rackets)):
			rack = self.rackets[i]
			if ball.overlaps( rack ):
				if (rack.id == 0):
					ball.setPos( rack.box.centerx - self.size_b, ball.box.centery ) # '-' because the ball is going to the left
				elif (rack.id == 1):
					ball.setPos( rack.box.centerx + self.size_b, ball.box.centery ) # '+' because the ball is going to the right
				ball.collideWall( "x" )
				ball.collideRack( rack, "x" )
				ball.dx *= self.factor_rack
				ball.clampSpeed()


	# bouncing on the walls
	def checkWalls(self, ball):
		if ball.box.top <= 0 or ball.box.bottom >= self.height:

			ball.collideWall( "y" )
			ball.dy *= self.factor_wall
			ball.clampSpeed()


	# scoring a goal
	def checkGoals(self, ball):
		if ball.box.left <= 0 or ball.box.right >= self.width:
			# checking who scored
			if ball.box.left <= 0:
				self.scores[1] += 1
				ball.setDirs( -1, -ball.fy )
				ball.setPos (self.width * (3 / 4), (self.height - self.size_b) / 2 )
			if ball.box.right >= self.width:
				self.scores[0] += 1
				ball.setDirs( 1, -ball.fy )
				ball.setPos (self.width * (1 / 4), (self.height - self.size_b) / 2 )

			# reseting the ball's speed
			ball.setSpeeds( self.speed_b, ball.dy )
			ball.clampSpeed()


	def drawLines(self):
		pg.draw.line( self.win, self.col_fnt, ( self.width / 2, 0 ),  ( self.width / 2, self.height ), self.size_l )
		#pg.draw.line( self.win, self.col_fnt, ( 0, self.height / 2 ), ( self.width, self.height / 2 ), self.size_l )


	def drawScores(self):
		text1 = self.font.render(f'{self.scores[0]}', True, self.col_fnt)
		text2 = self.font.render(f'{self.scores[1]}', True, self.col_fnt)

		self.win.blit( text1, text1.get_rect( center = ( self.width * (1 / 4), self.height * (2 / 4) )))
		self.win.blit( text2, text2.get_rect( center = ( self.width * (3 / 4), self.height * (2 / 4) )))