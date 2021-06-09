import os, sys, signal
import math
from string import *
from random import random, randint, shuffle, normalvariate, uniform, choice
import pygame
import datetime
from pygame.locals import *
import tempfile
#from numpy import *
#from Numeric import *
from time import sleep
from lib.pypsyexp import *
import eztext
execfile('params.py')


laptop = False


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

#------------------------------------------------------------
# MelMat Class
#------------------------------------------------------------
class DDMExperiment(Experiment):
    def __init__(self, laptop, screenres, experimentname):
        
        self.experimentname = experimentname
        
        [self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode.txt')
        #self.cond = int(sys.argv[1])
        #self.subj = int(sys.argv[2])
        self.order = 1
        
        Experiment.__init__(self, laptop, screenres, experimentname)
        self.load_all_resources('images', 'sounds')
        print "I am subject %s in condition: %s" % (self.subj, str(self.cond))
        
        
        print("cond",self.cond)
        if self.cond == 0:
            self.instructions_index = 'gains.png'
        else:
            self.instructions_index = 'losses.png'
        
        self.filename = "data/%s.txt" % self.subj
        self.datafile = open(self.filename, 'w')

            #        if self.cond == 0:
                #self.total_payoff = 0.0
            #else:
        self.total_payoff = 0.0
        self.last_resp = 'na'
        self.last_earn = 0.0
        
        # initialize payoff probabilities randomly
        self.payoffs = [uniform(0.25, 0.75), uniform(0.25, 0.75), uniform(0.25, 0.75), uniform(0.25, 0.75)]

        self.practice_payoffs = [uniform(0.25, 0.75), uniform(0.25, 0.75), uniform(0.25, 0.75), uniform(0.25, 0.75)]

    
        button_images = ['tibetan1.png','tibetan2.png', 'tibetan3.png', 'tibetan4.png', 'tibetan5.png', 'tibetan6.png',
                         'tibetan7.png', 'tibetan8.png', 'tibetan9.png', 'tibetan10.png', 'tibetan11.png', 'tibetan12.png']
    
        shuffle(button_images)

        # main experiment images
        self.stage1images = [button_images[0], button_images[1]]
        self.stage1A = button_images[0]
        self.stage1B = button_images[1]
    
        self.stage2Aimages = [button_images[2], button_images[3]]
        self.stage2Bimages = [button_images[4], button_images[5]]
    
        self.stage2A1 = button_images[2]
        self.stage2A2 = button_images[3]
        self.stage2B1 = button_images[4]
        self.stage2B2 = button_images[5]

        # practice trials images
        self.practice1images = [button_images[6], button_images[7]]
        self.practice1A = button_images[6]
        self.practice1B = button_images[7]
    
        self.practice2Aimages = [button_images[8], button_images[9]]
        self.practice2Bimages = [button_images[10], button_images[11]]
    
        self.practice2A1 = button_images[8]
        self.practice2A2 = button_images[9]
        self.practice2B1 = button_images[10]
        self.practice2B2 = button_images[11]

        
    
        colors = [red, green, blue]
        shuffle(colors)
        self.stage1color = colors[0]
        self.stage2Acolor = colors[1]
        self.stage2Bcolor = colors[2]

        practice_colors = [yellow, purple, orange]
        shuffle(practice_colors)
        self.practice1color = practice_colors[0]
        self.practice2Acolor = practice_colors[1]
        self.practice2Bcolor = practice_colors[2]
        
    #------------------------------------------------------------
    # show_break
    #------------------------------------------------------------
    def show_break(self, waittime):
        background = self.show_centered_image(fnprefix+'break.gif',black)
        self.update_display(background)
        pygame.time.wait(waittime)
    
    def show_game_feedback(self):
        background = self.show_centered_image
    
    
    #------------------------------------------------------------
    # show_thanks
    #------------------------------------------------------------
    def show_thanks(self):
        #background = self.show_centered_image('thanks.gif',white)
        background = self.clear_screen(white)
        
        subj_text = "SUBJECT NUMBER: %s" % self.subj
        self.place_text_image(background, subj_text, 32, 0, 250, black, white)
        
        if self.cond == 1:
            self.total_payoff += 200
        earnings = 3.00 #+ (self.total_payoff)*.01 # was $1.
        entry_text = "YOU HAVE WON: $ %.2f" % earnings
        self.output_trial([earnings,(datetime.datetime.now().ctime())])
        
        self.place_text_image(background, entry_text, 32, 0, -80, black, white)
        self.update_display(background)
        
        #self.escapable_sleep(10000)
        #self.on_exit()
        
        while 1:
            res = self.get_response()
    
    #------------------------------------------------------------
    # get_click_response
    #------------------------------------------------------------
    def get_click_response(self):
        exit = False;
        while not exit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_exit()
                elif event.type == KEYDOWN:
                    if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                        self.on_exit()
                    elif( pygame.key.get_pressed()[K_z]):
                        for but in self.buttons:
                            if(but.myid=='l'):
                                but.do(self.screen)
                                return 0 # 'l'
                    elif( pygame.key.get_pressed()[K_SLASH]):
                        for but in self.buttons:
                            if(but.myid=='r'):
                                but.do(self.screen)
                                return 1 # 'r'
                '''
                    elif event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    for but in self.buttons:
                    if (but.containsPoint(x, y)):
                    rescode = but.do(self.screen)
                    exit = True
                    '''
        return rescode
    
    #------------------------------------------------------------
    # get_click_response_and_rt
    #------------------------------------------------------------
    def get_click_response_and_rt(self):
        time_stamp = pygame.time.get_ticks()
        res = self.get_click_response()
        
        #      if res=='~':	#added: gives way to exit program
        #     	exit()
            #if (res == 0):
        #rescode = 0
            #elif (res == 1):
        #rescode = 1
        
        rt = pygame.time.get_ticks() - time_stamp
        return [res, rt]
    
    #------------------------------------------------------------
    # draw_buttons
    #------------------------------------------------------------
    def draw_buttons(self, mysurf, button1, button2):
        self.buttons = []
        
        x_pos = 200
        
        
        self.buttons = self.buttons + [RespButton( x_pos, 262, 107,108, 'l', self.resources[button1],
                                                  self.resources[button1], self.resources["buttonpress.wav"], self)]
        self.buttons = self.buttons + [RespButton( x_pos+(165*3), 262, 107,108, 'r', self.resources[button2],
                                                  self.resources[button2], self.resources["buttonpress.wav"], self)]
        for i in self.buttons:
            i.draw(mysurf)
    
    #------------------------------------------------------------
    # draw_buttons2
    #------------------------------------------------------------
    def draw_buttons2(self, mysurf, button1, button2):
        self.buttons = []
        
        x_pos = 200
        
        
        self.buttons = self.buttons + [RespButton( x_pos, 492, 107,108, 'l', self.resources[button1],
                                                  self.resources[button1], self.resources["buttonpress.wav"], self)]
        self.buttons = self.buttons + [RespButton( x_pos+(165*3), 492, 107,108, 'r', self.resources[button2],
                                                  self.resources[button2], self.resources["buttonpress.wav"], self)]
        for i in self.buttons:
            i.draw(mysurf)


    #-------------------------------------------------------------
    # get_payoff_value
    #-------------------------------------------------------------
    def get_payoff_value(self, index):
        payoff_prob = self.payoffs[index]
        if self.cond == 0:
            payoff = int(random() <= payoff_prob)
        else: payoff = int(random() <= payoff_prob) - 1
        return payoff
    
    #--------------------------------------------------------------
    # draw_trial_reward
    #--------------------------------------------------------------
    def draw_trial_reward(self, mysurf, payoff ):
        if self.cond == 0:
            self.place_text_image(mysurf, '+   %.0f'%(payoff), 90, -45, 100, white , black)
        else:
            self.place_text_image(mysurf, '-   %.0f'%(-payoff), 90, -45, 100, white , black)
            #self.place_text_image(mysurf, 'Total score:  %.0f'%(self.total_payoff), 40, 205, -300, white , black)
        self.update_display(mysurf)
    
    
    
    #------------------------------------------------------------
    # do_trial
    #------------------------------------------------------------
    def do_trial(self, background, trialnum):
        #print '\n\ntrial ' + str(trialnum)
        
        background = self.clear_screen(black)
        self.place_text_image(background, "CHOOSE", 44, -20, 260, white, black)
        self.place_text_image(background, 'Total score:  %.0f'%(self.total_payoff), 40, 205, -300, white , black)
        self.update_display(background)
        
        
        
        pygame.draw.rect(background, self.stage1color, pygame.Rect(120, 200, 300, 200))
        pygame.draw.rect(background, self.stage1color, pygame.Rect(600, 200, 300, 200))
        self.update_display(background)
        
    
        shuffle(self.stage1images)
        
        self.draw_buttons(background, self.stage1images[0], self.stage1images[1])
        
        self.update_display(background)
        
        #background = self.clear_screen(black)
        self.place_text_image(background, 'Total score:  %.0f'%(self.total_payoff), 40, 205, -300, white , black)
        
        [res1, rt1] = self.get_click_response_and_rt()
        #self.update_display(background)
        
        chosen1 = self.stage1images[res1]
        transition_freq = (random() <= 0.7)
        
        if chosen1 == self.stage1A:
            rescode1 = 0
            if transition_freq ==0:
                stage2 = 0
                stage2_set = self.stage2Aimages
                color2 = self.stage2Acolor
            else:
                stage2 = 1
                stage2_set = self.stage2Bimages
                color2 = self.stage2Bcolor
                
        elif chosen1 == self.stage1B:
            rescode1 = 1
            if transition_freq ==0:
                stage2 = 1
                stage2_set = self.stage2Bimages
                color2 = self.stage2Bcolor
            else:
                stage2 = 0
                stage2_set = self.stage2Aimages
                color2 = self.stage2Acolor

        background = self.clear_screen(black)
        self.place_text_image(background, 'Total score:  %.0f'%(self.total_payoff), 40, 205, -300, white , black)
        pygame.draw.rect(background, self.stage1color, pygame.Rect(360, 180, 300, 200))
        self.show_image_add(background, chosen1, 0, -95)
        self.update_display(background)
        sleep(0.8)

        pygame.draw.rect(background, color2, pygame.Rect(120, 430, 300, 200))
        pygame.draw.rect(background, color2, pygame.Rect(600, 430, 300, 200))
        self.update_display(background)
    
        shuffle(stage2_set)
        
        self.draw_buttons2(background, stage2_set[0], stage2_set[1])
        self.update_display(background)
        self.place_text_image(background, "CHOOSE", 44, -20, 320, white, black)
        
        self.update_display(background)
        
        background = self.clear_screen(black)
        self.place_text_image(background, 'Total score:  %.0f'%(self.total_payoff), 40, 205, -300, white , black)
        
        [res2, rt2] = self.get_click_response_and_rt()
        
        chosen2 = stage2_set[res2]
        if chosen2 == self.stage2A1:
            rescode2 = 0
        elif chosen2 == self.stage2A2:
            rescode2 = 1
        elif chosen2 == self.stage2B1:
            rescode2 = 2
        else:
            rescode2 = 3
    
        for i in range(len(self.payoffs)):
            self.payoffs[i] += normalvariate(0, 0.025)
            if self.payoffs[i] < 0.25:
                self.payoffs[i] = 0.25
            if self.payoffs[i] > 0.75:
                self.payoffs[i] = 0.75
        
        payoff = self.get_payoff_value(rescode2)
        self.total_payoff += payoff
    
        pygame.draw.rect(background, color2, pygame.Rect(360, 180, 300, 200))
        self.show_image_add(background, chosen2, 0, -95)
        self.update_display(background)

        self.draw_trial_reward(background, payoff)
        self.place_text_image(background, 'Total score:  %.0f'%(self.total_payoff), 40, 205, -300, white , black)
        sleep(0.8)
        
        background = self.clear_screen(black)
        self.update_display(background)
        sleep(0.6)
        
        pygame.event.clear()
        
        self.output_trial([self.subj, self.cond, self.order, trialnum, chosen1, rescode1, rt1, chosen2, rescode2, rt2, int(transition_freq), stage2, payoff, self.total_payoff, self.payoffs[0], self.payoffs[1], self.payoffs[2], self.payoffs[3]])
    
        trialnum += 1


    #------------------------------------------------------------
    # do_practice_trial
    #------------------------------------------------------------
    def do_practice_trial(self, background, trialnum):
        #print '\n\ntrial ' + str(trialnum)
        
        background = self.clear_screen(black)
        self.place_text_image(background, "CHOOSE", 44, -20, 260, white, black)
        self.place_text_image(background, 'Practice Trials', 40, 205, -300, white , black)
        self.update_display(background)
        
        
        
        pygame.draw.rect(background, self.practice1color, pygame.Rect(120, 200, 300, 200))
        pygame.draw.rect(background, self.practice1color, pygame.Rect(600, 200, 300, 200))
        self.update_display(background)
    
        shuffle(self.practice1images)
        
        self.draw_buttons(background, self.practice1images[0], self.practice1images[1])
        
        self.update_display(background)
        

        self.place_text_image(background, 'Practice Trials', 40, 205, -300, white , black)
        
        [res1, rt1] = self.get_click_response_and_rt()
       
        #self.update_display(background)
        
        chosen1 = self.practice1images[res1]
        transition_freq = (random() <= 0.7)
        
        if chosen1 == self.practice1A:
            rescode1 = 0
            if transition_freq ==0:
                stage2 = 0
                stage2_set = self.practice2Aimages
                color2 = self.practice2Acolor
            else:
                stage2 = 1
                stage2_set = self.practice2Bimages
                color2 = self.practice2Bcolor
                
        elif chosen1 == self.practice1B:
            rescode1 = 1
            if transition_freq ==0:
                stage2 = 1
                stage2_set = self.practice2Bimages
                color2 = self.practice2Bcolor
            else:
                stage2 = 0
                stage2_set = self.practice2Aimages
                color2 = self.practice2Acolor

        background = self.clear_screen(black)
        self.place_text_image(background, 'Practice Trials', 40, 205, -300, white , black)
        pygame.draw.rect(background, self.practice1color, pygame.Rect(360, 180, 300, 200))
        self.show_image_add(background, chosen1, 0, -95)
        self.update_display(background)
        sleep(0.8)

        pygame.draw.rect(background, color2, pygame.Rect(120, 430, 300, 200))
        pygame.draw.rect(background, color2, pygame.Rect(600, 430, 300, 200))
        self.update_display(background)
    
        shuffle(stage2_set)
        
        self.draw_buttons2(background, stage2_set[0], stage2_set[1])
        self.update_display(background)
        self.place_text_image(background, "CHOOSE", 44, -20, 320, white, black)
        
        self.update_display(background)
        
        background = self.clear_screen(black)
        self.place_text_image(background, 'Practice Trials', 40, 205, -300, white , black)
        
        [res2, rt2] = self.get_click_response_and_rt()
        
        chosen2 = stage2_set[res2]
        if chosen2 == self.practice2A1:
            rescode2 = 0
        elif chosen2 == self.practice2A2:
            rescode2 = 1
        elif chosen2 == self.practice2B1:
            rescode2 = 2
        else:
            rescode2 = 3
    
        for i in range(len(self.practice_payoffs)):
            self.practice_payoffs[i] += normalvariate(0, 0.025)
            if self.practice_payoffs[i] < 0.25:
                self.practice_payoffs[i] = 0.25
            if self.practice_payoffs[i] > 0.75:
                self.practice_payoffs[i] = 0.75
        
        payoff = self.get_payoff_value(rescode2)
        #self.total_payoff += payoff
    
        pygame.draw.rect(background, color2, pygame.Rect(360, 180, 300, 200))
        self.show_image_add(background, chosen2, 0, -95)
        self.update_display(background)

        self.draw_trial_reward(background, payoff)
        self.place_text_image(background, 'Practice Trials', 40, 205, -300, white , black)
        sleep(0.8)
        
        background = self.clear_screen(black)
        self.update_display(background)
        sleep(0.6)
        
        pygame.event.clear()
        
        self.output_trial([self.subj, self.cond, self.order, trialnum, chosen1, rescode1, rt1, chosen2, rescode2, rt2, int(transition_freq), stage2, payoff, self.total_payoff, self.practice_payoffs[0], self.practice_payoffs[1], self.practice_payoffs[2], self.practice_payoffs[3]])
    
        trialnum += 1
    

    
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
    # do_regular_exp
    # round says whether this is first (1) or second (2) time to the function
    #------------------------------------------------------------
    def do_regular_exp(self):
        
        background = self.clear_screen(black)
        pygame.mouse.set_visible(1)
        stage = 1
        
        if self.cond == 0:
            instr = 'gains'
        else:
            instr = 'losses'
                
        while(stage!=6):
            if stage == 1:
                if (self.show_instructions('stages_instr1_'+instr+'.png',  'next.gif', 'back.gif')==BACK):
                    stage = 1
                else:
                    stage = 2
            elif stage == 2:
                if self.show_instructions('stages_instr2_'+instr+'.png',  'next.gif', 'back.gif')==BACK:
                    stage = 1
                else:
                    stage = 3
            elif stage == 3:
                if self.show_instructions('stages_instr3_'+instr+'.png',  'next.gif', 'back.gif')==BACK:
                    stage = 2
                else:
                    stage = 4
            elif stage == 4:
                if self.show_instructions('stages_instr4.png',  'next.gif', 'back.gif')==BACK:
                    stage = 3
                else:
                    stage = 5

            elif stage == 5:
                if self.show_instructions('pre_practice.png',  'next.gif', 'back.gif')==BACK:
                    stage = 4
                else:
                    stage = 6
        
    

        
        pygame.mouse.set_visible(False)
        pygame.time.wait(1000)
        # practice trials
        for j in range(-50, 0):
            self.do_practice_trial(background, j)

        pygame.mouse.set_visible(1)
        stage = 0
        while(stage!=1):
             if self.show_instructions('post_practice.png',  'begin.gif', 'back.gif')==BACK:
                    stage = 0
             else:
                    stage = 1
        pygame.mouse.set_visible(0)
        # main trials
        for i in range(1,ntrials_stages+1):
            
            
            
            self.do_trial(background, i)
            

            
            if ((i%50)==0):
                
                pygame.mouse.set_visible(True)
                if (i!=ntrials_stages):
                    self.show_instructions('break.png', 'next.gif', None)
                    pygame.mouse.set_visible(False)

        
        pygame.mouse.set_visible(True)
        pygame.time.wait(1000)
        if self.order == 2:
                self.show_thanks()

#-----------------------
# main                   
#------------------------
def main():
    global laptop, experimentname;
    experiment = DDMExperiment(laptop, screenres, experimentname)
    experiment.do_regular_exp()

#------------------------------------------------------------
# let's start
#------------------------------------------------------------
if __name__ == '__main__':
    main()

