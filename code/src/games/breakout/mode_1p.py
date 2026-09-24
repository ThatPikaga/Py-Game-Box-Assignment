# ======[ B R E A K O U T   --   1   P L A Y E R ]======
# single player breakout - smash all the bricks
# input uses the new handler so holding left then pressing right
# actually moves right without releasing left (same key-repeat fix as pong)

import pygame
import math as maths
import random
from src.core.game_base import GameBase
from src.core.constants import *
from src.engine.input_handler import GameKeyHandler
from src.games.breakout.blocks import create_grid
from src.games.breakout.powerups import PowerUp

class Breakout1PMode(GameBase):
    def __init__(self):
        super().__init__()
        self.name = "Breakout 1 Player"

        self.paddle = pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_W // 2,
                                   SCREEN_HEIGHT - 50, PADDLE_W, PADDLE_H)
        self.ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2,
                                 SCREEN_HEIGHT // 2, BALL_SIZE, BALL_SIZE)

        self.ball_speed_x = 4
        self.ball_speed_y = -4
        self.lives = 3
        self.score = 0
        self.bricks = []
        self.powerups = []

        # input handler — left/right with arrow keys OR A/D
        self.input = GameKeyHandler({
            "MOVE_LEFT":  pygame.K_LEFT,
            "MOVE_RIGHT": pygame.K_RIGHT,
            "MOVE_LEFT_ALT":  pygame.K_a,
            "MOVE_RIGHT_ALT": pygame.K_d,
        })

        self.font_title = title_font()
        self.font_body = body_font()

    def startup(self, persist):
        super().startup(persist)
        self.lives = 3
        self.score = 0
        self.powerups.clear()
        self.reset_ball()
        self._reset_bricks()
        self.input.clear()

    def _reset_bricks(self):
        brick_w = (SCREEN_WIDTH - (PADDING * (COLS + 1))) // COLS
        brick_h = 20
        self.bricks = create_grid(ROWS, COLS, brick_w, brick_h, OFFSET_TOP, PADDING)

    def reset_ball(self):
        self.ball.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.ball_speed_x = random.choice([-4, 4])
        self.ball_speed_y = -4
        self.paddle.width = PADDLE_W
        self.paddle.centerx = SCREEN_WIDTH // 2

    def handle_event(self, event):
        self.input.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_requested = True
        return None

    def update(self, dt):
        # =============== paddle movement (fixed: most-recent key held) =================
        active = self.input.get_active()
        if active in ("MOVE_LEFT", "MOVE_LEFT_ALT"):
            self.paddle.x -= PADDLE_MAX_SPEED
        elif active in ("MOVE_RIGHT", "MOVE_RIGHT_ALT"):
            self.paddle.x += PADDLE_MAX_SPEED

        self.paddle.left = max(0, self.paddle.left)
        self.paddle.right = min(SCREEN_WIDTH, self.paddle.right)

        # ball movement
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y

        # wall bounce (left/right walls)
        if self.ball.left <= 0 or self.ball.right >= SCREEN_WIDTH:
            self.ball_speed_x *= -1
            if self.ball.left <= 0: self.ball.left = 0
            else: self.ball.right = SCREEN_WIDTH

        # ceiling
        if self.ball.top <= 0:
            self.ball_speed_y *= -1
            self.ball.top = 0

        # ball fell off the bottom
        if self.ball.bottom >= SCREEN_HEIGHT:
            self.lives -= 1
            if self.sfx.get("life_lost"):
                try: self.sfx["life_lost"].play()
                except: pass
            if self.lives <= 0:
                self.lives = 0
                self.score = 0
                self._reset_bricks()
                self.powerups.clear()
            self.reset_ball()

        # paddle collision
        if self.ball.colliderect(self.paddle) and self.ball_speed_y > 0:
            self.ball.bottom = self.paddle.top
            pc = self.paddle.centerx
            bc = self.ball.centerx
            ri = bc - pc
            ni = ri / (self.paddle.width / 2)
            ni = max(-0.9, min(0.9, ni))
            self.ball_speed_x = ni * BOUNCE_SPEED
            self.ball_speed_y = -maths.sqrt(max(0, TOTAL_SPEED**2 - self.ball_speed_x**2))
            if self.sfx.get("padel_hit"):
                try: self.sfx["padel_hit"].play()
                except: pass

        # brick collision
        for brick in self.bricks:
            if brick.alive and self.ball.colliderect(brick):
                brick.alive = False
                self.score += brick.points

                # figure out which side we hit
                ol = self.ball.right - brick.left
                or_ = brick.right - self.ball.left
                ot = self.ball.bottom - brick.top
                ob = brick.bottom - self.ball.top
                mo = min(ol, or_, ot, ob)

                if mo == ol:
                    self.ball_speed_x *= -1
                    self.ball.right = brick.left
                elif mo == or_:
                    self.ball_speed_x *= -1
                    self.ball.left = brick.right
                elif mo == ot:
                    self.ball_speed_y *= -1
                    self.ball.bottom = brick.top
                elif mo == ob:
                    self.ball_speed_y *= -1
                    self.ball.top = brick.bottom

                if self.sfx.get("ball_obj_hit"):
                    try: self.sfx["ball_obj_hit"].play()
                    except: pass

                # chance to spawn a powerup
                if random.random() < 0.20:
                    self.powerups.append(
                        PowerUp(brick.centerx, brick.centery,
                                random.choice(['EXPAND','SHRINK','SLOW','FAST']))
                    )
                break

        # powerups
        for p in self.powerups[:]:
            p.update()
            if p.colliderect(self.paddle):
                if p.type == 'EXPAND':
                    self.paddle.width = min(200, self.paddle.width + 30)
                elif p.type == 'SHRINK':
                    self.paddle.width = max(60, self.paddle.width - 30)
                elif p.type == 'SLOW':
                    pass  # simplified — could adjust ball speed
                elif p.type == 'FAST':
                    pass
                if self.sfx.get("pwrUp_success"):
                    try: self.sfx["pwrUp_success"].play()
                    except: pass
                self.powerups.remove(p)
            elif p.top > SCREEN_HEIGHT:
                self.powerups.remove(p)

        # remove dead bricks
        self.bricks = [b for b in self.bricks if b.alive]

        # all bricks cleared — regenerate
        if not self.bricks:
            self._reset_bricks()
            self.reset_ball()

    def draw(self, surface):
        surface.fill(COL_BLACK)
        pygame.draw.rect(surface, COL_WHITE, self.paddle)
        pygame.draw.ellipse(surface, COL_WHITE, self.ball)

        for brick in self.bricks:
            pygame.draw.rect(surface, brick.colour, brick)

        for p in self.powerups:
            p.draw(surface)

        # HUD
        st = self.font_body.render(f"Score: {self.score}", True, COL_WHITE)
        surface.blit(st, (20, 15))
        lt = self.font_body.render(f"Lives: {self.lives}", True, COL_WHITE)
        surface.blit(lt, (SCREEN_WIDTH - 120, 15))

    def cleanup(self):
        self.input.clear()