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

        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        if self.board[move.startRow][move.startCol] != '--':
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)  # adding it to the list of previous moves
            self.whiteToMove = not self.whiteToMove  # swapping the player

    def undoMove(self):
        if len(self.moveLog) != 0:  # making sure there is atleast 1 move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    # All moves considering checks
    # For each move we check the by doing following:
    # 1. make the move
    # 2. generate all possible moves for opposite player
    # 3. see if any of the moves attack your king
    # 4. if king is safe it is valid, add it to list
    # 5. return list of valid moves only
    def getValidMoves(self):
        return self.getAllPossibleMoves()  # for now we don't worry aboout checks

    # All moves with considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(self.length):
            for c in range(self.length):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # calls appropriate function

        return moves

    # Get all the moves for pawn located at r,c and add them to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn's move
            if self.board[r - 1][c] == "--":  # single square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # two square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # capturing black piece to the left
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 < self.length:  # capturing black piece to the right
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:  # black pawn's move
            if self.board[r + 1][c] == "--":  # single square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # two square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # capturing white piece to the left
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 < self.length:  # capturing white piece to the right
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    # Get all the moves for rook located at r,c and add them to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, down, left, right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, self.length):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
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
        knightMoves = ((-2, 1), (-2, -1), (2, 1), (2, -1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        allyColor = 'w' if self.whiteToMove else 'b'
        for k in knightMoves:
            endRow = r + k[0]
            endCol = c + k[1]
            if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # either empty square of opposition's piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Get all the moves for bishop located at r,c and add them to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))  # top left, bottom left, bottom right, top right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, self.length):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
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
        kingMoves = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(self.length):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < self.length and 0 <= endCol < self.length:  # inside the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # either empty square of opposition's piece
                    moves.append(Move((r, c), (endRow, endCol), self.board))


class Move():
    ranksToRows = {
        "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {
        "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
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
