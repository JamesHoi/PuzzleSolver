import cv2
from PIL import Image
import numpy as np
from algorithm.gaps import image_helpers


## 读取图像，解决imread不能读取中文路径的问题
def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img


def cv_imwrite(img, file_path, suffix=".jpg"):
    cv2.imencode(suffix, img)[1].tofile(file_path)


def cv_img2pil(cv_img):
    cv_img2 = cv2.cvtColor(np.uint8(cv_img), cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv_img2)


def pil_img2cv(pil_img):
    return cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)


def save_cv_img(cv_img, directory):
    cv_img2pil(cv_img).save(directory)


def save_combine_cv_img(pieces, rows, columns, directory):
    save_cv_img(image_helpers.assemble_image(pieces, rows, columns), directory)


def save_cv_pieces(cv_pieces, directory):
    for i in range(len(cv_pieces)):
        save_cv_img(cv_pieces[i], directory + "/{}.png".format(i))
