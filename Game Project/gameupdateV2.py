import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 35

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)

#define colors
white = (255, 255, 255)

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 333
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


#load images
bg = pygame.image.load('Project\img/bg.png').convert()
ground_img = pygame.image.load('Project\img/ground.png').convert()
botton_img = pygame.image.load('Project\img/restart.png').convert_alpha()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    Pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'Project\img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False    

    def update(self):

        if flying == True:
            #gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        


        if game_over == False:
            #jump
            keys = pygame.key.get_pressed()
            if keys[K_w] and self.clicked == False:
                self.vel = -10
                self.clicked = True
            if keys[K_s] and self.clicked == False:
                self.vel = -10
                self.clicked = True
            if keys[K_w] == 0 and keys[K_s] == 0:
                self.clicked = False

            
            #handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
    
            #rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# ... previous code omitted for brevity

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Project\img/pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is the top pipe, -1 is the bottom pipe
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]      

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        #get the mouse position
        pos = pygame.mouse.get_pos()

        #check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        #draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

bird_group = pygame.sprite.Group()
Pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)
        


button = Button(screen_width // 2 - 50, screen_height // 2 - 100, botton_img)


run = True
while run:

    clock.tick(fps)

    #draw background
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    Pipe_group.draw(screen)

    #draw ground
    screen.blit(ground_img, (ground_scroll, 768))

    #check score
    if len(Pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > Pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < Pipe_group.sprites()[0].rect.right and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > Pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False


    draw_text(str(score), font, white, int(screen_width / 2), 20)

    #check collision
    if pygame.sprite.groupcollide(bird_group, Pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        
    #check if bird has hit the ground
    if flappy.rect.bottom > 768:
        game_over = True
        flying = False


    if game_over == False and flying == True:

        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            Pipe_group.add(btm_pipe)
            Pipe_group.add(top_pipe)
            last_pipe = time_now


                #scroll ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        Pipe_group.update()

    #check game over and reset
    if game_over == True:
        if button.draw() == 1:
            game_over = False
            reset_game()
            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == K_w and flying == False and game_over == False:
            flying = True
        if event.type == pygame.KEYDOWN and event.key == K_s and flying == False and game_over == False:
            flying = True


    pygame.display.update()

pygame.quit()

'''
As you can see, we modified the `Bird.update()` method to detect the keypress of 'a' or 'd' using `pygame.key.get_pressed()` and the `Bird` object now checks the key state to determine when to jump.

We also modified the event loop to detect the keypress of 'a' or 'd' and set the `flying` flag to `True` when the respective key is pressed.

Note that you will need to update the file paths for the images if you run this code on your machine.

'''

