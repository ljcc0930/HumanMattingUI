from tools import painterTools
painterColors = {'Foreground':[255] * 3, 'Background': [0] * 3, 'Unknown': [128] * 3}
toolButtons = 'Undo Run Save Previous Next'.split(' ')
toolTexts = []
for i in painterColors: toolTexts.append(i)
for i in painterTools: toolTexts.append(i)
for i in toolButtons: toolTexts.append(i)
