'''
base_state.py — Parent class for all game/menu states
Provides standard interface so the state manager can treat everything the same
'''

import pygame

class BaseState:
    # Every game or menu screen inherits from this

    def __init__(self):
        self.name = "BaseState"
        self.done = False # set True when this state wants to quit
        self.next_state = None # name of the state to switch to
        self.persist = {} # data to pass between states (e.g. settings, assets)

    # Startup when state becomes active. Receive persisted data
    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None

    # Process a single pygame event
    def handle_event(self, event):
        pass

    # Tick logic. dt = milliseconds since last frame
    def update(self, dt):
        pass

    # Render to the main surface
    def draw(self, surface):
        pass

    # call before moving of from curent state
    def cleanup(self):
        pass
