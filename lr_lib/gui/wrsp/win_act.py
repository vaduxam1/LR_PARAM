# -*- coding: UTF-8 -*-
# связь окна с lr_lib.gui.action.main_action.ActionWindow

import collections

import tkinter as tk

import lr_lib
import lr_lib.gui.action.main_action
import lr_lib.gui.wrsp.win_frame
import lr_lib.core.var.vars as lr_vars


class WinAct(lr_lib.gui.wrsp.win_frame.WinFrame):
    """связь с lr_lib.gui.action.main_action.ActionWindow"""
    def __init__(self):
        lr_lib.gui.wrsp.win_frame.WinFrame.__init__(self)

        self.action_windows = collections.OrderedDict()  # {id: lr_lib.gui.action.main_action.ActionWindow, }

        self.actionButton = tk.Button(
            self.find_frame, text=' action.c  editor ', font=lr_vars.DefaultFont + ' italic bold', padx=0, pady=0,
            command=self.new_action_window, relief='ridge', background='orange')
        return

    def get_main_action(self) -> lr_lib.gui.action.main_action.ActionWindow:
        """если открыто несколько action онон, какое вернуть"""
        for action in self.action_windows:
            return self.action_windows[action]
        return

    def new_action_window(self, *args, folder=None, file='action.c') -> lr_lib.gui.action.main_action.ActionWindow:
        """создать lr_lib.gui.action.main_action.ActionWindow()"""
        if folder is None:
            folder = lr_vars.VarFilesFolder.get()

        if lr_lib.gui.action._other.get_action_file(folder=folder, file=file):
            action = lr_lib.gui.action.main_action.ActionWindow()
            self.action_windows[action.id_] = action  # сохранить

            action._start_auto_update_action_info_lab()  # автообновление label состояния пула
            action.tk_text.after_callback()  # автообновление потсветки и т.д.

            self.after(100, self.focus_set)  # тк гдето само активируется
            self.after(500, action.focus_set)  # открыть поверх главного окна

            return action
        return
