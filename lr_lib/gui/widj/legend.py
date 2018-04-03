# -*- coding: UTF-8 -*-
# web_ леленда

import itertools

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.gui.widj.tooltip_canvas
import lr_lib.core.var.vars as lr_vars


def clrs() -> [str, ]:
    """цвет"""
    cs = sorted(c for c in lr_vars.VarColorTeg.get() if not any((r >= 0) for r in map(
         c.find, {'white', 'black', 'navy', 'grey', 'alice'})))
    return cs


Colors = iter(itertools.cycle(clrs()))


class WebLegend(tk.Toplevel):
    """окно web_ леленды"""
    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow'):
        super().__init__(master=parent, padx=0, pady=0)
        self.geometry('{}x{}'.format(*lr_vars._Tk_LegendWIND_SIZE))
        self.ttl = ' Нажатие правой кнопкой мыши - переход в соответствующую обрасть action.c текста'
        self.title(self.ttl)
        self.attributes('-topmost', True)

        self.web_canavs = {}

        self.parent = parent
        self.minimal_canvas_size = list(lr_vars.Legend_minimal_canvas_size)
        self.H = tk.IntVar(value=lr_vars.LegendHight)

        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)

        hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)

        self.canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.config(scrollregion='0 0 %s %s' % tuple(self.minimal_canvas_size))

        self.interior = tk.Frame(self.canvas)
        self.interior.bind('<Configure>', self._configure_interior)

        self.h_entry = tk.Spinbox(
            self, width=4, justify='center', from_=0, to=10000, command=self.print, textvariable=self.H)
        lr_lib.gui.widj.tooltip.createToolTip(self.h_entry, 'высота, между верхними и нижними объектами')

        def enter_H(*_) -> None:
            """self.H.set по кнопке Enter, при ручном вводе"""
            self.H.set(int(self.h_entry.get()))
            self.print()

        self.h_entry.bind("<KeyRelease-Return>", enter_H)
        self.h_entry.pack()

        self.tr = []  # [(0, 'NoTransaction_1'), (1, 'login'),...
        self.tr_but = tk.Button(self, text='transac', command=self.show_transac)
        self.tr_but.pack()
        lr_lib.gui.widj.tooltip.createToolTip(self.tr_but, 'показать соответствие номеров(из окна легенды) и имен транзакций')

        self.top_var = tk.BooleanVar(value=True)
        self.top_cbx = tk.Checkbutton(self, text='onTop', command=self._set_on_top, variable=self.top_var)
        self.top_cbx.pack()
        lr_lib.gui.widj.tooltip.createToolTip(self.top_cbx, 'поверх других окон')

        lr_lib.gui.etc.gui_other.center_widget(self)

    def _set_on_top(self, *args) -> None:
        """поверх других окон"""
        self.attributes('-topmost', self.top_var.get())

    def _configure_interior(self, *args) -> None:
        """update the scrollbars to match the size of the inner frame"""
        size = (max(self.interior.winfo_reqwidth(), self.minimal_canvas_size[0]),
                max(self.interior.winfo_reqheight(), self.minimal_canvas_size[1]))
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def add_web_canavs(self):
        for web_ in self.parent.web_action.get_web_snapshot_all():
            self.web_canavs[web_.snapshot] = {1: {}, 2: {}, 'enable': True, 'enable_in': True}

    def print(self, *_, colors=Colors) -> None:
        self.canvas.delete("all")
        web_actions = tuple(self.parent.web_action.get_web_snapshot_all())
        sep = 25
        w_ = 30
        width = 40
        height = 35
        wdt = {w.snapshot: w for w in web_actions}
        self.minimal_canvas_size[0] = lr_vars.Legend_scroll_len_modificator * len(wdt)
        self._configure_interior()
        _transaction = None
        self.tr.clear()
        lt = 0
        H = self.H.get()
        lcolor = 'black'
        rep_param = self.parent.web_action.websReport.param_statistic
        colrs = clrs()

        for i in self.web_canavs:
            transaction = wdt[i].transaction

            if transaction != _transaction:
                if transaction:
                    lt = len(self.tr)
                    lcolor = color = next(colors)
                else:
                    lt = None
                    lcolor = color = 'grey'
                t = (lt, transaction)
                text = '({})->'.format(lt)
                self.tr.append(t)
            else:
                text = '<-{}'.format(lt)

            self.canvas.create_text((sep + 40), 10, text=text)
            if color in ('grey', 'yellow', ):
                lcolor = 'black'

            st = 'Snap: {}\nout: {}'.format(i, len(wdt[i].web_reg_save_param_list))
            r_in = 'транзакция: "{t}"\n{s}'.format(
                s=self.parent.web_action.websReport.stats_in_web(i).strip(), t=transaction)
            r_out = 'транзакция: "{t}"\n{s}'.format(
                s=self.parent.web_action.websReport.stats_out_web(i).strip(), t=transaction)

            def onObjectClick1(event, i=i, colors=colors) -> None:
                """показать/удалить линии out"""
                self.canvas.delete("all")
                self.web_canavs[i]['enable'] = not self.web_canavs[i]['enable']
                self.print(colors=colors)

            def onObjectClick3(event, i=i) -> None:
                self.parent.search_in_action(word='Snapshot=t{i}.inf'.format(i=i), hist=False)

            def onObjectClick2(event, i=i, colors=colors) -> None:
                """показать/удалить линии in"""
                self.canvas.delete("all")
                self.web_canavs[i]['enable_in'] = not self.web_canavs[i]['enable_in']
                self.print(colors=colors)

            # 1
            if wdt[i].web_reg_save_param_list:  # пометить, что создает новые {param}
                cmd = self.canvas.create_oval
                c = colrs.index(color)
                if c:
                    c -= 1
                cl = colrs[c:] + colrs[:c]
                onObjectClick1 = lambda event, i=i, cl=cl: onObjectClick1(event, i=i, colors=iter(itertools.cycle(cl)))
                onObjectClick2 = lambda event, i=i, cl=cl: onObjectClick2(event, i=i, colors=iter(itertools.cycle(cl)))
            else:
                cmd = self.canvas.create_rectangle
            xy1 = lcolor, sep, 20, (width + sep + w_), (20 + height)

            shape_1 = cmd(*xy1[1:], fill=color, width=2)

            lr_lib.gui.widj.tooltip_canvas.CanvasTooltip(self.canvas, shape_1, text=r_out)
            self.canvas.tag_bind(shape_1, '<ButtonPress-1>', onObjectClick1)
            self.canvas.tag_bind(shape_1, '<Button-3>', onObjectClick3)
            self.web_canavs[i][1] = list(xy1)

            t1 = self.canvas.create_text(sep + w_, 35, text=st)
            self.canvas.tag_bind(t1, '<ButtonPress-1>', onObjectClick1)
            self.canvas.tag_bind(t1, '<Button-3>', onObjectClick3)
            if transaction != _transaction:
                self.canvas.create_text((sep + w_), (H + 45), text='transac({})'.format(lt if transaction else "''"))
                _transaction = transaction

            # 2
            li = len(self.parent.web_action.websReport.web_snapshot_param_in_count[i])
            if li:
                cmd = self.canvas.create_oval
            else:  # пометить, что внутри не используются {param}
                cmd = self.canvas.create_rectangle
            xy2 = sep, H, (width + sep + w_), (H + height)

            shape_2 = cmd(*xy2, fill=color, width=2)

            self.canvas.tag_bind(shape_2, '<Button-3>', onObjectClick3)
            lr_lib.gui.widj.tooltip_canvas.CanvasTooltip(self.canvas, shape_2, text=r_in)
            self.canvas.tag_bind(shape_2, '<ButtonPress-1>', onObjectClick2)
            self.web_canavs[i][2] = list(xy2)

            t2 = self.canvas.create_text((sep + w_), (H + 15), text='in: {li}\nSnap: {i}'.format(i=i, li=li))
            self.canvas.tag_bind(t2, '<Button-3>', onObjectClick3)
            self.canvas.tag_bind(t2, '<ButtonPress-1>', onObjectClick2)

            sep += 70

        x = 20  # create_line's
        for web_ in web_actions:
            if self.web_canavs[web_.snapshot]['enable']:
                color, *xy1 = self.web_canavs[web_.snapshot][1]
                wn = [w.name for w in web_.web_reg_save_param_list]
                for w in web_.web_reg_save_param_list:
                    name = w.name
                    r_param = rep_param[name]

                    for i in r_param['snapshots']:
                        if self.web_canavs[i]['enable_in']:
                            in_count = self.parent.web_action.websReport.web_snapshot_param_in_count[i]
                            in_count = {k: in_count[k] for k in in_count if k in wn}

                            xy2 = self.web_canavs[i][2]
                            line = self.canvas.create_line(
                                xy1[2]-x, xy1[3], xy2[0]+x, xy2[1], fill=color, arrow=tk.LAST, width=2)

                            def onObjectClick(event, word='"{}"'.format(name)) -> None:
                                self.parent.search_in_action(word=word, hist=False)

                            self.canvas.tag_bind(line, '<Button-3>', onObjectClick)
                            r = 'Snapshot=t{i}.inf\n{r}'.format(r='\n'.join(in_count), i=i)
                            lr_lib.gui.widj.tooltip_canvas.CanvasTooltip(self.canvas, line, text=r)
                            self.canvas.tag_bind(line, '<ButtonPress-1>',
                                                 lambda *a, r=r.replace('\n', ', '): self.title(r + self.ttl))

    def show_transac(self, *args) -> None:
        """показать соответствие номеров(из окна легенды) и имен транзакций"""
        transacts = [(a, b) for (a, b) in self.tr if b]
        if transacts:
            tw = tk.Toplevel(self)
            tw.attributes('-topmost', True)
            tw.title('{} транзакций - соответствие номеров и имен'.format(len(transacts)))
            tw.grid_columnconfigure(0, weight=1)
            tw.grid_rowconfigure(0, weight=1)

            tk_text = tk.Text(
                tw, foreground='grey', background=lr_vars.Background, wrap=tk.NONE, padx=0, pady=0, undo=True,)

            text_scrolly = ttk.Scrollbar(tw, orient=tk.VERTICAL, command=tk_text.yview)
            text_scrollx = ttk.Scrollbar(tw, orient=tk.HORIZONTAL, command=tk_text.xview)
            tk_text.configure(
                yscrollcommand=text_scrolly.set, xscrollcommand=text_scrollx.set, bd=0, padx=0, pady=0)

            tk_text.insert(tk.END, '\n'.join('({}): {}'.format(a, b) for (a, b) in transacts))

            tk_text.grid(row=0, column=0, sticky=tk.NSEW)
            text_scrolly.grid(row=0, column=1, sticky=tk.NSEW)
            text_scrollx.grid(row=1, column=0, sticky=tk.NSEW)
