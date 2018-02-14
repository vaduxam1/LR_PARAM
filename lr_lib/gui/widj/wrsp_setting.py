# -*- coding: UTF-8 -*-
# окно настройки каментов и имени wrsp

import tkinter as tk

import lr_lib.gui.etc.gui_other

import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param


class WrspSettingWindow(tk.Toplevel):
    '''настройка каментов и имени wrsp'''
    def __init__(self, *args, parent=None):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка каментов и имени wrsp')

        t1 = '''
        //lr: IN(1)<-[1]: z_k620(P:1/874|S:874=[1:875]|T:41)
        //lr: OUT(2)-> aFFX9(P:3|S:2=[2:4]|T:2), z_k620(P:874|S:874=[1:875]|T:41)
        //lr: (login: 3=[1:3]) -> Param:3 | Snapshots:2=[2:4] | Transactions=2:['login', 'logout']
        '''
        t2 = '''
        z_k620(P:1/874|S:874=[1:875]|T:41)
            z_k620 - исходный param, для WRSP {P_2092_2__login__Button__z_k620__auth}
            P:1/874 - сколько раз использован данный param: текущий Snapshot / все Snapshot's
            S:874=[1:875] - Snapshot's, использующие данный param: кол-во = [ мин номер : макс номер ]
            T:41 - кол-во транзакций, использующих данный param
        '''
        t3 = '{p}\n{w}\n'.format(p='{P_2092_2__login__Button__z_k620__auth}', w=lr_param.WEB_REG_NUM)
        laf = tk.LabelFrame(self, text='{t1}\n{t2}\n{t3}\n'.format(t1=t1, t2=t2, t3=t3), font='Arial 7', labelanchor=tk.NW)

        tt_stat = 'коментарии с именем транзакции\n//lr: "login"(1/3=[1:3])'
        VarWebStatsTransac = tk.Checkbutton(laf, text=tt_stat, font='Arial 7',
                                            variable=lr_vars.VarWebStatsTransac, justify='left')
        tt_in = 'IN коментарии\n//lr: IN(1)<-[1]: z_k620(P:1 ...'
        VarWebStatsIn = tk.Checkbutton(laf, text=tt_in, font='Arial 7', justify='left',
                                       variable=lr_vars.VarWebStatsIn)
        tt_out = 'OUT коментарии\n//lr: OUT(2)-> aFFX9(P:3 ...'
        VarWebStatsOut = tk.Checkbutton(laf, text=tt_out, font='Arial 7', justify='left',
                                        variable=lr_vars.VarWebStatsOut)
        tt_warn = "WARNING коментарии\n//lr: WARNING: WrspInAndOutUsage: 1=['z_k620']"
        VarWebStatsWarn = tk.Checkbutton(laf, text=tt_warn, font='Arial 7', justify='left',
                                         variable=lr_vars.VarWebStatsWarn)
        tt_wrsp_transac = 'WRSP, статистика использования param\n' \
                          '//lr: (login: 3=[1:3]) -> Param:3 ...'
        VarWRSPStatsTransac = tk.Checkbutton(laf, text=tt_wrsp_transac, font='Arial 7', justify='left',
                                             variable=lr_vars.VarWRSPStatsTransac)
        tt_wrsp_trn = "WRSP, имена транзакций, использующих param\n" \
                      "... :['login', 'logout']"
        VarWRSPStatsTransacNames = tk.Checkbutton(laf, text=tt_wrsp_trn, font='Arial 7', justify='left',
                                                  variable=lr_vars.VarWRSPStatsTransacNames)
        tt_wrsp_st = 'WRSP, подробные/короткие коментарии\n' \
                     'Изменится только при пересоздании param\nкороткие(off): // PARAM["aFFX5"] // Snap[1]'
        VarWRSPStats = tk.Checkbutton(laf, text=tt_wrsp_st, font='Arial 7', justify='left',
                                      variable=lr_vars.VarWRSPStats)
        tt_SnapshotInName = '{infs}\nномер Snapshot-родителя в имени WRSP\n' \
                            'Изменится только при пересоздании param\n' \
                            'P_6637_1__zk620 -> P_6637__zk620'
        SnapshotInName = tk.Checkbutton(laf, text=tt_SnapshotInName, font='Arial 7', justify='left',
                                        variable=lr_vars.SnapshotInName)
        TransactionInNameMax = tk.Spinbox(laf, font='Arial 7', from_=0, to=1000,
                                          textvariable=lr_vars.TransactionInNameMax)

        MaxLbWrspName = tk.Spinbox(laf, textvariable=lr_vars.MaxLbWrspName, font='Arial 7', from_=0, to=1000)
        MaxRbWrspName = tk.Spinbox(laf, textvariable=lr_vars.MaxRbWrspName, font='Arial 7', from_=0, to=1000)
        MaxParamWrspName = tk.Spinbox(laf, textvariable=lr_vars.MaxParamWrspName, font='Arial 7', from_=0, to=1000)
        MinWrspRnum = tk.Spinbox(laf, textvariable=lr_vars.MinWrspRnum, font='Arial 7', from_=0, to=1000)
        MaxWrspRnum = tk.Spinbox(laf, textvariable=lr_vars.MaxWrspRnum, font='Arial 7', from_=0, to=10**5)
        wrsp_name_splitter = tk.Entry(laf, textvariable=lr_vars.wrsp_name_splitter, font='Arial 7')
        WrspNameFirst = tk.Entry(laf, textvariable=lr_vars.WrspNameFirst, font='Arial 7')

        apply_btn = tk.Button(laf, font='Arial 7', text='применить',
                              command=lambda: self.parent.save_action_file(file_name=False))

        lr_tooltip.createToolTip(apply_btn, 'применить изменения')
        lr_tooltip.createToolTip(VarWebStatsTransac, tt_stat)
        lr_tooltip.createToolTip(VarWebStatsIn, tt_in)
        lr_tooltip.createToolTip(VarWebStatsOut, tt_out)
        lr_tooltip.createToolTip(VarWebStatsWarn, tt_warn)
        lr_tooltip.createToolTip(VarWRSPStatsTransac, tt_wrsp_transac)
        lr_tooltip.createToolTip(VarWRSPStatsTransacNames, tt_wrsp_trn)
        lr_tooltip.createToolTip(VarWRSPStats, tt_wrsp_st)
        lr_tooltip.createToolTip(SnapshotInName, tt_SnapshotInName)
        lr_tooltip.createToolTip(TransactionInNameMax, '{transaction}\nв WRSP имени, использовать символы(максимум) имени транзакции\n'
                                                       'Изменится только при пересоздании param\n'
                                                       '0 - откл')
        lr_tooltip.createToolTip(MaxLbWrspName, '{lb_name}\nмакс число символов, взятых из LB, для WRSP имени\n'
                                                'Изменится только при пересоздании param\n'
                                                '0 - откл')
        lr_tooltip.createToolTip(MaxRbWrspName, '{rb_name}\nмакс число символов, взятых из RB, для WRSP имени\n'
                                                'Изменится только при пересоздании param\n'
                                                '0 - откл')
        lr_tooltip.createToolTip(MaxParamWrspName, '{wrsp_name}\nмакс число символов, взятых из param, для WRSP имени\n'
                                                   'Изменится только при пересоздании param\n'
                                                   '0 - откл')
        lr_tooltip.createToolTip(MinWrspRnum, '{wrsp_rnd_num}\nмин число, для случайного номера, в WRSP имени\n'
                                              'Изменится только при пересоздании param\n'
                                              '0 - откл')
        lr_tooltip.createToolTip(MaxWrspRnum, '{wrsp_rnd_num}\nмакс число, для случайного номера, в WRSP имени\n'
                                              'Изменится только при пересоздании param\n'
                                              '0 - откл')
        lr_tooltip.createToolTip(wrsp_name_splitter, 'символ разделения в имени WRSP(для "_"): "aFFX9" -> "a_FFX_9"\n'
                                                     'Изменится только при пересоздании param\nничего - откл')
        lr_tooltip.createToolTip(WrspNameFirst, '{letter}\nначало(P) WRSP имени: {P_11_zkau_22}\n'
                                                'Изменится только при пересоздании param\n'
                                                'ничего - откл')

        laf.grid(row=1, column=1, sticky=tk.W)

        VarWebStatsTransac.grid(row=2, column=1, sticky=tk.W)
        VarWebStatsIn.grid(row=1, column=1, sticky=tk.W)
        VarWebStatsOut.grid(row=1, column=2, sticky=tk.W)
        VarWebStatsWarn.grid(row=2, column=2, sticky=tk.W)
        VarWRSPStatsTransac.grid(row=3, column=1, sticky=tk.W)
        VarWRSPStatsTransacNames.grid(row=3, column=2, sticky=tk.W)
        VarWRSPStats.grid(row=4, column=1, sticky=tk.W)
        SnapshotInName.grid(row=4, column=2, sticky=tk.W)

        MaxLbWrspName.grid(row=5, column=1)
        MaxRbWrspName.grid(row=5, column=2)
        MaxParamWrspName.grid(row=6, column=1)
        MinWrspRnum.grid(row=6, column=2)
        MaxWrspRnum.grid(row=7, column=2)
        wrsp_name_splitter.grid(row=8, column=2)
        WrspNameFirst.grid(row=8, column=1)
        TransactionInNameMax.grid(row=7, column=1)

        apply_btn.grid(row=10, column=1, columnspan=3)

        lr_lib.gui.etc.gui_other.center_widget(self)