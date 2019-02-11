# -*- coding: UTF-8 -*-
# диалог окно

import codecs
import queue

import tkinter as tk
import tkinter.messagebox
import tkinter.ttk as ttk

K_FIND = 'Найти'
K_SKIP = 'Пропуск'
K_CANCEL = 'Отменить'
K_CREATE = 'Создать'
CREATE_or_FIND = lambda x: (K_CREATE if x else '')


class YesNoCancel(tk.Toplevel):
    """
    диалог окно, тк велосипед, работает только в потоке
    """

    def __init__(
            self,
            buttons: [str, ],
            text_before: str,
            text_after: str,
            title: str,
            parent=None,
            default_key='',
            is_text=None,
            focus=None,
            combo_dict=None,
            t_enc=False,
            color=None,
            btn_font='Arial 9 bold',
    ):
        """
        :param buttons: названия кнопок
        :param text_before: текст описания
        :param text_after: текст нижнего описания
        :param title: тайтл окна
        :param parent: родитель окна
        :param default_key: кнопка по умолчанию
        :param is_text: текст основного tk.Text виджета
        :param focus: установить фокус ввода
        :param combo_dict: ttk.Combobox значения
        :param t_enc: декодировать is_text
        :param color: label1 цвет фона
        """
        super().__init__(master=parent, padx=0, pady=0)
        buttons = list(filter(bool, buttons))

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
            values = list(self.combo_dict.keys())

            # Combobox
            self.combo = ttk.Combobox(self, textvariable=self.combo_var, values=values, )

            def enc(*a) -> None:
                """выбор в Combobox -> вывод нового текста в self.tk_text"""
                cv = self.combo_var.get()
                callback = self.combo_dict[cv]
                text = callback()  # получить text
                self.new_text(text)  # вывести
                return
            self.combo.bind("<<ComboboxSelected>>", enc)

        # Label
        self.text_before = tk.Label(self, text=str(text_before), font='Arial 10', bg=color, justify=tk.LEFT, )
        self.text_before.grid(row=3, column=0, sticky=tk.NSEW, columnspan=2, )

        # Label
        self.text_after = tk.Label(self, text=str(text_after), font='Arial 10', justify=tk.LEFT, )
        self.text_after.grid(row=100, column=0, sticky=tk.NSEW, columnspan=2, )

        bl = list(map(len, buttons))
        width = max(bl)
        if width > 20:
            width = 20
        i = 10

        # Button's
        for name in buttons:

            def cmd(*a, n=name) -> None:
                """
                button callback, выход при нажатии
                :param n: str: имя кнопки калбека, для возврата в функцию, вызвавщую диалог, при выходе
                :return: None
                """
                if n == K_CREATE:
                    if tkinter.messagebox.askokcancel('Продолжить?', K_CREATE, parent=self):
                        self.queue.put(n)
                    else:
                        pass  # оставаться в диалог окне
                else:
                    self.queue.put(n)  # выйти
                return

            # Button
            self.buttons[name] = tk.Button(self, text=name, command=cmd, width=width, font=btn_font, padx=0, pady=0,)
            self.buttons[name].bind("<KeyRelease-Return>", cmd)
            self.buttons[name].grid(row=i, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)

            i += 1
            continue

        if self.combo_dict:
            self.combo.grid(row=(i + 1), column=0, padx=0, pady=0)

        # tk.Text
        self.tk_text = tk.Text(self, wrap="none", padx=0, pady=0)
        self.text = ''  # текст tk.Text при выходе

        if is_text is not None:
            try:
                height = len(is_text.split('\n'))
                if height > 25:
                    height = 25
                elif height < 5:
                    height = 5
                self.tk_text.configure(height=height, width=100)
            except Exception as ex:
                pass

            if t_enc:
                is_text = codecs.decode(is_text, 'unicode_escape', 'replace')

            self.tk_text.insert(1.0, is_text)
            self.text_scrolly = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tk_text.yview)
            self.text_scrollx = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tk_text.xview)
            self.tk_text.configure(yscrollcommand=self.text_scrolly.set, xscrollcommand=self.text_scrollx.set)
            self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
            self.text_scrollx.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2, padx=0, pady=0)
            self.text_scrolly.grid(row=0, column=1, sticky=tk.NSEW, padx=0, pady=0)

        if self.buttons:
            if self.default_key not in self.buttons:
                bk = list(self.buttons.keys())
                self.default_key = bk[0]

            if not focus:
                btn = self.buttons[self.default_key]
                btn.focus_set()

            b = self.buttons[self.default_key]
            b.configure(height=2, background='orange')

        self.center_widget()
        if focus:
            focus.focus_set()
        return

    def new_text(self, text: str) -> None:
        """
        стереть = новый текст в self.tk_text
        """
        self.tk_text.delete(1.0, tk.END)
        self.tk_text.insert(1.0, text)
        return

    def _wind_attributes(self) -> None:
        """
        сделать окно похожим на dialog
        """
        # self.resizable(width=False, height=False)
        self.attributes('-topmost', True)  # свсегда сверху
        # self.attributes("-toolwindow", 1)  # remove maximize/minimize
        self.protocol('WM_DELETE_WINDOW', self.close)  # remove close_threads
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        return

    def text_get(self) -> str:
        """
        текст tk.Text
        """
        t = self.tk_text.get(1.0, tk.END)
        return t

    def ask(self) -> str:
        """
        приостановить поток, до получения ответа
        """
        try:
            item = self.queue.get()
            return item
        finally:
            self.alive_ = False
            t = self.text_get()
            self.text = '\n{}'.format(t)
            self.destroy()
            self.parent.focus_set()

    def close(self) -> None:
        """
        отмена при выходе
        """
        self.queue.put_nowait(self.default_key)
        return

    def center_widget(self) -> None:
        """
        center window on screen
        """
        self.withdraw()
        self.update_idletasks()

        x = (self.winfo_screenwidth() - self.winfo_reqwidth())
        x /= 2
        y = (self.winfo_screenheight() - self.winfo_reqheight())
        y /= 2
        g = ("+%d+%d" % (x, y))

        self.geometry(g)
        self.deiconify()
        return
