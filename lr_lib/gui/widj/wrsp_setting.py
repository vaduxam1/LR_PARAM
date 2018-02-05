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
        VarWebStatsTransac = tk.Checkbutton(self, text='VarWebStatsTransac', font=lr_vars.DefaultFont,
                                            variable=lr_vars.VarWebStatsTransac)
        VarWebStatsIn = tk.Checkbutton(self, text='VarWebStatsIn', font=lr_vars.DefaultFont,
                                       variable=lr_vars.VarWebStatsIn)
        VarWebStatsOut = tk.Checkbutton(self, text='VarWebStatsOut', font=lr_vars.DefaultFont,
                                        variable=lr_vars.VarWebStatsOut)
        VarWebStatsWarn = tk.Checkbutton(self, text='VarWebStatsWarn', font=lr_vars.DefaultFont,
                                         variable=lr_vars.VarWebStatsWarn)
        VarWRSPStatsTransac = tk.Checkbutton(self, text='VarWRSPStatsTransac', font=lr_vars.DefaultFont,
                                             variable=lr_vars.VarWRSPStatsTransac)
        VarWRSPStatsTransacNames = tk.Checkbutton(self, text='VarWRSPStatsTransacNames', font=lr_vars.DefaultFont,
                                                  variable=lr_vars.VarWRSPStatsTransacNames)
        VarWRSPStats = tk.Checkbutton(self, text='VarWRSPStats', font=lr_vars.DefaultFont,
                                      variable=lr_vars.VarWRSPStats)
        SnapshotInName = tk.Checkbutton(self, text='SnapshotInName', font=lr_vars.DefaultFont,
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
        lr_tooltip.createToolTip(VarWebStatsTransac, 'коментарии с именем транзакции')
        lr_tooltip.createToolTip(VarWebStatsIn, 'In коментарии')
        lr_tooltip.createToolTip(VarWebStatsOut, 'Out коментарии')
        lr_tooltip.createToolTip(VarWebStatsWarn, 'Warning коментарии')
        lr_tooltip.createToolTip(VarWRSPStatsTransac, 'для wrsp, статистика использования param')
        lr_tooltip.createToolTip(VarWRSPStatsTransacNames, 'для wrsp, имена транзакций в которых используется param')
        lr_tooltip.createToolTip(VarWRSPStats, 'для wrsp, создавать подробные/короткие коментарии\n'
                                               'Изменится только при пересоздании param')
        lr_tooltip.createToolTip(SnapshotInName, 'в wrsp имени param, отображать номер Snapshot, в котором создан wrsp\n'
                                                 'Изменится только при пересоздании param')
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
        lr_tooltip.createToolTip(wrsp_name_splitter, 'символ разделения в имени wrsp(для "_"): Win__aFFX9__id -> Win__a_FFX_9__id\n'
                                                     'Изменится только при пересоздании param\nничего - откл')
        lr_tooltip.createToolTip(WrspNameFirst, 'начало(P) wrsp имени param: {P_11_zkau_22}\n'
                                                'Изменится только при пересоздании param\n'
                                                'ничего - откл')

        VarWebStatsTransac.pack()
        VarWebStatsIn.pack()
        VarWebStatsOut.pack()
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
