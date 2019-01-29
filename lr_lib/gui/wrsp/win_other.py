# -*- coding: UTF-8 -*-
# разное

import subprocess
import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_other
import lr_lib.gui.wrsp.win_filesort


class WinOther(lr_lib.gui.wrsp.win_filesort.WinFileSort):
    """разное"""

    def __init__(self):
        lr_lib.gui.wrsp.win_filesort.WinFileSort.__init__(self)

        self.cbxFirstLastFile = tk.Checkbutton(
            self.mid_frame, variable=lr_vars.VarFirstLastFile, text='reverse', font=(lr_vars.DefaultFont + ' italic'),
            padx=0, pady=0, command=self.firstOrLastFile,
        )

        self.StrongSearchInFile_cbx = tk.Checkbutton(
            self.mid_frame, variable=lr_vars.VarStrongSearchInFile, padx=0, pady=0, text='strong',
            font=(lr_vars.DefaultFont + ' italic'),
        )

        self.unblock = tk.Button(
            self.last_frame, text='unblock', font=(lr_vars.DefaultFont + ' bold'), padx=0, pady=0,
            command=self.force_unblock, relief='groove',
        )

        self.ButtonClearDown = tk.Button(
            self.last_frame, text='clearW', command=self.clear, font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0,
            relief='groove',
        )

        cmd1 = lambda: self.tk_text.delete(0.0, 'end')
        self.ButtonClearUp = tk.Button(
            self.last_frame, text='clearT', command=cmd1,
            font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0, relief='groove',
        )

        cmd2 = lambda: lr_lib.core.etc.other.openTextInEditor(self.tk_text.get('1.0', tk.END))
        self.ButtonNote = tk.Button(
            self.last_frame, text='text', command=cmd2,
            font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0, relief='groove',
        )

        cmd3 = lambda: subprocess.Popen([lr_vars.EDITOR['exe'], lr_vars.logFullName])
        self.ButtonLog = tk.Button(
            self.last_frame, text='log', font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0,
            command=cmd3, relief='groove',
        )

        self.ButtonParamFileOpen = tk.Button(
            self.last_frame, text='file(3)', font=(lr_vars.DefaultFont + ' bold'), padx=0, pady=0,
            command=self.param_file_editor, relief='groove',
        )

        self.spin_toolTipTimeout = tk.Entry(
            self.last_frame, textvariable=lr_vars.VarToolTipTimeout, width=4, font=(lr_vars.DefaultFont + ' italic'))

        self.cbxOrdVersion = tk.Checkbutton(
            self.mid_frame, variable=lr_vars.VarOrdVersion, padx=0, pady=0, font=lr_vars.DefaultFont, text='ord',
        )

        log_vals = list(lr_lib.core.var.vars_other.loggingLevels.keys())
        self.comboLogger = ttk.Combobox(
            self.last_frame, textvariable=lr_vars.VarWindowLogger, justify='center', font=lr_vars.DefaultFont,
            width=5, style="BW.TButton",
        )
        self.comboLogger['values'] = log_vals
        cmd4 = lambda *a: lr_vars.VarWindowLogger.set(self.comboLogger.get())
        self.comboLogger.bind("<<ComboboxSelected>>", cmd4)

        self.ButtonShowParam = tk.Button(
            self.mid_frame, text='сформировать web_reg_save_param ', command=self.show_LR_Param, padx=0, pady=0,
            font=(lr_vars.DefaultFont + ' bold'), background='orange',
        )

        self.cbxClipboard = tk.Checkbutton(
            self.mid_frame, variable=self.cbxWrspClipboard, text='clipb', font=(lr_vars.DefaultFont + ' italic'),
            padx=0, pady=0,
        )

        self.cbxClearShow = tk.Checkbutton(
            self.mid_frame, variable=self.cbxClearShowVar, text='clear', font=(lr_vars.DefaultFont + ' italic'),
            padx=0, pady=0,
        )

        self.cbxAutoShowParam = tk.Checkbutton(
            self.show_param_frame, variable=self.cbxWrspAutoCreate, text='auto', font=(lr_vars.DefaultFont + ' italic'),
            padx=0, pady=0,
        )

        self.cbxAutoNoteParam = tk.Checkbutton(
            self.mid_frame, variable=self.cbxNotepadWrsp, text='note', font=(lr_vars.DefaultFont + ' italic'),
            padx=0, pady=0,
        )

        self.cbxFileNamesNumsShow = tk.Checkbutton(
            self.show_param_frame, variable=lr_vars.VarFileNamesNumsShow, text='name',
            font=(lr_vars.DefaultFont + ' italic'), padx=0, pady=0,
        )

        self.cbxPopupWindow = tk.Checkbutton(
            self.last_frame, variable=lr_vars.VarShowPopupWindow, text='Win', padx=0, pady=0, background='orange',
            font=(lr_vars.DefaultFont + ' italic bold'),
        )
        return

    def force_unblock(self, *args) -> None:
        self._block_ = False
        self._block(False)
        return

    @lr_lib.core.var.vars_other.T_POOL_decorator
    def param_file_editor(self, *args):
        """открыть param файл в editor"""
        f = lr_lib.core.wrsp.files.get_file_with_kwargs(lr_vars.FilesWithParam)['File']['FullName']
        p = subprocess.Popen([lr_vars.EDITOR['exe'], f])
        return p

    def clear(self) -> None:
        """очистить поля ввода"""
        self.show_frame_info_working()
        lr_lib.core.var.vars_other.clearVars()
        self.LB.set('')
        self.RB.set('')

        self.comboFiles['values'] = [self.no_files_text]
        self.comboParts['values'] = [0]
        self.comboFiles.current(0)
        self.comboParts.current(0)

        lr_lib.gui.widj.lbrb5.LBRBText.set_label_text()

        self.set_comboFiles_width()
        self.sortKey1.set('Snapshot')
        self.sortKey2.set('Nums')
        self.last_frame_text_set()

        lr_vars.Tk.title(lr_vars.VERSION)
        return

    def last_frame_text_set(self) -> None:
        """отображение всякой информации"""
        t = 'inf={i}: файлов={f} | MP: {pool}[{p_size}] | T: {tpool}[{tpool_size}] | {d}'.format(
            d=lr_vars.VarFilesFolder.get(),
            f=len(lr_vars.AllFiles),
            pool=lr_vars.M_POOL._name,
            i=len(list(lr_lib.core.etc.other.get_files_infs(lr_vars.AllFiles))),
            tpool_size=lr_vars.T_POOL._size,
            p_size=lr_vars.M_POOL._size,
            tpool=lr_vars.T_POOL._name,
        )
        self.last_frame['text'] = t
        return

    def err_to_widgts(self, exc_type, exc_val, exc_tb, ern) -> None:
        """отображение ошибки"""
        err = '{n}( {e} )'.format(n=ern, e=exc_val)
        lr_vars.Tk.title('{e} | {v}'.format(e=err, v=lr_vars.VERSION))
        t = err.split('\n')[:5]
        t = '\n'.join(t)
        self.last_frame.config(text=t[:500])
        # lr_tooltip.createToolTip(self.comboFiles, '\n'.join(lr_other._chunks(str(exc_val), 60)))
        return
