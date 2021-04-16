#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Very simple tetris implementation
#
# Control keys:
#       Down - Drop stone faster
# Left/Right - Move stone
#         Up - Rotate Stone clockwise
#     Escape - Quit game
#          P - Pause game
#     Return - Instant drop
#
# Have fun!

# NOTE: If you're looking for the old python2 version, see
#       <https://gist.github.com/silvasur/565419/45a3ded61b993d1dd195a8a8688e7dc196b08de8>

# Copyright (c) 2010 "Laria Carolin Chabowski"<me@laria.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import operator

from pprint import pprint
from random import randrange as rand
import random
import pygame
import sys
import csv

from tetris_ai import TetrisAI

# The configuration
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
    # [[1, 1, 1],
    #  [0, 1, 0]],
    #
    # [[4, 0, 0],
    #  [4, 4, 4]],
    #
    # [[0, 0, 5],
    #  [5, 5, 5]],
    #
    # [[6, 6, 6]],
    [[1]],
    [[1, 1]],
    [[1, 1],
     [1, 1]],
    [[1, 1],
     [0, 1]]

]


def rotate_clockwise(shape):
    return [
        [shape[y][x] for y in range(len(shape))]
        for x in range(len(shape[0]) - 1, -1, -1)
    ]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[cy + off_y][cx + off_x]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [
        [0 for x in range(cols)]
        for y in range(rows)
    ]
    board += [[1 for x in range(cols)]]
    return board


class TetrisApp(object):
    def __init__(self, ai: TetrisAI):
        self.ai = ai
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.width = cell_size * (cols + 6)
        self.height = cell_size * rows
        self.rlim = cell_size * cols
        self.bground_grid = [[8 if x % 2 == y % 2 else 0 for x in range(cols)]
                             for y in range(rows)]

        self.default_font = pygame.font.Font(
            pygame.font.get_default_font(), 12)
        self.total_score = 0
        self.number_of_games = 0
        self.total_lines = 0

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.event.set_blocked(pygame.MOUSEMOTION)  # We do not need
        # mouse movement
        # events, so we
        # block them.
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(cols / 2 - len(self.stone[0]) / 2)
        self.stone_y = 0

        if check_collision(self.board,
                           self.stone,
                           (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1
        self.score = 0
        self.lines = 0
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

    def disp_msg(self, msg, topleft):
        x, y = topleft
        for line in msg.splitlines():
            self.screen.blit(
                self.default_font.render(
                    line,
                    False,
                    (255, 255, 255),
                    (0, 0, 0)),
                (x, y))
            y += 14

    def center_msg(self, msg):
        for i, line in enumerate(msg.splitlines()):
            msg_image = self.default_font.render(line, False,
                                                 (255, 255, 255), (0, 0, 0))

            msgim_center_x, msgim_center_y = msg_image.get_size()
            msgim_center_x //= 2
            msgim_center_y //= 2

            self.screen.blit(msg_image, (
                self.width // 2 - msgim_center_x,
                self.height // 2 - msgim_center_y + i * 22))

    def draw_matrix(self, matrix, offset):
        off_x, off_y = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(
                            (off_x + x) *
                            cell_size,
                            (off_y + y) *
                            cell_size,
                            cell_size,
                            cell_size), 0)

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level * 6:
            self.level += 1
            newdelay = 1000 - 50 * (self.level - 1)
            newdelay = 100 if newdelay < 100 else newdelay
            pygame.time.set_timer(pygame.USEREVENT + 1, newdelay)

    def move(self, delta_x):
        if not self.gameover and not self.paused:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > cols - len(self.stone[0]):
                new_x = cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def quit(self):
        self.center_msg("Exiting...")
        file = open('data.csv', 'w', newline='')
        with file:
            # identifying header
            header = ['state', 'action', 'q_value']
            writer = csv.DictWriter(file, fieldnames=header)

            # writing data row-wise into the csv file
            writer.writeheader()
            for key in self.ai.q_function_val:
                state = key[0]
                action = key[1]
                q_value = self.ai.q_function_val[key]
                writer.writerow({'state': state,
                                 'action': action,
                                 'q_value': q_value})

        print(self.total_score/self.number_of_games)
        print(self.total_lines/self.number_of_games)

        sys.exit()

    def drop(self, manual):
        if not self.gameover and not self.paused:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                    self.board,
                    self.stone,
                    (self.stone_x, self.stone_y))
                ai_board = self.board
                ai_board = [line for line in ai_board if any(line)]
                while len(ai_board) < 2:
                    ai_board.insert(0, [0, 0, 0, 0])

                ai_board = ai_board[: 2]
                ai_board = tuple(map(tuple, ai_board))

                # pprint(ai_board)
                ai_stone = tuple(map(tuple, self.next_stone))
                self.new_stone()

                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(
                                self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                self.add_cl_lines(cleared_rows)
                self.ai.state = (ai_board, ai_stone)
                return True
        return False

    def insta_drop(self):
        if not self.gameover and not self.paused:
            while (not self.drop(True)):
                pass

    def rotate_stone(self):
        if not self.gameover and not self.paused:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def start_game(self):
        if self.gameover:
            self.total_score  += self.score
            self.number_of_games += 1
            self.total_lines += self.lines
            self.ai.score = 0
            if self.ai.epsilon >= 0.05:
                # print(self.ai.epsilon)
                self.ai.epsilon -= 1.0/7500
            self.init_game()
            self.gameover = False

    def train(self):
        self.gameover = False
        self.paused = False

        key_actions = {
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': lambda: self.insta_drop(),
            'UP': self.rotate_stone,
            'SPACE': self.start_game
        }

        dont_burn_my_cpu = pygame.time.Clock()

        while 1:
            if self.number_of_games > 10000:
                self.quit()

            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.start_game()
            else:
                pygame.draw.line(self.screen,
                                 (255, 255, 255),
                                 (self.rlim + 1, 0),
                                 (self.rlim + 1, self.height - 1))
                self.disp_msg("Next:", (
                    self.rlim + cell_size,
                    2))
                self.disp_msg("Score: %d\n\nLevel: %d\
                    \nLines: %d" % (self.score, self.level, self.lines),
                              (self.rlim + cell_size, cell_size * 5))
                self.draw_matrix(self.bground_grid, (0, 0))
                self.draw_matrix(self.board, (0, 0))
                self.draw_matrix(self.stone,
                                 (self.stone_x, self.stone_y))
                self.draw_matrix(self.next_stone,
                                 (cols + 1, 2))
            pygame.display.update()

            p = random.random()
            if p < self.ai.epsilon:
                a = random.choice(self.ai.get_all_actions())
            else:
                keys = list(self.ai.q_function_val.keys())
                # for key in keys:
                # pprint(key[0][1])
                # pprint(tuple(map(tuple, self.stone)))
                # print(key[0][1] == tuple(map(tuple, self.stone)))
                # print()
                ai_board = self.board
                ai_board = [line for line in ai_board if any(line)]
                while len(ai_board) < 2:
                    ai_board.insert(0, [0, 0, 0, 0])

                ai_board = ai_board[: 2]
                ai_board = tuple(map(tuple, ai_board))
                keys = [key
                        for key in keys
                        if key[0][0] == ai_board and
                        key[0][1] == tuple(map(tuple, self.stone))
                        ]

                if len(keys) != 0:
                    new_dict = {key:self.ai.q_function_val[key] for key in keys}
                    best_key = max(new_dict.items(),
                                   key=operator.itemgetter(1))[0]
                    a = best_key[1]
                    print(new_dict[best_key])
                else:
                    a = random.choice(self.ai.get_all_actions())


            current_state = self.ai.state

            for key in a:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))

            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,
               key=pygame.K_DOWN))

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    # pprint(AI.q_function_val)
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                                             + key):
                            key_actions[key]()

            r = self.score - self.ai.score
            self.ai.score = self.score
            new_possible_actions = self.ai.get_all_actions()
            possible_next_q_values = []

            for action in new_possible_actions:
                # pprint(self.ai.state)
                # pprint(action)
                possible_next_q_values.append(
                    self.ai.q_function_val.get((self.ai.state, action), 0))
            self.ai.q_function_val[(current_state, a)] = r + self.ai.discount_factor * max(possible_next_q_values)

            # for key in self.ai.q_function_val:
            #
            # with open("sample.json", "w") as outfile:
            #     json.dump(self.ai.q_function_val, outfile, indent = 4)
            dont_burn_my_cpu.tick(30)

    def test(self):
        self.ai.import_q_function_data()
        self.gameover = False
        self.paused = False

        key_actions = {
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': lambda: self.insta_drop(),
            'UP': self.rotate_stone,
            'SPACE': self.start_game
        }

        dont_burn_my_cpu = pygame.time.Clock()

        while 1:
            if self.number_of_games > 100:
                self.quit()
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.start_game()
            else:
                pygame.draw.line(self.screen,
                                 (255, 255, 255),
                                 (self.rlim + 1, 0),
                                 (self.rlim + 1, self.height - 1))
                self.disp_msg("Next:", (
                    self.rlim + cell_size,
                    2))
                self.disp_msg("Score: %d\n\nLevel: %d\
                    \nLines: %d" % (self.score, self.level, self.lines),
                              (self.rlim + cell_size, cell_size * 5))
                self.draw_matrix(self.bground_grid, (0, 0))
                self.draw_matrix(self.board, (0, 0))
                self.draw_matrix(self.stone,
                                 (self.stone_x, self.stone_y))
                self.draw_matrix(self.next_stone,
                                 (cols + 1, 2))
            pygame.display.update()

            keys = list(self.ai.q_function_val.keys())
            # for key in keys:
                # pprint(key[0][1])
                # pprint(tuple(map(tuple, self.stone)))
                # print(key[0][1] == tuple(map(tuple, self.stone)))
                # print()
            ai_board = self.board
            ai_board = [line for line in ai_board if any(line)]
            while len(ai_board) < 2:
                ai_board.insert(0, [0, 0, 0, 0])

            ai_board = ai_board[: 2]
            ai_board = tuple(map(tuple, ai_board))
            keys = [key
                   for key in keys
                   if key[0][0] == ai_board and
                   key[0][1] == tuple(map(tuple, self.stone))
                   ]

            if len(keys) != 0:
                new_dict = {key: self.ai.q_function_val[key] for key in keys}
                best_key = max(new_dict.items(),
                               key=operator.itemgetter(1))[0]
                a = best_key[1]
                # print(new_dict[best_key])
            else:
                a = random.choice(self.ai.get_all_actions())
            # print(keys)
            # max(self.ai.q_function_val.items(), key=operator.itemgetter(1))[0]
            # current_state = self.ai.state

            for key in a:
                 pygame.event.post(
                     pygame.event.Event(pygame.KEYDOWN, key=key))

            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,
                                                 key=pygame.K_DOWN))

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                                             + key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(30)

    def random_test(self):
        self.gameover = False
        self.paused = False

        key_actions = {
            'LEFT': lambda: self.move(-1),
            'RIGHT': lambda: self.move(+1),
            'DOWN': lambda: self.insta_drop(),
            'UP': self.rotate_stone,
            'SPACE': self.start_game
        }

        dont_burn_my_cpu = pygame.time.Clock()

        while 1:
            if self.number_of_games > 100:
                self.quit()
            self.screen.fill((0, 0, 0))
            if self.gameover:
                self.start_game()
            else:
                pygame.draw.line(self.screen,
                                 (255, 255, 255),
                                 (self.rlim + 1, 0),
                                 (self.rlim + 1, self.height - 1))
                self.disp_msg("Next:", (
                    self.rlim + cell_size,
                    2))
                self.disp_msg("Score: %d\n\nLevel: %d\
                    \nLines: %d" % (self.score, self.level, self.lines),
                              (self.rlim + cell_size, cell_size * 5))
                self.draw_matrix(self.bground_grid, (0, 0))
                self.draw_matrix(self.board, (0, 0))
                self.draw_matrix(self.stone,
                                 (self.stone_x, self.stone_y))
                self.draw_matrix(self.next_stone,
                                 (cols + 1, 2))
            pygame.display.update()
            a = random.choice(self.ai.get_all_actions())
            for key in a:
                pygame.event.post(
                    pygame.event.Event(pygame.KEYDOWN, key=key))

            pygame.event.post(pygame.event.Event(pygame.KEYDOWN,
                                                 key=pygame.K_DOWN))

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.drop(False)
                elif event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_"
                                             + key):
                            key_actions[key]()

            dont_burn_my_cpu.tick(30)


if __name__ == '__main__':
    AI = TetrisAI()
    App = TetrisApp(AI)

    # App.train()
    # App.random_test()
    App.test()

