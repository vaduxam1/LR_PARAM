# -*- coding: UTF-8 -*-
# основные виджеты (4) (5)LB (5)RB

import string
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars_param
import lr_lib.gui.wrsp.win_text


class WinPartsLbRb(lr_lib.gui.wrsp.win_text.WinText):
    """
    основные виджеты: (4) (5)LB (5)RB
        main_window.Window
        win_menu.WinMenu
        win_folder.WinFolder
        win_other.WinOther
        win_filesort.WinFileSort
        win_maxmin.WinMaxMin
        win_widj.WinWidj
      + win_part_lbrb.WinPartsLbRb
        win_text.WinText
        win_block.WinBlock
        win_act.WinAct
        win_frame.WinFrame
        ttk.Frame
    """

    def __init__(self):
        lr_lib.gui.wrsp.win_text.WinText.__init__(self)

        self.t4 = tk.Label(self.mid_frame, text='(4)', font=(lr_vars.DefaultFont + ' italic bold'), padx=0, pady=0,
                           foreground='brown')
        # (4) Parts
        self.comboParts = ttk.Combobox(
            self.mid_frame, justify='center', width=5, font=(lr_vars.DefaultFont + ' bold'),
        )

        # (5) Lb/Rb
        self.LB = lr_lib.gui.widj.lbrb5.LBRBText('LB', self)
        self.RB = lr_lib.gui.widj.lbrb5.LBRBText('RB', self)
        self.LB.tag_configure('right', justify='right')

        self.last_frameCbx1 = ttk.Label(self.LB.label_info, padding="0 0 0 0")
        self.last_frameCbx2 = ttk.Label(self.RB.label_info, padding="0 0 0 0")

        self.t5l = tk.Label(
            self, text='(5)', font=(lr_vars.DefaultFont + ' italic bold'), padx=0, pady=0, foreground='brown',
        )
        self.t5r = tk.Label(
            self, text='(5)', font=(lr_vars.DefaultFont + ' italic bold'), padx=0, pady=0, foreground='brown',
        )

        spl = [
            lr_lib.core.var.vars_param.SplitList,
            lr_lib.core.var.vars_param._SplitList0,
            lr_lib.core.var.vars_param._SplitList1,
            lr_lib.core.var.vars_param._SplitList2,
            lr_lib.core.var.vars_param._SplitList_3,
            list(string.whitespace),
            'list(string.ascii_letters)',
            'list(string.digits)',
            'list(string.punctuation)',
        ]
        split_list = tuple(map(str, spl))

        # --- LB ---
        self.ButtonNewLB = tk.Button(
            self.last_frameCbx1, text='reset', command=self.comboParts_change, font=(lr_vars.DefaultFont + ' italic'),
            width=4, padx=0, pady=0, relief='groove',
        )
        self.LBcbx_return = tk.Checkbutton(
            self.last_frameCbx1, variable=lr_vars.VarReturnLB, text='\\n', font=(lr_vars.DefaultFont + ' italic'),
            command=self.comboParts_change, padx=0, pady=0, anchor=tk.S,
        )
        self.LBcbx_rus = tk.Checkbutton(
            self.last_frameCbx1, variable=lr_vars.VarRusLB, text='ascii', font=(lr_vars.DefaultFont + ' italic'),
            command=self.comboParts_change, padx=0, pady=0,
        )
        self.lb_split_label = tk.LabelFrame(self.last_frameCbx1, bd=1, padx=0, pady=0, )

        self.LBcbx_SplitList = tk.Checkbutton(
            self.lb_split_label, variable=lr_vars.VarSplitListLB, text='split', font=(lr_vars.DefaultFont + ' bold'),
            command=self.spl_cbx_cmd_lb, padx=0, pady=0,
        )
        self.LBent_SplitList = ttk.Combobox(self.lb_split_label, font=lr_vars.DefaultFont, width=2, )
        self.LBent_SplitList['values'] = list(split_list)
        self.LBent_SplitList.current(0)

        self.LBSpinSplitList = tk.Spinbox(
            self.lb_split_label, from_=0, to=100, textvariable=lr_vars.VarSplitListNumLB, width=2,
            font=lr_vars.DefaultFont, command=self.comboParts_change,
        )
        self.max_lb = tk.Entry(
            self.last_frameCbx1, width=4, textvariable=lr_vars.VarMaxLenLB, justify='center', foreground='grey',
            background=lr_lib.core.var.vars_highlight.Background, font=(lr_vars.DefaultFont + ' italic'),
        )
        self.spin_LB_height = tk.Spinbox(
            self.last_frameCbx1, from_=1, to=99, textvariable=self.LB.heightVar, width=2, command=self.LB.set_height,
            font=(lr_vars.DefaultFont + ' italic'), background=lr_lib.core.var.vars_highlight.Background,
        )
        cmd1 = lambda: self.lr_note(self.LB)
        self.ButtonLB_note = tk.Button(
            self.last_frameCbx1, text='note', command=cmd1, width=3,
            font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0, relief='groove',
        )
        self.partNumEmptyLbNext = tk.Checkbutton(
            self.last_frameCbx1, variable=lr_vars.VarPartNumEmptyLbNext, text='empty',
            font=(lr_vars.DefaultFont + ' bold'), padx=0, pady=0,
        )
        self.partNumDenyLbNext = tk.Checkbutton(
            self.last_frameCbx1, variable=lr_vars.VarPartNumDenyLbNext, text='deny',
            font=(lr_vars.DefaultFont + ' bold'), padx=0, pady=0,
        )
        self.LbB1Cbx = tk.Checkbutton(
            self.lb_split_label, variable=lr_vars.VarLbB1, text='{}', font=lr_vars.DefaultFont, padx=0, pady=0,
        )
        self.LbB2Cbx = tk.Checkbutton(
            self.lb_split_label, variable=lr_vars.VarLbB2, text='[]', font=lr_vars.DefaultFont, padx=0, pady=0,
        )
        self.LbRstripCbx = tk.Checkbutton(
            self.last_frameCbx1, variable=lr_vars.VarLbLstrip, text='strip', font=lr_vars.DefaultFont, padx=0, pady=0,
        )
        self.LbEndCbx = tk.Checkbutton(
            self.last_frameCbx1, variable=lr_vars.VarLEnd, text='end', font=lr_vars.DefaultFont, padx=0, pady=0,
        )

        # --- RB ---
        self.ButtonNewRB = tk.Button(
            self.last_frameCbx2, text='reset', command=self.comboParts_change, font=(lr_vars.DefaultFont + ' italic'),
            width=4, padx=0, pady=0, relief='groove',
        )
        self.RBcbx_return = tk.Checkbutton(
            self.last_frameCbx2, variable=lr_vars.VarReturnRB, text='\\n', font=(lr_vars.DefaultFont + ' italic'),
            command=self.comboParts_change, padx=0, pady=0,
        )
        self.RBcbx_rus = tk.Checkbutton(
            self.last_frameCbx2, variable=lr_vars.VarRusRB, text='ascii', font=(lr_vars.DefaultFont + ' italic'),
            command=self.comboParts_change, padx=0, pady=0,
        )
        self.rb_split_label = tk.LabelFrame(
            self.last_frameCbx2, bd=1, padx=0, pady=0,
        )

        self.RBcbx_SplitList = tk.Checkbutton(
            self.rb_split_label, variable=lr_vars.VarSplitListRB, text='split', font=(lr_vars.DefaultFont + ' bold'),
            command=self.spl_cbx_cmd_rb, padx=0, pady=0,
        )
        self.RBent_SplitList = ttk.Combobox(self.rb_split_label, font=lr_vars.DefaultFont, width=2, )
        self.RBent_SplitList['values'] = list(split_list)
        self.RBent_SplitList.current(0)

        self.RBSpinSplitList = tk.Spinbox(
            self.rb_split_label, from_=0, to=100, textvariable=lr_vars.VarSplitListNumRB, width=2,
            font=lr_vars.DefaultFont, command=self.comboParts_change,
        )

        self.max_rb = tk.Entry(
            self.last_frameCbx2, width=4, textvariable=lr_vars.VarMaxLenRB, justify='center', foreground='grey',
            background=lr_lib.core.var.vars_highlight.Background, font=(lr_vars.DefaultFont + ' italic'),
        )
        self.partNumEmptyRbNext = tk.Checkbutton(
            self.last_frameCbx2, variable=lr_vars.VarPartNumEmptyRbNext, text='empty',
            font=(lr_vars.DefaultFont + ' bold'), padx=0, pady=0,
        )
        self.partNumDenyRbNext = tk.Checkbutton(
            self.last_frameCbx2, variable=lr_vars.VarPartNumDenyRbNext, text='deny',
            font=(lr_vars.DefaultFont + ' bold'), padx=0, pady=0,
        )
        self.spin_RB_height = tk.Spinbox(
            self.last_frameCbx2, from_=1, to=99, textvariable=self.RB.heightVar, width=2, command=self.RB.set_height,
            font=(lr_vars.DefaultFont + ' italic'), background=lr_lib.core.var.vars_highlight.Background,
        )
        cmd2 = lambda: self.lr_note(self.RB)
        self.ButtonRB_note = tk.Button(
            self.last_frameCbx2, text='note', command=cmd2, width=3,
            font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0, relief='groove',
        )
        self.RbB1Cbx = tk.Checkbutton(
            self.rb_split_label, variable=lr_vars.VarRbB1, text='{}', font=lr_vars.DefaultFont, padx=0, pady=0,
        )
        self.RbB2Cbx = tk.Checkbutton(
            self.rb_split_label, variable=lr_vars.VarRbB2, text='[]', font=lr_vars.DefaultFont, padx=0, pady=0,
        )
        self.RbRstripCbx = tk.Checkbutton(
            self.last_frameCbx2, variable=lr_vars.VarRbRstrip, text='strip', font=lr_vars.DefaultFont, padx=0, pady=0,
        )
        self.RbEndCbx = tk.Checkbutton(
            self.last_frameCbx2, variable=lr_vars.VarREnd, text='end', font=lr_vars.DefaultFont, padx=0, pady=0,
        )

        #
        self.LBent_SplitList.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.LBent_SplitList.bind("<KeyRelease-Return>", self.comboParts_change)
        self.max_lb.bind("<KeyRelease-Return>", self.comboParts_change)

        self.RBent_SplitList.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.RBent_SplitList.bind("<KeyRelease-Return>", self.comboParts_change)
        self.max_rb.bind("<KeyRelease-Return>", self.comboParts_change)

        self.comboParts.bind("<<ComboboxSelected>>", self.comboParts_change)
        self.comboParts['values'] = [0]
        self.comboParts.current(0)
        return

    def comboParts_change(self, *args) -> None:
        """
        смена комбо(4)
        """
        if not lr_vars.FilesWithParam:
            return
        i = self.comboParts.get()
        i = int(i)
        lr_vars.VarPartNum.set(i)
        lr_lib.gui.widj.lbrb5.LBRBText.set_LB_RB()
        self.show_frame_info_file()
        return

    def show_frame_info_file(self) -> None:
        """
        отображение всякой информации
        """
        dt = lr_vars.VarWrspDict.get()

        t1 = '"{param}", {Name}, {inf_nums} > Файлы(из {files_all} найдено {file_index}/{param_files}) ' \
             '| Вхождения({param_part}/{param_count}, всего {param_all} в {_param_inf_all} inf) | {ver}'

        lr_vars.Tk.title(t1.format(ver=lr_vars.VERSION, **dt))

        t2 = 'Snapshot{inf_nums}, Файл[{file_index}/{param_files}], ' \
             'Часть[{param_part}/{param_count}], {len} символов.'

        self.main_frame['text'] = t2.format(**dt)
        return

    def spl_cbx_cmd_lb(self, *a) -> None:
        """
        lb SplitList widj
        """
        if lr_vars.VarSplitListLB.get():
            self.LBent_SplitList.configure(state='normal')
            self.LBSpinSplitList.configure(state='normal')
            self.LbB1Cbx.configure(state='normal')
            self.LbB2Cbx.configure(state='normal')
        else:
            self.LBent_SplitList.configure(state='disabled')
            self.LBSpinSplitList.configure(state='disabled')
            self.LbB1Cbx.configure(state='disabled')
            self.LbB2Cbx.configure(state='disabled')

        self.comboParts_change()
        return

    def spl_cbx_cmd_rb(self, *a) -> None:
        """
        rb SplitList widj
        """
        if lr_vars.VarSplitListRB.get():
            self.RBent_SplitList.configure(state='normal')
            self.RBSpinSplitList.configure(state='normal')
            self.RbB1Cbx.configure(state='normal')
            self.RbB2Cbx.configure(state='normal')
        else:
            self.RBent_SplitList.configure(state='disabled')
            self.RBSpinSplitList.configure(state='disabled')
            self.RbB1Cbx.configure(state='disabled')
            self.RbB2Cbx.configure(state='disabled')

        self.comboParts_change()
        return

    @lr_lib.core.var.etc.vars_other.T_POOL_decorator
    def lr_note(self, ob) -> None:
        """
        открыть в блокноте
        """
        t = ob.get()
        lr_lib.core.etc.other.openTextInEditor(t)
        return
