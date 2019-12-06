"""
Este programa é quase idêntico ao moving_platforms.py, mas demonstra uma
método Control.update_viewport () diferente que nos permite facilitar
rolagem.
Aqui a rolagem começa quando o jogador cruza 1/3 da tela.
A rolagem começa na metade da velocidade do jogador, mas quando o jogador atinge
a rolagem no meio do caminho corresponde à velocidade do próprio jogador.
-Escrito por Sean J. McKiernan 'Mekire'
-Traduzido e ajustado pro Mateus Viera Vasconcelos
"""

import os
import sys
import pygame as pg


CAPTION = "Plataformas em movimento"
SCREEN_SIZE = (700,500)


class _Physics(object):
    """Uma aula de física simplificada. Psuedo-gravidade é frequentemente bom o suficiente."""
    def __init__(self):
        """Você pode experimentar diferentes gravidades aqui."""
        self.velocity = [0, 0]
        self.grav = 1.0
        self.fall = False

    def physics_update(self):
        """Se o player estiver caindo, adicione gravidade à velocidade y atual."""
        if self.fall:
            self.velocity[1] += self.grav
        else:
            self.velocity[1] = 0


class Player(_Physics, pg.sprite.Sprite):
    """Classe representando nosso jogador."""
    def __init__(self,location,speed):
        """
        A localização é um par de coordenadas (x, y) e a velocidade é a
        velocidade em pixels por quadro. A velocidade deve ser um número inteiro.
        """
        _Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((30,55)).convert()
        self.image.fill(pg.Color("black"))
        self.rect = self.image.get_rect(topleft=location)
        self.frame_start_pos = None
        self.total_displacement = None
        self.speed = speed
        self.jump_power = -20.0
        self.jump_cut_magnitude = -3.0
        self.on_moving = False
        self.collide_below = False

    def check_keys(self, keys):
        """Encontre a auto.velocidade do jogador [0] com base nas teclas atualmente em espera."""
        self.velocity[0] = 0
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.velocity[0] -= self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.velocity[0] += self.speed

    def get_position(self, obstacles):
        """Calcule a posição do jogador neste quadro, incluindo colisões."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.velocity[1]),1,obstacles)
        if self.velocity[0]:
            self.check_collisions((self.velocity[0],0), 0, obstacles)

    def check_falling(self, obstacles):
        """Se o jogador não estiver em contato com o solo, entre no estado de queda."""
        if not self.collide_below:
            self.fall = True
            self.on_moving = False

    def check_moving(self,obstacles):
        """
        Verifique se o jogador está em uma plataforma móvel.
        Se o jogador estiver em contato com várias plataformas, o valor
        plataforma detectada terá presidência.
        """
        if not self.fall:
            now_moving = self.on_moving
            any_moving, any_non_moving = [], []
            for collide in self.collide_below:
                if collide.type == "moving":
                    self.on_moving = collide
                    any_moving.append(collide)
                else:
                    any_non_moving.append(collide)
            if not any_moving:
                self.on_moving = False
            elif any_non_moving or now_moving in any_moving:
                self.on_moving = now_moving

    def check_collisions(self, offset, index, obstacles):
        """
        Esta função verifica se uma colisão ocorrerá após o deslocamento de deslocamento
        píxeis. Se uma colisão for detectada, a posição será decrementada em um
        pixel e testado novamente. Isso continua até encontrarmos exatamente até onde podemos
        mover com segurança, ou decidimos que não podemos nos mover.
        """
        unaltered = True
        self.rect[index] += offset[index]
        while pg.sprite.spritecollideany(self, obstacles):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_above(self, obstacles):
        """Ao pular, não entre no estado de queda se não houver espaço para pular."""
        self.rect.move_ip(0, -1)
        collide = pg.sprite.spritecollideany(self, obstacles)
        self.rect.move_ip(0, 1)
        return collide

    def check_below(self, obstacles):
        """Verifique se o jogador está em contato com o chão."""
        self.rect.move_ip((0,1))
        collide = pg.sprite.spritecollide(self, obstacles, False)
        self.rect.move_ip((0,-1))
        return collide

    def jump(self, obstacles):
        """Chamado quando o usuário pressiona o botão de salto."""
        if not self.fall and not self.check_above(obstacles):
            self.velocity[1] = self.jump_power
            self.fall = True
            self.on_moving = False

    def jump_cut(self):
        """Chamado se o jogador soltar a tecla de salto antes da altura máxima."""
        if self.fall:
            if self.velocity[1] < self.jump_cut_magnitude:
                self.velocity[1] = self.jump_cut_magnitude

    def pre_update(self, obstacles):
        """Executado antes da atualização das plataformas."""
        self.frame_start_pos = self.rect.topleft
        self.collide_below = self.check_below(obstacles)
        self.check_moving(obstacles)

    def update(self, obstacles, keys):
        """Tudo o que precisamos para ficar atualizado; correu após a atualização das plataformas."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()
        start = self.frame_start_pos
        end = self.rect.topleft
        self.total_displacement = (end[0]-start[0], end[1]-start[1])

    def draw(self, surface):
        """Blit o jogador na superfície alvo."""
        surface.blit(self.image, self.rect)


class Block(pg.sprite.Sprite):
    """A class representing solid obstacles."""
    def __init__(self, color, rect):
        """Uma classe representando obstáculos sólidos."""
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"


class MovingBlock(Block):
    """Uma classe para representar blocos em movimento horizontal e vertical."""
    def __init__(self, color, rect, end, axis, delay=500, speed=2, start=None):
        """
       O bloco móvel irá se mover na direção do eixo (0 ou 1)
        entre rect.topleft e end. O argumento de atraso é a quantidade de tempo
        (em milissegundos) para pausar ao atingir um ponto final; velocidade é a
        velocidade das plataformas em pixels / quadro; se o início especificado for o local
        dentro do caminho dos blocos para iniciar (o padrão é rect.topleft).
        """
        Block.__init__(self, color, rect)
        self.start = self.rect[axis]
        if start:
            self.rect[axis] = start
        self.axis = axis
        self.end = end
        self.timer = 0.0
        self.delay = delay
        self.speed = speed
        self.waiting = False
        self.type = "moving"

    def update(self, player, obstacles):
        """Atualizar posição. Isso deve ser feito antes de mover qualquer ator."""
        obstacles = obstacles.copy()
        obstacles.remove(self)
        now = pg.time.get_ticks()
        if not self.waiting:
            speed = self.speed
            start_passed = self.start >= self.rect[self.axis]+speed
            end_passed = self.end <= self.rect[self.axis]+speed
            if start_passed or end_passed:
                if start_passed:
                    speed = self.start-self.rect[self.axis]
                else:
                    speed = self.end-self.rect[self.axis]
                self.change_direction(now)
            self.rect[self.axis] += speed
            self.move_player(now, player, obstacles, speed)
        elif now-self.timer > self.delay:
            self.waiting = False

    def move_player(self, now, player, obstacles, speed):
        """
        Move o jogador quando está em cima ou sobre a plataforma.
        Verificações de colisão estão em vigor para impedir que o bloco empurre o jogador
        através de uma parede.
        """
        if player.on_moving is self or pg.sprite.collide_rect(self,player):
            axis = self.axis
            offset = (speed, speed)
            player.check_collisions(offset, axis, obstacles)
            if pg.sprite.collide_rect(self, player):
                if self.speed > 0:
                    self.rect[axis] = player.rect[axis]-self.rect.size[axis]
                else:
                    self.rect[axis] = player.rect[axis]+player.rect.size[axis]
                self.change_direction(now)

    def change_direction(self, now):
        """Chamado quando a plataforma atinge um ponto de extremidade ou não tem mais espaço."""
        self.waiting = True
        self.timer = now
        self.speed *= -1


class Control(object):
    """Classe para gerenciar loop de eventos e estados de jogos."""
    def __init__(self):
        """Inicialize a tela e prepare os objetos do jogo."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,875), 4)
        self.level = pg.Surface((1000,1000)).convert()
        self.level_rect = self.level.get_rect()
        self.viewport = self.screen.get_rect(bottom=self.level_rect.bottom)
        self.win_text,self.win_rect = self.make_text()
        self.obstacles = self.make_obstacles()

    def make_text(self):
        """Renderiza um objeto de texto. O texto é renderizado apenas uma vez."""
        font = pg.font.Font(None, 50)
        message = "Vagabundo vai estuda para de joga"
        text = font.render(message, True, (100,100,175))
        rect = text.get_rect(centerx=self.level_rect.centerx, y=100)
        return text, rect

    def make_obstacles(self):
        """Adiciona alguns obstáculos arbitrariamente colocados a um sprite.."""
        walls = [Block(pg.Color("magenta"), (0,980,1000,20)),
                 Block(pg.Color("magenta"), (0,0,20,1000)),
                 Block(pg.Color("magenta"), (980,0,20,1000))]
        static = [Block(pg.Color("violet"), (250,780,200,100)),
                  Block(pg.Color("violet"), (600,880,200,100)),
                  Block(pg.Color("violet"), (20,360,880,40)),
                  Block(pg.Color("violet"), (950,400,30,20)),
                  Block(pg.Color("violet"), (20,630,50,20)),
                  Block(pg.Color("violet"), (80,530,50,20)),
                  Block(pg.Color("violet"), (130,470,200,215)),
                  Block(pg.Color("violet"), (20,760,30,20)),
                  Block(pg.Color("violet"), (400,740,30,40))]
        moving = [MovingBlock(pg.Color("yellow"), (20,740,75,20), 325, 0),
                  MovingBlock(pg.Color("yellow"), (600,500,100,20), 880, 0),
                  MovingBlock(pg.Color("yellow"),
                              (420,430,100,20), 550, 1, speed=3, delay=200),
                  MovingBlock(pg.Color("yellow"),
                              (450,700,50,20), 930, 1, start=930),
                  MovingBlock(pg.Color("yellow"),
                              (500,700,50,20), 730, 0, start=730),
                  MovingBlock(pg.Color("yellow"),
                              (780,700,50,20), 895, 0, speed=-1)]
        return pg.sprite.Group(walls, static, moving)

    def update_viewport(self, speed):
        """
        Viewport permitindo velocidade de rolagem variável com base na localização do jogador
        na tela. Aqui a rolagem começa quando o jogador cruza 1/3 da
        a tela. A rolagem começa na metade da velocidade do jogador, mas uma vez
        o jogador atinge a metade do caminho, a rolagem corresponde à sua
        Rapidez.
        """
        for i in (0,1):
            first_third = self.viewport[i]+self.viewport.size[i]//3
            second_third = first_third+self.viewport.size[i]//3
            player_center = self.player.rect.center[i]
            mult = 0
            if speed[i] > 0 and player_center >= first_third:
                mult = 0.5 if player_center < self.viewport.center[i] else 1
            elif speed[i] < 0 and player_center <= second_third:
                mult = 0.5 if player_center > self.viewport.center[i] else 1
            self.viewport[i] += mult*speed[i]
        self.viewport.clamp_ip(self.level_rect)

    def event_loop(self):
        """Sempre podemos sair, e o jogador às vezes pode pular."""
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump(self.obstacles)
            elif event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def update(self):
        """Atualize o player, obstáculos e janela de exibição atual."""
        self.keys = pg.key.get_pressed()
        self.player.pre_update(self.obstacles)
        self.obstacles.update(self.player, self.obstacles)
        self.player.update(self.obstacles, self.keys)
        self.update_viewport(self.player.total_displacement)

    def draw(self):
        """
        Desenhe todos os objetos necessários para a superfície nivelada e, em seguida, desenhe
        a seção viewport do nível para a superfície da tela.
        """
        self.level.fill(pg.Color("lightblue"), self.viewport)
        self.obstacles.draw(self.level)
        self.level.blit(self.win_text, self.win_rect)
        self.player.draw(self.level)
        self.screen.blit(self.level, (0,0), self.viewport)

    def display_fps(self):
        """Mostre os programas FPS no identificador da janela."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)

    def main_loop(self):
        """Tão simples quanto possível."""
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()