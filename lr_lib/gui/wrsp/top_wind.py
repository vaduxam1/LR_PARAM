# -*- coding: UTF-8 -*-
# Toplevel окна для основного gui окна lr_vars.Window

import contextlib
import subprocess

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.files as lr_files
import lr_lib.core.etc.other as lr_other
import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.gui.widj.dialog as lr_dialog


def folder_wind(self) -> None:
    '''окно списка всех файлов'''
    top = tk.Toplevel()
    top.transient(self)
    top.resizable(width=False, height=False)
    top.title('список всех файлов - %s' % len(lr_vars.AllFiles))
    comboAllFilesFolder = ttk.Combobox(top, foreground='grey', font=lr_vars.DefaultFont)
    buttonAllFilesFolder = tk.Button(top, text='open', font=lr_vars.DefaultFont + ' italic', padx=0, pady=0,
                                     command=lambda: subprocess.Popen([lr_vars.EDITOR['exe'], comboAllFilesFolder.get()]))
    ttip = lambda a: lr_tooltip.createToolTip(comboAllFilesFolder, lr_other.file_string(
        lr_files.get_file_with_kwargs(lr_vars.AllFiles, FullName=comboAllFilesFolder.get()), deny=[]))
    comboAllFilesFolder.bind("<<ComboboxSelected>>", ttip)
    lr_tooltip.createToolTip(buttonAllFilesFolder, 'открыть выбранный файл')
    lr_tooltip.createToolTip(comboAllFilesFolder, 'список всех файлов, в которых производится поиск {param}'
                                                  '\n\t# Window.folder_wind\n\t# lr_vars.AllFiles')
    files = list(f['File']['FullName'] for f in lr_vars.AllFiles)
    comboAllFilesFolder['values'] = files
    with contextlib.suppress(Exception):
        m = max(len(f) for f in files)
        if m > 100: m = 100
        comboAllFilesFolder.configure(width=m)
    buttonAllFilesFolder.pack()
    comboAllFilesFolder.pack()


def enc_wind(self) -> None:
    '''окно кодировки файлов'''
    top = tk.Toplevel()
    top.transient(self)
    top.resizable(width=False, height=False)
    tt = 'кодировка файлов для (2)-(5)\n\t# Window.enc_wind'
    top.title(tt)
    encodeEntry = ttk.Combobox(top, justify='center', textvariable=lr_vars.VarEncode, width=65, foreground='grey',
                               background=lr_vars.Background, font=lr_vars.DefaultFont + ' italic')
    encodeEntry['values'] = lr_vars.ENCODE_LIST
    encodeEntry.bind("<<ComboboxSelected>>", lambda *a: self.comboFiles_change())
    lr_tooltip.createToolTip(encodeEntry, tt)
    encodeEntry.pack()


def pool_wind(self) -> None:
    '''окно настройки пулов'''
    top = tk.Toplevel()
    top.transient(self)
    top.resizable(width=False, height=False)
    tt = 'окно настройки пулов  # Window.pool_wind'
    top.title(tt)

    def set_pool(pool) -> None:
        '''установить новый пул'''
        pool.reset()
        self.last_frame_text_set()

    labMP = tk.Label(top, text='MPPool')
    labMP.grid(row=1, column=1)
    lr_tooltip.createToolTip(labMP, 'основной пул(process), поиск в файлах и тд')

    entryMPName = ttk.Combobox(top, justify='center', textvariable=lr_vars.M_POOL.name, width=65, foreground='grey',
                               background=lr_vars.Background, font=lr_vars.DefaultFont + ' italic')
    entryMPName['values'] = list(lr_vars.T_POOL.pools.keys())
    entryMPName.bind("<<ComboboxSelected>>", lambda *a: set_pool(lr_vars.M_POOL))
    lr_tooltip.createToolTip(entryMPName, 'тип MP пула(любые стандартные(process))')
    entryMPName.grid(row=2, column=0, columnspan=7)

    spinMP = tk.Spinbox(top, from_=0, to=999, textvariable=lr_vars.M_POOL.size, width=3, font=lr_vars.DefaultFont,
                        command=lambda *a: set_pool(lr_vars.M_POOL))
    spinMP.grid(row=2, column=7)
    lr_tooltip.createToolTip(spinMP, 'размер MP пула')

    labT = tk.Label(top, text='TPool')
    labT.grid(row=3, column=1)
    lr_tooltip.createToolTip(labT, 'доп пул(thread only), выполнение в фоне, подсветка и тд')

    entryTName = ttk.Combobox(top, justify='center', textvariable=lr_vars.T_POOL.name, width=65, foreground='grey',
                              background=lr_vars.Background, font=lr_vars.DefaultFont + ' italic')
    entryTName['values'] = list(lr_vars.T_POOL.pools.keys())
    entryTName.bind("<<ComboboxSelected>>", lambda *a: set_pool(lr_vars.T_POOL))
    lr_tooltip.createToolTip(entryTName, 'тип T пула(чтото из thread)')
    entryTName.grid(row=4, column=0, columnspan=7)

    spinT = tk.Spinbox(top, from_=0, to=999, textvariable=lr_vars.T_POOL.size, width=3, font=lr_vars.DefaultFont, command=set_pool(lr_vars.T_POOL))
    spinT.grid(row=4, column=7)
    lr_tooltip.createToolTip(spinT, 'размер T пула')

    spinSThreadAutoSizeTimeOut = tk.Spinbox(top, from_=0, to=10**5, textvariable=lr_vars.SThreadAutoSizeTimeOut, width=4, font=lr_vars.DefaultFont)
    spinSThreadAutoSizeTimeOut.grid(row=5, column=2)
    lr_tooltip.createToolTip(spinSThreadAutoSizeTimeOut, 'SThreadAutoSizeTimeOut отзывчивость(мсек) SThreadPool - период опроса, для изменения размера пула')

    spinMainThreadUpdateTime = tk.Spinbox(top, from_=0, to=10**5, textvariable=lr_vars.MainThreadUpdateTime, width=4, font=lr_vars.DefaultFont)
    spinMainThreadUpdateTime.grid(row=5, column=0)
    lr_tooltip.createToolTip(spinMainThreadUpdateTime, 'MainThreadUpdateTime интервал(мс) проверки очереди выполнения для главного потока')

    spinSThreadPoolSizeMin = tk.Spinbox(top, from_=0, to=10 ** 5, textvariable=lr_vars.SThreadPoolSizeMin, width=4, font=lr_vars.DefaultFont)
    spinSThreadPoolSizeMin.grid(row=5, column=3)
    lr_tooltip.createToolTip(spinSThreadPoolSizeMin, 'SThreadPool min size')

    spinSThreadPoolSizeMax = tk.Spinbox(top, from_=0, to=10 ** 5, textvariable=lr_vars.SThreadPoolSizeMax, width=4, font=lr_vars.DefaultFont)
    spinSThreadPoolSizeMax.grid(row=5, column=4)
    lr_tooltip.createToolTip(spinSThreadPoolSizeMax, 'SThreadPool max size (int>2)')

    spinSThreadPoolAddMinQSize = tk.Spinbox(top, from_=0, to=10 ** 5, textvariable=lr_vars.SThreadPoolAddMinQSize, width=4, font=lr_vars.DefaultFont)
    spinSThreadPoolAddMinQSize.grid(row=5, column=5)
    lr_tooltip.createToolTip(spinSThreadPoolAddMinQSize, 'SThreadPool - минимальная длина очереди, для добавления, более чем одного потока, за раз')

    spinSThreadPooMaxAddThread = tk.Spinbox(top, from_=0, to=10 ** 5, textvariable=lr_vars.SThreadPooMaxAddThread, width=4, font=lr_vars.DefaultFont)
    spinSThreadPooMaxAddThread.grid(row=5, column=6)
    lr_tooltip.createToolTip(spinSThreadPooMaxAddThread, 'SThreadPool - max число потоков, для добавления за один раз(до SThreadPoolSizeMax)')

    spinSThreadExitTimeout = tk.Spinbox(top, from_=0, to=10 ** 5, textvariable=lr_vars.SThreadExitTimeout, width=4, font=lr_vars.DefaultFont)
    spinSThreadExitTimeout.grid(row=5, column=1)
    lr_tooltip.createToolTip(spinSThreadExitTimeout, 'SThreadPool таймаут(сек) выхода, бездействующих потоков(до SThreadPoolSizeMin)')
    spinSThreadMonitorUpdate = tk.Spinbox(top, from_=0, to=10 ** 5, textvariable=lr_vars._SThreadMonitorUpdate, width=4, font=lr_vars.DefaultFont)
    spinSThreadMonitorUpdate.grid(row=5, column=7)
    lr_tooltip.createToolTip(spinSThreadMonitorUpdate, 'SThreadPool (мс) время обновления Window.pool_wind текста состояния пула')

    if lr_vars.T_POOL_NAME == 'SThreadPool(threading.Thread)':
        pool_state_updater(self)


@lr_vars.T_POOL_decorator
def pool_state_updater(self) -> None:
    '''SThreadPool(threading.Thread) текст состояния пула'''
    def pool_state_string(st=lambda i: '{0:<6} : {1}'.format(*i)) -> str:
        '''инфо о потоках T_POOL'''
        s = '\n'.join('\n{n} {t}'.format(t=('\n' + '\n'.join(map(st, t.task.items())) if t.task else 'sleep'), n=t.name)
                      for t in lr_vars.T_POOL.threads)
        return s

    def thread_info_updater(y: lr_dialog.YesNoCancel) -> None:
        '''перезапуск инфо'''
        t1, t2 = y.label1['text'].split('\n', 1)
        t1 = '{0}: size({1})'.format(t1.split(':', 1)[0], len(lr_vars.T_POOL.threads))
        y.label1.config(text='{0}\n{1}'.format(t1, t2))
        y.new_text(pool_state_string())
        if y.alive_:
            y.after(lr_vars._SThreadMonitorUpdate.get(), thread_info_updater, y)

    y = lr_dialog.YesNoCancel(['выйти'], 'T_POOL\nмонитор', 'инфо о задачах, выполняющихся в SThread потоках',
                              title=pool_state_updater, parent=self, is_text=pool_state_string())
    y.after(100, thread_info_updater, y)
    y.ask()
