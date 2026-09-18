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
- **Three play modes** per game: human vs. human, human vs. AI, and pure single‑player where applicable (for games like Breakout). Modes are auto-detected from each game's `__init__.py` — the carousel shows a mode selection screen with buttons built automatically.
- **Menus and navigation**:
  - **Main Menu**: A carousel game select, navigated via left/right arrow keys. Press **E** on a selected game to launch; if the game has multiple modes, a mode select screen appears first.
  - **Pause Menu**: Press **ESC** during any game to bring up the pause overlay with options to resume (ESC), quit to menu (Q), or open settings (S — placeholder for now).
  - **Settings** *(stub)*: Press **S** on the carousel to open the settings screen. Coming soon.
  - **Scoreboard** *(stub)*: Press **T** on the carousel to view saved stats. Coming soon.
- **Asset management**: a single config file stores file paths and sizes; a startup routine loads and scales all images and sounds. Missing files are handled gracefully (no crashes).
- **Modular code architecture**: each game mode extends `GameBase` from `src/core/game_base.py`, the state machine treats everything the same. Modes are separate `.py` files in each game's folder (`mode_1p.py`, `mode_2p.py`, `mode_ai.py`).
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

**Stage 1 - [06/08/2026 / Week 1]**  
>Completed proposal writing and curating sound assets, some where gathered from https://freesound.org while others were created in Audacity. They have been named and credited in Attribution txt files in their designated folder. Still need to create main loop skeleton, config file structure, and asset loader.

**Stage 2 - [15/08/2026 / Week 2]**  
>Learning about some things in python such as dunders like `__init__'. While we have learnt this in class in the past, I like to refresh if I feel a need. 
 
>`What does __init__ do in Python?` - https://www.youtube.com/watch?v=VEbuZox5qC4

>`What is the __init__ method in Python?` https://www.youtube.com/watch?v=PwmQHPU7_Og

>`What does __name__ == __main__ do in Python?` - https://www.youtube.com/watch?v=x5IbdKnvt6k


**Stage 3 - [19/08/2026 / Week 3]**  
> Created `starrynight.py` to serve as a dynamic main menu background, eliminating the need for heavy GIF file rendering. Fixed a rendering order issue from the previous lesson where the background clearing step was accidentally overwriting the stars. The script generates stars across three distinct depth layers to create a parallax effect (`speed = layer * 0.1`). Stars move downward continuously; once a star goes off-screen (`y > height`), its properties reset and it respawns at `y = 0` to create an infinite loop. Now we need to setup the file structure so that I can get started on coding the skeletons.

**Stage 4 - [21/08 2026 / Week 3]**  
>Created all placeholder files ready for code as per the intended file structure.
Created Pong game, teacher helped me with math calculations for ball when colliding with paddle. Changed score files in data. from a .py file to .json. Also changed name of files in game folder from things like "pong_main.py" & "pong_ai.py" to simply be "main.py" and "ai.py", since all games are in separate folders, there is no need to give custom names.
There was an issue with the collisions of the ball.

>`line 95, in <module>
    ball_speed_x = -maths.sqrt(total_speed**2-ball_speed_y**2)
                    ValueError: math domain error`

>This was fixed by more help from the teacher:
 Added `and ball_speed_x < 0` for the player and `and ball_speed_x > 0` for the opponent.
**Safe Square Root:** Wrapped values in `max(0, ...)` to prevent math errors if `ball_speed_y` ever exceeds `total_speed`.
**Direction:** Kept the same positive speed for the player bounce and negative speed for the opponent bounce.

Bug: ball colliding into wall and being stuck inside if the paddle accidently pushes it into the wall. 
![[Pasted image 20260828113834.png]]

On top of this there is a bug where if the user hits the ball perfectly down, it does not collide and bounce off creating a bug where the ball is stuck going up and down. 
![[Screenshot 2026-08-21 112531.png|459]]
Issue was that ball speed being 0 at x axis did nothing `= 0`, it has been update to  `<= 0`
To fix ball collision error. if ball.top <= 0 then ball.top = 0.

**Stage 5 - [21/08 2026 / Week 4]** 
>Built very basic number guesser game with difficulty selector (easy, medium, hard), different amount of tries for each. Also gave it a mode selection (Ai or Local). Ai always selects secret number else then heads or tails between two players to pick who starts and picks a number.  
A classmate of mine recommended I use a dir file location package in python for my menu game selection when I build it, package is "pathlib".
`from pathlib import path` is how it needs to be used.

Built basic scissors paper rock without an ai difficulty system.
For 2 player local mode. P1 has 3 button assigned for Scissors, Paper, & Rock (A, W, D), P2 has (Left_Btn, Up_Btn, &, Right_Btn). Rules: cover hand used to select your option and play against your friend digitally because you obviously can't play in real life. 
![[Pasted image 20260828131606.png]]

**Stage 6 - [31/08/2026 / Week 5]**
Created basic memory match using numbers using numbers as card faces and a basic chequered pattern for backs. Three playstyles to pick on start; Single player, Local vs or Ai vs. 3 modes, Easy (24 cards - 12 pairs), Medium (52 cards - 26 pairs), Hard (104 cards - 52 pairs). Background made to look like generic wood floor -- just for aesthetic. Highest pairs found wins. For single player there is a lives system; Easy (18 lives), Medium (31 lives), and Hard (52 lives), this ensures that there is still a level of competition.

**Stage 7 - [07/09/2026 / Week 6]**
Created very basic breakout (Arkanoid) and making sure to import same collision system that I used from pong. Two issues presented: Ball would kill bricks if perfectly on a bricks edge, passing it to the next, secondly ball would not get push up or down from paddle depending on which corner hit. The same ball wall clipping bug fix was used in the same manner to fix both clipping issues found.

![[breakoutVersion1.png]]

Built the carousel menu system with the starfield background from starynight.py so the menu looks dynamic instead of a static image. The carousel loads cover art from the assets/gui/cover-art folder using the filenames that match each game — no manual mapping needed per game thanks to a central game registry in settings.py. Left/right arrows scroll through covers, E or Enter launches the selected game.

Also added Tetris as a new game after a suggestion from Dexter, they said it would give the arcade box more depth, and I agree. Gave it a two-player mode inspired by SNES Tetris & Dr. Mario: each player has their own board side by side (P1 uses arrow keys + space, P2 uses WASD + shift), and if one player's stack hits the top of their board the other player wins. The blocks are rendered as coloured rectangles so there are no assets needed thank god.

Wired up a state machine in main.py so the carousel menu can launch any game and ESC returns to the menu. Had to wrap each game in a small class (PongGame, BreakoutGame, etc.) so they all respond to the same handle_event/update/draw interface seeing as the existing games each had their own while loop before, so I left those loops inside if __name__ blocks for standalone testing.

Made settings.py as a central config for all file paths, colours, and game names. Assets loader was updated to read music from the music subfolder inside sfx/ (where the actual .wav files live). Scoreboard and Settings screens are filled out with placeholder text for now. I will be planning to fill them in with saved stats and volume controls.

Added a MusicManager in src/engine/music_manager.py that handles the menu theme and game-specific music switching. It uses pygame.mixer.music so it's lightweight — no threading needed, just plays on top of the game loop. The carousel menu starts the main_theme.wav, and whenever a game launches the wrapper swaps to that game's track (breakout.wav, tetris.wav, etc.). On the SFX side I wired in sounds for Tetris (line clear = num_correct.wav, game over = life_lost.wav), Breakout (paddle hits, brick breaks, powerup collects, life lost), Guess Number (correct/wrong), Scissors Paper Rock (selection confirm), and Memory Match (card flip up/down, match found/wrong). Pong is missing its SFX file still so that one just has nothing play for now — but the placeholders are set up so once I get the pong.wav (the SFX one, not the music one) it'll just work.

*Next session I will fix the draw order (layering) of game covers on main menue along with making sure all game share floating screen size of main menue while allowing fullscreen*. Then I need to implement score saving with .json files (the data/ modules are created but not connected yet), add the "press T for scoreboard" and "press S for settings" navigation from the carousel, and maybe add a visual game-over summary screen to each game.*


*Creating base cover art using Canva.com*
![[screenshot-createingcoverartoncanva-07-09-2026.png]]

*Easy to fix layering issue of main menu*
![[screenshot-2026-09-07_23-19-55.png]]

**Stage 8 - [09/09/2026 / Major Rewrite]**
>Holy moly. This was a big one. I basically ripped the whole thing apart and put it back together properly. Here's the rundown of what happened and why.

>The main problem was that every game had its own copy-pasted colours, sizes, and input handling. Pong's controls felt awful because if you held W (up) then pressed S (down), nothing happened until you released W first. My old code only checked KEYDOWN events, not what keys were *currently* being held. So I built `GameKeyHandler` in `input_handler.py` that tracks keys in an ordered list. The most recently pressed key is the "active" one. If you hold W then press S, S becomes active immediately. This made Pong actually playable.

>Another pain point: every game had `WHITE = (255, 255, 255)` and `WIDTH = 950` declared at the top of its own file. Six files. Six times. I moved everything into `src/core/constants.py`, which holds colours, paddle sizes, ball sizes, Tetris piece shapes, all of it. Every game now imports from there. If I want to change the paddle width across every game, I change one number.

>The mode selection was also a mess. Tetris had its own menu screen with hardcoded rects, Memory had its own, Guess Number had its own. Each one did the same thing differently, since I was coding everything in different sessions. I built `ModeSelectScreen` in `src/menu/mode_select.py` that reads a `MODES` dict from each game's `__init__.py` and auto-builds buttons. Now if I add a new mode to a game, I just drop a new `mode_*.py` file in that game's folder and add it to the MODES dict and now the screen builds itself.

>Each game mode now extends `GameBase` from `src/core/game_base.py` so the state machine treats everything the same. Clean `startup()` / `handle_event()` / `update()` / `draw()` / `cleanup()` interface. No more guessing what methods a game has.

>Added a shared pause menu (`PauseMenu` in `src/menu/pause_menu.py`) that every game gets for free. ESC pauses, Q quits to menu, S opens settings, ESC resumes. The wrapper in `main.py` handles event routing so the games themselves don't need to know anything about pause.

>I also fixed the carousel draw order. Before, covers were drawn left-to-right in list order, which meant the right-side cover could overlap the selected one and that made it look unprofessional. Now I split the draw into two passes: first all non-selected covers, then the selected one on top.

>Found and fixed a bug in Memory's `evaluate_match()` where the "flip cards back on mismatch" code was in a broken second `else` clause at the wrong indentation level. The old code had:
>```python
>if match: ...
>else:     # mismatch handling
>    ...
>else:     # BUG: this was dead code — cards never flipped back
>```
>Took me longer than I'd like to admit staring at that one.

>All game SFX and music loading is handled with try/except. If a sound file is missing, the game just doesn't play that sound instead of crashing.

>**What I learned:** Don't let six files diverge on the same constants. Put them in one place from day one. Also, key handling in games needs to think about *held* keys, not just pressed keys, the distinction makes or breaks gameplay feel.

>**Still to do:** Settings screen and Scoreboard screen (both placeholders), per-game asset manifests (assets.json), actual stat saving/loading from the data/ files, and maybe some polish on the visual side now that the motor runs clean.

>**Files changed/created this stage:**
>- `src/core/constants.py` - new: shared colours, sizes, speeds
>- `src/core/game_base.py` - new: base class for all game modes
>- `src/menu/pause_menu.py` - new: shared ESC-overlay pause
>- `src/menu/mode_select.py` - new: auto-building mode picker
>- `src/engine/input_handler.py` - rewritten: proper held-key tracking with "most recent wins" logic
>- `src/menu/carousel_menu.py` - fixed: draw order (selected on top), mode select integration
>- `main.py` - updated: pause menu handling, mode select support, new game wrapper
>- `settings.py` - updated: GAME_REGISTRY with module paths
>- `src/games/breakout/mode_1p.py` - new rewrite
>- `src/games/pong/mode_ai.py`, `mode_2p.py` - new rewrites with fixed input
>- `src/games/tetris/mode_1p.py`, `mode_2p.py` - new rewrites with shared Board class
>- `src/games/memory/mode_1p.py`, `mode_2p.py`, `mode_ai.py` - new rewrites with fixed match logic
>- `src/games/guess_number/mode_ai.py`, `mode_local.py` - new rewrites
>- `src/games/spr/mode_ai.py`, `mode_2p.py` - new rewrites
>- `code/structure.txt` - new: project structure overview for anyone picking this up

**Stage 9 - [9/09/2026 / DAS + Draw Order Fix]**
>Smaller session today but two important fixes that make a big difference in feel.

>**Carousel draw order - another try of fixing**
>The stage 8 fix was just a bandaid: just drew "non-selected first, selected last". That meant left-side covers were drawn in list order (fine), but right-side covers were also drawn in list order, so the furthest right cover would paint over the one next to it. Looked fine in some positions, wrong in others. The proper fix is:
>1. Left of selected: draw furthest-left first, work inward (so the nearest left cover is on top of the further ones)
>2. Right of selected: draw closest-to-selected first, work outward (so the nearest right cover paints over the further ones)
>3. Selected: dead last
>
>So for a layout like covers 1 through 6 where 6 is selected, the draw order is: 1, 2, 3, 4, 5, 6 (furthest left first, then closest left, then closest right, then furthest right, then, selected). If 3 is selected from the same layout: 1, 2, 4, 5, 6, 3. Each side stacks properly.

>**Tetris DAS**
>I'd never actually tested the Tetris movement after the rewrite, I just set generic DAS numbers and moved on. When I actually played it, the piece would start drifting almost immediately when you held a direction, which felt wrong for Tetris. It's fine for Pong/Breakout where you want instant response, but Tetris needs that deliberate "hold, wait for it... there it goes" rhythm.
>
>Changed both `mode_1p.py` and `mode_2p.py` to use `DAS_DELAY=167, DAS_REPEAT=16`. Also fixed the DAS check to only repeat the most-recently-held direction (using `get_active()`) instead of blindly checking both left and right each frame, this prevents the two fighting each other if both buttons somehow register.
>
>**What I learned:** DAS timing isn't one-size-fits-all. What feels snappy in Pong (instant held-key following) feels twitchy in Tetris. The DAS values exist for a reason, they match the rhythm of placing pieces in a grid where precision matters more than speed.

>**Still to do:** Same as last time - Settings, Scoreboard, stat saving with names. The motor runs. Now I can start polishing. Once this is all done, better AI can be implemented for games like spr, pong, and memory match.

**Stage 10 - [10/09/2026 / Carousel Rework — 3-Item Viewport + Infinite Loop]**
>Full carousel rewrite. The old system drew all N covers every frame with a clunky z-index sort that broke as soon as you had more than ~5 games. 
>New approach: only ever show 3 covers, the left neighbor, selected, right neighbor. Draw order is simply 1=left, 2=right, 3=selected (back to front). Scales are exactly 1.0 for selected, 0.8 for neighbors which make it a crisp, predictable with no more fading or magic numbers.
>
>**Infinite looping** - Pressing left on the first game wraps to the last, and pressing right on the last wraps to the first. The shortest-path interpolation during scrolling makes it feel like a real carousel rather than a film reel.
>
>**Smooth scrolling** - the fractional part of `current_offset` drives a slide transform on all three covers simultaneously so they glide between positions instead of snapping. The scrolling also normalises diffs across the wrap boundary so you never see a full-circle spin.
>
>**What I learned:** A 3-slot viewport is way simpler than trying to dynamically order N covers every frame. The modular wrapping math was the only tricky part,  specifically normalising the shortest-path diff so the smooth scroll doesn't take the long way around the circle. Using `_mod_dist` and `_wrap_index` keeps all the wrap logic in two helper functions rather than sprinkled through the update loop.
>
>**Still to do:** Same as last time... Settings, Scoreboard, stat saving with names, and then AI. Seeing as the motor now runs well, I can start polishing.

**Stage 11 - [12/09/2026 / common.py - Tidy up of Game Modes]**
>Another big one, but this time it's all about cleanup. Every game with multiple modes (Pong, SPR, Guess Number, Memory) had the same problem: copy-pasted code. Memory Match was the worst of all. It had three mode files each containing their own card grid logic, menu drawing, and event handling, with minor tweaks between them. It worked, but changing anything meant fixing it in three places.
>
>**The fix:** Each multi-mode game now has a `common.py` that holds everything the modes share:
>- **Pong** - `paddle_bounce()`, `wall_bounce()`, `draw_pong_board()`, and `PongBaseMode` with shared `_update_ball()`, `_check_paddle_hit_left/right()`, and `_check_scoring()`. The AI and 2P modes now just set up their paddles and call the base methods. 50 lines of mode-specifics each vs. 100+ lines of copy-pasted physics.
>- **Memory Match** - `MemoryBaseMode` handles the entire card grid: flipping, matching, menu drawing, scroll wheel support, game-over overlay. The three modes (`mode_1p.py`, `mode_2p.py`, `mode_ai.py`) only override `_on_match()`, `_on_mismatch()`, `_check_game_over()`, and a few HUD helpers. Mode 1P dropped from 200+ lines to 40. Mode AI went from a tangled mess of "is it my turn yet?" logic to a clean 77 lines with just `_execute_ai_turn()`.
>- **SPR** - `evaluate_round()`, `draw_title_bar()`, `draw_main_card()`, `draw_game_over_results()`, and `SPRBaseMode` with shared event routing. The 2P and AI modes now only define their key mappings, playing-state UI, and round resolution. No more duplicated "Scissors beats Paper" logic in two files.
>- **Guess Number** - `GuessNumBaseMode` with shared input validation, difficulty buttons, and the typing/backspace logic. `GuessNumUI` provides static drawing helpers. The AI mode and Local 2P mode just plug in their own flow (coin flip for 2P, immediate start for AI).
>
>Breakout only has one mode so it didn't need the treatment, and Tetris already had a shared `Board` class that both modes imported,that was the template I followed for everything else.
>
>**What I learned:** If you're copy-pasting between files and changing three things each time, you don't have three modes, it is one mode and two variations. A shared base class with override points is way easier to maintain than three nearly-identical files. Memory's `_on_match()/_on_mismatch()/_check_game_over()` hooks are a good pattern: the base does the heavy lifting, the subclasses just define what *happens* when things turn on.
>
>**Still to do:** Settings screen, Scoreboard, stat saving.
>**Problems to fix:** pong and breakout ball reset positioning 

**Stage 12 - [16/09/2026 / Settings + Scoreboard screen & Username Stat Saving]**
>Big session today. finally filled in two major placeholders that have been staring at me for a few days now. The arcade box now has a proper settings system and a scoreboard that actually shows something useful, though not without running into some tricky state machine bugs along the way.

**Settings Menu - Context-Aware Audio & Controls**  
>The old settings screen was literally three lines of placeholder text. Now it's a full two-tab interface (General and Controls) that saves per-context settings to JSON files in `data/settings/`. The key insight here is "context", if you open settings from the main menu, you're tweaking main menu volume. If you open it from inside Tetris (via pause menu), you're tweaking Tetris-specific volume and controls. Same for any other game.
>
- **General tab:** SFX Volume slider (0-100%) with ON/OFF toggle, Music Volume slider (0-100%) with ON/OFF toggle, and a "Learn more?" button that loads context-appropriate info from `src/info/*.txt` files into a scrollable popup window.
- **Controls tab:** Shows key bindings for the current context. Main menu just says "uses default navigation", but games show their actual bindings (Pong shows P1/P2 up/down, Tetris shows movement/rotate/drop, etc.). Clicking a binding waits 5 seconds for you to press a new key.
- All settings save to JSON files named like `main_menu.json`, `tetris_settings.json`, `pong_settings.json`, etc. The audio settings apply immediately via `pygame.mixer` — music volume uses the MusicManager's `set_volume()`, and SFX toggles actually stop/start playback. Documentation for mixer methods came from [https://www.pygame.org/docs/ref/mixer.html](https://www.pygame.org/docs/ref/mixer.html), which I used for getting the volume chaining (`Sound.set_volume` × `Channel.set_volume` = final volume).

**Scoreboard - Username-Based Stats Display**  
The scoreboard used to say "Coming soon". Now, when you press T on a game in the carousel, it loads that game's stats JSON and displays the top 10 players by score. The display shows rank, username, score, and games played in a clean table format, with top 3 ranks getting gold highlighting.

**How Stats Work Now (Username System)**  
Here's the flow: When a player launches a game, they first see a name entry screen (max 12 characters). They type their name and confirm. That username becomes their identifier for this session. When they exit the game, their score gets saved to `data/[game]_stats.json` under their username key. The JSON structure looks like:

{
  "Zen": { "score": 1500, "games_played": 1 },
  "Tim": { "score": 800, "games_played": 3 }
}

Next time the player opens the scoreboard from the main menu, they'll see their name ranked against others. Different games have different stat fields (Tetris uses `score`, Pong might use `wins`, etc.), but the scoreboard adapts by checking for common field names.

**Challenges & Bug Fixes Encountered**  
While implementing this, I asked for help because pressing **S** on the carousel wasn't bringing up the settings screen at all. No crash, no error, it just did nothing. Same with **T** for the scoreboard. It turned out `settings_menu.py` was fine; the actual bug was in `main.py`'s state transition logic.

- **The silent `pass`:** Found this in `main.py`: `if isinstance(next_obj, GameBase) or hasattr(next_obj, "startup"): ... else: pass`. That `pass` was doing exactly what it says: nothing. `carousel._open_settings()` and `_open_scoreboard()` both set `next_state` to a plain string (`"SETTINGS"` / `"SCOREBOARD"`), not a game object, so it fell straight into the `else` branch and got quietly swallowed. Changed it to check `isinstance(next_obj, str) and next_obj in state_machine.states` and call `state_machine.change(next_obj, persist)`.
- **Pause menu dead end:** Opening Settings from the pause menu (**S** while paused) was also just sitting there doing nothing. `GameWrapperState` was correctly setting `game_wrapper.done = True` and `game_wrapper.next_state = "SETTINGS"`, but `main.py`'s loop only ever checked for `"MAIN_MENU"`. Added the missing `elif` to handle this transition.
- **Accidental app quit:** While tracing through that, I found a nastier bug: the ESC-quits-the-app check on the carousel only checked `mode_select`, not `name_entry`. So if you pressed ESC while typing your player name (meant to cancel back to the carousel), it quit the entire application instead. Added `and not carousel.name_entry` to that check.
- **Module path mismatch:** In `carousel_menu.py`'s direct-launch path for games without a `MODES` dict (like Breakout), the check `attr.__module__ == f"{module_prefix}.__init__"` could never be true, because a class defined directly inside a package's `__init__.py` has `__module__` equal to the package path itself. Changed the comparison to just `attr.__module__ == module_prefix`.
- **Blank UI polish:** The Controls tab was blank for Guess Number and Memory Match since neither has bindings set up in `_init_ui`. Added a "no custom key bindings yet" message so it's not an empty, broken-looking box.

**Files Changed/Created:**

- `src/menu/settings_menu.py` — Complete rewrite: tabs, volume sliders, toggles, binding UI, Learn more popup, JSON save/load, and added "no custom key bindings yet" message for applicable games.
- `src/menu/scoreboard.py` — Complete rewrite: loads game-specific stats JSON, displays top 10 leaderboard.
- `src/menu/carousel_menu.py` — Added `_open_scoreboard()` and `_open_settings()` methods, wired **T** and **S** keys, fixed `__module__` check in the mode-less direct-launch path.
- `src/menu/pause_menu.py` — Updated `handle_key()` to return game context tuple for settings navigation.
- `main.py` — Fixed carousel → SETTINGS/SCOREBOARD transition (was a dead `pass`), game wrapper → SETTINGS transition (was missing entirely), ESC-quits-app check now also respects `name_entry` being open, added SETTINGS and SCOREBOARD states to state machine.
- `data/settings/` — New directory created automatically for storing per-context settings JSON files.

**What I learned:**  
Context matters. A "one size fits all" settings file would've been easier but wrong — users expect their Tetris controls to be separate from Pong controls, and main menu volume to be independent of game volume. The pygame.mixer documentation was essential for understanding how Sound volumes chain with Channel volumes and music volumes. JSON is way better than `.npy` for stats when you want human-readable files that can store named entries (usernames).  
Furthermore, a state machine is only as good as the code watching for its transitions. `SettingsMenu`, `Scoreboard`, `carousel.done`/`next_state` were all written correctly, but `main.py`'s dispatcher had one dead `pass` and one missing `elif`, which was enough to make two entire screens act like they didn't exist. It's worth actually testing _every_ entry point (carousel AND pause menu) after wiring up a new screen, instead of just the one I remembered to try.

**Still to do:**
- Make each game save stats on exit with the username.
- Fix per-game settings menu so they persist correctly across sessions.
- _Known limitation:_ Settings opened from the pause menu dumps you back to the main carousel on Back/Save/Enter instead of resuming the paused game underneath (same as Scoreboard already does). Didn't touch that yet, since it'd mean changing what `GameWrapperState.cleanup()` does to a mid-game session, and I don't want to guess at that without checking what each game's own `cleanup()` does first.

**Stage 13 - [18/09/2026 / Mode Difficulty Menu]**
Making & Updating Difficulties of games for further layer of depth.
>Pong:
- Classic - Basic AI + normal ball movement
- Advanced - Fast randomised ball movement + Basic AI
- Hell - Ball speed +1 every time hit by paddle, resets on death + Better AI with better ball detection

Breakout:

Memory Match:
Difficulties already made, need to update ai of game. 

Need to make general `difficulty_select.py` to select same way as per mode select. Instead of being inside of `/*game` it will be inside `/*game/difficulties/*difficulty.py`. For example, Pong will be `/pong/diffuculties/` inside it would be `/diff_1.py`, `/diff_2.py`, `/diff_3.py`. Then the buttons would be displayed the same way as per the `__init__.py` files, we can simply add 
>DIFFICULTIES = {
"Classic": "diff_1",
"Advanced": "diff_2",
"Hell": "diff_3",
}


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