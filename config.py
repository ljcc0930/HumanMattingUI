from tools import painterTools
painterColors = {'Foreground':[255] * 3, 'Background': [0] * 3, 'Unknown': [128] * 3}
buttonKeys = 'Undo Run Save Previous Next'.split(' ')

toolKeys = list(painterTools.keys())
toolKeys.sort()

colorKeys = list(painterColors.keys())
colorKeys.sort()

toolTexts = colorKeys + toolKeys + buttonKeys 
