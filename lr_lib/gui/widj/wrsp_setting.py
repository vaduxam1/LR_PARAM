# -*- coding: UTF-8 -*-
# окно настройки каментов и имени wrsp

import tkinter as tk

import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.core.var.vars as lr_vars


class WrspSettingWindow(tk.Toplevel):
    '''настройка каментов и имени wrsp'''
    def __init__(self, *args, parent=None):
        super().__init__(padx=0, pady=0)
        self.parent = parent
        self.transient(self.parent)
        self.resizable(width=False, height=False)
        self.title('настройка каментов и имени wrsp')
        tt_stat = 'коментарии с именем транзакции (VarWebStatsTransac)\n//lr: "login"(4/10=[4:13])'
        VarWebStatsTransac = tk.Checkbutton(self, text=tt_stat, font=lr_vars.DefaultFont,
                                            variable=lr_vars.VarWebStatsTransac, justify='left')
        tt_in = 'In-param коментарии (VarWebStatsIn)\n//lr: IN(2)<-[1]: aFFX9(P:2/3|S:2=[2:4]|T:2)'
        VarWebStatsIn = tk.Checkbutton(self, text=tt_in, font=lr_vars.DefaultFont, justify='left',
                                       variable=lr_vars.VarWebStatsIn)
        tt_out = 'Out-param коментарии (VarWebStatsOut)\n//lr: OUT(1)-> aFFX9(P:3|S:2=[2:4]|T:2)'
        VarWebStatsOut = tk.Checkbutton(self, text=tt_out, font=lr_vars.DefaultFont, justify='left',
                                        variable=lr_vars.VarWebStatsOut)
        tt_warn = 'Warning коментарии (VarWebStatsWarn)\n//lr: WARNING: WrspInAndOutUsage: 1=["z_k620"]'
        VarWebStatsWarn = tk.Checkbutton(self, text=tt_warn, font=lr_vars.DefaultFont, justify='left',
                                         variable=lr_vars.VarWebStatsWarn)
        tt_wrsp_transac = 'для WRSP, статистика использования param (VarWRSPStatsTransac)\n' \
                          '//lr: (login: 3=[1:4]) -> Param:3 | Snapshots:2=[2:4] | Transactions=1:["login"]'
        VarWRSPStatsTransac = tk.Checkbutton(self, text=tt_wrsp_transac, font=lr_vars.DefaultFont, justify='left',
                                             variable=lr_vars.VarWRSPStatsTransac)
        tt_wrsp_trn = 'для WRSP, имена транзакций\nв которых используется param (VarWRSPStatsTransacNames)\n' \
                      ' | Transactions=2:[["NoTransaction_1", "login"]'
        VarWRSPStatsTransacNames = tk.Checkbutton(self, text=tt_wrsp_trn, font=lr_vars.DefaultFont, justify='left',
                                                  variable=lr_vars.VarWRSPStatsTransacNames)
        tt_wrsp_st = 'для WRSP, создавать подробные/короткие коментарии\n' \
                     'Изменится только при пересоздании param (VarWRSPStats)\nкороткие: // PARAM["aFFX5"] // Snap[1]'
        VarWRSPStats = tk.Checkbutton(self, text=tt_wrsp_st, font=lr_vars.DefaultFont, justify='left',
                                      variable=lr_vars.VarWRSPStats)
        tt_SnapshotInName = 'в WRSP имени param, отображать номер Snapshot, в котором создан wrsp\n' \
                            'Изменится только при пересоздании param (SnapshotInName)\n' \
                            'P_6637_1__zk620 -> P_6637__zk620'
        SnapshotInName = tk.Checkbutton(self, text=tt_SnapshotInName, font=lr_vars.DefaultFont, justify='left',
                                        variable=lr_vars.SnapshotInName)
        TransactionInNameMax = tk.Spinbox(self, font=lr_vars.DefaultFont, from_=0, to=1000,
                                          textvariable=lr_vars.TransactionInNameMax)

        MaxLbWrspName = tk.Spinbox(self, textvariable=lr_vars.MaxLbWrspName, font=lr_vars.DefaultFont, from_=0, to=1000)
        MaxRbWrspName = tk.Spinbox(self, textvariable=lr_vars.MaxRbWrspName, font=lr_vars.DefaultFont, from_=0, to=1000)
        MaxParamWrspName = tk.Spinbox(self, textvariable=lr_vars.MaxParamWrspName, font=lr_vars.DefaultFont, from_=0, to=1000)
        MinWrspRnum = tk.Spinbox(self, textvariable=lr_vars.MinWrspRnum, font=lr_vars.DefaultFont, from_=0, to=1000)
        MaxWrspRnum = tk.Spinbox(self, textvariable=lr_vars.MaxWrspRnum, font=lr_vars.DefaultFont, from_=0, to=10**5)
        wrsp_name_splitter = tk.Entry(self, textvariable=lr_vars.wrsp_name_splitter, font=lr_vars.DefaultFont)
        WrspNameFirst = tk.Entry(self, textvariable=lr_vars.WrspNameFirst, font=lr_vars.DefaultFont)

        apply_btn = tk.Button(self, font=lr_vars.DefaultFont, text='применить',
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
        lr_tooltip.createToolTip(TransactionInNameMax, 'в wrsp имени param, отображать максимум символов transaction, в которой создан wrsp\n'
                                                       'Изменится только при пересоздании param\n'
                                                       '0 - откл')
        lr_tooltip.createToolTip(MaxLbWrspName, 'макс число символов, взятых из LB, для wrsp имени param\n'
                                                'Изменится только при пересоздании param\n'
                                                '0 - откл')
        lr_tooltip.createToolTip(MaxRbWrspName, 'макс число символов, взятых из RB, для wrsp имени param\n'
                                                'Изменится только при пересоздании param\n'
                                                '0 - откл')
        lr_tooltip.createToolTip(MaxParamWrspName, 'макс число символов, взятых из param, для wrsp имени param\n'
                                                   'Изменится только при пересоздании param\n'
                                                   '0 - откл')
        lr_tooltip.createToolTip(MinWrspRnum, 'мин число, для случайного номера, в wrsp имени param\n'
                                              'Изменится только при пересоздании param\n'
                                              '0 - откл')
        lr_tooltip.createToolTip(MaxWrspRnum, 'макс число, для случайного номера, в wrsp имени param\n'
                                              'Изменится только при пересоздании param\n'
                                              '0 - откл')
        lr_tooltip.createToolTip(wrsp_name_splitter, 'символ разделения в имени wrsp(для "_"): "aFFX9" -> "a_FFX_9"\n'
                                                     'Изменится только при пересоздании param\nничего - откл')
        lr_tooltip.createToolTip(WrspNameFirst, 'начало(P) wrsp имени param: {P_11_zkau_22}\n'
                                                'Изменится только при пересоздании param\n'
                                                'ничего - откл')

        VarWebStatsTransac.pack(side='left')
        VarWebStatsIn.pack(side='left')
        VarWebStatsOut.pack(side='rigth')
        VarWebStatsWarn.pack()
        VarWRSPStatsTransac.pack()
        VarWRSPStatsTransacNames.pack()
        VarWRSPStats.pack()
        SnapshotInName.pack()

        MaxLbWrspName.pack()
        MaxRbWrspName.pack()
        MaxParamWrspName.pack()
        MinWrspRnum.pack()
        MaxWrspRnum.pack()
        wrsp_name_splitter.pack()
        WrspNameFirst.pack()
        TransactionInNameMax.pack()

        apply_btn.pack()
