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

execfile('pairings.py')
execfile('transfer_set.py')

###########################################################
# defines
###########################################################
experimentname = "Cat-DM task"
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

# Stimulus numbers.
num_dims = 2                # Number of stimulus parameters.
num_stims = 10**num_dims     # Number of possible stimuli


# Pattern file

# payoff structure
high_payoff = 60   # mean reward for higher payoff option
low_payoff = 40    # mean reward for lower payoff option
noise_level = 15  #sd of the random normal distribution rewards are drawn from

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
            
        experimentname = "Cat-DM task"
        
        Experiment.__init__(self, laptop, screenres, experimentname)
 
        #[self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode.txt')
        self.cond = int(sys.argv[1])
        self.subj = int(sys.argv[2])

        print "I am subject %s in condition: %s" % (self.subj, str(self.cond))

        
        self.load_all_resources('images', 'sounds') ## this is from lib
         
        self.filename = "data/%s.dat" % self.subj
        self.datafile = open(self.filename, 'w')
        
        self.break_every = 50
        
        # this sets up the basics for all the gabors--width, height and gaussian blur
        grid_w = grid_h = 100
        windowsd = 20
        self.setup_gabor(grid_w, grid_h, windowsd)
        
        self.rot_offset = randint(-80, 80 )
        self.freq_offset = randint(-30, 30)
        
        self.output_trial([self.freq_offset, self.rot_offset])
        
        #basic options
        # ADD SOME STUFF HERE
        if self.subj%4 < 2:
            self.cat_dim = 0
        else:
            self.cat_dim = 1
                        
            
        # set which group gives higher rewards
        if self.subj%8 < 4:
            self.high_group = 0
            self.low_group = 1
        else:
            self.high_group = 1
            self.low_group = 0
            
        self.low_payoff = 40
        self.high_payoff = 60
            
        self.total_points = 0
        
        # sets up the list of test items ( the freqs and orientations for the gabors)
        # also determines which category and group each one is in
        
        freq_index = 0
        orient_index = 0
        
        self.test_items = []
        for freq in xrange(70+self.freq_offset, 180+self.freq_offset, 11):
            freq_index += 1
            orient_index = 0
            for orient in xrange( -40+self.rot_offset, 40+self.rot_offset, 8):
                orient_index += 1
                
                if [freq_index, orient_index][self.cat_dim] < 6:
                    cat = 0
                else:
                    cat = 1
                
                #[freq, orient] = self.getrealstim( [freq, orient])
                
                self.test_items.append( [freq, orient, cat, freq_index, orient_index] )
      
    #----------------------------------------------------  
    # getrealstim          
    #----------------------------------------------------
    def getrealstim(self, coords):
        # Scale is -35.35 to +35.35
        newr = round( newvals[0]*1.5 +50 )
        newtheta = round( newvals[1]*1.5 + 40 + self.rot_offset )
        return newr, newtheta

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
    def get_similarity_response_and_rt(self):
    
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
                    elif( pygame.key.get_pressed()[K_5]):
                        res = 5 
                        exit = True # 
                    elif( pygame.key.get_pressed()[K_6]):
                        res = 6 
                        exit = True # 
                    elif( pygame.key.get_pressed()[K_7]):
                        res = 7 
                        exit = True # 
        
        rt = pygame.time.get_ticks() - time_stamp
        return [res, rt]
    
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
                        
                    elif( pygame.key.get_pressed()[K_z]):
                        res = 0 # 'z' # CAT A
                        exit = True
                    elif( pygame.key.get_pressed()[K_SLASH]):
                        res = 1 # '/?' # CAT B
                        exit = True
        
        
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
        self.place_text_image(background, entry_text, 32, 0, -80, black, white)
        self.update_display(background)
        
        self.escapable_sleep(10000)
        self.on_exit()

        while 1:
            [res, rescode, rt] = self.get_response()
        raise SystemExit
        
    #------------------------------------------------------------
    # get_payoff
    #------------------------------------------------------------
    def get_payoff(self, stimulus_group):
        
        if stimulus_group == self.high_group:            
            payoff = self.high_payoff + int(normalvariate(0, noise_level))
        
        else:
            payoff = self.low_payoff + int(normalvariate(0, noise_level))
            
        return payoff


    
    ###########################################################
    # do_category_trial
    ###########################################################
    def do_category_trial(self, stimulus):
    
        # give breaks
        if self.trial%self.break_every == self.break_every-1: # do a break every 50 trials
            self.show_break('break.png', 'next.gif', None)
        
        # 
        background = self.clear_screen(black)
        
        # draws the gabor
        gabor_surface = self.draw_gabor( stimulus[0], stimulus[1], 3)
        gabor_rect = gabor_surface.get_rect()
        gabor_rect.center = background.get_rect().center
        background.blit( gabor_surface, gabor_rect )
        
        
        trial_text = "Group A or Group B?"
        self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)

        self.place_text_image(background, 'A', 144, -360, 250, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'B', 144, 360, 250, FOREGROUND, BACKGROUND)

        self.update_display(background)
        
        [res, rt] = self.get_click_response_and_rt()
        
        background = self.clear_screen(black)
        trial_text = "Group A or Group B?"
        self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)

        self.place_text_image(background, 'A', 144, -360, 250, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'B', 144, 360, 250, FOREGROUND, BACKGROUND)

        self.update_display(background)
        self.update_display(background)
        
        sleep(1.0)
        
        if res == stimulus[2]:
           hit = 1
        else: 
           hit = 0

        # SOMEWHERE IN HERE SHOULD BE ITI ETC
        sleep(1.0) # adjust ITI
        
        # LIST OF THINGS TO OUTPUT ON EACH TRIAL
        self.output_trial([self.subj, self.cond, self.cat_dim, self.high_group, 3,
                           self.trial, res, rt, hit,
                           stimulus[0], stimulus[1], stimulus[2], stimulus[3], stimulus[4],
                           'NA', 'NA', 'NA', 'NA', 'NA',
                           'NA', self.total_points, 'NA', 'NA']) 

        self.trial += 1


    ###########################################################
    # do_dm_trial
    ###########################################################
    def do_dm_trial(self, stimulus1, stimulus2):
    
        # give breaks
        if self.trial%self.break_every == self.break_every-1: # do a break every 50 trials
            self.show_break('break.png', 'next.gif', None)
        
        

        background = self.clear_screen(black)
        self.place_text_image(background, 'Goal: 16000', 30, 300, -345, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'Total points: %i' % self.total_points, 30, 300, -310, FOREGROUND, BACKGROUND)
        
        # draws the gabor
        # CHANGE THIS TO DRAW TWO GABORS
        gabor1_surface = self.draw_gabor( stimulus1[0], stimulus1[1], 3.0)
        gabor1_rect = gabor1_surface.get_rect()
        
        gabor2_surface = self.draw_gabor( stimulus2[0], stimulus2[1], 3.0)
        gabor2_rect = gabor2_surface.get_rect()
        

        
        gabor1_rect.center = (background.get_rect().center[0] - 300, background.get_rect().center[1])
        gabor2_rect.center = (background.get_rect().center[0] + 300, background.get_rect().center[1])
        
        background.blit( gabor1_surface, gabor1_rect )
        background.blit( gabor2_surface, gabor2_rect )
        
        
        trial_text = "CHOOSE ONE"
        self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)

        
        self.update_display(background)
        
        
        [res, rt] = self.get_click_response_and_rt()
        
        
        # use the reward group of the chosen stimulus to determine the reward
        payoff = self.get_payoff([stimulus1, stimulus2][res][2])
        #print payoff
        self.total_points += payoff
        
        background = self.clear_screen(black)
        self.place_text_image(background, 'Goal: 16000', 30, 300, -345, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'Total points: %i' % self.total_points, 30, 300, -310, FOREGROUND, BACKGROUND)
        self.update_display(background)
        
        self.place_text_image(background, '%s points' %payoff, 48, 0, 0, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'Goal: 16000', 30, 300, -345, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'Total points: %i' % self.total_points, 30, 300, -310, FOREGROUND, BACKGROUND)
        self.update_display(background)
        
        # adjust ITI perhaps
        sleep(1.0)
        
        if [stimulus1,stimulus2][res][2] == self.high_group:
           hit = 1
        else: 
           hit = 0
        
        background = self.clear_screen(black)
        self.place_text_image(background, 'Goal: 16000', 30, 300, -345, FOREGROUND, BACKGROUND)
        self.place_text_image(background, 'Total points: %i' % self.total_points, 30, 300, -310, FOREGROUND, BACKGROUND)
        self.update_display(background)
        
        sleep(1.0)
        
        # LIST OF THINGS TO OUTPUT ON EACH TRIAL
        self.output_trial([self.subj, self.cond, self.cat_dim, self.high_group, 1,
                           self.trial, res, rt, hit,
                           stimulus1[0], stimulus1[1], stimulus1[2], stimulus1[3], stimulus1[4],
                           stimulus2[0], stimulus2[1], stimulus2[2], stimulus2[3], stimulus2[4],
                           payoff, self.total_points, 'NA', 'NA']) 

        self.trial += 1

    ###########################################################
    # do_similarity_trial
    ###########################################################
    def do_similarity_trial(self, stimulus1, stimulus2, dim, type):
    
        # give breaks
        if self.trial%self.break_every == self.break_every-1: # do a break every 50 trials
            self.show_break('break.png', 'next.gif', None)
        
        
        background = self.clear_screen(black)
        
        
        #trial_text = "How similar are the two symbols?"
        #self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)

        self.update_display(background)
        
        # draws the gabor
        # CHANGE THIS TO DRAW TWO GABORS
        gabor1_surface = self.draw_gabor( stimulus1[0], stimulus1[1], 3.0)
        gabor1_rect = gabor1_surface.get_rect()
        
        gabor2_surface = self.draw_gabor( stimulus2[0], stimulus2[1], 3.0)
        gabor2_rect = gabor2_surface.get_rect()
        

        
        gabor1_rect.center = (background.get_rect().center[0] - 300, background.get_rect().center[1]-60)
        gabor2_rect.center = (background.get_rect().center[0] + 300, background.get_rect().center[1]-60)
        
        background.blit( gabor1_surface, gabor1_rect )
        background.blit( gabor2_surface, gabor2_rect )
        
        
        

        
        self.update_display(background)
        
        sleep(1.0)
        
        background = self.show_centered_image('sim-background.png', black)

        trial_text = "How similar were the two symbols?"
        self.place_text_image(background, trial_text, 42, 0, -250, FOREGROUND, BACKGROUND)
        
        self.update_display(background)
        
        
        
        [res, rt] = self.get_similarity_response_and_rt()
        
        # SOMEWHERE HERE I NEED TO LIMIT PRESENTATION TIME
        
        # use the reward group of the chosen stimulus to determine the reward
        payoff = 'NA'
        
        background = self.clear_screen(black)
        
        self.update_display(background)
        
        #self.place_text_image(background, '%s points' %payoff, 48, 0, 0, FOREGROUND, BACKGROUND)
        #self.update_display(background)
        
        # adjust ITI perhaps
        sleep(1.0)
        
        hit = 'NA'
        
        
        # LIST OF THINGS TO OUTPUT ON EACH TRIAL
        self.output_trial([self.subj, self.cond, self.cat_dim, self.high_group, 2,
                           self.trial, res, rt, hit,
                           stimulus1[0], stimulus1[1], stimulus1[2], stimulus1[3], stimulus1[4],
                           stimulus2[0], stimulus2[1], stimulus2[2], stimulus2[3], stimulus2[4],
                           payoff, self.total_points, dim, type]) 

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

                    
        
        stimuli = self.test_items

        
        for j in range(num_dm_trials):
                if j%40 == 0: shuffle(stimuli)
                self.do_dm_trial(stimuli[(j%40)*2], stimuli[(j%40)*2+1])
                
                
        stage = 1
        #print 'DM task done'
        # similarity task instructions
        while(stage!=2):
            if stage == 1:
                if (self.show_instructions('sim-instrux1.png',  'next.gif', 'back.gif')==BACK):
                    stage = 1
                else:
                    stage = 2

                    
        similarity_pairs = pairings
        shuffle(pairings)
        
        for pair in pairings:
           dim = pair[4]
           type = pair[5]
           for stimulus in self.test_items:
               if [stimulus[3], stimulus[4]] == [pair[0], pair[1]]:
                   stimulus1 = stimulus
               elif [stimulus[3], stimulus[4]] == [pair[2], pair[3]]:
                   stimulus2 = stimulus
           self.do_similarity_trial(stimulus1, stimulus2, dim, type)

        
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
        
        shuffle(cat_set)
        for item in cat_set:
            for stimulus in self.test_items:
                if [stimulus[3], stimulus[4]] == [item[0], item[1]]:
                    trial_stim = stimulus
            self.do_category_trial(trial_stim)
                    
                
        
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

