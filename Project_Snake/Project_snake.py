import pygame, random
from pygame.locals import *
# --- DEFs --- #
def on_grid_random():
    x = random.randint(0, 590)
    y = random.randint(0, 590)
    return(x//10 * 10, y//10 * 10)

def collision(c1, c2):
    return(c1[0] == c2[0]) and (c1[1] == c2[1])

# --- CONFIGS --- #
FPS = 20
# --- Colors --- # 
white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

# --- MACROS --- #
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

pygame.init()
screen = pygame.display.set_mode(( 700, 700 ))
pygame.display.set_caption('SnakeGame')

# --- Snake atrbutes --- #
snake = [(200, 200), (210, 200), (220, 200)]
snake_skin = pygame.Surface((10, 10))
snake_skin.fill( white )
my_direction = LEFT

# --- APPLE atributes --- #
apple = pygame.Surface((10, 10))
apple.fill(red)
apple_pos = on_grid_random()

clock = pygame.time.Clock()

# --- Wall Atributes --- #

# --- MAIN LOOP --- #
while True:
    clock.tick(FPS)

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

    if collision(snake[0], apple_pos):
        apple_pos = on_grid_random()
        snake.append((0, 0))
        
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

    if collision( snake )

    screen.fill(black)
    screen.blit(apple, apple_pos)
    for pos in snake: 
        screen.blit(snake_skin, pos)

    pygame.display.update()
