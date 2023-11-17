import pygame as pg
import GameObject as go
import GameInterface as gi

class Pong(gi.Game):
	name = "Pong"

	width = 2048

	def initRackets(self):
		self.rackets.append( go.GameObject( 1, self, self.size_b, self.height * (1 / 2), self.size_b, self.size_r ))
		self.rackets[0].setSpeeds( 0, self.speed_r )

		self.rackets.append( go.GameObject( 2, self, self.width - self.size_b, self.height  * (1 / 2), self.size_b, self.size_r ))
		self.rackets[1].setSpeeds( 0, self.speed_r )

		self.racketCount = 2


	def initControlers(self):
		self.addBot("bot 1")
		self.addBot("bot 2")


	def initBalls(self):
		self.balls.append( go.GameObject( 1, self, self.width * (1 / 4), self.height * (1 / 2) , self.size_b, self.size_b ))
		self.balls[0].setSpeeds( self.speed_b, self.speed_b )
		self.balls[0].setDirs( 1, 1 )


	def initScores(self):
		self.scores.append( 0 )
		self.scores.append( 0 )


	def handlePygameInputs(self, key):
		# player 1
		if key == pg.K_a:
			self.makeMove( 1, gi.ad.STOP )
		elif key == pg.K_w:
			self.makeMove( 1, gi.ad.UP )
		elif key == pg.K_s:
			self.makeMove( 1, gi.ad.DOWN )

		# player 2
		if key == pg.K_LEFT:
			self.makeMove( 2, gi.ad.STOP )
		elif key == pg.K_UP:
			self.makeMove( 2, gi.ad.UP )
		elif key == pg.K_DOWN:
			self.makeMove( 2, gi.ad.DOWN )


	# bouncing off the rackets
	def checkRackets(self, ball):
		for i in range(len(self.rackets)):
			rack = self.rackets[i]
			if ball.overlaps( rack ):
				if (rack.id == 1):
					ball.setPos( rack.box.centerx + self.size_b, ball.box.centery ) # '+' because the ball is going to the right
				elif (rack.id == 2):
					ball.setPos( rack.box.centerx - self.size_b, ball.box.centery ) # '-' because the ball is going to the left
				ball.collideRack( rack, "x" )
				self.scorePoint( rack.id, gi.ad.HITS )


	# bouncing on the walls
	def checkWalls(self, ball):
		if ball.box.top <= 0 or ball.box.bottom >= self.height:
			ball.collideWall( "y" )


	# scoring a goal
	def checkGoals(self, ball):
		if ball.box.left <= 0 or ball.box.right >= self.width:
			# checking who scored
			if ball.box.left <= 0:
				if self.last_ponger > 0:
					self.scorePoint( 2, gi.ad.GOALS )
				ball.setDirs( -1, -ball.fy )
				ball.setPos (self.width * (3 / 4), self.height * (1 / 2) )
			if ball.box.right >= self.width:
				if self.last_ponger > 0:
					self.scorePoint( 1, gi.ad.GOALS )
				ball.setDirs( 1, -ball.fy )
				ball.setPos (self.width * (1 / 4), self.height * (1 / 2))

			self.respawnBall( ball )


	def respawnBall(self, ball):
		ball.box.centery = self.height * (1 / 2)
		ball.setSpeeds( self.speed_b, ball.dy )


	def drawLines(self):
		pg.draw.line( self.win, self.col_fnt, ( 0, 0 ), ( self.width, 0 ), self.size_l * 2 )
		pg.draw.line( self.win, self.col_fnt, ( self.width / 2, 0 ), ( self.width / 2, self.height ), self.size_l )
		pg.draw.line( self.win, self.col_fnt, ( 0, self.height ), ( self.width, self.height ), self.size_l * 2)


	def drawScores(self):
		text1 = self.font.render(f'{self.scores[0]}', True, self.col_fnt)
		text2 = self.font.render(f'{self.scores[1]}', True, self.col_fnt)

		self.win.blit( text1, text1.get_rect( center = ( self.width * (1 / 4), self.height * (2 / 4) )))
		self.win.blit( text2, text2.get_rect( center = ( self.width * (3 / 4), self.height * (2 / 4) )))


if __name__ == '__main__':
	g = Pong()
	g.start()
	g.run()