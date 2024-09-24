import os
import pygame
from os.path import join
from random import randint
from PIL import Image
import json

# Initialize Pygame
pygame.init()

# Game Settings
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Leaderboard File
LEADERBOARD_FILE = r'C:\Space shooter\Space shooter\leaderboard.txt'


def display_game_over():
    game_over_surf = font.render('Game Over', True, (255, 0, 0))
    score_surf = font.render(f'Final Score: {score:.2f}', True, (255, 255, 255))
    restart_surf = font.render('Press R to Restart or Q to Quit', True, (255, 255, 255))

    game_over_rect = game_over_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
    score_rect = score_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
    restart_rect = restart_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))

    display_surface.blit(game_over_surf, game_over_rect)
    display_surface.blit(score_surf, score_rect)
    display_surface.blit(restart_surf, restart_rect)

paused = False

def display_pause_menu():
    pause_surf = font.render('Paused', True, (255, 0, 0))
    resume_surf = font.render('Press R to Resume', True, (255, 255, 255))
    controls_surf = font.render('Press C for Controls', True, (255, 255, 255))
    score_surf = font.render(f'Score: {score}', True, (255, 255, 255))
    quit_surf = font.render('Press Q to Quit', True, (255, 255, 255))

    pause_rect = pause_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
    resume_rect = resume_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
    controls_rect = controls_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
    score_rect = score_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
    quit_rect = quit_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))

    display_surface.blit(pause_surf, pause_rect)
    display_surface.blit(resume_surf, resume_rect)
    display_surface.blit(controls_surf, controls_rect)
    display_surface.blit(score_surf, score_rect)
    display_surface.blit(quit_surf, quit_rect)

show_controls = False

def display_controls():
    controls_surf = font.render('Controls:', True, (255, 255, 0))
    move_surf = font.render('Arrow Keys to Move', True, (255, 255, 255))
    shoot_surf = font.render('Space to Shoot', True, (255, 255, 255))
    back_surf = font.render('Press B to Back', True, (255, 255, 255))

    display_surface.fill((0, 0, 0))  # Clear screen for controls
    display_surface.blit(controls_surf, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 60))
    display_surface.blit(move_surf, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 20))
    display_surface.blit(shoot_surf, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 20))
    display_surface.blit(back_surf, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 60))

def load_gif_frames(gif_path):
    with Image.open(gif_path) as img:
        frames = []
        for frame in range(img.n_frames):
            img.seek(frame)
            frame_surface = pygame.image.frombuffer(img.tobytes(), img.size, img.mode).convert_alpha()
            frame_surface = pygame.transform.scale(frame_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            frames.append(frame_surface)
        return frames


# Load GIF and extract frames for background
background_gif_path = r'C:\Space shooter\Space shooter\images\lightspeed-10957.gif'
background_frames = load_gif_frames(background_gif_path)
background_index = 0
background_time = 0
frame_duration = 100

# Load laser GIF frames
laser_gif_path = r'C:\Space shooter\Space shooter\images\laser.gif'
laser_frames = load_gif_frames(laser_gif_path)

# Load Resources
font = pygame.font.Font(join(r"C:\Space shooter\Space shooter\images\Oxanium-Bold.ttf"), 20)

# Load explosion frames
explosion_folder = r"C:\Space shooter\Space shooter\images\explosion"
explosion_frames = []
for filename in os.listdir(explosion_folder):
    if filename.endswith('.png'):
        image_path = os.path.join(explosion_folder, filename)
        explosion_frames.append(pygame.image.load(image_path).convert_alpha())

# Load asteroid images
asteroid_folder = r"C:\Space shooter\Space shooter\images\spacegame_asset_pack"
asteroid_surfs = []
for filename in os.listdir(asteroid_folder):
    if filename.startswith("asteroid_") and filename.endswith('.png'):
        image_path = os.path.join(asteroid_folder, filename)
        asteroid_surfs.append(pygame.image.load(image_path).convert_alpha())

# Load Sounds
laser_sound = pygame.mixer.Sound(join(r'C:\Space shooter\Space shooter\audio\laser.wav'))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join(r'C:\Space shooter\Space shooter\audio\explosion.wav'))
explosion_sound.set_volume(0.1)
game_music = pygame.mixer.Sound(join(r'C:\Space shooter\Space shooter\audio\game_music.wav'))
game_music.set_volume(0.1)
game_music.play(loops=-1)

# Sprite Groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()


# Score and Health Variables
score = 0
player_health = 3
score_multiplier = 1  # New variable for score multiplier


def display_health_and_score():
    health_surf = font.render(f'Health: {player_health}', True, (255, 0, 0))
    score_surf = font.render(f'Score: {score * score_multiplier}', True, (255, 255, 255))
    display_surface.blit(health_surf, (10, 40))
    display_surface.blit(score_surf, (10, 70))  # Display score below health


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []


def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f)


def update_leaderboard(score):
    leaderboard = load_leaderboard()
    leaderboard.append(score)
    leaderboard.sort(reverse=True)
    leaderboard = leaderboard[:10]
    save_leaderboard(leaderboard)
    return leaderboard


def display_health():
    health_surf = font.render(f'Health: {player_health}', True, (255, 0, 0))
    display_surface.blit(health_surf, (10, 40))


def collision():
    global running, game_over, score, player_health, player, score_multiplier

    # Check for collision between player and meteors
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True)
    if collision_sprites:
        player_health -= 1  # Reduce health on collision
        for meteor in collision_sprites:
            AnimatedExplosion(explosion_frames, player.rect.center, all_sprites)  # Create explosion at player's position
            explosion_sound.play()  # Play explosion sound
        if player_health <= 0:
            game_over = True  # Trigger game over state

    # Check for collision between lasers and meteors
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()  # Kill the laser only if it hits meteors
            for meteor in collided_sprites:
                AnimatedExplosion(explosion_frames, meteor.rect.midtop, all_sprites)
                explosion_sound.play()
                score += 1 * score_multiplier  # Increment score for each meteor hit

    # Check for collision between lasers and enemies
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, enemy_sprites, True)
        if collided_sprites:
            laser.kill()  # Kill the laser if it hits an enemy
            for enemy in collided_sprites:
                AnimatedExplosion(explosion_frames, enemy.rect.midtop, all_sprites)
                explosion_sound.play()
                score += 2 * score_multiplier  # Increment score for each enemy hit

    # Check for collision between the player and enemies
    collision_enemies = pygame.sprite.spritecollide(player, enemy_sprites, True)
    if collision_enemies:
        player_health -= 1  # Reduce health on enemy contact
        for enemy in collision_enemies:
            enemy.kill()  # Remove the enemy upon collision
            AnimatedExplosion(explosion_frames, player.rect.center, all_sprites)  # Create explosion at player's position
            explosion_sound.play()  # Play explosion sound
        if player_health <= 0:
            game_over = True  # Trigger game over state


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, pos, groups):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.speed = randint(100, 200)

    def update(self, dt):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join(r"C:\Space shooter\Space shooter\images\player.png")).convert_alpha()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.base_speed = 500
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        self.keyboard_timer = 0
        self.keyboard_inactivity_duration = 2000
        self.keyboard_control = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
            self.rect.center += self.direction * self.base_speed * dt
            self.keyboard_control = True
            self.keyboard_timer = pygame.time.get_ticks()
        elif not self.keyboard_control and pygame.time.get_ticks() - self.keyboard_timer > self.keyboard_inactivity_duration:
            self.keyboard_control = False

        if keys[pygame.K_SPACE] and self.can_shoot:
            AnimatedLaser(laser_frames, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

    def laser_timer(self):
        if not self.can_shoot and pygame.time.get_ticks() - self.laser_shoot_time >= self.cooldown_duration:
            self.can_shoot = True


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


class AnimatedLaser(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = pygame.transform.scale(self.frames[self.frame_index], (10, 30))
        self.rect = self.image.get_rect(midbottom=pos)
        self.animation_timer = 0
        self.frame_duration = 100

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

        self.animation_timer += dt * 1000
        if self.animation_timer >= self.frame_duration:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.frame_index], (10, 30))
            self.animation_timer = 0


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.speed = randint(100, 200)

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

def spawn_meteor():
    Meteor(asteroid_surfs[randint(0, len(asteroid_surfs) - 1)],
           (randint(0, WINDOW_WIDTH), -50), (all_sprites, meteor_sprites))

# Main Game Loop
running = True
game_over = False
player = Player(all_sprites)

while running:
    dt = clock.tick(60) / 1000
    display_surface.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Pause the game with ESC
                paused = not paused  # Toggle pause state
            if paused:
                if event.key == pygame.K_r:  # Resume
                    paused = False
                if event.key == pygame.K_c:  # Start showing controls
                    show_controls = True
                if event.key == pygame.K_q:  # Quit
                    running = False
            elif game_over:
                if event.key == pygame.K_r:
                    # Reset game state
                    player_health = 3
                    score = 0
                    score_multiplier = 1  # Reset score multiplier
                    enemy_sprites.empty()
                    all_sprites.empty()
                    player = Player(all_sprites)
                    game_over = False
                if event.key == pygame.K_q:
                    running = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_c:  # Stop showing controls when C is released
                show_controls = False

    if not paused and not game_over:
        if randint(1, 100) <= 5:
            spawn_meteor()

        # Update all sprite groups
        all_sprites.update(dt)
        meteor_sprites.update(dt)
        laser_sprites.update(dt)
        enemy_sprites.update(dt)  # Update enemy sprites
        collision()

        display_surface.blit(background_frames[background_index], (0, 0))

        # Update background frames
        background_time += dt * 1000
        if background_time >= frame_duration:
            background_index = (background_index + 1) % len(background_frames)
            background_time = 0

        # Draw sprites
        all_sprites.draw(display_surface)
        display_health_and_score()  # Call the new function here
    elif paused:
        display_pause_menu()
        if show_controls:  # Display controls if the flag is true
            display_controls()
    else:
        display_game_over()

    pygame.display.update()

# Save leaderboard and quit
update_leaderboard(score)
pygame.quit()
