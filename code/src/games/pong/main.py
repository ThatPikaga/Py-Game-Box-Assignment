import pygame
import sys
import math as maths
from ai import AI

pygame.init()
clock = pygame.time.Clock()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong with AI")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Objects
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_SIZE = 15

player = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Speed
player_speed = 0
player_max_speed = 9
ball_speed_x = 5
ball_speed_y = 5
total_speed = 8
bounce_speed = total_speed - 1


# AI
ai = AI(speed=5)

# Scores
player_score = 0
opponent_score = 0
font = pygame.font.Font(None, 74)

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_speed_x *= -1
    ball_speed_y *= -1



# Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player_speed = -player_max_speed
            if event.key == pygame.K_s:
                player_speed = player_max_speed
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                player_speed = 0

    # Move Player
    player.y += player_speed
    player.top = max(0, player.top)
    player.bottom = min(HEIGHT, player.bottom)

    # Move AI Opponent
    ai.move(opponent, ball)
    opponent.top = max(0, opponent.top)
    opponent.bottom = min(HEIGHT, opponent.bottom)

    # Move Ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Wall Collisions (Top/Bottom)
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1

    # Paddle Collisions
    for paddle in [player, opponent]:
        # Paddle Collisions
        if ball.colliderect(player) and ball_speed_x < 0:
            ball_speed_x *= -1
            paddle_center = player.centery
            ball_center = ball.centery
            rela_intersec_y = ball_center - paddle_center
            normalised_intersect = rela_intersec_y / (PADDLE_HEIGHT / 2)
            ball_speed_y = normalised_intersect * bounce_speed
            ball_speed_x = maths.sqrt(max(0, total_speed**2 - ball_speed_y**2))

        if ball.colliderect(opponent) and ball_speed_x > 0:
            ball_speed_x *= -1
            paddle_center = opponent.centery
            ball_center = ball.centery
            rela_intersec_y = ball_center - paddle_center
            normalised_intersect = rela_intersec_y / (PADDLE_HEIGHT / 2)
            ball_speed_y = normalised_intersect * bounce_speed
            ball_speed_x = -maths.sqrt(max(0, total_speed**2 - ball_speed_y**2))


    # Scoring
    if ball.left <= 0:
        opponent_score += 1
        reset_ball()
    if ball.right >= WIDTH:
        player_score += 1
        reset_ball()

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player)
    pygame.draw.rect(screen, WHITE, opponent)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Render Score
    player_text = font.render(str(player_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 4, 20))
    opponent_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(opponent_text, (3 * WIDTH // 4, 20))

    pygame.display.flip()
    clock.tick(60)
