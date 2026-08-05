# Major Project Documentation – PyArcade

---

## Proposal

### Client
Casual gamers who enjoy classic pick‑up‑and‑play titles with local multiplayer and AI opponents, to cure boredom and revive some nostalgia from the early 2000s.

### The Product
An original desktop arcade collection built with Pygame. The app presents a carousel menu where the user scrolls through game covers and launches one of five classic games: Pong, Scissors‑Paper‑Rock, Guess the Number, Breakout, and Memory Match. Every game supports single‑player, local two‑player, or versus‑AI modes. Before a match, players enter a name (like old‑school arcade high‑score screens), and performance stats are saved per game. A dedicated scoreboard screen, opened by pressing **T** on the menu, shows lifetime stats – number of AI defeats, longest rally, fastest clear time, etc. – making the experience feel like a real arcade cabinet.

### Essential Features
- **Core games** working with basic graphics, sound, and controls.
- **Three play modes** per game: human vs. human, human vs. AI, and pure single‑player where applicable.
- **Menu and navigation**: a carousel game select, difficulty choice, and player‑name entry.
- **Scoreboard**: press **T** on the menu to view saved stats for the currently highlighted game; left/right arrow switches between game scoreboards.
- **Asset management**: a single config file stores file paths and sizes; a startup routine loads and scales all images and sounds.
- **Modular code architecture**: the menu returns a state, and the main loop uses a switch/case to run the correct game module – easy to add new games later.

### Add‑ons (If time bids)
1. Advanced split‑screen: two‑player race mode in Breakout with independent surfaces.
2. Breakout power‑ups: timed items (wider paddle, extra ball, laser) drop from broken bricks, with visual and sound effects.
3. Random Breakout level generator to avoid repetitive brick layouts.
4. Enhanced AI humanisation: adjustable difficulty (reaction delay, occasional misses) for Pong and Breakout; adaptive counter‑strategy for Scissors‑Paper‑Rock.
5. More games: e.g., Snake, Space Invaders or Galaga, Flappy Bird clone.
6. Full arcade‑style attract mode: demo loops when idle – perhaps just get the AI to play against itself.

### Intended File Structure
code/ (Root folder)  
├── main.py # App entry point; runs the core state machine loop  
├── settings.py # Central config; file paths, window sizes, colors, FPS  
├── assets_loader.py # Startup routine; loads and scales all images and sounds  
├── assets/ (Universal asset storage)  
	│ ├── fonts/ # Arcade-style TTF fonts  
	│ ├── sfx/ # UI clicks, game-specific sound & music  
	│ └── images/ # Carousel covers, backgrounds, sprites  
├── data/ (Persistent arcade score storage)  
	│ ├── pong_stats.npy  
	│ ├── spr_stats.npy  
	│ ├── guess_stats.npy  
	│ ├── breakout_stats.npy  
	│ └── memory_stats.npy  
└── src/ (Source code directory)  
	├── **init**.py  
	├── engine/ (Core framework files)  
		│ ├── **init**.py  
		│ ├── base_state.py # Parent class that all games/menus inherit from  
		│ ├── state_manager.py # Handles switching between menu, games, scoreboard  
		│ └── input_handler.py # Manages name entry and cabinet button maps  
	├── menu/ (Menu and UI states)  
		│ ├── **init**.py  
		│ ├── carousel_menu.py # Main game selection visual carousel  
		│ ├── name_entry.py # Old-school high score name input screen  
		│ └── scoreboard.py # Toggles stats with 'T'; cycles with arrows  
	└── games/ (Individual game modules)  
		├── **init**.py  
		├── base_game.py # Shared game logic (AI modes, universal scoring)  
		├── pong/  
			│ ├── **init**.py  
			│ ├── pong_main.py # Pong state manager & loop  
			│ └── pong_ai.py # Humanized AI (speed caps, random overshoots)  
		├── spr/  
			│ ├── **init**.py  
			│ ├── spr_main.py # Scissors-Paper-Rock state & loop  
			│ └── spr_ai.py # Frequency counter AI tracking player moves  
		├── guess_number/  
			│ ├── **init**.py  
			│ └── guess_main.py # Guess the Number state & loop  
		├── breakout/  
			│ ├── **init**.py  
			│ ├── breakout_main.py # Breakout state, split-screen management  
			│ ├── breakout_ai.py # Humanized tracking AI for Breakout  
			│ └── powerups.py # Droppable timed items (laser, wide paddle)  
		└── memory_match/  
			├── **init**.py  
			├── memory_main.py # Memory Match state & loop  
			└── memory_ai.py # Grid memory matrix AI tracking seen cards



### Research & Problem Breakdown
This section covers disecting the project into challenges and investigated existing solutions.

| Problem                             | Research & Approach                                                                                                                                                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Game loop and state management**  | Tutorials (e.g., “Pygame State Machine” by Clear Code) show how a central loop can delegate to different states, keeping code organised.                                                                                                                                          |
| **AI opponents that feel human**    | For Pong/Breakout, I will cap the AI paddle speed and add random overshoots, based on techniques I saw on Stack Overflow. For SPR, I’ll implement a simple frequency counter that beats the player’s most frequent move. The Concentration AI will maintain a list of seen cards. |
| **Asset loading and scaling**       | I’ll load images after `pygame.init()`. Paths and target sizes will be stored in a `.py` config file and scaled in a dedicated function, avoiding loading too fast.                                                                                                               |
| **Persistent arcade scores**        | NumPy arrays (`.npy`) are lightweight and Python‑native; no external database needed.                                                                                                                                                                                             |
| **Split‑screen rendering**          | Instead of drawing directly to the display surface, I’ll create two subsurface rectangles and copy each player’s view independently, like SNES *Tetris & Dr. Mario*. [Video of Gameplay](https://www.youtube.com/watch?v=uoJxVnkDA8Y&t=1s)                                        |
| **Win condition checks with NumPy** | Using a boolean brick grid in Breakout, `np.any()` instantly tells if any bricks remain.                                                                                                                                                                                          |
| **Sound system**                    | Write down all needed sounds for entire game box, then create or find & credit sounds that will be used and import them accordingly per game or menu.                                                                                                                             |

**Sources:**  
- Clear Code YouTube tutorials  
- GeeksforGeeks (NumPy save method: [https://www.geeksforgeeks.org/python/numpy-save/](https://www.geeksforgeeks.org/python/numpy-save/))  
- Stack Overflow thread on Pong AI paddle flickering: [https://stackoverflow.com/questions/22868629/pong-game-ai-paddle-flickering](https://stackoverflow.com/questions/22868629/pong-game-ai-paddle-flickering) (mentions speeding up ball randomly for enhanced challenge)  
- Pygame Fundamentals – Clear Code: [https://www.youtube.com/watch?v=YOCt8nsQqEo&list=PL8ui5HK3oSiHnIdi0XIAVXHAeulNmBrLy](https://www.youtube.com/watch?v=YOCt8nsQqEo&list=PL8ui5HK3oSiHnIdi0XIAVXHAeulNmBrLy)  
- Pygame official documentation  

### Timeline (Week‑by‑week, assuming ~3 hours class time per week + homework)

| Week | Tasks                                                                                                              | Documentation / Testing                                                           |
| ---- | ------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| 1    | Create main loop skeleton, config file structure, asset loader. Find assets.                                       | Proposal writing. Test: window opens, asset loader prints loaded paths.           |
| 2    | Implement carousel menu: scrolling covers, state returns. Stub out all five game files. Player‑name entry screen.  | Document menu state logic. Test: navigation works, switches to dummy game screen. |
| 3    | Build Pong – core mechanics, simple AI, and scorekeeping. Integrate into menu.                                     | Begin game‑specific docs. Test: Pong playable, AI moves.                          |
| 4    | Build Scissors‑Paper‑Rock with emoji UI and random AI. Add smart counter‑AI as add‑on if time.                     | Document AI logic. Test: all modes functional.                                    |
| 5    | Build Guess the Number with binary‑search AI.                                                                      | Test: human guesses and AI guesses work.                                          |
| 6    | Build Breakout core (reuse Pong physics). Add brick grid, collision, basic level. Power‑ups implemented as add‑on. | Document physics reuse. Test: ball destroys bricks, win condition triggers.       |
| 7    | Build Memory Match – grid display, card flip logic, basic random AI. Add Level‑2 “remembering” AI.                 | Document grid logic and AI. Test: matches detected, AI behaves correctly.         |
| 8    | Implement save system: .npy stats arrays, scoreboard screen navigation, stats updating after each match.           | Test: scores persist across sessions, scoreboard navigation.                      |
| 9    | Add split‑screen mode for Breakout two‑player. Polish UI, sound effects, music loops.                              | Full integration testing. Document split‑screen approach.                         |
| 10   | Refine AI humanisation, add difficulty selector, tweak power‑up timings.                                           | Prepare final documentation, user guide.                                          |
| 11   | Buffer week – tackle add‑ons (random layout generator, attract mode) or fix unexpected bugs.                       | Finalise documentation.                                                           |
| 12   | Final testing, code freeze, submission.                                                                            | Complete all documentation.                                                       |

*The project should follow the Stanford / Double Diamond Design Process – starting with broad exploration, then focusing on defined problems, prototyping solutions, and iterating through testing and refinement.*

---

## Record of Development and Design Thinking

*Collect evidence from at least four stages of development. For each stage, include:*  
- A screenshot, video, or code sample  
- A description of what was developed  
- Challenges encountered  
- Changes made from the original plan  
- Next steps  

**Stage 1 – [Date / Week]**  
*(Insert your evidence and commentary here.)*

**Stage 2 – [Date / Week]**  
*(Insert your evidence and commentary here.)*

**Stage 3 – [Date / Week]**  
*(Insert your evidence and commentary here.)*

**Stage 4 – [Date / Week]**  
*(Insert your evidence and commentary here.)*

*(Add more stages if needed.)*

---

## Evaluation and Review

*Answer the following guiding questions after completing the project. Be meaningful and creative; link your answers to evidence from the development record.*

**Planning**  
- What aspects of your original plan were successful?  
- What changes did you make and why?  

**Development**  
- What technical challenges did you encounter?  
- How did you overcome them?  

**Project Management**  
- How effectively did you manage your time?  
- What would you do differently?  

**Skills**  
- What new skills did you learn?  
- Which skills improved most?  

**Evaluation**  
- How well does the final product meet user needs?  
- What would you improve if given another month?  

*(Write your evaluation below, referring back to your proposal, research, and development records.)*