# scoreboard.py — Scoreboard screen that shows saved stats per game
# Press T on the carousel to view stats; left/right to cycle games
# Stub for now — will load from data/*.py files

import pygame

class Scoreboard:
    def __init__(self):
        self.name = "SCOREBOARD"
        self.done = False
        self.next_state = None
        self.persist = {}
        self.font_title = None
        self.font_body = None

    def startup(self, persist):
        self.persist = persist
        self.done = False
        self.next_state = None
        self.font_title = pygame.font.Font(None, 42)
        self.font_body = pygame.font.Font(None, 28)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
            self.next_state = "MAIN_MENU"

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((5, 5, 15))
        t = self.font_title.render("SCOREBOARD", True, (255, 215, 0))
        surface.blit(t, (475 - t.get_width()//2, 100))
        s = self.font_body.render("Coming soon — stats tracking per game", True, (150, 150, 180))
        surface.blit(s, (475 - s.get_width()//2, 200))
        e = self.font_body.render("Press ESC to return", True, (150, 150, 180))
        surface.blit(e, (475 - e.get_width()//2, 500))

    def cleanup(self):
        pass
