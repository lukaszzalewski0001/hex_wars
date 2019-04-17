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

import ctypes
import pygame
import random

import controls
import game


class NewGameOptions:
    '''Options collected from sliders when creating new map'''

    def __init__(self, map_size, hex_number, players_number, die_sides_number,
                 max_dice_on_single_hex):
        self.map_size = list(map_size)
        self.hex_number = hex_number
        self.players_number = players_number
        self.die_sides_number = die_sides_number
        self.max_dice_on_single_hex = max_dice_on_single_hex


class Graphics:
    '''
    Graphics object. This class contains rendering functionality, controls
    etc.
    '''

    def __init__(self, map_, gameplay, window_size):
        ctypes.windll.user32.SetProcessDPIAware()

        self.map_ = map_
        self.gameplay = gameplay
        self.window_size = window_size
        self.surface = pygame.display.set_mode(self.window_size,
                                               pygame.FULLSCREEN)

        self.new_game_options = NewGameOptions(
                                    self.map_.size,
                                    self.map_.hex_number,
                                    len(self.map_.players),
                                    self.gameplay.die_sides_number,
                                    self.gameplay.max_dice_on_single_hex)

        self.__init_fonts()
        self.__init_right_bar()

    def __init_fonts(self):
        '''Initializes fonts'''
        self.font_bar_size = 32
        self.font_bar = pygame.font.SysFont(
                            'arial',
                            self.font_bar_size,
                            bold=1)
        self.font_sliders = pygame.font.SysFont('arial', 20, bold=1)

    def __init_right_bar(self):
        '''Initializes right bar and controls on it'''
        self.right_bar_units = (self.window_size[0] / 32,
                                self.window_size[1] / 32)

        self.right_bar_rect = (
            self.window_size[0] - (self.right_bar_units[0] * 8),
            0, self.right_bar_units[0] * 8, self.window_size[1])

        self.__init_hex_right_bar_representation()
        self.__init_controls()

    def __init_hex_right_bar_representation(self):
        '''Initializes choosen hex visual representation'''
        self.attacking_hex_representation_middle = (
            self.window_size[0] - self.right_bar_rect[2] +
            self.right_bar_units[0], self.right_bar_units[1] * 2)

        self.attacking_hex_representation_polygon = \
            self.map_.calculate_hex_polygon(
                self.attacking_hex_representation_middle)

        self.defending_hex_representation_middle = (
            self.window_size[0] - self.right_bar_units[0],
            self.right_bar_units[1] * 2)

        self.defending_hex_representation_polygon = \
            self.map_.calculate_hex_polygon(
                self.defending_hex_representation_middle)

        self.attacking_hex_power_representation_middle = \
            list(self.attacking_hex_representation_middle)

        self.attacking_hex_power_representation_middle[1] += \
            self.right_bar_units[1] * 4

        self.defending_hex_power_representation_middle = \
            list(self.defending_hex_representation_middle)
        self.defending_hex_power_representation_middle[1] += \
            self.right_bar_units[1] * 4

    def __init_controls(self):
        '''Initializes controls'''
        self.__init_sliders()
        self.__init_button()

    def __init_button(self):
        '''Initializes new map button'''
        self.button_new_map_rect = self.slider_max_dice_on_single_hex_rect[:]
        self.button_new_map_rect[0] += self.right_bar_units[0] * 1
        self.button_new_map_rect[1] += self.right_bar_units[1] * 2
        self.button_new_map_rect[2] -= self.right_bar_units[0] * 2
        self.button_new_map_rect[3] += self.right_bar_units[1] * 2
        self.button_new_map = controls.Button(
            self.button_new_map_rect, 'new map', self.font_sliders,
            (50, 50, 50))

    def __init_sliders(self):
        '''Initializes sliders'''
        self.sliders = []
        self.__init_slider_fight_time()
        self.__init_slider_map_size_x()
        self.__init_slider_map_size_y()
        self.__init_slider_hex_number()
        self.__init_slider_players_number()
        self.__init_slider_die_sides_number()
        self.__init_slider_max_dice_on_single_hex()

    def __init_slider_fight_time(self):
        '''Initializes slider responsible for fight time'''
        self.slider_fight_time_rect = \
            [self.right_bar_rect[0] + self.right_bar_units[0],
             self.right_bar_rect[1] + self.right_bar_units[1] * 10,
             self.right_bar_rect[2] - self.right_bar_units[0] * 2,
             self.right_bar_units[1] * 0.8]

        self.slider_fight_time = controls.Slider(
            self.slider_fight_time_rect, [0, -self.right_bar_units[1]],
            'fight time', self.font_sliders, 0, 5000,
            1000, 100, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_fight_time)

    def __init_slider_map_size_x(self):
        '''Initializes slider responsible for map size x'''
        self.slider_map_size_x_rect = self.slider_fight_time_rect[:]
        self.slider_map_size_x_rect[1] += self.right_bar_units[1] * 6
        self.slider_map_size_x = controls.Slider(
            self.slider_map_size_x_rect,
            [0, -self.right_bar_units[1]], 'map size x',
            self.font_sliders, 5, 100,
            10, 1, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_map_size_x)

    def __init_slider_map_size_y(self):
        '''Initializes slider responsible for map size y'''
        self.slider_map_size_y_rect = self.slider_map_size_x_rect[:]
        self.slider_map_size_y_rect[1] += self.right_bar_units[1] * 2
        self.slider_map_size_y = controls.Slider(
            self.slider_map_size_y_rect, 
            [0, -self.right_bar_units[1]], 'map size y',
            self.font_sliders, 5, 100,
            10, 1, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_map_size_y)

    def __init_slider_hex_number(self):
        '''Initializes slider responsible for hex number'''
        self.slider_hex_number_rect = self.slider_map_size_y_rect[:]
        self.slider_hex_number_rect[1] += self.right_bar_units[1] * 2
        self.slider_hex_number = controls.Slider(
            self.slider_hex_number_rect,
            [0, -self.right_bar_units[1]], 'hex number',
            self.font_sliders, 10, 100,
            25, 1, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_hex_number)

    def __init_slider_players_number(self):
        '''Initializes slider responsible for players number'''
        self.slider_players_number_rect = self.slider_hex_number_rect[:]
        self.slider_players_number_rect[1] += self.right_bar_units[1] * 2
        self.slider_players_number = controls.Slider(
            self.slider_players_number_rect,
            [0, -self.right_bar_units[1]], 'players number',
            self.font_sliders, 2, 20,
            2, 1, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_players_number)

    def __init_slider_die_sides_number(self):
        '''Initializes slider responsible for die sides number'''
        self.slider_die_sides_number_rect = self.slider_players_number_rect[:]
        self.slider_die_sides_number_rect[1] += self.right_bar_units[1] * 2
        self.slider_die_sides_number = controls.Slider(
            self.slider_die_sides_number_rect,
            [0, -self.right_bar_units[1]], 'die sides number',
            self.font_sliders, 2, 50,
            6, 1, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_die_sides_number)

    def __init_slider_max_dice_on_single_hex(self):
        '''Initializes slider responsible for max dice on single hex'''
        self.slider_max_dice_on_single_hex_rect = \
            self.slider_die_sides_number_rect[:]
        self.slider_max_dice_on_single_hex_rect[1] += \
            self.right_bar_units[1] * 2
        self.slider_max_dice_on_single_hex = controls.Slider(
            self.slider_max_dice_on_single_hex_rect,
            [0, -self.right_bar_units[1]], 'max dice on single hex',
            self.font_sliders, 2, 100,
            8, 1, (0, 0, 0), (255, 150, 0))

        self.sliders.append(self.slider_max_dice_on_single_hex)

    def set_options_for_new_map(self):
        '''Reads values from new game options and sets options for new map'''
        self.map_.size = self.new_game_options.map_size

        map_area = self.map_.size[0] * self.map_.size[1]
        self.map_.hex_number = int(
            self.new_game_options.hex_number / 100 * map_area)

        if self.new_game_options.players_number > self.map_.hex_number:
            self.new_game_options.players_number = self.map_.hex_number

        self.map_.players = []
        self.map_.players.append(game.Player((255, 0, 0)))
        for player in range(self.new_game_options.players_number - 1):
            self.map_.players.append(game.Player((
                random.randrange(40, 215),
                random.randrange(40, 215),
                random.randrange(40, 215))))

        self.gameplay.die_sides_number = self.new_game_options.die_sides_number

        self.gameplay.max_dice = self.new_game_options.max_dice_on_single_hex

    def read_sliders_values(self):
        '''Reads sliders values and saves them to new game options object'''
        self.gameplay.fight_time = self.slider_fight_time.value
        self.new_game_options.map_size[0] = self.slider_map_size_x.value
        self.new_game_options.map_size[1] = self.slider_map_size_y.value
        self.new_game_options.hex_number = self.slider_hex_number.value
        self.new_game_options.players_number = self.slider_players_number.value
        self.new_game_options.die_sides_number = \
            self.slider_die_sides_number.value
        self.new_game_options.max_dice_on_single_hex = \
            self.slider_max_dice_on_single_hex.value

    def render(self):
        '''Rendering'''
        self.surface.fill((0, 0, 0))

        self.__draw_visible_hexes()

        self.__draw_right_bar_hexes()

        self.__draw_right_bar_hexes_power()

        self.__draw_controls()

        pygame.display.flip()

    def __draw_visible_hexes(self):
        '''Draws all visible hexes'''
        font_dice_number_text_size = int(self.map_.side_length)
        font_dice_number_text = pygame.font.SysFont(
            'timesnewroman', font_dice_number_text_size, 1)

        for hex_ in self.map_.get_visibile_hex_list(self.right_bar_rect):
            if hex_ == self.gameplay.attacking_hex:
                pygame.draw.lines(self.surface, hex_.player.color, True, 
                                  hex_.polygon, 1)
            else:
                pygame.draw.polygon(self.surface, hex_.player.color, 
                                    hex_.polygon)

            dice_number_text = font_dice_number_text.render(
                str(hex_.dice_number), True, (255, 255, 255))

            self.surface.blit(dice_number_text, (
                hex_.middle[0] - font_dice_number_text_size / 4,
                hex_.middle[1] - font_dice_number_text_size / 2))

        pygame.draw.rect(self.surface, (40, 40, 40), self.right_bar_rect)

    def __draw_right_bar_hexes(self):
        '''Draws choosen hexes representation on right bar'''
        if self.gameplay.attacking_hex:
            pygame.draw.polygon(
                self.surface, 
                self.gameplay.attacking_hex.player.color,
                self.attacking_hex_representation_polygon)

            attacking_hex_text = self.font_bar.render(
                str(self.gameplay.attacking_hex.dice_number),
                True, (255, 255, 255))

            self.surface.blit(attacking_hex_text, (
                self.attacking_hex_representation_middle[0] -
                self.font_bar_size / 4,
                self.attacking_hex_representation_middle[1] -
                self.font_bar_size / 2))

        if self.gameplay.defending_hex:
            pygame.draw.polygon(
                self.surface,
                self.gameplay.defending_hex.player.color,
                self.defending_hex_representation_polygon)

            defending_hex_text = self.font_bar.render(
                str(self.gameplay.defending_hex.dice_number),
                True, (255, 255, 255))
            self.surface.blit(defending_hex_text, (
                self.defending_hex_representation_middle[0] -
                self.font_bar_size / 4,
                self.defending_hex_representation_middle[1] -
                self.font_bar_size / 2))

    def __draw_right_bar_hexes_power(self):
        '''Draws choosen hexes power representation on right bar'''
        if self.gameplay.attacking_hex_power:
            attacking_hex_power_text = self.font_bar.render(
                str(self.gameplay.attacking_hex_power), True,
                self.gameplay.attacking_hex.player.color)

            self.surface.blit(attacking_hex_power_text, (
                self.attacking_hex_power_representation_middle[0] -
                self.font_bar_size / 4,
                self.attacking_hex_power_representation_middle[1] -
                self.font_bar_size / 2))

        if self.gameplay.defending_hex_power:
            defending_hex_power_text = self.font_bar.render(
                str(self.gameplay.defending_hex_power), True,
                self.gameplay.defending_hex.player.color)

            self.surface.blit(defending_hex_power_text, (
                self.defending_hex_power_representation_middle[0] -
                self.font_bar_size / 4,
                self.defending_hex_power_representation_middle[1] -
                self.font_bar_size / 2))

    def __draw_controls(self):
        '''Draws controls'''
        for slider in self.sliders:
            slider.render(self.surface)

        self.button_new_map.render(self.surface)
