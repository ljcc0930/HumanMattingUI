import numpy as np

from tools import painterTools

painterColors = {'Foreground':  (255, 255, 255), 
                 'Background':  (0, 0, 0), 
                 'Unknown':     (128, 128, 128)}
buttonString = \
'''ImageAlphaSlider-
Foreground Background Unknown
Filler FillerUp|FillerDown * FillerSlider- * * Pen
#Squeeze SolveForeground FillUnknown UnknownUp|UnknownDown
Undo Save
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
    'SolveForeground': 'Clean Trimap'
    }

def getText(command):
    if command not in commandText:
        return command
    return commandText[command]

sliderConfig = {
"ImageAlphaSlider":     (0, 1, "continuous"),
"FillerSlider":         (1, 250, "log")
}


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

imgScale = (750, 475)
imgRow = 1

defaultSplit = 3

background = np.ones([20, 20, 3]).astype("uint8") * 255
background[:10, :10] = 128
background[10:, 10:] = 128

def getBackground(size):
    bh, bw = background.shape[:2]
    h, w = size[:2]
    dh = (h - 1) // bh + 1
    dw = (w - 1) // bw + 1
    line = np.concatenate([background] * dw, axis = 1)
    bg = np.concatenate([line] * dh, axis = 0)[:h, :w]
    return bg
