import os
import cv2
import random
# dirs = 'closedform  closedform_facetri  deep  deep2  deep2_facetri  deep_facetri  shared  shared_facetri'.split('  ')
# dir_path = [os.path.join('/data2/matting_results_0422', d) for d in dirs]
dir_path = ['/data2/pictureWhite/face-tri-10000-modified/']
dir_path = ['/data2/pictureWhite/images'] + dir_path
dir_path = dir_path + ['/data2/pictureWhite/final_result']
# dir_path = ['/home/wuxian/Aliyun/trimap/face-tri-10000-modified/']
# dir_path = ['/home/wuxian/Aliyun/image'] + dir_path
# dir_path = dir_path + ['/home/wuxian/Aliyun/result10000/UI/']

add = ['{}.jpg', '{}.png', '{}.png']

imgs = [i.split('.')[0] for i in os.listdir(dir_path[1])]
random.shuffle(imgs)
fout = open('../final_list.txt', 'w')
for i in imgs:
    s = []
    for j, ad in zip(dir_path, add):
        img = ad.format(i)
        path = os.path.join(j, img)
        # if not os.path.exists(path):
        #     print(path)
        s.append(path)
        # cv2.imshow(j, cv2.imread(path))
    # cv2.waitKey(0)
    print(' '.join(s), file = fout)
