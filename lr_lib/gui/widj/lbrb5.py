# -*- coding: UTF-8 -*-
# виджет (5) LB/RB

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars


class LBRBText(tk.Text):
    """класс виджета (5)LB/RB"""
    bounds = {}.fromkeys(['LB', 'RB'])  # LB/RB instance
    info_text = {'LB': '(5) LB | строк=%s | длина=%s', 'RB': '(5) RB | строк=%s | длина=%s'}

    def __init__(self, name: str, parent: 'lr_lib.gui.wrsp.main_window.Window'):
        self.heightVar = tk.IntVar(value=lr_vars.DEFAULT_LB_RB_MIN_HEIGHT)

        self.label_info = tk.LabelFrame(parent, text=self.info_text[name], font=(lr_vars.DefaultFont + ' bold italic'),
                                        padx=0, pady=0, relief='groove', labelanchor=tk.N, bd=4)
        self.label_info.grid_rowconfigure(0, weight=1)
        self.label_info.grid_columnconfigure(0, weight=1)

        super().__init__(self.label_info, height=lr_vars.DEFAULT_LB_RB_MIN_HEIGHT, background=lr_vars.Background,
                         font=lr_vars.DefaultLBRBFont, wrap=tk.NONE, padx=0, pady=0)
        self.name = name

        self.bounds[name] = self

        self.scrolly = ttk.Scrollbar(self.label_info, orient=tk.VERTICAL, command=self.yview)
        self.scrollx = ttk.Scrollbar(self.label_info, orient=tk.HORIZONTAL, command=self.xview)
        self.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set, bd=0, padx=0, pady=0)
        return

    def get(self, index1=1.0, index2='end') -> str:
        """текущий LB/RB"""
        i = super().get(index1, index2)[:-1]  # [:-1] - '\n'
        return i

    def set(self, text: str) -> None:
        """задать LB/RB"""
        self.delete(1.0, 'end')
        self.insert(1.0, text)
        try:
            self.label_info['text'] = (self.info_text[self.name] % (len(text.split('\n')), len(text)))
        except TypeError:
            self.label_info['text'] = (self.info_text[self.name] % (len(text.decode().split('\n')), len(text)))
        return

    @classmethod
    def set_LB_RB(cls, *args) -> None:
        """извлечь LB/RB из файла"""
        cls.set_label_text()

        lb = lr_vars.VarLB.get()
        try:
            cls.bounds['LB'].set(lb)
        except Exception as ex:
            lr_vars.Logger.error('LB {}'.format(ex.args))
            r = lb.encode(lr_vars.VarEncode.get(), errors='replace')
            cls.bounds['LB'].set(r)

        rb = lr_vars.VarRB.get()
        try:
            cls.bounds['RB'].set(rb)
        except Exception as ex:
            lr_vars.Logger.error('RB {}'.format(ex.args))
            r = lb.encode(lr_vars.VarEncode.get(), errors='replace')
            cls.bounds['RB'].set(r)
        return

    @classmethod
    def set_label_text(cls) -> None:
        """сброс label-текста"""
        for b in cls.info_text:
            r = cls.info_text[b]
            cls.bounds[b].label_info['text'] = r
            continue
        return

    def set_height(self) -> None:
        """кол-во строк LB/RB"""
        self.configure(height=self.heightVar.get())
        return
