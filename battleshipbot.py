import numpy as np

class BattleshipBot:
    def __init__(self, boardSideLength, ships):
        self.boardSideLength = boardSideLength
        self.type = "standard"
        self.board = self.createZeroBoard()

        self.VERTICAL = 1
        self.HORIZONTAL = 0

        self.shipSizes = np.array(ships)
        self.largestShip = max(self.shipSizes)

        self.sunkenCells = 0

        unique, counts = np.unique(self.shipSizes, return_counts = True)
        self.uniqueCountsByIndices = [0 for i in range(self.largestShip + 1)] 

        for index, count in zip(unique, counts):
            self.uniqueCountsByIndices[index] = count

        # 0 unknown
        # 1 hit 
        # -1 miss
        # 2 sunk
        self.probabilityBoard = self.createZeroBoard()

    def createZeroBoard(self):
        return np.zeros((self.boardSideLength, self.boardSideLength))
        
    def addHit(self, x, y):
        self.board[y][x] = 1
    
    def addMiss(self, x, y):
        self.board[y][x] = -1
        
    def addSunk(self, x, y):        
        print('original sink', x, y)
        sunkenBefore = self.sunkenCells
        self.recursiveSinker(x, y)
        sunkenAfter = self.sunkenCells

        sunkenShipSize = sunkenAfter - sunkenBefore
        try:
            self.shipSizes = np.delete(self.shipSizes, np.where(self.shipSizes == sunkenShipSize)[0][0])
        except:
            print("tried to remove ship of size", sunkenShipSize, "this size does not exist")
        

    def recursiveSinker(self, x, y):
        print("trying to sink", x, y)
        # sink the current square
        self.board[y][x] = 2
        self.sunkenCells += 1
        

        # check all squares around it
        # sink squares that are hit and miss squares that are unknown
        for xOffset in range(-1, 2):
            for yOffset in range(-1, 2):
                newX, newY = x + xOffset, y + yOffset
                if (xOffset != 0 or yOffset != 0) and newX >= 0 and newX < self.boardSideLength and newY >= 0 and newY < self.boardSideLength:
                    square = self.board[newY, newX].astype(int)
                    if square == 1:
                        self.recursiveSinker(newX, newY)
                    elif square == 0:
                        self.addMiss(newX, newY)
                        
    
    def displayBoard(self):
        print('-'*self.boardSideLength*3)

        print(self.board)

        print('-'*self.boardSideLength*3)

    def getMostLikelyPosition(self, recalculateProbabilityBoard = True, raw = False):
        if recalculateProbabilityBoard:
            self.calculateProbabilityBoard()

        mostLikelyPositionRaw = np.unravel_index(battleshipBot.probabilityBoard.argmax(), battleshipBot.probabilityBoard.shape)

        if raw:
            return mostLikelyPositionRaw

        return (chr(ord('A') + mostLikelyPositionRaw[1]), mostLikelyPositionRaw[0] + 1)
    
    def increase(self, board, x, y, amount):
        if x >= 0 and x < self.boardSideLength and y >= 0 and y < self.boardSideLength: 
            board[y, x] += amount
        return
    
    def calculateProbabilityBoard(self):        
        probBoard = np.zeros((self.boardSideLength, self.boardSideLength))

        numberOfHits = sum(sum((self.board == 1).astype(int)))
        print('number of hit', numberOfHits)

        # if there is more than one hit then they must be forming a pattern, thus follow the pattern
        if numberOfHits > 1:
            for y in range(self.boardSideLength):
                for x in range(self.boardSideLength):
                    # horizontal
                    hitSection = self.board[y, x : x + numberOfHits]
                    print("horizontal", x, y, hitSection)
                    
                    if np.all(hitSection == 1):
                        print('increasing horizontal', x + numberOfHits, y, x - 1, y)

                        # found row of hits, add prob 1 to each end
                        self.increase(probBoard, x + numberOfHits, y, 1)
                        self.increase(probBoard, x - 1, y, 1)

                    # vertical
                    hitSection = self.board[y : y + numberOfHits, x]
                    print('vertical', x, y, hitSection)


                    if np.all(hitSection == 1):
                        print('increasing vertical', x, y + numberOfHits, x, y - 1)
                        # found row of hits, add prob 1 to each end
                        self.increase(probBoard, x, y + numberOfHits, 1)
                        self.increase(probBoard, x, y - 1, 1)
        else:
            # if there is just one hit everywhere around it has equal probability
            for y in range(self.boardSideLength):
                for x in range(self.boardSideLength):
                    if self.board[y, x] == 1:
                        self.increase(probBoard, x + 1, y, 1)
                        self.increase(probBoard, x - 1, y, 1)
                        self.increase(probBoard, x, y + 1, 1)
                        self.increase(probBoard, x, y - 1, 1)

        print("before zeroing step")
        print(probBoard)


        probBoard[self.board != 0] = 0

        if numberOfHits > 0:
            self.probabilityBoard = probBoard
            return
        
        # this is not efficent but I don't think it needs to be for this application
        for shipSize in range(len(self.uniqueCountsByIndices)):
            numberOfSize = self.uniqueCountsByIndices[shipSize]
            if not numberOfSize: continue

            for y in range(self.boardSideLength):
                for x in range(self.boardSideLength):
                    # horizontal
                    partToCheck = self.board[y, x : x + shipSize]
                    endPoints = np.where(partToCheck != 0)[0]
                    endPoint = endPoints[0] if len(endPoints) else len(partToCheck)

                    if endPoint >= shipSize:
                        probBoard[y, x : x + endPoint] += numberOfSize

                    # vertical
                    partToCheck = self.board[y : y + shipSize, x]
                    endPoints = np.where(partToCheck != 0)[0]
                    endPoint = endPoints[0] if len(endPoints) else len(partToCheck)

                    if endPoint >= shipSize:
                        probBoard[y : y + endPoint, x] += numberOfSize

        self.probabilityBoard = probBoard


if __name__ == "__main__":
    # battleshipBot = BattleshipBot(10, [4, 3, 3, 2, 2, 2, 1, 1, 1, 1])
    battleshipBot = BattleshipBot(10, [5, 4, 3, 3, 2])

    with open("output.txt", "a+") as f:
        while True:
            mostLikelyPositionRaw = battleshipBot.getMostLikelyPosition(recalculateProbabilityBoard=True, raw=True)
            mostLikelyPosition = battleshipBot.getMostLikelyPosition(recalculateProbabilityBoard=False, raw=False)
            print('-'*10, 'COMPUTING BEST SHOT FOR BOARD', '-'*10)
            print('BOARD')
            print(battleshipBot.board)
            print('SHIP LOCATION LIKELIHOODS')
            print(battleshipBot.probabilityBoard)
            print("shoot at: ", mostLikelyPosition)


            result = input('Was it a HIT, a MISS, or SUNK (h, m, s)?: ')
            f.write(result + '\n')

            if result == 'h':
                battleshipBot.addHit(mostLikelyPositionRaw[1], mostLikelyPositionRaw[0])
            if result == 'm':
                battleshipBot.addMiss(mostLikelyPositionRaw[1], mostLikelyPositionRaw[0])
            if result == 's':
                battleshipBot.addSunk(mostLikelyPositionRaw[1], mostLikelyPositionRaw[0])
            
        




