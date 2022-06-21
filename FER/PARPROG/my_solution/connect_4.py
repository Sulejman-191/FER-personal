from mpi4py import MPI
import board as bd
import numpy as np
import time


class Message:
    DATA = 1
    REQUEST = 2
    TASK = 3
    WAIT = 4
    RESULT = 5
    END = 6

    def __init__(self, msg_type, *args, **kwargs):
        self.msg_type = msg_type
        self.args = args
        self.kwargs = kwargs


def load_human_move(board):
    while True:
        print("Current state of the board:")
        print(board)
        text = input(f"Your move:")
        try:
            col = int(text)
            if col < 0 or col >= board.dim[1]:
                raise ValueError
            return col
        except ValueError:
            print(f"Your input must be a number between 0 and {board.dim[1]}. You inserted: {text}")


def connect_four_master(comm: MPI.Intracomm, file_name=None):
    num_of_processes = comm.Get_size()
    # print(bd.Board.board_from_file(file_name))
    # print(bd.Board.board_from_text(open(file_name).read()))
    # print(bd.Board((6, 7)))
    board = bd.Board.board_from_file(file_name)
    # print(f"winner = {board.check_for_winner_after_move((3, 3))}")

    while True:
        t_srt = time.time()
        tasks = set()

        non_zero_idx: tuple = np.nonzero(board.curr_state)
        print(non_zero_idx)
        untouched_columns = set(range(board.dim[1])) - set(non_zero_idx[1])

        for col in untouched_columns:
            tasks.add((board.dim[0] - 1, col))

        for x, y in zip(non_zero_idx[0], non_zero_idx[1]):
            if x > 0:
                tasks.add((x - 1, y))

        print(f"TASKS: ", tasks)

        for i in range(1, num_of_processes):
            comm.send(Message(Message.DATA, board=board), dest=i)

        results = {}
        num_of_workers = num_of_processes - 1
        while num_of_workers > 0:
            stat = MPI.Status()
            msg: Message = comm.recv(source=MPI.ANY_SOURCE, status=stat)
            src = stat.Get_source()

            if msg.msg_type == Message.REQUEST:

                if tasks:
                    task = tasks.pop()
                    comm.send(Message(Message.TASK, task=task), dest=src)
                else:
                    num_of_workers -= 1
                    comm.send(Message(Message.WAIT), dest=src)

            if msg.msg_type == Message.RESULT:
                results[msg.kwargs['task']] = msg.kwargs['result']
                # print(f"{src} returned {results}")

        # if 1 in results.values():
        #     print(f"{filter(lambda k, v: v == 1, results.items())}")
        best_move = None
        for key, val in results.items():
            if best_move is None or best_move[1] < val:
                best_move = (key, val)
        t_end = time.time()

        for key, value in results.items():
            print(f"Move {key} has quality of: {value}")
        print(f"Best move and value: {best_move}")
        print(f"Calculated in: {t_end - t_srt} sec")

        board.set_value_on_position(best_move[0], bd.Board.CPU)

        valid = False
        while valid:
            try:
                human_move = load_human_move(board)
                existing_position = set(filter(lambda k: k[1] == human_move, results.keys())).pop()
                human_position = (existing_position[0], human_move)
                print(f"Human position: {existing_position} {human_position}")
                board.set_value_on_position(human_position, bd.Board.HUMAN)
                valid = True
            except ValueError as v:
                print(v)


def connect_four_worker(comm: MPI.Intracomm, ):
    while True:
        msg = comm.recv(source=0)

        if msg.msg_type == Message.END:
            time.sleep(1)
            break

        board: bd.Board | None = None
        if msg.msg_type == Message.DATA:
            board = msg.kwargs['board']

        while True:
            comm.send(Message(Message.REQUEST), dest=0)

            msg = comm.recv(source=0)
            if msg.msg_type == Message.WAIT:
                break

            task = msg.kwargs['task']

            new_position = board.get_new_position(task[0], bd.Board.CPU)
            # print(f"new: ", new_position)
            winner = board.check_for_winner_after_move(new_position)
            board.set_value_on_position(new_position)

            if winner is not None:
                comm.send(Message(Message.RESULT, task=task, result=(1 if winner == bd.Board.CPU else -1)), dest=0)
                continue

            new_position = board.get_new_position(task[1], bd.Board.CPU)
            winner = board.check_for_winner_after_move(new_position)
            board.set_value_on_position(new_position)

            if winner is not None:
                comm.send(Message(Message.RESULT, task=task, result=(1 if winner == bd.Board.CPU else -1)), dest=0)
                continue

            # in depth
            comm.send(Message(Message.RESULT, task=task, result=np.random.rand(1)), dest=0)


if __name__ == "__main__":
    intracomm = MPI.COMM_WORLD
    if intracomm.Get_rank() == 0:
        connect_four_master(intracomm, )
    else:
        connect_four_worker(intracomm)
