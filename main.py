import pygame, random, math
from pygame import mixer

pygame.init()

# Screen Size (x, y)
screen = pygame.display.set_mode((800, 600))

# Frame Rate
clock = pygame.time.Clock()

# Background
background1 = pygame.image.load('./assets/images/background1.png')
background2 = pygame.image.load('./assets/images/background2.png')
background3 = pygame.image.load('./assets/images/background3.png')
background4 = pygame.image.load('./assets/images/background4.png')
background5 = pygame.image.load('./assets/images/background5.png')
background6 = pygame.image.load('./assets/images/background6.png')

# Background Sound
pygame.mixer.init()
mixer.music.load('./assets/music/background.wav')
mixer.music.set_volume(0.5)
music_stopped = False

# Title & Icon
pygame.display.set_caption('Asteroid Attack')
icon = pygame.image.load('./assets/images/asteroid1.png')
pygame.display.set_icon(icon)

# Player
playerImg = pygame.image.load('./assets/images/spaceship3.png')
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyY_change = []
num_of_enemies = 2

asteroid_images = ['./assets/images/asteroid1.png', './assets/images/asteroid2.png', './assets/images/asteroid3.png']
for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
    enemyX.append(random.randint(0, 765))
    enemyY.append(random.randint(0, 200))
    enemyY_change.append(2)

# Projectile
projectileImg = pygame.image.load('./assets/images/projectile.png')
projectileX = 370
projectileY = 480
projectileY_change = 6
projectile_status = "ready"

# Score
score_value = 0

try:
    with open('file.txt', 'r') as file:
        content = file.read()
    high_score = int(content)
except(ValueError, FileNotFoundError):
    high_score = 0

font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 32)
score_font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 42)

textX = 10
textY = 10

# Game Over
over_font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 64)
gameover = False

# Play Again
again_font = pygame.font.Font('./assets/fonts/Rajdhani-Medium.ttf', 24)

# Main Menu
menu_font = pygame.font.Font('./assets/fonts/Poppins-BlackItalic.ttf', 50)
menu_font_2 = pygame.font.Font('./assets/fonts/Poppins-MediumItalic.ttf', 42)
menu_font_3 = pygame.font.Font('./assets/fonts/Poppins-Regular.ttf', 36)
click = False

# Instructions
instructions_font = pygame.font.Font('./assets/fonts/Poppins-BlackItalic.ttf', 50)
instructions_font2 = pygame.font.Font('./assets/fonts/Poppins-Regular.ttf', 36)
instructions_font3 = pygame.font.Font('./assets/fonts/Anton-Regular.ttf', 40)
new_click = False

# Levels
level_font = pygame.font.Font('./assets/fonts/Poppins-BlackItalic.ttf', 50)
levels_font = pygame.font.Font('./assets/fonts/Poppins-Regular.ttf', 36)
level_click = False

# Lives
livesImg = pygame.image.load('./assets/images/heart.png')
lives = 3
lives_shown = [True, True, True]

# Pause Menu
pause_font = pygame.font.Font('./assets/fonts/Poppins-BlackItalic.ttf', 64)
pause_font2 = pygame.font.Font('./assets/fonts/Poppins-Regular.ttf', 32)
pause_font3 = pygame.font.Font('./assets/fonts/Poppins-Regular.ttf', 24)

overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 180))
paused = False

pause_click = False


def pause_menu():
    global paused, music_stopped, pause_click

    game_frame = screen.copy()

    waiting = True
    while waiting:
        screen.blit(game_frame, (0, 0))

        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Title
        pause_text = pause_font.render("GAME PAUSED", True, (100, 150, 255))
        screen.blit(pause_text, pause_text.get_rect(center = (400, 150)))

        # Instructions
        instructions = pause_font3.render("Press ESC to resume", True, (200, 220, 255))
        screen.blit(instructions, instructions.get_rect(center = (400, 230)))

        # Mouse
        mx, my = pygame.mouse.get_pos()

        # Resume Button
        resume_button = pygame.Rect(300, 300, 200, 50)
        if resume_button.collidepoint((mx, my)):
            pygame.draw.rect(screen, (45, 55, 85), resume_button, border_radius = 10)
            if pause_click:
                waiting = False
        else:
            pygame.draw.rect(screen, (60, 70, 100), resume_button, border_radius = 10)

        resume_text = pause_font2.render("RESUME", True, (255, 255, 255))
        screen.blit(resume_text, resume_text.get_rect(center = (resume_button.center)))

        # Main Menu Button
        menu_button = pygame.Rect(300, 370, 200, 50)
        if menu_button.collidepoint((mx, my)):
            pygame.draw.rect(screen, (45, 55, 85), menu_button, border_radius = 10)
            if pause_click:
                return "menu"
        else:
            pygame.draw.rect(screen, (60, 70, 100), menu_button, border_radius = 10)

        menu_text = pause_font2.render("MAIN MENU", True, (255, 255, 255))
        screen.blit(menu_text, menu_text.get_rect(center = (menu_button.center)))


        pause_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pause_click = True

        pygame.display.update()
        clock.tick(60)

    return "resume"


def main_menu():
    global click
    click = False
    menu_bg = pygame.image.load('./assets/images/menu_bg.png')

    while True:
        screen.blit(menu_bg, (0, 0))

        # Title
        title_text = menu_font.render("ASTEROID", True, (100, 150, 255))
        subtitle_text = menu_font_2.render("ATTACK", True, (200, 200, 255))
        screen.blit(title_text, title_text.get_rect(center=(400, 130)))
        screen.blit(subtitle_text, subtitle_text.get_rect(center=(400, 180)))

        # Mouse position
        mx, my = pygame.mouse.get_pos()

        # Buttons
        button_play = pygame.Rect(300, 300, 200, 50)
        button_quit = pygame.Rect(300, 380, 200, 50)

        if button_play.collidepoint((mx, my)):
            pygame.draw.rect(screen, (45, 55, 85), button_play, border_radius=10)
            if click:
                instructions_screen()
                click = False
        else:
            pygame.draw.rect(screen, (60, 70, 100), button_play, border_radius=10)

        if button_quit.collidepoint((mx, my)):
            pygame.draw.rect(screen, (45, 55, 85), button_quit, border_radius=10)
            if click:
                pygame.quit()
                quit()
        else:
            pygame.draw.rect(screen, (60, 70, 100), button_quit, border_radius=10)

        play_text = menu_font_3.render("PLAY", True, (255, 255, 255))
        quit_text = menu_font_3.render("QUIT", True, (255, 255, 255))
        screen.blit(play_text, play_text.get_rect(center=button_play.center))
        screen.blit(quit_text, quit_text.get_rect(center=button_quit.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        clock.tick(60)


def instructions_screen():
    global new_click
    new_click = False
    instructions_bg = pygame.image.load('./assets/images/menu_bg.png')
    while True:
        screen.blit(instructions_bg, (0, 0))

        # Text
        instructions_title = instructions_font.render("HOW TO PLAY", True, (100, 150, 255))
        screen.blit(instructions_title, instructions_title.get_rect(center = (400, 90)))

        instructions_text = [
            "Move: Left and Right Arrow Keys",
            "Shoot: Press SPACE",
            "One shot at a time!",
            "Mute/Unmute Music: Press M",
            "Restart: Press E after Game Over",
            "Quit: Press ESC anytime",
        ]

        for i, line in enumerate(instructions_text):
            text = instructions_font2.render(line, True, (200, 220, 255))
            screen.blit(text, text.get_rect(center = (400, 200 + i * 38)))

        # Mouse Position
        mx, my = pygame.mouse.get_pos()

        # Button
        continue_button = pygame.Rect(300, 480, 200, 50)

        if continue_button.collidepoint((mx, my)):
            pygame.draw.rect(screen, (45, 55, 85), continue_button, border_radius = 10)
            if new_click:
                levels()
                new_click = False
        else:
            pygame.draw.rect(screen, (60, 70, 100), continue_button, border_radius = 10)

        continue_text = instructions_font2.render("Continue", True, (255, 255, 255))
        screen.blit(continue_text, continue_text.get_rect(center = (continue_button.center)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    new_click = True

        pygame.display.update()
        clock.tick(60)

    
def levels():
    global level_click
    level_click = False
    levels_bg = pygame.image.load('./assets/images/menu_bg.png')

    while True:
        screen.blit(levels_bg, (0, 0))

        # Title
        levels_title_text = level_font.render("LEVELS", True, (100, 150, 255))
        screen.blit(levels_title_text, levels_title_text.get_rect(center = (400, 100)))

        # Mouse Position
        mx, my = pygame.mouse.get_pos()

        # Buttons
        level1_button = pygame.Rect(240, 200, 80, 80)
        level2_button = pygame.Rect(360, 200, 80, 80)
        level3_button = pygame.Rect(480, 200, 80, 80)
        level4_button = pygame.Rect(240, 320, 80, 80)
        level5_button = pygame.Rect(360, 320, 80, 80)
        level6_button = pygame.Rect(480, 320, 80, 80)

        if level1_button.collidepoint((mx, my)):
            pygame.draw.circle(screen, (45, 55, 85), (level1_button.center), 40)
            if level_click:
                level1()
                level_click = False
        else:
            pygame.draw.circle(screen, (60, 70, 100), (level1_button.center), 40)


        if level2_button.collidepoint((mx, my)):
            pygame.draw.circle(screen, (45, 55, 85), (level2_button.center), 40)
            if level_click:
                level2()
                level_click = False
        else:
            pygame.draw.circle(screen, (60, 70, 100), (level2_button.center), 40)

        
        if level3_button.collidepoint((mx, my)):
            pygame.draw.circle(screen, (45, 55, 85), (level3_button.center), 40)
            if level_click:
                level3()
                level_click = False
        else:
            pygame.draw.circle(screen, (60, 70, 100), (level3_button.center), 40)

        
        if level4_button.collidepoint((mx, my)):
            pygame.draw.circle(screen, (45, 55, 85), (level4_button.center), 40)
            if level_click:
                level4()
                level_click = False
        else:
            pygame.draw.circle(screen, (60, 70, 100), (level4_button.center), 40)


        if level5_button.collidepoint((mx, my)):
            pygame.draw.circle(screen, (45, 55, 85), (level5_button.center), 40)
            if level_click:
                level5()
                level_click = False
        else:
            pygame.draw.circle(screen, (60, 70, 100), (level5_button.center), 40)


        if level6_button.collidepoint((mx, my)):
            pygame.draw.circle(screen, (45, 55, 85), (level6_button.center), 40)
            if level_click:
                level6()
                level_click = False
        else:
            pygame.draw.circle(screen, (60, 70, 100), (level6_button.center), 40)


        level_texts = [
            (level1_button.center, "1"),
            (level2_button.center, "2"),
            (level3_button.center, "3"),
            (level4_button.center, "4"),
            (level5_button.center, "5"),
            (level6_button.center, "6"),
        ]

        for pos, label in level_texts:
            text = levels_font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center = pos))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    level_click = True

        pygame.display.update()
        clock.tick(60)


def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    global gameover
    global high_score
    global score_value
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    over_text_rect = over_text.get_rect(center = (400, 250))
    screen.blit(over_text, over_text_rect)

    if score_value > high_score:
        high_score = score_value

    score_text = score_font.render("High Score: " + str(high_score), True, (255, 255, 255))
    score_text_rect = score_text.get_rect(center = (400, 300))
    screen.blit(score_text, score_text_rect)

    play_again_text = again_font.render("Press 'E' to play again", True, (255, 255, 255))
    play_again_text_rect = play_again_text.get_rect(center = (400, 340))
    screen.blit(play_again_text, play_again_text_rect)

    # game_over_sound = mixer.Sound('game_over.wav')
    # game_over_sound.play()
    pygame.mixer.music.stop()
    gameover = True


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
    

screen_shake = 0


# Level One
def level1():
    global playerX, playerY, playerX_change
    global projectileX, projectileY, projectile_status, score_value, gameover
    global music_stopped
    global num_of_enemies, asteroid_images
    global projectileY_change
    global lives, livesImg, lives_shown
    global screen_shake

    render_offset = [0, 0]

    music_stopped = False

    projectileY_change = 7
    
    mixer.music.play(-1)

    num_of_enemies = 1
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
        enemyX.append(random.randint(0, 765))
        enemyY.append(random.randint(0, 50))
        enemyY_change.append(2)

    running = True
    while running:

        # Background Color (rgb)
        screen.fill((0, 0, 0))
        screen.blit(background1, (render_offset[0], render_offset[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not gameover:
                    playerX_change = -7
                if event.key == pygame.K_RIGHT and not gameover:
                    playerX_change = 7
                if event.key == pygame.K_SPACE and not gameover:
                    if projectile_status == "ready":
                        projectile_Sound = mixer.Sound('./assets/music/laser.wav')
                        projectile_Sound.play()
                        projectile_Sound.set_volume(0.25)
                        projectileX = playerX
                        fire_projectile(projectileX, projectileY)
                if event.key == pygame.K_m and not music_stopped:
                    mixer.music.stop()
                    music_stopped = True
                elif event.key == pygame.K_m and music_stopped:
                    mixer.music.play()
                    music_stopped = False
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "menu":
                        running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
                if event.key == pygame.K_e and gameover:
                    projectile_status = "ready"
                    score_value = 0
                    lives = 3
                    lives_shown = [True, True, True]
                    gameover = False
                    mixer.music.play(-1)
                    playerX = 370
                    playerY = 480
                    for i in range(num_of_enemies):
                        enemyX[i] = random.randint(0, 765)
                        enemyY[i] = random.randint(0, 50)

        playerX += playerX_change

        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        for i in range(num_of_enemies):
            if enemyY[i] > 500:
                if lives == 1:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    with open('file.txt', 'w') as file:
                        file.write(str(high_score))
                    break

            enemyY[i] += enemyY_change[i]
            if enemyY[i] >= 520:
                screen_shake = 30
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                lives -= 1

            
            if screen_shake > 0:
                render_offset[0] = random.randint(0, 8) - 4
                render_offset[1] = random.randint(0, 8) - 4
                screen_shake -= 1
            else:
                render_offset = [0, 0]



            if lives == 2:
                lives_shown = [False, True, True]
            if lives == 1:
                lives_shown = [False, False, True]
            if lives == 0:
                lives_shown = [False, False, False]

            if lives_shown[0]:
                screen.blit(livesImg, (680, 12))
            if lives_shown[1]:
                screen.blit(livesImg, (720, 12))
            if lives_shown[2] and lives >= 1:
                screen.blit(livesImg, (760, 12))

            if isCollision(enemyX[i], enemyY[i], projectileX, projectileY):
                collision_Sound = mixer.Sound('./assets/music/explosion.wav')
                collision_Sound.play()
                collision_Sound.set_volume(0.7)
                projectileY = 480
                projectile_status = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                enemyImg[i] = pygame.image.load(random.choice(asteroid_images))

            enemy(enemyX[i] + render_offset[0], enemyY[i] + render_offset[1], i)

        if projectileY <= 0:
            projectileY = 480
            projectile_status = "ready"

        if projectile_status == "fire":
            fire_projectile(projectileX + render_offset[0], projectileY + render_offset[1])
            projectileY -= projectileY_change

        player(playerX + render_offset[0], playerY + render_offset[1])
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(60)



# Level Two
def level2():
    global playerX, playerY, playerX_change
    global projectileX, projectileY, projectile_status, score_value, gameover
    global music_stopped
    global projectileY_change
    global lives, livesImg, lives_shown
    global screen_shake

    render_offset = [0, 0]

    projectileY_change = 8

    mixer.music.play(-1)

    num_of_enemies = 2
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
        enemyX.append(random.randint(0, 765))
        enemyY.append(random.randint(0, 50))
        enemyY_change.append(2)


    running = True
    while running:

        # Background Color (rgb)
        screen.fill((0, 0, 0))
        screen.blit(background2, (render_offset[0], render_offset[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not gameover:
                    playerX_change = -7
                if event.key == pygame.K_RIGHT and not gameover:
                    playerX_change = 7
                if event.key == pygame.K_SPACE and not gameover:
                    if projectile_status == "ready":
                        projectile_Sound = mixer.Sound('./assets/music/laser.wav')
                        projectile_Sound.play()
                        projectile_Sound.set_volume(0.25)
                        projectileX = playerX
                        fire_projectile(projectileX, projectileY)
                if event.key == pygame.K_m and not music_stopped:
                    mixer.music.stop()
                    music_stopped = True
                elif event.key == pygame.K_m and music_stopped:
                    mixer.music.play()
                    music_stopped = False
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "menu":
                        running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
                if event.key == pygame.K_e and gameover:
                    projectile_status = "ready"
                    score_value = 0
                    lives = 3
                    lives_shown = [True, True, True]
                    gameover = False
                    mixer.music.play(-1)
                    playerX = 370
                    playerY = 480
                    for i in range(num_of_enemies):
                        enemyX[i] = random.randint(0, 765)
                        enemyY[i] = random.randint(0, 50)

        playerX += playerX_change

        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        
        for i in range(num_of_enemies):
            if enemyY[i] > 500:
                if lives == 1:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    with open('file.txt', 'w') as file:
                        file.write(str(high_score))
                    break

            enemyY[i] += enemyY_change[i]
            if enemyY[i] >= 520:
                screen_shake = 30
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                lives -= 1

            
            if screen_shake > 0:
                render_offset[0] = random.randint(0, 8) - 4
                render_offset[1] = random.randint(0, 8) - 4
                screen_shake -= 1
            else:
                render_offset = [0, 0]


            if lives == 2:
                lives_shown = [False, True, True]
            if lives == 1:
                lives_shown = [False, False, True]
            if lives == 0:
                lives_shown = [False, False, False]

            if lives_shown[0]:
                screen.blit(livesImg, (680, 12))
            if lives_shown[1]:
                screen.blit(livesImg, (720, 12))
            if lives_shown[2] and lives >= 1:
                screen.blit(livesImg, (760, 12))


            if isCollision(enemyX[i], enemyY[i], projectileX, projectileY):
                collision_Sound = mixer.Sound('./assets/music/explosion.wav')
                collision_Sound.play()
                collision_Sound.set_volume(0.7)
                projectileY = 480
                projectile_status = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                enemyImg[i] = pygame.image.load(random.choice(asteroid_images))

            enemy(enemyX[i] + render_offset[0], enemyY[i] + render_offset[1], i)

        if projectileY <= 0:
            projectileY = 480
            projectile_status = "ready"

        if projectile_status == "fire":
            fire_projectile(projectileX, projectileY)
            projectileY -= projectileY_change

        player(playerX + render_offset[0], playerY + render_offset[1])
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(60)


# Level Three
def level3():
    global playerX, playerY, playerX_change
    global projectileX, projectileY, projectile_status, score_value, gameover
    global music_stopped
    global projectileY_change
    global lives, livesImg, lives_shown
    global screen_shake

    render_offset = [0, 0]

    projectileY_change = 9

    mixer.music.play(-1)

    num_of_enemies = 3
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
        enemyX.append(random.randint(0, 765))
        enemyY.append(random.randint(0, 50))
        enemyY_change.append(2)


    running = True
    while running:

        # Background Color (rgb)
        screen.fill((0, 0, 0))
        screen.blit(background3, (render_offset[0], render_offset[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not gameover:
                    playerX_change = -7
                if event.key == pygame.K_RIGHT and not gameover:
                    playerX_change = 7
                if event.key == pygame.K_SPACE and not gameover:
                    if projectile_status == "ready":
                        projectile_Sound = mixer.Sound('./assets/music/laser.wav')
                        projectile_Sound.play()
                        projectile_Sound.set_volume(0.25)
                        projectileX = playerX
                        fire_projectile(projectileX, projectileY)
                if event.key == pygame.K_m and not music_stopped:
                    mixer.music.stop()
                    music_stopped = True
                elif event.key == pygame.K_m and music_stopped:
                    mixer.music.play()
                    music_stopped = False
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "menu":
                        running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
                if event.key == pygame.K_e and gameover:
                    projectile_status = "ready"
                    score_value = 0
                    lives = 3
                    lives_shown = [True, True, True]
                    gameover = False
                    mixer.music.play(-1)
                    playerX = 370
                    playerY = 480
                    for i in range(num_of_enemies):
                        enemyX[i] = random.randint(0, 765)
                        enemyY[i] = random.randint(0, 50)

        playerX += playerX_change

        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        
        for i in range(num_of_enemies):
            if enemyY[i] > 500:
                if lives == 1:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    with open('file.txt', 'w') as file:
                        file.write(str(high_score))
                    break

            enemyY[i] += enemyY_change[i]
            if enemyY[i] >= 520:
                screen_shake = 30
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                lives -= 1

            
            if screen_shake > 0:
                render_offset[0] = random.randint(0, 8) - 4
                render_offset[1] = random.randint(0, 8) - 4
                screen_shake -= 1
            else:
                render_offset = [0, 0]


            if lives == 2:
                lives_shown = [False, True, True]
            if lives == 1:
                lives_shown = [False, False, True]
            if lives == 0:
                lives_shown = [False, False, False]

            if lives_shown[0]:
                screen.blit(livesImg, (680, 12))
            if lives_shown[1]:
                screen.blit(livesImg, (720, 12))
            if lives_shown[2] and lives >= 1:
                screen.blit(livesImg, (760, 12))

            if isCollision(enemyX[i], enemyY[i], projectileX, projectileY):
                collision_Sound = mixer.Sound('./assets/music/explosion.wav')
                collision_Sound.play()
                collision_Sound.set_volume(0.7)
                projectileY = 480
                projectile_status = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                enemyImg[i] = pygame.image.load(random.choice(asteroid_images))

            enemy(enemyX[i] + render_offset[0], enemyY[i] + render_offset[1], i)

        if projectileY <= 0:
            projectileY = 480
            projectile_status = "ready"

        if projectile_status == "fire":
            fire_projectile(projectileX, projectileY)
            projectileY -= projectileY_change

        player(playerX + render_offset[0], playerY + render_offset[1])
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(60)


# Level Four
def level4():
    global playerX, playerY, playerX_change
    global projectileX, projectileY, projectile_status, score_value, gameover
    global music_stopped
    global projectileY_change
    global lives, livesImg, lives_shown
    global screen_shake

    render_offset = [0, 0]

    projectileY_change = 10

    mixer.music.play(-1)

    num_of_enemies = 4
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
        enemyX.append(random.randint(0, 765))
        enemyY.append(random.randint(0, 50))
        enemyY_change.append(2)


    running = True
    while running:

        # Background Color (rgb)
        screen.fill((0, 0, 0))
        screen.blit(background4, (render_offset[0], render_offset[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not gameover:
                    playerX_change = -7
                if event.key == pygame.K_RIGHT and not gameover:
                    playerX_change = 7
                if event.key == pygame.K_SPACE and not gameover:
                    if projectile_status == "ready":
                        projectile_Sound = mixer.Sound('./assets/music/laser.wav')
                        projectile_Sound.play()
                        projectile_Sound.set_volume(0.25)
                        projectileX = playerX
                        fire_projectile(projectileX, projectileY)
                if event.key == pygame.K_m and not music_stopped:
                    mixer.music.stop()
                    music_stopped = True
                elif event.key == pygame.K_m and music_stopped:
                    mixer.music.play()
                    music_stopped = False
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "menu":
                        running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
                if event.key == pygame.K_e and gameover:
                    projectile_status = "ready"
                    score_value = 0
                    lives = 3
                    lives_shown = [True, True, True]
                    gameover = False
                    mixer.music.play(-1)
                    playerX = 370
                    playerY = 480
                    for i in range(num_of_enemies):
                        enemyX[i] = random.randint(0, 765)
                        enemyY[i] = random.randint(0, 50)

        playerX += playerX_change

        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        
        for i in range(num_of_enemies):
            if enemyY[i] > 500:
                if lives == 1:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    with open('file.txt', 'w') as file:
                        file.write(str(high_score))
                    break

            enemyY[i] += enemyY_change[i]
            if enemyY[i] >= 520:
                screen_shake = 30
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                lives -= 1

            
            if screen_shake > 0:
                render_offset[0] = random.randint(0, 8) - 4
                render_offset[1] = random.randint(0, 8) - 4
                screen_shake -= 1
            else:
                render_offset = [0, 0]


            if lives == 2:
                lives_shown = [False, True, True]
            if lives == 1:
                lives_shown = [False, False, True]
            if lives == 0:
                lives_shown = [False, False, False]

            if lives_shown[0]:
                screen.blit(livesImg, (680, 12))
            if lives_shown[1]:
                screen.blit(livesImg, (720, 12))
            if lives_shown[2] and lives >= 1:
                screen.blit(livesImg, (760, 12))

            if isCollision(enemyX[i], enemyY[i], projectileX, projectileY):
                collision_Sound = mixer.Sound('./assets/music/explosion.wav')
                collision_Sound.play()
                collision_Sound.set_volume(0.7)
                projectileY = 480
                projectile_status = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                enemyImg[i] = pygame.image.load(random.choice(asteroid_images))

            enemy(enemyX[i] + render_offset[0], enemyY[i] + render_offset[1], i)

        if projectileY <= 0:
            projectileY = 480
            projectile_status = "ready"

        if projectile_status == "fire":
            fire_projectile(projectileX, projectileY)
            projectileY -= projectileY_change

        player(playerX + render_offset[0], playerY + render_offset[1])
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(60)


# Level Five
def level5():
    global playerX, playerY, playerX_change
    global projectileX, projectileY, projectile_status, score_value, gameover
    global music_stopped
    global projectileY_change
    global lives, livesImg, lives_shown
    global screen_shake

    render_offset = [0, 0]

    projectileY_change = 11

    mixer.music.play(-1)

    num_of_enemies = 5
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
        enemyX.append(random.randint(0, 765))
        enemyY.append(random.randint(0, 50))
        enemyY_change.append(2)


    running = True
    while running:

        # Background Color (rgb)
        screen.fill((0, 0, 0))
        screen.blit(background5, (render_offset[0], render_offset[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not gameover:
                    playerX_change = -7
                if event.key == pygame.K_RIGHT and not gameover:
                    playerX_change = 7
                if event.key == pygame.K_SPACE and not gameover:
                    if projectile_status == "ready":
                        projectile_Sound = mixer.Sound('./assets/music/laser.wav')
                        projectile_Sound.play()
                        projectile_Sound.set_volume(0.25)
                        projectileX = playerX
                        fire_projectile(projectileX, projectileY)
                if event.key == pygame.K_m and not music_stopped:
                    mixer.music.stop()
                    music_stopped = True
                elif event.key == pygame.K_m and music_stopped:
                    mixer.music.play()
                    music_stopped = False
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "menu":
                        running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
                if event.key == pygame.K_e and gameover:
                    projectile_status = "ready"
                    score_value = 0
                    lives = 3
                    lives_shown = [True, True, True]
                    gameover = False
                    mixer.music.play(-1)
                    playerX = 370
                    playerY = 480
                    for i in range(num_of_enemies):
                        enemyX[i] = random.randint(0, 765)
                        enemyY[i] = random.randint(0, 50)

        playerX += playerX_change

        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        
        for i in range(num_of_enemies):
            if enemyY[i] > 500:
                if lives == 1:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    with open('file.txt', 'w') as file:
                        file.write(str(high_score))
                    break

            enemyY[i] += enemyY_change[i]
            if enemyY[i] >= 520:
                screen_shake = 30
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                lives -= 1

            
            if screen_shake > 0:
                render_offset[0] = random.randint(0, 8) - 4
                render_offset[1] = random.randint(0, 8) - 4
                screen_shake -= 1
            else:
                render_offset = [0, 0]


            if lives == 2:
                lives_shown = [False, True, True]
            if lives == 1:
                lives_shown = [False, False, True]
            if lives == 0:
                lives_shown = [False, False, False]

            if lives_shown[0]:
                screen.blit(livesImg, (680, 12))
            if lives_shown[1]:
                screen.blit(livesImg, (720, 12))
            if lives_shown[2] and lives >= 1:
                screen.blit(livesImg, (760, 12))

            if isCollision(enemyX[i], enemyY[i], projectileX, projectileY):
                collision_Sound = mixer.Sound('./assets/music/explosion.wav')
                collision_Sound.play()
                collision_Sound.set_volume(0.7)
                projectileY = 480
                projectile_status = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                enemyImg[i] = pygame.image.load(random.choice(asteroid_images))

            enemy(enemyX[i] + render_offset[0], enemyY[i] + render_offset[1], i)

        if projectileY <= 0:
            projectileY = 480
            projectile_status = "ready"

        if projectile_status == "fire":
            fire_projectile(projectileX, projectileY)
            projectileY -= projectileY_change

        player(playerX + render_offset[0], playerY + render_offset[1])
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(60)


# Level Six
def level6():
    global playerX, playerY, playerX_change
    global projectileX, projectileY, projectile_status, score_value, gameover
    global music_stopped
    global projectileY_change
    global lives, livesImg, lives_shown
    global screen_shake

    render_offset = [0, 0]

    projectileY_change = 12

    mixer.music.play(-1)

    num_of_enemies = 6
    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load(random.choice(asteroid_images)))
        enemyX.append(random.randint(0, 765))
        enemyY.append(random.randint(0, 50))
        enemyY_change.append(2)


    running = True
    while running:

        # Background Color (rgb)
        screen.fill((0, 0, 0))
        screen.blit(background6, (render_offset[0], render_offset[1]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not gameover:
                    playerX_change = -7
                if event.key == pygame.K_RIGHT and not gameover:
                    playerX_change = 7
                if event.key == pygame.K_SPACE and not gameover:
                    if projectile_status == "ready":
                        projectile_Sound = mixer.Sound('./assets/music/laser.wav')
                        projectile_Sound.play()
                        projectile_Sound.set_volume(0.25)
                        projectileX = playerX
                        fire_projectile(projectileX, projectileY)
                if event.key == pygame.K_m and not music_stopped:
                    mixer.music.stop()
                    music_stopped = True
                elif event.key == pygame.K_m and music_stopped:
                    mixer.music.play()
                    music_stopped = False
                if event.key == pygame.K_ESCAPE:
                    result = pause_menu()
                    if result == "menu":
                        running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    playerX_change = 0
                if event.key == pygame.K_e and gameover:
                    projectile_status = "ready"
                    score_value = 0
                    lives = 3
                    lives_shown = [True, True, True]
                    gameover = False
                    mixer.music.play(-1)
                    playerX = 370
                    playerY = 480
                    for i in range(num_of_enemies):
                        enemyX[i] = random.randint(0, 765)
                        enemyY[i] = random.randint(0, 50)

        playerX += playerX_change

        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        
        for i in range(num_of_enemies):
            if enemyY[i] > 500:
                if lives == 1:
                    for j in range(num_of_enemies):
                        enemyY[j] = 2000
                    game_over_text()
                    with open('file.txt', 'w') as file:
                        file.write(str(high_score))
                    break

            enemyY[i] += enemyY_change[i]
            if enemyY[i] >= 520:
                screen_shake = 30
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                lives -= 1

            
            if screen_shake > 0:
                render_offset[0] = random.randint(0, 8) - 4
                render_offset[1] = random.randint(0, 8) - 4
                screen_shake -= 1
            else:
                render_offset = [0, 0]


            if lives == 2:
                lives_shown = [False, True, True]
            if lives == 1:
                lives_shown = [False, False, True]
            if lives == 0:
                lives_shown = [False, False, False]

            if lives_shown[0]:
                screen.blit(livesImg, (680, 12))
            if lives_shown[1]:
                screen.blit(livesImg, (720, 12))
            if lives_shown[2] and lives >= 1:
                screen.blit(livesImg, (760, 12))

            if isCollision(enemyX[i], enemyY[i], projectileX, projectileY):
                collision_Sound = mixer.Sound('./assets/music/explosion.wav')
                collision_Sound.play()
                collision_Sound.set_volume(0.7)
                projectileY = 480
                projectile_status = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 765)
                enemyY[i] = random.randint(0, 50)
                enemyImg[i] = pygame.image.load(random.choice(asteroid_images))

            enemy(enemyX[i] + render_offset[0], enemyY[i] + render_offset[1], i)

        if projectileY <= 0:
            projectileY = 480
            projectile_status = "ready"

        if projectile_status == "fire":
            fire_projectile(projectileX, projectileY)
            projectileY -= projectileY_change

        player(playerX + render_offset[0], playerY + render_offset[1])
        show_score(textX, textY)
        pygame.display.update()
        clock.tick(60)
main_menu()