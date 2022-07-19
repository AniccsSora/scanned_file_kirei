import cv2
from PIL import Image, ImageOps
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

def make_hist(np_image):
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    #
    axs[0].set_title("linear-y")
    n, _, patches = axs[0].hist(np_image.reshape(-1), bins=256);
    #
    axs[1].set_title("log-y")
    n, _, patches = axs[1].hist(np_image.reshape(-1), bins=256);
    plt.yscale('log')
    #
    plt.suptitle("Grey Histogram", fontsize=18)
    plt.tight_layout()
    plt.savefig("Grey Histogram.png", dpi=1200)


def make_hist_3ch(pil_image, vline=[]):
    """
    :param pil_image: PIL image
    :param vline (List): 要繪製的垂直線之 x number.[大於零的數字]
    :return: 畫圖
    """
    r = pil_image.histogram()[0:0 + 256]
    g = pil_image.histogram()[256:256 + 256]
    b = pil_image.histogram()[512:512 + 256]

    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    axs[0].plot(r, color='#FF0000')
    axs[0].plot(g, color='#00FF00')
    axs[0].plot(b, color='#0000FF')
    #
    axs[1].plot(r, color='#FF0000')
    axs[1].plot(g, color='#00FF00')
    axs[1].plot(b, color='#0000FF')
    for vln in vline:
        axs[1].axvline(vln)
    # axs[1].axvline(230)
    plt.yscale('log')
    #
    plt.suptitle("RGB Histogram (plot)", fontsize=18)
    #
    plt.savefig("3 chennels Historgram.png", dpi=1200)


def bound_squeeze(pil_image, bound):
    """
    這是處理 3channels 的圖片用
    根據直方圖上下界做處理，低於下界的給定黑色[0,0,0]，大於上界的給白色[255,255,255]。

    :param pil_image:
    :param bound  List:(int, int) : [下界, 上屆]
    :return: 返還處理完畢的 ndarray.
    """
    img_nd_copy = np.array(pil_image)

    assert img_nd_copy.ndim == 3
    # shape_ori = img_nd_copy.shape
    # img_nd_copy = img_nd_copy.reshape(-1, 3)
    #
    out_ = bound[0]
    out_lt = bound[1]

    #
    edit_low = img_nd_copy < out_  # 小於 下區間的
    edit_height = img_nd_copy > out_lt  # 大於 上區間的

    edit_low = np.all(edit_low, axis=2)
    edit_height = np.all(edit_height, axis=2)

    img_nd_copy[edit_low] = [0, 0, 0]
    img_nd_copy[edit_height] = [255, 255, 255]

    return img_nd_copy


def do_median_filter(np_image, median_ksize):
    ks_ = (median_ksize, median_ksize)
    #
    after_median_0 = ndimage.median_filter(np_image[:, :, 0], size=ks_)
    after_median_1 = ndimage.median_filter(np_image[:, :, 1], size=ks_)
    after_median_2 = ndimage.median_filter(np_image[:, :, 2], size=ks_)
    #
    new_median = np.dstack((after_median_0, after_median_1, after_median_2))
    #
    for_save = Image.fromarray(new_median)
    for_save.save(f"./after_median_{median_ksize}.png")

    return new_median


def set_margin_white(np_image, w_inner, h_inner):
    """
    將邊緣的 邊界設為 白色，
    :param np_image:
    :param w_inner: List(float, float), 要保留的寬度區間， 區間為[0., 1.].
    :param h_inner: List(float, float), 要保留的高度區間， 區間為[0., 1.].
    :return: 邊界處理完畢的 image.
    """
    assert np_image.ndim == 3
    w, h = np_image.shape[1::-1]

    np_image[::, 0:int(w * w_inner[0])] = [255, 255, 255]  # L
    np_image[::, int(w * w_inner[1]):] = [255, 255, 255]  # R
    np_image[0:int(h * h_inner[0]), ::] = [255, 255, 255]  # T
    np_image[int(h * h_inner[1]):, ::] = [255, 255, 255]  # B

    return np_image


def white_margin_example(img, W_INNER, H_INNER):
    """
    展示 白化margin 的結果
    """
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)

    img.thumbnail((500, 500))

    res = set_margin_white(np.array(img), W_INNER, H_INNER)

    Image.fromarray(res).save("./while_margin_example.png")


if __name__ == '__main__':

    # hyper param
    FILE_PATH = "./file.jpg"
    RATIO = 1  # 縮放大小, 1=原圖大小
    LB_BOUND = [60, 210]  # 分割下界、上界
    MEDIAN_KSIZE = 3  # 中值濾波器 kernel size
    W_INNER = [0.0745, 0.880]  # 邊界強制留白處理時的 "不處理區間"
    H_INNER = [0.0450, 0.925]  # 邊界強制留白處理時的 "不處理區間"
    #

    file = Path(FILE_PATH)

    img = Image.open(file)
    white_margin_example(np.array(img), W_INNER, H_INNER)

    if RATIO < 1:
        img = img.resize((int(img.size[0] * RATIO), int(img.size[1] * RATIO)))

    grey_img = ImageOps.grayscale(img)
    img_nd, grey_img_nd = np.array(img), np.array(grey_img)
    #
    # 增加對比度
    img = ImageOps.autocontrast(img)
    grey_img = ImageOps.autocontrast(grey_img)
    #
    # 繪製直方圖
    make_hist(grey_img_nd)
    plt.show()
    # 繪製直方圖 (三通道版)
    make_hist_3ch(img, LB_BOUND)
    plt.show()
    #
    img_squeezed_nd = bound_squeeze(img, LB_BOUND)
    #
    #  show 出 squeeze 的 image.
    plt.imshow(img_squeezed_nd)
    plt.show()

    for_save = Image.fromarray(img_squeezed_nd)
    for_save.save("./squeezed.png")
    #
    median_ndimg = do_median_filter(img_squeezed_nd, median_ksize=MEDIAN_KSIZE)
    #
    w_inner = W_INNER
    h_inner = H_INNER
    fin = set_margin_white(median_ndimg, w_inner, h_inner)
    #
    for_save = Image.fromarray(fin)
    for_save.save(f"./final_image.png")
    #

