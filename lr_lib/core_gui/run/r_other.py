# -*- coding: UTF-8 -*-
# окно Настраиваемый запуск поиска WRSP

import contextlib
import tkinter as tk
from typing import Iterable, Tuple, List, Callable

import lr_lib
from lr_lib.core.var import vars as lr_vars


@contextlib.contextmanager
def block(self) -> Iterable:
    """
    заблокировать/разблокировать виджеты в gui
    """
    try:
        state = (not self.parent._is_block_)
    except AttributeError:
        state = (not self._is_block_)

    if not state:
        yield
        return

    with lr_lib.gui.etc.color_progress.ColorProgress(self):
        self._is_block_ = True
        lr_vars.MainThreadUpdater.submit(lambda: _block(self, True))
        try:
            yield
        finally:
            self._is_block_ = False
            lr_vars.MainThreadUpdater.submit(lambda: _block(self, False))
    return


def _block(self, bl: bool) -> None:
    """
    заблокировать/разблокировать виджеты в gui
    """
    state = ('disabled' if bl else 'normal')

    for item in self.block_items:
        item_getattr(item, state)
        continue

    try:
        self.update()
    except AttributeError:
        self.main_label.update()
    return


def item_getattr(item, state: str) -> None:
    """
    заблокировать/разблокировать виджеты в gui
    """
    for attr in dir(item):
        if attr.startswith('_'):
            continue
        try:
            ga = getattr(item, attr)
            ga.configure(state=state)
        except (AttributeError, tk.TclError) as ex:
            pass
        continue
    return


def set_state_widg(var, widgs: List) -> Callable:
    """
    widg: normal/disabled
    """

    def _set_state_widg(*args, **kwargs) -> None:
        v = var.get()
        s = ('normal' if v else 'disabled')
        for w in widgs:
            try:
                w.config(state=s)
            except:
                try:
                    for ob in w.winfo_children():
                        try:
                            ob.config(state=s)
                        except:
                            pass
                        continue
                except:
                    pass
            continue
        return

    return _set_state_widg
