# PacTest
AI-generated pac-man style game, meant to be proof of concept

Pac-Man Style Game in Python
This project is a Pac-Man style game implemented in Python using the Pygame library. It features a randomly generated maze with loops and crossing paths, animated sprites for the player (Pac-Man) and ghosts (each sporting a unique, silly hat), collectible dots and power pellets, special fruit bonuses, and a fully functional UI with score, level, and life counters. The game also includes a pause menu and a game-over screen.

Features
Randomly Generated Maze:
A recursive backtracking algorithm creates a maze with extra wall removals to form loops and crossing paths, ensuring varied and engaging levels.

Animated Sprites:

Player Animation:
The player cycles through a multi-frame animation simulating an opening and closing mouth, similar to classic Pac-Man.
Ghost Animation:
Each ghost is animated with its own multi-frame movement cycle and is adorned with a randomly colored, silly hat.
Collectibles and Power-Ups:

Dots & Power Pellets:
Standard dots add to the score, while larger power pellets temporarily empower the player to eat ghosts.
Special Fruit:
Occasionally, fruits spawn in place of dots, providing bonus points when collected.
Game Mechanics:

The player starts with 3 lives and loses one upon contact with a ghost (unless empowered by a power pellet).
Completing a level occurs when all dots are collected.
Ghosts become vulnerable during power-up mode, allowing the player to "eat" them for extra points.
User Interface:
Displays the player's score, current level, and remaining lives.
Includes a pause menu (toggle with P) and a game-over screen with a restart option (R).

60 FPS Refresh Rate:
The game runs at a smooth 60 frames per second for an optimal gaming experience.

Requirements
Python 3.x
Pygame
Install via pip:
bash
Copy
pip install pygame
How to Run
Ensure you have Python 3.x installed on your computer.
Install the Pygame library using pip if you haven't already:
bash
Copy
pip install pygame
Save the game script (the provided Python file) to your local machine.
Open a terminal or command prompt in the directory containing the script.
Run the script:
bash
Copy
python your_script_name.py
Game Controls
Arrow Keys: Move Pac-Man around the maze.
P: Toggle pause/resume.
R: Restart the game (when paused or on the game-over screen).
Code Overview
Maze Generation:
The Maze class generates a maze using recursive backtracking with added randomness to create loops and crossing paths.

Sprite Classes:

Wall: Represents the maze walls.
Dot and Fruit: Represent the collectible items.
Player: Controls the Pac-Man character, handling movement, collisions, and animations.
Ghost: Handles the enemy ghosts with random movement and animated sprites (including silly hats).
Main Game Loop:
Manages game states (playing, paused, game over), updates sprite positions and animations, checks for collisions, and handles user inputs.

Customization
Animation and Graphics:
The animations for the player and ghosts are generated using Pygame’s drawing functions. You can customize the look by modifying the drawing logic in the load_animations methods.

Difficulty Settings:
Adjust variables like CELL_SIZE, ROWS, COLS, ghost speed, or power-up durations to tailor the gameplay experience.

Maze Complexity:
Modify the probability in the add_loops method of the Maze class to create more or fewer loops and paths.

License
This project is provided as-is under the MIT License. Feel free to modify and distribute it as needed.
