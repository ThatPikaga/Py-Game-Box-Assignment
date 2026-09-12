# state_manager.py - Handles switching between menu, games, scoreboard, etc.
# Inspired by the Clear Code Pygame state machine tutorial

import pygame

class StateManager:
    # Holds all states and manages transitions

    def __init__(self, initial_state_name, states_dict):
        self.states = states_dict          # {name: instance}
        self.current_name = initial_state_name
        self.current = states_dict[initial_state_name]
        self.current.startup({})

    def change(self, state_name, persist=None):
        # Switch to a new state, optionally passing data
        if state_name not in self.states:
            print(f"  [StateManager] Unknown state '{state_name}' - staying put.")
            return

        self.current.cleanup()
        self.current_name = state_name
        self.current = self.states[state_name]
        self.current.startup(persist or {})

    def handle_event(self, event):
        self.current.handle_event(event)

    def update(self, dt):
        self.current.update(dt)

    def draw(self, surface):
        self.current.draw(surface)

    def check_transition(self):
        # If the current state signals it's done, perform the transition
        if self.current.done:
            self.change(self.current.next_state, self.current.persist)
