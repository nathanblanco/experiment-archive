Alien Device experiment code:

This an experiment that looks at categorization in a decision-making context.
It uses gabors as stimuli. There are three parts. First a decision-making task where
participants are not told that the stimuli actually fit into two categories that determine
rewards. The second part has similarity judgments to look for secondary effects of learning
the categories. In the third part we tell them that there were actually categories
and see if they learned them.

This code utilizes the PyPsyExp (http://gureckislab.org/pypsyexp/sphinx/;
https://github.com/NYUCCL/PyPsyExp) framework which is included in the /lib folder. 
Running the experiment requires Python 2.x, Numpy, and Pygame. To start the experiment 
run the driver.py file. This code was written and used to collect data sometime around 2014.

Guide to the various files and folders:

data                  --folder where data from the experiment is stored
data_questionaires    --folder where questionnaire data is stored
driver.py             --open this to run the experiment. runs the questionnaires, than the experiment code
exp.py                --has the code for the actual experiment
eztext.py             --code for inputting things in text boxes
images                --folder that has the images needed for the experiment
lib                   --this contains the PyPsyExp library that has a lot of useful code for python experiments
pairings.py           --has a list used in the experiment for one of the parts
patterncode.txt       --this is used for automatically managing subject numbers and conditions
                        (it is not currently used here)
                        first row is current condition, second is total number of conditions,
                        third is current subject number.
questionaires.py      --the code that runs the questionnaires
sounds                --folder that contains the sound files needed
text.py               --someone else's code that i use for instructions sometimes (I don't think it's used here at all)
transfer_set.py       --has a list used in the experiment for one of the parts