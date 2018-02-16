# -*- coding: UTF-8 -*-
# web_ леленда

import itertools

import tkinter as tk

import lr_lib.core.var.vars as lr_vars
import lr_lib.gui.widj.tooltip_canvas as lr_tooltip_canvas


class WebLegend(tk.Toplevel):
    '''окно web_ леленды'''
    def __init__(self, parent):
        super().__init__(master=parent, padx=0, pady=0)
        self.geometry('{}x{}'.format(*lr_vars._Tk_LegendWIND_SIZE))
        self.web_canavs = {}

        self.parent = parent
        self.minimal_canvas_size = list(lr_vars.Legend_minimal_canvas_size)
        self.H = tk.IntVar(value=lr_vars.LegendHight)

        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)

        hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=tk.FALSE)

        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.config(scrollregion='0 0 %s %s' % tuple(self.minimal_canvas_size))

        self.interior = tk.Frame(self.canvas)
        self.interior.bind('<Configure>', self._configure_interior)

        self.h_entry = tk.Spinbox(self, width=4, justify='center', from_=0, to=9999,
                                  command=lambda *a: self.print(transac_show=False), textvariable=self.H)
        self.h_entry.pack()

    def _configure_interior(self, *args) -> None:
        '''update the scrollbars to match the size of the inner frame'''
        size = (max(self.interior.winfo_reqwidth(), self.minimal_canvas_size[0]),
                max(self.interior.winfo_reqheight(), self.minimal_canvas_size[1]))
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def add_web_canavs(self):
        for web_ in self.parent.web_action.get_web_snapshot_all():
            self.web_canavs[web_.snapshot] = {1: {}, 2: {}, 'enable': True, 'enable_in': True}

    def print(self, transac_show=True, colors=iter(itertools.cycle(lr_vars.VarColorTeg.get() - {'white', 'black', 'navy', }))) -> None:
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
        tr = []
        lt = 0
        H = self.H.get()
        lcolor = 'black'
        rep_param = self.parent.web_action.websReport.param_statistic

        for i in self.web_canavs:
            transaction = wdt[i].transaction

            if transaction != _transaction:
                if transaction:
                    lt = len(tr)
                    lcolor = color = next(colors)
                else:
                    lt = None
                    lcolor = color = 'white'
                t = (lt, transaction)
                text = '({})->'.format(lt)
                tr.append(t)
            else:
                text = '<-{}'.format(lt)

            self.canvas.create_text((sep + 40), 10, text=text)
            if color in ('white', 'yellow', ):
                lcolor = 'black'

            xy1 = lcolor, sep, 20, (width + sep + w_), (20 + height)
            st = 'Snap: {}\nout: {}'.format(i, len(wdt[i].web_reg_save_param_list))

            r_in = self.parent.web_action.websReport.stats_in_web(i).strip()
            r_out = self.parent.web_action.websReport.stats_out_web(i).strip()

            def onObjectClick1(event, i=i) -> None:
                '''показать/удалить линии out'''
                self.canvas.delete("all")
                self.web_canavs[i]['enable'] = not self.web_canavs[i]['enable']
                self.print(transac_show=False)

            def onObjectClick2(event, i=i) -> None:
                '''показать/удалить линии in'''
                self.canvas.delete("all")
                self.web_canavs[i]['enable_in'] = not self.web_canavs[i]['enable_in']
                self.print(transac_show=False)

            if wdt[i].web_reg_save_param_list:
                shape_1 = self.canvas.create_rectangle(*xy1[1:], fill=color, width=2)
                lr_tooltip_canvas.CanvasTooltip(self.canvas, shape_1, text=r_out)
                self.canvas.tag_bind(shape_1, '<ButtonPress-1>', onObjectClick1)
            self.web_canavs[i][1] = list(xy1)

            t1 = self.canvas.create_text(sep + w_, 35, text=st)
            self.canvas.tag_bind(t1, '<ButtonPress-1>', onObjectClick1)
            if transaction != _transaction:
                self.canvas.create_text((sep + w_), (H + 45), text='transac({})'.format(lt if transaction else "''"))
                _transaction = transaction

            xy2 = sep, H, (width + sep + w_), (H + height)
            shape_2 = self.canvas.create_rectangle(*xy2, fill=color, width=2)
            lr_tooltip_canvas.CanvasTooltip(self.canvas, shape_2, text=r_in)
            self.canvas.tag_bind(shape_2, '<ButtonPress-1>', onObjectClick2)
            self.web_canavs[i][2] = list(xy2)

            li = len(self.parent.web_action.websReport.web_snapshot_param_in_count[i])
            t2 = self.canvas.create_text((sep + w_), (H + 15), text='in: {li}\nSnap: {i}'.format(i=i, li=li))
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
                            line = self.canvas.create_line(xy1[2]-x, xy1[3], xy2[0]+x, xy2[1], fill=color, arrow=tk.LAST, width=2)

                            r = 'Snapshot=t{i}.inf\n{r}'.format(r='\n'.join(in_count), i=i)
                            lr_tooltip_canvas.CanvasTooltip(self.canvas, line, text=r)
                            self.canvas.tag_bind(line, '<ButtonPress-1>', lambda *a, r=r.replace('\n', ', '): self.title(r))

        if transac_show:
            t = [(a, b) for (a, b) in tr if b]
            if t:
                tw = tk.Toplevel(self)
                tw.attributes('-topmost', True)
                tw.title('transactions')
                l = tk.Label(tw)
                l.pack()
                t = [(a, b) for (a, b) in tr if b]
                m = str(max([len(b) for (_, b) in t]) if t else 1)
                s = 't({})\t{:>%s}' % m
                tl = [s.format(a, b) for (a, b) in t]
                l.configure(text='\n'.join(tl))
