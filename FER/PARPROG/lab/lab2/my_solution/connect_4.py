from mpi4py import MPI
import board as bd
import numpy as np
import time


def connect_four_master(file_name=None):
    # print(bd.Board.board_from_file(file_name))
    # print(bd.Board.board_from_text(open(file_name).read()))
    # print(bd.Board((6, 7)))
    board = bd.Board.board_from_file(file_name)
    print(f"winner = {board.check_for_winner_after_move((3, 3))}")


def connect_four_worker():
    pass


if __name__ == "__main__":
    if MPI.COMM_WORLD.Get_rank() == 0:
        connect_four_master("igra.txt")
    else:
        connect_four_worker()
