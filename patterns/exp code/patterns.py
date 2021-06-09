#!/usr/bin/pythonw



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
import itertools



#------------------------------------------------------------
# Define some global settings
#------------------------------------------------------------
LAPTOPRES = (1024,768)
FULLSCREENRES = (1024, 768)

NEXT = 1
BACK = 0

#
experimentname = 'Patterns'
laptop = True


            
#if laptop:
screenres = LAPTOPRES
    #else:
    #    screenres = FULLSCREENRES

# colors we might use
white = (255, 255, 255)
grey = (175,175,175)
boxgrey = (128,128,128)
black = (0, 0, 0)

blue = (30, 170, 250)
green = (0,175,0)
red = (175, 0, 0)
yellow = (255, 215, 0)

oxygreen = (22,71,8)
screengreen = (173,198,156)
ltgrey = (193,193,193)
divred = (102,63,62)

transparent = (128, 128, 128)


#------------------------------------------------------------
# MouseButton Classes:
# general code that makes the clickable buttons
#------------------------------------------------------------

# buttons for moving to next page of instructions
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

# buttons for getting responses during the task
class RespButton(MouseButton):
    def __init__(self, x, y, w, h, id, myimage, myimagepressed, snd, presstime, app):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.myid = id
        self.image = myimage
        self.image.set_colorkey((255,255,255))
        self.imagep = myimagepressed
        self.imagep.set_colorkey((255,255,255))
        self.snd = snd
        self.presstime = presstime
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
        pygame.time.wait(self.presstime) #
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
        pygame.display.flip()
        return self.myid

#------------------------------------------------------------
# ExplDev Class
#------------------------------------------------------------
class ExplDevExp(Experiment):
	def __init__(self, laptop, screenres, experimentname):
	
		# inititialize everything
		self.experimentname = experimentname
	
		Experiment.__init__(self, laptop, screenres, experimentname)
		self.load_all_resources('images', 'sounds')
	
		self.cond = 'baseline' # 
		self.subj = self.record_subj('Subject #: ')
		self.age = self.record_subj('Age:  ')
		self.gender = self.record_subj('Gender:  ')
	
		self.filename = "data/%s.dat" % self.subj
		self.datafile = open(self.filename, 'w')
		
		# log start time in the datafile
		self.output_trial([datetime.datetime.now().ctime()])
	
		self.trial = 1
	
		# Locations of the creatures 
		# The first two are xy coords with origin at top-left, 
		# the next two are for coordinates with origin in the center of the screen
		self.locations = [ [110, 520], [540, 520]]
		
		# THESE WILL BE SHIFTED RIGHT
		 # Locations of the response options for the final test phase
		self.transfer_locations = [ [110, 520], 
									[350, 520], 
									[590, 520], 
									[830, 520]]


		# add in pattern_type, match_type, and correct answer for each
		self.pretest_set = [ ['pre_1_top.png', 'pre_1_bottomA.png', 'pre_1_bottomB.png', 'ABB', 'Shape', 'B'],
							 ['pre_2_top.png', 'pre_2_bottomA.png', 'pre_2_bottomB.png', 'ABB', 'Color', 'B'],
							 ['pre_3_top.png', 'pre_3_bottomA.png', 'pre_3_bottomB.png', 'BBA', 'Color', 'B'],
							 ['pre_4_top.png', 'pre_4_bottomA.png', 'pre_4_bottomB.png', 'ABA', 'Shape', 'A'],
							 ['pre_5_top.png', 'pre_5_bottomA.png', 'pre_5_bottomB.png', 'AAB', 'Shape', 'B'],
							 ['pre_6_top.png', 'pre_6_bottomA.png', 'pre_6_bottomB.png', 'BBA', 'Color', 'B'],
							 ['pre_7_top.png', 'pre_7_bottomA.png', 'pre_7_bottomB.png', 'ABA', 'Color', 'B'],
							 ['pre_8_top.png', 'pre_8_bottomA.png', 'pre_8_bottomB.png', 'AAB', 'Shape', 'A'],
							 ['pre_9_top.png', 'pre_9_bottomA.png', 'pre_9_bottomB.png', 'AAB', 'Shape', 'A'],
							 ['pre_10_top.png', 'pre_10_bottomA.png', 'pre_10_bottomB.png', 'ABA', 'Color', 'B'],
							 ['pre_11_top.png', 'pre_11_bottomA.png', 'pre_11_bottomB.png', 'AAB', 'Color', 'A'],
							 ['pre_12_top.png', 'pre_12_bottomA.png', 'pre_12_bottomB.png', 'ABB', 'Shape', 'B']]

							 
		self.posttest_set = [ ['post_1_top.png', 'post_1_bottomA.png', 'post_1_bottomB.png', 'ABB', 'Color', 'A'],
							  ['post_2_top.png', 'post_2_bottomA.png', 'post_2_bottomB.png', 'ABB', 'Shape', 'B'],
							  ['post_3_top.png', 'post_3_bottomA.png', 'post_3_bottomB.png', 'ABA', 'Color', 'A'],
							  ['post_4_top.png', 'post_4_bottomA.png', 'post_4_bottomB.png', 'ABB', 'Shape', 'B'],
							  ['post_5_top.png', 'post_5_bottomA.png', 'post_5_bottomB.png', 'BBA', 'Color', 'B'],
							  ['post_6_top.png', 'post_6_bottomA.png', 'post_6_bottomB.png', 'AAB', 'Shape', 'A'],
							  ['post_7_top.png', 'post_7_bottomA.png', 'post_7_bottomB.png', 'BBA', 'Shape', 'B'],
							  ['post_8_top.png', 'post_8_bottomA.png', 'post_8_bottomB.png', 'AAB', 'Color', 'A'],
							  ['post_9_top.png', 'post_9_bottomA.png', 'post_9_bottomB.png', 'AAB', 'Color', 'A'],
							  ['post_10_top.png', 'post_10_bottomA.png', 'post_10_bottomB.png', 'ABA', 'Shape', 'A'],
							  ['post_11_top.png', 'post_11_bottomA.png', 'post_11_bottomB.png', 'BBA', 'Shape', 'B'],
							  ['post_12_top.png', 'post_12_bottomA.png', 'post_12_bottomB.png', 'ABA', 'Color', 'B']]
					 
		self.gen4_set = [	 ['gen4_1_top.png', 'gen4_1_bottomA.png', 'gen4_1_bottomB.png', 'AAAB', 'Color', 'B'],
							 ['gen4_2_top.png', 'gen4_2_bottomA.png', 'gen4_2_bottomB.png', 'AABB', 'Shape', 'B'],
							 ['gen4_3_top.png', 'gen4_3_bottomA.png', 'gen4_3_bottomB.png', 'ABAB', 'Color', 'B'],
							 ['gen4_4_top.png', 'gen4_4_bottomA.png', 'gen4_4_bottomB.png', 'ABBB', 'Shape', 'A'],
							 ['gen4_5_top.png', 'gen4_5_bottomA.png', 'gen4_5_bottomB.png', 'AABB', 'Color', 'A'],
							 ['gen4_6_top.png', 'gen4_6_bottomA.png', 'gen4_6_bottomB.png', 'ABBB', 'Color', 'A'],
							 ['gen4_7_top.png', 'gen4_7_bottomA.png', 'gen4_7_bottomB.png', 'AAAB', 'Shape', 'B'],
							 ['gen4_8_top.png', 'gen4_8_bottomA.png', 'gen4_8_bottomB.png', 'ABAB', 'Color', 'A'],
							 ['gen4_9_top.png', 'gen4_9_bottomA.png', 'gen4_9_bottomB.png', 'AAAB', 'Color', 'A'],
							 ['gen4_10_top.png', 'gen4_10_bottomA.png', 'gen4_10_bottomB.png', 'AABB', 'Shape', 'A'],
							 ['gen4_11_top.png', 'gen4_11_bottomA.png', 'gen4_11_bottomB.png', 'ABBB', 'Shape', 'B'],
							 ['gen4_12_top.png', 'gen4_12_bottomA.png', 'gen4_12_bottomB.png', 'ABAB', 'Shape', 'A'],
							 ['gen4_13_top.png', 'gen4_13_bottomA.png', 'gen4_13_bottomB.png', 'AAAB', 'Shape', 'A'],
							 ['gen4_14_top.png', 'gen4_14_bottomA.png', 'gen4_14_bottomB.png', 'AABB', 'Color', 'B'],
							 ['gen4_15_top.png', 'gen4_15_bottomA.png', 'gen4_15_bottomB.png', 'ABAB', 'Shape', 'A'],
							 ['gen4_16_top.png', 'gen4_16_bottomA.png', 'gen4_16_bottomB.png', 'ABBB', 'Color', 'B']]
							 
		
		self.gencon_set = [  ['gencon_1_top.png', 'gencon_1_bottomA.png', 'gencon_1_bottomB.png', 'ABB', 'Color', 'B'],
							 ['gencon_2_top.png', 'gencon_2_bottomA.png', 'gencon_2_bottomB.png', 'AAB', 'Color', 'B'],
							 ['gencon_3_top.png', 'gencon_3_bottomA.png', 'gencon_3_bottomB.png', 'ABA', 'Shape', 'B'],
							 ['gencon_4_top.png', 'gencon_4_bottomA.png', 'gencon_4_bottomB.png', 'BBA', 'Shape', 'B'],
							 ['gencon_5_top.png', 'gencon_5_bottomA.png', 'gencon_5_bottomB.png', 'AAB', 'Shape', 'A'],
							 ['gencon_6_top.png', 'gencon_6_bottomA.png', 'gencon_6_bottomB.png', 'BBA', 'Shape', 'A'],
							 ['gencon_7_top.png', 'gencon_7_bottomA.png', 'gencon_7_bottomB.png', 'ABB', 'Color', 'B'],
							 ['gencon_8_top.png', 'gencon_8_bottomA.png', 'gencon_8_bottomB.png', 'ABA', 'Shape', 'B'],
							 ['gencon_9_top.png', 'gencon_9_bottomA.png', 'gencon_9_bottomB.png', 'ABB', 'Shape', 'A'],
							 ['gencon_10_top.png', 'gencon_10_bottomA.png', 'gencon_10_bottomB.png', 'AAB', 'Color', 'A'],
							 ['gencon_11_top.png', 'gencon_11_bottomA.png', 'gencon_11_bottomB.png', 'BBA', 'Color', 'B'],
							 ['gencon_12_top.png', 'gencon_12_bottomA.png', 'gencon_12_bottomB.png', 'ABA', 'Color', 'B'],
							 ['gencon_13_top.png', 'gencon_13_bottomA.png', 'gencon_13_bottomB.png', 'ABA', 'Color', 'A'],
							 ['gencon_14_top.png', 'gencon_14_bottomA.png', 'gencon_14_bottomB.png', 'AAB', 'Shape', 'B'],
							 ['gencon_15_top.png', 'gencon_15_bottomA.png', 'gencon_15_bottomB.png', 'ABA', 'Color', 'A'],
							 ['gencon_16_top.png', 'gencon_16_bottomA.png', 'gencon_16_bottomB.png', 'BBA', 'Shape', 'B']]
			
				 
		self.training_set = [ ['training1.png', 
								['training_1_1_top.png', 'training_1_1_bottomA.png', 'training_1_1_bottomB.png', 'AAB', 'Color', 'A'],
								['training_1_2_top.png', 'training_1_2_bottomA.png', 'training_1_2_bottomB.png', 'AAB', 'Color', 'B']],
								
								['training2.png', 
								['training_2_1_top.png', 'training_2_1_bottomA.png', 'training_2_1_bottomB.png', 'ABA', 'Shape', 'B'],
								['training_2_2_top.png', 'training_2_2_bottomA.png', 'training_2_2_bottomB.png', 'ABA', 'Shape', 'A']],
								
								['training3.png', 
								['training_3_1_top.png', 'training_3_1_bottomA.png', 'training_3_1_bottomB.png', 'ABB', 'Color', 'A'],
								['training_3_2_top.png', 'training_3_2_bottomA.png', 'training_3_2_bottomB.png', 'ABB', 'Color', 'B']],
								
								['training4.png', 
								['training_4_1_top.png', 'training_4_1_bottomA.png', 'training_4_1_bottomB.png', 'BBA', 'Shape', 'B'],
								['training_4_2_top.png', 'training_4_2_bottomA.png', 'training_4_2_bottomB.png', 'BBA', 'Shape', 'A']],
								
								['training5.png', 
								['training_5_1_top.png', 'training_5_1_bottomA.png', 'training_5_1_bottomB.png', 'AAB', 'Shape', 'B'],
								['training_5_2_top.png', 'training_5_2_bottomA.png', 'training_5_2_bottomB.png', 'AAB', 'Shape', 'A']],
								
								['training6.png', 
								['training_6_1_top.png', 'training_6_1_bottomA.png', 'training_6_1_bottomB.png', 'ABA', 'Color', 'A'],
								['training_6_2_top.png', 'training_6_2_bottomA.png', 'training_6_2_bottomB.png', 'ABA', 'Color', 'B']],
								
								['training7.png', 
								['training_7_1_top.png', 'training_7_1_bottomA.png', 'training_7_1_bottomB.png', 'ABB', 'Shape', 'B'],
								['training_7_2_top.png', 'training_7_2_bottomA.png', 'training_7_2_bottomB.png', 'ABB', 'Shape', 'A']],
								
								['training8.png', 
								['training_8_1_top.png', 'training_8_1_bottomA.png', 'training_8_1_bottomB.png', 'BBA', 'Color', 'A'],
								['training_8_2_top.png', 'training_8_2_bottomA.png', 'training_8_2_bottomB.png', 'BBA', 'Color', 'B']],
								
								['training9.png', 
								['training_9_1_top.png', 'training_9_1_bottomA.png', 'training_9_1_bottomB.png', 'AAB', 'Color', 'A'],
								['training_9_2_top.png', 'training_9_2_bottomA.png', 'training_9_2_bottomB.png', 'AAB', 'Color', 'B']],
								
								['training10.png', 
								['training_10_1_top.png', 'training_10_1_bottomA.png', 'training_10_1_bottomB.png', 'ABA', 'Shape', 'B'],
								['training_10_2_top.png', 'training_10_2_bottomA.png', 'training_10_2_bottomB.png', 'ABA', 'Shape', 'B']],
								
								['training11.png', 
								['training_11_1_top.png', 'training_11_1_bottomA.png', 'training_11_1_bottomB.png', 'ABB', 'Color', 'A'],
								['training_11_2_top.png', 'training_11_2_bottomA.png', 'training_11_2_bottomB.png', 'ABB', 'Color', 'A']],
								
								['training12.png', 
								['training_12_1_top.png', 'training_12_1_bottomA.png', 'training_12_1_bottomB.png', 'BBA', 'Shape', 'B'],
								['training_12_2_top.png', 'training_12_2_bottomA.png', 'training_12_2_bottomB.png', 'BBA', 'Shape', 'B']],
								
								['training13.png', 
								['training_13_1_top.png', 'training_13_1_bottomA.png', 'training_13_1_bottomB.png', 'AAB', 'Shape', 'A'],
								['training_13_2_top.png', 'training_13_2_bottomA.png', 'training_13_2_bottomB.png', 'AAB', 'Shape', 'B']],
								 
								['training14.png', 
								['training_14_1_top.png', 'training_14_1_bottomA.png', 'training_14_1_bottomB.png', 'ABA', 'Color', 'A'],
								['training_14_2_top.png', 'training_14_2_bottomA.png', 'training_14_2_bottomB.png', 'ABA', 'Color', 'A']],
								
								['training15.png', 
								['training_15_1_top.png', 'training_15_1_bottomA.png', 'training_15_1_bottomB.png', 'ABB', 'Shape', 'B'],
								['training_15_2_top.png', 'training_15_2_bottomA.png', 'training_15_2_bottomB.png', 'ABB', 'Shape', 'A']],
								
								['training16.png', 
								['training_16_1_top.png', 'training_16_1_bottomA.png', 'training_16_1_bottomB.png', 'BBA', 'Color', 'A'],
								['training_16_2_top.png', 'training_16_2_bottomA.png', 'training_16_2_bottomB.png', 'BBA', 'Color', 'B']]]

							
		self.transfer_set = [['transfer_1_top.png', 'transfer_1_bottomA.png', 'transfer_1_bottomB.png', 'transfer_1_bottomC.png', 'transfer_1_bottomD.png', 'ABAB', 'Color', 'B'],
							 ['transfer_2_top.png', 'transfer_2_bottomA.png', 'transfer_2_bottomB.png', 'transfer_2_bottomC.png', 'transfer_2_bottomD.png', 'AABB', 'Color', 'A'],
							 ['transfer_3_top.png', 'transfer_3_bottomA.png', 'transfer_3_bottomB.png', 'transfer_3_bottomC.png', 'transfer_3_bottomD.png', 'ABAB', 'Shape', 'C'],
							 ['transfer_4_top.png', 'transfer_4_bottomA.png', 'transfer_4_bottomB.png', 'transfer_4_bottomC.png', 'transfer_4_bottomD.png', 'AAAB', 'Shape', 'D'],
							 ['transfer_5_top.png', 'transfer_5_bottomA.png', 'transfer_5_bottomB.png', 'transfer_5_bottomC.png', 'transfer_5_bottomD.png', 'ABBB', 'Color', 'A'],
							 ['transfer_6_top.png', 'transfer_6_bottomA.png', 'transfer_6_bottomB.png', 'transfer_6_bottomC.png', 'transfer_6_bottomD.png', 'ABAB', 'Color', 'B'],
							 ['transfer_7_top.png', 'transfer_7_bottomA.png', 'transfer_7_bottomB.png', 'transfer_7_bottomC.png', 'transfer_7_bottomD.png', 'ABBB', 'Shape', 'C'],
							 ['transfer_8_top.png', 'transfer_8_bottomA.png', 'transfer_8_bottomB.png', 'transfer_8_bottomC.png', 'transfer_8_bottomD.png', 'AABB', 'Shape', 'D']]

							 


	#-------------------------------------------------------------
	# record_subj:
	# This allows the subject number to be input at the start of the experiment
	#-------------------------------------------------------------
	def record_subj(self, text_prompt):
		background = self.clear_screen(white)

		last_txtbox_value = None
		txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt=text_prompt)
		# main loop!

		while 1:
			# events for txtbx
			events = pygame.event.get()
			# update txtbx
			txtbx.update(events, background)
			# blit txtbx on the sceen

			if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break

			if(txtbx.value != last_txtbox_value):
			
				self.update_display(background)
				txtbx.draw(background)
				self.update_display(background)
				last_txtbox_value = txtbx.value

		return last_txtbox_value

	#------------------------------------------------------------
	# show_instructions:
	# displays instruction screens
	#------------------------------------------------------------
	def show_instructions(self, filename, butfn, butfn2):
		background = self.show_centered_image(filename, white)
		self.screen.blit(background, (0,0))
		self.button = NextButton(760, 725, 265, 50, self.resources[butfn],self.resources["buttonpress.wav"], self)
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
	# final_screen:
	# displays the final screen at the end of the experiment
	#------------------------------------------------------------
	def final_screen(self):
	
		background = self.clear_screen(white)
	
		end_text = "Thanks for playing the game!"
		self.place_text_image(background, end_text, 32, 0, -100, black, white)
	
		end_text2= "Experimenter: press 'shift  ~' to close the experiment"
		self.place_text_image(background, end_text2, 32, 0, 50, black, white)
	
		# output time exp finished to the end of the datafile
		self.output_trial([(datetime.datetime.now().ctime())])
	
		self.update_display(background)
	
		while 1:
			res = self.get_response()
	
	#------------------------------------------------------------
	# draw_buttons:
	# creates the clickable creature buttons
	#------------------------------------------------------------
	def draw_buttons(self, left_image, right_image, mysurf):
	
		self.buttons = []
	
	
		#(self, x, y, w, h, id, myimage, myimagepressed, snd, presstime, app):
		self.buttons = self.buttons + [RespButton(self.locations[0][0], self.locations[0][1], 360, 160, 'A', self.resources[left_image], self.resources[left_image], self.resources["buttonpress.wav"], 100, self)]
		self.buttons = self.buttons + [RespButton(self.locations[1][0], self.locations[1][1], 360, 160, 'B', self.resources[right_image], self.resources[right_image], self.resources["buttonpress.wav"], 100, self)]
	
		for i in self.buttons:
			i.draw(mysurf)
		
	# EDIT THIS FOR TRANSFER TASK
	#------------------------------------------------------------
	# draw_test_buttons:
	# creates the clickable choice options for the final test phase
	#------------------------------------------------------------
	def draw_transfer_buttons(self, image_set, mysurf):

		# randomize locations of the five choice options
	
		 #(self, x, y, w, h, id, myimage, myimagepressed, snd, presstime, app):
		self.buttons = []
		self.buttons = self.buttons + [RespButton(self.transfer_locations[0][0], self.transfer_locations[0][1], 75, 75, 'A', self.resources[image_set[0]], self.resources[image_set[0]],self.resources["buttonpress.wav"], 100, self)]
		self.buttons = self.buttons + [RespButton(self.transfer_locations[1][0], self.transfer_locations[1][1], 75, 75, 'B', self.resources[image_set[1]], self.resources[image_set[1]],self.resources["buttonpress.wav"], 100, self)]
		self.buttons = self.buttons + [RespButton(self.transfer_locations[2][0], self.transfer_locations[2][1], 75, 75, 'C', self.resources[image_set[2]], self.resources[image_set[2]],self.resources["buttonpress.wav"], 100, self)]
		self.buttons = self.buttons + [RespButton(self.transfer_locations[3][0], self.transfer_locations[3][1], 75, 75, 'D', self.resources[image_set[3]], self.resources[image_set[3]],self.resources["buttonpress.wav"], 100, self)]
	
		for i in self.buttons:
			i.draw(mysurf)


	#------------------------------------------------------------
	# redraw_buttons
	#------------------------------------------------------------
	def redraw_buttons(self, mysurf, loc=None):
		for i in self.buttons:
			i.draw(mysurf)

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
				elif event.type == MOUSEBUTTONDOWN:
					#print("here")
					(x,y) = pygame.mouse.get_pos()
					for but in self.buttons:
						if (but.containsPoint(x, y)):
							rescode = but.do(self.screen)
							exit = True
		return rescode

	#------------------------------------------------------------
	# get_click_response_and_rt
	#------------------------------------------------------------
	def get_click_response_and_rt(self):
		time_stamp = pygame.time.get_ticks()
		res = self.get_click_response()
	
		rt = pygame.time.get_ticks() - time_stamp
		return [res, rt]


	#------------------------------------------------------------
	# do_trial:
	# this controls what happens on each trial of the main task
	#------------------------------------------------------------
	def do_trial(self, image_set, part):
	
		top_image = image_set[0]
		left_image = image_set[1]
		right_image = image_set[2]
		pattern_type = image_set[3]
		match_type = image_set[4]
		correct_resp = image_set[5]
		# set up the screen, buttons, meter etc
		background = self.clear_screen(white)
		
#		background.set_colorkey((255,255,255))
	
		self.show_image_add(background, top_image, 0, -90)

		self.draw_buttons(left_image, right_image, background)
		
		text_line1 = "The part that repeats in my pattern is %s because it has" % pattern_type
		
		if pattern_type == 'ABB':
			text_line2 = "one and then two that are different."
			text_line3 = ""
		elif pattern_type == 'BBA':
			text_line2 = "two that are the same and then one that is different."
			text_line3 = ""
		elif pattern_type == 'ABA':
			text_line2 = " one, then one that is different, then one that is the same as the first."
			text_line3 = ""
		elif pattern_type == 'AAB':
			text_line2 = "two and then one that is different."
			text_line3 = ""
		elif pattern_type == 'AAAB':
			text_line2 = "three, then one that is different."
			text_line3 = ""
		elif pattern_type == 'AABB':
			text_line2 = "two of the same and then two that are different."
			text_line3 = ""
		elif pattern_type == 'ABAB':
			text_line2 = "one, one that is different, then one that is the same as the first,"
			text_line3 = "then one that is the same as the second."
		elif pattern_type == 'ABBB':
			text_line2 = "one and then three that are different."
			text_line3 = ""
		
		text_line4 = "Can you make the same kind of pattern from the choices below?"
		
		
		self.place_text_image(background, text_line1, 28, 0, -330, black, white)
		self.place_text_image(background, text_line2, 28, 0, -295, black, white)
		self.place_text_image(background, text_line3, 28, 0, -260, black, white)
		self.place_text_image(background, text_line4, 28, 0, -215, black, white)
		
		
		
		self.update_display(background)
	
		# wait for and collect response
		[res, rt] = self.get_click_response_and_rt()
		#pygame.mouse.set_visible(0)
	
		if res == correct_resp:
			correct = 1
		else:
			correct = 0

		self.update_display(background) 
	
		#pygame.time.wait(100) 
	
		# reset buttons
		#self.redraw_buttons(background)
		#self.update_display(background)
	
		# output results of trial to datafile
		# -key to columns:
		# 		subject number
		#		condition
		#		trial number
		#		part of the experiment
		#		response (0: left, 1: right)
		#		response time
		#		correct: 1, incorrect: 0
		#		pattern type
		#		match type
		#		example stimulus file
		#		left option stimulus file (or first for transfer)
		#		right option stimulus (second option for transer)
		#		third response image (transfer only)
		#		fourth response image (transfer only)
		self.output_trial([self.subj, self.cond, self.trial, part, res, rt, correct, pattern_type, match_type, top_image, left_image, right_image, 'NA', 'NA'])
	
		self.trial+=1

		background = self.clear_screen(white)
		self.update_display(background)
		# short intertrial interval
		self.escapable_sleep(500)
		#pygame.mouse.set_visible(1)
	
	#------------------------------------------------------------
	# do_transfer_trial
	# this controls what happens in the final text trials at the end
	#------------------------------------------------------------
	def do_transfer_trial(self, image_set):
	
	
		top_image = image_set[0]
	
		response_images = image_set[1:5]

		pattern_type = image_set[5]
		match_type = image_set[6]
		correct_resp = image_set[7]
	
		pygame.mouse.set_visible(1)
		background = self.clear_screen(white)
	
		# display the creature
		self.show_image_add(background, top_image, 0, -90)
	
		# display the response options
		self.draw_transfer_buttons(response_images, background)
		
		text_line1 = "The part that repeats in my pattern is %s because it has" % pattern_type
		
		if pattern_type == 'ABB':
			text_line2 = "one and then two that are different."
			text_line3 = ""
		elif pattern_type == 'BBA':
			text_line2 = "two that are the same and then one that is different."
			text_line3 = ""
		elif pattern_type == 'ABA':
			text_line2 = " one, then one that is different, then one that is the same as the first."
			text_line3 = ""
		elif pattern_type == 'AAB':
			text_line2 = "two and then one that is different."
			text_line3 = ""
		elif pattern_type == 'AAAB':
			text_line2 = "three, then one that is different."
			text_line3 = ""
		elif pattern_type == 'AABB':
			text_line2 = "two of the same and then two that are different."
			text_line3 = ""
		elif pattern_type == 'ABAB':
			text_line2 = "one, one that is different, then one that is the same as the first,"
			text_line3 = "then one that is the same as the second."
		elif pattern_type == 'ABBB':
			text_line2 = "one and then three that are different."
			text_line3 = ""
		
		text_line4 = "Can you fill in the blank?"
		
		
		self.place_text_image(background, text_line1, 28, 0, -330, black, white)
		self.place_text_image(background, text_line2, 28, 0, -295, black, white)
		self.place_text_image(background, text_line3, 28, 0, -260, black, white)
		self.place_text_image(background, text_line4, 28, 0, -215, black, white)
	
		# Display text
	#        img_text = "If you picked this creature, how much candy do you think you'd get?"
	#        self.place_text_image(background, img_text, 36, 0, 75, white, black)
		
		self.update_display(background)
	
		# wait for and get the response
		[res, rt] = self.get_click_response_and_rt()
		#pygame.mouse.set_visible(0)
	
		if res == correct_resp:
			correct = 1
		else:
			correct = 0
	
	#        background = self.clear_screen(black)
		self.update_display(background)
	
		# output results of trial to datafile
		# -key to columns:
		# 		subject number
		#		condition
		#		trial number
		#		part of the experiment
		#		response (0: left, 1: right)
		#		response time
		#		correct: 1, incorrect: 0
		#		pattern type
		#		match type
		#		example stimulus file
		#		left option stimulus file (or first for transfer)
		#		right option stimulus (second option for transer)
		#		third response image (transfer only)
		#		fourth response image (transfer only)
		self.output_trial([self.subj, self.cond, self.trial, 'transfer', res, rt, correct, pattern_type, match_type, top_image, response_images[0], response_images[1], response_images[2], response_images[3]])
	
		self.trial+=1
	
		background = self.clear_screen(white)
		self.update_display(background)
		# short intertrial interval
		self.escapable_sleep(500)
		#pygame.mouse.set_visible(1)
	
	#------------------------------------------------------------
	# do_regular_exp
	# this coordinates the experiment as a whole
	#------------------------------------------------------------
	def do_regular_exp(self):

		# show the instructions
		stage = 1

		# there will be more instruction screens
		while(stage!=5):
			if stage == 1:
				self.show_instructions('WarmUp1.png','next.gif', None)
				stage = 2
			elif stage == 2:
				if self.show_instructions('WarmUp2.png','next.gif', 'back.gif')==BACK:
					stage = 1
				else:
					stage = 3
			elif stage == 3:
				if self.show_instructions('WarmUp3.png','next.gif', 'back.gif')==BACK:
					stage = 2
				else:
					stage = 4
			elif stage == 4:
				if self.show_instructions('WarmUp4.png','begin.gif', 'back.gif')==BACK:
					stage = 3
				else:
					stage = 5

		# set up the screen in preparation for the task
		background = self.clear_screen(white)


 		for trial in self.pretest_set:
 			self.do_trial(trial, 'pretest')
 		
 		for train_trial in self.training_set:
 			self.show_instructions(train_trial[0],'next.gif', None)
			self.do_trial(train_trial[1], 'training')
 			self.do_trial(train_trial[2], 'training')
 		
 		for trial in self.posttest_set:
 			print trial
 			self.do_trial(trial, 'posttest')
 		
 		for trial in self.gen4_set:
 			self.do_trial(trial, 'gen-4')
 		
 		for trial in self.gencon_set:
 			self.do_trial(trial, 'gencon')
		
		for transfer_trial in self.transfer_set:
			self.do_transfer_trial(transfer_trial)
	

# 		self.show_instructions('end-instructions.png','next.gif', None)
		# display the final screen
		self.final_screen()

#-------------------------------------------------------------
# main                   
#-------------------------------------------------------------
def main():
    global laptop, experimentname;
    experiment = ExplDevExp(laptop, screenres, experimentname)
    experiment.do_regular_exp()

#------------------------------------------------------------
# let's start
#------------------------------------------------------------
if __name__ == '__main__':
    main()
