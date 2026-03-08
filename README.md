## 🕹️ Pac-Man AI: Adversarial Search & Pathfinding
This project implements a fully functional Pac-Man game in Python using Pygame, featuring various AI agents ranging from simple reflex logic to advanced adversarial search algorithms like Minimax and Alpha-Beta Pruning.

## 🚀 Features
Multiple AI Modes: Toggle between different levels of intelligence:

Reflex: A heuristic-based agent that reacts to immediate surroundings (food and ghosts).

Minimax: A strategic agent that simulates future game states to maximize its score.

Alpha-Beta: An optimized version of Minimax that prunes the search tree for faster decision-making.

Search Algorithms: Includes implementations of BFS, DFS, and A* for pathfinding.

Smooth Movement: Custom "forced centering" logic ensures Pac-Man aligns perfectly with the maze grid for AI decisions.

Visual Feedback: Real-time mouth animation and invincibility "blinking" effects.

## 🛠️ Installation & Setup

1. Prerequisites: Ensure you have Python 3.10+ and Pygame installed.
   pip install pygame
2. Clone the Repository:
   git clone https://github.com/morutanmaria/Pacman-AI.git
   cd Pacman-AI
3. Run the Game:
   python main.py

## 🎮 How to Play
Manual Mode: Use the Arrow Keys to navigate.

Switching AI Modes: (Modify your main.py or HUD logic to toggle between reflex, minimax, and alphabeta).

Invincibility: After being hit, Pac-Man gains a 2-second grace period (blinking effect) to reposition.

## 🧠 Technical Deep Dive
The Adversarial Search (Alpha-Beta)
The core of the AI's intelligence lies in the alphabeta method within the Player class. It treats the game as a zero-sum game where:

Pac-Man (Maximizer): Tries to choose moves that lead to the highest score (eating pellets, staying safe).

Ghosts (Minimizers): Try to choose moves that lead to the lowest score for Pac-Man (catching him).

The search space is optimized using Alpha-Beta Pruning, which ignores branches that cannot possibly influence the final decision, significantly improving performance over standard Minimax.

State Evaluation
The evaluate_state function calculates the "utility" of a game state based on:

Pellet Proximity: High reward for getting closer to food.

Ghost Proximity: Severe penalty for being within 8 tiles of a ghost (scaled cubically as they get closer).

Food Remaining: Reward for clearing the board.

## ⚡ Performance Optimization
Due to the exponential nature of search trees, the following optimizations are implemented:

Depth Limiting: The search is capped at a specific depth (e.g., Depth 2 or 3) to prevent frame-rate lag.

Move Filtering: Pac-Man is discouraged from reversing direction unless necessary, reducing the branching factor.

Adversarial Ply Management: Depth is only decremented after all ghosts have made their move, completing one full game cycle.
