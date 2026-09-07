import pygame
import sys
import math as maths
import random
from blocks import create_grid
from powerups import PowerUp

pygame.init()
clock = pygame.time.Clock()

# Screen
WIDTH, HEIGHT = 950, 950
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")

# colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Objects
PADDLE_WIDTH, PADDLE_HEIGHT = 120, 15
BALL_SIZE = 15

paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 50, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)

# Brick Configuration
ROWS = 6
COLS = 15
PADDING = 3
OFFSET_TOP = 60
BRICK_WIDTH = (WIDTH - (PADDING * (COLS + 1))) // COLS
BRICK_HEIGHT = 20

bricks = create_grid(ROWS, COLS, BRICK_WIDTH, BRICK_HEIGHT, OFFSET_TOP, PADDING)

# Speed & Vector (Based on my pong physics)
ball_speed_x = 4
ball_speed_y = -4
total_speed = 8
bounce_speed = total_speed - 1
paddle_speed = 0
paddle_max_speed = 8

# Game States
SCORE = 0
LIVES = 3
font = pygame.font.Font(None, 36)

powerups = []
powerup_types = ['EXPAND', 'SHRINK', 'SLOW', 'FAST']

def reset_ball():
    global ball_speed_x, ball_speed_y, total_speed
    ball.center = (WIDTH // 2, HEIGHT - 100)
    total_speed = 8
    ball_speed_x = random.choice([-4, 4])
    ball_speed_y = -4
    # Reset paddle
    paddle.width = PADDLE_WIDTH
    paddle.centerx = WIDTH // 2

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                paddle_speed = -paddle_max_speed
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                paddle_speed = paddle_max_speed
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                paddle_speed = 0

    # Move Paddle
    paddle.x += paddle_speed
    paddle.left = max(0, paddle.left)
    paddle.right = min(WIDTH, paddle.right)

    # Move Ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Wall Collisions (Left/Right/Top)
    if ball.left <= 0 or ball.right >= WIDTH:
        ball_speed_x *= -1
        if ball.left <= 0:
            ball.left = 0
        else:
            ball.right = WIDTH

    if ball.top <= 0:
        ball_speed_y *= -1
        ball.top = 0

    # Fall out of bounds
    if ball.bottom >= HEIGHT:
        LIVES -= 1
        if LIVES <= 0:
            # GAME RESTARS
            paddle.w
            LIVES = 0
            SCORE = 0
            bricks = create_grid(ROWS, COLS, BRICK_WIDTH, BRICK_HEIGHT, OFFSET_TOP, PADDING)
            powerups.clear()
        reset_ball()

    # Paddle Collision (With positional clipping to prevent passing through)
    if ball.colliderect(paddle) and ball_speed_y > 0:
        # 1. Reposition the ball to sit perfectly on top of the paddle
        ball.bottom = paddle.top
        
        # 2. Apply the Pong physics angle calculation
        paddle_center = paddle.centerx
        ball_center = ball.centerx
        rela_intersec_x = ball_center - paddle_center
        normalised_intersect = rela_intersec_x / (paddle.width / 2)
        
        # Clip normalisation to prevent extreme angles
        normalised_intersect = max(-0.9, min(0.9, normalised_intersect))
        
        ball_speed_x = normalised_intersect * bounce_speed
        ball_speed_y = -maths.sqrt(max(0, total_speed**2 - ball_speed_x**2))


    # Brick Collisions
    for brick in bricks:
        if brick.alive and ball.colliderect(brick):
            brick.alive = False
            SCORE += brick.points
            
            # Simple collision direction determination
            overlap_left = ball.right - brick.left
            overlap_right = brick.right - ball.left
            overlap_top = ball.bottom - brick.top
            overlap_bottom = brick.bottom - ball.top
            
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            # Bounce and explicitly push the ball out of the brick to prevent sticking
            if min_overlap == overlap_left:
                ball_speed_x *= -1
                ball.right = brick.left
            elif min_overlap == overlap_right:
                ball_speed_x *= -1
                ball.left = brick.right
            elif min_overlap == overlap_top:
                ball_speed_y *= -1
                ball.bottom = brick.top
            elif min_overlap == overlap_bottom:
                ball_speed_y *= -1
                ball.top = brick.bottom
                
            # Spawn Powerup
            if random.random() < 0.20:
                powerups.append(PowerUp(brick.centerx, brick.centery, random.choice(powerup_types)))
            break

    # Update & Check Powerups
    for p in powerups[:]:
        p.update()
        if p.colliderect(paddle):
            if p.type == 'EXPAND':
                paddle.width = min(200, paddle.width + 30)
            elif p.type == 'SHRINK':
                paddle.width = max(60, paddle.width - 30)
            elif p.type == 'SLOW':
                total_speed = max(5, total_speed - 2)
            elif p.type == 'FAST':
                total_speed = min(12, total_speed + 2)
            powerups.remove(p)
        elif p.top > HEIGHT:
            powerups.remove(p)

    # Clean dead bricks
    bricks = [b for b in bricks if b.alive]
    if not bricks:
        bricks = create_grid(ROWS, COLS, BRICK_WIDTH, BRICK_HEIGHT, OFFSET_TOP, PADDING)
        reset_ball()

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    
    for brick in bricks:
        pygame.draw.rect(screen, brick.colour, brick)
        
    for p in powerups:
        p.draw(screen)

    # Interface Text
    score_text = font.render(f"Score: {SCORE}", True, WHITE)
    screen.blit(score_text, (20, 15))
    lives_text = font.render(f"Lives: {LIVES}", True, WHITE)
    screen.blit(lives_text, (WIDTH - 120, 15))

    pygame.display.flip()
    clock.tick(60)
