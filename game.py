import pygame
from pygame.locals import *
from sys import exit
from render import GameRender
from gomoku_ai import *
from gomoku_ai_2 import *
import os
import ai_2

#run in terminal
if __name__ == '__main__': 
    gomoku = Gomoku()
    render = GameRender(gomoku)

    #change the AI here, bigger the depth stronger the AI


    #ai = gomokuAI(gomoku, BoardState.WHITE, 2)

   # ai2 = gomokuAI2(gomoku, BoardState.WHITE)
    ai = gomokuAI2(gomoku, BoardState.BLACK)
    ai2 = gomokuAI2(gomoku, BoardState.WHITE)





    result = BoardState.EMPTY

    #enable ai here
    enable_ai = True
    enable_ai2 = True


    #edit if ai plays first
    ai.first_step()

    result = gomoku.get_chess_result()
    board1 = gomoku.get_chessMap()
    render.change_state()
    while True:
        #ai vs ai section

        if enable_ai2:
            print 'now ai 2'
            ai2.one_step(board1,60,3)
           # ai2.one_step()
            print 'ai 2 finished'
            result = gomoku.get_chess_result()

            if result != BoardState.EMPTY:
                color = 'white' if result == BoardState.WHITE else 'black'
                print color, "wins"
                break
            if enable_ai:

                #ai.one_step()
                ai.one_step(board1, 60, 1)
                result = gomoku.get_chess_result()

                if result != BoardState.EMPTY:
                    color = 'white' if result == BoardState.WHITE else 'black'
                    print color, "wins"

                    break
            else:
                render.change_state()
            board1 = gomoku.get_chessMap()

        #pygame event, player vs. ai section
        for event in pygame.event.get():
            #exit

            if event.type == QUIT:

                exit()
            elif event.type ==  MOUSEBUTTONDOWN:
                #play a step
                if render.one_step():
                    result = gomoku.get_chess_result()
                else:
                    continue
                if result != BoardState.EMPTY:
                    break
                if enable_ai:

                    #ai.one_step()
                    ai.one_step(board1, 60, 3)

                    result = gomoku.get_chess_result()
                else:
                    render.change_state()
        
        #draw
        render.draw_chess()
        render.draw_mouse()

        if result != BoardState.EMPTY:
            render.draw_result(result)

        #update
        pygame.display.update()