import cv2
import numpy as np
import torch
from .alpha_net import AlphaNet

MEAN_BGR = np.array([104.00699, 116.66877, 122.67892])


def deep_matting(image, trimap, model, gpu_id=-1):
    image = image.astype(np.float32)
    image -= MEAN_BGR
    image = image.transpose(2, 0, 1)
    image = torch.from_numpy(image)
    image.unsqueeze_(0)

    trimap_0 = np.zeros((trimap.shape[0], trimap.shape[1]))
    trimap_1 = np.zeros((trimap.shape[0], trimap.shape[1]))
    trimap_2 = np.zeros((trimap.shape[0], trimap.shape[1]))
    trimap = trimap[:, :, 0]
    trimap_0[trimap < 5] = 1
    trimap_2[trimap > 250] = 1
    trimap_1 = np.logical_not(np.logical_or(trimap_0, trimap_2))
    trimap_0 = np.expand_dims(trimap_0, axis=0)
    trimap_1 = np.expand_dims(trimap_1, axis=0)
    trimap_2 = np.expand_dims(trimap_2, axis=0)
    trimap = np.concatenate((trimap_0, trimap_1, trimap_2), axis=0)
    trimap = torch.from_numpy(trimap.astype(np.float32))
    trimap.unsqueeze_(0)

    if gpu_id >= 0:
        device = torch.device('cuda:{}'.format(gpu_id))
    else:
        device = torch.device('cpu')
    image = image.to(device)
    trimap = trimap.to(device)

    input = torch.cat((image, trimap), 1)
    output = model.forward(input)
    result = output[0, 0, :, :].cpu().detach().numpy()
    return result * 255

def load_model(model_path, gpu_id=-1):
    if gpu_id >= 0:
        device = torch.device('cuda:{}'.format(gpu_id))
    else:
        device = torch.device('cpu')

    model = AlphaNet()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    model.to(device)
    return model

if __name__ == "__main__":
    image_path = '/data2/pictureWhite/images/800018955.jpg'
    trimap_path = '/data2/pictureWhite/face-tri-10000/800018955.png'
    model_path = '/data2/human_matting/models/deep_models/deepmatting_model2.pth'
    result_path = 'result.png'

    image = cv2.imread(image_path)
    trimap = cv2.imread(trimap_path)
    model = load_model(model_path)
    result = deep_matting(image, trimap, model)
    cv2.imwrite(result_path, result)
