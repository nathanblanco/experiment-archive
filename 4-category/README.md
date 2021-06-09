Four-category learning task code:

This code runs an experiment in which participants learn to classify items into four 
categories. The category members are defined based on the values of two continuous-value
dimensions. The four categories were created by sampling from multivariate normal distributions
with different means. The category structure used is sometimes referred to as an 
information-integration structure. Surface features can either be lines of different length
and orientation, or gabor patches of different spatial frequency and orientation. The 
experiment  runs several questionnaires prior to the main task.

This code utilizes the PyPsyExp (http://gureckislab.org/pypsyexp/sphinx/;
https://github.com/NYUCCL/PyPsyExp) framework which is included in the /lib folder. 
Running the experiment requires Python 2.x, Numpy, and Pygame. To start the experiment 
run the driver.py file. This code was written around 2014/2015.