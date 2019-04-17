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
import abc


class Control:
    '''Base class for graphic controls'''

    def __init__(self, rect, title, font, color):
        self.rect = rect
        self.title = title
        self.font = font
        self.color = color

    def is_point_in_rect(self, point):
        '''Returns true if point is in button's rect

        Arguments:
            point {list(int, int)} -- point, mostly mouse position

        Returns:
            bool
        '''

        if self.rect[0] <= point[0] <= self.rect[0] + self.rect[2] and \
           self.rect[1] <= point[1] <= self.rect[1] + self.rect[3]:
            return True

        return False

    @abc.abstractmethod
    def render(self, surface):
        '''Abstract rendering method'''
        pass


class Button(Control):
    '''Button control, basically rect with checking if user clicked it'''

    def __init__(self, rect, title, font, color):
        super().__init__(rect, title, font, color)

        self.lines = [[self.rect[0], self.rect[1]],
                      [self.rect[0] + self.rect[2], self.rect[1]],
                      [self.rect[0] + self.rect[2], self.rect[1] +
                       self.rect[3]],
                      [self.rect[0], self.rect[1] + self.rect[3]]]

        self.text = font.render(self.title, True, (255, 255, 255))
        text_rect = self.text.get_rect()
        self.final_text_rect = rect[:]
        self.final_text_rect[0] += (self.rect[2] - text_rect[2]) / 2
        self.final_text_rect[1] += (self.rect[3] - text_rect[3]) / 2
        self.final_text_rect[2] = text_rect[2]
        self.final_text_rect[3] = text_rect[3]

    def render(self, surface):
        '''Renders button on surface

        Arguments:
            surface {pygame.Surface} -- surface to render on
        '''

        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.lines(surface, (0, 0, 0), True, self.lines, 4)
        surface.blit(self.text, self.final_text_rect)


class Slider(Control):
    '''Slider control'''

    def __init__(self, rect, text_rect_shift, title, font, min_value,
                 max_value, default_value, step, color, slider_color):
        super().__init__(rect, title, font, color)

        self.slider_rect = self.rect[:]
        self.slider_rect[2] //= 4

        self.text_rect = self.rect[:]
        self.text_rect[0] += text_rect_shift[0]
        self.text_rect[1] += text_rect_shift[1]

        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.step = step

        self.slider_color = slider_color

        self.__set_starting_position()

    def __set_starting_position(self):
        '''Sets slider starting position'''
        slider_relative = (self.value - self.min_value) / \
                          (self.max_value - self.min_value)
        self.slider_rect[0] += slider_relative * \
            (self.rect[2] - self.slider_rect[2])

    def move_slider(self, shift):
        '''Moves slider by given shift

        Arguments:
            shift {list(int, int)}
        '''

        self.slider_rect[0] += shift[0]
        if self.slider_rect[0] < self.rect[0]:
            self.slider_rect[0] = self.rect[0]
        elif self.slider_rect[0] + self.slider_rect[2] > \
                self.rect[0] + self.rect[2]:
            self.slider_rect[0] = self.rect[0] + self.rect[2] - \
                self.slider_rect[2]

        slider_relative = ((self.rect[2] - self.slider_rect[2]) -
                           (self.slider_rect[0] - self.rect[0])) / \
            (self.rect[2] - self.slider_rect[2])

        self.value = int(
            self.min_value + (self.max_value - self.min_value) *
            (1.0 - slider_relative)) // \
            self.step * self.step

    def render(self, surface):
        '''Renders slider on surface

        Arguments:
            surface {pygame.Surface} -- surface to render on
        '''

        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.slider_color, self.slider_rect)
        title_text = self.font.render(self.title, True, (255, 255, 255))
        surface.blit(title_text, self.text_rect)
