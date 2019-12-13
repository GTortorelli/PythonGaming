from pygame import *
import pygame
from pygame.locals import *

# --- COLORS --- #
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
weird_gray = (54, 54, 54)

# --- Macros --- #
UP = 0
RIGHT = 1
LEFT = 3

pygame.init()
screen = pygame.display.set_mode(( 1380, 650 ))
pygame.display.set_caption('Square Shooters')
clock = pygame.time.Clock()

# --- Player --- #
p1_move = 0
player = [(10, 10)]
player_skin = pygame.image.load('player.png')
player_skin2 = pygame.Surface((20, 20))
player_skin2.fill(white)
p1_x = 200
p1_y = 200
p1_pos = (p1_x, p1_y) 

# --- classes --- #
class Player:
    def __init__(self, posx, posy):
        self.pos_x = posx
        self.pos_y = posy



# --- Main loop --- #
quit_ = True
while quit_:

    for event in pygame.event.get():
        # Quit
        if event.type == QUIT:
            pygame.quit()

        # Player moves
        if event.type == KEYUP:
            if event.key == K_UP:
                p1_move = UP

            if event.key == K_LEFT:
                p1_move = LEFT

            if event.key == K_RIGHT:
                p1_move = RIGHT

    screen.blit(player_skin, p1_pos)
    screen.blit(player_skin2, (300, 300))

    pygame.display.update()