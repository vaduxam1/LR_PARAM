# -*- coding: UTF-8 -*-
# окно Настраиваемый запуск поиска WRSP

import contextlib
import tkinter as tk
from typing import Iterable, Tuple, List, Callable, Any

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
    except Exception:
        raise

    if not state:
        yield
        return

    with lr_lib.gui.etc.color_progress.ColorProgress(self):
        self._is_block_ = True
        lr_vars.MainThreadUpdater.submit(lambda: _block(self, True))
        try:
            yield
        except Exception:
            raise
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
    except Exception:
        raise
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
        except (AttributeError, tk.TclError):
            pass
        except Exception:
            raise
        continue
    return


def set_state_widg(var: 'tk.Variable', widgs: List['tk.Widget'], callback=None) -> Callable[[], None]:
    """
    widg: normal/disabled
    """

    def _set_state(*_ar, **_kw) -> None:
        is_on_state = var.get()
        state = ('normal' if is_on_state else 'disabled')

        for w in widgs:
            try: w.config(state=state)  # config
            except:pass
            try:  # ob children config
                for ob in w.winfo_children():
                    try: ob.config(state=state)  # config
                    except:pass
                    continue
            except:pass
            continue

        if callback:
            callback()
        return
    return _set_state
