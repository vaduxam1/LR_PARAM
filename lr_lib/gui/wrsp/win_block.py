# -*- coding: UTF-8 -*-
# блокировать виджеты

import contextlib
import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.etc.color_progress
import lr_lib.gui.wrsp.win_act

AllowWidj = (
    'text', 'tk_text', 'min_inf', 'max_inf', 'unblock', 'cbxPopupWindow', 'last_frame',
)


class WinBlock(lr_lib.gui.wrsp.win_act.WinAct):
    """
    блокировать виджеты
        main_window.Window
        win_menu.WinMenu
        win_folder.WinFolder
        win_other.WinOther
        win_filesort.WinFileSort
        win_maxmin.WinMaxMin
        win_widj.WinWidj
        win_part_lbrb.WinPartsLbRb
        win_text.WinText
      + win_block.WinBlock
        win_act.WinAct
        win_frame.WinFrame
        ttk.Frame
    """

    def __init__(self):
        lr_lib.gui.wrsp.win_act.WinAct.__init__(self)

        self._block_ = None  # принудительно блокировать виджеты
        return

    @contextlib.contextmanager
    def block(self, w=AllowWidj, force=False) -> iter:
        """
        заблокировать/разблокировать виджеты в gui
        """
        with lr_lib.gui.etc.color_progress.ColorProgress(self):
            try:
                if self._block_:
                    yield
                else:
                    if force:
                        self._block_ = True

                    lr_vars.MainThreadUpdater.submit(lambda: self._block(True, w=w))
                    yield
            finally:
                if force:
                    self._block_ = False

                if not self._block_:
                    lr_vars.MainThreadUpdater.submit(lambda: self._block(False, w=w))
        return

    def _block(self, bl: bool, w=()) -> None:
        """
        заблокировать/разблокировать виджеты в gui
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
