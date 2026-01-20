import pygame
import random
import math
from enum import Enum
from pygame import mixer
from dataclasses import dataclass
from typing import List, Tuple, Sequence


# ============================================================================
# GAME STATE MANAGEMENT
# ============================================================================

class GameState(Enum):
    """Game state enum for state machine."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameStateManager:
    """Manages game state transitions and active state."""
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
    
    def transition(self, new_state: GameState):
        """Transition to a new game state."""
        self.previous_state = self.current_state
        self.current_state = new_state
    
    def is_playing(self) -> bool:
        """Check if game is actively playing."""
        return self.current_state == GameState.PLAYING


# ============================================================================
# DIFFICULTY SCALING SYSTEM
# ============================================================================

class DifficultyScaler:
    """
    Manages difficulty progression over time.
    
    Formulas:
    - Spawn rate: base_rate + (elapsed_seconds * scale_factor)
    - Speed: base_speed * (1 + score * speed_scale_factor)
    """
    
    def __init__(self):
        self.base_spawn_rate = 1.0  # asteroids per second
        self.spawn_scale_factor = 0.05  # increase by 0.05 per second
        self.base_speed = 2.0
        self.speed_scale_factor = 0.01  # 1% speed increase per score point
        self.elapsed_time = 0
    
    def update(self, dt: float):
        """Update elapsed time."""
        self.elapsed_time += dt
    
    def get_spawn_rate(self) -> float:
        """Get current spawn rate based on elapsed time."""
        return min(
            self.base_spawn_rate + (self.elapsed_time * self.spawn_scale_factor),
            5.0  # cap at 5 asteroids per second
        )
    
    def get_speed(self, score: int) -> float:
        """Get current asteroid speed based on score."""
        return max(
            self.base_speed * (1 + score * self.speed_scale_factor),
            2.0
        )
    
    def reset(self):
        """Reset difficulty for new game."""
        self.elapsed_time = 0


# ============================================================================
# GAME ENTITIES
# ============================================================================

@dataclass
class Vector2:
    """Simple 2D vector."""
    x: float
    y: float


class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: float, y: float, image: pygame.Surface):
        self.pos = Vector2(x, y)
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()
    
    def draw(self, surface: pygame.Surface, offset: Tuple[int, int] = (0, 0)):
        """Draw entity on surface."""
        surface.blit(self.image, (self.pos.x + offset[0], self.pos.y + offset[1]))
    
    def get_rect(self):
        """Get rectangle for collision detection."""
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)


class Player(Entity):
    """Player spaceship entity."""
    
    SPEED = 7
    BOUNDARY_LEFT = 0
    BOUNDARY_RIGHT = 736
    
    def __init__(self, x: float, y: float, image: pygame.Surface):
        super().__init__(x, y, image)
        self.velocity = 0
    
    def handle_input(self, keys: Sequence[bool]):
        """Handle player input."""
        if keys[pygame.K_LEFT]:
            self.velocity = -self.SPEED
        elif keys[pygame.K_RIGHT]:
            self.velocity = self.SPEED
        else:
            self.velocity = 0
    
    def update(self):
        """Update player position."""
        self.pos.x += self.velocity
        
        # Boundary checking
        if self.pos.x <= self.BOUNDARY_LEFT:
            self.pos.x = self.BOUNDARY_LEFT
        elif self.pos.x >= self.BOUNDARY_RIGHT:
            self.pos.x = self.BOUNDARY_RIGHT


class Bullet(Entity):
    """Projectile/bullet entity."""
    
    SPEED = 7
    
    def __init__(self, x: float, y: float, image: pygame.Surface):
        super().__init__(x, y, image)
        self.active = False
    
    def fire(self, x: float, y: float):
        """Fire bullet from given position."""
        self.pos.x = x
        self.pos.y = y
        self.active = True
    
    def update(self):
        """Update bullet position."""
        if self.active:
            self.pos.y -= self.SPEED
            if self.pos.y < 0:
                self.active = False


class Asteroid(Entity):
    """Asteroid enemy entity with AI behavior."""
    
    def __init__(self, x: float, y: float, image: pygame.Surface, speed: float = 2.0):
        super().__init__(x, y, image)
        self.speed = speed
        self.drift_speed = random.uniform(0.5, 2.0)
        self.drift_direction = random.choice([-1, 1])
        self.homing_chance = 0.02  # 2% chance to target player
        self.is_homing = False
        self.lifetime = 0
    
    def set_difficulty_speed(self, speed: float):
        """Update speed based on difficulty."""
        self.speed = speed
    
    def update(self, player_pos: Vector2 = None):
        """
        Update asteroid position with smart behavior.
        Drifts horizontally with variance, occasionally homes toward player.
        """
        self.lifetime += 1
        
        # Vertical movement (always falling)
        self.pos.y += self.speed
        
        # Horizontal drift with variance
        self.pos.x += self.drift_speed * self.drift_direction
        
        # Occasional homing behavior (light AI)
        if player_pos and random.random() < self.homing_chance and not self.is_homing:
            self.is_homing = True
        
        if self.is_homing and player_pos:
            if self.pos.x < player_pos.x:
                self.pos.x += 1
            elif self.pos.x > player_pos.x:
                self.pos.x -= 1
            
            if self.lifetime % 60 == 0:
                self.is_homing = False
        
        # Boundary wrapping
        if self.pos.x < 0:
            self.pos.x = 800
        elif self.pos.x > 800:
            self.pos.x = 0
        
        # Occasional direction change
        if random.random() < 0.01:
            self.drift_direction *= -1


class EnemyManager:
    """Manages all asteroid enemies."""
    
    ASTEROID_IMAGES = [
        './assets/images/asteroid1.png',
        './assets/images/asteroid2.png',
        './assets/images/asteroid3.png'
    ]
    
    def __init__(self):
        self.asteroids: List[Asteroid] = []
    
    def initialize_level(self, num_asteroids: int):
        """Initialize asteroids for a level."""
        self.asteroids.clear()
        for _ in range(num_asteroids):
            self._spawn_asteroid()
    
    def _spawn_asteroid(self, x: float = None, y: float = None, speed: float = 2.0):
        """Spawn a single asteroid."""
        if x is None:
            x = random.randint(0, 765)
        if y is None:
            y = random.randint(0, 50)
        
        image = pygame.image.load(random.choice(self.ASTEROID_IMAGES))
        asteroid = Asteroid(x, y, image, speed)
        self.asteroids.append(asteroid)
    
    def update(self, difficulty_scaler: DifficultyScaler, player_pos: Vector2, score: int):
        """Update all asteroids and handle spawning based on difficulty."""
        speed = difficulty_scaler.get_speed(score)
        for asteroid in self.asteroids:
            asteroid.set_difficulty_speed(speed)
            asteroid.update(player_pos)
        
        # Spawn new asteroids based on difficulty scaling
        spawn_rate = difficulty_scaler.get_spawn_rate()
        spawn_probability = spawn_rate / 60  # per-frame probability at 60 FPS
        
        if random.random() < spawn_probability and len(self.asteroids) < 12:
            self._spawn_asteroid(speed=speed)
    
    def get_active_asteroids(self) -> List[Asteroid]:
        """Get all active asteroids."""
        return self.asteroids


# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class Game:
    """
    Main game class - orchestrates all game systems.
    
    Responsibilities:
    - Central game loop
    - Coordinates all entities (player, asteroids, bullets)
    - Handles collisions and score
    - Manages game state and difficulty
    """
    
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption('Asteroid Attack')
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game systems
        self.state_manager = GameStateManager()
        self.difficulty_scaler = DifficultyScaler()
        
        # Game state
        self.score = 0
        self.high_score = self._load_high_score()
        self.lives = 3
        self.screen_shake = 0
        self.click = False
        
        # Assets
        self._load_assets()
        
        # Entities
        self.player = Player(370, 480, self.player_img)
        self.bullet = Bullet(370, 480, self.projectile_img)
        self.enemy_manager = EnemyManager()
        
        # UI
        self.font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 32)
        self.score_font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 42)
        self.menu_font = pygame.font.Font('./assets/fonts/Poppins-BlackItalic.ttf', 50)
        self.menu_font_2 = pygame.font.Font('./assets/fonts/Poppins-MediumItalic.ttf', 42)
        self.menu_font_3 = pygame.font.Font('./assets/fonts/Poppins-Regular.ttf', 36)
        self.over_font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 64)
        
        self.overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Music
        self.music_playing = False
        self._init_music()
    
    def _load_assets(self):
        """Load all game assets."""
        icon = pygame.image.load('./assets/images/asteroid1.png')
        pygame.display.set_icon(icon)
        
        self.player_img = pygame.image.load('./assets/images/spaceship3.png')
        self.projectile_img = pygame.image.load('./assets/images/projectile.png')
        self.lives_img = pygame.image.load('./assets/images/heart.png')
        
        self.backgrounds = [
            pygame.image.load('./assets/images/background1.png'),
            pygame.image.load('./assets/images/background2.png'),
            pygame.image.load('./assets/images/background3.png'),
            pygame.image.load('./assets/images/background4.png'),
            pygame.image.load('./assets/images/background5.png'),
            pygame.image.load('./assets/images/background6.png'),
        ]
        
        self.menu_bg = pygame.image.load('./assets/images/menu_bg.png')
    
    def _init_music(self):
        """Initialize background music."""
        try:
            pygame.mixer.init()
            mixer.music.load('./assets/music/background.wav')
            mixer.music.set_volume(0.5)
        except Exception:
            pass
    
    def _load_high_score(self) -> int:
        """Load high score from file."""
        try:
            with open('file.txt', 'r') as f:
                return int(f.read())
        except (ValueError, FileNotFoundError):
            return 0
    
    def _save_high_score(self):
        """Save high score to file."""
        if self.score > self.high_score:
            self.high_score = self.score
        try:
            with open('file.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def _play_sound(self, sound_path: str, volume: float = 0.7):
        """Play a sound effect."""
        try:
            sound = mixer.Sound(sound_path)
            sound.set_volume(volume)
            sound.play()
        except:
            pass
    
    def _check_collisions(self):
        """Check bullet-asteroid collisions."""
        if not self.bullet.active:
            return
        
        bullet_rect = self.bullet.get_rect()
        
        for asteroid in self.enemy_manager.get_active_asteroids():
            asteroid_rect = asteroid.get_rect()
            if bullet_rect.colliderect(asteroid_rect):
                self._play_sound('./assets/music/explosion.wav')
                self.bullet.active = False
                self.score += 1
                
                # Respawn asteroid
                asteroid.pos.x = random.randint(0, 765)
                asteroid.pos.y = random.randint(0, 50)
    
    def _check_asteroid_collisions(self):
        """Check if asteroids hit bottom of screen."""
        for asteroid in self.enemy_manager.get_active_asteroids():
            if asteroid.pos.y > 500:
                self.screen_shake = 30
                asteroid.pos.x = random.randint(0, 765)
                asteroid.pos.y = random.randint(0, 50)
                self.lives -= 1
                
                if self.lives <= 0:
                    self.state_manager.transition(GameState.GAME_OVER)
    
    def _update(self):
        """Update game logic."""
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()
        
        self.bullet.update()
        
        self.enemy_manager.update(
            self.difficulty_scaler,
            self.player.pos,
            self.score
        )
        
        # Handle shooting
        if keys[pygame.K_SPACE] and not self.bullet.active:
            self._play_sound('./assets/music/laser.wav', 0.25)
            self.bullet.fire(self.player.pos.x, self.player.pos.y)
        
        self._check_collisions()
        self._check_asteroid_collisions()
        
        self.difficulty_scaler.update(1.0 / self.FPS)
        
        # Screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
    
    def _draw(self):
        """Draw game elements."""
        self.screen.fill((0, 0, 0))
        
        # Apply screen shake offset
        offset = (0, 0)
        if self.screen_shake > 0:
            offset = (random.randint(-4, 4), random.randint(-4, 4))
        
        # Draw background
        bg_index = min(self.score // 10, len(self.backgrounds) - 1)
        self.screen.blit(self.backgrounds[bg_index], (offset[0], offset[1]))
        
        # Draw entities
        self.player.draw(self.screen, offset)
        
        if self.bullet.active:
            self.bullet.draw(self.screen, offset)
        
        for asteroid in self.enemy_manager.get_active_asteroids():
            asteroid.draw(self.screen, offset)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_x = [680, 720, 760]
        for i in range(self.lives):
            self.screen.blit(self.lives_img, (lives_x[i], 12))
        
        pygame.display.update()
    
    def start_level(self, level: int):
        """Start a specific level."""
        self.score = 0
        self.lives = 3
        self.screen_shake = 0
        self.difficulty_scaler.reset()
        
        num_asteroids = level
        self.enemy_manager.initialize_level(num_asteroids)
        
        self.state_manager.transition(GameState.PLAYING)
        mixer.music.play(-1)
        self.music_playing = True
    
    def handle_events(self):
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state_manager.current_state == GameState.PLAYING:
                        self.state_manager.transition(GameState.PAUSED)
                    elif self.state_manager.current_state == GameState.PAUSED:
                        self.state_manager.transition(GameState.PLAYING)
                
                if event.key == pygame.K_m:
                    if self.music_playing:
                        mixer.music.stop()
                        self.music_playing = False
                    else:
                        mixer.music.play(-1)
                        self.music_playing = True
                
                if event.key == pygame.K_e and self.state_manager.current_state == GameState.GAME_OVER:
                    self.state_manager.transition(GameState.MENU)

                if event.key == pygame.K_ESCAPE and self.state_manager.current_state == GameState.GAME_OVER:
                    self._save_high_score()
                    self.state_manager.transition(GameState.MENU)    
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.click = True
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            
            state = self.state_manager.current_state
            
            if state == GameState.MENU:
                self._draw_menu()
            elif state == GameState.PLAYING:
                self._update()
                self._draw()
            elif state == GameState.PAUSED:
                self._draw_pause_menu()
            elif state == GameState.GAME_OVER:
                self._draw_game_over()
            
            self.clock.tick(self.FPS)
        
        pygame.quit()
    
    def _draw_menu(self):
        """Draw main menu."""
        self.screen.blit(self.menu_bg, (0, 0))
        
        title = self.menu_font.render("ASTEROID", True, (100, 150, 255))
        subtitle = self.menu_font_2.render("ATTACK", True, (200, 200, 255))
        self.screen.blit(title, title.get_rect(center=(400, 130)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(400, 180)))
        
        mx, my = pygame.mouse.get_pos()
        
        play_btn = pygame.Rect(300, 300, 200, 50)
        quit_btn = pygame.Rect(300, 380, 200, 50)
        
        play_color = (45, 55, 85) if play_btn.collidepoint((mx, my)) else (60, 70, 100)
        quit_color = (45, 55, 85) if quit_btn.collidepoint((mx, my)) else (60, 70, 100)
        
        pygame.draw.rect(self.screen, play_color, play_btn, border_radius=10)
        pygame.draw.rect(self.screen, quit_color, quit_btn, border_radius=10)
        
        play_text = self.menu_font_3.render("PLAY", True, (255, 255, 255))
        quit_text = self.menu_font_3.render("QUIT", True, (255, 255, 255))
        
        self.screen.blit(play_text, play_text.get_rect(center=play_btn.center))
        self.screen.blit(quit_text, quit_text.get_rect(center=quit_btn.center))
        
        if self.click:
            if play_btn.collidepoint((mx, my)):
                self.start_level(1)
                self.click = False
            if quit_btn.collidepoint((mx, my)):
                self.running = False
                self.click = False
        
        pygame.display.update()
        self.clock.tick(self.FPS)
    
    def _draw_pause_menu(self):
        """Draw pause menu."""
        self.screen.fill((0, 0, 0))
        self.overlay.fill((0, 0, 0, 180))
        self.screen.blit(self.overlay, (0, 0))
        
        pause_text = self.menu_font.render("PAUSED", True, (100, 150, 255))
        self.screen.blit(pause_text, pause_text.get_rect(center=(400, 150)))
        
        instructions = self.menu_font_3.render("Press ESC to resume or M for menu", True, (200, 220, 255))
        self.screen.blit(instructions, instructions.get_rect(center=(400, 270)))
        
        pygame.display.update()
        self.clock.tick(self.FPS)
    
    def _draw_game_over(self):
        """Draw game over screen."""
        self.screen.fill((0, 0, 0))
        
        game_over = self.over_font.render("GAME OVER", True, (255, 255, 255))
        self.screen.blit(game_over, game_over.get_rect(center=(400, 200)))
        
        high_score_text = self.score_font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(high_score_text, high_score_text.get_rect(center=(400, 280)))
        
        current_score = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(current_score, current_score.get_rect(center=(400, 330)))
        
        restart_text = self.menu_font_3.render("Press E to play again or ESC for menu", True, (200, 220, 255))
        self.screen.blit(restart_text, restart_text.get_rect(center=(400, 400)))
        
        pygame.display.update()
        self.clock.tick(self.FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
