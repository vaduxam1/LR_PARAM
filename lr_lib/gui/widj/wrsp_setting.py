# -*- coding: UTF-8 -*-
# окно настройки каментов и имени wrsp

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_other
import lr_lib.core_gui.rename


class WrspSettingWindow(tk.Toplevel):
    """настройка каментов и имени wrsp"""
    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow'):
        super().__init__(padx=0, pady=0)
        self.title('настройка каментов и имени wrsp')
        self.transient(self.parent)
        self.resizable(width=False, height=False)

        self.parent = parent

        laf = tk.LabelFrame(self, text='{t1}\n{t2}\n'.format(t1='', t2=TTR), font='Arial 7', labelanchor=tk.NW, bd=3)
        _lab = tk.LabelFrame(self, text=t3, bd=3)
        _lab1 = tk.LabelFrame(_lab, text='{letter}')
        _lab2 = tk.LabelFrame(_lab, text='{wrsp_rnd_num}')
        _lab3 = tk.LabelFrame(_lab, text='{infs}')
        _lab4 = tk.LabelFrame(_lab, text='{transaction}')
        _lab5 = tk.LabelFrame(_lab, text='{lb_name}')
        _lab6 = tk.LabelFrame(_lab, text='{wrsp_name}')
        _lab7 = tk.LabelFrame(_lab, text='{rb_name}')
        _lab8 = tk.LabelFrame(_lab, text='"aFFX9" -> "a_FFX_9"')

        VarWebStatsTransac = tk.Checkbutton(
            laf, text=tt_stat, font='Arial 7', variable=lr_vars.VarWebStatsTransac, justify='left',
        )
        VarWebStatsIn = tk.Checkbutton(
            laf, text=tt_in, font='Arial 7', justify='left', variable=lr_vars.VarWebStatsIn,
        )
        VarWebStatsOut = tk.Checkbutton(
            laf, text=tt_out, font='Arial 7', justify='left', variable=lr_vars.VarWebStatsOut,
        )
        VarWebStatsWarn = tk.Checkbutton(
            laf, text=tt_warn, font='Arial 7', justify='left', variable=lr_vars.VarWebStatsWarn,
        )
        VarWRSPStatsTransacNames = tk.Checkbutton(
            laf, text=tt_wrsp_trn, font='Arial 7', justify='left', variable=lr_vars.VarWRSPStatsTransacNames,
        )

        def set_WRSPStatsTransac() -> None:
            """VarWRSPStatsTransacNames state='disabled"""
            if lr_vars.VarWRSPStatsTransac.get():
                VarWRSPStatsTransacNames.config(state='normal')
            else:
                VarWRSPStatsTransacNames.config(state='disabled')
            return

        set_WRSPStatsTransac()
        VarWRSPStatsTransac = tk.Checkbutton(
            laf, text=tt_wrsp_transac, font='Arial 7', justify='left', variable=lr_vars.VarWRSPStatsTransac,
            command=set_WRSPStatsTransac,
        )

        VarWRSPStats = tk.Checkbutton(
            laf, text=tt_wrsp_st, font='Arial 7', justify='left', variable=lr_vars.VarWRSPStats,
        )
        SnapshotInName = tk.Checkbutton(
            _lab3, text=tt_SnapshotInName, font='Arial 7', justify='left', variable=lr_vars.SnapshotInName,
        )
        TransactionInNameMax = tk.Spinbox(
            _lab4, font='Arial 7', from_=-1, to=1000, textvariable=lr_vars.TransactionInNameMax,
        )

        MaxLbWrspName = tk.Spinbox(_lab5, textvariable=lr_vars.MaxLbWrspName, font='Arial 7', from_=-1, to=1000)
        MaxRbWrspName = tk.Spinbox(_lab7, textvariable=lr_vars.MaxRbWrspName, font='Arial 7', from_=-1, to=1000)
        MaxParamWrspName = tk.Spinbox(_lab6, textvariable=lr_vars.MaxParamWrspName, font='Arial 7', from_=-1, to=1000)
        MinWrspRnum = tk.Spinbox(_lab2, textvariable=lr_vars.MinWrspRnum, font='Arial 7', from_=-1, to=1000)
        MaxWrspRnum = tk.Spinbox(_lab2, textvariable=lr_vars.MaxWrspRnum, font='Arial 7', from_=-1, to=10**5)
        wrsp_name_splitter = tk.Entry(_lab8, textvariable=lr_vars.wrsp_name_splitter, font='Arial 7')
        WrspNameFirst = tk.Entry(_lab1, textvariable=lr_vars.WrspNameFirst, font='Arial 7')

        apply_btn = tk.Button(
            self, font='Arial 8 bold', text='Применить', command=lambda: self.parent.save_action_file(file_name=False),
        )
        wrsp_rename_btn = tk.Button(
            self, font='Arial 7', text='wrsp_rename',
            command=lambda *_: lr_lib.core_gui.rename.all_wrsp_rename(self.parent, parent=self),
        )
        wrsp_auto_rename_btn = tk.Button(
            _lab, font='Arial 8 bold italic', text='wrsp_auto_rename',
            command=lambda *_: lr_lib.core_gui.rename.all_wrsp_auto_rename(self.parent),
        )

        lr_lib.gui.widj.tooltip.createToolTip(apply_btn, 'применить изменения')
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsTransac, tt_stat)
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsIn, tt_in)
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsOut, tt_out)
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsWarn, tt_warn)
        lr_lib.gui.widj.tooltip.createToolTip(VarWRSPStatsTransac, tt_wrsp_transac)
        lr_lib.gui.widj.tooltip.createToolTip(VarWRSPStatsTransacNames, tt_wrsp_trn)
        lr_lib.gui.widj.tooltip.createToolTip(VarWRSPStats, tt_wrsp_st)
        lr_lib.gui.widj.tooltip.createToolTip(SnapshotInName, tt_SnapshotInName)

        lr_lib.gui.widj.tooltip.createToolTip(
            TransactionInNameMax,
            '{transaction}\nв WRSP имени, использовать символы(максимум) имени транзакции\n'
            'Изменится при пересоздании param\n'
            '0 - все\n'
            '-1 - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            MaxLbWrspName,
            '{lb_name}\nмакс число символов, взятых из LB, для WRSP имени\n'
            'Изменится при пересоздании param\n'
            '0 - все\n'
            '-1 - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            MaxRbWrspName,
            '{rb_name}\nмакс число символов, взятых из RB, для WRSP имени\n'
            'Изменится при пересоздании param\n'
            '0 - все\n'
            '-1 - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            MaxParamWrspName,
            '{wrsp_name}\nмакс число символов, взятых из param, для WRSP имени\n'
            'Изменится при пересоздании param\n'
            '0 - все\n'
            '-1 - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            MinWrspRnum,
            '{wrsp_rnd_num}\nмин число, для случайного номера, в WRSP имени\n'
            'Изменится при пересоздании param\n'
            '0 - все\n'
            '-1 - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            MaxWrspRnum,
            '{wrsp_rnd_num}\nмакс число, для случайного номера, в WRSP имени\n'
            'Изменится при пересоздании param\n'
            '0 - все\n'
            '-1 - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            wrsp_name_splitter,
            'символ разделения в имени WRSP\nдля "_" : "aFFX9" -> "a_FFX_9"\n'
            'Изменится при пересоздании param\nничего - откл'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            WrspNameFirst,
            '{letter}\nначало(P) WRSP имени: {P_6637_2_aFFX9}\n'
            'Изменится при пересоздании param\n'
            'ничего - откл'
        )

        lr_lib.gui.widj.tooltip.createToolTip(
            wrsp_rename_btn,
            'скопом переименовать, все уже созданные web_reg_save_param\n'
            'имена слева, не трогать\nимена справа, переименовать, либо не трогать'
                                              )
        lr_lib.gui.widj.tooltip.createToolTip(
            wrsp_auto_rename_btn,
            'автоматически переименовать(пересоздание имени), '
            'все уже созданные web_reg_save_param\n'
            'с учетом всех настроек имени,\n'
            'и изменения имен транзакций, после его создания\n\n'
            'имена слева, не трогать\nимена справа, переименовать, либо не трогать'
        )

        laf.grid(row=1, column=1, sticky=tk.W, columnspan=3)

        VarWebStatsTransac.grid(row=2, column=1, sticky=tk.W)
        VarWebStatsIn.grid(row=1, column=1, sticky=tk.W)
        VarWebStatsOut.grid(row=1, column=2, sticky=tk.W)
        VarWebStatsWarn.grid(row=2, column=2, sticky=tk.W)
        VarWRSPStatsTransac.grid(row=3, column=1, sticky=tk.W)
        VarWRSPStatsTransacNames.grid(row=3, column=2, sticky=tk.W)
        VarWRSPStats.grid(row=4, column=1, sticky=tk.W, columnspan=3)
        SnapshotInName.grid(row=4, column=2, sticky=tk.W)

        MaxLbWrspName.grid(row=5, column=1)
        MaxRbWrspName.grid(row=5, column=2)
        MaxParamWrspName.grid(row=6, column=1)
        MinWrspRnum.grid(row=6, column=2)
        MaxWrspRnum.grid(row=7, column=2)
        wrsp_name_splitter.grid(row=8, column=2)
        WrspNameFirst.grid(row=8, column=1)
        TransactionInNameMax.grid(row=7, column=1)

        apply_btn.grid(row=10, column=2)
        wrsp_rename_btn.grid(row=10, column=1)
        wrsp_auto_rename_btn.grid(row=5, column=3, sticky=tk.S, columnspan=2)

        _lab.grid(row=5, column=1, columnspan=3)
        _lab8.grid(row=5, column=1)
        _lab1.grid(row=5, column=2)
        _lab2.grid(row=6, column=1)
        _lab3.grid(row=6, column=2)
        _lab4.grid(row=6, column=3)
        _lab5.grid(row=7, column=1)
        _lab6.grid(row=7, column=2)
        _lab7.grid(row=7, column=3)

        lr_lib.gui.etc.gui_other.center_widget(self)
        return


TTR = '''
* расшишровка(есть разные, но смысл тот же) для aFFX9(P:1/874|S:874=[1:875]|T:41) :

  "aFFX9" - исходный param, для WRSP имени "{P_6637_2__login__Button__aFFX9__auth}"
  "P:5/84" - кол-во использований aFFX9 : "в текущем Snapshot"(необязат) / "во всх Snapshot's"
  "S:72=[1:875]" - кол-во Snapshot's, использующих aFFX9 : кол-во=[мин_номер : макс_номер(необязат)]
  "T:41" - кол-во транзакций, использующих aFFX9
'''.strip()

tt_stat = '''
Коментарии с именем транзакции.
    //lr: "Choice_status"(5/8=[25:32])
    web_submit_data("...
'''.strip()

tt_in = '''
IN коментарии.
    //lr: IN(3)<-[2]: z__5j(P:1/34|S:34=[2:35]|T:6),
                     bJsP2c(P:2/2|S:1=[13]|T:1)
    web_submit_data("...
'''.strip()

tt_out = '''
OUT коментарии.
    //lr: OUT(1)-> bJsPec(P:1|S:1=[14]|T:1)
    web_submit_data("...
'''.strip()

tt_warn = '''
WARNING коментарии.
    //lr: WARNING: NO ASCII Symbols(rus?)
    web_submit_data("...
'''.strip()

tt_wrsp_trn = '''
WRSP, имена транзакций, использующих param
 //lr: (NoTransaction_3: 18=[7:24]) -> ...
            | Transactions=1:['Choice_status']
 web_reg_save_param(...
'''.strip()

tt_wrsp_transac = '''
Статистика использования WRSP.
 //lr: (NoTransaction_3: 18=[7:24]) ->
    Param:3 | Snapshots:1=[26] | Transactions=1:
 web_reg_save_param(...
'''.strip()

tt_wrsp_st = '''
WRSP, короткие/подробные коментарии. Изменится при пересоздании param.

 Короткие (Off) однострочные:
    // PARAM["bJsP2h"] // Snap[23] // FILE["t23.txt"]
    web_reg_save_param(...

 Подробные (On) двухстрочные:
    // Snap[23], [1:35]=35 -> [23:32]=5 | FILE["t23.txt"], with_param = 1/5 | 20:42:01-07/12/18
    // PARAM["bJsP2h"], count=1/1, NA=0 | LB[21~21] NA=0, RB[22~22] NA=0
    web_reg_save_param(...
'''

tt_SnapshotInName = '''
Snapshot-родителя в имени WRSP.
Изменится при пересоздании param.
  P_3080__bJsP2h -> P_3080_23__bJsP2h
'''.strip()

t3 = '{p}\n{w}\n'.format(p='{P_6637_2__login__Button__a_FFX_9__auth}', w=lr_lib.core.wrsp.param.WEB_REG_NUM)
