# Major Project Documentation – PyCade

---

## Proposal
# PyCayde
*A Retro style arcade box*
<div style="page-break-after: always;"></div>

<div style="page-break-after: always;"></div>
### Client
Casual gamers who enjoy classic pick‑up‑and‑play titles with local multiplayer and AI opponents, to cure boredom and revive some nostalgia from the early 2000s without any ads, in‑app purchases or WiFi.

### The Product
An original desktop arcade collection built with Pygame. The app presents a carousel menu where users scroll through game covers and launch one of five classic games: Pong, Scissors‑Paper‑Rock, Guess the Number, Breakout, and Memory Match. Every game includes multiple play modes, user profile creation, and stat tracking. A dedicated scoreboard screen tracks lifetime achievements across all titles.

---
<div style="page-break-after: always;"></div>
### Essential Features
- **Core games** working with basic graphics, sound, and controls.
- **Three play modes** per game: human vs. human, human vs. AI, and pure single‑player where applicable (for games like Breakout).
- **Menus and navigation**:
  - **Main Menu**: A carousel game select, navigated via left/right arrow keys. Press **E** on a selected game to launch; from there, enter username and then choose game mode and difficulty.
  - **Settings** *(refer to Designs sections)*: Press **S** on the menu to open the settings screen ("General" tab by default). Change things like sound volume and later AI difficulty or other options. The Controls screen can be selected from the side panel inside Settings (as per designs at the bottom of this page). Press **ENTER** to save, **ESC** to exit back to the main menu.
  - **Scoreboard**: Press **T** on the menu to view saved stats for the currently highlighted game; left/right arrow switches between game scoreboards.
  - **Game Pause**: Press **ESC** during any game to bring up a classic pause menu (inspired by Angry Birds style) – refer to the inspiration section for reference.
- **Asset management**: a single config file stores file paths and sizes; a startup routine loads and scales all images and sounds.
- **Modular code architecture**: the menu returns a state, and the main loop uses a switch/case to run the correct game module – easy to add new games later.
---

### Add‑ons (If time bids)
1. Advanced split‑screen: two‑player race mode in Breakout with independent surfaces/screens.
2. Enhanced AI humanisation: adjustable difficulty (reaction delay, occasional misses) for Pong and Breakout; adaptive counter‑strategy.
3. Breakout power‑ups: timed items (wider paddle, extra ball, laser) drop from broken bricks, with visual and sound effects.
4. Random Breakout level generator to avoid repetitive brick layouts.
5. More games: e.g., Snake, Space Invaders/Galaga, Flappy Bird clone.
6. Full arcade‑style attract mode: demo loops when idle – perhaps just get the macro “AI” to play against itself.

<div style="page-break-after: always;"></div>

### Intended File Structure
<div style="font-size: calc(1em - 3.5px); line-height: 1.2;">
<pre>
code/ (Root folder)  
├── main.py # App entry point; runs the core state machine loop  
├── settings.py # Central config; file paths, window sizes, colors, FPS  
├── assets_loader.py # Startup routine; loads and scales all images and sounds  
├── assets/ (Universal asset storage)  
	│ ├── sfx/ # UI clicks, game-specific sound & music  
	│ └── images/ # Carousel covers, backgrounds, sprites
	| ├── starynight.py #menu background
├── data/ (Persistent arcade score storage)  
	│ ├── pong_stats.npy  
	│ ├── spr_stats.npy  
	│ ├── guess_stats.npy  
	│ ├── breakout_stats.npy  
	│ └── memory_stats.npy  
└── src/ (Source code directory)  
	├── __init__.py  
	├── engine/ (Core framework files)  
		│ ├── __init__.py  
		│ ├── base_state.py # Parent class that all games/menus inherit from  
		│ ├── state_manager.py # Handles switching between menu, games, scoreboard  
		│ └── input_handler.py # Manages name entry and cabinet button maps  
	├── menu/ (Menu and UI states)  
		│ ├── __init__.py  
		│ ├── carousel_menu.py # Main game selection visual carousel  
		│ ├── name_entry.py # Old-school high score name input screen  
		│ ├── settings_menu.py    # Settings screen (general, controls tabs)
		│ └── scoreboard.py # Toggles stats with 'T'; cycles with arrows  
	└── games/ (Individual game modules)  
		├── __init__.py  
		├── base_game.py  # Shared game logic (AI modes, universal scoring, pause menu)
		├── pong/  
			│ ├── __init__.py  
			│ ├── pong_main.py # Pong state manager & loop  
			│ └── pong_ai.py # Humanized AI (speed caps, random overshoots)  
		├── spr/  
			│ ├── __init__.py  
			│ ├── spr_main.py # Scissors-Paper-Rock state & loop  
			│ └── spr_ai.py # Frequency counter AI tracking player moves  
		├── guess_number/  
			│ ├── __init__.py  
			│ └── guess_main.py # Guess the Number state & loop  
		├── breakout/  
			│ ├── __init__.py  
			│ ├── breakout_main.py # Breakout state, split-screen management  
			│ ├── breakout_ai.py # Humanized tracking AI for Breakout  
			│ └── powerups.py # Droppable timed items (laser, wide paddle)  
		└── memory_match/  
			├── __init__.py  
			├── memory_main.py # Memory Match state & loop  
			└── memory_ai.py # Grid memory matrix AI tracking seen cards
</pre> 
</div>

<div style="page-break-after: always;"></div>

### Research & Problem Breakdown
This section covers disecting the project into challenges and investigated existing solutions.

| Problem                             | Research & Approach                                                                                                                                                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Game loop and state management**  | Tutorials (e.g., “Pygame State Machine” by Clear Code) show how a central loop can delegate to different states, keeping code organised.                                                                                                                                          |
| **AI opponents that feel human**    | For Pong/Breakout, I will cap the AI paddle speed and add random overshoots, based on techniques I saw on Stack Overflow. For SPR, I’ll implement a simple frequency counter that beats the player’s most frequent move. The Concentration AI will maintain a list of seen cards. |
| **Asset loading and scaling**       | I’ll load images after `pygame.init()`. Paths and target sizes will be stored in a `.py` config file and scaled in a dedicated function, avoiding loading too fast.                                                                                                               |
| **Persistent arcade scores**        | NumPy arrays (`.npy`) are lightweight and Python‑native; no external database needed.                                                                                                                                                                                             |
| **Split‑screen rendering**          | Instead of drawing directly to the display surface, I’ll create two subsurface rectangles and copy each player’s view independently, perhaps like SNES *Tetris & Dr. Mario*. [Video of Gameplay](https://www.youtube.com/watch?v=uoJxVnkDA8Y&t=1s)                                |
| **Win condition checks with NumPy** | Using a boolean brick grid in Breakout, `np.any()` instantly tells if any bricks remain.                                                                                                                                                                                          |
| **Sound system and UI Assets**      | Write down all needed sounds for entire game box, then create or find & credit sounds that will be used and import them accordingly per game or menu, the same will follow for UI assets.                                                                                         |

---
<div style="page-break-after: always;"></div>
### **Timeline** (Week‑by‑week, assuming ~3 hours class time per week + homework)

| Week | Tasks                                                                                                                                           | Documentation / Testing                                                           |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 1    | Create main loop skeleton, config file structure, asset loader. Find assets.                                                                    | Proposal writing. Test: window opens, asset loader prints loaded paths.           |
| 2    | Implement carousel menu: switching covers, state returns. Build settings system/screen. Stub out all five game files. Player‑name entry screen. | Document menu state logic. Test: navigation works, switches to dummy game screen. |
| 3    | Build Pong – core mechanics, simple AI, and scorekeeping. Integrate into menu. Build pause menu function to be used in all games.               | Begin game‑specific docs and UI documentation. Test: Pong playable, AI moves.     |
| 4    | Build Scissors‑Paper‑Rock with emoji UI and random AI. Add smart counter‑AI as add‑on if time.                                                  | Document AI logic. Test: all modes functional.                                    |
| 5    | Build Guess the Number with binary‑search AI.                                                                                                   | Test: human guesses and AI guesses work.                                          |
| 6    | Build Breakout core (reuse Pong physics). Add brick grid, collision, basic level (13×5). Power‑ups implemented as add‑on.                       | Document physics reuse. Test: ball destroys bricks, win condition triggers.       |
| 7    | Build Memory Match – grid display, card flip logic, basic random AI. Add Level‑2 “remembering” AI.                                              | Document grid logic and AI. Test: matches detected, AI behaves correctly.         |
| 8    | Implement save system: .npy stats arrays, scoreboard screen navigation, stats updating after each match.                                        | Test: scores persist across sessions, scoreboard navigation works.                |
| 9    | Add split‑screen mode for Breakout two‑player. Polish UI, sound effects, music loops.                                                           | Full integration testing. Document split‑screen approach.                         |
| 10   | Refine AI humanisation, add difficulty selector, tweak power‑up timings.                                                                        | Prepare final documentation, user guide.                                          |
| 11   | Buffer week – tackle add‑ons (random layout generator, attract mode) or fix unexpected bugs.                                                    | Finalise documentation.                                                           |
| 12   | Final testing, code freeze, submission.                                                                                                         | Complete all documentation.                                                       |

*The project should follow the Stanford / Double Diamond Design Process – starting with broad exploration, then focusing on defined problems, prototyping solutions, and iterating through testing and refinement.*

---
<div style="page-break-after: always;"></div>
# **Screen Designs** *(Excluding Game Screens)*

##### Main Menu
![[Heading (3).png]]

<div style="page-break-after: always;"></div>
#### **Settings System Screens** *(default will be set to general)*

##### General
![[Heading (2).png]]

<div style="page-break-after: always;"></div>
##### Controls
![[Heading (1).png]]

---
<div style="page-break-after: always;"></div>
# Inspiration
Below are images which I plan to be of inspiration during development:


### Pause Menu

##### Angry Birds Star Wars 
![[Pasted image 20260806195231.png]]
Source: https://www.mobygames.com/game/62348/angry-birds-star-wars-ii/screenshots/android/643874/

#####  Angry Birds Classic
![[Pasted image 20260806195452.png]]
Source: https://www.mobygames.com/game/46396/angry-birds/screenshots/macintosh/490935/
### Breakout

##### Arkanoid
![[Pasted image 20260806195820.png|390]]
Source: https://en.wikipedia.org/wiki/Arkanoid#/media/File:Arkanoid.png


### Two player split screen

##### Tetris & Dr. Mario
![[Pasted image 20260806200301.png|456]]
Source: https://ultimatepopculture.fandom.com/wiki/Tetris_%26_Dr._Mario?file=Tetris_%26_Dr._Mario_screenshot.png


---

# Bibliography 

1. Clear Code. (n.d.). Pygame Fundamentals [YouTube playlist]. YouTube. Retrieved from https://www.youtube.com/playlist?list=PL8ui5HK3oSiHnIdi0XIAVXHAeulNmBrLy 
2. GeeksforGeeks. (n.d.). numpy.save() in Python. GeeksforGeeks. Retrieved from https://www.geeksforgeeks.org/python/numpy-save/ 
3. Stack Overflow. (2014, April 9). Pong game AI paddle flickering. Stack Overflow. Retrieved from https://stackoverflow.com/questions/22868629/pong-game-ai-paddle-flickering 
4. Pygame Developers. (n.d.). Pygame Documentation. Retrieved from https://www.pygame.org/docs/ 
5. Tetris & Dr. Mario (SNES). (2018, December 23). Tetris & Dr. Mario SNES 2 Player Gameplay [Video]. YouTube. Retrieved from https://www.youtube.com/watch?v=uoJxVnkDA8Y&t=1s 
6. MobyGames. (n.d.). Angry Birds Star Wars II – Screenshot (Android). MobyGames. Retrieved from https://www.mobygames.com/game/62348/angry-birds-star-wars-ii/screenshots/android/643874/ 
7. MobyGames. (n.d.). Angry Birds – Screenshot (Macintosh). MobyGames. Retrieved from https://www.mobygames.com/game/46396/angry-birds/screenshots/macintosh/490935/ 
8. Wikipedia contributors. (n.d.). Arkanoid. Wikipedia. Retrieved from https://en.wikipedia.org/wiki/Arkanoid#/media/File:Arkanoid.png 
9. Fandom. (n.d.). Tetris & Dr. Mario. Ultimate Pop Culture Wiki. Retrieved from https://ultimatepopculture.fandom.com/wiki/Tetris_%26_Dr._Mario?file=Tetris_%26_Dr._Mario_screenshot.png

---

## Record of Development and Design Thinking

*Collect evidence from at least four stages of development. For each stage, include:*  
- A screenshot, video, or code sample  
- A description of what was developed  
- Challenges encountered  
- Changes made from the original plan  
- Next steps  

**Stage 1 – [06/08/2026 / Week 1]**  
>Completed proposal writing and curating sound assets, some where gathered from https://freesound.org while others were created in Audacity. They have been named and credited in Attribution txt files in their designated folder. Still need to create main loop skeleton, config file structure, and asset loader.

**Stage 2 – [15/08/2026 / Week 2]**  
>Learning about some things in python such as dunders like `__init__'. While we have learnt this in class in the past, I like to refresh if I feel a need. 
 
>`What does __init__ do in Python?` - https://www.youtube.com/watch?v=VEbuZox5qC4

>`What is the __init__ method in Python?` https://www.youtube.com/watch?v=PwmQHPU7_Og

>`What does __name__ == __main__ do in Python?` - https://www.youtube.com/watch?v=x5IbdKnvt6k


**Stage 3 – [19/08/2026 / Week 3]**  
> Created `starrynight.py` to serve as a dynamic main menu background, eliminating the need for heavy GIF file rendering. Fixed a rendering order issue from the previous lesson where the background clearing step was accidentally overwriting the stars. The script generates stars across three distinct depth layers to create a parallax effect (`speed = layer * 0.1`). Stars move downward continuously; once a star goes off-screen (`y > height`), its properties reset and it respawns at `y = 0` to create an infinite loop. Now we need to setup the file structure so that I can get started on coding the skeletons.

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