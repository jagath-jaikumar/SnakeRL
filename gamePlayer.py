from gameElements import *
import json
import time
import os
import matplotlib.pyplot as plt
import progressbar


class GamePlay:

	def __init__(self, GameRunner):
		self.game = GameRunner
		self.boardsizeTrain = 3
		self.boardsizeTest = 3
		self.num_iterations_train = 100
		self.num_iterations_test = 30

	def train(self):
		self.qL = QLearn(self.boardsizeTrain)
		s = Snake()
		board = Board(self.boardsizeTrain,s, False, True)
		
		while(board.gamesCompleted < self.num_iterations_train):

			x = self.qL.algorithm1(board.gamestate.body, board.gamestate.apple, board.n)
			board.changeHeading(x)
			board.updateBoard()


			self.qL.algorithm2(board.gameOver, board.gameWon, board.gamestate.body, board.gamestate.apple, board.n)


			if board.gameOver or board.gameWon:
				board.resetAll()

		self.qL.saveQTable()
		return (len(self.qL.qTable))

	def play(self, verbose = True):
		s = Snake()
		board = Board(self.boardsizeTest, s, verbose = verbose, replayOn = True)
		if verbose:
			board.draw()
		score = 0
		while (True):
			state = self.qL.stateNow(board.gamestate.body, board.gamestate.apple, board.n)
			x = self.qL.bestAction(state)
			if verbose:
				print(x)
			board.changeHeading(x)
			board.updateBoard()
			if board.gameOver or board.gameWon:
				break
			if verbose:
				board.draw()
			#time.sleep(.1)

		score = board.gameScore
		if verbose:
			print("score: ", board.gameScore)
			print(len(self.qL.qTable))

		return [board.gameScore, len(self.qL.qTable)]


	def trainTestResults(self):
		self.qL.reset()
		scores = []
		qTableSizes = []
		trials = []
		print("Training and testing...")
		bar = progressbar.ProgressBar()
		for i in bar(range(self.num_iterations_test)):
			self.train()
			trials.append(i+1)
			res = self.play(verbose = False)
			scores.append(res[0])
			qTableSizes.append(res[1])


		plt.scatter(trials, scores)
		plt.xlabel("Trials")
		plt.ylabel("Scores")
		plt.ylim([0,self.boardsizeTest**2 + 1])
		plt.show()
		plt.scatter(qTableSizes, scores)
		plt.xlabel("Table Size")
		plt.ylabel("Scores")
		plt.ylim([0,self.boardsizeTest**2 + 1])
		plt.show()

		


class QLearn:

	def __init__(self,n):
		self.qTable = {}
		self.learningRate = 0.5
		self.discountFactor = 0.9
		self.randomize = 0.05

		self.availableActions = ['w','a','s','d']

		self.score = 0
		self.missed = 0

		self.n = n
		self.filename = "qTables/"+str(self.n)+'x'+str(self.n) + '.json'
		if (os.path.exists(self.filename)):
			with open(self.filename, 'r') as fp:
				self.qTable = json.load(fp)


	def printQTable(self):
		print(json.dumps(self.qTable, indent=1))

	def reset(self):
		if (os.path.exists(self.filename)):
			os.remove(self.filename)

	def saveQTable(self):
		with open(self.filename, 'w') as fp:
			json.dump(self.qTable, fp)


	def stateNow(self, body, apple, n):
		playerHeadx = body[0][0]
		playerHeady = body[0][1]
		fruitx = apple[0]
		fruity = apple[1]

		trail = body[1:]


		trailRelativePose = [0]*len(trail)

		fruitRelativePosex = fruitx - playerHeadx
		while(fruitRelativePosex < 0):
			fruitRelativePosex += n
		while(fruitRelativePosex > n):
			fruitRelativePosex -= n

		fruitRelativePosey = fruity - playerHeady
		while(fruitRelativePosey < 0):
			fruitRelativePosey += n
		while(fruitRelativePosey > n):
			fruitRelativePosey -= n

		stateName = str(fruitRelativePosex) + "," + str(fruitRelativePosey)

		l = len(trail)
		if len(trail) >1:

			for i in range(l):
				if (trailRelativePose[i] == 0):
					trailRelativePose[i] = [0, 0]

				trailRelativePose[i][0] = trail[i][0] - playerHeadx;
				while(trailRelativePose[i][0] < 0):
					trailRelativePose[i][0] += n
				while(trailRelativePose[i][0] > n):
					trailRelativePose[i][0] -= n
				
				trailRelativePose[i][1] = trail[i][1] - playerHeady
				while (trailRelativePose[i][1] < 0):
					trailRelativePose[i][1] += n
				while (trailRelativePose[i][1] > n):
					trailRelativePose[i][1] -= n

				stateName += ',' + str(trailRelativePose[i][0]) + ',' + str(trailRelativePose[i][1]);
		return stateName

	def tableRow(self,s):
		if s not in self.qTable:
			self.qTable[s] = {'w' :  0, 'a' : 0, 's' : 0, 'd' : 0}

		return self.qTable[s]
	

	def updateTable(self, s0, s1, reward, action):
		q0 = self.tableRow(s0)
		q1 = self.tableRow(s1)

		newValue = reward + self.discountFactor * max([q1['w'], q1['a'], q1['s'], q1['d']]) - q0[action]
		self.qTable[s0][action] = q0[action] + self.learningRate * newValue



	def bestAction(self, s):
		q = self.tableRow(s)
		if random.random() < self.randomize:
			r = random.randint(0,3)
			return self.availableActions[r]

		maxValue = q[self.availableActions[0]]
		choseAction = self.availableActions[0]
		actionsZero = []

		for i in range(len(self.availableActions)):
			if(q[self.availableActions[i]] == 0): 
				actionsZero.insert(0,self.availableActions[i])

			if(q[self.availableActions[i]] > maxValue):
				maxValue = q[self.availableActions[i]]
				choseAction = self.availableActions[i]

		if(maxValue == 0):
			r2 = random.randint(0,len(actionsZero)-1)
			choseAction = actionsZero[r2]

		return choseAction


	def algorithm1(self, body, apple, n):
		if (len(body) == 1):
			s = "nobody"
			r = random.randint(0,3)
			a =  self.availableActions[r]
		else:	
			s = self.stateNow(body, apple, n)
			a = self.bestAction(s)

		self.curState = s
		self.curAction = a

		return a

	def algorithm2(self, gameOver, gameWon, body, apple, n):

		if gameWon == True:
			r = 1
			nextState = self.stateNow(body, apple, n)
			self.updateTable(self.curState, nextState, r, self.curAction)
			if(r > 0):
				self.score += r
			if(r < 0):
				self.missed += r

		elif gameOver == True:
			r = -1
			nextState = self.stateNow(body, apple, n)
			self.updateTable(self.curState, nextState, r, self.curAction)
			if(r > 0):
				self.score += r
			if(r < 0):
				self.missed += r
		else:
			playerHeadx = body[0][0]
			playerHeady = body[0][1]
			fruitx = apple[0]
			fruity = apple[1]
			r = 0

			if (playerHeadx - fruitx == 0 and playerHeady - fruity == 0):
				r = 1
			else:
				r = -0.1

			nextState = self.stateNow(body, apple, n)
			self.updateTable(self.curState, nextState, r, self.curAction)


			if(r > 0):
				self.score += r
			if(r < 0):
				self.missed += r
		


if __name__ == "__main__":
	game = GameRunner()
	player = GamePlay(game)

	player.train()

	player.trainTestResults()

