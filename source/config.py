import numpy as np

from tools import painterTools

painterColors = {'Foreground':  (255, 255, 255), 
                 'Background':  (0, 0, 0), 
                 'Unknown':     (128, 128, 128)}
buttonKeys = 'Undo Run Save Previous Next'.split(' ')

toolKeys = list(painterTools.keys())
toolKeys.sort()
colorKeys = list(painterColors.keys())
colorKeys.sort()

toolTexts = colorKeys + toolKeys + buttonKeys 
