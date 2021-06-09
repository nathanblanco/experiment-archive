import os, sys, signal
import math
from string import *
from numpy import *
from random import random, randint, shuffle, normalvariate
import pygame
import datetime
from pygame.locals import *
from pygame.base import *
import tempfile
from time import sleep
from lib.pypsyexp import *
import eztext
#execfile('params.py')


experimentname = "Categorization"
experimentversion = '1.6'
black = (0, 0, 0)
darkgrey  = (25, 25, 25)
grey = (175,175,175)
white = (255, 255, 255)

LAPTOPRES = (1024,768)
FULLSCREENRES = (1024,768)

pink = (255,120,255)  # 22 39 0 0 in CMYK
pastelgreen = (187,255,187) # 20 0 23 0 in CMYK

FOREGROUND = white
BACKGROUND = black

NEXT = 1
BACK = 0

laptop = False

screenres = LAPTOPRES

#------------------------------------------------------------
# MelMat Class
#------------------------------------------------------------
class MelMatExp(Experiment):
    def __init__(self, laptop, screenres, experimentname):
        
        self.experimentname = experimentname
        self.last_trial = None
        
        [self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode.txt')
        
        Experiment.__init__(self, laptop, screenres, experimentname)
        self.load_all_resources('images', 'sounds')
        
        self.subj = self.record_subj_num()
        self.session = self.record_session()
        self.cond = self.record_features()
        print "I am subject %s in condition %s" % (self.subj, self.cond)
        pygame.display.quit()
        


    def run_experiments(self):
        
        if sys.platform == 'darwin':
        
            #os.system("python questionaires.py "+str(self.cond)+" "+str(self.subj)+" "+str(self.session))
            os.system("python exp.py "+str(self.cond)+" "+str(self.subj)+" "+str(self.session))


        elif sys.platform == 'win32':

            #file_path = '' # WE'LL NEED TO ADD THIS IF WINDOWS MACHINE
            
            #os.system(file_path+'questionaires.py '+str(self.cond)+" "+str(self.subj))
            os.system(file_path+'exp.py '+str(self.cond)+" "+str(self.subj)+" "+str(self.session))


    def record_subj_num(self):
        background = self.show_centered_image('instructions-background.gif',black)

        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt='Walk-in ID: ')
        # main loop!

        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen

            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break

            if(txtbx.value != last_txtbox_value):
                #self.place_text_image(background, 'In the next hundred trials, how many CHANGES do you expect to see?', 32, -60, -200, white, black)
                self.update_display(background)
                txtbx.draw(background)
                self.update_display(background)
                last_txtbox_value = txtbx.value


        return last_txtbox_value
        
        
    def record_session(self):
        background = self.show_centered_image('instructions-background.gif',black)

        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt='Session: ')
        # main loop!

        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen

            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break

            if(txtbx.value != last_txtbox_value):
                #self.place_text_image(background, 'In the next hundred trials, how many CHANGES do you expect to see?', 32, -60, -200, white, black)
                self.update_display(background)
                txtbx.draw(background)
                self.update_display(background)
                last_txtbox_value = txtbx.value
                
        return last_txtbox_value
                
    def record_features(self):
        background = self.show_centered_image('instructions-background.gif',black)

        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt='Features (1: lines; 2: gabors): ')
        # main loop!

        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen

            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break

            if(txtbx.value != last_txtbox_value):
                #self.place_text_image(background, 'In the next hundred trials, how many CHANGES do you expect to see?', 32, -60, -200, white, black)
                self.update_display(background)
                txtbx.draw(background)
                self.update_display(background)
                last_txtbox_value = txtbx.value


        return last_txtbox_value



#-----------------------
# main
#------------------------
def main():
    global laptop, experimentname;
    experiment = MelMatExp(laptop, screenres, experimentname)
    experiment.run_experiments()

#------------------------------------------------------------
# let's start
#------------------------------------------------------------
if __name__ == '__main__':
    main()
