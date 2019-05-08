import numpy as np
from scipy import signal


kernel1 = np.array([[-1, 0, 1],
                    [-2, 0, 2],
                    [-1, 0, 1]]).astype('float') / 12
kernel2 = np.array([[-1, -2, -1],
                    [0, 0, 0],
                    [1, 2, 1]]).astype('float') / 12

def conv2d(img, k, pad = 0):
    d = img.ndim
    r = list(range(d))
    img = img.transpose(r[2:] + r[:2])
    def dfs(img):
        if img.ndim == 2:
            return signal.convolve2d(img, k, boundary='fill', mode='same', fillvalue = pad)
        else:
            a = []
            for i in img:
                a.append(dfs(i))
            return np.stack(a, axis = 0)
    ret = dfs(img)
    return ret.transpose(r[-2:] + r[:-2])

def calcGradient(img):
    gradx = conv2d(img, kernel1)
    grady = conv2d(img, kernel2)
    grad = (gradx ** 2 + grady ** 2).sum(axis = 2) ** 0.5
    grad[0] = grad[1]
    grad[-1] = grad[-2]
    grad[:, 0] = grad[:, 1]
    grad[:, -1] = grad[:, -2]
    return grad

def floodFill(flag, theta, start):
    assert flag.ndim == 2
    flag = flag < theta
    f = flag.copy()
    N, M = flag.shape[:2]
    d = [start]
    def vis(x, y):
        if flag[x, y]:
            flag[x, y] = False
            d.append((x, y))
    while len(d) > 0:
        x, y = d.pop()
        if x > 0:
            vis(x - 1, y)
        if y > 0:
            vis(x, y - 1)
        if x + 1 < N:
            vis(x + 1, y)
        if y + 1 < M:
            vis(x, y + 1)
    return np.logical_not(np.logical_xor(flag, f))

def fillUnknown(self, width):
    #TODO
    pass
