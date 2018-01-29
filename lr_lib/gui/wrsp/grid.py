# -*- coding: UTF-8 -*-
# grid всех виджетов для основного gui окна

import tkinter as tk


def grid_widj(self):
    '''grid всех виджетов для основного gui окна'''
    self.main_frame.grid(row=2, column=0, sticky=tk.NS, padx=0, pady=0)
    self.find_frame.grid(row=4, column=0, sticky=tk.NS, padx=0, pady=0)
    self.show_param_frame.grid(row=6, column=0, sticky=tk.NS, padx=0, pady=0)
    self.mid_frame.grid(row=7, column=0, sticky=tk.NS, padx=0, pady=0)
    self.last_frameCbx1.grid(row=13, column=0, sticky=tk.NS, padx=0, pady=0)
    self.last_frameCbx2.grid(row=18, column=0, sticky=tk.NS, padx=0, pady=0)
    self.last_frame.grid(row=26, column=0, sticky=tk.N, padx=0, pady=0)

    self.t0.grid(row=1, column=20, sticky=tk.E, padx=0, pady=0)
    self.t01.grid(row=1, column=21, sticky=tk.E, padx=0, pady=0)
    self.t1.grid(row=1, column=0, sticky=tk.E, padx=0, pady=0)
    self.t2.grid(row=1, column=14, sticky=tk.E, padx=0, pady=0)
    self.t3.grid(row=4, column=1, sticky=tk.E, padx=0, pady=0)
    self.t4.grid(row=4, column=6, sticky=tk.W, padx=0, pady=0)
    self.t02.grid(row=4, column=6, sticky=tk.E, padx=0, pady=0)
    self.t6.grid(row=5, column=1, sticky=tk.E, padx=0, pady=0)

    self.tk_text.grid(row=0, column=0, sticky=tk.NSEW, padx=0, pady=0)
    self.text_scrolly.grid(row=0, column=1, sticky=tk.NS, padx=0, pady=0)
    self.text_scrollx.grid(row=1, column=0, sticky=tk.EW, padx=0, pady=0)

    self.sortKey1.grid(row=2, column=5, sticky=tk.EW, padx=0, pady=0, columnspan=2)
    self.sortKey2.grid(row=2, column=7, sticky=tk.EW, padx=0, pady=0, columnspan=200)
    self.comboLogger.grid(row=1, column=75, sticky=tk.N, padx=0, pady=0)
    self.spin_toolTipTimeout.grid(row=1, column=80, sticky=tk.N, padx=0, pady=0)
    self.cbxPopupWindow.grid(row=1, column=76, sticky=tk.E, padx=0, pady=0)
    self.unblock.grid(row=1, column=74, sticky=tk.E, padx=0, pady=0)
    self.Button_change_folder.grid(row=1, column=100, sticky=tk.E, padx=0, pady=0)

    self.min_inf.grid(row=1, column=15, sticky=tk.N, padx=0, pady=0)
    self.ButtonFindParamFiles.grid(row=1, column=16, sticky=tk.EW, padx=0, pady=0)
    self.cbxFileNamesNumsShow.grid(row=1, column=19, sticky=tk.E, padx=0, pady=0)
    self.max_inf.grid(row=1, column=17, sticky=tk.N, padx=0, pady=0)
    self.cbxFirstLastFile.grid(row=4, column=3, sticky=tk.W, padx=0, pady=0)
    self.StrongSearchInFile_cbx.grid(row=4, column=4, sticky=tk.W, padx=0, pady=0)
    self.comboParts.grid(row=4, column=5, sticky=tk.E, padx=0, pady=0)

    self.actionButton.grid(row=1, column=19, sticky=tk.N, padx=0, pady=0)

    self.ButtonShowParam.grid(row=5, column=2, sticky=tk.EW, padx=0, pady=0)
    self.comboFiles.grid(row=4, column=2, sticky=tk.EW, padx=0, pady=0)
    self.comboParam.grid(row=1, column=1, sticky=tk.EW, padx=0, pady=0)

    self.ButtonNewLB.grid(row=1, column=25, sticky=tk.E, padx=0, pady=0)
    self.LBcbx_return.grid(row=1, column=27, sticky=tk.E, padx=0, pady=0)
    self.LBcbx_rus.grid(row=1, column=28, sticky=tk.E, padx=0, pady=0)
    self.lb_split_label.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
    self.LBcbx_SplitList.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
    self.LBent_SplitList.grid(row=1, column=30, sticky=tk.E, padx=0, pady=0)
    self.LBSpinSplitList.grid(row=1, column=31, sticky=tk.E, padx=0, pady=0)
    self.max_lb.grid(row=1, column=26, sticky=tk.E, rowspan=2, padx=0, pady=0)

    self.ButtonNewRB.grid(row=1, column=25, sticky=tk.E, padx=0, pady=0)
    self.RBcbx_return.grid(row=1, column=27, sticky=tk.E, padx=0, pady=0)
    self.RBcbx_rus.grid(row=1, column=28, sticky=tk.E, padx=0, pady=0)
    self.rb_split_label.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
    self.RBcbx_SplitList.grid(row=1, column=29, sticky=tk.E, padx=0, pady=0)
    self.RBent_SplitList.grid(row=1, column=30, sticky=tk.E, padx=0, pady=0)
    self.RBSpinSplitList.grid(row=1, column=31, sticky=tk.E, padx=0, pady=0)
    self.max_rb.grid(row=1, column=26, sticky=tk.E, rowspan=2, padx=0, pady=0)

    self.t5l.grid(row=10, column=1, sticky=tk.E, padx=0, pady=0)
    self.t5r.grid(row=15, column=1, sticky=tk.E, padx=0, pady=0)

    self.LB.grid(row=11, column=0, sticky=tk.EW, padx=0, pady=0)
    self.LB.scrolly.grid(row=11, column=1, sticky=tk.NSEW, padx=0, pady=0)
    self.LB.scrollx.grid(row=12, column=0, sticky=tk.NSEW, padx=0, pady=0)
    self.LB.label_info.grid(row=10, column=0, sticky=tk.NSEW, padx=0, pady=0)

    self.RB.grid(row=16, column=0, sticky=tk.EW, padx=0, pady=0)
    self.RB.scrolly.grid(row=16, column=1, sticky=tk.NSEW, padx=0, pady=0)
    self.RB.scrollx.grid(row=17, column=0, sticky=tk.NSEW, padx=0, pady=0)
    self.RB.label_info.grid(row=15, column=0, sticky=tk.NSEW, padx=0, pady=0)

    self.spin_LB_height.grid(row=1, column=64, sticky=tk.E, padx=0, pady=0)
    self.ButtonLB_note.grid(row=1, column=65, sticky=tk.E, padx=0, pady=0)
    self.partNumEmptyLbNext.grid(row=1, column=56, sticky=tk.E, padx=0, pady=0)
    self.partNumDenyLbNext.grid(row=1, column=57, sticky=tk.E, padx=0, pady=0)

    self.LbB1Cbx.grid(row=1, column=54, sticky=tk.E, padx=0, pady=0)
    self.LbB2Cbx.grid(row=1, column=55, sticky=tk.E, padx=0, pady=0)
    self.LbRstripCbx.grid(row=1, column=61, sticky=tk.E, padx=0, pady=0)
    self.LbEndCbx.grid(row=1, column=62, sticky=tk.E, padx=0, pady=0)

    self.spin_RB_height.grid(row=1, column=64, sticky=tk.E, padx=0, pady=0)
    self.ButtonRB_note.grid(row=1, column=65, sticky=tk.E, padx=0, pady=0)
    self.partNumEmptyRbNext.grid(row=1, column=58, sticky=tk.E, padx=0, pady=0)
    self.partNumDenyRbNext.grid(row=1, column=59, sticky=tk.E, padx=0, pady=0)

    self.RbB1Cbx.grid(row=1, column=56, sticky=tk.E, padx=0, pady=0)
    self.RbB2Cbx.grid(row=1, column=57, sticky=tk.E, padx=0, pady=0)
    self.RbRstripCbx.grid(row=1, column=62, sticky=tk.E, padx=0, pady=0)
    self.RbEndCbx.grid(row=1, column=63, sticky=tk.E, padx=0, pady=0)

    self.ButtonParamFileOpen.grid(row=1, column=5, sticky=tk.EW, padx=0, pady=0)
    self.ButtonClearDown.grid(row=1, column=8, sticky=tk.E, padx=0, pady=0)
    self.ButtonClearUp.grid(row=1, column=15, sticky=tk.E, padx=0, pady=0)
    self.ButtonNote.grid(row=1, column=6, sticky=tk.EW, padx=0, pady=0)
    self.ButtonLog.grid(row=1, column=7, sticky=tk.E, padx=0, pady=0)
    self.cbxClipboard.grid(row=5, column=5, sticky=tk.E, padx=0, pady=0)
    self.cbxOrdVersion.grid(row=5, column=3, sticky=tk.N, padx=0, pady=0)
    self.cbxAutoNoteParam.grid(row=5, column=4, sticky=tk.E, padx=0, pady=0)
    self.cbxAutoShowParam.grid(row=1, column=20, sticky=tk.E, padx=0, pady=0)
    self.cbxClearShow.grid(row=5, column=6, sticky=tk.E, padx=0, pady=0)

    self.change_folder_cbx.grid(row=1, column=101, sticky=tk.E, padx=0, pady=0)
    self.deny_file_cbx.grid(row=1, column=102, sticky=tk.E, padx=0, pady=0)
    self.filesStats_cbx.grid(row=1, column=103, sticky=tk.E, padx=0, pady=0)
