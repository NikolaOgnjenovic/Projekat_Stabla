import copy

from BoardState import BoardState
from math import inf
import time


def nth_bit_set(number: int, n: int) -> bool:
    return (number & (1 << n)) == 0


# Used for storing values & positions of available moves for the bot
class Node:
    def __init__(self, position: int):
        self.children = []
        self.value = None
        self.position = position

    def add_child(self, node):
        self.children.append(node)


weights = [20, -3, 11, 8, 8, 11, -3, 20,
               -3, -7, -4, 1, 1, -4, -7, -3,
               11, -4, 2, 2, 2, 2, -4, 11,
               8, 1, 2, -3, -3, 2, 1, 8,
               8, 1, 2, -3, -3, 2, 1, 8,
               11, -4, 2, 2, 2, 2, -4, 11,
               -3, -7, -4, 1, 1, -4, -7, -3,
               20, -3, 11, 8, 8, 11, -3, 20
               ]
x_weights = [-1, -1, 0, 1, 1, 1, 0, -1]
y_weights = [0, 1, 1, 1, 0, -1, -1, -1]

# Piece difference, frontier disks and disk squares
def piece_difference(player_board: int, opponent_board: int) -> (float, float, float):
    player_tiles = 0
    opponent_tiles = 0
    player_front_tiles = 0
    opponent_front_tiles = 0
    d = 0
    for i in range(8):
        for j in range(8):
            if nth_bit_set(player_board, i * 8 + j):
                d += weights[i * 8 + j]
                player_tiles += 1
            elif nth_bit_set(opponent_board, i * 8 + j):
                d -= weights[i * 8 + j]
                opponent_tiles += 1

            if nth_bit_set(opponent_board, i * 8 + j) or nth_bit_set(player_board, i * 8 + j):
                for k in range(8):
                    x = i + x_weights[k]
                    y = j + y_weights[k]
                    if 0 <= x < 8 and 0 <= y < 8 and not (nth_bit_set(opponent_board, x * 8 + y) or nth_bit_set(player_board, x * 8 + i)):
                        if nth_bit_set(opponent_board, i * 8 + j):
                            player_front_tiles += 1
                        else:
                            opponent_front_tiles += 1
                        break
    if player_tiles > opponent_tiles:
        p = (100.0 * player_tiles) / (player_tiles + opponent_tiles)
    elif player_tiles < opponent_tiles:
        p = -(100.0 * opponent_tiles) / (player_tiles + opponent_tiles)
    else:
        p = 0

    if player_front_tiles > opponent_front_tiles:
        f = -(100.0 * player_front_tiles) / (player_front_tiles + opponent_front_tiles)
    elif player_front_tiles < opponent_front_tiles:
        f = (100.0 * opponent_front_tiles) / (player_front_tiles + opponent_front_tiles)
    else:
        f = 0

    return p, f, d


def corner_occupancy(player_board: int, opponent_board: int) -> float:
    player_tiles = opponent_tiles = 0
    if nth_bit_set(player_board, 0):
        player_tiles += 1
    elif nth_bit_set(opponent_board, 0):
        opponent_tiles += 1

    if nth_bit_set(player_board, 7):
        player_tiles += 1
    elif nth_bit_set(opponent_board, 7):
        opponent_tiles += 1

    if nth_bit_set(player_board, 21):
        player_tiles += 1
    elif nth_bit_set(opponent_board, 21):
        opponent_tiles += 1

    if nth_bit_set(player_board, 28):
        player_tiles += 1
    elif nth_bit_set(opponent_board, 28):
        opponent_tiles += 1

    return 25 * (player_tiles - opponent_tiles)


def corner_closeness(player_board: int, opponent_board: int) -> float:
    player_tiles = opponent_tiles = 0

    if not (nth_bit_set(opponent_board, 0) or nth_bit_set(player_board, 0)):
        if nth_bit_set(player_board, 1):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 1):
            opponent_tiles += 1

        if nth_bit_set(player_board, 4):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 4):
            opponent_tiles += 1

        if nth_bit_set(player_board, 3):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 3):
            opponent_tiles += 1

    if not (nth_bit_set(opponent_board, 7) or nth_bit_set(player_board, 7)):
        if nth_bit_set(player_board, 6):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 6):
            opponent_tiles += 1

        if nth_bit_set(player_board, 9):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 9):
            opponent_tiles += 1

        if nth_bit_set(player_board, 10):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 10):
            opponent_tiles += 1

    if not (nth_bit_set(opponent_board, 21) or nth_bit_set(player_board, 21)):
        if nth_bit_set(player_board, 22):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 22):
            opponent_tiles += 1

        if nth_bit_set(player_board, 19):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 19):
            opponent_tiles += 1

        if nth_bit_set(player_board, 18):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 18):
            opponent_tiles += 1

    if not (nth_bit_set(opponent_board, 28) or nth_bit_set(player_board, 28)):
        if nth_bit_set(player_board, 25):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 25):
            opponent_tiles += 1

        if nth_bit_set(player_board, 24):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 24):
            opponent_tiles += 1

        if nth_bit_set(player_board, 27):
            player_tiles += 1
        elif nth_bit_set(opponent_board, 27):
            opponent_tiles += 1

    return -12.5 * (player_tiles - opponent_tiles)


def mobility(board_state: BoardState, is_black: bool) -> float:
    player_tiles = len(board_state.get_available_moves(is_black))
    opponent_tiles = len(board_state.get_available_moves(is_black))

    if player_tiles > opponent_tiles:
        m = (100.0 * player_tiles) / (player_tiles + opponent_tiles)
    elif opponent_tiles < player_tiles:
        m = -(100.0 * opponent_tiles) / (player_tiles + opponent_tiles)
    else:
        m = 0

    return m


heuristic_hash: dict = {} # Hash map of already calculated table heuristic values

# Calculates the numerical value of the current state of the game
def heuristic(board_state: BoardState, is_black: bool) -> float:
    # If the heuristic for the current board state has already been calculated return it instead of calculating it
    global heuristic_hash
    board_hash = str(board_state.black_board) + ' ' + str(board_state.white_board)
    if heuristic_hash.__contains__(board_hash):
        return heuristic_hash.get(board_hash)

    # Call the heuristic functions with the black board as player_tiles and the white board as opponent_tiles
    if is_black:
        p, f, d = piece_difference(board_state.black_board, board_state.white_board)
        l = corner_closeness(board_state.black_board, board_state.white_board)
        c = corner_occupancy(board_state.black_board, board_state.white_board)
    # Call the heuristic functions with the white board as player_tiles and the black board as opponent_tiles
    else:
        p, f, d = piece_difference(board_state.white_board, board_state.black_board)
        l = corner_closeness(board_state.white_board, board_state.black_board)
        c = corner_occupancy(board_state.white_board, board_state.black_board)

    m = mobility(board_state, is_black)
    score = (10 * p) + (801.724 * c) + (382.026 * l) + (78.922 * m) + (74.396 * f) + (10.0 * d)
    heuristic_hash[board_hash] = score
    return score


class OpponentAI:
    board_state: BoardState

    is_black: bool
    max_depth: int
    end_time: float

    def __init__(self, is_black: bool):
        self.heuristic_hash = {}
        self.is_black = is_black
        self.max_depth = 20

    # Returns the position of the move that the bot will play or None if no moves are available
    def get_next_move(self, board_state: BoardState) -> int | None:
        root = Node(-1)

        if len(board_state.available_moves) == 0:
            return None

        for move in board_state.available_moves:
            root.add_child(Node(move))

        # Start looking for moves from the depth 4 upwards for 3 seconds
        depth = 4
        end_time = time.time() + 2.9
        self.end_time = end_time
        move = None
        while depth <= self.max_depth and time.time() < end_time:
            # Minimax each child
            for child in root.children:
                child.value = self.minimax(depth, True, -inf, inf, board_state, child.position)

            # If no moves are calculated, return None
            if len(root.children) < 1:
                return None

            # Pick a move with the best heuristic value
            move = root.children[0]
            for i in range(1, len(root.children)):
                if root.children[i].value > move.value:
                    move = root.children[i]

            depth += 1

        print('Max depth reached:', depth - 1)
        if move is not None:
            return move.position
        else:
            return None

    def minimax(self, depth: int, is_maximizer: bool, alpha: float, beta: float, state: BoardState, move_position: int) -> float:
        # Make a copy of the board state and make the given move on the copied board
        board_state = copy.deepcopy(state)
        board_state.make_move(move_position)

        if time.time() > self.end_time or depth < 1 or board_state.game_over:
            return heuristic(board_state, self.is_black)

        if is_maximizer:
            for move in board_state.available_moves:
                val = self.minimax(depth - 1, False, alpha, beta, board_state, move)

                alpha = max(alpha, val)
                if alpha >= beta:
                    return beta
            return alpha
        else:
            for move in board_state.available_moves:
                val = self.minimax(depth - 1, True, alpha, beta, board_state, move)

                beta = min(beta, val)
                if alpha >= beta:
                    return alpha
            return beta