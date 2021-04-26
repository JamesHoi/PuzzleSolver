# -*- coding: utf-8 -*-

import sys


def print_progress(iteration, total, prefix="", suffix="", decimals=1, bar_length=50,queue=None,is_finished=True):
    """ Call in a loop to create terminal progress bar"""
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = "\033[32m█\033[0m" * filled_length + "\033[31m-\033[0m" * (bar_length - filled_length)

    # sys.stdout.write("\r{0: <16} {1} {2}{3} {4}".format(prefix, bar, percents, "%", suffix))
    queue.put((float(percents), "{}{}{}{}".format(prefix, percents, "%", suffix), "正在尝试用gaps自动拼图",is_finished))

    # if iteration == total:
    #    sys.stdout.write("\n")
    # sys.stdout.flush()
