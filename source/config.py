import numpy as np

from tools import painterTools

painterColors = {'Foreground':  (255, 255, 255), 
                 'Background':  (0, 0, 0), 
                 'Unknown':     (128, 128, 128)}
buttonString = 'FillUnknown Undo Save/Run SaveAlpha/Previous Next'
buttonKeys = [s.split(' ') for s in buttonString.split('/')]
commandText = {
    'SaveAlpha': 'Save Alpha',
    'Save': 'Save Trimap',
    'FillUnknown': 'FillUnknown',
    }

def getText(command):
    if command not in commandText:
        return command
    return commandText[command]

toolKeys = list(painterTools.keys())
toolKeys.sort()
colorKeys = list(painterColors.keys())
colorKeys.sort()

toolTexts = [colorKeys, toolKeys] + buttonKeys

blankSize = [10, 40]
for i in range(len(blankSize) - 1)[::-1]:
    blankSize[i + 1] -= blankSize[i]
buttonScale = (100, 50)
buttonCol = 3

imgScale = (400, 300)
imgRow = 3
