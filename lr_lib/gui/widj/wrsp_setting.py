# -*- coding: UTF-8 -*-
# окно настройки каментов и имени wrsp

import tkinter as tk

import lr_lib
import lr_lib.core.var.vars as lr_vars


class WrspSettingWindow(tk.Toplevel):
    """настройка каментов и имени wrsp"""
    def __init__(self, parent: 'lr_lib.gui.action.main_action.ActionWindow'):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка каментов и имени wrsp')

        t1 = '''для web_: //lr: IN(7)<-[2]: aFFX9(P:5/84|S:72=[1:875]|T:41), azzR3(P:2/2|S:1=[1]|T:1)
        для web_: //lr: OUT(2)-> aAB20(P:3|S:2=[2:4]|T:2), aFFT7(P:874|S:874=[1:875]|T:41)
        для WRSP: //lr: (login: 3=[1:3]) -> Param:3 | Snapshots:2=[2:4] | Transactions=2:['login', 'logout']'''
        t2 = '''
        * расшишровка(есть разные, но смысл тот же) для aFFX9(P:1/874|S:874=[1:875]|T:41) :
            "aFFX9" - исходный param, для WRSP имени "{P_6637_2__login__Button__aFFX9__auth}"
            "P:5/84" - кол-во использований aFFX9 : "в текущем Snapshot"(необязат) / "во всх Snapshot's"
            "S:72=[1:875]" - кол-во Snapshot's, использующих aFFX9 : кол-во=[мин_номер : макс_номер(необязат)]
            "T:41" - кол-во транзакций, использующих aFFX9'''
        laf = tk.LabelFrame(self, text='{t1}\n{t2}\n'.format(t1=t1, t2=t2), font='Arial 7', labelanchor=tk.NW, bd=3)
        t3 = '{p}\n{w}\n'.format(p='{P_6637_2__login__Button__a_FFX_9__auth}', w=lr_lib.core.wrsp.param.WEB_REG_NUM)
        _lab = tk.LabelFrame(self, text=t3, bd=3)
        _lab1 = tk.LabelFrame(_lab, text='{letter}')
        _lab2 = tk.LabelFrame(_lab, text='{wrsp_rnd_num}')
        _lab3 = tk.LabelFrame(_lab, text='{infs}')
        _lab4 = tk.LabelFrame(_lab, text='{transaction}')
        _lab5 = tk.LabelFrame(_lab, text='{lb_name}')
        _lab6 = tk.LabelFrame(_lab, text='{wrsp_name}')
        _lab7 = tk.LabelFrame(_lab, text='{rb_name}')
        _lab8 = tk.LabelFrame(_lab, text='"aFFX9" -> "a_FFX_9"')

        tt_stat = 'коментарии с именем транзакции\n//lr: "login"(1/3=[1:3])'
        VarWebStatsTransac = tk.Checkbutton(laf, text=tt_stat, font='Arial 7',
                                            variable=lr_vars.VarWebStatsTransac, justify='left')

        tt_in = 'IN коментарии\n//lr: IN(7)<-[2]: aFFX9( ...'
        VarWebStatsIn = tk.Checkbutton(laf, text=tt_in, font='Arial 7', justify='left',
                                       variable=lr_vars.VarWebStatsIn)

        tt_out = 'OUT коментарии\n//lr: OUT(2)-> aAB20( ...'
        VarWebStatsOut = tk.Checkbutton(laf, text=tt_out, font='Arial 7', justify='left',
                                        variable=lr_vars.VarWebStatsOut)

        tt_warn = "WARNING коментарии\n//lr: WARNING: NO ASCII Symbols(rus?)"
        VarWebStatsWarn = tk.Checkbutton(laf, text=tt_warn, font='Arial 7', justify='left',
                                         variable=lr_vars.VarWebStatsWarn)

        tt_wrsp_trn = "WRSP, имена транзакций, использующих param\n" \
                      "<< ... :['login', 'logout']"
        VarWRSPStatsTransacNames = tk.Checkbutton(laf, text=tt_wrsp_trn, font='Arial 7', justify='left',
                                                  variable=lr_vars.VarWRSPStatsTransacNames)

        tt_wrsp_transac = 'статистика использования WRSP\n' \
                          '//lr: (login: 3=[1:3]) -> Param:3 ...ons=2'

        def set_WRSPStatsTransac() -> None:
            """VarWRSPStatsTransacNames state='disabled"""
            if lr_vars.VarWRSPStatsTransac.get():
                VarWRSPStatsTransacNames.config(state='normal')
            else:
                VarWRSPStatsTransacNames.config(state='disabled')
            return

        set_WRSPStatsTransac()
        VarWRSPStatsTransac = tk.Checkbutton(laf, text=tt_wrsp_transac, font='Arial 7', justify='left',
                                             variable=lr_vars.VarWRSPStatsTransac, command=set_WRSPStatsTransac)

        tt_wrsp_st = 'WRSP, подробные/короткие коментарии\n' \
                     'Изменится при пересоздании param\nкороткие(off): // PARAM["aFFX5"] // Snap[1]'
        VarWRSPStats = tk.Checkbutton(laf, text=tt_wrsp_st, font='Arial 7', justify='left',
                                      variable=lr_vars.VarWRSPStats)

        tt_SnapshotInName = 'Snapshot-родителя в имени WRSP\nИзменится при пересоздании param\n' \
                            'P_6637__aFFX9 -> P_6637_2__aFFX9'
        SnapshotInName = tk.Checkbutton(_lab3, text=tt_SnapshotInName, font='Arial 7', justify='left',
                                        variable=lr_vars.SnapshotInName)

        TransactionInNameMax = tk.Spinbox(_lab4, font='Arial 7', from_=-1, to=1000,
                                          textvariable=lr_vars.TransactionInNameMax)

        MaxLbWrspName = tk.Spinbox(_lab5, textvariable=lr_vars.MaxLbWrspName, font='Arial 7', from_=-1, to=1000)
        MaxRbWrspName = tk.Spinbox(_lab7, textvariable=lr_vars.MaxRbWrspName, font='Arial 7', from_=-1, to=1000)
        MaxParamWrspName = tk.Spinbox(_lab6, textvariable=lr_vars.MaxParamWrspName, font='Arial 7', from_=-1, to=1000)
        MinWrspRnum = tk.Spinbox(_lab2, textvariable=lr_vars.MinWrspRnum, font='Arial 7', from_=-1, to=1000)
        MaxWrspRnum = tk.Spinbox(_lab2, textvariable=lr_vars.MaxWrspRnum, font='Arial 7', from_=-1, to=10**5)
        wrsp_name_splitter = tk.Entry(_lab8, textvariable=lr_vars.wrsp_name_splitter, font='Arial 7')
        WrspNameFirst = tk.Entry(_lab1, textvariable=lr_vars.WrspNameFirst, font='Arial 7')

        apply_btn = tk.Button(self, font='Arial 8 bold', text='Применить',
                              command=lambda: self.parent.save_action_file(file_name=False))
        wrsp_rename_btn = tk.Button(self, font='Arial 7', text='wrsp_rename', command=self.all_wrsp_rename)
        wrsp_auto_rename_btn = tk.Button(_lab, font='Arial 8 bold italic', text='wrsp_auto_rename',
                                         command=lambda *_: lr_lib.gui.etc.action_lib.all_wrsp_auto_rename(self.parent))

        lr_lib.gui.widj.tooltip.createToolTip(apply_btn, 'применить изменения')
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsTransac, tt_stat)
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsIn, tt_in)
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsOut, tt_out)
        lr_lib.gui.widj.tooltip.createToolTip(VarWebStatsWarn, tt_warn)
        lr_lib.gui.widj.tooltip.createToolTip(VarWRSPStatsTransac, tt_wrsp_transac)
        lr_lib.gui.widj.tooltip.createToolTip(VarWRSPStatsTransacNames, tt_wrsp_trn)
        lr_lib.gui.widj.tooltip.createToolTip(VarWRSPStats, tt_wrsp_st)
        lr_lib.gui.widj.tooltip.createToolTip(SnapshotInName, tt_SnapshotInName)
        lr_lib.gui.widj.tooltip.createToolTip(TransactionInNameMax, '{transaction}\nв WRSP имени, использовать символы(максимум) имени транзакции\n'
                                                       'Изменится при пересоздании param\n'
                                                       '0 - все\n'
                                                       '-1 - откл')
        lr_lib.gui.widj.tooltip.createToolTip(MaxLbWrspName, '{lb_name}\nмакс число символов, взятых из LB, для WRSP имени\n'
                                                'Изменится при пересоздании param\n'
                                                '0 - все\n'
                                                '-1 - откл')
        lr_lib.gui.widj.tooltip.createToolTip(MaxRbWrspName, '{rb_name}\nмакс число символов, взятых из RB, для WRSP имени\n'
                                                'Изменится при пересоздании param\n'
                                                '0 - все\n'
                                                '-1 - откл')
        lr_lib.gui.widj.tooltip.createToolTip(MaxParamWrspName, '{wrsp_name}\nмакс число символов, взятых из param, для WRSP имени\n'
                                                   'Изменится при пересоздании param\n'
                                                   '0 - все\n'
                                                   '-1 - откл')
        lr_lib.gui.widj.tooltip.createToolTip(MinWrspRnum, '{wrsp_rnd_num}\nмин число, для случайного номера, в WRSP имени\n'
                                              'Изменится при пересоздании param\n'
                                              '0 - все\n'
                                              '-1 - откл')
        lr_lib.gui.widj.tooltip.createToolTip(MaxWrspRnum, '{wrsp_rnd_num}\nмакс число, для случайного номера, в WRSP имени\n'
                                              'Изменится при пересоздании param\n'
                                              '0 - все\n'
                                              '-1 - откл')
        lr_lib.gui.widj.tooltip.createToolTip(wrsp_name_splitter, 'символ разделения в имени WRSP\nдля "_" : "aFFX9" -> "a_FFX_9"\n'
                                                     'Изменится при пересоздании param\nничего - откл')
        lr_lib.gui.widj.tooltip.createToolTip(WrspNameFirst, '{letter}\nначало(P) WRSP имени: {P_6637_2_aFFX9}\n'
                                                'Изменится при пересоздании param\n'
                                                'ничего - откл')

        lr_lib.gui.widj.tooltip.createToolTip(wrsp_rename_btn, 'скопом переименовать, все уже созданные web_reg_save_param\n'
                                                  'имена слева, не трогать\nимена справа, переименовать, либо не трогать')
        lr_lib.gui.widj.tooltip.createToolTip(wrsp_auto_rename_btn, 'автоматически переименовать(пересоздание имени), '
                                                       'все уже созданные web_reg_save_param\n'
                                                       'с учетом всех настроек имени,\n'
                                                       'и изменения имен транзакций, после его создания\n\n'
                                                       'имена слева, не трогать\nимена справа, переименовать, либо не трогать')

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

    @lr_vars.T_POOL_decorator
    def all_wrsp_rename(self, *args) -> None:
        """переименавать все wrsp, вручную"""
        _wrsps = tuple(self.parent.web_action.get_web_reg_save_param_all())
        wrsps = tuple(w.name for w in _wrsps)
        mx = max(map(len, wrsps or ['']))
        m = ('"{:<%s}" -> "{}"' % mx)
        all_wrsps = '\n'.join(m.format(old, new) for (old, new) in zip(wrsps, wrsps))
        y = lr_lib.gui.widj.dialog.YesNoCancel(['Переименовать', 'Отмена'], 'Переименовать wrsp слева',
                                  'в wrsp справа', 'wrsp', parent=self, is_text=all_wrsps)

        if y.ask() == 'Переименовать':
            new_wrsps = [t.split('-> "', 1)[1].split('"', 1)[0].strip() for t in y.text.strip().split('\n')]
            assert (len(wrsps) == len(new_wrsps))
            with self.parent.block():
                self.parent.backup()
                text = self.parent.tk_text.get('1.0', tk.END)

                for (old, new) in zip(wrsps, new_wrsps):
                    text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old), lr_lib.core.wrsp.param.param_bounds_setter(new))
                    text = text.replace(lr_lib.core.wrsp.param.param_bounds_setter(old, start='"', end='"'),
                                        lr_lib.core.wrsp.param.param_bounds_setter(new, start='"', end='"'))
                    continue

                self.parent.web_action.set_text_list(text, websReport=True)
                self.parent.web_action_to_tk_text(websReport=False)
        return
