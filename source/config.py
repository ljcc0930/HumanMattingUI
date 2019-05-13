import numpy as np

from tools import painterTools

painterColors = {'Foreground':  (255, 255, 255), 
                 'Background':  (0, 0, 0), 
                 'Unknown':     (128, 128, 128)}
buttonString = \
'''Foreground Background Unknown
Filler FillerUp|FillerDown FillerSlider- Pen
#Squeeze #FillUnknown #UnknownUp|#UnknownDown Undo Save
Run SaveAlpha
SplitUp|SplitDown ShowGrid UndoAlpha
Previous Next'''
buttonKeys = [[tool.split('|') for tool in block.split(' ')] for block in buttonString.split('\n')]
commandText = {
    'SaveAlpha': 'Save Alpha',
    'Save': 'Save Trimap',
    'FillUnknown': 'Fill Unknown',
    'FillerUp': 'Filler+',
    'FillerDown': 'Filler-',
    'FillerUpTen': 'Filler+10',
    'FillerDownTen': 'Filler-10',
    'UnknownUp': 'Unknown+',
    'UnknownDown': 'Unknown-',
    'SplitUp': 'Split Up',
    'SplitDown': 'Split Down',
    'ShowGrid': 'Show Grid',
    'UndoAlpha': 'Undo Alpha',
    }

def getText(command):
    if command not in commandText:
        return command
    return commandText[command]

toolKeys = list(painterTools.keys())
toolKeys.sort()
colorKeys = list(painterColors.keys())
colorKeys.sort()

toolTexts = buttonKeys

blankSize = [10, 40]
defaultBlank = 5

for i in range(len(blankSize) - 1)[::-1]:
    blankSize[i + 1] -= blankSize[i]
buttonScale = (100, 50)
buttonCol = 3

imgScale = (400, 300)
imgRow = 3

defaultSplit = 3
