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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scissors Paper Rock: Evolution")
clock = pygame.time.Clock()
font_title = pygame.font.SysFont(FONT_NAME, 32, bold=True)
font_body = pygame.font.SysFont(FONT_NAME, 20)
font_large = pygame.font.SysFont(FONT_NAME, 24, bold=True)

class SPRGame:
    def __init__(self):
        self.state = "MENU_MODE"
        self.mode = ""
        
        # Menu Selection Buttons
        self.btn_ai = pygame.Rect(125, 220, 180, 60)
        self.btn_local = pygame.Rect(345, 220, 180, 60)
        
        # AI Mode Mouse Click Buttons
        self.btn_scissors = pygame.Rect(55, 340, 160, 60)
        self.btn_paper = pygame.Rect(245, 340, 160, 60)
        self.btn_rock = pygame.Rect(435, 340, 160, 60)
        
        # Reset Button (Game Over State Only)
        self.btn_reset = pygame.Rect(235, 360, 180, 50)
        
        self.reset_round_variables()

    def reset_round_variables(self):
        self.p1_choice = ""
        self.p2_choice = ""
        self.status_message = ""
        self.winner_message = ""

    def select_mode(self, chosen_mode):
        self.mode = chosen_mode
        self.reset_round_variables()
        self.state = "PLAYING"
        if self.mode == "SPR_AI":
            self.status_message = "Click a button below to make your move against the AI!"
        else:
            self.status_message = "P1: Press A/W/D | P2: Press Left/Up/Right. Cover your hands!"

    def evaluate_winner(self, choice1, choice2, p2_name="AI"):
        if choice1 == choice2:
            self.winner_message = "It's a Draw!"
            self.status_message = f"Both picked {choice1}."
        elif (choice1 == "Scissors" and choice2 == "Paper") or \
             (choice1 == "Paper" and choice2 == "Rock") or \
             (choice1 == "Rock" and choice2 == "Scissors"):
            self.winner_message = "Player 1 Wins!"
            self.status_message = f"{choice1} beats {choice2}."
        else:
            self.winner_message = f"{p2_name} Wins!"
            self.status_message = f"{choice2} beats {choice1}."
        self.state = "GAME_OVER"

    def handle_ai_round(self, choice):
        self.p1_choice = choice
        self.p2_choice = random.choice(["Scissors", "Paper", "Rock"])
        self.evaluate_winner(self.p1_choice, self.p2_choice, "AI")

    def handle_local_key(self, key):
        # Player 1 Inputs
        if self.p1_choice == "":
            if key == pygame.K_a: self.p1_choice = "Scissors"
            elif key == pygame.K_w: self.p1_choice = "Paper"
            elif key == pygame.K_d: self.p1_choice = "Rock"
            
        # Player 2 Inputs
        if self.p2_choice == "":
            if key == pygame.K_LEFT: self.p2_choice = "Scissors"
            elif key == pygame.K_UP: self.p2_choice = "Paper"
            elif key == pygame.K_RIGHT: self.p2_choice = "Rock"

        # Once both options lock in, settle the score
        if self.p1_choice != "" and self.p2_choice != "":
            self.evaluate_winner(self.p1_choice, self.p2_choice, "Player 2")

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # Title Card
        title_rect = pygame.Rect(30, 20, SCREEN_WIDTH - 60, 60)
        pygame.draw.rect(surface, COLOR_CARD, title_rect, border_radius=8)
        mode_label = f" ({self.mode})" if self.mode else ""
        title_text = font_title.render(f"Scissors Paper Rock{mode_label}", True, COLOR_TEXT_DARK)
        surface.blit(title_text, (title_rect.x + 20, title_rect.y + 12))

        if self.state == "MENU_MODE":
            prompt = font_large.render("Select Your Game Mode:", True, COLOR_TEXT_DARK)
            surface.blit(prompt, (50, 140))
            
            pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_ai, border_radius=6)
            pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_local, border_radius=6)
            
            ai_lbl = font_large.render("SPR_AI", True, (255, 255, 255))
            loc_lbl = font_large.render("SPR_Local", True, (255, 255, 255))
            
            surface.blit(ai_lbl, (self.btn_ai.x + 50, self.btn_ai.y + 16))
            surface.blit(loc_lbl, (self.btn_local.x + 40, self.btn_local.y + 16))

        elif self.state == "PLAYING":
            if self.mode == "SPR_AI":
                board_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 180)
                pygame.draw.rect(surface, COLOR_CARD, board_rect, border_radius=8)
                
                lbl_top = font_large.render("Your Move", True, COLOR_PRIMARY)
                lbl_status = font_body.render(self.status_message, True, COLOR_TEXT_DARK)
                surface.blit(lbl_top, (board_rect.x + 20, board_rect.y + 25))
                surface.blit(lbl_status, (board_rect.x + 20, board_rect.y + 80))

                # Draw UI Interaction Buttons
                pygame.draw.rect(surface, COLOR_PLAYER, self.btn_scissors, border_radius=6)
                pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_paper, border_radius=6)
                pygame.draw.rect(surface, COLOR_AI, self.btn_rock, border_radius=6)
                
                surface.blit(font_large.render("Scissors", True, (255, 255, 255)), (self.btn_scissors.x + 38, self.btn_scissors.y + 16))
                surface.blit(font_large.render("Paper", True, (255, 255, 255)), (self.btn_paper.x + 50, self.btn_paper.y + 16))
                surface.blit(font_large.render("Rock", True, (255, 255, 255)), (self.btn_rock.x + 58, self.btn_rock.y + 16))
                
            else:
                board_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 240)
                pygame.draw.rect(surface, COLOR_CARD, board_rect, border_radius=8)
                
                lbl_warn = font_large.render("No peeking! Cover your selections!", True, COLOR_AI)
                lbl_joke = font_body.render("Play against your friend digitally because you obviously can't in real life.", True, COLOR_TEXT_MUTED)
                lbl_status = font_body.render(self.status_message, True, COLOR_TEXT_DARK)
                
                surface.blit(lbl_warn, (board_rect.x + 20, board_rect.y + 20))
                surface.blit(lbl_joke, (board_rect.x + 20, board_rect.y + 60))
                surface.blit(lbl_status, (board_rect.x + 20, board_rect.y + 105))

                # Status Tracker Indicators
                p1_ready = "Locked In!" if self.p1_choice else "Waiting for key (A, W, D)..."
                p2_ready = "Locked In!" if self.p2_choice else "Waiting for key (Left, Up, Right)..."
                
                surface.blit(font_body.render(f"Player 1 Status: {p1_ready}", True, COLOR_PLAYER if self.p1_choice else COLOR_TEXT_DARK), (board_rect.x + 20, board_rect.y + 155))
                surface.blit(font_body.render(f"Player 2 Status: {p2_ready}", True, COLOR_PLAYER if self.p2_choice else COLOR_TEXT_DARK), (board_rect.x + 20, board_rect.y + 195))

        elif self.state == "GAME_OVER":
            board_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 210)
            pygame.draw.rect(surface, COLOR_CARD, board_rect, border_radius=8)

            if "1" in self.winner_message: win_color = COLOR_PLAYER
            elif "2" in self.winner_message or "AI" in self.winner_message: win_color = COLOR_AI
            else: win_color = COLOR_TEXT_MUTED

            lbl_win = font_large.render(self.winner_message, True, win_color)
            lbl_p1 = font_body.render(f"Player 1 Selected: {self.p1_choice}", True, COLOR_TEXT_DARK)
            
            p2_label = "AI Selected" if self.mode == "SPR_AI" else "Player 2 Selected"
            lbl_p2 = font_body.render(f"{p2_label}: {self.p2_choice}", True, COLOR_TEXT_DARK)
            lbl_status = font_body.render(self.status_message, True, COLOR_TEXT_MUTED)

            surface.blit(lbl_win, (board_rect.x + 20, board_rect.y + 20))
            surface.blit(lbl_p1, (board_rect.x + 20, board_rect.y + 65))
            surface.blit(lbl_p2, (board_rect.x + 20, board_rect.y + 105))
            surface.blit(lbl_status, (board_rect.x + 20, board_rect.y + 155))

            # Draw Menu / Reset Button
            pygame.draw.rect(surface, COLOR_PRIMARY, self.btn_reset, border_radius=6)
            btn_text = font_large.render("Main Menu", True, (255, 255, 255))
            surface.blit(btn_text, (self.btn_reset.x + 35, self.btn_reset.y + 12))

game = SPRGame()

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
                    game.select_mode("SPR_AI")
                elif game.btn_local.collidepoint(mouse_pos):
                    game.select_mode("SPR_Local")
                    
            elif game.state == "PLAYING" and game.mode == "SPR_AI":
                if game.btn_scissors.collidepoint(mouse_pos):
                    game.handle_ai_round("Scissors")
                elif game.btn_paper.collidepoint(mouse_pos):
                    game.handle_ai_round("Paper")
                elif game.btn_rock.collidepoint(mouse_pos):
                    game.handle_ai_round("Rock")
                    
            elif game.state == "GAME_OVER":
                if game.btn_reset.collidepoint(mouse_pos):
                    game.__init__() # Resets back to mode select

        elif event.type == pygame.KEYDOWN:
            if game.state == "PLAYING" and game.mode == "SPR_Local":
                game.handle_local_key(event.key)

    game.update()
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)