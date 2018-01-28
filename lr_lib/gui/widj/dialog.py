# -*- coding: UTF-8 -*-
# диалог окно

import queue
import contextlib
import tkinter as tk
import tkinter.ttk as ttk


class YesNoCancel(tk.Toplevel):
    '''диалог окно, тк велосипед, работает только в потоке'''
    def __init__(self, buttons: [str, ], text_before: str, text_after: str, title: str, parent=None, default_key='', is_text=None, focus=None, combo_dict=None):
        super().__init__(master=parent, padx=0, pady=0)
        self._wind_attributes()
        self.alive_ = True

        self.parent = parent
        self.buttons = {}
        self.queue = queue.Queue()
        self.title(str(title))
        self.default_key = default_key
        self.combo_dict = combo_dict

        self.combo_var = tk.StringVar(value='')
        if self.combo_dict:
            self.combo = ttk.Combobox(self, textvariable=self.combo_var, values=list(self.combo_dict.keys()))

            def enc(*a) -> None:
                callback = self.combo_dict[self.combo_var.get()]
                self.new_text(callback())

            self.combo.bind("<<ComboboxSelected>>", enc)

        self.label1 = tk.Label(self, text=str(text_before), font='Arial 11', padx=0, pady=0)
        self.label1.grid(row=3, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
        self.label2 = tk.Label(self, text=str(text_after), font='Arial 10', padx=0, pady=0)
        self.label2.grid(row=100, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)

        width = max(map(len, buttons))
        if width > 20: width = 20
        i = 10

        for name in buttons:
            cmd = lambda *a, n=name: self.queue.put_nowait(n)
            self.buttons[name] = tk.Button(
                self, text=name, command=cmd, width=width, font='Arial 9 bold', padx=0, pady=0)
            self.buttons[name].bind("<KeyRelease-Return>", cmd)
            self.buttons[name].grid(row=i, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
            i += 1

        if self.combo_dict: self.combo.grid(row=(i + 1), column=0, padx=0, pady=0)

        self.text = ''
        self.tk_text = tk.Text(self, wrap="none", padx=0, pady=0)
        if is_text is not None:
            with contextlib.suppress(Exception):
                height = len(is_text.split('\n'))
                if height > 25: height = 25
                elif height < 5: height = 5
                self.tk_text.configure(height=height)

            self.tk_text.insert(1.0, is_text)
            self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
            self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
            self.tk_text.configure(yscrollcommand=self.text_scrolly.set, xscrollcommand=self.text_scrollx.set, padx=0, pady=0)
            self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
            self.text_scrollx.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
            self.text_scrolly.grid(row=0, column=1, sticky=tk.NSEW, padx=0, pady=0)

        if self.buttons:
            if self.default_key not in self.buttons: self.default_key = list(self.buttons.keys())[0]
            if not focus: self.buttons[self.default_key].focus_set()
            self.buttons[self.default_key].configure(height=2, background='orange')
        if focus: focus.focus_set()

    def new_text(self, text: str) -> None:
        '''стереть = новый текст в self.tk_text'''
        self.tk_text.delete(1.0, tk.END)
        self.tk_text.insert(1.0, text)

    def _wind_attributes(self) -> None:
        '''сделать окно похожим на dialog'''
        # self.resizable(width=False, height=False)
        self.attributes('-topmost', True)  # свсегда сверху
        # self.attributes("-toolwindow", 1)  # remove maximize/minimize
        self.protocol('WM_DELETE_WINDOW', self.close)  # remove close_threads
        center_widget(self)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def ask(self) -> str:
        '''приостановить поток, до получения ответа'''
        try: return self.queue.get()
        finally:
            self.alive_ = False
            self.text = self.tk_text.get(1.0, tk.END) + '\n'
            self.destroy()
            self.parent.focus_set()

    def close(self) -> None:
        '''отмена при выходе'''
        self.queue.put_nowait(self.default_key)


def center_widget(widget) -> None:
    '''center window on screen'''
    widget.withdraw()
    widget.update_idletasks()
    x = (widget.winfo_screenwidth() - widget.winfo_reqwidth()) / 2
    y = (widget.winfo_screenheight() - widget.winfo_reqheight()) / 2
    widget.geometry("+%d+%d" % (x, y))
    widget.deiconify()