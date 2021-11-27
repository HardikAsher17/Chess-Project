# class to store data related to current state of the game
# determines valid moves and logs of the moves

class GameState():
    def __init__(self):
        # 8x8 board, 2d list, name of piece in 2 characters(color, type)
        # "--" represents empty block
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.length = len(self.board)
        self.moveFunction = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }

        self.moveLog = []
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)  # Tracking kings' location for checking if they are under attack
        self.blackKingLocation = (0, 4)
        self.inCheck = False    # checking if the king is under attack
        self.pins = []     # checking for pieces between our piece and the opponent's attacking piece
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        # self.isPawnPromotion = False
        # if (self.pieceMoved =- 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
        #     self.isPawnPromotion = True
        self.enPassantPossible = ()  # coordinates for the square where enpassant capture is possible

    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move)  # adding it to the list of previous moves
        self.whiteToMove = not self.whiteToMove  # swapping the player
        # update king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # if pawn moves twice, next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()

        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--'

        # # pawn promotion
        if move.pawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N: ")  # later UI part
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:  # making sure there is atleast 1 move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king's position if needed
            if move.pieceMoved == 'wk':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bk':
                self.blackKingLocation = (move.startRow, move.startCol)

            # if pawn moves twice, next move can capture enpassant
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--'  # removes the pawn that was added in the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # puts the pawn back on the correct square it was captured from
                self.enPassantPossible = (move.endRow, move.endCol)  # allow an enpassant to happen on the next move
                # undo a 2 square pawn advance should make enPassantPossible = () again
                if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                    self.enPassantPossible = ()


    # All moves considering checks
    # For each move we check the by doing following:
    # 1. make the move
    # 2. generate all possible moves for opposite player
    # 3. see if any of the moves attack your king
    # 4. if king is safe it is valid, add it to list
    # 5. return list of valid moves only
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            # print("incheck")
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy squares and the king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # squares that the pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, self.length):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you get to a piece and checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1): # go through backwards when u r removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:   # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            # print("notincheck")
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True

        else:
            self.checkMate = False
            self.staleMate = False

        return moves
    '''
    Determine if the enemy can attack the square r, c
    '''

    # def inCheck(self):
    #     if self.whiteToMove:
    #         return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    #     else:
    #         return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    #
    # def squareUnderAttack(self, r, c):
    #     self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
    #     oppMoves = self.getAllPossibleMoves()
    #     self.whiteToMove = not self.whiteToMove  # switch turns back
    #     for move in oppMoves:
    #         if move.endRow == r and move.endCol == c:  # means the square is under attack
    #             return True
    #     return False

    # All moves with considering checks
    def getAllPossibleMoves(self):
        moves = []
        # print(self.whiteToMove)
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # calls appropriate function

        # seen = {}
        # dupes = []
        # a = []
        # for x in moves:
        #     if x.getChessNotation() not in seen:
        #         seen[x.getChessNotation()] = 1
        #     else:
        #         if seen[x.getChessNotation()] == 1:
        #             dupes.append(x.getChessNotation())
        #         seen[x.getChessNotation()] += 1
        #     a.append(x.getChessNotation())
        # print("dupliactes")
        # print(dupes)
        # print("all moves")
        # print(a)
        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        # startRow = self.blackKingLocation[0]
        # startCol = self.blackKingLocation[1]
        # enemyColor = "w"
        # allyColor = "b"
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0,  -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()   # reset possible pin
            for i in range(1, self.length):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < self.length and 0 <= endCol < self.length:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # no piece blocking, so it's a check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:        # a piece blocking, that is, a pin
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break  # off board

        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


    # Get all the moves for pawn located at r,c and add them to the list
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        pawnPromotion = False

        # if self.whiteToMove:  # white pawn's move
        # print(c, r+moveAmount,)
        if self.board[r+moveAmount][c] == "--":  # single square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r+moveAmount == backRow:
                    pawnPromotion = True
                moves.append(Move((r, c), (r+moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r+2*moveAmount][c] == "--":  # two square pawn advance
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))

        if c-1 >= 0:  # capturing black piece to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r+moveAmount][c - 1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveAmount, c - 1), self.board, pawnPromotion=pawnPromotion))
                if(r+moveAmount, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+moveAmount, c - 1), self.board, enPassant=True))

        if c + 1 <= 7:  # capturing black piece to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r+moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
                if (r+moveAmount, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+moveAmount, c + 1), self.board, enPassant=True))

        if self.board[r + 1][c] == "--":  # single square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # two square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            elif (r + 1, c - 1) == self.enPassantPossible:
                moves.append(Move((r, c), (r + 1, c - 1), self.board, enPassant=True))

        # captures
        if c - 1 >= 0:  # capturing white piece to the left
            if self.board[r + 1][c - 1][0] == 'w':
                if not piecePinned or pinDirection == (1, -1):
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
        if c + 1 < 7:  # capturing white piece to the right
            if self.board[r + 1][c + 1][0] == 'w':
                if not piecePinned or pinDirection == (1, 1):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
            elif (r + 1, c + 1) == self.enPassantPossible:
                moves.append(Move((r, c), (r + 1, c + 1), self.board, enPassant=True))

    # Get all the moves for rook located at r,c and add them to the list
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, down, left, right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, self.length):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break  # can't move ahead of a piece
                        else:  # own piece
                            break
                else:  # outside the board
                    break

    # Get all the moves for knight located at r,c and add them to the list
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, 1), (-2, -1), (2, 1), (2, -1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        allyColor = "w" if self.whiteToMove else "b"
        for k in knightMoves:
            endRow = r + k[0]
            endCol = c + k[1]
            if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # either empty square of opposition's piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    # Get all the moves for bishop located at r,c and add them to the list
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # top left, bottom left, bottom right, top right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, self.length):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':  # empty space
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break  # can't move ahead of a piece
                        else:  # own piece
                            break
                else:  # outside the board
                    break

    # Get all the moves for queen located at r,c and add them to the list
    def getQueenMoves(self, r, c, moves):
        # queen moves like both bishop and rook
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # Get all the moves for king located at r,c and add them to the list
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(self.length):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # either empty square of opposition's piece
                    # place king on end square and check fo checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)


class Move():
    ranksToRows = {
        "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {
        "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        # pawn promotion
        self.pawnPromotion = pawnPromotion
        # self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        # enpassant
        if enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'  # enpassant captures opposite colored pawn
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    # overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


# isPawnPromotion became pawnPromotion
# isEnpassantMove became enPassant from the 8th YT video