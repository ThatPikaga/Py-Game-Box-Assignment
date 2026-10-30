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
An original desktop arcade collection built with Pygame. The current build has a carousel for Pong, Scissors-Paper-Rock, Guess Number, Breakout, Memory Match, and Tetris. Game folders are discovered automatically, and cover art, sound effects, and music live beside each game's Python files. Players can enter a username and view saved results in a scoreboard overlay.

---
<div style="page-break-after: always;"></div>
### Essential Features
- **Core games** working with basic graphics, sound, and controls.
- **Three play modes** per game: human vs. human, human vs. AI, and pure single‑player where applicable (for games like Breakout). Modes are auto-detected from each game's `__init__.py` — the carousel shows a mode selection screen with buttons built automatically.
- **Menus and navigation**:
  - **Main Menu**: A carousel game select, navigated via left/right arrow keys. Press **E** on a selected game to launch; if the game has multiple modes, a mode select screen appears first.
  - **Pause Menu**: Press **ESC** during a game to open the shared pause overlay. It can resume, return to the carousel, or open Settings.
  - **Settings**: Press **S** on the carousel or from the pause menu to change sound/music volume, enable or disable audio, and view controls.
  - **Scoreboard**: Press **T** while a game is selected in the carousel to view that game's saved results in an overlay. Press **ESC** or select **Back** to return to the same carousel.
- **Automatic game and asset discovery**: the launcher scans `src/games/` for game folders, finds cover art ending in `_boxcover.png` or `_boxcover.jpg`, and loads each game's own root-level sounds and music. Missing cover art uses a placeholder.
- **Modular code architecture**: each game mode can extend `GameBase` from `src/core/game_base.py`. Modes are separate `.py` files inside each game's folder (`mode_1p.py`, `mode_2p.py`, `mode_ai.py`).
---

### Add‑ons (If time bids)
1. Advanced split‑screen: two‑player race mode in Breakout with independent surfaces/screens.
2. Enhanced AI humanisation: adjustable difficulty (reaction delay, occasional misses) for Pong and Breakout; adaptive counter‑strategy.
3. Breakout power‑ups: timed items (wider paddle, extra ball, laser) drop from broken bricks, with visual and sound effects.
4. Random Breakout level generator to avoid repetitive brick layouts.
5. More games: e.g., Snake, Space Invaders/Galaga, Flappy Bird clone.
6. Full arcade‑style attract mode: demo loops when idle – perhaps just get the macro “AI” to play against itself.

<div style="page-break-after: always;"></div>

### Current File Structure

The original project plan has changed as the launcher has been built. The working layout is now:

```text
code/
├── main.py                    # Starts Pygame and connects the screens
├── settings.py                # Window and launcher settings
├── assets_loader.py           # Discovers games and loads their assets
├── assets/
│   ├── fonts/                 # Fonts used by menu screens
│   ├── gui/backgrounds/       # Launcher background
│   └── sfx/                   # Launcher menu sounds and main_theme.wav
├── data/                      # Saved JSON results and settings
└── src/
    ├── core/                  # GameBase, constants, discovery and stats
    ├── engine/                # State manager, input and music manager
    ├── menu/                  # Carousel, settings, pause and scoreboard screens
    └── games/
        ├── breakout/
        ├── guess_number/
        ├── memory/
        ├── pong/
        ├── spr/
        └── tetris/
```

Each folder under `src/games/` owns its game code, cover art, sound effects and optional music. For the full instructions to add a game, read `code/structure.txt`.

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

Added a MusicManager in src/engine/music_manager.py that handles the menu theme and game-specific music switching. It uses pygame.mixer.music so it's lightweight — no threading needed, just plays on top of the game loop. The carousel menu starts the main_theme.wav, and whenever a game launches the wrapper swaps to that game's track (breakout.wav, tetris.wav, etc.). On the SFX side I wired in sounds for Tetris (line clear = num_correct.wav, game over = life_lost.wav), Breakout (paddle hits, brick breaks, powerup collects, life lost), Guess Number (correct/wrong), Scissors Paper Rock (selection confirm), and Memory Match (card flip up/down, match found/wrong). Pong is missing its SFX file still so that one just has nothing play for now, but the placeholders are set up so once I get the pong.wav (the SFX one, not the music one) it'll just work.

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


**What I learned:**  
The pygame.mixer documentation was essential for understanding how Sound volumes chain with Channel volumes and music volumes. A state machine is only as good as the code watching for its transitions. `SettingsMenu`, `Scoreboard`, `carousel.done`/`next_state` were all written correctly, but `main.py`'s dispatcher had one dead `pass` and one missing `elif`, which was enough to make two entire screens act like they didn't exist. It's worth actually testing _every_ entry point (carousel AND pause menu) after wiring up a new screen.

**Still to do:**
- Make each game save stats on exit with the username.
- _Known limitation:_ Settings opened from the pause menu dumps you back to the main carousel on Back/Save/Enter instead of resuming the paused game underneath (same as Scoreboard already does). Need to update it to be an overlay... not changed state.



**Stage 13 - [18/09/2026 / Mode Difficulty Menu + pong update]**
>Making & Updating Difficulties of games for further layer of depth.
>Pong:
> - Classic - Basic AI + normal ball movement
> - Advanced - Fast randomised ball movement + Basic AI
> - Hell - Ball speed +1 every time hit by paddle, resets on death + Better AI with better ball detection

>Made the general `difficulty_select.py` to select same way as per mode select. Instead of being inside of `/*game` it will be inside `/*game/difficulties/*difficulty.py`. For example, Pong will be `/pong/diffuculties/` inside it would be `/diff_1.py`, `/diff_2.py`, `/diff_3.py`. Then the buttons would be displayed the same way as per the `__init__.py` files, we can simply add in:
>```
	DIFFICULTIES = {
	"Classic": "diff_1",
	"Advanced": "diff_2",
	"Hell": "diff_3",
	} ```

>This system was added in for Pong — difficulty select now shows right after mode select, confirmed that's the order I wanted it in. Reused `mode_select.py`'s exact pattern like planned: `difficulty_select.py` reads a `DIFFICULTIES` dictionary and builds buttons the same way, and `src/games/pong/difficulties/__init__.py` exports `DIFFICULTIES = {"Classic": "diff_1", "Advanced": "diff_2", "Hell": "diff_3"}` just like the plan said.

>**Keeping each difficulty down to a few lines**
>I like to keep my code minimised where possible, and object oriented — making a difficulty file isn't a rewritten game, it's just a handful of overridden class attributes. I've made a `Difficulty` base class (`src/core/difficulty_base.py`, engine-level so any future game's difficulties can reuse it) with just `name`/`description`, then a `PongDifficulty` subclass 
>(`src/games/pong/difficulties/_base.py`) with Pong's actual tuning knobs and sane defaults. `diff_1.py` (Classic) barely has to override anything:

>```python
>class Difficulty(PongDifficulty):
>    name = "Classic"
>    description = "Basic AI, steady ball speed. Good for learning the ropes."
>```
>`diff_2.py` (Advanced) just bumps `ball_base_speed` and flips `randomise_ball` on. `diff_3.py` (Hell) is the only one that touches the AI fields so far.

>**Wiring it up**
>`carousel_menu.py` now holds onto the mode instance I just built (`pending_launch_instance`) and checks `{module_prefix}.difficulties` for a `DIFFICULTIES` dictionary before launching. If there isn't one, it launches exactly like before, which is why Breakout, Memory Match etc. are completely unaffected until they get their own `difficulties/` folder. If there is one, it shows `DifficultySelectScreen`, and once a difficulty's picked it just gets slapped onto the mode instance as `mode_instance.difficulty = diff_obj` before launch. `PongBaseMode._apply_difficulty()` (called from `mode_ai.py`/`mode_2p.py`'s own `startup()`) reads that off and sets ball speed + AI tuning from it.

>**Making the ball/AI actually difficulty-aware**
>`paddle_bounce()` used to always normalise the ball to the fixed `TOTAL_SPEED` constant on every single bounce, which would've completely ignored any difficulty's ball speed and made "+1 speed every hit" impossible. Gave it optional `total_speed`/`bounce_speed` params (default exactly matches the old hardcoded behaviour, so Breakout, which also reads `TOTAL_SPEED`/`BOUNCE_SPEED` from `constants.py`, isn't affected at all). `PongBaseMode` now tracks `_current_speed` (ramps up in `_on_paddle_hit()` when `difficulty.speed_up_on_hit` is set) and `_base_speed` (what `reset_ball()` puts it back to — `reset_ball()` already runs on every single score, so "resets on death" came for free).

>**The AI — keeping Hell beatable**
>Classic and Advanced both use the exact same "Basic AI" as before (`ai.py`'s original chase-the-ball's-current-y logic, untouched). Hell turns on `predictive=True`, which works out where the ball will actually BE by the time it reaches the paddle, including bouncing the prediction off the top/bottom walls in the maths. On its own that'd be a perfect wall, so two things keep it beatable: `ai_error=14` mixes a few px of random misjudgement into the target every frame, and the AI only starts predicting once the ball's actually heading its way — if it's moving away, the AI just drifts back to the middle instead of camping the exact spot, so an angled return shot has room to work. Paddle speed's still capped too (`ai_speed=9`), so a sharp angle late in a sped-up Hell rally can still outrun it.

>**Files changed/created this stage:**
>- `src/core/difficulty_base.py` — new: generic `Difficulty` base class (name + description)
>- `src/menu/difficulty_select.py` — new: `DifficultySelectScreen`, same pattern as `mode_select.py`
>- `src/games/pong/difficulties/__init__.py` — new: `DIFFICULTIES` dict
>- `src/games/pong/difficulties/_base.py` — new: `PongDifficulty` shared defaults
>- `src/games/pong/difficulties/diff_1.py`, `diff_2.py`, `diff_3.py` — new: Classic/Advanced/Hell
>- `src/games/pong/ai.py` — rewritten: added predictive targeting + error for Hell, Basic mode untouched
>- `src/games/pong/common.py` — `paddle_bounce()` takes optional `total_speed`/`bounce_speed`; `PongBaseMode` gained `_apply_difficulty()`, `_on_paddle_hit()`, and a difficulty-aware `reset_ball()`
>- `src/games/pong/mode_ai.py` / `mode_2p.py` — call `_apply_difficulty()` in `startup()`; `mode_ai.py` also feeds the AI ball velocity + screen height now
>- `src/menu/carousel_menu.py` — mode select now routes through a difficulty check before launching (`_has_difficulties`, `_proceed_to_difficulty_or_launch`), `__module__` bug fixed again
>- `main.py` — `difficulty_select` added to the ESC-quits-app guard

>**Still to do:** Breakout and the rest still need their own `difficulties/` folders. The pattern's the same (a `_base.py` with defaults, `diff_N.py` files overriding a few attributes, a `DIFFICULTIES` dict in `__init__.py`) but the actual numbers depend on what each game's AI/physics. Memory Match already has difficulties made and just needs to be updated to use them before we can start upgrading its Ai.

>**Follow-up - player paddle speed** - [24/09/2026]
>Turned out changing numbers in the difficulty files wasn't doing anything to the player's own paddle - it was still moving at a flat speed no matter what. Reason: `mode_ai.py` and `mode_2p.py` were moving the player paddle with the hardcoded `TOTAL_SPEED` constant straight from `constants.py` (`self.player.y -= TOTAL_SPEED`). Every other speed in this system (ball, AI) went through `self.difficulty`, but player movement was never wired up to it at all.

>Digging into `constants.py` to figure out the least messy way to fix this, found `PADDLE_MAX_SPEED = 8` just sitting there completely unused. `TOTAL_SPEED` was doing double duty the whole time — ball physics AND player paddle movement — which is really two unrelated things that happened to share the same number (8) by coincidence💀. Rather than keep overloading `TOTAL_SPEED` (which still needs to stay put for the ball - `paddle_bounce()`/`BOUNCE_SPEED` depend on it), I gave the player paddle its own dedicated `paddle_speed` field on `PongDifficulty`, defaulting to `PADDLE_MAX_SPEED` when no difficulty's attached. Same pattern as everything else this stage: `_apply_difficulty()` pulls it off `self.difficulty` in `startup()`, mode files just read `self.paddle_speed` instead of the constant directly.

>**Why this needed its own value per difficulty** 
>This is really about giving the player a fair fight, not just "more depth". On Hell, `ai_speed` was already set to 9 - meaning the AI could out-move the player paddle, which was stuck at the old flat 8, on top of the AI being predictive and the ball constantly speeding up. That combination is what was making Hell feel nearly impossible - the AI had a genuine raw-speed advantage before the smarter targeting even came into it. Set `paddle_speed` to 10 for Hell specifically (faster than the AI's own 9) so the player's raw moevemtns are actually ahead, and the AI's edge comes entirely from prediction/ball speed rather than just being able to physically outrun the player too. 

>**Files changed in this small variable change:**
>- `src/games/pong/difficulties/_base.py` — added `paddle_speed` (default `8`, matches `PADDLE_MAX_SPEED`)
>- `src/games/pong/common.py` — `PongBaseMode` now tracks `self.paddle_speed`, set in `_apply_difficulty()`
>- `src/games/pong/mode_ai.py`, `mode_2p.py` — player (and P1/P2) movement reads `self.paddle_speed` instead of the `TOTAL_SPEED` constant directly

> **Changes still to be made in Pong:**
> - Fix ball reset. Ball must launch outward from centre of player paddle via use of Space key (enter for P2)
> - Add SFX

> **General Updates still to be made**
> - Update all other games to include new difficulty system
> - Fix settings implementation (make overlay instead of change state😅) 
> - Apply universal custom font - https://www.pygame.org/docs/ref/font.html 

**Universal Custom Font & Tetris Refactor** - [24/09/2026]
> Finally tackled the custom font implementation and did some much-needed housekeeping on the Tetris files👀.
> 
> **The Font Situation:** I made my `constants.py` set up with `title_font()`, `body_font()`, and `header_font()` helpers pointing to "Press Start 2P", but _none_ of the menu or game files were actually using them. Every single screen was still hardcoding `pygame.font.Font(None, ...)` which explicitly tells Pygame to ignore the custom font and use the system default. Also had a crash on startup because `assets_loader.py` was missing the `"fonts": {}` dictionary key, and `constants.py` was trying to use `path.join` without importing `os` — took a solid 15 minutes to figure that out.
> 
> **The Fix:** I went through every menu (`carousel_menu.py`, `mode_select.py`, `difficulty_select.py`, `scoreboard.py`, `settings_menu.py`, `pause_menu.py`, `name_entry.py`) and the SPR game files, swapping out the hardcoded `None` calls for the centralised helper functions. Now, changing the font or its sizes in `constants.py` acts as the single source of truth and updates the entire arcade box instantly.
> 
> **Tetris Refactor (Goodbye 500-line files🥹):** Tetris was the only game without a `common.py`, resulting in `mode_1p.py` and `mode_2p.py` being bloated with duplicated `Board` logic and grid-drawing code — completely forgot to updated it. Extracted the entire `Board` class (piece spawning, rotation, wall-kicks, line clearing) and a `draw_board_grid_and_pieces()` helper into a new `src/games/tetris/common.py`. This chopped the mode files down significantly and makes the 2P mode much cleaner since it just imports the shared board and drawing logic. Applied the new custom fonts to Tetris while I was in there.

> **Changes still to be made in Pong:**
> 
> - Fix ball reset. Ball must launch outward from centre of player paddle via use of Space key (enter for P2)
> - Add SFX

> **General Updates still to be made**
> 
> - Update all other games to include new difficulty system
> - Fix settings implementation



**Stage 14 - [15/10/2026 - 17/10/2026 / Difficulty Expansion, Settings Overlay & Pong SFX]**
> Finally rolled out the difficulty system to the rest of the arcade box. Following the pattern I established for Pong  (inside of a dedicated difficulties folder with `__init__.py `, `_base.py` and `dif_x.py` files ), I added the `difficulties/` folder to Memory, Breakout, Guess Number, Scissors Paper Rock, and Tetris. Each of these now features Easy, Medium, and Hard options that adjust some sort of game variable. There was also a quick fix within pong where I had no sound. No sound was occurring at any stage because while I had the files linked, I never had them called or woken up which kept them in switched off state.

> **Game-specific difficulty tuning details**
> 
> - **Memory Match:** The Ai now saves the cards that are flipped over each time (matched pairs are not saved). For each difficulty the AI will have a memory cap — easy forgets cards seen after 2, and for something like Hard it will remember up to 8 cards — which will add a level of flair on top of simply varied board sizes. After that was done, because I have now changed to a custom font by Google, I had to adjust text sizes in `common.py` so the labels actually fit the screen without clipping.

> - **Tetris:** In two-player mode, clearing rows now sends a corresponding number of garbage rows to the opponent's board, pushing their stack up which will create a level of pressure, requiring faster thinking. Difficulty also scales the starting fall speed, making higher difficulties genuinely frantic.

> - **Breakout:** Difficulty now changes base lives, paddle speed, and ball speed. I also updated the game over screen seeing as I had left it as a simple clear board after the last life was lost and start again. I have now made it so the player actually sees what they achieved. This game much like the rest — except for memory match — still does not have any form of replaying from after game over. There is only back to main menu thus resulting in needing to re-select the game.

> - **Guess Number:** The difficulty selector directly controls the number of allowed guesses, making "Hard" actually challenging.

> - **Scissors Paper Rock:** The AI difficulty now adjusts the probability of the AI deliberately choosing a move that counters the player's current move, rather than relying entirely on random selection between the three possible moves. Although this change itself was simple to implement, it adds another layer of difficulty to the game. I do have ideas for making the AI more advanced, such as developing a prediction-based system that analyses patterns in the player's previous choices to estimate what they might choose next. However, implementing something like this would be a much more time-consuming task, and I can imagine it becoming quite frustrating to develop. For now, I'll spare myself the brain damage and keep things simple. To avoid spending an excessive amount of time and code on this single feature, I used a straightforward probability check to see if the AI should counter the player's move or choose one at random. 
> code snippet: 
> ```
> counter_chance = getattr(self.difficulty, "counter_chance", 0.0)
> if random.random() < counter_chance:
	winning_moves = {"Scissors": "Rock", "Paper": "Scissors", "Rock": "Paper"}
	self.ai_choice = winning_moves[player_choice]
else:
	self.ai_choice = random_ai_choice()
	```
	Also took the liberty of 
> 
> **Settings Overlay Fix** I finally tackled the annoying bug where opening settings from the pause menu would dump you back to the the carousel state. I reworked `settings_menu.py` to act as a dimmed overlay on top of the current screen (using the same alpha-surface dimming technique). Closing it now seamlessly returns you to the exact menu or paused game you were in, instead of replacing the state entirely.
> 
> **What I learned:**  
> Consistency is key. Reusing the `difficulty_select.py` pattern across all games saved me hours of rewriting menu logic. Also, treating UI elements like Settings as overlays rather than state changes makes the application feel much more cohesive and professional.
> 
> **Still to do:**
> 
> - Center the stat saving so each game doesn't need its own save code💀.
> - Make the carousel automatically discover new games without a hardcoded registry.
> 
> **Files changed/created this stage:**
> 
> - `src/games/breakout/difficulties/` — new: Easy, Medium, Hard configs
> - `src/games/guess_number/difficulties/` — new: Easy, Medium, Hard configs
> - `src/games/spr/difficulties/` — new: Easy, Medium, Hard configs
> - `src/games/tetris/difficulties/` — new: Easy, Medium, Hard configs
> - `src/menu/settings_menu.py` — rewritten: now functions as a dimmed overlay instead of a state replacement
> - `src/games/memory/common.py` — adjusted UI text scaling

**Stage 15 - [16/10/2026 - 17/10/2026 / Stats Saving & Documentation]**
> I've gotten a grasp of the whole stat saving problem. Up until now, saving results was a bit of a mess, with each game sort of doing its own thing seeing as I had not planned this far into the project. I built dedicated `src/core/stats.py` module to handle all of this in one place.
> 
> **Unified Stats System**
> When a game closes, it now passes its current result data to this central handler, which saves it under the player's entered username into a dedicated JSON file in `code/data/`. The structure tracks the best score, last score, total games played, win count, and the last played mode. I wired this up across Breakout, Guess Number, Memory Match, Pong, Scissors Paper Rock, and Tetris. The Scoreboard screen now reads directly from these `*_stats.json` files, meaning the leaderboard finally shows the save data!
> 
> **Documentation Cleanup** 
> I updated `code/structure.txt` to be a proper manual. It now includes clear instructions on how to navigate the folder structure, locate controls and assets, and most importantly, a step-by-step guide on how to add a new game or difficulty using the current loader. I also renamed this entire development log to `README.md` so it's the first thing anyone sees when opening the project folder.
> 
> **What I learned:**  
>  Centering repetitive logic into a single place prevents tedious bugs and makes adding new games much easier. If a new game just needs to call `save_stats(username, data)` I don't have to worry about it corrupting the JSON or using the wrong path.
> 
> **Still to do:**
> 
> - Remove the hardcoded `GAME_REGISTRY` and make the launcher auto-discover games.
> - Convert the Scoreboard to an overlay to match the new Settings behavior so that if a user opens and closes the scoreboard for a game, it stays on that game in the carousel menu.
> 
> **Files changed/created this stage:**
> 
> - `src/core/stats.py` — new: centralized stat saving and loading logic
> - `code/data/` — updated: now properly populated with `*_stats.json` files per game
> - `code/structure.txt` — expanded: added comprehensive game-maker and user guide
> - `README.md` — renamed from the development log for better visibility

**Stage 16 - [17/10/2026 / Automatic Game Discovery & Asset Restructuring]**
> This was a major quality-of-life upgrade for the entire architecture. I completely removed the hardcoded `GAME_REGISTRY` from `settings.py`.
> 
> The carousel menu now scans `code/src/games/` for any folder containing an `__init__.py`. It reads the `GAME_NAME` and `MODES` attributes directly from that package. This means the carousel automatically laods with new games the moment their folder is created and structured correctly. No more manual registry configurationm makes the system a much nicer experience for any third party user.
> 
> I also reorganised the way assets work, to be modular. Each game folder now owns its own `*_boxcover.png` (or `.jpg`/`.jpeg`). The `assets_loader.py` scans for these and applies a placeholder if one is missing. More importantly, I moved all game-specific sound effects and music tracks directly into their respective game folders. Only the core launcher navigation sounds and `main_theme.wav` remain in the shared `assets/sfx/` directory. This change takes away yet again, the need to manually wire sounds.
> 
> As for the audio and scoreboard, the settings audio sliders now correctly iterate through and update all loaded game sounds, not just the menu ones. The MusicManager also dynamically looks for `music.wav` or `<folder>_music.wav` without needing a hardcoded dictionary. For the scoreboard, I added a fallback. if a new game doesn't have a traditional "score", it can implement a `get_scoreboard_data()` method to return a custom unit (like "Highest Wave" or "Fastest Time"), ensuring the leaderboard always has something meaningful to display.
> 
> Modularity means a new game should require zero changes to the core engine — that's just pain blatantly annoying and should only be used in a static scenario.
> By relying on consistent naming and `__init__.py` exports, the launcher remains completely separate from what games are actually installed.
> 
> **Still to do:**
> - Convert the Scoreboard to an overlay to match the Settings menu.
> 
> **Files changed/created this stage:**
> 
> - `assets_loader.py` — rewritten: dynamic folder scanning for games, covers, and local audio
> - `src/games/*/` — updated: moved SFX and music into individual game directories, added box art
> - `src/core/stats.py` — updated: added support for custom `get_scoreboard_data()` metrics
> - `code/structure.txt` — updated: added the new "Game Maker Guide" for auto-discovery


**Stage 17 - [18/10/2026 / Scoreboard Overlay & Final Polish]**
> Finished the last major UI inconsistency. The original Scoreboard replaced the current state entirely, meaning returning from it could lose the exact screen the player had open (like a paused game). Since I already solved this for the Settings menu, I applied the exact same overlay pattern to the Scoreboard.
> 
> **Overlay Implementation** In `main.py`, I added a `scoreboard_overlay` flag. When active, the event loop routes input to the overlay, and the draw loop renders it _after_ the current menu or game, complete with a dimmed background surface and a bordered panel. Both the Back button and the Escape key cleanly close the overlay by clearing the flag and resetting its finished status, leaving the underlying carousel or paused game exactly as it was. I also removed both Settings and Scoreboard from the state manager's list of normal states, as they are no longer states at all.
> 
> **Rubric & Documentation Check** I updated the user guide and this README to document the new overlay behavior. I also did a final pass against the project rubric, ensuring useful variable names, purposeful comments, modular structure, usability, and a visible testing log are all present and accounted for. Updated `structure.txt` to clearly explain how to add a game without needing to read every single source file 😅.
> 
> **What I learned:**  
> Consistency in UI patterns drastically improves the perceived quality of an application. Having both Settings and Scoreboard behave as non-destructive overlays makes the arcade box feel like a cohesive, professional product rather than a collection of disjointed scripts.
> 
> **Still to do:**
> 
> - Final live testing of keyboard flow, volume sliders, and visual layout on a machine with Pygame installed.
> 
> **Files changed/created this stage:**
> 
> - `main.py` — updated: added `scoreboard_overlay` flag and overlay draw routing
> - `src/menu/scoreboard.py` — rewritten: now renders as a dimmed overlay panel instead of a standalone state
> - `code/structure.txt` & `README.md` — updated: final documentation and rubric checks

**Stage 18 - [18/10/2026 / Configurable Screen Size & Scaling]**

> As a final polish, I want to ensure the arcade box isn't locked into a single rigid resolution. I made `SCREEN_WIDTH` and `SCREEN_HEIGHT` in `src/core/constants.py` the single source of truth for the window size. While I had intended for this at the start of this project, I found myself forgetting about it when creating a few of the games
> 
> **Dynamic Scaling Helpers** Simply changing the resolution isn't enough if all the UI elements and game objects are hardcoded to specific pixel coordinates. I added `scale_x()`, `scale_y()`, and `scale_size()` helper functions in `constants.py`. These automatically calculate proportions based on the original 1030 x 1030 base design. I went through the carousel, menu overlays, name entry, and game play areas, replacing hardcoded coordinates with these helpers. This ensures fonts, square game pieces, and UI panels scale perfectly regardless of the chosen resolution.
> 
> **Speed Adjustments** I also noticed that movement speeds in Breakout and Pong were still using fixed pixels-per-frame values. Even if the paddle was scaled up, it would move at the same absolute speed, making the game feel sluggish at higher resolutions. I updated these difficulty speed values to also apply the `scale_size()` ratio, keeping the gameplay feel consistent across all resolutions.
> 
> **Screen Size Change: Quick Test Log**
> 
> - **Shared resolution settings:** Code-path check passed. `main.py` correctly uses the shared constants.
> - **Layout scaling:** Simulated calculations for 1030x1030, 1280x720, and 800x600. Scaling values changed appropriately while maintaining a 1.0 scale for the base design.
> - **Game movement:** Verified that Breakout and Pong difficulty speeds now correctly apply the `scale_size()` ratio.
> - **Python syntax:** `python -m compileall` passed with no errors.
> - **Full visual run:** Not run in this workspace due to missing Pygame installation. Requires a live test on a machine with project requirements installed.
> 
> **What I learned:**  
> Responsive design in Pygame is entirely possible without a massive refactor, well, that is if you throw in a few scaling helpers and rigorously replace those magic numbers with proportional calculations of course.
> 
> **Still to do:**
> 
> - Nothing except creating how to play/use info for games and main menu — additional games if I want, or any further enhancements
> 
> **Files changed/created this stage:**
> 
> - `src/core/constants.py` — updated: added `scale_x`, `scale_y`, `scale_size` helpers and unified `SCREEN_WIDTH`/`SCREEN_HEIGHT`
> - `src/menu/` & `src/games/` — updated: replaced hardcoded coordinates and speeds with scaling helpers
> - `code/structure.txt` — updated: added instructions on how to safely change the screen resolution

**Stage 19 - [18/10/2026 / Play Again Flow & Game Information]**

> I noticed that finishing a game often left the player with a way to return to the main menu, rather than a clear replay flow. I changed this so the end screen can offer **Play Again**, which returns to that game's mode selection. The existing username is kept in the shared persist data, so the name-entry screen is only shown for the first session and is skipped when a player replays or chooses another game.
>
> **Replay State Flow** The game wrapper now recognises a `PLAY_AGAIN` transition. It returns to the carousel state while carrying the completed game's name as replay context, and the carousel reopens that game's mode selector instead of the main carousel. The selected mode then follows the normal difficulty selection flow again. This keeps mode and difficulty selection in the same sequence as starting a game for the first time.
>
> **Game-Over Controls** Added visible Play Again buttons and keyboard shortcuts to the end screens for Memory Match, Guess Number, Scissors Paper Rock, Breakout, and both Tetris modes. Pong previously had no match end, so both its single-player-versus-AI and local two-player modes now finish when a side reaches five points and show a shared result overlay with Play Again.
>
> **Game Information Files** Replaced the placeholder text in each file under `src/info/` with relevant instructions for the main menu, Breakout, Guess Number, Memory Match, Pong, Scissors Paper Rock, and Tetris.
>
> **Testing**
>
> - **Transition review:** Checked the launcher and carousel routing so Play Again preserves the username and reopens the correct game's mode selector.
> - **Source review:** Checked the updated game-over event paths and button drawing code.
> - **Full visual run:** Not run in this environment; a live Pygame test is still needed to verify layout and interaction at runtime.
>
> **What I learned:** A replay action is more than restarting the current object. It needs to return to the correct point in the application's state flow, reset the game cleanly, and preserve session information that should not be requested again.
>
> **Still to do:**
>
> - Perform a full interactive test of every game's Play Again button and mode/difficulty selection on a machine with Pygame installed.
>
> **Files changed/created this stage:**
>
> - `main.py` — updated: added the Play Again state transition from the game wrapper
> - `src/menu/carousel_menu.py` — updated: preserves the player name and reopens the selected game's mode selector for replay
> - `src/games/memory/common.py`, `src/games/guess_number/common.py`, `src/games/spr/common.py` — updated: added replay actions to shared game-over controls
> - `src/games/breakout/mode_1p.py`, `src/games/tetris/mode_1p.py`, `src/games/tetris/mode_2p.py` — updated: added visible Play Again buttons
> - `src/games/pong/common.py`, `src/games/pong/mode_ai.py`, `src/games/pong/mode_2p.py` — updated: added first-to-five match endings and replay controls
> - `src/menu/settings_menu.py` — updated: aligned settings controls and labels within the panel
> - `src/info/*.txt` — updated: replaced placeholder text with game information and documented Pong's five-point match
> - `readme.md` — updated: added this Stage 19 development log

> **Follow-up polish (same stage):** I fixed a rendering issue on the Scissors Paper Rock game-over screen where the Play Again button was drawn without its text. I also changed the mode-selection flow so choosing Local 2 Player skips the difficulty screen and starts the game directly, while Vs AI still has its normal difficulty selection. Finally, I reorganised the Settings screen around the panel bounds: the context label, volume labels, sliders, percentages, toggles, control-binding rows, and footer buttons are now positioned relative to the box, with the volume controls grouped into separate rows.

> **Follow-up files changed:**
>
> - `src/games/spr/common.py` — updated: centred and drew the Play Again label inside its button
> - `src/menu/carousel_menu.py` — updated: bypassed difficulty selection for Scissors Paper Rock Local 2 Player only
> - `src/menu/settings_menu.py` — updated: kept Settings text and controls inside the panel and improved spacing and grouping

> **Follow-up polish (same stage):** Removed the literal “Context:” prefix from Settings so the header shows only the current game name (or “Main Menu”). Widened the Learn more button so its label fits cleanly inside the button.
>
> **Automatic game information loading:** Removed the hardcoded game-to-filename map. Learn more now loads `info.txt` from the selected game's root folder using the game's module path, while main-menu help comes from `src/menu/info.txt`. Moved each existing game's instructions beside that game and removed the legacy `src/info/*.txt` files, so adding a game with an `info.txt` file requires no Settings code changes.
>
> **Follow-up files changed:**
>
> - `src/menu/settings_menu.py` — updated: displays only the current context name, widens Learn more, and resolves info files automatically
> - `main.py` — updated: reads the game module path from the game class so per-game information is located correctly
> - `src/games/*/info.txt` — added: stores each game's own instructions in its root folder
> - `src/menu/info.txt` — added: stores main-menu help text beside the menu code
> - `src/info/*.txt` — removed: no longer needed after moving help text beside each game/menu
> - `structure.txt` — updated: documents how game creators add their own `info.txt` without editing Settings


> **Final info-screen polish:** The Learn More overlay felt cramped and unfinished after being quickly assembled, so I edited it with more breathing room, clearer text hierarchy, better wrapping, and a proper footer. This should be the last of these small visual clean-up passes.


**Stage 20 - [21/10/2026 / Final Adjustments]**
This stage is all about polishing things further. After testing my latest major updates, I see that there is much wrong with it. Some of the screens have got incorrectly placed graphics that do not adjust accordingly to the scaling since I have not updated them. Pong has a collisions bug where if the ball gets to fast then it phases through the players panel, Hugo my friend has recommended I do Raycasting Collisions, — a lot simpler than it sounds — Semi-transcribed: "Balls current positio This thing, ball's new positioIn between them is the ba So you can see that if you're just checking pixels, it'll go from here to here and never actually touch the ba Because like you're just adding spee So like the, it doesn't interpolat It just a Distanc So it teleports behind the pane Yea Now, before you teleport it, so before you actually add the speed onto the distance, onto the position, what you can do is you can say, okay, draw a line, like not actual drawing, but like imagine a line from the original point to what its next point would b And if that line at any pointyour path. Yeah, I if that line intersects at any point, you know that it has like gone through initiative. Right. Okay. So then you can say, okay, just throw it back out. Yeah, but you can do it. There's two ways of doing it. There's two ways of doing it. Either you can bounce it back just immediately. So just like do the same bounce code. Yeah. But like just add its current position. So even though it technically hasn't touched the paddle, like you can just say, I'll touch the panel. Yeah, or you can calculate when that line would have hit the pedal, which is just the maths. And then calculate the rest of the path. Yeah, as if it hit the panel. Right. So let me get my book to explain. So your paddle is there. That's your paddle. Very craftly drawn paddle. But that's your paddle. This is the ball's position one. Right, so that's where it is. And then you can imagine that it's going on, just going to follow the line. That kind of a path. And it's speed is enough that when you just add the speed, it teleports behind the paddle. So that's ball position two. So does that make sense? Yeah, yeah. Because it's gone too far. Like to move the ball, you're just adding speed, right? Yes. Or like a change in... It's just a change in speed, yeah. Whatever. Just to get it updated. Like you're adding it. And so in that adding, if this adding is too much, it'll just skip over the paddle. Because it's changed in that time.I got a line in between them. If that line intersects the paddle. The paddle at any point. Then we can say, okay, it should have hit the paddle. Right. And then from the two options you have. I just inferred its axis. Either you do the bounce logic for this position one. So you just say, oh, okay, it hit a wall there. And it bounces off. The problem with that is once you get up to really high speeds, like theoretically is possible. This bounce position will just keep getting close or getting closer. And you'll get errors. Okay. As you get, like theoretically, you can get fast enough where, like, you'll crash your game. Because it's just too fast to compute. It tries to be like, okay.So that's not the recommended way. So then what should I do? The other way is you can calculate easily how far along this line it hit the paddle. Right. And then from that point instead of adding more X subtract it. So the same bounce code. So instead of doing that you flip along this paddle. Yes. There. So you see that's what I thought. Yeah that's what I thought. Yeah. These are the same. Yeah. Just inverted. Now the way you would do that is one you have an X distance to the paddle. have the total x distance. your new X can be calculated by getting the distance to the ball yeah the distance to the paddle and then subtracting what would have been the excess distance that it would have teleported would have gone okay so yeah because we have the line and we know this distance from the wall to the wall there and the wall to the wall there same yep so it's the same X distance just negative of each other yeah okay so you can see it bounces back that much I just flip that around and your Y distance because it's not affected it's perpendicular yep doesn't change so you don't have to do anything about you that's so much better than your Y yeah you just have to what like do your X I would have never thought about and so code wise so let's say wherever your paddle is at like 250 X don't worry about the action numbers. 240. So it's gone past. Like in theory, like in theory, yeah, going from there to there, it doesn't cross over 50 because you're just adding minus 20. And so like, it'll never see like, okay, it was 50 at some point, which is how your collision works. Yeah. So it won't realize there's a collision. So you can do that. If you do this, you can say, okay, cool. It has hit the wall at some point. So you like, you make the line and you do whatever functioning code there is to say, it does this line here. Okay, it hits the paddle. Great. What you can say is, okay, I know the distance from my old ball to the paddle is 10 because of our math. If you're... you can then say, okay, the distance the ball would have traveled on the X is 260 minus 240. The speed. So that's the speed. There's 20 units. So travels 20 units. Every tick. There's your currency. So you know it travels 10 to the paddle and you want to know how far it would have traveled more than we've ever thought of. And so that is 20 minus... 10. That didn't even get that. It was 10, right? So that means that your ball would have traveled 10 further.So 250 plus 10, 26 So in the example we use, because I use less than even others, it goes back to the same expositio But it works for any numbe Damn, that's actually really goo So you get the new exposition is 26 But you need to update the wate And the white position, you just update it as normal, because it's not effectiv Yea Yeah, you just set it ther Yeah, because it's where it's meant to b The speed, you can update the same as you were before, as if it collide So you can add however much speed to the x and make sure that it inverts, because you hit somethin That's an easier fix than a fill is going to b No, it's very simple So in variable terms, so you remember the variable It is handle x minus... And then here is X speed minus this to paddle is how far bounces from the pedal. And then you are new X. So I'm going to call it new new so I'm going to get confused. Because that's your theoretical new. It was your new new update of it is equal to the paddle X plus, and then just make sure to update XP as you normally would for any collision. 

We need to fix power-ups inside of Breakout; Speed ball + 2, Ball spawn 1+ from paddle, speed ball - 2. The other Paddle length is fine but just needs to incresse more until being collected like 7 times. 
Seeing as games might be dropped into the /games folder, we need to update the engine to launch the games at whatever aspect they have been set to unless they use the screen dimensions set in constants. They need to simply launch independently. Same with constants for games; because we are creating a launcher for independent games I should make my current games independent by making their own constants.py. This just makes sure that no on screen calculations made by a user gets affected by a screen size change, some people might not build their game to auto adjust to screen size, this will fix that issue.


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
