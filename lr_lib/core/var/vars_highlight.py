﻿# -*- coding: UTF-8 -*-
# Highlight переменные, настройки

import os
import itertools
import random
import string

import lr_lib.core.var._var
import lr_lib.core.var.vars
import lr_lib.core.var.vars_other
import lr_lib.core.var.vars_param
import lr_lib.etc.help

HighlightOn = True  # включить подсветку
HighlightAfter0 = 1500  # задержка(мс), перед перезапуском проверки необходимости подсветки
HighlightAfter1 = 250  # задержка(мс), перед стартом подсветки всех линий, отображенных на экране
HighlightAfter2 = 250  # задержка(мс), перед подсветкой одной линии
Background = 'khaki'
ColorProgressDelay = 0.5  # мс - чем меньше тем быстрее смена цветов "гирлянды"

highlight_words_folder = os.path.join(lr_lib.core.var.vars.lib_folder, 'etc')
highlight_words_main_file = os.path.join(highlight_words_folder, 'highlight_words.txt')
highlight_words_files_startswith = 'highlight_words'

_COLORS = itertools.cycle(lr_lib.etc.help.COLORS.keys())


def random_color(ckeck=True, all_color='ABCDEF1234567890', r=6, ) -> str:
    """итератор - случайный цвет"""
    # ch = True
    while ckeck:
        # if ch:
        #     color = '#{}'.format(''.join(random.choice(all_color) for _ in range(r)))
        # else:
        color = next(_COLORS)

        yield color
        # ch = (not ch)
        continue
    return


ColorIterator = random_color()
VarColorTeg = lr_lib.core.var._var.Var(value=set(lr_lib.etc.help.COLORS.keys()))
_LB_LIST_highlight = {'uuid_', 'dtid', 'sessionid', 'Snapshot', 'Snapshot=t', 'EXTRARES', '.inf', }
_LB_LIST_highlight.update(lr_lib.core.var.vars_other._unpunct(s) for s in lr_lib.core.var.vars_param.LB_PARAM_FIND_LIST)
tnrvf = set('\\{}'.format(s) for s in 'tnrvf')
PopUpWindColor1 = 'LightGrey'  # просто какойто общий цвет для выделения PopUpWindow
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

    highlight_words.update(lr_lib.etc.help.COLORS.keys())
    highlight_words.update(lr_lib.etc.help.HEX)
    for s in string.digits:
        highlight_words.add('Value={\\"\\":%s' % s)
        continue

    highlight_words.update(tnrvf)
    return


rd = {
    '/*', '*/', 'WARNING',
}
rd.update(lr_lib.core.var.vars_param.DENY_WEB_)

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
