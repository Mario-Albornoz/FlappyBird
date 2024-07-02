#flappy bird main
import pygame
from pygame.locals import *
import random
import sys
import os



pygame.init()

clock = pygame.time.Clock()
fps = 60

#Screen set up
screen_width = 704
screen_height = 756

screen = pygame.display.set_mode((screen_width , screen_height))
surface = pygame.Surface((screen_width,screen_height), pygame.SRCALPHA)
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('ptmono', 60)

fontformessage = pygame.font.SysFont('ptmono', 30)
fontforgameover = pygame.font.SysFont('ptmono', 50)
fontpause = pygame.font.SysFont('ptmono',20)
outlinefontpause = pygame.font.SysFont('ptmono',20)
#define color
white = (255,255,255)
black = (0, 0, 0)
#define text functions
text_visible = True
text_timer = pygame.time.get_ticks()  # Initialize the timer

#define game variables 
ground_scroll = 0
scroll_speed = 3
flying = False
game_over = False
game_paused = False
pipe_gap = 163
pipe_frequency = 1750 #miliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
pass_pipe = False
score = 0
menu = False
hardcore = False
default_char = 'red'
birdselection = default_char

#variables for highscore feature
newhighscore = False
highscore = 0 

#load images
bg = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/bg.png')
ground_img = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/ground.png')
button_img = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/restart.png')
bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}{birdselection}.png') for num in range(1, 4)]
menu_img = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/CharacterMenu.png')


#high score read and update function 

def read_highscore():
    try:
        with open('highscore.txt',"r") as file:
            highscoreLine = file.readline().strip()
            #print(highscoreLine)
            highscore = int(highscoreLine)
    except ValueError:
        print("Invalid data in highscore file. Setting highscore to 0.")
        highscore = 0
    return highscore
    

def update_highscore(current_score):
    global newhighscore
    highscore = read_highscore()
    if current_score > highscore:
        newhighscore = True
        with open("highscore.txt","w") as file:
            file.write(str(current_score))
        print('now highscore')
        return True
    return False

#score function
def draw_text(text, font, text_color, x, y):
    img = font.render(text,True,text_color)
    screen.blit(img,(x,y))

def draw_message(text,font, text_color, x, y):
    img = font.render(text,True,text_color)
    screen.blit(img,(x,y))

# Reset function
def reset_game():
    global score
    update_highscore(score)
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height/2)
    score = 0
    
    return score

# Pause function (menu)

def draw_pause():
    pygame.draw.rect(surface, (0,0,0,150), [0,0,screen_width,screen_height])
    # use this line below to insert pause image 
    #pygame.draw.rect(surface, 'dark gray', [(screen_width//4) + 6,screen_height//3,screen_width//2,screen_height//8],0,10)
    screen.blit(surface, (0,0))
    

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = bird_images
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def die(self):
        self.kill()
    
    def update(self):
        if game_over == False or game_over == True:
            if flying == True and game_paused == False:
                #Gravity
                self.vel += 0.4
                if self.vel > 8:
                    self.vel = 8
                if self.rect.bottom < 696:
                    self.rect.y += int(self.vel)
        
    

        if game_over == False and not game_paused:
            #jump 
            if pygame.key.get_pressed()[pygame.K_UP] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -9.5
            
            if pygame.key.get_pressed()[pygame.K_UP] == 0:
                self.clicked = False

            #if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                #self.clicked = True 
                #self.vel = -9.5   

            #if pygame.mouse.get_pressed()[0] == 0:
                #self.clicked = False

            #handle animation
            self.counter += 1
            flap_cooldown = 6

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            #rotate bird
            if flying == True:
                self.image = pygame.transform.rotate(self.images[self.index], self.vel*-2.5)
        else:
            if not game_paused: 
                self.image = pygame.transform.rotate(self.images[self.index], self.vel-80)


#class pipes
class Pipe(pygame.sprite.Sprite):
    def __init__(self,x,y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is the top and -1 is the bottom
        if position == 1:
            #flip image the function takes as input the intance the x and y axis
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x,y - int(pipe_gap/2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap/2)]
    
#update pipes
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image, is_visible: bool):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.is_visible = is_visible
        self.visible = True  # Added
        self.blink_timer = pygame.time.get_ticks()  # Added

    def draw(self):
        
        if self.is_visible == False and pygame.time.get_ticks() - self.blink_timer > 380:
            self.blink_timer = pygame.time.get_ticks()
            self.visible = not self.visible  # Toggle visibility

        if self.visible:
            screen.blit(self.image, (self.rect.x, self.rect.y))    
        
        # Blink every 500 milliseconds
        

        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()

        # check if mouse over button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        return action
    
# Extra mode

def game_logic_hardcore():
    global ground_scroll
    global score
    global game_over
    global flying
    global last_pipe
    global pass_pipe
    global pipe_frequency
    global scroll_speed
    current_highscore = read_highscore()
    
	#Check if in homescreen and display button
 
     
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
        and pass_pipe is False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, black, ((screen_width//2) - 18), 41)            
    draw_text(str(score), font, white, ((screen_width//2) - 20), 40)

    #look for collission
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        
    # Check if bird hit ground
    if flappy.rect.bottom >= 695:
        game_over = True
        flying = False

   
    #generate pipes
    if game_over == False and flying == True and not game_paused:
        draw_text('Press SPACE to pause', fontpause, black, (screen_width//3 - 2),727)
        draw_text('Press SPACE to pause', fontpause, white, (screen_width//3),725)
        time_now = pygame.time.get_ticks()
        pipe_height = random.randint(-100,100)

        # Variable changes for the hardcore mode and making the mode harder

        pipe_frequency = 800
        scroll_speed = 7
        if flappy.clicked == True:
            flappy.vel = -9

        if time_now - last_pipe > pipe_frequency:
            btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            # print(time_now)
            last_pipe = time_now
            #if score > counter + 2:
                #pipe_frequency = pipe_frequency - 50
                #counter =+ 2
    #Scroll gorund during the game    
        ground_scroll -= scroll_speed
        if abs((ground_scroll)) > 35:
            ground_scroll = 0

        pipe_group.update()
    
    #check for game_over and reset
    if game_over == True:
        if score > current_highscore:
            draw_text('NEW HIGHSCORE!!!',fontpause,black,((screen_width//2)-99)+2, screen_height//2 - 91)
            draw_text('NEW HIGHSCORE!!!',fontpause,white,((screen_width//2)-100)+2, screen_height//2 - 90)
        #    update_highscore(score)
        if button.draw() == True:
            update_highscore(score)
            game_over = False
            score = reset_game()
            scroll_speed = 3
            pipe_frequency = 1750

    if game_paused:
        draw_pause()
    

# Create button for hardcore mode and for normal mode 
hardcoreMode = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/HardcoreMode.png')
normalMode = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/RegularMode.png')

hardcoreMode_button = Button(screen_width//2 - 60, screen_height//2 - 175, hardcoreMode, True)
normalMode_button = Button(screen_width//2 - 60, screen_height//2 - 125, normalMode, True)

def home_screen_and_game():
    global ground_scroll
    global scroll_speed
    global text_timer
    global text_visible
    global menu
    global hardcore

   
    highscore = read_highscore()

    clock.tick(fps)
    screen.blit(bg, (0,0))
    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()
    screen.blit(ground_img, (ground_scroll,695))
    #check for highscore and update highscore
    #   update_highscore(score)
    
    
     

    if game_over == False and flying == False and not game_paused:
        draw_text(f'Highscore : {highscore}',fontpause,black, 11 , screen_height//2 - 374) 
        draw_text(f'Highscore : {highscore}',fontpause,white, 10 , screen_height//2 - 375) 
        #draw_text('PRESS any KEY to start the game', fontpause, white, (screen_width//4 + 10), screen_height//2 + 225)
    #Display start message blinking every 500 milliseconds
        if pygame.time.get_ticks() - text_timer > 450:
            text_timer = pygame.time.get_ticks()
            text_visible = not text_visible  # Toggle visibility
        if text_visible:
            draw_text('PRESS any KEY to start the game', outlinefontpause, black, (screen_width//4 + 6), screen_height//2 + 291)
            draw_text('PRESS any KEY to start the game', fontpause, white, (screen_width//4 + 5), screen_height//2 + 290)
            
    #Display message stating the mode the game is in 
        if hardcore == True:
            draw_text('Mode: Hardcore',fontformessage, black, (screen_width//2 - 91), screen_height//2 - 223)
            draw_text('Mode: Hardcore',fontformessage, white, (screen_width//2 - 93), screen_height//2 - 225)
        else:
            draw_text('Mode: Regular',fontformessage, black, (screen_width//2 - 91), screen_height//2 - 223)
            draw_text('Mode: Regular',fontformessage, white, (screen_width//2 - 93), screen_height//2 - 225)
    #scroll ground duing homescreen
        ground_scroll -= scroll_speed
        if abs((ground_scroll)) > 35:
            ground_scroll = 0
            
        if char_selection_button.draw() == True:
            menu = True
            
        if menu:
            character_selection()
    # Create option for different mode
        if hardcoreMode_button.draw() == True:
            hardcore = True

        if normalMode_button.draw()== True:
            hardcore = False


#create pipe and bird group     
pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height/2))

bird_group.add(flappy)

#create restart button
button = Button(screen_width//2 - 60, screen_height//2 - 30, button_img, False)        
            
#Load Character images for menu Selection and back button
ice = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird1ice.png')
coin = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird1coin.png')
benito =pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird2benito.png')
purple = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird1purple.png')
darkpurple = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird1darkpurple.png')
red = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird1red.png')
back = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/backMenu.png')
taylor = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test1.png')
debut = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test1.png')
fearles = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test7.png')
speaknow = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test11.png')
taylorred = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test15.png')
taylor1989 = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test19.png')
reputation = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test23.png')
lover = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test29.png')
folklore = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test31.png')
evermore = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test35.png')
midnights = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test40.png')
ttpd = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test44.png')
tpd = pygame.image.load('/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird1taylor.png')
#size taylor character 

#Create character selection button 
char_selection_button = Button(screen_width//2 - 60, screen_height//2 - 75, menu_img, True)
char_red = Button(screen_width//2 - 275, screen_height//2 + 60, red, True)
char_ice = Button(screen_width//2 - 175, screen_height//2 + 60, ice, True)
char_benito = Button(screen_width//2 - 75, screen_height//2 + 55, benito, True)
char_coin = Button(screen_width//2  + 40, screen_height//2 + 60, coin, True)
char_purple = Button(screen_width//2 + 150, screen_height//2 + 60, purple, True)
char_darkpurple = Button(screen_width//2 + 250, screen_height//2 + 60, darkpurple, True)
backMenu = Button(screen_width//2 - 60, screen_height//2 - 20, back, True)
char_taylor = Button(screen_width//2 + 245, screen_height//2 + 200, taylor, True)
char_tpd = Button(screen_width//2 - 175, screen_height//2 + 60, tpd, True)

char_debut = Button(screen_width//2 - 293, screen_height//2 + 110,debut , True)
char_fearless = Button(screen_width//2 - 195, screen_height//2 + 110,fearles , True)
char_speaknow = Button(screen_width//2 - 83, screen_height//2 + 110,speaknow , True)
char_redtaylor = Button(screen_width//2 + 32 , screen_height//2 + 110,taylorred , True)
char_1989 = Button(screen_width//2 + 142 , screen_height//2 + 110,taylor1989 , True)
char_reputation = Button(screen_width//2 + 242, screen_height//2 + 110,reputation , True)
char_lover = Button(screen_width//2 - 293, screen_height//2 + 200,lover , True)
char_folklore =  Button(screen_width//2 - 193, screen_height//2 + 200,folklore , True)
char_evermore = Button(screen_width//2 - 93, screen_height//2 + 200,evermore , True)
char_midnights = Button(screen_width//2 + 27, screen_height //2 + 200,midnights, True)
char_ttpd =  Button(screen_width//2 + 137, screen_height//2 + 200,ttpd , True)

#Character Selection Function


def character_selection():
    global birdselection
    global menu
    global flappy
    global bird_images
    global pipe_gap
    

    if backMenu.draw()== True:
        menu = False
    if char_red.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}red.png') for num in range(1, 4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 163
        
    #if char_ice.draw() == True:
    #    bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}ice.png') for num in range(1, 4)]
    #    bird_group.remove(flappy)
    #    flappy = Bird(100,int(screen_height)/2)
    #    bird_group.add(flappy)
    #    pipe_gap = 163

    if char_benito.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}benito.png') for num in range(1, 4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 163
        
    if char_coin.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}coin.png') for num in range(1, 4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 163
        
    if char_purple.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}purple.png') for num in range(1, 4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 163
        
    if char_darkpurple.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}darkpurple.png') for num in range(1, 4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 163
    
    if char_taylor.draw()== True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(1,47)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap  = 203



    if char_tpd.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/bird{num}taylor.png') for num in range(1,4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 163
    
    if char_debut.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(1,4)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 203

    if char_fearless.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(7,11)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 203

    if char_speaknow.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(11,15)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 203

    if char_redtaylor.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(15,19)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 203

    if char_1989.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(19,23)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 203

    if char_reputation.draw() == True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(23,27)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap = 203

    if char_lover.draw()== True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(27,31)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap  = 203
    
    if char_folklore.draw()== True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(31,35)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap  = 203
    
    if char_evermore.draw()== True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(35,39)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap  = 203
    
    if char_midnights.draw()== True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(39,43)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap  = 203
    
    if char_ttpd.draw()== True:
        bird_images = [pygame.image.load(f'/Users/marioandresalbornoz/Desktop/CS/FlappyBird/flappy_images/Birds(png)/test{num}.png') for num in range(43,47)]
        bird_group.remove(flappy)
        flappy = Bird(100,int(screen_height)/2)
        bird_group.add(flappy)
        pipe_gap  = 203
        

def game_logic():
    global ground_scroll
    global score
    global game_over
    global flying
    global last_pipe
    global pass_pipe
    global pipe_frequency
    global scroll_speed
    current_highscore = read_highscore()

    scroll_speed = 3
    pipe_frequency = 1750
    
    #update_highscore(score)
	#Check if in homescreen and display button
 
        
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
        and pass_pipe is False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, black, ((screen_width//2) - 18), 41)  
    draw_text(str(score), font, white, ((screen_width//2) - 20), 40)

    #look for collission
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        
    # Check if bird hit ground
    if flappy.rect.bottom >= 695:
        game_over = True
        flying = False

   
    #generate pipes
    if game_over == False and flying == True and not game_paused:
        draw_text('Press SPACE to pause', fontpause, black, (screen_width//3 - 1),726)
        draw_text('Press SPACE to pause', fontpause, white, (screen_width//3),725)
        time_now = pygame.time.get_ticks()
        pipe_height = random.randint(-100,100)

        if time_now - last_pipe > pipe_frequency:
            btm_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            # print(time_now)
            last_pipe = time_now

    #Scroll gorund during the game    
        ground_scroll -= scroll_speed
        if abs((ground_scroll)) > 35:
            ground_scroll = 0

        pipe_group.update()
    
    #check for game_over and reset
    if game_over == True:
        if score > current_highscore:
            draw_text('NEW HIGHSCORE!!!',fontpause,black,((screen_width//2)-99)+2, screen_height//2 - 91)
            draw_text('NEW HIGHSCORE!!!',fontpause,white,((screen_width//2)-100)+2, screen_height//2 - 90)
        #    update_highscore(score)
        if button.draw() == True:
            game_over = False
            score = reset_game()

    if game_paused:
        draw_pause()







#Run game loop
run = True
while run:
    
    home_screen_and_game()
    if hardcore == True:
        game_logic_hardcore()
    if hardcore == False:
        game_logic()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
			# Start the game by pressing SPACE when not flying and not game over
            if pygame.key.get_pressed() and not flying and not game_over:
                flying = True
                game_paused = False	
			# Toggle pause mode by pressing SPACE when flying and not game over
            elif event.key == pygame.K_SPACE and flying and not game_over:
                game_paused = not game_paused
        #if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over and not menu:
            #if char_selection_button.draw() == False:
                #flying = True
                #game_paused = False
        # Inside your game loop or update function
            



    pygame.display.update()
pygame.quit()