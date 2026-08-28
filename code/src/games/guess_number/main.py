import pygame
import random
import sys


pygame.init()

SCREEN_WIDTH = 650
SCREEN_HEIGHT = 500
FONT_NAME = "Arial"

COLOR_BG = (240, 244, 248)       
COLOR_CARD = (255, 255, 255)     
COLOR_TEXT_DARK = (30, 41, 59)   
COLOR_TEXT_MUTED = (100, 116, 139) 
COLOR_PRIMARY = (59, 130, 246)   
COLOR_PLAYER = (16, 185, 129)    
COLOR_AI = (239, 68, 68)         

# Setup Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Number Guesser Evolution")
clock = pygame.time.Clock()

# Fonts
font_title = pygame.font.SysFont(FONT_NAME, 32, bold=True)
font_body = pygame.font.SysFont(FONT_NAME, 20)
font_large = pygame.font.SysFont(FONT_NAME, 24, bold=True)

class NumberGuesserGame:
    def __init__(self):
        self.state = "MENU_MODE"
        self.mode = ""
        self.max_tries = 15
        self.player_tries = 15
        self.input_text = ""
        self.status_message = ""
        self.winner = ""
        
        self.btn_ai = pygame.Rect(125, 200, 180, 60)
        self.btn_local = pygame.Rect(345, 200, 180, 60)
        
        self.btn_easy = pygame.Rect(55, 220, 160, 60)
        self.btn_medium = pygame.Rect(245, 220, 160, 60)
        self.btn_hard = pygame.Rect(435, 220, 160, 60)
        
    def select_mode(self, chosen_mode):
        self.mode = chosen_mode
        self.state = "MENU_DIFFICULTY"

    def select_difficulty(self, allowed_tries):
        self.max_tries = allowed_tries
        self.player_tries = allowed_tries
        
        if self.mode == "GuessNumAi":
            self.secret_number = random.randint(1, 1000)
            self.status_message = "The AI has locked in a secret number! Guess it."
            self.state = "PLAYING"
        else:
            self.state = "COIN_FLIP"
            self.status_message = "Flipping a coin to decide who chooses the number..."
            self.coin_timer = pygame.time.get_ticks()

    def handle_coin_flip(self):
        self.p1_is_chooser = random.choice([True, False])
        self.chooser_name = "Player 1" if self.p1_is_chooser else "Player 2"
        self.guesser_name = "Player 2" if self.p1_is_chooser else "Player 1"
        self.status_message = f"It's {'Heads' if self.p1_is_chooser else 'Tails'}! {self.chooser_name} chooses the secret number."
        self.input_text = ""
        self.state = "SETTING_NUM"

    def handle_set_number(self):
        if not self.input_text:
            return
        try:
            num = int(self.input_text)
            if 1 <= num <= 1000:
                self.secret_number = num
                self.player_tries = self.max_tries
                self.input_text = ""
                self.status_message = f"Number locked! {self.guesser_name}, start guessing!"
                self.state = "PLAYING"
            else:
                self.status_message = "Enter a number between 1 and 1000!"
                self.input_text = ""
        except ValueError:
            self.input_text = ""

    def handle_guess(self):
        if not self.input_text:
            return
        try:
            guess = int(self.input_text)
        except ValueError:
            self.input_text = ""
            return

        if guess < 1 or guess > 1000:
            self.status_message = "Out of range! Guess between 1 and 1000."
            self.input_text = ""
            return

        self.player_tries -= 1
        curr_guesser = "Player" if self.mode == "GuessNumAi" else self.guesser_name

        if guess == self.secret_number:
            self.status_message = f"{curr_guesser} guessed {guess} and WON!"
            self.state = "GAME_OVER"
            self.winner = curr_guesser
        elif guess < self.secret_number:
            self.status_message = f"{curr_guesser} guessed {guess}. The secret number is HIGHER!"
        else:
            self.status_message = f"{curr_guesser} guessed {guess}. The secret number is LOWER!"

        if self.player_tries == 0 and self.state != "GAME_OVER":
            self.status_message = f"Game Over! Out of tries. The number was {self.secret_number}."
            self.state = "GAME_OVER"
            self.winner = "Nobody... you suck"

        self.input_text = ""

    def update(self):
        if self.state == "COIN_FLIP":
            if pygame.time.get_ticks() - self.coin_timer >= 1500:
                self.handle_coin_flip()

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # Title Card
        title_rect = pygame.Rect(30, 20, SCREEN_WIDTH - 60, 60)
        pygame.draw.rect(surface, COLOR_CARD, title_rect, border_radius=8)
        
        mode_label = f" ({self.mode})" if self.mode else ""
        title_text = font_title.render(f"Number Guesser{mode_label}", True, COLOR_TEXT_DARK)
        surface.blit(title_text, (title_rect.x + 20, title_rect.y + 12))

        if self.state == "MENU_MODE":
            prompt = font_large.render("Select Your Game Mode:", True, COLOR_TEXT_DARK)
            surface.blit(prompt, (50, 140))
            
            pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_ai, border_radius=6)
            pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_local, border_radius=6)
            
            ai_lbl = font_large.render("GuessNumAi", True, (255, 255, 255))
            loc_lbl = font_large.render("GuessNumLocal", True, (255, 255, 255))
            
            surface.blit(ai_lbl, (self.btn_ai.x + 22, self.btn_ai.y + 16))
            surface.blit(loc_lbl, (self.btn_local.x + 12, self.btn_local.y + 16))

        elif self.state == "MENU_DIFFICULTY":
            prompt = font_large.render("Select Game Difficulty:", True, COLOR_TEXT_DARK)
            surface.blit(prompt, (50, 140))
            
            pygame.draw.rect(surface, COLOR_PLAYER, self.btn_easy, border_radius=6)
            pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_medium, border_radius=6)
            pygame.draw.rect(surface, COLOR_AI, self.btn_hard, border_radius=6)
            
            easy_lbl = font_large.render("Easy (20)", True, (255, 255, 255))
            med_lbl = font_large.render("Medium (10)", True, (255, 255, 255))
            hard_lbl = font_large.render("Hard (5)", True, (255, 255, 255))
            
            surface.blit(easy_lbl, (self.btn_easy.x + 35, self.btn_easy.y + 16))
            surface.blit(med_lbl, (self.btn_medium.x + 20, self.btn_medium.y + 16))
            surface.blit(hard_lbl, (self.btn_hard.x + 40, self.btn_hard.y + 16))

        elif self.state == "COIN_FLIP":
            board_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 100)
            pygame.draw.rect(surface, COLOR_CARD, board_rect, border_radius=8)
            lbl = font_body.render(self.status_message, True, COLOR_TEXT_DARK)
            surface.blit(lbl, (board_rect.x + 20, board_rect.y + 38))

        elif self.state == "SETTING_NUM":
            board_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 140)
            pygame.draw.rect(surface, COLOR_CARD, board_rect, border_radius=8)
            
            lbl_title = font_large.render(self.status_message, True, COLOR_AI)
            lbl_warn = font_large.render("No peeking you sneaky beaky!", True, COLOR_AI)
            lbl_sub = font_body.render(f"{self.guesser_name}, close your eyes right now!", True, COLOR_TEXT_MUTED)
            
            surface.blit(lbl_title, (board_rect.x + 20, board_rect.y + 15))
            surface.blit(lbl_warn, (board_rect.x + 20, board_rect.y + 50))
            surface.blit(lbl_sub, (board_rect.x + 20, board_rect.y + 90))

            prompt = font_body.render("Type a secret number (1-1000) and press Enter:", True, COLOR_TEXT_DARK)
            surface.blit(prompt, (40, 280))

            input_box = pygame.Rect(40, 315, 200, 45)
            pygame.draw.rect(surface, COLOR_CARD, input_box, border_radius=5)
            pygame.draw.rect(surface, COLOR_PRIMARY, input_box, width=2, border_radius=5)
            
            hidden_display = "*" * len(self.input_text)
            val_text = font_large.render(hidden_display, True, COLOR_TEXT_DARK)
            surface.blit(val_text, (input_box.x + 15, input_box.y + 10))

        elif self.state in ["PLAYING", "GAME_OVER"]:
            board_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 150)
            pygame.draw.rect(surface, COLOR_CARD, board_rect, border_radius=8)

            if self.state == "GAME_OVER":
                turn_str = f"Winner: {self.winner}!" if self.winner != "Nobody" else "Game Over!"
                turn_color = COLOR_PLAYER if self.winner != "Nobody" else COLOR_TEXT_MUTED
            else:
                turn_str = "Your Turn to Guess" if self.mode == "GuessNumAi" else f"Turn: {self.guesser_name} Guessing"
                turn_color = COLOR_PLAYER

            lbl_turn = font_large.render(turn_str, True, turn_color)
            lbl_tries = font_body.render(f"Tries Remaining: {self.player_tries} / {self.max_tries}", True, COLOR_TEXT_DARK)
            lbl_status = font_body.render(self.status_message, True, COLOR_TEXT_MUTED)

            surface.blit(lbl_turn, (board_rect.x + 20, board_rect.y + 20))
            surface.blit(lbl_tries, (board_rect.x + 20, board_rect.y + 60))
            surface.blit(lbl_status, (board_rect.x + 20, board_rect.y + 100))

            if self.state == "PLAYING":
                prompt = font_body.render("Type your guess and press Enter:", True, COLOR_TEXT_DARK)
                surface.blit(prompt, (40, 290))

                input_box = pygame.Rect(40, 325, 200, 45)
                pygame.draw.rect(surface, COLOR_CARD, input_box, border_radius=5)
                pygame.draw.rect(surface, COLOR_PRIMARY, input_box, width=2, border_radius=5)

                val_text = font_large.render(self.input_text, True, COLOR_TEXT_DARK)
                surface.blit(val_text, (input_box.x + 15, input_box.y + 10))
            else:
                self.btn_reset = pygame.Rect(40, 320, 180, 50)
                pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_reset, border_radius=6)
                btn_text = font_large.render("Main Menu", True, (255, 255, 255))
                surface.blit(btn_text, (self.btn_reset.x + 35, self.btn_reset.y + 12))


game = NumberGuesserGame()

# Main Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if game.state == "MENU_MODE":
                if game.btn_ai.collidepoint(mouse_pos):
                    game.select_mode("GuessNumAi")
                elif game.btn_local.collidepoint(mouse_pos):
                    game.select_mode("GuessNumLocal")
                    
            elif game.state == "MENU_DIFFICULTY":
                if game.btn_easy.collidepoint(mouse_pos):
                    game.select_difficulty(20)
                elif game.btn_medium.collidepoint(mouse_pos):
                    game.select_difficulty(10)
                elif game.btn_hard.collidepoint(mouse_pos):
                    game.select_difficulty(5)
                    
            elif game.state == "GAME_OVER":
                if game.btn_reset.collidepoint(mouse_pos):
                    game.__init__()
                        
        elif event.type == pygame.KEYDOWN:
            if game.state in ["SETTING_NUM", "PLAYING"]:
                if event.key == pygame.K_RETURN:
                    if game.state == "SETTING_NUM":
                        game.handle_set_number()
                    else:
                        game.handle_guess()
                elif event.key == pygame.K_BACKSPACE:
                    game.input_text = game.input_text[:-1]
                else:
                    if event.unicode.isdigit() and len(game.input_text) < 3:
                        game.input_text += event.unicode

    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)
