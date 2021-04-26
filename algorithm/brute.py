import cv2
from PIL import Image
import numpy as np
from backend.settings import settings


def brute_task(queue, threshold, m_pieces, o_pieces):
    """
    :param m_pieces: modified_pieces
    :param o_pieces: original_pieces
    :return:
    """
    SMALL_WIDTH = settings.piece_size
    SMALL_HEIGHT = settings.piece_size
    ROW = settings.pic_rows
    COLUMN = settings.pic_columns
    PIECE_NUM = settings.pieces_num
    CONFIDENCE = 0.95
    USED = [0, 0]
    for i in range(int(ROW) * int(COLUMN) - 2):
        USED.append(0)
    INDEX_LIST = []

    def cmp(a,b,threshold=10):
        count=0
        for i in range(SMALL_HEIGHT):
            for j in range(SMALL_WIDTH):
                pix_a = a.getpixel((i,j))
                pix_b = b.getpixel((i,j))
                if abs(pix_a[0]-pix_b[0])<threshold and abs(pix_a[1]-pix_b[1])<threshold and abs(pix_a[2]-pix_b[2])<threshold:
                    count = count+1
        return count/(SMALL_HEIGHT*SMALL_WIDTH)

    def run():
        queue.put((0, "初始化完成", "正在尝试暴力对比像素点拼图", False))
        for i in range(int(ROW) * int(COLUMN)):
            # queue.put((i / PIECE_NUM, "正在处理第{}/{}".format(i, PIECE_NUM), "正在尝试暴力对比像素点拼图", False))
            num = 0; max_p = 0
            for j in range(int(ROW) * int(COLUMN)):
                if USED[j] == 0:
                    percent = cmp(m_pieces[j], o_pieces[i],threshold=threshold)
                    if percent > max_p:
                        max_p = percent
                        num = j
                else: continue
            # m_pieces[num].save("test.jpg")
            # o_pieces[i].save("test1.jpg")
            # print(max_p)
            if max_p > CONFIDENCE:
                USED[num] = 1
                INDEX_LIST.append(num)
                queue.put(((i / PIECE_NUM)*100,"{}处理完毕，置信度{}".format(i, max_p),"正在尝试暴力对比像素点拼图",False))
            else:
                INDEX_LIST.append(-1)
                queue.put(((i / PIECE_NUM)*100, "{}找到的匹配置信度不足{}".format(i,max_p), "正在尝试暴力对比像素点拼图", False))
        return INDEX_LIST
    return run()