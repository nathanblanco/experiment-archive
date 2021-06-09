#------------------------------------------------------------
# import modules
#------------------------------------------------------------
import os, sys, signal
import math
from string import *
from numpy import *
from ftplib import FTP
from random import random, randint, shuffle, normalvariate
import pygame
import datetime
from pygame.locals import *
import tempfile
from time import sleep
from lib.pypsyexp import *
import eztext

#execfile('params.py')

experimentname = "Cat-DM task"
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
# PreExpSurveys Class
#------------------------------------------------------------
class PreExpSurveys(Experiment):
    def __init__(self, laptop, screenres, experimentname):
        
        self.experimentname = experimentname
        self.last_trial = None
        
        #[self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode_quest.txt')
        self.cond = int(sys.argv[1])
        self.subj = int(sys.argv[2])

        print "I am subject %s in condition %s" % (self.subj, self.cond)
        
        Experiment.__init__(self, laptop, screenres, experimentname)
        
        self.filename = "data_questionaires/%s.dat" % self.subj
        self.datafile = open(self.filename, 'w')
                
                
        self.load_all_resources('images', 'sounds')
        
        # log time
        self.output_trial([datetime.datetime.now().ctime()])
    



        # MOVE ALL THIS TO QUESTIONAIRES.PY
        self.cesd_score = -1
        self.bis_score = -1
        self.SR = 0
        self.SP = 0
        
        self.age = 0
        self.gender = 'x'
        self.education = 'x'


    #------------------------------------------------------------
    # do_cesd
    #------------------------------------------------------------
    def do_cesd(self):
        
        
        
        
        questions = ['I was bothered by things that usually do not bother me.',
                     'I did not feel like eating; my appetite was poor.',
                     'I felt that I could not shake off the blues even with help from my family or friends.',
                     'I felt that I was just as good as other people.',
                     'I had trouble keeping my mind on what I was doing.',
                     'I felt depressed.',
                     'I felt that everything I did was an effort.',
                     'I felt hopeful about the future.',
                     'I thought my life had been a failure.',
                     'I felt fearful.',
                     'My sleep was restless.',
                     'I was happy.',
                     'I talked less than usual.',
                     'I felt lonely.',
                     'People were unfriendly.',
                     'I enjoyed life.',
                     'I had crying spells.',
                     'I felt sad.',
                     'I felt that people dislike me.',
                     'I could not get "going".']
        
        
        resp = [0]*len(questions)
        for line in range(len(questions)):
            while 1:
                resp[line] = self.cesd_trial(questions[line])
                if resp[line] == '1' or resp[line] == '2' or resp[line] == '3' or resp[line] == '4': break
            
        self.output_trial(resp)
        
        totalscore = 0
        # 4 8 12 and 16 are scored reversed.
        for i in range(len(resp)):
            if (i == 3) or (i == 7) or (i == 11) or (i == 15):
                totalscore += 4 - int(resp[i])
            else:
                totalscore += int(resp[i]) - 1
        
        print totalscore
        return totalscore

    def cesd_trial(self, question):
        
        background = self.show_centered_image('instructions-background.gif',black)
        self.place_text_image(background, 'CESD Instructions:', 24, 0, -270, white, black)
        
        
        cesdInstructions=['We will be showing you a list of ways you might have felt or behaved.',
                          'Please indicate how often you have felt this way during the last week',
                          'by typing the number corresponding to the statements that best describes you.',
                          'Please answer every statement, even if you are not completely sure which answer is right for you.']
        
        
        self.place_text_image(background, cesdInstructions[0], 24, 0, -220, white,  black)
        self.place_text_image(background, cesdInstructions[1], 24, 0, -190, white,  black)
        self.place_text_image(background, cesdInstructions[2], 24, 0, -160, white,  black)
        self.place_text_image(background, cesdInstructions[3], 24, 0, -130, white,  black)
        
        cesdScale = ['1 - Rarely or none of the time (less than 1 day).',
                     '2 - Some or a little of the time (1-2 days).',
                     '3 - Occassionally or a moderate amount of time (3-4 days).',
                     '4 - Most or all of the time (5-7 days).']
        
        self.place_text_image(background, cesdScale[0], 21, 0, 130, white,  black)
        self.place_text_image(background, cesdScale[1], 21, 0, 150, white,  black)
        self.place_text_image(background, cesdScale[2], 21, 0, 170, white,  black)
        self.place_text_image(background, cesdScale[3], 21, 0, 190, white,  black)
        
        
        self.update_display(background)
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
            
            
            self.place_text_image(background, question, 32, 0, -10, white, black)
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        return last_txtbox_value
    #------------------------------------------------------------
    # do_bis11
    #------------------------------------------------------------
    def do_bis11(self):
        
        
        
        
        questions = ['I plan tasks carefully.',
                     'I do things without thinking.',
                     'I make-up my mind quickly.',
                     'I am happy-go-lucky.',
                     "I don't pay 'attention'.",
                     'I have "racing" thoughts.',
                     'I plan trips well ahead of time.',
                     'I am self controlled.',
                     'I concentrate easily.',
                     'I save regularly.',
                     'I "squirm" at plays or lectures.',
                     'I am a careful thinker.',
                     'I plan for job security.',
                     'I say things without thinking.',
                     'I like to think about complex problems.',
                     'I change jobs.',
                     'I act "on impulse."',
                     'I get easily bored when solving thought problems.',
                     'I act on the spur of the moment.',
                     'I am a steady thinker.',
                     'I change residences.',
                     'I buy things on impulse.',
                     'I can only think about one thing at a time.',
                     'I change hobbies.',
                     'I spend or charge more than I earn.',
                     'I often have extraneous thoughts when thinking.',
                     'I am more interested in the present than the future.',
                     'I am restless at the theater or lectures.',
                     'I like puzzles.',
                     'I am future oriented.']
        
        
        resp = [0]*len(questions)
        for line in range(len(questions)):
            while 1:
                resp[line] = self.bis11_trial(questions[line])
                if resp[line] == '1' or resp[line] == '2' or resp[line] == '3' or resp[line] == '4': break
        
        self.output_trial(resp)
        
        totalscore = 0
        # 4 8 12 and 16 are scored reversed.
        for i in range(len(resp)):
            if (i == 8) or (i == 19) or (i == 29) or (i == 0) or (i == 6) or (i ==7) or (i==11) or (i==12) or (i==9) or (i==14) or (i==28):
                totalscore += 5 - int(resp[i])
            else:
                totalscore += int(resp[i])
        
        print totalscore
        return totalscore

    def bis11_trial(self, question):
        
        background = self.show_centered_image('instructions-background.gif',black)
        self.place_text_image(background, 'BIS Instructions:', 24, 0, -270, white, black)
        
        
        bisInstructions=['People differ in the ways they act and think in different situations.  This is a test',
                         'to measure some of the ways in which you act and think.  Read each statement and enter',
                         'the number that corresponds to how often you feel that way.  Do not spend too much',
                         'time on any statement. Answer quickly and honestly.']
        
        
        self.place_text_image(background, bisInstructions[0], 24, 0, -220, white,  black)
        self.place_text_image(background, bisInstructions[1], 24, 0, -190, white,  black)
        self.place_text_image(background, bisInstructions[2], 24, 0, -160, white,  black)
        self.place_text_image(background, bisInstructions[3], 24, 0, -130, white,  black)
        
        bisScale = ['1 - Rarely/Never',
                    '2 - Occasionally',
                    '3 - Often',
                    '4 - Almost Always/Always']
        
        self.place_text_image(background, bisScale[0], 21, 0, 130, white,  black)
        self.place_text_image(background, bisScale[1], 21, 0, 150, white,  black)
        self.place_text_image(background, bisScale[2], 21, 0, 170, white,  black)
        self.place_text_image(background, bisScale[3], 21, 0, 190, white,  black)
        
        
        self.update_display(background)
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
            
                #if(txtbx.value != last_txtbox_value):
            self.place_text_image(background, question, 32, 0, -10, white, black)
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        return last_txtbox_value

    #------------------------------------------------------------
    # do_spsrq
    #------------------------------------------------------------
    def do_spsrq(self):
        
        questions = [['Do you often refrain from doing something because you are afraid of it being illegal?'],
                     ['Does the good prospect of obtaining money motivate you strongly to do some things?'],
                     ['Do you prefer not to ask for something when you are not sure you will obtain it?'],
                     ['Are you frequently encouraged to act by the possibility of being valued', 'in your work, in your studies, with your friends or with family?'],
                     ['Are you often afraid of new or unexpected situations?'],
                     ['Do you often meet people that you find physically attractive?'],
                     ['Is if difficult for you to telephone someone you do not know?'],
                     ['Do you like taking drugs or alcohol because of the pleasure you get from them?'],
                     ['Do you often renounce your rights when you know you can avoid a quarrel', 'with a person or an organization?'],
                     ['Do you often do things to be praised?'],
                     ['As a child, were you troubled by punishments at home or in school?'],
                     ['Do you like being the center of attention at a party or a social meeting?'],
                     ['In tasks that you are not prepared for, do you attach great importance', 'to the possibility of failure?'],
                     ['Do you spend a lot of time on obtaining a good image?'],
                     ['Are you easily discouraged in difficult situations?'],
                     ['Do you need people to show their affection for you all the time?'],
                     ['Are you a shy person?'],
                     ['When you are in a group, do you try to make your opinions the most', 'intelligent or the funniest?'],
                     ['Whenever possible, do you avoid demonstrating your skills for fear of being embarrassed?'],
                     ['Do you often take the opportunity to talk to people you find attractive?'],
                     ['When you are with a group, do you have difficulties selecting a good topic to talk about?'],
                     ["As a child, did you do a lot of things to get people's approval?"],
                     ['Is it often difficult for you to fall asleep when you think', 'about things you have done or must do?'],
                     ['Does the possibility of social advancement move you to action,', 'even if this involves not playing fair?'],
                     ['Do you think a lot before complaining in a restaurant if your', 'meal is not well prepared?'],
                     ['Do you generally give preferences to those activities that imply an immediate gain?'],
                     ['Would you be bothered if you had to return to a store when you', 'noticed you were given the wrong change?'],
                     ['Do you often have trouble resisting the temptation of doing forbidden things?'],
                     ['Whenever you can, do you avoid going to unknown places?'],
                     ['Do you like to compete and do everything you can to win?'],
                     ['Are you often worried by things that you said or did?'],
                     ['Is it easy for you to associate tastes and smells to very pleasant events?'],
                     ['If you were working, would it be difficult for you to ask your', 'boss for a raise (salary increase)?'],
                     ['Are there a large number of objects or sensations that remind you', 'of pleasant events?'],
                     ['Do you generally try to avoid speaking in public?'],
                     ['When you start to play a slot machine, is it often difficult for you to stop?'],
                     ['Do you regularly think that you could accomplish more, if not for', 'your insecurity or fear?'],
                     ['Do you sometimes do things for quick gains?'],
                     ['Comparing yourself to people you know, are you afraid of many things?'],
                     ['Does your attention easily stray from your work in the presence of', 'an attractive stranger?'],
                     ['Do you often find yourself worrying about things to the extent that', 'you find it hard to think?'],
                     ['Would you be interested in money to the point of being able to do risky jobs?'],
                     ['Do you often refrain from doing something you like in order not to be', 'rejected or disapproved of by others?'],
                     ['Do you like to be competitive in all activities?'],
                     ['Generally, do you pay more attentions to threats than to pleasant events?'],
                     ['Would you like to be a socially powerful person?'],
                     ['Do you often refrain from doing something because of your fear of being embarrassed?'],
                     ['Do you like displaying your physical abilities even though this may involve danger?']]
        
        
        resp = [0]*len(questions)
        for line in range(len(questions)):
            while 1:
                resp[line] = self.spsrq_trial(questions[line])
                if resp[line] == 'y' or resp[line] == 'n': break
        
        self.output_trial(resp)
        
        
        
        for i in range(len(resp)):
            if i%2 == 0 and resp[i] == 'y':
                self.SP += 1
            elif i%2 == 1 and resp[i] == 'y':
                self.SR += 1


    def spsrq_trial(self, question):
        
        background = self.show_centered_image('instructions-background.gif',black)
        self.place_text_image(background, 'SPSRQ Instructions:', 24, 0, -270, white, black)
        
        
        cesdInstructions=['Please answer the following questions by typing either',
                          "'y' for yes, or 'n' for no",
                          'Please answer every statement, even if you are not completely sure which answer is right for you.']
        
        
        self.place_text_image(background, cesdInstructions[0], 24, 0, -220, white,  black)
        self.place_text_image(background, cesdInstructions[1], 24, 0, -190, white,  black)
        self.place_text_image(background, cesdInstructions[2], 24, 0, -160, white,  black)
        
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
            
                #if(txtbx.value != last_txtbox_value):
            y = -10
            for i in question:
                self.place_text_image(background, i, 32, 0, y, white, black)
                y += 32
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        return last_txtbox_value

    #------------------------------------------------------------
    # do_masq
    #------------------------------------------------------------
    def do_masq(self):
        
        questions = [ 
                     'Felt sad', 
                     'Startled easily', 
                     'Felt cheerful', 
                     'Felt afraid', 
                     'Felt discouraged', 
                     'Hands were shaky', 
                     'Felt optimistic', 
                     'Had diarrhea', 
                     'Felt worthless', 
                     'Felt really happy', 
                     'Felt nervous', 
                     'Felt depressed', 
                     'Was short of breath', 
                     'Felt uneasy', 
                     'Was proud of myself', 
                     'Had a lump in my throat', 
                     'Felt pain', 
                     'Felt unattractive', 
                     'Had hot or cold spells', 
                     'Had an upset stomach', 
                     'Felt like a failure', 
                     'Felt like I was having a lot of fun', 
                     'Blamed myself for a lot of things', 
                     'Hands were cold or sweaty', 
                     'Felt withdrawn from other people', 
                     'Felt keyed up, on edge', 
                     'Felt like I had a lot of energy', 
                     'Was trembling or shaking', 
                     'Felt inferior to others', 
                     'Had trouble swallowing', 
                     'Felt like crying', 
                     'Was unable to relax', 
                     'Felt really slowed down', 
                     'Was disappointed in myself', 
                     'Felt nauseous', 
                     'Felt hopeless', 
                     'Felt dizzy or lightheaded', 
                     'Felt sluggish or tired', 
                     "Felt really 'up' or lively", 
                     'Had pain in my chest', 
                     'Felt really bored', 
                     'Felt like I was choking', 
                     'Looked forward to things with enjoyment', 
                     'Muscles twitched or trembled', 
                     'Felt pessimistic about the future', 
                     'Had a very dry mouth', 
                     'Felt like I had a lot of interesting things to do', 
                     'Was afraid I was going to die', 
                     'Felt like I had accomplished a lot', 
                     'Felt like it took extra effort to get started', 
                     'Felt like nothing was very enjoyable', 
                     'Heart was racing or pounding', 
                     'Felt like I had a lot to look forward to', 
                     'Felt numbness or tingling in my body', 
                     "Felt tense or 'high-strung'", 
                     'Felt hopeful about the future', 
                     "Felt like there wasn't anything interesting or fun to do", 
                     'Seemed to move quickly and easily', 
                     'Muscles were tense or sore', 
                     'Felt really good about myself', 
                     'Thought about death or suicide', 
                     'Had to urinate frequently']
        
        
        resp = [0]*len(questions)
        for line in range(len(questions)):
            while 1:
                resp[line] = self.masq_trial(questions[line])
                if resp[line] == '1' or resp[line] == '2' or resp[line] == '3' or resp[line] == '4' or resp[line] == '5': break
        
        self.output_trial(resp)
        

        reversed_scored = [2, 6, 9, 14, 21, 26, 38, 42, 46, 48, 52, 55, 57, 59]

        totalscore = 0
        # 4 8 12 and 16 are scored reversed.
        for i in range(len(resp)):
            if i in reversed_scored:
                totalscore += 6 - int(resp[i])
            else:
                totalscore += int(resp[i])
                
        print totalscore
        return totalscore


    def masq_trial(self, question):
        
        background = self.show_centered_image('instructions-background.gif',black)
        self.place_text_image(background, 'MASQ Instructions:', 24, 0, -270, white, black)
        
        masqInstructions = ['The following items will be a list of feelings, sensations, problems, and experiences that',
                            'people sometimes have. Read each item and then choose the option that best describes how',
                            'much you have felt or experienced things this way during the past week, including today.']
                            
        
        
        self.place_text_image(background, masqInstructions[0], 24, 0, -220, white,  black)
        self.place_text_image(background, masqInstructions[1], 24, 0, -190, white,  black)
        self.place_text_image(background, masqInstructions[2], 24, 0, -160, white,  black)
        
        
        masqScale = ['1 - NOT AT ALL',
                     '2 - A LITTLE BIT',
                     '3 - MODERATELY',
                     '4 - QUITE A BIT',
                     '5 - EXTREMELY']
        
        self.place_text_image(background, masqScale[0], 21, 0, 130, white,  black)
        self.place_text_image(background, masqScale[1], 21, 0, 150, white,  black)
        self.place_text_image(background, masqScale[2], 21, 0, 170, white,  black)
        self.place_text_image(background, masqScale[3], 21, 0, 190, white,  black)
        self.place_text_image(background, masqScale[4], 21, 0, 210, white,  black)
        
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
 

            self.place_text_image(background, question, 32, 0, -10, white, black)
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        return last_txtbox_value
        
    #---------------------------------------------------    
    # apathy
    #---------------------------------------------------
    def do_apathy(self):
        
        questions = ['Are you interested in learning new things?',
                     'Does anything interest you?',
                     'Are you concerned about your condition?',
                     'Do you put much effort into things?',
                     'Are you always looking for something to do?',
                     'Do you have plans for the future?',
                     'Do you have motivation?',
                     'Do you have energy for daily activities?',
                     'Does someone have to tell you what to do each day?',
                     'Are you indifferent to things?',
                     'Are you unconcerned with many things?',
                     'Do you need a push to get started?',
                     'Are you neither happy nor sad, just in between?',
                     'Would you consider yourself apathetic?' ]
        
        
        resp = [0]*len(questions)
        for line in range(len(questions)):
            while 1:
                resp[line] = self.apathy_trial(questions[line])
                if resp[line] == '1' or resp[line] == '2' or resp[line] == '3' or resp[line] == '4': break
        
        self.output_trial(resp)
        

        totalscore = 0
        
        for i in range(8):
            totalscore += 4 - int(resp[i])
        for i in range(8,14):
            totalscore += int(resp[i])-1
                
        print totalscore
        return totalscore


    def apathy_trial(self, question):
        
        background = self.show_centered_image('instructions-background.gif',black)
        self.place_text_image(background, 'Instructions:', 24, 0, -270, white, black)
        
        apathyInstructions = ['For each of the next questions, please select the answer that best describes', 
                               'your thoughts, feelings, and actions during the past 4 weeks',  
                               'Use number 1-4 to select the appropriate option.']
                            
        
        
        self.place_text_image(background, apathyInstructions[0], 24, 0, -220, white,  black)
        self.place_text_image(background, apathyInstructions[1], 24, 0, -190, white,  black)
        self.place_text_image(background, apathyInstructions[2], 24, 0, -160, white,  black)
        
        
        apathyScale = ['1 - NOT AT ALL',
                     '2 - SLIGHTLY',
                     '3 - SOME',
                     '4 - ALOT']
        
        self.place_text_image(background, apathyScale[0], 21, 0, 130, white,  black)
        self.place_text_image(background, apathyScale[1], 21, 0, 150, white,  black)
        self.place_text_image(background, apathyScale[2], 21, 0, 170, white,  black)
        self.place_text_image(background, apathyScale[3], 21, 0, 190, white,  black)
        
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
 

            self.place_text_image(background, question, 32, 0, -10, white, black)
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        return last_txtbox_value
        
            
    #------------------------------------------------------------
    # standard_questions
    #------------------------------------------------------------
    def standard_questions(self):
        
        # AGE
        background = self.show_centered_image('instructions-background.gif',black)
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=10, color=(0,255,0), prompt = 'Type here: ')
        

        # main loop!
        while 1:

            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
            
            if(txtbx.value != last_txtbox_value):
                self.place_text_image(background, "What is your age?", 32, 0, -10, white, black)
                self.update_display(background)
                txtbx.draw(background)
                
                self.update_display(background)
                last_txtbox_value = txtbx.value
                self.clear_screen(black)
        
        self.age = last_txtbox_value
        
        background = self.show_centered_image('instructions-background.gif',black)
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
            
                #if(txtbx.value != last_txtbox_value):
            self.place_text_image(background, "What is your gender?", 32, 0, -10, white, black)
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        self.gender = last_txtbox_value
        
        background = self.show_centered_image('instructions-background.gif',black)
        
        edScale = ['1 - SOME SCHOOL',
                   '2 - HS GRADUATE',
                   '3 - SOME COLLEGE',
                   '4 - 2YR COLLEGE',
                   '5 - 4YR COLLEGE',
                   '6 - POSTGRADUATE']
        
        self.place_text_image(background, edScale[0], 21, 0, 130, white,  black)
        self.place_text_image(background, edScale[1], 21, 0, 150, white,  black)
        self.place_text_image(background, edScale[2], 21, 0, 170, white,  black)
        self.place_text_image(background, edScale[3], 21, 0, 190, white,  black)
        self.place_text_image(background, edScale[4], 21, 0, 210, white,  black)
        self.place_text_image(background, edScale[5], 21, 0, 230, white,  black)
        self.update_display(background)
        
        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt = 'Type here: ')
        # main loop!
        
        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen
            
            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break
            
                #if(txtbx.value != last_txtbox_value):
            self.place_text_image(background, "Education level?", 32, 0, -10, white, black)
            self.update_display(background)
            txtbx.draw(background)
            self.update_display(background)
            last_txtbox_value = txtbx.value
            self.clear_screen(black)
        
        self.education = last_txtbox_value

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

#########################
    def do_questionaires(self):
        
        pygame.mouse.set_visible(1)
        stage = 1
        while(stage!=2):
            if stage == 1:
                if (self.show_instructions('main-instrux.png',  'next.gif', 'back.gif')==BACK):
                    stage = 1
                else:
                    stage = 2
    
        #self.standard_questions()
        #self.cesd_score = self.do_cesd()
        self.do_spsrq()
        self.bis_score = self.do_bis11()
        self.masq_score = self.do_masq()
        self.apathy_score = self.do_apathy()

        self.output_trial(['self.subj', 'self.age', 'self.gender', 'self.education', 'self.cesd_score', self.bis_score, self.SP, self.SR, self.masq_score, self.apathy_score])

#-----------------------
# main
#------------------------
def main():
    global experimentname;
    experiment = PreExpSurveys(laptop, screenres, experimentname)
    experiment.do_questionaires()

#------------------------------------------------------------
# let's start
#------------------------------------------------------------
if __name__ == '__main__':
    main()

