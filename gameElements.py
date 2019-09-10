import random
import gameUtils as utils
import sys

class Board:

	def __init__(self, n, snake, verbose = True, replayOn = False):
		self.gamesCompleted = 0
		self.n = n
		self.board = []
		self.snake = snake

		self.gameOver = False
		self.gameWon = False

		self.verbose = verbose
		self.replayOn = replayOn

		for i in range(n):
			col = n * [0]
			self.board.append(col)

		self.apple = [random.randint(0,n-1),random.randint(0,n-1)]
		self.board[self.apple[0]][self.apple[1]] = 'a'

		self.snakeHead = self.apple
		
		while self.snakeHead == self.apple:
			self.snakeHead = [random.randint(0,n-1),random.randint(0,n-1)]

		self.board[self.snakeHead[0]][self.snakeHead[1]] = 'h'
		self.snake.body = [[self.snakeHead[0],self.snakeHead[1]]]


		self.gamestate = GameState(self.snake.body, [self.apple[0], self.apple[1]])
		self.gameScore = 0


	def draw(self):
		n = self.n
		for x in range(n):
			line = ""
			for y in range(n):
				if self.board[y][x] == 0:
					line += "[ ]"
				elif self.board[y][x] == 'a':
					line += "[a]"
				elif self.board[y][x] == 's':
					line += "[s]"
				elif self.board[y][x] == 'h':
					line += "[h]"
			print(line)
		print()

	def updateBoard(self):

		appleHit = False



		snakeHeading = self.snake.heading

		if snakeHeading == 'n':
			self.snakeHead[1] -= 1
			self.snakeHead[1] %= self.n
		elif snakeHeading == 's':
			self.snakeHead[1] += 1
			self.snakeHead[1] %= self.n
		elif snakeHeading == 'e':
			self.snakeHead[0] += 1
			self.snakeHead[0] %= self.n
		elif snakeHeading == 'w':
			self.snakeHead[0] -= 1
			self.snakeHead[0] %= self.n


		x = self.snakeHead[0]
		y = self.snakeHead[1]

		if self.snakeHead[0] == self.apple[0] and self.snakeHead[1] == self.apple[1]:

			appleHit = True
			self.snake.increaseLength()

		
		self.snake.body.insert(0,[x,y])
		temp = []
		for i in range(self.snake.length):
			temp.append(self.snake.body[i])

		self.snake.body = temp

		if self.snake.length > 2 and self.checkSnake():
			self.gameOver = True

		if (self.snake.length == self.n ** 2):
			self.gameWon = True
			self.gameOver = True
			self.endGame()

		if self.gameOver:
			self.endGame()


		if self.gameWon or self.gameOver:
			return

		for i in range(self.n):
			for j in range(self.n):
				self.board[i][j] = 0
		count = 0
		for i in self.snake.body:
			if any(isinstance(x, list) for x in i):
				i = i[0]
			if count == 0:
				self.board[i[0]][i[1]] = 'h'
			else:
				self.board[i[0]][i[1]] = 's'
			count += 1


		if appleHit:
			self.updateApple()

		self.board[self.apple[0]][self.apple[1]] = 'a'



		tempbody = []
		for i in range(self.snake.length):
			tempbody.append(self.snake.body[i])
		tempapple = []
		for i in self.apple:
			tempapple.append(i)



		self.gamestate = GameState(tempbody, tempapple)

	def updateApple(self):
		
		self.apple = [random.randint(0,self.n-1),random.randint(0,self.n-1)]
		while self.checkApple():
			self.apple = [random.randint(0,self.n-1),random.randint(0,self.n-1)]


	def checkApple(self):
		x = self.apple[0]
		y = self.apple[1]

		l = [x,y]

		for i in self.snake.body:
			if i[0] == x and i[1] == y:
				return True

		return False


	def checkSnake(self):
		x = self.snake.body[0][0]
		y = self.snake.body[0][1]

		l = [x,y]

		for i in range(1, len(self.snake.body)):
			temp = self.snake.body[i]
			if any(isinstance(x, list) for x in temp):
				temp = temp[0]
			if x == temp[0] and y == temp[1]:
				return True

		return False


	def changeHeading(self,x):
		prevHeading = self.snake.heading
		if x == 'w':
			if prevHeading != 's':
				self.snake.heading = 'n'
		elif x == 'a':
			if prevHeading != 'e':
				self.snake.heading = 'w'
		elif x == 's':
			if prevHeading != 'n':
				self.snake.heading = 's'
		elif x == 'd':
			if prevHeading != 'w':
				self.snake.heading = 'e'
		elif x == 'q':
			sys.exit(1)


	def endGame(self):
		self.gamesCompleted +=1
		if self.gameWon or self.gameOver:
			self.gameScore = self.snake.length
			if self.verbose:
				if self.gameWon:
					print("You Won!")
				else:
					print("Game Over!")
				print("Score: ", self.snake.length)
			if self.replayOn == False:
				sys.exit(0)



	def resetAll(self):
		self.board = []
		self.snake = Snake()

		self.gameOver = False
		self.gameWon = False

		for i in range(self.n):
			col = self.n * [0]
			self.board.append(col)

		self.apple = [random.randint(0,self.n-1),random.randint(0,self.n-1)]
		self.board[self.apple[0]][self.apple[1]] = 'a'

		self.snakeHead = self.apple
		
		while self.snakeHead == self.apple:
			self.snakeHead = [random.randint(0,self.n-1),random.randint(0,self.n-1)]

		self.board[self.snakeHead[0]][self.snakeHead[1]] = 's'
		self.snake.body = [[self.snakeHead]]


		self.gamestate = GameState(self.snake.body[0], [self.apple[0], self.apple[1]])
		self.gameScore = 0


class Snake:

	headings = ['n', 's', 'e', 'w']
	def __init__(self):
		self.body = []
		self.length = 1
		self.heading = self.headings[random.randint(0,3)]


	def increaseLength(self):
		self.length += 1


class GameState:

	def __init__(self, body, apple):
		self.body = body
		self.apple = apple



class GameRunner:

	def __init__(self, n=5):
		self.boardsize = n
		pass


	def runEasy(self):
		self.s = Snake()
		self.board = Board(self.boardsize,self.s)
		self.board.draw()
		while(True):
			x = utils.getKey()
			self.board.changeHeading(x)
			self.board.updateBoard()
			self.board.draw()


if __name__ == "__main__":
	game = GameRunner(3)
	game.runEasy()
