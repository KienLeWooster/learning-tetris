import pygame
import csv

cell_size = 18
cols = 8
rows = 16
maxfps = 30

colors = [
    (0, 0, 0),
    (255, 85, 85),
    (100, 200, 115),
    (120, 108, 245),
    (255, 140, 50),
    (50, 120, 52),
    (146, 202, 73),
    (150, 161, 218),
    (35, 35, 35)  # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

]


def new_board():
    board = [
        [0 for x in range(cols)]
        for y in range(2)
    ]
    return board


class TetrisAI:
    def __init__(self):
        initial_board = tuple(map(tuple, new_board()))
        print(initial_board)
        current_block = tuple([(1, 1, 1), (0, 1, 0)])
        self.score = 0
        self.discount_factor = 0.3
        self.state = (initial_board, current_block)
        self.action = []
        # A dictionary where the key is a tuple of the state and action and the
        #   key is its corresponding q-value
        self.q_function_val = {}
        self.epsilon = 1.0

    def get_all_actions(self):
        actions = []
        horizontal_size = len(self.state[1][0])
        possible_moves_left = 3
        possible_moves_right = 4

        for rotations in range(4):
            current_action = [
                pygame.K_UP
                for _ in range(rotations)]
            for i in range(possible_moves_left + 1):
                actions.append(tuple(current_action +
                               [pygame.K_LEFT
                                for _ in range(i)]
                               ))
            for i in range(possible_moves_right + 1):
                actions.append(tuple(current_action +
                               [pygame.K_RIGHT
                                for _ in range(i)]
                               ))
        return actions

    def import_q_function_data(self):
        with open('data.csv', 'r') as infile:
            csv_reader = csv.reader(infile)
            next(csv_reader)
            for row in csv_reader:
                row = list(map(eval, row))
                self.q_function_val[(row[0], row[1])] = row[2]
