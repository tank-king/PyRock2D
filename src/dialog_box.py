import abc
import sys

import pygame
from pygame.locals import *

from src.globals import Config, BaseStructure, Events, get_text
from src.ui import Button, UI


# import multiprocessing
# import atexit
# import signal


class DialogBox(BaseStructure):
    """
    Abstract class (needs to be inherited)
    """

    def __init__(self):
        # self.result_queue = multiprocessing.Queue()
        self._argc = 0
        self.window = pygame.display.get_surface()
        # self.exit_flag = multiprocessing.Event()
        self.running = True
        self.back = Button('Back', action=self.exit_dialog, topleft=[10, 10])

        # Set up signal handlers
        # TODO: this is not working properly at the moment, need to make sure child process gets closed
        # TODO: if parent process force stopped
        # signal.signal(signal.SIGTERM, self._signal_handler)
        # signal.signal(signal.SIGINT, self._signal_handler)

    # def _signal_handler(self, signum, frame):
    #     print(f"Received signal = {signum}, frame = {frame}. Setting exit flag.")
    #     self.exit_flag.set()

    def exit_dialog(self):
        self.running = False

    @abc.abstractmethod
    def get_caption(self):
        raise NotImplementedError

    def get_argc(self):
        return self._argc

    def get_result(self):
        return [None] * self.get_argc()

    # def return_result(self):
    #     self.result_queue.put(self.get_result())

    def _dialog_process(self):
        # pygame.init()
        self.running = True
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        # Pygame window settings
        # width, height = Config.DEFAULT_DIALOG_BOX_SIZE
        # screen = pygame.display.set_mode([width, height])
        # window = Window.from_display_module()
        # window.focus()
        # pygame.display.set_caption(self.get_caption())
        # screen = pygame.Surface([width, height])
        window = pygame.display.get_surface()
        clock = pygame.Clock()

        while self.running:
            mouse_hovered = False
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.type == Events.MOUSE_HOVERED:
                    mouse_hovered = True
                if event.type == pygame.WINDOWRESIZED:
                    Config.W, Config.H = event.x, event.y
                if mouse_hovered:
                    if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_HAND:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                else:
                    if pygame.mouse.get_cursor() != pygame.SYSTEM_CURSOR_ARROW:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            self.back.update(events, 1)
            self.update(events, 1)
            self.draw(window)
            self.back.draw(window)
            # self.draw(screen)
            # window.blit(screen, screen.get_rect(center=window.get_rect().center))
            pygame.display.update()
            clock.tick(60)
            # if self.exit_flag.is_set():
            #     running = False

    def draw(self, screen: pygame.Surface):
        screen.fill(Config.BG_COLOR)
        # rect = screen.get_rect(center=self.window.get_rect().center)
        # pygame.draw.rect(screen, 'red', rect)

    def show(self):
        self._dialog_process()
        return self.get_result()

    # def show_multiprocess(self):
    #     dialog_process = multiprocessing.Process(target=self._dialog_process)
    #     dialog_process.daemon = True
    #     dialog_process.start()
    #
    #     # wait until process complete
    #     dialog_process.join()
    #     return self.get_result()


class MessageBox(DialogBox):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def get_caption(self):
        return self.message

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        text = get_text(self.message, 'white', wraplength=int(Config.DEFAULT_DIALOG_BOX_SIZE[0] * 0.8))
        screen.blit(text, text.get_rect(center=screen.get_rect().center))


class CustomDialogBox(DialogBox):
    def __init__(self, message, **kwargs: UI):
        # expected kwargs to be of format -> {name:ui object}
        super().__init__()
        self.message = message
        self.objects = kwargs
        self.total_length = ...

    def get_caption(self):
        return self.message

    def get_result(self):
        return self.objects.values()

    def update(self, events: list[pygame.event.Event], dt):
        for _, i in self.objects.items():
            i.update(events, dt)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        padding = 25
        text = get_text(self.message, 'white', wraplength=int(Config.DEFAULT_DIALOG_BOX_SIZE[0] * 0.8))
        screen.blit(text, text.get_rect(center=[screen.get_width() // 2, text.get_height() // 2 + padding]))
        y = 100
        for i, j in self.objects.items():
            t = get_text(i + ":", 'white')
            rect = t.get_rect(topright=[screen.get_width() * 0.5 - padding, y])
            screen.blit(t, rect)
            obj = self.objects[i]
            obj.rect.topleft = [screen.get_width() * 0.5 + padding, rect.topleft[1]]
            y += max(rect.h, obj.rect.h) + padding / 2
        for _, i in self.objects.items():
            i.draw(screen)
