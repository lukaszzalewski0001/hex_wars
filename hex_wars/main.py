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

import controls
import map
import game
import graphics
import events


class Main:
    '''
    Main object. It contains all most important object, like map, graphics,
    etc.
    '''

    def __init__(self):
        pygame.init()
        players = [game.Player((255, 0, 0))]

        resolution = pygame.display.Info()

        self.window_size = (resolution.current_w, resolution.current_h)

        self.map_ = map.Map((5, 5), 10, players, 4, 32, self.window_size)
        self.map_.create_map()

        self.gameplay = game.Gameplay(self.map_, 6, 2000, 8)
        self.graphics = graphics.Graphics(self.map_, self.gameplay,
                                          self.window_size)
        self.event_handler = events.EventHandler(self.map_, self.graphics,
                                                 self.gameplay)

    def play(self):
        '''Starts event loop'''
        self.event_handler.event_loop()

main = Main()
main.play()
