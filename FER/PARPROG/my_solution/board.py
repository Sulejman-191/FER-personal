import numpy as np
from collections import Counter
import operator


class Board:

    CPU = 1
    HUMAN = 2

    def __init__(self, board_dim=(6, 7), initial_position: list | np.ndarray = None):
        if np.shape(board_dim) != (2,):
            raise Exception('Board must be 2D')
        self.dim = board_dim
        self.curr_state = np.zeros(board_dim, dtype=int) if initial_position is None else initial_position
        self.verbose = True

    def __repr__(self):
        # result = " | ".join(range(self.dim[1]))
        result = np.array2string(self.curr_state)
        return result

    def check_for_winner_after_move(self, position: tuple):
        print(f"checking board:\n", self.curr_state) if self.verbose else None
        if np.shape(position) != (2,):
            raise Exception('Position must have two integers')

        if Board.is_out_of_bounds(self.dim, position):
            raise Exception("Position out of bounds")

        # check horizontal
        tmp_res = self._is_winning_list(
            self.curr_state[position[0], max(position[1] - 3, 0): min(position[1] + 4, self.dim[1])],
            verbose=self.verbose)

        if tmp_res is not None:
            print(f"horizontal WINNER {tmp_res}") if self.verbose else None
            return tmp_res

        # check vertical
        tmp_res = self._is_winning_list(
            self.curr_state[position[0]: min(position[0] + 4, self.dim[0]), position[1]],
            verbose=self.verbose)

        if tmp_res is not None:
            return tmp_res

        # check main diagonal
        tmp_res = self._is_winning_list(self._get_diagonal(position), verbose=self.verbose)

        if tmp_res is not None:
            return tmp_res

        # check secondary diagonal
        tmp_res = self._is_winning_list(self._get_diagonal(position, main=False), verbose=self.verbose)

        if tmp_res is not None:
            return tmp_res

        return None

    def _get_diagonal(self, position: tuple, main=True):
        tmp = []
        for i in range(-3, 4, 1):
            # print(f"tuple={tuple(map(operator.add, position, (i if main else -i, i)))}") if self.verbose else None
            tmp_position = tuple(map(operator.add, position, (i if main else -i, i)))
            if not Board.is_out_of_bounds(self.dim, tmp_position):
                tmp.append(self.curr_state[tmp_position])
        return np.array(tmp)

    def get_new_position(self, column_idx, player_id: int = None):

        if column_idx < 0 or column_idx > self.dim[1]:
            raise Exception(f"Trying to play a move outside the board. Tried column={column_idx}, while dim={self.dim}")
        column = self.curr_state[:, column_idx]
        if len(np.nonzero(column)[0]):
            idx = min(np.nonzero(column)[0])
        else:
            idx = self.dim[0] - 1

        print(f"new_pos={idx, column_idx}") if self.verbose else None
        if idx < 1:
            raise Exception("Column is full: ", column)

        if player_id is not None:
            self.set_value_on_position((idx, column_idx), player_id)
        return idx, column_idx

    def set_value_on_position(self, position: tuple, value=0):
        if np.shape(position) != (2,):
            raise Exception('Position must have two integers')
        if self.curr_state[position] != 0 and value != 0:
            raise ValueError(f"Something is already on position: {position}")
        self.curr_state[position] = value
        print(f"Board after change ({position}, {value})\n{self.curr_state}") if self.verbose else None

    @staticmethod
    def _is_winning_list(arr: list | np.ndarray, verbose=False):
        print(f"checking: {arr}") if verbose else None
        ca = Counter(arr)
        if ca[0]:
            del ca[0]  # delete neutral element: 0
        if any(v >= 4 for v in ca.values()):  # are there 4 same values in the list
            return Board._check_if_four_consecutive(arr)

    @staticmethod
    def _check_if_four_consecutive(arr: list):
        for i, j, x, y in zip(arr, arr[1:], arr[2:], arr[3:]):
            if i == j == x == y and i != 0:  # neutral element can't be winner
                return i

    @staticmethod
    def is_out_of_bounds(bounds: tuple, position: tuple):
        return position[0] < 0 or position[1] < 0 or position[0] >= bounds[0] or position[1] >= bounds[1]

    @staticmethod
    def board_from_text(text: str):
        """

        :param text: string where first line is two numbers which represent num of rows and columns and all other
        rows are state of the game represented by integers
        :return: Board
        """
        if not text:
            return Board()
        lines = text.strip().split('\n')
        return Board(tuple(np.fromstring(lines[0], dtype=int, sep=' ')),
                     np.array([(np.fromstring(line, dtype=int, sep=' ')).tolist() for line in lines[1:]]))

    @staticmethod
    def board_from_file(file_name: str):
        """

        :param file_name: name of the file to convert to board. first line is two numbers which represent num of rows
        and columns and all other rows are state of the game represented by integers
        :return: Board
        """
        if not file_name:
            return Board()
        return Board(tuple(np.loadtxt(file_name, max_rows=1, dtype=int)), np.loadtxt(file_name, skiprows=1, dtype=int))
