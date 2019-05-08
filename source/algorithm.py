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

def squeeze(img, FBU = False):
    img = img.astype('float')

    B = img ** 2
    F = (255 - img) ** 2
    while(B.ndim > 2):
        B = B.sum(axis = 2)
        F = F.sum(axis = 2)
    F = F < 10
    B = B < 10
    if FBU:
        U = np.logical_not(np.logical_or(F, B))
        return F, B, U

    F = F.astype('int')
    B = B.astype('int')

    img = (F * (255 - 128) + 128 - B * 128).astype('uint8')
    return np.stack([img] * 3, axis = 2)


def fillUnknown(img, width, in_flag = True):
    if width == 0:
        return squeeze(img)
    F, B, U = squeeze(img, FBU = True)

    a = np.zeros(F.shape).astype('bool')

    plr1 = np.logical_and(F[1:], B[:-1])
    plr2 = np.logical_and(B[1:], F[:-1])
    plr = np.logical_or(plr1, plr2)
    pud1 = np.logical_and(F[:, 1:], B[:, :-1])
    pud2 = np.logical_and(B[:, 1:], F[:, :-1])
    pud = np.logical_or(pud1, pud2)

    a[1:] = np.logical_or(a[1:], plr)
    a[:-1] = np.logical_or(a[:-1], plr)
    a[:, 1:] = np.logical_or(a[:, 1:], pud)
    a[:, :-1] = np.logical_or(a[:, :-1], pud)

    for it in range(width - 1):
        b = a.copy()
        b[1:] = np.logical_or(b[1:], a[:-1])
        b[:-1] = np.logical_or(b[:-1], a[1:])
        b[:, 1:] = np.logical_or(b[:, 1:], a[:, :-1])
        b[:, :-1] = np.logical_or(b[:, :-1], a[:, 1:])
        a = b

    U = np.logical_or(a, U)
    B = np.logical_and(B, np.logical_not(U))
    F = np.logical_and(F, np.logical_not(U))

    img = (F * (255 - 128) + 128 - B * 128).astype('uint8')
    return np.stack([img] * 3, axis = 2)

if __name__ == "__main__":
    inputPaths = [
        '/data2/pictureWhite/floodfill-mask/811956505.png',
        '/data2/pictureWhite/images/811956505.jpg',
        '/data2/pictureWhite/floodfill-mask/806843743.png',
        '/data2/pictureWhite/images/806843743.jpg',
        '/data2/pictureWhite/floodfill-mask/802786318.png',
        '/data2/pictureWhite/images/802786318.jpg',
        '/data2/pictureWhite/floodfill-mask/804069429.png',
        '/data2/pictureWhite/images/804069429.jpg',
        '/data2/pictureWhite/floodfill-mask/816466402.png',
        '/data2/pictureWhite/images/816466402.jpg',
    ]

    for inputPath in inputPaths:
        import cv2
        img = cv2.imread(inputPath)
        cv2.imshow('img', img)
        cv2.imshow('squeeze', squeeze(img))
        img = fillUnknown(img, width = 1)
        cv2.imshow('fill', img)
        cv2.waitKey(0)
