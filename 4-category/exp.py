###########################################################
# import modules
###########################################################

import os, sys
import copy
import math
import numpy as np
from random import random, randrange, choice, shuffle, seed, normalvariate
from scipy import stats, randn
import pygame
from pygame.locals import *
import tempfile
from time import sleep
from lib.pypsyexp import *
import datetime

execfile('stim_set.py')

###########################################################
# defines
###########################################################
experimentname = "Cat task"
experimentversion = '1.6'
laptop = False
black = (0, 0, 0)
darkgrey  = (25, 25, 25)
grey = (175,175,175)
white = (255, 255, 255)

LAPTOPRES = (1024,768)
FULLSCREENRES = (1024,768)



SINGLE = 0
DOUBLE = 1

# more colors
red = (255,0,0)
blue = (0,0,255)
yellow = (228, 241, 20)
green = (0, 255, 0)

pink = (255,120,255)  # 22 39 0 0 in CMYK
pastelgreen = (187,255,187) # 20 0 23 0 in CMYK

FOREGROUND = white
BACKGROUND = black

NEXT = 1
BACK = 0

num_dm_trials = 300


laptop = False

screenres = LAPTOPRES

#------------------------------------------------------------
# RewardButton
#------------------------------------------------------------
class RewardButton(object):
    def __init__(self, pos, myimage):
        
        self.xcoord = 400
        self.ycoord = 300
        self.moveto(pos)
        self.image = myimage
    
    def moveto(self,pos):
        self.rect = Rect(self.xcoord, self.ycoord, 200, 100)
    
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)

#------------------------------------------------------------
# MouseButton Classes (statelights, next, resp)
#------------------------------------------------------------
class StateButton(MouseButton):
    def __init__(self, x, y, w, h, myimage):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.image = myimage
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
    def do(self):
        print "Implemented in subclasses"

class NextButton(MouseButton):
    def __init__(self, x, y, w, h, myimage, snd, app):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.image = myimage
        self.snd = snd
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
    def do(self):
        self.snd.play()

class RespButton(MouseButton):
    def __init__(self, x, y, w, h, id, myimage, myimagepressed, snd, app):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.myid = id
        self.image = myimage
        self.imagep = myimagepressed
        self.snd = snd
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
    def do(self, surface):
        self.image_rect = self.imagep.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.imagep,self.image_rect)
        pygame.display.flip()
        self.snd.play()
        pygame.time.wait(100)
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
        pygame.display.flip()
        return self.myid

        
###########################################################
# CatDMExperiment Class
###########################################################
class CatDMExperiment(Experiment):
    def __init__(self, laptop, experimentname, experimentversion, suppress_pygame = False, special_patternfile = False):

        if laptop:
            screenres = LAPTOPRES
        else:
            screenres = FULLSCREENRES
            
        experimentname = "Cat task"
        
        Experiment.__init__(self, laptop, screenres, experimentname)
 
        #[self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode.txt')
        
        # condition is the surface features
        # 1 for lines; 2 for gabors
        print sys.argv
        
        self.cond = int(sys.argv[1])
        
        
        self.subj = int(sys.argv[2])
        self.session = int(sys.argv[3])

        print "I am subject %s in condition: %s" % (self.subj, str(self.cond))

        
        self.load_all_resources('images', 'sounds') ## this is from lib
         
        self.filename = "data/%s-%s.dat" % (self.subj, self.session)
        self.datafile = open(self.filename, 'w')
        
        self.break_every = 50
        
        # this sets up the basics for all the gabors--width, height and gaussian blur
        grid_w = grid_h = 100
        windowsd = 20
        self.setup_gabor(grid_w, grid_h, windowsd)
        
        
        

        
        # sets up the list of test items ( the freqs and orientations for the gabors)
        # also determines which category and group each one is in
        
        freq_index = 0
        orient_index = 0
        
        
        # sets up the stimuli
        self.stimuli = stim_set
        
        self.trial = 1
        


    #------------------------------------------------------------
    # show_instructions
    #------------------------------------------------------------
    def show_instructions(self, filename, butfn, butfn2):
        background = self.show_centered_image(filename, black)
        self.screen.blit(background, (0,0))
        self.button = NextButton(640, 725, 265, 50, self.resources[butfn],self.resources["buttonpress.wav"], self)
        self.button.draw(self.screen)
        if butfn2 != None:
            self.button2 = NextButton(140, 725, 265, 50, self.resources[butfn2],self.resources["buttonpress.wav"], self)
            self.button2.draw(self.screen)
        pygame.display.flip()
        
        time_stamp = pygame.time.get_ticks()
        
        retval = NEXT
        exit = False;
        while not exit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.on_exit()
                elif event.type == MOUSEBUTTONDOWN:
                    #print("here")
                    (x,y) = pygame.mouse.get_pos()
                    if (self.button.containsPoint(x, y)):
                        self.button.do()
                        exit = True
                        retval = NEXT
                    if butfn2 != None:
                        if (self.button2.containsPoint(x, y)):
                            self.button2.do()
                            exit = True
                            retval = BACK
        rt = pygame.time.get_ticks() - time_stamp
        return retval
        

    #------------------------------------------------------------
    # get_click_response_and_rt
    #------------------------------------------------------------

    
    def get_click_response_and_rt(self):
    
        time_stamp = pygame.time.get_ticks()
        exit = False;
        while not exit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_exit()
                elif event.type == KEYDOWN:
                    if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                        self.on_exit()
                        
                    elif( pygame.key.get_pressed()[K_1]):
                        res = 1 
                        exit = True # 
                    elif( pygame.key.get_pressed()[K_2]):
                        res = 2 
                        exit = True # 
                    elif( pygame.key.get_pressed()[K_3]):
                        res = 3 
                        exit = True # 
                    elif( pygame.key.get_pressed()[K_4]):
                        res = 4 
                        exit = True # 
        
        
        rt = pygame.time.get_ticks() - time_stamp
        return [res, rt]
        
    #------------------------------------------------------------
    # show_break
    #------------------------------------------------------------
    def show_break(self, filename, butfn, butfn2):
        background = self.show_centered_image(filename, black)
        self.screen.blit(background, (0,0))
        self.button = NextButton(640, 725, 265, 50, self.resources[butfn],self.resources["buttonpress.wav"], self)
        self.button.draw(self.screen)
        if butfn2 != None:
            self.button2 = NextButton(140, 725, 265, 50, self.resources[butfn2],self.resources["buttonpress.wav"], self)
            self.button2.draw(self.screen)
        pygame.display.flip()
        
        time_stamp = pygame.time.get_ticks()
        
        retval = NEXT
        exit = False;
        while not exit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.on_exit()
                elif event.type == MOUSEBUTTONDOWN:
                    #print("here")
                    (x,y) = pygame.mouse.get_pos()
                    if (self.button.containsPoint(x, y)):
                        self.button.do()
                        exit = True
                        retval = NEXT
                    if butfn2 != None:
                        if (self.button2.containsPoint(x, y)):
                            self.button2.do()
                            exit = True
                            retval = BACK
        rt = pygame.time.get_ticks() - time_stamp
        return retval
    
    
    def show_game_feedback(self):
        background = self.show_centered_image


    #------------------------------------------------------------
    # show_thanks
    #------------------------------------------------------------
    def show_thanks(self):        
        background = self.show_centered_image('thanks.gif',white)

        subj_text = "SUBJECT NUMBER: %s" % self.subj
        self.place_text_image(background, subj_text, 32, 0, 250, black, white)
        
        #self.earnings = 1.00
        #entry_text = "YOU HAVE WON: $ %.2f" % int(self.earnings)
        self.output_trial([(datetime.datetime.now().ctime())])
           
        print 'here'
        #self.place_text_image(background, entry_text, 32, 0, -80, black, white)
        self.update_display(background)
        
        self.escapable_sleep(10000)
        self.on_exit()

        while 1:
            [res, rescode, rt] = self.get_response()
        raise SystemExit
        
    
    ###########################################################
    # do_category_trial
    ###########################################################
    def do_category_trial(self, stimulus):
    
        # give breaks
        if self.trial%self.break_every == 1 and self.trial != 1: # do a break every 50 trials
            self.show_break('break.png', 'next.gif', None)
        
        # 
        background = self.clear_screen(black)
        
        # draws the gabor
        if self.cond == 2:
            gabor_surface = self.draw_gabor( stimulus[1], stimulus[2]-60, 3) # the 3 is scaling factor
            gabor_rect = gabor_surface.get_rect()
            gabor_rect.center = background.get_rect().center
            background.blit( gabor_surface, gabor_rect )
        
        # draws a line
        #pygame.draw.rect(background, self.stage1color, pygame.Rect(120, 200, 300, 200))
        elif self.cond == 1:
            stimTheta = stimulus[2] * pi / 180 - 45
            stimLength = stimulus[1]

            # line end points
            X1 = background.get_rect().centerx + (.5 * stimLength * cos(stimTheta))
            Y1 = background.get_rect().centery + (.5 * stimLength * sin(stimTheta))
            X2 = background.get_rect().centerx - (.5 * stimLength * cos(stimTheta))
            Y2 = background.get_rect().centery - (.5 * stimLength * sin(stimTheta))
        
            pygame.draw.line(background, white, (X1, Y1), (X2, Y2), 2)
        
        category = stimulus[0]
        
        trial_text = "Which category (1, 2, 3, or 4)?"
        self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)


        self.update_display(background)
        
        [res, rt] = self.get_click_response_and_rt()
        
        background = self.clear_screen(black)
        trial_text = "Which category (1, 2, 3, or 4)?"
        self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)
        
        
        background = self.clear_screen(black)

        # COMPUTE ACCURACY, DISPLAY FEEDBACK
        if res == category:
           hit = 1
           self.place_text_image(background, 'Correct!', 48, 0, 0, FOREGROUND, BACKGROUND)
        else: 
           hit = 0
           self.place_text_image(background, 'Incorrect.', 48, 0, 0, FOREGROUND, BACKGROUND)
        
        
        self.update_display(background)
        
        # adjust ITI perhaps
        sleep(0.5)
                
        background = self.clear_screen(black)
        self.update_display(background)
        
        sleep(0.25)
        
        
        
        # LIST OF THINGS TO OUTPUT ON EACH TRIAL # adjust this
        self.output_trial([self.subj, self.cond, self.session,
                           self.trial, res, rt, hit,
                           stimulus[0], stimulus[1], stimulus[2]-60]) 

        self.trial += 1



    
    ###########################################################
    # do_experiment
    ###########################################################
    def do_experiment(self):
    
    
        background = self.clear_screen(black)
        pygame.mouse.set_visible(1)          
        stage = 1
        

        while(stage!=3):
            if stage == 1:
               if (self.show_instructions('task-instrux1.png',  'next.gif', 'back.gif')==BACK):
                    stage = 1
               else:
                    stage = 2
            elif stage == 2:
                if self.show_instructions('task-instrux2.png',  'next.gif', 'back.gif')==BACK:
                    stage = 1
                else:
                    stage = 3

        
        # THEN DO THE CATEGORIZATION BLOCK
 
        stage = 1
        #print 'DM task done'
        # similarity task instructions
        while(stage!=2):
            if stage == 1:
                if (self.show_instructions('cat-instrux1.png',  'next.gif', 'back.gif')==BACK):
                    stage = 1
                else:
                    stage = 2    
        
        shuffle(self.stimuli)
        for item in self.stimuli:
            self.do_category_trial(item)
                    
                
        
        self.show_thanks()
        


#-----------------------
# main                   
#------------------------
def main():
    global laptop, screenres, experimentname;
    experiment = CatDMExperiment(laptop, screenres, experimentname)
    experiment.do_experiment()
    #experiment.print_test_items()


###########################################################
# let's start
###########################################################

if __name__ == '__main__':
    main()

