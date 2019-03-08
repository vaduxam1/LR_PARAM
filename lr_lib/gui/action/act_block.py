# -*- coding: UTF-8 -*-
# action.с окно - блокирование виджетов

import contextlib
import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.excepthook
import lr_lib.gui.action.act_scroll
import lr_lib.gui.etc.color_progress


class ActBlock(lr_lib.gui.action.act_scroll.ActScrollText):
    """
    блокировка виджетов
        main_action.ActionWindow
        act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
        act_backup.ActBackup
      + act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_scroll.ActScrollText.__init__(self)

        # Button
        cmd = lambda *a: self._block(False)
        self.unblock = tk.Button(
            self.file_bar, text='unblock', font=(lr_vars.DefaultFont + ' bold'), command=cmd,
        )
        return

    @contextlib.contextmanager
    def block(self, w=('tk_text', 'unblock', 'search_entry', 'search_res_combo', 'toolbar',)) -> iter:
        """
        заблокировать/разблокировать виджеты в gui - запуск
        """
        with lr_lib.gui.etc.color_progress.ColorProgress(self):
            try:
                lr_vars.MainThreadUpdater.submit(lambda: self._block(True, w=w))
                yield
            except Exception as ex:
                lr_lib.etc.excepthook.excepthook(ex)
            finally:
                lr_vars.MainThreadUpdater.submit(lambda: self._block(False, w=w))
        return

    def _block(self, bl: bool, w=()) -> None:
        """
        заблокировать/разблокировать виджеты в gui - ядро
        """
        state = ('disabled' if bl else 'normal')

        for attr in dir(self):
            if (not attr.startswith('_')) and (attr not in w):
                try:
                    getattr(self, attr).configure(state=state)
                except (AttributeError, tk.TclError) as ex:
                    pass
            continue

        self.update()
        return
