'''
    Copyright 2019 Łukasz Zalewski.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import numpy
import math
import random


class Hex:
    '''Hex object'''

    def __init__(self, middle, polygon, player):
        self.middle = middle
        self.polygon = polygon
        self.player = player
        self.dice_number = 0

    def is_point_inside_polygon(self, point):
        '''Returns True if point is inside polygon else False

        Arguments:
            point {list(int, int)} -- point, mostly mouse position

        Returns:
            bool
        '''

        is_inside = False

        i = 0
        j = len(self.polygon) - 1

        while i < len(self.polygon):
            if ((
                self.polygon[i][1] > point[1]) !=
                (self.polygon[j][1] > point[1])) and \
                    (point[0] < (self.polygon[j][0]-self.polygon[i][0]) *
                        (point[1]-self.polygon[i][1]) /
                        (self.polygon[j][1]-self.polygon[i][1]) +
                        self.polygon[i][0]):
                is_inside = not is_inside

            j = i
            i += 1

        return is_inside


class Map:
    '''Map object'''

    # inits
    def __init__(self, size, hex_number, players, dice_per_hex,
                 default_side_length, window_size):
        self.size = size

        self.hex_number = hex_number

        self.hex_map = numpy.zeros([self.size[0], self.size[1]], dtype=Hex)

        self.players = players

        self.dice_per_hex = dice_per_hex
        self.dice_number = self.hex_number * self.dice_per_hex

        self.window_size = window_size

        self.pos_shift = [0, 0]

        self.default_side_length = default_side_length
        self.__init_side_lengths(default_side_length)

    def __init_side_lengths(self, side_length):
        '''Initializes attributes related to hex's side length

        Arguments:
            side_length {int} -- hex's side length
        '''

        self.side_length = side_length
        self.half_side_length = int(self.side_length / 2)
        self.half_side_length_root3 = int(self.half_side_length * math.sqrt(3))

    # creation and transformation of visual hex representation
    def __recalculate_hex_polygons(self):
        '''Recalculates all hex's middle points and polygons'''

        for i in range(self.hex_map.shape[0]):
            for j in range(self.hex_map.shape[1]):
                if type(self.hex_map[i, j]) == Hex:
                    hex_middle = self.__calculate_hex_middle((i, j))
                    hex_middle_shifted = [item1 + item2 for item1, item2 in
                                          zip(hex_middle, self.pos_shift)]
                    self.hex_map[i, j].middle = hex_middle_shifted
                    self.hex_map[i, j].polygon = \
                        self.calculate_hex_polygon(hex_middle_shifted)

    def __calculate_hex_middle(self, point):
        '''Calculates and returns hex's middle point coords

        Arguments:
            point {list(int, int)} -- hex's index in 2d array representation
                of map

        Returns:
            [list(int, int)] -- hex's middle point coords
        '''

        hex_middle = [0, 0]

        hex_middle[0] += self.half_side_length_root3
        hex_middle[1] += self.side_length

        hex_middle[0] += (point[0] * 2*self.half_side_length_root3)
        hex_middle[0] += (point[1] * self.half_side_length_root3)
        hex_middle[1] += (point[1] *
                          (self.half_side_length + self.side_length))

        return hex_middle

    def calculate_hex_polygon(self, hex_middle):
        '''Calculates and returns hex's polygon

        Arguments:
            hex_middle {list(int, int)} -- hex's middle point coords

        Returns:
            list(list(int, int)) -- list of points building hex's polygon
        '''

        polygon = (
            (hex_middle[0], hex_middle[1] + self.side_length),
            (hex_middle[0] + self.half_side_length_root3,
             hex_middle[1] + self.half_side_length),
            (hex_middle[0] + self.half_side_length_root3,
             hex_middle[1] - self.half_side_length),
            (hex_middle[0], hex_middle[1] - self.side_length),
            (hex_middle[0] - self.half_side_length_root3,
             hex_middle[1] - self.half_side_length),
            (hex_middle[0] - self.half_side_length_root3,
             hex_middle[1] + self.half_side_length))

        return polygon

    def resize_polygons(self, side_length):
        '''Changes hex's side length and related attributes, then resizes hex's polygon

        Arguments:
            side_length {int} -- hex's side length
        '''

        if side_length >= 6 and side_length <= 60:
            self.__init_side_lengths(side_length)
            self.__recalculate_hex_polygons()

    def move_polygons(self, pos_shift):
        '''Moves hex's polygon by given shift

        Arguments:
            pos_shift {list(int, int)} -- position shift
        '''

        self.pos_shift = [item1 + item2 for item1, item2 in
                          zip(self.pos_shift, pos_shift)]

        self.__recalculate_hex_polygons()

    # map creation
    def __side_to_point_diff(self, side, point):
        '''If move in given direction is possible returns moved point else
               returns unchanged point

        Arguments:
            side {int} -- where to move (0 .. 5)
            point {list(int, int)} -- point (index on hex's 2darray map) to
                move

        Returns:
            [list(int, int)] -- moved point
        '''

        point_ = point[:]

        if side == 0:
            point_[1] += 1
        elif side == 1:
            point_[0] += 1
        elif side == 2:
            point_[0] += 1
            point_[1] -= 1
        elif side == 3:
            point_[1] -= 1
        elif side == 4:
            point_[0] -= 1
        elif side == 5:
            point_[0] -= 1
            point_[1] += 1

        if self.__is_point_on_map(point_):
            return point_

        return point

    def __is_point_on_map(self, point):
        '''Returns True if point is in map's boundaries else False

        Arguments:
            point {list(int, int)} -- point (index on hex's 2d array map)

        Returns:
            [bool]
        '''

        if (point[0] < 0 or point[0] >= self.size[0]) or (point[1] < 0 or
           point[1] >= self.size[1]):
            return False

        return True

    #
    # hexes and dice distribution
    def __create_hex_distribution_list(self):
        '''Returns list with number of hexes per player. Each element
               corresponds to player in players list

        Returns:
            list(int) -- list with number of hexes per player
        '''

        hex_per_player = self.hex_number // len(self.players)
        hex_distribution_list = [hex_per_player] * len(self.players)

        for hex_left in range(self.hex_number % len(self.players), 0, -1):
            while True:
                hex_choosen = random.randrange(len(hex_distribution_list))
                if hex_distribution_list[hex_choosen] == hex_per_player:
                    hex_distribution_list[hex_choosen] += 1
                    break

        return hex_distribution_list

    def __choose_player(self, hex_distribution_list):
        '''Chooses player from list

        Arguments:
            hex_distribution_list {list(int)} -- list with number of nexes per
                player

        Returns:
            int -- player index
        '''

        while True:
            player = random.randrange(len(self.players))
            if hex_distribution_list[player] > 0:
                hex_distribution_list[player] -= 1
                return player

    def __create_dice_distribution_list(self):
        '''Returns list with number of dice per hex. Each element corresponds to hex on
        flat 2d array map representation

        Returns:
            list(int) -- list with number of dice per hex
        '''

        dice_left = 0
        dice_distribution_list = [0] * self.hex_number

        for hex_ in range(len(dice_distribution_list)):
            dice_number = random.randrange(self.dice_per_hex - 2,
                                           self.dice_per_hex + 1)
            dice_left += self.dice_per_hex - dice_number
            dice_distribution_list[hex_] = dice_number

        for die in range(dice_left):
            while True:
                hex_choosen = random.randrange(self.hex_number)
                if dice_distribution_list[hex_choosen] < self.dice_per_hex + 2:
                    dice_distribution_list[hex_choosen] += 1
                    break

        return dice_distribution_list

    def __is_dice_distribution_fair(self, dice_distribution_list,
                                    fair_variation):
        '''Returns True if variation between lowest and highest dice number if
               smaller than fair_variation, otherwise returns False

        Arguments:
            dice_distribution_list {list(int)} -- list with number of dice per
                hex
            fair_variation {float} -- maximum variation (between 0.2 and 0.4)

        Returns:
            bool
        '''

        if not (0.2 <= fair_variation <= 0.4):
            raise Exception('fair_variation isn\'t in range')

        players_dice_number = {}
        hex_list = [hex_ for hex_ in list(self.hex_map.flat) if type(hex_) ==
                    Hex]

        for hex_number in range(len(dice_distribution_list)):
            player = hex_list[hex_number].player
            if player in players_dice_number:
                players_dice_number[player] += dice_distribution_list[
                    hex_number]
            else:
                players_dice_number[player] = dice_distribution_list[
                    hex_number]

        min_ = min(players_dice_number.values())
        max_ = max(players_dice_number.values())
        average = sum(players_dice_number.values()) / len(players_dice_number)

        if (average / min_ > 1.0 + fair_variation) or (average / max_ < 1.0 -
           fair_variation):
            return False

        return True

    def __distribute_dice_to_hexes(self, dice_distribution_list):
        '''Distributes dice to hexes

        Arguments:
            dice_distribution_list {list(int)} -- list with dice number per hex
        '''

        hex_list = [hex_ for hex_ in list(self.hex_map.flat) if type(hex_) ==
                    Hex]

        for hex_ in range(len(dice_distribution_list)):
            hex_list[hex_].dice_number += dice_distribution_list[hex_]

    #
    # main map creation
    def create_map(self):
        '''
        Initializes hex's 2d array map with hex's objects.
        Distributes hexes to players and dice to hexes
        '''

        self.pos_shift = [0, 0]

        self.hex_map = numpy.zeros([self.size[0], self.size[1]], Hex)

        hex_distribution_list = self.__create_hex_distribution_list()

        point = [random.randrange(self.size[0]), random.randrange(self.size[1])]

        i = 0
        while i < self.hex_number:
            point = self.__side_to_point_diff(random.randrange(6), point)
            if not self.hex_map[point[0], point[1]]:
                hex_middle = self.__calculate_hex_middle(point)
                self.hex_map[point[0], point[1]] = Hex(
                    hex_middle,
                    self.calculate_hex_polygon(hex_middle),
                    self.players[self.__choose_player(hex_distribution_list)])
                i += 1

        while True:
            dice_distribution_list = self.__create_dice_distribution_list()
            if self.__is_dice_distribution_fair(dice_distribution_list, 0.3):
                break

        self.__distribute_dice_to_hexes(dice_distribution_list)

    # etc
    def get_visibile_hex_list(self, right_bar_rect):
        '''Returns list of hexes in visibility range

        Arguments:
            right_bar_rect {list(int)}

        Returns:
            [list(Hex)] -- list of hexes in visibility range
        '''

        hex_list = []
        for i in range(self.hex_map.shape[0]):
            for j in range(self.hex_map.shape[1]):
                if type(self.hex_map[i, j]) == Hex:
                    if ((i) * 2 * self.half_side_length_root3 +
                        self.pos_shift[0]) + \
                         ((j) * self.half_side_length_root3) <= \
                         right_bar_rect[0]:
                            if (j * (self.side_length +
                                self.half_side_length)) + \
                                 self.pos_shift[1] <= self.window_size[1]:
                                hex_list.append(self.hex_map[i, j])

        return hex_list
