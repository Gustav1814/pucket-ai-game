A fast-paced, competitive game where players launch pucks across a board aiming for goals. This implementation features a computerized version where players compete against an AI opponent.
📋 Table of Contents

Features
Installation
How to Play
Controls
Game Mechanics
Technical Details
Development Roadmap
Team
License

✨ Features
Current Implementation

Core Gameplay: Launch pucks across the board and aim for the goal on your opponent's side
Physics Engine: Realistic puck movement with friction, collisions, and boundary interactions
Turn-Based System: Players take turns launching their pucks
AI Opponent: Computer player with strategic decision-making
Scoring System: Track successful goals for each player
Win Condition: First player to get all their pucks into the opponent's goal wins
Debug Mode: Press F3 to see additional game information

Planned Features

Power-Ups: Speed boosts, shields, freeze effects, and multi-launch capabilities
Obstacles: Bumpers, portals, and walls that affect puck trajectories
Advanced AI: Enhanced opponent using Minimax algorithm with Alpha-Beta pruning
Difficulty Levels: Multiple AI difficulty settings

🚀 Installation
Prerequisites

Python 3.x
pip (Python package manager)

Setup

Clone the repository:
bashgit clone https://github.com/Gustav1814/pucket-game.git
cd pucket-game

Install dependencies:
bashpip install -r requirements.txt

Run the game:
bashpython src/game.py


🎯 How to Play
Objective
Be the first player to launch all your pucks into the goal on your opponent's side of the board.
Game Flow

Players start with 5 pucks each on their side of the board
Players take turns launching pucks across the central divider
Pucks can collide with each other and bounce off walls
A puck scores when it enters the opponent's goal (hole)
The first player to score all their pucks wins!

🕹️ Controls
Key/ActionFunctionMouseClick and drag to aim and set launch powerTabSwitch between your active pucksF3Toggle debug modeRRestart game (after game over)
⚙️ Game Mechanics
Physics

Pucks move with realistic physics including:

Friction (gradually slows down pucks)
Elastic collisions between pucks
Wall bouncing with energy loss
Maximum velocity limits



Turn System

Players alternate turns
A turn ends when all pucks have stopped moving
There's a brief cooldown between turns for stability

AI Strategy
The AI opponent:

Evaluates the best puck to launch
Calculates optimal angle to the goal
Adds slight randomness for unpredictability
Adjusts power based on distance

🔧 Technical Details
Architecture
pucket-game/
├── src/
│   └── game.py         # Main game implementation
├── docs/
│   └── README.docx     # Project documentation
├── requirements.txt    # Python dependencies
└── README.md          # This file
Core Components

Game Engine: Built with Pygame for graphics and game loop
Physics System: Custom collision detection and response
AI Module: Strategic decision-making for computer opponent
Turn Manager: Handles game state transitions

Technologies Used

Python 3.x: Core programming language
Pygame: Game development framework
Math: Physics calculations and AI decision making

📈 Development Roadmap
Phase 1: Core Gameplay ✅

 Basic board, pucks, and goals
 Simple physics engine
 Turn-based gameplay
 Basic AI opponent

Phase 2: Enhanced Features 🚧

 Power-ups system
 Obstacles implementation
 Improved physics interactions
 More sophisticated AI

Phase 3: Advanced AI 📅

 Minimax algorithm with Alpha-Beta pruning
 Heuristic evaluation functions
 Learning components
 Multiple difficulty levels

👥 Team
NameIDRoleHamaiz Siddiqui22k-4682DeveloperAbdul Wadood22k-4764DeveloperZeerak Shahzad22k-4692Developer
Course: Artificial Intelligence
Instructor: Ms. Mehak Mazhar
Institution: [Your University Name]
Date: May 2025
🐛 Troubleshooting
Common Issues

Game Freezes

Try restarting the game
Check console for error messages


Graphics Issues

Update Pygame: pip install --upgrade pygame
Verify Python version compatibility


Performance Problems

Close other resource-intensive applications
Enable debug mode (F3) to check frame rate



Debug Mode
Press F3 during gameplay to see:

Current player information
Turn state and timing
Puck velocity indicators
Frame rate metrics

🤝 Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

Developed as part of the AI course requirements
Implements game theory concepts and artificial intelligence techniques
Special thanks to Ms. Mehak Mazhar for guidance


