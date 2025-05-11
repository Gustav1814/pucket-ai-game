import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
BOARD_WIDTH, BOARD_HEIGHT = 700, 500
PUCK_RADIUS = 20
HOLE_RADIUS = 25
DIVIDER_WIDTH = 10
FPS = 60
MAX_VELOCITY = 10
FRICTION = 0.98

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (200, 200, 200)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pucket: Simplified Version")
clock = pygame.time.Clock()

# Debug flag
DEBUG = False

class Puck:
    def __init__(self, position, color, player_id):
        self.position = position
        self.color = color
        self.radius = PUCK_RADIUS
        self.velocity = (0, 0)
        self.player_id = player_id
        self.active = True  # Whether the puck is still in play
    
    def draw(self):
        if not self.active:
            return
            
        pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius)
        
        # Draw velocity vector in debug mode
        if DEBUG and (abs(self.velocity[0]) > 0.1 or abs(self.velocity[1]) > 0.1):
            end_x = self.position[0] + self.velocity[0] * 5
            end_y = self.position[1] + self.velocity[1] * 5
            pygame.draw.line(screen, GREEN, self.position, (end_x, end_y), 2)
    
    def update(self):
        if not self.active:
            return
            
        # Apply friction
        self.velocity = (self.velocity[0] * FRICTION, self.velocity[1] * FRICTION)
        
        # Update position
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]
        )
        
        # Check board boundaries
        if self.position[0] < PUCK_RADIUS:
            self.position = (PUCK_RADIUS, self.position[1])
            self.velocity = (-self.velocity[0] * 0.8, self.velocity[1])
        elif self.position[0] > WIDTH - PUCK_RADIUS:
            self.position = (WIDTH - PUCK_RADIUS, self.position[1])
            self.velocity = (-self.velocity[0] * 0.8, self.velocity[1])
            
        if self.position[1] < PUCK_RADIUS:
            self.position = (self.position[0], PUCK_RADIUS)
            self.velocity = (self.velocity[0], -self.velocity[1] * 0.8)
        elif self.position[1] > HEIGHT - PUCK_RADIUS:
            self.position = (self.position[0], HEIGHT - PUCK_RADIUS)
            self.velocity = (self.velocity[0], -self.velocity[1] * 0.8)
    
    def launch(self, angle, power):
        if not self.active:
            return
            
        power = min(power, MAX_VELOCITY)
        self.velocity = (
            power * math.cos(angle),
            power * math.sin(angle)
        )
    
    def is_stopped(self):
        return abs(self.velocity[0]) < 0.1 and abs(self.velocity[1]) < 0.1

class Player:
    def __init__(self, id, name, color, is_ai=False):
        self.id = id
        self.name = name
        self.color = color
        self.pucks = []
        self.is_ai = is_ai
        self.score = 0
        self.move_made = False  # Flag to track if a move has been made
    
    def initialize_pucks(self, count, start_positions):
        self.pucks = []
        for i in range(count):
            position = start_positions[i % len(start_positions)]
            self.pucks.append(Puck(position, self.color, self.id))
    
    def all_pucks_stopped(self):
        for puck in self.pucks:
            if puck.active and not puck.is_stopped():
                return False
        return True
            
    def has_active_pucks(self):
        for puck in self.pucks:
            if puck.active:
                return True
        return False

class PucketGame:
    def __init__(self):
        self.initialize_game()
        
    def initialize_game(self):
        # Create players
        self.players = [
            Player(0, "Player", BLUE, is_ai=False),
            Player(1, "AI", RED, is_ai=True)
        ]
        
        # Board setup
        self.board_x = (WIDTH - BOARD_WIDTH) // 2
        self.board_y = (HEIGHT - BOARD_HEIGHT) // 2
        
        # Initialize player pucks
        self.num_pucks_per_player = 5
        
        # Create starting positions
        player_start_positions = []
        ai_start_positions = []
        
        # Each player's side
        for i in range(self.num_pucks_per_player):
            player_start_positions.append((
                self.board_x + 100 + (i % 3) * 50,
                self.board_y + 100 + (i // 3) * 60
            ))
            
            ai_start_positions.append((
                self.board_x + BOARD_WIDTH - 100 - (i % 3) * 50,
                self.board_y + BOARD_HEIGHT - 100 - (i // 3) * 60
            ))
        
        self.players[0].initialize_pucks(self.num_pucks_per_player, player_start_positions)
        self.players[1].initialize_pucks(self.num_pucks_per_player, ai_start_positions)
        
        # Game state
        self.current_player_idx = 0
        self.game_over = False
        self.winner = None
        
        # Launch parameters
        self.launch_power = 0
        self.launch_angle = 0
        self.is_launching = False
        self.selected_puck_idx = 0
        
        # Goals (holes)
        self.goals = self.create_goals()
        
        # AI decision timer
        self.ai_timer = 0
        self.ai_thinking = False
        
        # Turn management
        self.turn_cooldown = 0
        self.turn_cooldown_duration = 30  # Half a second at 60 FPS
        self.all_stopped_frames = 0  # Count frames where pucks are stopped
        self.required_stopped_frames = 30  # Wait this many frames with all pucks stopped before switching turns
        
        # Debug info
        self.debug_text = ""
    
    def create_goals(self):
        goals = []
        
        # Player's goal (on AI side)
        goals.append((
            self.board_x + BOARD_WIDTH - 50,
            self.board_y + BOARD_HEIGHT // 2
        ))
        
        # AI's goal (on player side)
        goals.append((
            self.board_x + 50,
            self.board_y + BOARD_HEIGHT // 2
        ))
        
        return goals
    
    def draw_board(self):
        # Draw the board background
        pygame.draw.rect(screen, BROWN, (self.board_x, self.board_y, BOARD_WIDTH, BOARD_HEIGHT))
        
        # Draw the center divider
        pygame.draw.rect(screen, BLACK, 
                         (WIDTH // 2 - DIVIDER_WIDTH // 2, 
                          self.board_y, 
                          DIVIDER_WIDTH, 
                          BOARD_HEIGHT))
        
        # Draw the goals (holes)
        for goal in self.goals:
            pygame.draw.circle(screen, BLACK, goal, HOLE_RADIUS)
    
    def draw_game_state(self):
        # Clear the screen
        screen.fill(WHITE)
        
        # Draw the board
        self.draw_board()
        
        # Draw pucks
        for player in self.players:
            for puck in player.pucks:
                puck.draw()
        
        # Draw launch line if launching
        if self.is_launching and not self.players[self.current_player_idx].is_ai:
            selected_puck = self.get_selected_puck()
            if selected_puck and selected_puck.active:
                end_x = selected_puck.position[0] + math.cos(self.launch_angle) * self.launch_power * 5
                end_y = selected_puck.position[1] + math.sin(self.launch_angle) * self.launch_power * 5
                pygame.draw.line(screen, BLACK, selected_puck.position, (end_x, end_y), 2)
        
        # Draw scores and current player indicator
        font = pygame.font.SysFont('Arial', 24)
        
        player_text = f"{self.players[0].name}: {self.players[0].score}"
        ai_text = f"{self.players[1].name}: {self.players[1].score}"
        
        player_surface = font.render(player_text, True, BLUE)
        ai_surface = font.render(ai_text, True, RED)
        
        screen.blit(player_surface, (20, 20))
        screen.blit(ai_surface, (WIDTH - 20 - ai_surface.get_width(), 20))
        
        # Current player indicator
        current_text = f"Current Turn: {self.players[self.current_player_idx].name}"
        current_surface = font.render(current_text, True, BLACK)
        screen.blit(current_surface, (WIDTH // 2 - current_surface.get_width() // 2, 20))
        
        # Game over message
        if self.game_over and self.winner:
            over_text = f"Game Over! {self.winner.name} Wins!"
            over_surface = font.render(over_text, True, BLACK)
            restart_text = "Press R to Restart"
            restart_surface = font.render(restart_text, True, BLACK)
            
            screen.blit(over_surface, (WIDTH // 2 - over_surface.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(restart_surface, (WIDTH // 2 - restart_surface.get_width() // 2, HEIGHT // 2 + 10))
        
        # Debug info
        if DEBUG:
            debug_surface = font.render(self.debug_text, True, BLACK)
            screen.blit(debug_surface, (20, HEIGHT - 30))
    
    def get_selected_puck(self):
        current_player = self.players[self.current_player_idx]
        active_pucks = [p for p in current_player.pucks if p.active]
        
        if not active_pucks:
            return None
            
        self.selected_puck_idx = self.selected_puck_idx % len(active_pucks)
        return active_pucks[self.selected_puck_idx]
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if self.game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.initialize_game()
                continue
                
            if self.players[self.current_player_idx].is_ai:
                continue
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Switch selected puck
                    self.selected_puck_idx += 1
                
                # Toggle debug mode with F3
                if event.key == pygame.K_F3:
                    global DEBUG
                    DEBUG = not DEBUG
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Start launching
                self.is_launching = True
                
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Finish launching
                if self.is_launching:
                    selected_puck = self.get_selected_puck()
                    if selected_puck:
                        selected_puck.launch(self.launch_angle, self.launch_power)
                        # Mark that a move has been made
                        self.players[self.current_player_idx].move_made = True
                        # Reset frames counter
                        self.all_stopped_frames = 0
                    self.is_launching = False
                    self.launch_power = 0
        
        # Update launch parameters based on mouse position if launching
        if self.is_launching and not self.players[self.current_player_idx].is_ai:
            mouse_pos = pygame.mouse.get_pos()
            selected_puck = self.get_selected_puck()
            
            if selected_puck:
                dx = mouse_pos[0] - selected_puck.position[0]
                dy = mouse_pos[1] - selected_puck.position[1]
                
                self.launch_angle = math.atan2(dy, dx)
                distance = math.sqrt(dx*dx + dy*dy)
                self.launch_power = min(distance / 20, MAX_VELOCITY)
    
    def update_game_state(self):
        # Update pucks
        for player in self.players:
            for puck in player.pucks:
                puck.update()
        
        # Check collisions between pucks
        self.check_puck_collisions()
        
        # Check goal collisions
        self.check_goal_collisions()
        
        # Turn management
        self.manage_turns()
        
        # Check win condition
        for player in self.players:
            if not player.has_active_pucks():
                self.game_over = True
                self.winner = player
        
        # Update debug text
        if DEBUG:
            current_player = self.players[self.current_player_idx]
            self.debug_text = f"Player: {self.current_player_idx}, Move Made: {current_player.move_made}, Stopped Frames: {self.all_stopped_frames}, Cooldown: {self.turn_cooldown}"
    
    def manage_turns(self):
        # If turn cooldown is active, decrement it
        if self.turn_cooldown > 0:
            self.turn_cooldown -= 1
            return

        # Check if the current player's pucks have all stopped
        if self.players[self.current_player_idx].all_pucks_stopped():
            # Only count frames if a move has been made
            if self.players[self.current_player_idx].move_made:
                self.all_stopped_frames += 1
                
                # If pucks have been stopped for enough frames, switch turns
                if self.all_stopped_frames >= self.required_stopped_frames:
                    # Reset for next player
                    self.all_stopped_frames = 0
                    
                    # Switch to the other player
                    self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
                    
                    # Reset move made flag for the new player
                    self.players[self.current_player_idx].move_made = False
                    
                    # Set a cooldown before the new player can make a move
                    self.turn_cooldown = self.turn_cooldown_duration
                    
                    # Reset AI thinking state
                    if self.players[self.current_player_idx].is_ai:
                        self.ai_thinking = False
                        self.ai_timer = 0
    
    def check_puck_collisions(self):
        # Check collisions between pairs of pucks
        for i, player1 in enumerate(self.players):
            for puck1 in player1.pucks:
                if not puck1.active:
                    continue
                    
                # Check collision with other pucks
                for j, player2 in enumerate(self.players):
                    for puck2 in player2.pucks:
                        if puck1 == puck2 or not puck2.active:
                            continue
                            
                        dx = puck2.position[0] - puck1.position[0]
                        dy = puck2.position[1] - puck1.position[1]
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        # Prevent division by zero
                        if distance < 0.0001:
                            # Pucks are exactly in the same position - move one slightly
                            puck2.position = (
                                puck2.position[0] + random.uniform(0.1, 1.0),
                                puck2.position[1] + random.uniform(0.1, 1.0)
                            )
                            # Recalculate after adjustment
                            dx = puck2.position[0] - puck1.position[0]
                            dy = puck2.position[1] - puck1.position[1]
                            distance = math.sqrt(dx*dx + dy*dy)
                        
                        if distance < puck1.radius + puck2.radius:
                            # Collision handling: elastic collision
                            # Calculate collision normal
                            nx = dx / distance
                            ny = dy / distance
                            
                            # Calculate relative velocity
                            vx = puck1.velocity[0] - puck2.velocity[0]
                            vy = puck1.velocity[1] - puck2.velocity[1]
                            
                            # Calculate velocity component along the normal
                            vn = vx * nx + vy * ny
                            
                            # Don't process collision if pucks are moving away from each other
                            if vn > 0:
                                continue
                            
                            # Calculate impulse
                            impulse = -1.8 * vn / 2  # Slightly less elastic for stability
                            
                            # Apply impulse to velocities
                            puck1.velocity = (
                                puck1.velocity[0] + impulse * nx,
                                puck1.velocity[1] + impulse * ny
                            )
                            
                            puck2.velocity = (
                                puck2.velocity[0] - impulse * nx,
                                puck2.velocity[1] - impulse * ny
                            )
                            
                            # Separate the pucks to prevent sticking
                            overlap = 0.5 * (puck1.radius + puck2.radius - distance)
                            puck1.position = (
                                puck1.position[0] - overlap * nx,
                                puck1.position[1] - overlap * ny
                            )
                            
                            puck2.position = (
                                puck2.position[0] + overlap * nx,
                                puck2.position[1] + overlap * ny
                            )
    
    def check_goal_collisions(self):
        for player_idx, player in enumerate(self.players):
            opponent_idx = (player_idx + 1) % len(self.players)
            opponent_goal = self.goals[player_idx]
            
            for puck in player.pucks:
                if not puck.active:
                    continue
                    
                # Check if puck is in the opponent's goal
                dx = puck.position[0] - opponent_goal[0]
                dy = puck.position[1] - opponent_goal[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < HOLE_RADIUS - 5:  # Little margin to make it easier
                    # Puck is in goal
                    puck.active = False
                    player.score += 1
                    
                    # Check if all pucks from this player are in goals
                    if not player.has_active_pucks():
                        self.game_over = True
                        self.winner = player
    
    def ai_make_move(self):
        """Simple AI strategy for stability"""
        if not self.players[self.current_player_idx].is_ai:
            return
        
        # Don't make a move if the AI player has already made one this turn
        if self.players[self.current_player_idx].move_made:
            return
            
        if not self.ai_thinking:
            self.ai_thinking = True
            self.ai_timer = 0
            
        # Simulate thinking time
        self.ai_timer += 1
        if self.ai_timer < 30:  # Half a second delay
            return
            
        # Reset thinking flag
        self.ai_thinking = False
        
        # Get active pucks
        ai_player = self.players[self.current_player_idx]
        active_pucks = [p for p in ai_player.pucks if p.active]
        
        if not active_pucks:
            return
        
        # Simple AI: Aim for the goal with a random puck
        selected_puck = random.choice(active_pucks)
        opponent_goal = self.goals[self.current_player_idx]
        
        # Calculate angle to the goal
        dx = opponent_goal[0] - selected_puck.position[0]
        dy = opponent_goal[1] - selected_puck.position[1]
        angle = math.atan2(dy, dx)
        
        # Add some randomness
        angle += random.uniform(-0.2, 0.2)
        
        # Calculate power based on distance
        distance = math.sqrt(dx*dx + dy*dy)
        power = min(distance / 50, MAX_VELOCITY * 0.8)  # 80% of max to increase accuracy
        
        # Launch the puck
        selected_puck.launch(angle, power)
        
        # Mark that the AI has made a move
        self.players[self.current_player_idx].move_made = True
        
        # Reset the stopped frames counter
        self.all_stopped_frames = 0
    
    def run_game(self):
        try:
            while True:
                # Handle input
                self.handle_input()
                
                # AI player's turn
                if self.players[self.current_player_idx].is_ai and not self.game_over:
                    self.ai_make_move()
                
                # Update game state
                self.update_game_state()
                
                # Draw the game
                self.draw_game_state()
                
                # Update the display
                pygame.display.update()
                
                # Cap the frame rate
                clock.tick(FPS)
        except Exception as e:
            # Print any errors and continue running
            print(f"Error: {e}")
            # Reset game if an error occurs
            self.initialize_game()
            self.run_game()

# Run the game if this script is executed
if __name__ == "__main__":
    game = PucketGame()
    game.run_game()