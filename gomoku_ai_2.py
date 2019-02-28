#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
from boardstate import *
from copy import deepcopy
from gomoku import Gomoku

import Queue as q
import time
from evaluate import *


class gomokuAI2(object):
    def __init__(self, gomoku, currentState):

        self.__gomoku = gomoku
        self.__currentState = currentState
        self.__currentI = -1
        self.__currentJ = -1

    def set_board(self, i, j, state):
        self.__gomoku.set_chessboard_state(i, j, state)

    def first_step(self):
        # AI plays in the center
        self.__gomoku.set_chessboard_state(7, 7, self.__currentState)
        print 'ai '+str(self.__currentState)+' moves on: (7, 7) '
        return True

    def second_step(self):
        """
            board : board object
            return: (int,int)

            If the AI must go second, it shouldn't think,
            it should just go diagonal adjacent to the first
            placed tile; diagonal into the larger area of the
            board if one exists

            this could be re-define by openning regulations when ai takes black and go first_step
            """
        for i in self.__gomoku.get_chessMap():
            if i != BoardState.EMPTY:
                x = i[0]
                y = i[1]
        self.__gomoku.set_chessboard_state(x + 1, y, self.__currentState)
        return True

    def _eval_func(self, board, position, attack):
        """
        board   : current chess map
        position: (int,int)
        attack  :  bool
        return  :  int

        Takes a board, and a position on that board,
        and evaluates the importance of that position on
        the board.  It does so by evaluating the number of 
        ways that that position can be used in making five in connection, 
        with an exponential weighting for more pieces in a connection.  
        Extremely heavy weighting
        for making a full on five.connects- but the connection is
        weighted heavier if in attack mode than if in defense mode.
        That way, the function will always place taking a winning
        move over blocking another's winning move.
        """
        (y, x) = position
        color = self.__currentState if attack else self.getEnemyColor(self.__currentState)
        total_score = 0

        # relative positions that we/enemy may place their stones
        for pair in ((1, 0), (0, 1), (1, 1), (1, -1)):
            (dy, dx) = pair
            pathlist = [0]
            # postion: before/after = -1/1
            for s in (1, -1):
                for i in range(1, 5):
                    py = y + dy * i * s
                    px = x + dx * i * s
                    # out of board, or enemy blocking
                    if (not self._inBoard((py, px))) or board[py][px] == self.getEnemyColor(color):
                        # we ignore >=6 connections, we regards >=5 connections all win, if needs, add overline rule checking below:
                        # or (i + 1 == 5 and self._inBoard((py + dy * s, px + dx * s)) and  board[py + dy * s][ px + dx * s] == color):
                        break

                    elif s > 0:  # append to back if right of position
                        pathlist.append(board[py][px])
                    elif s < 0:  # insert to front if left of position
                        pathlist.insert(0, board[py][px])

            paths_num = len(pathlist) - 5 + 1  # number of ways you can make board.connect in a row using position

            if paths_num > 0:
                for i in range(paths_num):
                    path_score = pathlist[i:i + 5].count(color)
                    # if 4 connections we put extremely heavy weights; and if in attack mode weights much heavier
                    total_score += path_score ** 5 if path_score != 4 else 100 ** (9 if attack else 8)

        return total_score

    def getEnemyColor(self, myColor):
        '''

        :param myColor: (int) my current using color
        :return: (int) enemy's color

        '''
        if myColor == 1:
            return 2
        elif myColor == 2:
            return 1

    def _inBoard(self, (y, x)):
        """
        (y,x) : (int,int)
        return: bool

        Judge if a coordinates is inside pre-defined board
        """
        return 0 <= y < N and 0 <= x < N

    def evaluate_position(self, board, position):
        """
        board   : current chess map
        position: (y,x)
        return  : int

        Evaluate both defense value(attack for other side) and attack value
        of the candidate position. 
        Returns 0 is the position id not a valid move(the position is occupied)
        """
        if self._valid_move(board, position):
            return self._eval_func(board, position, True) + self._eval_func(board, position, False)
        else:
            return 0

    def _valid_move(self, board, pos):
        i, j = pos
        if board[i][j] == BoardState.EMPTY:
            return True
        else:
            return False

    def attackArea(self, (y, x), connect):
        """
        (y,x)  : (int,int)
        connect: int
        return : list of (int,int)

        Takes a coordinate, and returns a list of the coordinates
        within connect spaces of (y,x) that could be attacked by a
        Queen (in chess) sitting in space (y,x)
        """
        area = []
        for pair in ((1, 0), (0, 1), (1, 1), (1, -1)):
            (dy, dx) = pair
            for s in (1, -1):
                for i in range(1, connect):
                    py = y + dy * i * s
                    px = x + dx * i * s
                    area.append((py, px))
        return area

    def topMoves(self, board, limit):
        """
        board : current chess map
        limit : int
        return: list of (int,(int,int))

        Takes a board object, and returns
        the top 'limit' number of moves, as
        valued by evaluate_position()
        """
        top_queue = q.PriorityQueue()
        spots = set()

        blacks = self.__gomoku.black_occupied()  # list of coordinates that black took
        whites = self.__gomoku.white_occupied()  # list of coordinates that white took

        for pos in blacks + whites:
            for attack in self.attackArea(pos, 5):
                if self._inBoard(attack):
                    spots.add(attack)
        for s in spots:
            # * -1 as PriorityQueue queues the values from smallest, but
            # we want largest value on top, so * -1
            top_queue.put((self.evaluate_position(board, s) * (-1), s))

        toplist = []
        for x in range(limit):
            toplist.append(top_queue.get())

        return map(lambda (x, y): (-x, y), toplist)

    def justBestMoves(self, board, limit):
        """
        board : current chess map
        limit : int
        return: list of (int,int)

        The same as topMovs(), but returns only
        move(s) with highest value, and only moves returned
        """
        toplist = self.topMoves(board, limit)
        highest_value = toplist[0][0]
        best_move = []
        for val, move in toplist:
            if val == highest_value:
                best_move.append(move)
        return best_move


    def one_step(self, board, time_limit, dive=1):
        """
        board : current chess map, 2d list [[int]]
        time_limit: float
        dive  : int
        return: (int,int)

        Takes a board, a time limit, and a dive number, and
        implements quiescent search dive_#.
        Returns a move where quiescent search predicts a win, or
        the best move according to evalute_position()
        """

        checkTOP_ = 10
        checkDEPTH_ = 20
        moves_list = self.topMoves(board, checkTOP_)
        mehlist = []
        bahlist = []
        tfract = (time_limit - ((0.1) * (time_limit / 10 + 1))) / float(len(moves_list))

        for item in moves_list:
            (val, move) = item
            i, j = move
            nextboard = deepcopy(board)
            nextboard[i][j] = self.__currentState

            if self.__gomoku.connected_five(i, j, self.__currentState):
                self.__gomoku.set_chessboard_state(i, j, self.__currentState)
                print 'ai ' + str(self.__currentState) + ' moves on: (' + str(i) + ' ,' + str(j) + ') '
                return True

            if dive == 1:
                score = -self.dive_1(nextboard, checkDEPTH_ - 1)
            elif dive == 2:
                score = -self.dive_2(nextboard, checkDEPTH_ - 1)
            elif dive == 3:
                score = -self.dive_3(nextboard, checkDEPTH_ - 1, time.time(), tfract)
            elif dive == 4:
                score = -self.dive_4(nextboard, time.time(), tfract)
            elif dive == 5:
                score = -self.dive_5(nextboard, checkDEPTH_ - 1)

            if score == 1:
                self.__gomoku.set_chessboard_state(i, j, self.__currentState)
                print 'ai ' + str(self.__currentState) + ' moves on: (' + str(i) + ' ,' + str(j) + ') '
                return True
            elif score == 0:
                mehlist.append((score, move))
            elif score > -1:
                bahlist.append((score, move))

        if len(mehlist):
            i, j = mehlist[0][1]
            self.__gomoku.set_chessboard_state(i, j, self.__currentState)
            print 'ai ' + str(self.__currentState) + ' moves on: ('+str(i)+' ,'+str(j)+') '

            return True

        elif len(bahlist):
            bahlist.sort()
            i, j = bahlist[-1][1]
            self.__gomoku.set_chessboard_state(i, j, self.__currentState)
            print 'ai ' + str(self.__currentState) + ' moves on: ('+str(i)+' ,'+str(j)+') '
            return True

        else:
            i, j = moves_list[0][1]
            self.__gomoku.set_chessboard_state(i, j, self.__currentState)
            print 'ai ' + str(self.__currentState) + ' moves on: ('+str(i)+' ,'+str(j)+') '

            return True
        return False

    ########Different versions of quiescent searches below#######################


    def dive_1(self, board, dlimit):

        bestmove = self.topMoves(board, 1)[0][1]
        i, j = bestmove
        newboard = deepcopy(board)
        newboard[i][j] = self.__currentState
        if self.__gomoku.connected_five(i, j, self.__currentState):
            return 1
        elif not dlimit:
            return 0
        else:
            return -self.dive_1(newboard, dlimit - 1)

    def dive_2(self, board, dlimit):
        # board = self.__gomoku.get_chessMap()
        bestmoves = self.justBestMoves(board, 5)  # maybe widen this window?
        overall = 0.0
        split_factor = 1.0 / len(bestmoves)
        for bmove in bestmoves:
            i, j = bmove
            newboard = deepcopy(board)
            newboard[i][j] = self.__currentState

            if self.__gomoku.connected_five(i, j, self.__currentState):
                return 1
            elif not dlimit:
                continue
            else:
                score = -self.dive_2(newboard, dlimit - 1)
                if score == 1:
                    return 1
                else:
                    overall += split_factor * score
        return overall

    def dive_3(self, board, dlimit, start_tyme, tlimit):

        bestmove = self.topMoves(board, 1)[0][1]
        i, j = bestmove
        newboard = deepcopy(board)
        newboard[i][j] = self.__currentState

        if self.__gomoku.connected_five(i, j, self.__currentState):
            return 1
        elif time.time() - start_tyme > tlimit or not dlimit:
            return 0
        else:
            return -self.dive_3(newboard, dlimit - 1, start_tyme, tlimit)

    def dive_4(self, board, start_tyme, tlimit):

        bestmove = self.topMoves(board, 1)[0][1]
        i, j = bestmove
        newboard = deepcopy(board)
        newboard[i][j] = self.__currentState

        if self.__gomoku.connected_five(i, j, self.__currentState):
            return 1
        elif time.time() - start_tyme > tlimit:
            return 0
        else:
            return -self.dive_4(newboard, start_tyme, tlimit)

    def dive_5(self, board, dlimit):

        TOPCHECK = 3
        bestmoves = self.topMoves(board, TOPCHECK)
        overall = 0.0
        split_factor = 1.0 / len(bestmoves)
        for bmove in bestmoves:
            val,(i,j) = bmove
            newboard = deepcopy(board)
            newboard[i][j] = self.__currentState

            if self.__gomoku.connected_five(i, j, self.__currentState):
                return 1
            elif not dlimit:
                return 0
            else:
                score = -self.dive_5(newboard, dlimit - 1)
                if score == 1:
                    return 1
                elif not score:
                    return 0
                else:
                    overall += split_factor
        return overall
