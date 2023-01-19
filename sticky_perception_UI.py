

''' STICKY PERCEPTION: SUPPORT FOR PREDICTIVE CODING IN THE UNIFORMITY ILLUSION?

    This code runs an experiment which investigates the effect of perceptual
    'stickiness' following exposure to the uniformity illusion
    
    You can read my thesis here to get more information about the experiment: 
        LINK 
    
    Code & study design by Nina Fitzmaurice 
    Contact: ninafitzmaurice@gmail.com 
    
    Citation APA
    N.B. Fitzmaurice, Sticky Perception in the Uniformity Illusion, (2022), 
    GitHub repository, access link
 '''

import psychopy.visual
from psychopy.visual import Aperture
import psychopy.event
import psychopy.tools
from psychopy.tools import monitorunittools
from psychopy import monitors
import numpy as np
import random 
from  psychopy.iohub import launchHubServer
from psychopy import gui
from psychopy import data
import pandas as pd
import os

# This code runs the uniformity illusion with delayed central stimuli updating
#### Nina Fitzmaurice thesis project 2022

## Conditions: 
# Experimental = UI (also acts as control as the illusion does not consistently occur)
# control = short latency of stimuli (optional, can be removed)
# control = catch trial illusion forced (optional, can be removed) 


# saves to new folder 'data', new patch to child dir 
current_dir = os.path.dirname(os.path.abspath(__file__))
new_dir = current_dir + os.sep + u'Nina_UI_Data'
# create directory
if os.path.isdir(new_dir) == False:
    os.mkdir(new_dir)

# change to new dir
os.chdir(new_dir)

print('new dir to save data to:     ', os.getcwd())

experiment_name = 'Uniformity_illusion'

info = {'Participant_nr': 'xxx'}
dlg = gui.DlgFromDict(dictionary=info, title=experiment_name)

if dlg.OK == False:
    psychopy.core.quit()

sub_ID = info['Participant_nr']
info['date'] = data.getDateStr()

filename = '%s_%s_%s.csv' % (info['Participant_nr'], 
            experiment_name, info['date'])

test_filename = '%s_%s_%s_%s.csv' % (info['Participant_nr'], 
            experiment_name,'TEST_', info['date'])


# live updating into txt file as back up: 
# Open a file with access mode 'a'
# so it can be appended 
backUp = open(filename+'_backUp.txt', 'a+')


###############################################################

#### EXPERIMENT PARAMS
# ignore this 
#10.6 = short latency trial duration estimate
#15.6 = longer dur trials
# 156 % 3 == 0 
# 156 trials will last around 32 mins
# 12 trials per stimuli (13 unique stimuli in total)

## SET AS DESIRED 
# duration of stimuli (secs)
exp_stim_duration = 8
# short latency catch stimuli duration
catch_duration = 2
# duration of mask (secs)
mask_duration = 0.1
# inter stim noise duration (secs) = for noise btw centre change and REPRODUCTION
inter_stim_dur = 1
# inter TRIAL duration (secs) = for noise btwn TRIALS
inter_trial_dur = 1.5

# number of trials
# ok this is a mess, I will probably change it later right now I cant be bothered
# will result in uneven number of control and experimental conditions
# I dont think its a huge deal?? 
# IMPORTANT!!! every trial % 3 == 0 will be a SHORT LATENCY CATCH TRIAL
# ----------------- ONLY FOR NON UI CATCH TRIALS
# N trials must % 3 == 0!! So 1/3 of trials are short latenct catch trials
n_trials = 9
if n_trials % 3 != 0:
    raise Exception("n_trials % 3 MUST = 0!")
# 16 stimuli to test, so 13/156 = trials per stimuli
# n_trials /= 16


## SCALE - work out for different aspect ratios
# I tried to do this automatically but psychopy is annoying so this is how it is
# preserves scaling of the stimuli
# my aspect ratio = 16:9
# so, scaling = 9/16
# you might also need to adjust the number of dots per row and col in the stimuli to 
# make it look better on different ratios but that code is later 
scale = 0.563


#### QUIT KEY
# quit key to abort study at any time
quit_key = 'q'

def quit_key_pressed():
    win.close()

psychopy.event.globalKeys.add(quit_key, quit_key_pressed)

## WINDOW
win = psychopy.visual.Window(
    #size=[1368, 912],
    size=[1368/2, 912/2],
    allowStencil=True,
    units='pix',
    fullscr=True,
    color=[-1, -1, -1],
    monitor = monitors.Monitor('samplingExperiment'))


####################################################

## Setting up the eyetracker, uncomment if needed 
#iohub_config = {
#    'eyetracker.hw.sr_research.eyelink.EyeTracker':{
#        'name': 'tracker',
#        'model_name': 'EYELINK 1000 DESKTOP',
#        'calibration': {
#            'auto_pace': False,
#            'screen_background_color': [75,75,75]
#            },
#        'runtime_settings': {
#            'sampling_rate': 500,
#            'track_eyes': 'RIGHT'
#            }
#        
#        }
#    }
#
#iohub_config['eyetracker.hw.sr_research.eyelink.EyeTracker']['default_native_data_file_name']= ('NINA' + '%s' % (info['Participant_nr']))
#iohub_config['eyetracker.hw.sr_research.eyelink.EyeTracker']['simulation_mode'] = False
#io = launchHubServer(window = win, **iohub_config)
#tracker = io.devices.tracker

#################################################################

# not ideal, couldnt get the others to work smoothly
# feel free to change it but then you must remove scaling in the whole script,
# I think 
win.units = 'norm' 

## MOUSE
myMouse = psychopy.event.Mouse(visible=True)
# [0] = left, [1] = wheel in the middle is pressed, [2], right
# leftClick, wheelClick, rightClick = myMouse.getPressed()

## APERTURE:
# experimental only 
aperture = psychopy.visual.Aperture(win, size= (0.97,1), pos=(0,0), shape='square', 
    inverted=False, units=None)
    
# for demo only
demo_aperture = psychopy.visual.Aperture(win, size= (0.3,0.3), pos=(0,-0.475), shape='square', 
    inverted=False, units=None)


# aperture should be off initially 
aperture.enabled = False
demo_aperture.enabled = False


####### STIMULI COORDINATES

def make_stim_coords(STIM_TYPE, x_circles, y_circles, x_start, x_end, y_start, y_end):
    # normalisation = length of x, y = 2
    # set step size from point x/y start to x/y end
    x_len =  abs(x_start) + abs(x_end)
    #print('x len: ',x_len)
    # if negative y start coord, then convert both to pos values and 
    # subract smaller from bigger (to get distance between points)
    if y_start < 0:
        y_len =  round(abs(y_end) - abs(y_start), 1)
        
    elif y_start > 0 and y_end < 0:
        y_len = round(y_start + abs(y_end), 1)
    
    #print('y len ', y_len)
    
    x_step = x_len/x_circles
    y_step = y_len/y_circles
    
    # coords for circles, upper left to lower right
    if STIM_TYPE == 'colour':
        x_coords = np.array(np.arange(x_start, x_end + x_step, x_step))
        y_coords = np.array(np.arange(y_start, y_end, -1*y_step))
    else: 
        x_coords = np.array(np.arange(x_start, x_end, x_step))
        y_coords = np.array(np.arange(y_start, y_end, -1*y_step))
    #print(x_coords)
    #print(y_coords)
    # makes coordinate grid
    coords = np.array(np.meshgrid(x_coords, y_coords)).T.reshape(-1, 2)
    
    if STIM_TYPE == 'size':
        # for the shift of rows.......
        x = np.empty((x_circles)) # number of rows (y coords in meshgrid)
        x[::2] = 0 # for every odd row = every x coord is 0
        x[1::2] = 0.7* x_step # for every odd row = every x coord is half x step
        y = np.zeros((y_circles)) # for every instance of x, the y coord is 0 
        
        # formatt in same way as coords 
        shift = np.array(np.meshgrid(y, x)).T.reshape(-1, 2)
        shift = np.fliplr(shift)
        
        # add n to every x coord on the yth row
        coords_shifted = shift + coords
        
        # dots will be shifted over!! 
        
        return coords_shifted
    
    elif STIM_TYPE == 'colour':
        # dots will NOT be shifted over!! 
        return coords
    

## TO CUSTOMISE 
# args: STIM_TYPE, x_circles, y_circles, x_start, x_end, y_start, y_end

# STIM_TYPE = for size or colour stim
#   size stim = coords will be shifted 
#   colour stim = coords will not be shifted 

# x_circles MUST BE EVEN 
# y_circles MUST BE EVEN

# values are normalised!!

# coordinates for the mini demo in instructions
coords_demo_periph = make_stim_coords('colour', 10,8,-0.3,0.3,-0.2,-0.75)
coords_demo_cent = make_stim_coords('colour', 10,8,-0.3,0.3,-0.2,-0.75)

# coordinates for experimental stimuli grids/element arrays
coords_colour = make_stim_coords('colour', 18,12,-0.95,0.975,0.95,-1.05)
coords_size = make_stim_coords('size', 18,12,-0.95,0.975,0.95,-1.05)


## DEMO ELEMENT ARRAY
# makes a grid of dots like the experimental stimuli but with fewer params
def demo_stimuli_grid(coords, size, R,G,B):
    grid = psychopy.visual.ElementArrayStim(win, units = None,
    nElements=len(coords), sizes=size,
    xys=coords, elementTex=None, elementMask = 'circle')
    
    grid.colors = [R,G,B]
    grid.sizes *= [scale,1]
    
    return grid

## DEMO STIMULI can customise 
demo_cent = demo_stimuli_grid(coords_demo_periph, 0.045,0,1,0)
demo_periph = demo_stimuli_grid(coords_demo_cent, 0.045,1,0,0)


## STIMULI ELEMENT ARRAY
# makes grid of stimuli
# opacity 
# sizes = size of elements 
# mask = gaussian blur, circle, other feature if you want  
# RGB = colour 
# orientation = orientation of each element 
def stimuli_grid(coordinates, opacity, sizes, mask, orientation, R,G,B):
    
    grid = psychopy.visual.ElementArrayStim(win, units = None,
        nElements=len(coordinates), sizes=sizes,
        xys=coordinates, elementTex=None, elementMask = mask)
    
    grid.colors = [R,G,B]
    grid.colorSpace='rgb'
    grid.sizes *= [scale,1]
    
    grid.opacities = opacity
    
    if orientation == 'rand': 
        # possible orientations from 0 deg to 80 deg
        rotation = np.arange(0,80,1)
        # assigns random orientation in range above for each element 
        grid.oris = np.random.choice(rotation, len(coords_shifted), replace=True)
    else:
        grid.oris = orientation
    
    # I removed fringe width because it wasn't blury enough, but code is here incase
    # change of mind or someone wants to use it
#    if mask == 'raisedCos':
#        grid.maskParams = {'fringeWidth': fw}
    
    return grid


## NOISE
noiseTexture = np.random.rand(300, 300) * 2.0 - 1
noise = psychopy.visual.GratingStim(win, tex=noiseTexture,
        size=(2,2), units='norm',
        interpolate=False, autoLog=False)


## STIMULI VALUES
# Size
small = 0.06
big = 0.09
repro_size = small+((big-small)/2)
colour_stim_size = 0.1


## BLOCKS list of block types 
# easy to customise
block_list = ['centFill_RT','centFill_Repro','blackOut']

## STIMULI TRIALS, for participants to practice before experiment starts
# customise values for the stimuli grid in the stimuli dicts
# stimuli_grid(coordinates, opacity, sizes, mask, orientation, R,G,B)
CF_test_stim_list = [
            # centre small periph big
            {'Trial': {'Cent': stimuli_grid(coords_size,1,small,'circle',0,1,1,0),
                        'Periph': stimuli_grid(coords_size,1,big,'circle',0,1,1,0), 
                        'Cent_new': stimuli_grid(coords_size,1,big,'circle',0,1,1,0),
                        'Repro': stimuli_grid(coords_size,1,repro_size,'circle',0,1,1,0),
                        'Condition': ['Exp', 'Cent_big'],
                        'Name': 'Size'}},
            
            # exp 001 
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,0,1),
                        'Condition': ['Exp', '001'],
                        'Name': 'Colour'}}
                        
                        ]

BO_test_stim_list = [
            # exp 010 blackOut
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,1,0),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,1,0),
                        'Condition': ['Exp', '010', 'blackOut'],
                        'Name': 'Colour'}},
            
            # exp 001 blackOut
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,0,1),
                        'Condition': ['Exp', '001', 'blackOut'],
                        'Name': 'Colour'}}
                        ]

## EXPERIMENT for data collection 
## STIMULI centFill
centFill_stim_list = [

    # CREATING STIMULI:
    # opacity = x, size = x, mask = x, orientation = x, R = x, G = x, B = x
            
            ## SIZE
            # centre big periph small
            {'Trial': {'Cent': stimuli_grid(coords_size,1, big,'circle',0,1,1,0),
                        'Periph': stimuli_grid(coords_size,1,small,'circle',0,1,1,0), 
                        'Cent_new': stimuli_grid(coords_size,1,small,'circle',0,1,1,0),
                        # for reproduction task = size between small and big!
                        'Repro': stimuli_grid(coords_size,1,repro_size,'circle',0,1,1,0),
                        'Condition': ['Exp', 'Cent_small'],
                        'Name': 'Size'}},
            
            # centre small periph big
            {'Trial': {'Cent': stimuli_grid(coords_size,1,small,'circle',0,1,1,0),
                        'Periph': stimuli_grid(coords_size,1,big,'circle',0,1,1,0), 
                        'Cent_new': stimuli_grid(coords_size,1,big,'circle',0,1,1,0),
                        'Repro': stimuli_grid(coords_size,1,repro_size,'circle',0,1,1,0),
                        'Condition': ['Exp', 'Cent_big'],
                        'Name': 'Size'}},
            
            # diff too big for illusion 
            # eh I didnt use this in the end, kinda messy but hey ho do what you will with it
            {'Trial': {'Cent': stimuli_grid(coords_size,1,0.03,'circle',0,1,1,0),
                        'Periph': stimuli_grid(coords_size,1,0.09,'circle',0,1,1,0), 
                        'Cent_new': stimuli_grid(coords_size,1,0.09,'circle',0,1,1,0),
                        'Repro': stimuli_grid(coords_size,1,repro_size,'circle',0,1,1,0),
                        'Condition': ['Exp', 'no_UI'],
                        'Name': 'Size'}},
            
            # Catch trial
            # stimuli gets BIGGER to match big centre during catch trial 
            {'Trial': {'Cent': stimuli_grid(coords_size,1,big,'circle',0,1,1,0),
                        'Periph': stimuli_grid(coords_size,1,small,'circle',0,1,1,0), 
                        'Cent_new': stimuli_grid(coords_size,1,big,'circle',0,1,1,0),
                        # for reproduction task = size between small and big!
                        'Repro': stimuli_grid(coords_size,1,repro_size,'circle',0,1,1,0),
                        'Condition': ['Catch'],
                        'Name': 'Size'}},
            
            ## COLOUR
            # Condition value is the colour of the centre
            # exp 010
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,1,0),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,1,0),
                        'Condition': ['Exp', '010'],
                        'Name': 'Colour'}},
            
            # exp 001
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,0,1),
                        'Condition': ['Exp', '001'],
                        'Name': 'Colour'}},
            
            # exp 101
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0.91,0.78,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0.91,0.78,0),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,1,0,1),
                        'Condition': ['Exp', '101'],
                        'Name': 'Colour'}},
            
            # Catch trials
            # Catch 001
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7),
                        'Catch': stimuli_grid(coords_colour,0,colour_stim_size,'circle',0,0,0,1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,0,1),
                        'Condition': ['Catch', '001'],
                        'Name': 'Colour'}},
            
            # Catch 010
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,1,0),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0),
                        'Catch': stimuli_grid(coords_colour,0,colour_stim_size,'circle',0,0,1,0),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,1,0),
                        'Condition': ['Catch', '010'],
                        'Name': 'Colour'}},
            
            # Catch 101
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0.91,0.78,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0.91,0.78,0),
                        'Catch': stimuli_grid(coords_colour,0,colour_stim_size,'circle',0,1,0,1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,1,0,0),
                        'Condition': ['Catch', '101'],
                        'Name': 'Colour'}}#,

## made these stimuli didnt use them, the code to run them might be broken if you chose to
## add them in be aware it may not be so smooth I dont remember 
#            # Orientation
#            
#            {'Trial': {'Cent': stimuli_grid(0.07,'circle',0,0,0,1),
#                        'Periph': stimuli_grid(0.07,'circle',0,1,0,0), 
#                        'Cent_new': stimuli_grid(0.07,'circle',0,1,0,0),
#                        'Condition': ['Exp', '001'],
#                        'Name': 'Ori'}},
#                        
#                        {'Trial': {'Cent': stimuli_grid(0.07,'circle',0,0,0,1),
#                        'Periph': stimuli_grid(0.07,'circle',0,1,0,0), 
#                        'Cent_new': stimuli_grid(0.07,'circle',0,1,0,0),
#                        'Condition': ['Exp', '001'],
#                        'Name': 'Ori'}},
#                        
#                        {'Trial': {'Cent': stimuli_grid(0.07,'circle',0,0,0,1),
#                        'Periph': stimuli_grid(0.07,'circle',0,1,0,0), 
#                        'Cent_new': stimuli_grid(0.07,'circle',0,1,0,0),
#                        'Condition': ['Exp', '001'],
#                        'Name': 'Ori'}},

#            # Donuts
#            # centre donut periph circle
#            {'Trial': {'Cent': stimuli_grid(1,0.07,'circle',0,1,1,1),
#                        'Cent_2': stimuli_grid(1,0.03,'circle',0,0,0,0),
#                        'Periph': stimuli_grid(1,0.07,'circle',0,1,1,1),
#                        'Cent_2_new': stimuli_grid(1,0.07,'circle',0,1,1,1), 
#                        'Condition': ['Exp', 'Cent_donut'],
#                        'Name': 'Donut'}},
#            
#            # centre circle periph donut
#            {'Trial': {'Cent': stimuli_grid(1,0.07,'circle',0,1,1,1),
#                        'Periph': stimuli_grid(1,0.07,'circle',0,1,1,1), 
#                        'Periph_2': stimuli_grid(1,0.03,'circle',0,0, 0, 0), 
#                        'Cent_2_new': stimuli_grid(1,0.03,'circle',0,0, 0, 0), 
#                        'Condition': ['Exp', 'Periph_donut'],
#                        'Name': 'Donut'}},
#            
#            # Catch trail
#            {'Trial': {'Cent': stimuli_grid(1,0.07,'circle',0,1,1,1),
#                        'Cent_2': stimuli_grid(1,0.03,'circle',0,0, 0, 0),
#                        'Periph': stimuli_grid(1,0.07,'circle',0,1,1,1), 
#                        'Periph_2': stimuli_grid(1,0,'circle',0,0, 0, 0),
#                        'Cent_2_new': stimuli_grid(1,0.03,'circle',0,0, 0, 0),
#                        'Condition': ['Catch'],
#                        'Name': 'Donut'}}
            
             ]

## STIMULI blackOut
blackOut_stim_list = [
    # CREATING STIMULI:
    # opacity = x, size = x, mask = x, orientation = x, R = x, G = x, B = x
        
            # Centre black out trials
            # exp 010 blackOut
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,1,0),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,1,0),
                        'Condition': ['Exp', '010', 'blackOut'],
                        'Name': 'Colour'}},
            
            # exp 001 blackOut
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,0,1),
                        'Condition': ['Exp', '001', 'blackOut'],
                        'Name': 'Colour'}},
            
            # exp 101 blackOut
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0.91,0.78,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,1,0,1),
                        'Condition': ['Exp', '101', 'blackOut'],
                        'Name': 'Colour'}},
            
            # Catch trials
            # Catch 001
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,0.75,0.7), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Catch': stimuli_grid(coords_colour,0,colour_stim_size,'circle',0,0,0,1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,0,1),
                        'Condition': ['Catch', '001','blackOut'],
                        'Name': 'Colour'}},
            
            # Catch 010
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0,1,0),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Catch': stimuli_grid(coords_colour,0,colour_stim_size,'circle',0,0,1,0),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,0,1,0),
                        'Condition': ['Catch', '010','blackOut'],
                        'Name': 'Colour'}},
            
            # Catch 101
            {'Trial': {'Cent': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,1,0,1),
                        'Periph': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,0.91,0.78,0), 
                        'Cent_new': stimuli_grid(coords_colour,1,colour_stim_size,'circle',0,-1,-1,-1),
                        'Catch': stimuli_grid(coords_colour,0,colour_stim_size,'circle',0,1,0,1),
                        'Repro': stimuli_grid(coords_colour,0.5,colour_stim_size,'circle',0,1,0,0),
                        'Condition': ['Catch', '101','blackOut'],
                        'Name': 'Colour'}}
                        
                        ]


## TEXT STIM & FIXATION & BUTTONS

text_screen = psychopy.visual.TextBox(win,
                         text='q',
                         font_size=32,
                         font_color=[1,1,1],
                         size=(1,1),
                         pos=(0,0.2),
                         grid_horz_justification='centre',
                         units='norm'
                         )

fix = psychopy.visual.TextStim(win, text='+', pos=0, color=[1,1,1],
                                colorSpace ='rgb', opacity=0.5, units='norm', 
                                height=0.09)

welcome = u'''Thank you for participating in this study! 

Please read the instructions carefully.


Press SPACE to see the instructions.'''

#-------------------------

CF_instructions_RT = u'''During each trial you will be shown different visual illusions. Maintain fixation on the central fixation cross while viewing the illusions.

After a few seconds of viewing the illusion, the centre of the screen is going to change. Maintain fixation during this change.

LEFT CLICK the mouse when all the dots on the screen look the same:'''

CF_instructions_REPRO_a = u'''During each trial you will be shown different visual illusions. Maintain fixation on the central fixation cross while viewing the illusions.

After a few seconds of viewing the illusion, the centre of the screen is going to change. Maintain fixation on the cross during this change.

Example:'''

BO_instructions_a = u'''During each trial you will be shown different visual illusions. Maintain fixation on the central fixation cross while viewing the illusions.

After a few seconds of viewing the illusion, the centre of the screen is going to black out. Maintain fixation on the cross during this change.

Example:'''

#------------------------

CF_instructions_REPRO_b = u'''A few seconds after the centre changes, a new screen will appear.

Try to re-create the stimuli you saw in the periphery AFTER the centre changed.

SCROLL the mouse to change the features of the stimuli. Try this out now!'''

BO_instructions_b = u'''A few seconds after the centre blacks out, a new screen will appear.

Try to re-create the stimuli you saw in the periphery AFTER the centre went blank.

SCROLL the mouse to change the features of the stimuli. Try this out now!'''

start_eyetracking = u'''The experimenter will set up the eyetracker now. '''

#------------------------

start_test_trials = u'''Press SPACE to start practice trials'''

test_trials_complete = u'''Test trials completed!

Press SPACE to start the experiment.'''

start_of_block = u'''starting block...'''

end_of_block = u'''This block has ended.

Take a break, youre doing great!'''

end_of_experiment = '''Thank you for your time, the experiment is complete!'''


## STRUCTURE PER TRIAL
''' kinda a mess T_T 
this function will run each trial in the stim list through the trial format

1. centre is different to periphey, and UI occurs or not (includes catch trials)
1.a. if participant left click = reports seeing the UI, no click = reports
     didnt see the UI 

2. the centre changes to match the periphery, waits for click from 
particpant (indicated when they see the illusory periphery destablise). 
2.a. RT at time of click is stored
2.b. there is NOT timeout! wait until participant reports uniformity 

3. a noise grating to mask any retinal after-effects (at least a bit) 

4. REPRODUCTION TASK: only the periphery is visible, scroll wheel to change 
attributes of the periphery to match the illusory perception. left click
to submit choice '''


def RUN_TRIALS(trials, block, blockNumber, trialNumber):
    # SEND MESSAGE TO EYE TRACKER
    # tracker.sendMessage(f'''block {block} {blockNumber} starts''')
    
    ### LATENCY & UI CATCH TRIALS
    '''MESS MESS MESS - I will change this at some point
    for now its ok
    
    making sure that a random 1/3 of all trials are latency catch
     and that 1/3 of the UI catch trials are run rather than all of them
     NOTE = it is set up this way because the UI catch trials are in the stimuli
           dicts (stim_lists) but the latency catches are not. 
           UI catch must also be 1/3 of trials or the trial split would
           not be even. 
           this code will make sure only a random 1/3 of UI catch trials run!
    
     1. make dict with all trial indexes as the keys
     2. randomly select 1/3 of trials from each index and 
        add this random 1/3rd of trials to the dict.
        i.e.     dict = {'1':[2,4,7],'2':[5,11,3]...}'''
    catch_reps = {}
    # if not trial blocks...
    if blockNumber != 'NaN':
        # for every trial type in the stim list 
        for i in range(1,len(trials.trialList)+1): 
            # add trial index as a key in the dict
            if i not in catch_reps:
                # for each index that is not in the list, make a new key
                # and append random 1/3 of trials to that list
                catch_reps[i] = np.random.choice(np.arange(1,n_trials+1), 
                                                        int(n_trials/3), replace=False)
    
    skipped_counter = 0
    
    for trial in trials:
        #tracker.setRecordingState(True)
        
        # 1. setting up trial....
            
        # 1.a.
        # organising number of trials that are catch trials
        ## LATENCY & UI CATCH TRIALS NEW VERSION
        # 2/3rds of trials are a latency or UI catch 
        # excluding trial blocks 
        # part of the aforementioned mess
        if blockNumber != 'NaN':
            if 'Catch' in trial['Trial']['Condition']:
                # if thisRepN in dict[trial index]
                #        this rep N is saved to dict as a catch trial
                if trials.thisRepN+1 in catch_reps.get(trials.thisIndex+1):
                    stim_duration = exp_stim_duration
                    data['Catch_latency'].append(0)
                    
                elif trials.thisRepN+1 not in catch_reps.get(trials.thisIndex+1):
                    skipped_counter += 1
                    #print('SKIPPED ',trials.thisN, trial['Trial']['Condition'])
                    #trials.next()
                    #print('trial n before continue: ', trials.thisN)
                    continue
                    
            elif 'Catch' not in trial['Trial']['Condition']:
                # LATENCY CATCH
                if trials.thisRepN+1 in catch_reps.get(trials.thisIndex+1):
                    stim_duration = catch_duration
                    data['Catch_latency'].append(1)
                    
                elif trials.thisRepN+1 not in catch_reps.get(trials.thisIndex+1):
                    stim_duration = exp_stim_duration
                    data['Catch_latency'].append(0)
                    
        else:
            stim_duration = exp_stim_duration
            data['Catch_latency'].append(0)
            
#-----------------------------------------------------------------------
#          ignore 
#        ## LATENCY CATCH TRIALS: OLD VERSION === NOT RANDOMISED
#        # each trial INDEX (the trial identifier) is appended to a list
#        # ---- to keep track of how many times each trial was completed
#        # every third trial will be a short latency catch trial
#        # IF n trials % 3 == 0!!!
#        # THIS EXCLUDES FORCED UI CATCH TRIALS
#        complete_trials.append(trials.thisIndex+1)
#        #print('count   ', complete_trials.count(trials.thisIndex))
#        if complete_trials.count(trials.thisIndex+1) % 3 == 0:
#            if not 'Catch' in trial['Trial']['Condition']:
#                #print('MODULOOOO 3')
#                stim_duration = catch_duration
#                data['Catch_latency'].append(1)
#                data['Catch_UI'].append(0)
#            else:
#                stim_duration = exp_stim_duration
#                data['Catch_latency'].append(0)
#        else:
#            stim_duration = exp_stim_duration
#            data['Catch_latency'].append(0)
#--------------------------------------------------------------------
        
        # ONLY THE TRIALS RAN!!
        trialNumber += 1
        
        ## saving trial related data 
        # sub ID
        data['Sub_ID'].append(sub_ID)
        # +1 bc python indexing starts at 0
        # rep number
        data['Rep_n'].append(trials.thisRepN+1)
        # block number
        data['Block_n'].append(blockNumber)
        # block type (centFill or blackOut or test)
        data['Block_type'].append(block)
        # trial number out of total trials 
        data['Trial_n'].append(trialNumber)
        # trial number out of current repeat
        data['Trial_Rep_n'].append(trials.thisTrialN+1)
        # index of trial 
        data['Trial_index'].append(trials.thisIndex+1)
        # the name of the stimuli group 
        data['Stimuli'].append(trial['Trial']['Name'])
        # more details about the stimuli condition in string 
        data['Condition'].append(trial['Trial']['Condition'])
        
        # these values are saved to compare the reproduction task values to
        # colour = compare repro opacity to actual opacity (100% opace)
        if trial['Trial']['Name'] == 'Colour':
            data['Cent_opacity'].append(1)
        else:
            # not import for size trials
            data['Cent_opacity'].append('NaN')
        
        # compare the repro values to these values
        # these values match the centre values for each stimuli
        if trial['Trial']['Name'] == 'Size': 
            if 'Cent_small' in trial['Trial']['Condition']:
                data['Cent_size'].append(big)
                
            elif  'Cent_big' in trial['Trial']['Condition']:
                data['Cent_size'].append(small)
                
            elif 'no_UI' in trial['Trial']['Condition']:
                data['Cent_size'].append(0.03)
                
            elif 'Catch' in trial['Trial']['Condition']:
                data['Cent_size'].append(big)
        else:
            data['Cent_size'].append('NaN')
            
        
        if 'Exp' in trial['Trial']['Condition']:
            data['Exp'].append(1)
        else:
            data['Exp'].append(0)
        
        if 'Catch' in trial['Trial']['Condition']:
            data['Catch_UI'].append(1)
        else:
            data['Catch_UI'].append(0)
        
        
        ### INIT PARAMS FOR CATCH TRIALS
        radius_catch = small
        # the size of the inner circle is set to 0 in catch trial
        radius_catch_donut = 0
        # set opacity catch to 0 == fully transparent, will increase to 1! 
        opacities_catch = 0
        
        
        ### INIT REPRODUCTION TASK VALUES
        if trial['Trial']['Name'] == 'Size':
            trial['Trial']['Repro'].setSizes(repro_size)
            trial['Trial']['Repro'].sizes *= [scale,1]
            
        if trial['Trial']['Name'] == 'Colour':
            if '010' in trial['Trial']['Condition']:
                trial['Trial']['Repro'].colors = [0,1,0]
            if '001' in trial['Trial']['Condition']:
                trial['Trial']['Repro'].colors = [0,0,1]
            if '101' in trial['Trial']['Condition']:
                trial['Trial']['Repro'].colors = [1,0,1]
        
        timer = psychopy.core.Clock() # sets a clock for each trial 
        

        # NOISE BEFORE EACH TRIAL TO CLEAR EFFECTS OF LAST TRIAL
        while timer.getTime()<inter_trial_dur:
                # remove apature 
                aperture.enabled = False
                noise.phase += (0.01 / 2, 0.005 / 2)
                noise.draw()
                win.flip()
                if timer.getTime()>inter_trial_dur:
                    break
        
        # SEND MESSAGE TO EYE TRACKER
        #tracker.sendMessage(f'''UI: trial index: {trials.thisIndex}. trial n: {trialNumber}, rep: {trials.thisRepN+1}, block: {block}''')
        # 2. running trials...
        while timer.getTime()<stim_duration:
            
            # to report seeing UI 
            mouseClicks = myMouse.getPressed()
            if mouseClicks[0]==1:
                UI_was_seen = True
        
            # draw peripheral stimuli
            aperture.enabled = True
            aperture.inverted= True
            
            # this will select UI CATCH TRIALS (UI forced to occur)
            if 'Catch' in trial['Trial']['Condition']:
                
                if trial['Trial']['Name'] == 'Size':
                    # speed(steps) = distance/time
                    # distance = big-small
                    # time = stim duration
                    radius_catch += ((big-small)/(stim_duration*60))
                    trial['Trial']['Periph'].sizes = radius_catch
                    trial['Trial']['Periph'].sizes *= [scale,1]
                    trial['Trial']['Periph'].draw()
                
                elif trial['Trial']['Name'] == 'Donut':
                    # speed(steps) = distance/time
                    # distance = from 0 to 0.03
                    # time = stim duration
                    trial['Trial']['Periph'].draw()
                    radius_catch_donut += (0.03/(stim_duration*60))
                    trial['Trial']['Periph_2'].sizes = radius_catch_donut
                    trial['Trial']['Periph_2'].sizes *= [scale,1]
                    trial['Trial']['Periph_2'].draw()
                    
                elif trial['Trial']['Name'] == 'Colour':
                    trial['Trial']['Periph'].draw()
                    # this will slowly increase the opacity of the second periphery:
                    # same values as centre and repro
                    opacities_catch += (1/(stim_duration*60)) # from one to 0 over the duration of the stimuli
                    trial['Trial']['Catch'].opacities = opacities_catch
                    trial['Trial']['Catch'].draw()
            
            # draw the double periph stimuli for donut condition
            elif 'Exp' and 'Periph_donut' in trial['Trial']['Condition']:
                trial['Trial']['Periph'].draw()
                trial['Trial']['Periph_2'].draw()
            
            # periphery for all other conditions
            elif 'Exp'and not 'Periph_donut' in trial['Trial']['Condition']:
                trial['Trial']['Periph'].draw()            
            
            # draw central stimuli for all trials OTHER than donut_cent
            aperture.inverted= False
            trial['Trial']['Cent'].draw()
            
            # for the donut conditions = because needs to draw second central stimuli
            # donut catch trial AND donut_cent need dobould stimuli drawn in centre
            if trial['Trial']['Name'] == 'Donut':
                if 'Catch' in trial['Trial']['Condition'] or 'Cent_donut' in trial['Trial']['Condition']:
                    trial['Trial']['Cent_2'].draw()
            
            # flip to window 
            win.flip()
            
            # after set time, win cleared
            if timer.getTime()>stim_duration:
                win.flip()
                run = False
                break
        
        # append in data file if UI was reported or not
        if UI_was_seen == True:
            data['Uniformity'].append(1)
        else:
            data['Uniformity'].append(0)
        
        # MSG TO EYETRACKER
        #tracker.sendMessage(f'''MASK: trial index: {trials.thisIndex}. trial n: {trialNumber}, rep: {trials.thisRepN+1}, block: {block}''')
        # MASK = short blank before centre change to prevent 
        # effects of movement/change on the retina in the centre only
        timer.reset()
        while timer.getTime()<(mask_duration):
            win.flip()
            
            if timer.getTime()>=(mask_duration): 
                break
        
        # SEND MESSAGE TO EYE TRACKER
        #tracker.sendMessage(f'''CENTRE CHANGE: trial index: {trials.thisIndex}. trial n: {trialNumber}, rep: {trials.thisRepN+1}, block: {block}''')
        # 3. centre change 
        # CENTRE CHANGE = the central stimuli drawn match the periphery 
        # this while loop includes the reproduction task because I made a mess
        # I am too lazt to fix it so just dont touch anything 
        myMouse.clickReset()
        run_centre_change = True
        # so the reproduction task doesnt start to run before mouse click 
        run_repro = False 
        # TIMER FOR REACTIONS TIMES
        RT_timer = psychopy.core.Clock()
        while run_centre_change and timer.getTime()>=mask_duration:
            # re-draw peripheral stimuli
            aperture.enabled = True
            aperture.inverted= True
            
            # draws the same periphery as before 
            trial['Trial']['Periph'].draw()
            # only for Donut conditions: 
            # incl catch and periph_donut because they both need a double centre 
            if trial['Trial']['Name'] == 'Donut':
                if 'Catch' in trial['Trial']['Condition'] or 'Periph_donut' in trial['Trial']['Condition']:
                    trial['Trial']['Periph_2'].draw()
            
            # draw central stimuli 
            aperture.inverted= False
            # for all other stimuli types
            if trial['Trial']['Name'] != 'Donut':
                trial['Trial']['Cent_new'].draw()
            
            if trial['Trial']['Name'] == 'Donut':
                trial['Trial']['Cent'].draw()
                trial['Trial']['Cent_2_new'].draw()
            
            win.flip()
            
            mouseClicks = [0]
            if block == 'centFill_RT':
                mouseClicks = myMouse.getPressed()
            # SET DURATION FOR BLACKOUT AND CENTFILL_REPRO TRIALS
            elif block == 'blackOut' or block == 'centFill_Repro':
                psychopy.core.wait(1.7)
                mouseClicks[0] = 1
                # SEND MESSAGE TO EYE TRACKER
                #tracker.sendMessage(f'''CENT CHANGE TIMEOUT: trial index: {trials.thisIndex}. trial n: {trialNumber}, rep: {trials.thisRepN+1}, block: {block}''')
            
            if mouseClicks[0]==1:
                # NO RT for black out trials, no uniformity reoccurs
                # NP RT for repro cent fill, set duration 
                if block == 'blackOut' or block =='centFill_Repro':
                    data['RT'].append('NaN')
                elif block == 'centFill_RT':
                    # SEND MESSAGE TO EYE TRACKER
                    #tracker.sendMessage(f'''RT CENT CHANGE:  trial index: {trials.thisIndex}. trial n: {trialNumber}, rep: {trials.thisRepN+1}, block: {block}''')
                    data['RT'].append(round(RT_timer.getTime(),4))
                
                # so RT timer doesnt run in back
                RT_timer = None
                # reset timer for inter stim noise grating
                timer.reset()
                
                # after click, noise grating shown
                while timer.getTime()<inter_stim_dur:
                    if block == 'centFill_Repro' or block == 'blackOut':
                        # remove apature 
                        aperture.enabled = False
                        noise.phase += (0.01 / 2, 0.005 / 2)
                        noise.draw()
                        win.flip()
                    elif block == 'centFill_RT':
                    # SKIPS THE NOISE BETWEEN REPRO CENT CHANGE
                        data['Reproduction'].append('NaN')
                        break
                        
                # when the timer exceeds the noise stim duration (specified at
                # start of script) then reset mouse clicks and init reproduction
                # task by setting run_repro to TRUE and run_centre_change to FALSE
                # This way the loops do not over-ride eachother, and kinda resolves my mess
                if timer.getTime()>=inter_stim_dur:
                    if block == 'centFill_Repro' or block =='blackOut':
                        myMouse.clickReset()
                        run_repro = True
                        run_centre_change = False
                    elif block == 'centFill_RT':
                        run_repro = False
            
            # REPRODUCTION TASK
            # ONLY the periph is drawn up
            # scroll wheel changes the stimuli attributes of the periphery and
            # draws to screen, participant clicks right mouse to submit
            aperture.enabled = True
            aperture.inverted= True
            myMouse.clickReset()
            psychopy.event.clearEvents('mouse')
            
            while run_repro and timer.getTime()>inter_stim_dur:
                # to exit reproduction task left click
                leftClick_repro = myMouse.getPressed()[0]
                ## SCROLL UP = Negative
                ## SCROLL DOWN = Positive
                scroll = myMouse.getWheelRel()[1]
                # uses reproduction task element of stimulus dict
                # can scroll up and down to change size uptil reaching limits
                # limits = big and small stimuli +/-0.005 (bit of overshoot)
                
                if scroll < 0:
                    ## SIZE INCREASE
                    if trial['Trial']['Name'] == 'Size':
                        trial['Trial']['Repro'].sizes += [(0.002*scale),0.002]
                        if trial['Trial']['Repro'].sizes[1,1] > (big + 0.005):
                            trial['Trial']['Repro'].sizes -= [(0.002*scale),0.002]
                    
                    ## COLOUR opacity INCREASE
                    elif trial['Trial']['Name'] == 'Colour':
                            trial['Trial']['Repro'].opacities += 0.02
                            if trial['Trial']['Repro'].opacities[1] > 1:
                                trial['Trial']['Repro'].opacities -= 0.02
                
                elif scroll > 0:
                    ## SIZE DECREASE
                    if trial['Trial']['Name'] == 'Size':
                        trial['Trial']['Repro'].sizes -= [(0.002*scale),0.002]
                        if trial['Trial']['Repro'].sizes[1,1] < (small - 0.005):
                            trial['Trial']['Repro'].sizes += [(0.002*scale),0.002]
                    
                    ## COLOUR opacity DECREASE
                    elif trial['Trial']['Name'] == 'Colour':
                            trial['Trial']['Repro'].opacities -= 0.02
                            if trial['Trial']['Repro'].opacities[1] < 0:
                                trial['Trial']['Repro'].opacities += 0.02
                
                #trial['Trial']['Repro'].sizes *= [scale,1]
                
                if trial['Trial']['Name'] == 'Colour':
                    trial['Trial']['Periph'].draw()
                
                trial['Trial']['Repro'].draw()
                win.flip()
                
                
                if (leftClick_repro):
                    # append data of final reproduction to dataframe
                    if trial['Trial']['Name'] == 'Size':
                        data['Reproduction'].append(trial['Trial']['Repro'].sizes[1,1])
                    elif trial['Trial']['Name'] == 'Colour':
                        data['Reproduction'].append(trial['Trial']['Repro'].opacities[1])
                    
                    run_repro = False
        
        ## EYE TRACKER RECORDING FOR THIS TRIAL DONE
        #tracker.setRecordingState(False)
        
        ### BACK UP DATA - live updating to txt file
        # make list of current trial data
        new_data_row = []
        # for every key in the data dict, append a new value
        for key in data:
        #for key in wtf_trial_numbers:
            # for the other trials: for key in keys, get the number 
            # in each list appended to they keys that 
            # corresponds to the current trial number 
            # INDEXING STARTS AT 0 AND TRIALS START AT 1!!!
            # so TRIAL NUMBER - 1
            #new_data_row.append(wtf_trial_numbers[key][trialNumber-1])
            new_data_row.append(data[key][trialNumber-1])
        
        # Append new line to txt file
        new_data_row = ",".join(map(str, new_data_row))
        backUp.write(str(new_data_row)+"\n")
        
        # clear window
        win.flip()
        myMouse.clickReset()
        


## INIT DATA FRAME

data = {'Sub_ID':[],'Block_n':[],'Block_type': [],'Trial_n':[],'Trial_Rep_n':[],
        'Rep_n':[], 'Trial_index':[],'Stimuli':[],'Condition':[],'Exp':[],
        'Catch_UI':[], 'Catch_latency':[],'Cent_size':[],'Cent_opacity':[],
        'RT':[],'Reproduction':[],'Uniformity':[]}

# headers to txt file
backUp.write (str(list(data.keys()))+'\n')

# making a df
df = pd.DataFrame(data)


#### EXPERIMENT STRUCTURE 
# Button for demos
instructions_button = psychopy.visual.Rect(win, width=0.2, height=0.1, 
                            units='norm', fillColor=[1,1,1], 
                            fillColorSpace='rgb', pos=(0.7,-0.7), size=None)


instructions_button_text = psychopy.visual.TextBox(win,
                         text='Ok, got it!',
                         font_size=30,
                         font_color=[0,0,0],
                         background_color=None,
                         size=(0.2,0.1),
                         pos=(0.7,-0.7),
                         grid_horz_justification='centre',
                         units='norm'
                         )


myMouse.clickReset()
experiment_run = True
START = True

while experiment_run:
    # instructions 
    # welcome screen, press space tp start experiment 
    if START == True:
        text_screen.setText(welcome) 
        text_screen.draw()
        win.flip()
        psychopy.event.waitKeys()
        START == False
    
    # block counter 
    block_n = 0
    
    # for every clock in the list of blocks (3 blocks) 
    for block in block_list:
        win.setMouseVisible(True)
        
        block_n += 1
        
        instructions_1 = True
        instructions_2 = False
        demo_run = True
        demo_timer = psychopy.core.Clock()
        
        while demo_run == True: 
            while instructions_1 == True:
                # instructions 1 + centre change demo
                if block == 'centFill_Repro' or block == 'blackOut':
                    keys = psychopy.event.getKeys(keyList=['space'])
                    demo_aperture.enabled = True
                    demo_aperture.inverted= True
                elif block == 'centFill_RT': 
                    demo_aperture.enabled = False
                    keys = None
                
                # TEXT
                # for centre fill blocks, set the instructions 
                if block == 'centFill_RT': 
                    text_screen.setText(CF_instructions_RT) 
                # for black out blocks, set the instructions 
                elif block == 'centFill_Repro': 
                    text_screen.setText(CF_instructions_REPRO_a)
                # for black out blocks, set the instructions 
                elif block == 'blackOut': 
                    text_screen.setText(BO_instructions_a)
                    
                text_screen.draw()
                instructions_button.draw()
                instructions_button_text.draw()
                
                # draw periph
                if demo_timer.getTime() < 7:
                    demo_periph.draw()
                
                # CENTRE STIMULI CHANGE + PERIPH CHANGE 
                # first centre drawn 
                # ONLY REPRO AND BLACKOUT cent change
                if block == 'centFill_Repro' or block == 'blackOut':
                    demo_aperture.inverted= False
                    if demo_timer.getTime() < 4:
                        demo_cent.draw()
                    # draw new central stimuli
                    elif demo_timer.getTime() > 4 and demo_timer.getTime() < 7:
                        # for filled centre 
                        if block == 'centFill_Repro': 
                            demo_periph.draw()
                        # for black out centre 
                        elif block == 'blackOut':
                            demo_cent.opacities = 0
                            demo_cent.draw()
                    # reset timer and opaicites
                    elif demo_timer.getTime() > 7.5:
                        demo_periph.opacities = 1
                        demo_cent.opacities = 1
                        demo_timer.reset()
                
                win.flip()
                
                if (keys):
                    instructions_1 = False
                    instructions_2 = True
                    # setting opacities to 1
                    demo_periph.opacities = 1
                    # set opacity of overlay color for repro task 0.5
                    demo_cent.opacities = 0.5
                elif myMouse.isPressedIn(instructions_button, buttons=[0]):
                    demo_timer = None
                    instructions_2 = False
                    instructions_1 = False
                    demo_run = False
                    
            while instructions_2 == True:
                keys = psychopy.event.getKeys(keyList=['space'])
                scroll = myMouse.getWheelRel()[1]
                demo_aperture.inverted= True
                
                # TEXT
                # for centre fill blocks, set the instructions 
                if block == 'centFill_Repro': 
                    text_screen.setText(CF_instructions_REPRO_b) 
                # for black out blocks, set the instructions 
                if block == 'blackOut': 
                    text_screen.setText(BO_instructions_b)
                text_screen.draw()
                instructions_button.draw()
                instructions_button_text.draw()
                
                # draw the background colour
                demo_periph.draw()
                demo_cent.draw()
                
                if scroll < 0:
                    demo_cent.opacities += 0.05
                    #demo_cent.draw()
                    if demo_cent.opacities[1] > 1:
                        demo_cent.opacities -= 0.05
                        #demo_cent.draw()
                
                elif scroll > 0:
                    demo_cent.opacities -= 0.05
                    #demo_cent.draw()
                    if demo_cent.opacities[1] < 0:
                        demo_cent.opacities += 0.05
                        #demo_cent.draw()
                
                demo_aperture.inverted= False
                
                win.flip()
                
                if (keys):
                    demo_timer.reset()
                    instructions_2 = False
                    instructions_1 = True
                    demo_periph.opacities = 1
                    demo_cent.opacities = 1
                elif myMouse.isPressedIn(instructions_button, buttons=[0]):
                    demo_timer = None
                    instructions_2 = False
                    instructions_1 = False
                    demo_run = False
                    
        
        if demo_run == False:
            aperture.enabled = False
            text_screen.setText(start_eyetracking)
            text_screen.draw()
            win.flip()
        psychopy.event.waitKeys()
        
        # EYE TRACKER CALIBRATION
        #tracker.runSetupProcedure()
        
        text_screen.setText(start_of_block)
        text_screen.draw()
        win.flip()
        psychopy.event.waitKeys()
        
        fix.autoDraw = True
        win.setMouseVisible(False)
        
        if block == 'centFill_RT' or block == 'centFill_Repro':
            # RUNS TEST TRIALS FOR BLOCK
            test_trials_CF = psychopy.data.TrialHandler(trialList=CF_test_stim_list, nReps=2, method = 'sequential')
            # trial number starts at 0, will end at 4 after this practice block
            if block == 'centFill_RT':
                RUN_TRIALS(test_trials_CF, block, 'NaN', 0)
            elif block == 'centFill_Repro':
                RUN_TRIALS(test_trials_CF, block, 'NaN', len(data['Reproduction']))
            
            aperture.enabled = False
            # after test trials 
            text_screen.setText(test_trials_complete)
            text_screen.draw()
            win.flip()
            psychopy.event.waitKeys()
            
            trials = psychopy.data.TrialHandler(trialList= centFill_stim_list, nReps=n_trials, method = 'random')
            # next trial number always starts at the current length of the dataframe - 1! 
            RUN_TRIALS(trials, block, block_n, len(data['Reproduction']))
            
            # save dict as df
            df =  pd.DataFrame.from_dict(data)
            # save dataframe as csv
            df.to_csv(filename, index = False, header=True)
            
            
            
            fix.autoDraw = False
            aperture.enabled = False
            # END OF BLOCK BREAK
            text_screen.setText(end_of_block)
            text_screen.draw()
            win.flip()
            psychopy.event.waitKeys()
            
            
            
        elif block == 'blackOut':
            # RUNS TEST TRIALS FOR BLOCK
            test_trials_BO = psychopy.data.TrialHandler(trialList=BO_test_stim_list, nReps=2, method = 'sequential')
            RUN_TRIALS(test_trials_BO, block, 'NaN', len(data['Reproduction']))
            
            # after test trials 
            aperture.enabled = False
            text_screen.setText(test_trials_complete)
            text_screen.draw()
            win.flip()
            psychopy.event.waitKeys()
            
            trials = psychopy.data.TrialHandler(trialList= blackOut_stim_list, nReps=n_trials, method = 'random')
            RUN_TRIALS(trials, block, block_n, len(data['Reproduction']))
            
            # save dict as df
            df =  pd.DataFrame.from_dict(data)
            # save dataframe as csv
            df.to_csv(filename, index = False, header=True)
        
        aperture.enabled = False
        fix.autoDraw = False
    
    # save dict as df
    df =  pd.DataFrame.from_dict(data)
    # save dataframe as csv
    df.to_csv(filename, index = False, header=True)
    # Close the file with live updating
    backUp.close()
    
    # end experiment
    text_screen.setText(end_of_experiment)
    text_screen.draw()
    win.flip()
    psychopy.event.waitKeys()
    
    # is set to true automatically at start 
    # tracker.setConnectionState(False)
    
    experiment_run = False
