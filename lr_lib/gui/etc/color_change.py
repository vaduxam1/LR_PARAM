# -*- coding: UTF-8 -*-
# гирлянда - смена цветов кнопок

from typing import Iterable, Tuple, Set, Dict, Callable

import lr_lib.core.var.vars_highlight
from lr_lib.core.var import vars as lr_vars

ColorCash = {}  # оригинальный цвет виджетов


def background_color_set(self, color='', _types=('Button',), obs=None) -> None:
    """
    поменять цвет всех виджетов
    """
    if obs is None:
        wid = [self, lr_vars.Window, ]
        obs = [ob for w in wid for ob in DiR(w, _types=_types)]
        try:
            obs.append(self.tk_text.linenumbers)
        except:
            pass

    for ob in obs:
        if color is None:
            if ob not in ColorCash:
                try:
                    ColorCash[ob] = ob['background']
                except Exception as ex:
                    continue
            background = _rnd_color(self, color)
        elif not color:
            if ob in ColorCash:
                background = ColorCash[ob]
            else:
                background = _rnd_color(self, color)
        else:
            background = _rnd_color(self, color)

        try:
            ob.config(background=background)
        except Exception as ex:
            pass
        continue
    return


def _rnd_color(self, color: 'str or None or ""') -> str:
    """
    вернуть имя цвета
    :param color: None-случайный/False-оригинальный/str-"Red"
    :return: "Red"
    """
    if color is None:
        color = next(lr_lib.core.var.vars_highlight.ColorIterator)
    elif not color:
        color = self.background_color_combo.get()
    return color


def DiR(ob, _types=('button',)) -> Iterable:
    """
    объекты для смены цвета
    """
    for attr in dir(ob):
        ga = getattr(ob, attr)
        ta = type(ga)
        if not any(map(str(ta).__contains__, _types)):
            continue

        try:
            ga['background']
            assert hasattr(ga, 'config')
        except:
            continue

        yield ga
        if hasattr(ga, 'winfo_children') and (not callable(ga)):
            yield from DiR(ga.winfo_children())
        continue
    return
