import pygame
import random
import math
from pygame import mixer

pygame.init()

# Screen Size (x, y)
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load('background.png')

# Background Sound
mixer.music.load('background.wav')
mixer.music.play(-1)

# Title & Icon
pygame.display.set_caption('Asteroid Attack')
icon = pygame.image.load('asteroid.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('spaceship.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyY_change = []
num_of_enemies = 2

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('asteroid.png'))
    enemyX.append(random.randint(0, 765))
    enemyY.append(random.randint(0, 50))
    enemyY_change.append(0.75)

# Projectile
projectileImg = pygame.image.load('projectile.png')
projectileX = 370
projectileY = 480
projectileY_change = 2
projectile_status = "ready"

# Score
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 30)

textX = 10
textY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)


def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))
    # game_over_sound = mixer.Sound('game_over.wav')
    # game_over_sound.play()
    pygame.mixer.music.stop()


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_projectile(x, y):
    global projectile_status
    projectile_status = "fire"
    screen.blit(projectileImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, projectileX, projectileY):
    distance = math.sqrt(math.pow(enemyX - projectileX, 2) + math.pow(enemyY - projectileY, 2))
    if distance < 32:
        return True
    else:
        return False


# Game Loop
running = True
while running:

    # Background Color (rgb)
    screen.fill((0, 0, 0))

    # Background Image
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard Controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -3
            if event.key == pygame.K_RIGHT:
                playerX_change = 3
            if event.key == pygame.K_SPACE:
                if projectile_status == "ready":
                    projectile_Sound = mixer.Sound('laser.wav')
                    projectile_Sound.play()
                    projectileX = playerX
                    fire_projectile(projectileX, projectileY)
            if event.key == pygame.K_ESCAPE:
                running = False
        if event.type == pygame.KEYUP:
            playerX_change = 0

    playerX += playerX_change

    # Boundaries
    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    for i in range(num_of_enemies):

        # Game Over
        if enemyY[i] > 440:
            for j in range(num_of_enemies):
                enemyY[j] = 2000
            game_over_text()
            break

        # Enemy Movement
        enemyY[i] += enemyY_change[i]
        if enemyY[i] >= 600:
            enemyX[i] = random.randint(0, 765)
            enemyY[i] = random.randint(0, 50)

        # Collision
        collision = isCollision(enemyX[i], enemyY[i], projectileX, projectileY)
        if collision:
            collision_Sound = mixer.Sound('explosion.wav')
            collision_Sound.play()
            projectileY = 480
            projectile_status = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, 765)
            enemyY[i] = random.randint(0, 50)

        enemy(enemyX[i], enemyY[i], i)

    # Projectile Movement
    if projectileY <= 0:
        projectileY = 480
        projectile_status = "ready"
    if projectile_status == "fire":
        fire_projectile(projectileX, projectileY)
        projectileY -= projectileY_change

    player(playerX, playerY)
    show_score(textX, textY)
    pygame.display.update()
