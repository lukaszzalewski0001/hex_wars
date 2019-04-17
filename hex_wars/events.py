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

import pygame
import sys

import map


class EventHandler:
    '''
    EventHandler object. This class containts communication with user and
    main game loop
    '''

    def __init__(self, map_, graphics, gameplay):
        self.map_ = map_
        self.graphics = graphics
        self.gameplay = gameplay

        self.last_mouse_pos = None
        self.last_mouse_pos_for_sliders = None
        self.slider_targeted = None

    def event_loop(self):
        '''Main event loop'''
        while True:
            self.handle_events()
            self.tick()

    # Events handling
    def handle_events(self):
        '''Handles user input'''
        for event in pygame.event.get():
            self.__check_event_game_close(event)

            self.__check_event_mouse(event)

            self.__check_event_human_turn(event)

    #
    # Nested event handling
    def __check_event_game_close(self, event):
        '''Checks if user wants to close the game'''
        if event.type == pygame.QUIT:
                sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit(0)

    def __check_event_mouse(self, event):
        '''Checks user input from mouse'''
        self.__check_event_mouse_button_down(event)
        self.__check_event_mouse_button_up(event)
        self.__check_event_mouse_motion(event)

    def __check_event_mouse_button_down(self, event):
        '''Checks if event was MOUSEBUTTONDOWN and then handles it'''
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for slider in self.graphics.sliders:
                    if slider.is_point_in_rect(pygame.mouse.get_pos()):
                        self.last_mouse_pos_for_sliders = \
                            pygame.mouse.get_pos()
                        self.slider_targeted = slider
                        break
                else:
                    if self.graphics.button_new_map.is_point_in_rect(
                     pygame.mouse.get_pos()):
                            self.graphics.set_options_for_new_map()
                            self.map_.create_map()
            elif event.button == 3:
                self.last_mouse_pos = pygame.mouse.get_pos()
            elif event.button == 4:
                self.map_.resize_polygons(self.map_.side_length + 2)
            elif event.button == 5:
                self.map_.resize_polygons(self.map_.side_length - 2)

    def __check_event_mouse_motion(self, event):
        '''Checks if event was MOUSEMOTION and then handles it'''
        if event.type == pygame.MOUSEMOTION:
            if self.last_mouse_pos:
                current_pos = pygame.mouse.get_pos()
                shift = [item1 - item2 for item1,
                         item2 in zip(current_pos, self.last_mouse_pos)]
                self.last_mouse_pos = current_pos
                self.map_.move_polygons(shift)
            elif self.last_mouse_pos_for_sliders:
                current_pos = pygame.mouse.get_pos()
                shift = [item1 - item2 for item1,
                         item2 in zip(current_pos,
                                      self.last_mouse_pos_for_sliders)]
                self.last_mouse_pos_for_sliders = current_pos
                self.slider_targeted.move_slider(shift)

    def __check_event_mouse_button_up(self, event):
        '''Checks if event was MOUSEBUTTONUP and then handles it'''
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.last_mouse_pos_for_sliders = None
                self.slider_targeted = None
            elif event.button == 3:
                self.last_mouse_pos = None

    def __check_event_human_turn(self, event):
        '''Checks if current player is human and handles input'''
        if self.gameplay.current_player_index == 0:
            self.__check_event_human_turn_keydown(event)
            self.__check_event_human_turn_mouse_button_down(event)

    def __check_event_human_turn_keydown(self, event):
        '''When human is playing checks if event was KEYDOWN and then handles it'''
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.gameplay.turn()
            elif event.key == pygame.K_a:
                self.map_.create_map()

    def __check_event_human_turn_mouse_button_down(self, event):
        '''
        When human is playing checks if event was MOUSEBUTTONDOWN and
        handles it
        '''

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for hex_ in list(self.map_.hex_map.flat):
                    if type(hex_) == map.Hex:
                        if hex_.is_point_inside_polygon(
                           pygame.mouse.get_pos()):
                            if hex_.player == self.map_.players[0] and \
                               hex_.dice_number > 1:
                                self.gameplay.attacking_hex = hex_
                            elif type(hex_.player) != \
                                self.map_.players[0] and \
                                self.gameplay.attacking_hex and \
                                    self.gameplay.is_hex_next_to_attacking_hex(
                                        hex_):
                                self.gameplay.defending_hex = hex_

    def tick(self):
        '''
        Handles everything that happens in main game loop besides user
        input
        '''

        self.gameplay.handle_ai()
        self.graphics.render()
        self.graphics.read_sliders_values()
        self.gameplay.fight_finish()
        self.gameplay.fight()
