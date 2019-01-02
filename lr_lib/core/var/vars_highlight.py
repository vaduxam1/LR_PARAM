# -*- coding: UTF-8 -*-
# Highlight переменные, настройки

import itertools
import os
import random
import string

from lr_lib.core.var._var import Var
from lr_lib.core.var.vars import lib_folder
from lr_lib.core.var.vars_other import _unpunct
from lr_lib.core.var.vars_param import LB_PARAM_FIND_LIST, DENY_WEB_
from lr_lib.etc.help import COLORS, HEX

HighlightOn = True  # включить подсветку
HighlightAfter0 = 1500  # задержка(мс), перед перезапуском проверки необходимости подсветки
HighlightAfter1 = 250  # задержка(мс), перед стартом подсветки всех линий, отображенных на экране
HighlightAfter2 = 250  # задержка(мс), перед подсветкой одной линии
Background = 'khaki'
highlight_words_folder = os.path.join(lib_folder, 'etc')
highlight_words_main_file = os.path.join(highlight_words_folder, 'highlight_words.txt')
highlight_words_files_startswith = 'highlight_words'


def random_color(ckeck=True, all_color=tuple(COLORS.keys())) -> str:
    """итератор - случайный цвет"""
    while ckeck:
        color = random.choice(all_color)
        yield color
        continue
    return


ColorIterator = random_color()
VarColorTeg = Var(value=set(COLORS.keys()))
_LB_LIST_highlight = {'uuid_', 'dtid', 'sessionid', 'Snapshot', 'Snapshot=t', 'EXTRARES', '.inf', }
_LB_LIST_highlight.update(_unpunct(s) for s in LB_PARAM_FIND_LIST)
tnrvf = set('\\{}'.format(s) for s in 'tnrvf')
PopUpWindColor1 = 'Grey'  # просто какойто общий цвет для выделения PopUpWindow
highlight_words = set()  # слова для подсветки


def init_highlight_words() -> None:
    """заполнить highlight_words"""
    for file in next(os.walk(highlight_words_folder))[2]:
        if file.startswith(highlight_words_files_startswith):
            with open(os.path.join(highlight_words_folder, file)) as hws:
                for line in hws:
                    lr = line.rstrip('\n')
                    ls = lr.strip()
                    if ls and (not ls.startswith('#')):
                        highlight_words.add(lr)
                    continue
        continue

    highlight_words.update(COLORS.keys())
    highlight_words.update(HEX)
    for s in string.digits:
        highlight_words.add('Value={\\"\\":%s' % s)
        continue

    highlight_words.update(tnrvf)
    return


rd = {
    '/*', '*/', 'WARNING',
}
rd.update(DENY_WEB_)

VarDefaultColorTeg = {
    'background': {
        'orange': rd,
        'springgreen': {'lr_end_transaction', },
        'yellowgreen': {'lr_think_time', },
        'mediumspringgreen': {'lr_start_transaction', },
    },
    'foreground': {
        'olive': highlight_words,
        'purple': _LB_LIST_highlight,
    },
}
DefaultColor = 'olive'  # цвет для "фонового" текста
hex_unicode_words = '\\\\x\w\w'  # re.compile(hex_unicode_words).findall('start\\xCE\\xE1end')
hex_unicode_ground = 'foreground'  # \\xCE\\xE1
hex_unicode_color = 'olive'  # \\xCE\\xE1
PunctDigitTag = 'foregroundblack'
RusTag = 'backgroundorange'
wrsp_color1 = 'chartreuse'
wrsp_color2 = 'darkblue'
color_transactions_names = 'darkslategrey'
color_warn_wrsp = 'red'
ForceOlive = (
    'value=xon', 'value=on', 'value={\\"left\\', 'value=i"', 'value={}', 'value={\\"', 'value=dummy',
    'value={\\"command',
)  # всегда подсвечивать olive цветом
ColorMainTegStartswith = 'background'  # не подсветит другим тегом, если подсвечено этим
OliveChildTeg = 'foregroundolive'  # не подсветит этим тегом, если подсвечено любым другим
minus_teg = {OliveChildTeg}  # other_tegs = (tegs_indxs.keys() - minus_teg)
web_reg_highlight_len = 6  # выделить начало имени web_reg_save_param
