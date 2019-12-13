import pygame, random
from pygame.locals import *
# --- DEFs --- #
def on_grid_random():
    x = random.randint(20, 560)
    y = random.randint(20, 560)
    return(x//10 * 10, y//10 * 10)

def collision(c1, c2):
    return(c1[0] == c2[0]) and (c1[1] == c2[1])

# --- CONFIGS --- #
FPS = 20

# --- Colors --- # 
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
weird_gray = (54, 54, 54)

# --- MACROS --- #
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
pygame.init()
screen = pygame.display.set_mode(( 700, 700 ))
pygame.display.set_caption('SnakeGame')
clock = pygame.time.Clock()
cont = 0

# --- Snake atrbutes --- #
snake = [(200, 200), (210, 200), (220, 200)]
snake_skin = pygame.Surface((10, 10))
snake_skin.fill( white )
my_direction = LEFT

# --- APPLE atributes --- #
apple = pygame.Surface((10, 10))
apple.fill(red)
apple_pos = on_grid_random()


# --- Wall Atributes --- #
wall = pygame.Surface((2, 700))
wall.fill(white)
wall_place = wall.get_rect()
wall_place.center = (0, 700//2)
wall_pos = (0, 700//2)

wall2 = pygame.Surface((700, 2))
wall2.fill(white)
wall_place2 = wall2.get_rect()
wall_place2.center = (700//2, 0)

wall3 = pygame.Surface((2, 700))
wall3.fill(white)
wall_place3 = wall3.get_rect()
wall_place.center = (700, 700//2)

wall4 = pygame.Surface((700, 2))
wall4.fill(white)
wall_place4 = wall4.get_rect()
wall_place4.center = (700//2, 700)

# --- SOUND --- #
sound = pygame.mixer.Sound('sound.ogg')
sound2 = pygame.mixer.Sound('sound2.ogg')
sound3 = pygame.mixer.Sound('sound3.ogg')
sound2.play()

# --- IMAGES --- #
image = pygame.image.load('hqdefault.jpg')
# --- MAIN LOOP --- #
quit_ = True
while quit_:
    clock.tick(FPS)

    # snake control
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()

        if event.type == KEYDOWN:
            if event.key == K_UP:
                my_direction = UP
            if event.key == K_DOWN:
                my_direction = DOWN
            if event.key == K_LEFT:
                my_direction = LEFT
            if event.key == K_RIGHT:
                my_direction = RIGHT


    for i in range(len(snake) - 1, 0, -1):
        snake[i] = (snake[i-1][0], snake[i-1][1])

    if my_direction == UP:
        snake[0] = (snake[0][0], snake[0][1] - 10)

    if my_direction == DOWN:
        snake[0] = (snake[0][0], snake[0][1] + 10)

    if my_direction == RIGHT:
        snake[0] = (snake[0][0] + 10, snake[0][1])

    if my_direction == LEFT:
        snake[0] = (snake[0][0] - 10, snake[0][1])

    # Collision betweens snake and the apple
    if collision(snake[0], apple_pos):
        sound.play()
        cont += 1
        apple_pos = on_grid_random()
        snake.append((0, 0))

    # Control the collisin between the snake and the walls
    for i in range(1, len(snake)):
        if collision(snake[0], snake[i]):
            quit_ = False

    for i in range(0, 700):
        if collision(snake[0], (0, i)):
            quit_ = False

    for i in range(0, 700):
        if collision(snake[0], (i, 0)):
            quit_ = False

    for i in range(0, 700):
        if collision(snake[0], (700, i)):
            quit_ = False

    for i in range(0, 700):
        if collision(snake[0], (i, 700)):
            quit_ = False

    # Filling the screen background and the objects in screen
    screen.fill(weird_gray)
    screen.blit(apple, apple_pos)
    screen.blit(wall, wall_place)
    screen.blit(wall2, wall_place2)
    screen.blit(wall3, wall_place3)
    screen.blit(wall4, wall_place4)

    for pos in snake: 
        screen.blit(snake_skin, pos)

    # Score blitting
    font = pygame.font.Font(None, 40)
    text = font.render(f'Score: {cont}', True, white, None)
    textBack = text.get_rect()
    textBack.center = (500, 50)
    screen.blit(text, textBack)

    pygame.display.update()
    

sound2.stop()
sound3.play()

while True:
    screen.blit(image, (150, 150))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
