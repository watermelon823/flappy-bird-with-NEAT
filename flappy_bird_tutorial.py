import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 250
WIN_HEIGHT = 400


BIRD_IMGS = [pygame.image.load(os.path.join("imgs", "bird1.png")),
            pygame.image.load(os.path.join("imgs", "bird2.png")),
            pygame.image.load(os.path.join("imgs", "bird3.png"))]
BIRD_RED = pygame.image.load(os.path.join("imgs", "bird_red.png "))
BIRD_RED = pygame.transform.scale(BIRD_RED, (45, 54))
PIPE_IMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs", "base.png"))
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))
STAT_FONT = pygame.font.SysFont("comiscans", 25)

class Bird:
    IMGS = BIRD_IMGS
    RED = BIRD_RED
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -8.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16

        if d <0:
            d -= 2

        self.y = self.y + d/2

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def draw_red(self, win):
        self.img = self.RED

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


    def oust(self):
        self.y = 10000

class Pipe:
    GAP = 130
    VEL = 2.5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(25, 225)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (int(self.x - bird.x), self.top - int(round(bird.y)))
        bottom_offset = (int(self.x - bird.x), self.bottom - int(round(bird.y)))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    birds[1].draw(win)
    birds[0].draw_red(win)
    pygame.display.update()


def main():
    bird1 = Bird(110, 175)
    bird2 = Bird(120, 175)
    birds= [bird1, bird2]
    base = Base(360)
    pipes = [Pipe(300)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        bird1.move()
        bird2.move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_SPACE:
                    if 0 < (bird1.y - bird2.y) < 12:
                        bird2.y -= 5
                    bird1.jump()
                if event.key == pygame.K_UP:
                    if 0 < (bird2.y - bird1.y) < 12:
                        bird1.y -= 5
                    bird2.jump()


        rem = []
        add_pipe = False
        for pipe in pipes:
            if pipe.collide(bird1):
                bird1.oust()

            if pipe.collide(bird2):
                bird2.oust()


            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and (pipe.x < bird1.x or pipe.x < bird2.x):
                pipe.passed = True
                add_pipe = True

            pipe.move()
        if add_pipe:
            score += 1
            pipes.append(Pipe(300))

        for r in rem:
            pipes.remove(r)

        # if bird.y +  bird.img.get_height() >= 360:
        #     pass

        if bird1.y > 1000 and bird2.y > 1000:
            break

        base.move()
        draw_window(win, birds, pipes, base, score)

    pygame.quit()
    quit()

main()


while True:
    bird.move()
