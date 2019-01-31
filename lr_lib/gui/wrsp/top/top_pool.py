# -*- coding: UTF-8 -*-
# Toplevel окно пула

import tkinter as tk
import tkinter.ttk as ttk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_highlight
import lr_lib.core.var.vars_other


class TopPoolSetting(tk.Toplevel):
    """
    окно настройки пулов
    """

    def __init__(self, action: 'lr_lib.gui.wrsp.main_window.Window'):
        tk.Toplevel.__init__(self)
        self.action = action

        self.transient(action)
        self.resizable(width=False, height=False)
        tt = 'окно настройки пулов  # Window.pool_wind'
        self.title(tt)

        labMP = tk.Label(self, text='MPPool')
        labMP.grid(row=1, column=1)
        lr_lib.gui.widj.tooltip.createToolTip(labMP, 'основной пул(process), поиск в файлах и тд')

        entryMPName = ttk.Combobox(
            self, justify='center', textvariable=lr_vars.M_POOL.name, width=65, foreground='grey',
            background=lr_lib.core.var.vars_highlight.Background,
            font=(lr_vars.DefaultFont + ' italic'),
        )
        entryMPName['values'] = list(lr_vars.T_POOL.pools.keys())
        cmd1 = lambda *a: self.set_pool(lr_vars.M_POOL)
        entryMPName.bind("<<ComboboxSelected>>", cmd1)
        lr_lib.gui.widj.tooltip.createToolTip(entryMPName, 'тип MP пула(любые стандартные(process))')
        entryMPName.grid(row=2, column=0, columnspan=7)

        spinMP = tk.Spinbox(
            self, from_=0, to=999, textvariable=lr_vars.M_POOL.size, width=3, font=lr_vars.DefaultFont,
            command=lambda *a: self.set_pool(lr_vars.M_POOL),
        )
        spinMP.grid(row=2, column=7)
        lr_lib.gui.widj.tooltip.createToolTip(spinMP, 'размер MP пула')

        labT = tk.Label(self, text='TPool')
        labT.grid(row=3, column=1)
        lr_lib.gui.widj.tooltip.createToolTip(labT, 'доп пул(thread only), выполнение в фоне, подсветка и тд')

        entryTName = ttk.Combobox(
            self, justify='center', textvariable=lr_vars.T_POOL.name, width=65, foreground='grey',
            background=lr_lib.core.var.vars_highlight.Background, font=(lr_vars.DefaultFont + ' italic'),
        )
        entryTName['values'] = list(lr_vars.T_POOL.pools.keys())
        cmd2 = lambda *a: self.set_pool(lr_vars.T_POOL)
        entryTName.bind("<<ComboboxSelected>>", cmd2)
        lr_lib.gui.widj.tooltip.createToolTip(entryTName, 'тип T пула(чтото из thread)')
        entryTName.grid(row=4, column=0, columnspan=7)

        spinT = tk.Spinbox(
            self, from_=0, to=999, textvariable=lr_vars.T_POOL.size, width=3, font=lr_vars.DefaultFont,
            command=self.set_pool(lr_vars.T_POOL),
        )
        spinT.grid(row=4, column=7)
        lr_lib.gui.widj.tooltip.createToolTip(spinT, 'размер T пула')

        spinSThreadAutoSizeTimeOut = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.SThreadAutoSizeTimeOut, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadAutoSizeTimeOut.grid(row=5, column=2)
        lr_lib.gui.widj.tooltip.createToolTip(
            spinSThreadAutoSizeTimeOut,
            'SThreadAutoSizeTimeOut отзывчивость(мсек) SThreadPool - период опроса, для изменения размера пула',
        )

        spinMainThreadUpdateTime = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.MainThreadUpdateTime, width=4, font=lr_vars.DefaultFont,
        )
        spinMainThreadUpdateTime.grid(row=5, column=0)
        lr_lib.gui.widj.tooltip.createToolTip(
            spinMainThreadUpdateTime,
            'MainThreadUpdateTime интервал(мс) проверки очереди выполнения для главного потока',
        )

        spinSThreadPoolSizeMin = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.SThreadPoolSizeMin, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadPoolSizeMin.grid(row=5, column=3)
        lr_lib.gui.widj.tooltip.createToolTip(spinSThreadPoolSizeMin, 'SThreadPool min size')

        spinSThreadPoolSizeMax = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.SThreadPoolSizeMax, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadPoolSizeMax.grid(row=5, column=4)
        lr_lib.gui.widj.tooltip.createToolTip(spinSThreadPoolSizeMax, 'SThreadPool max size (int>2)')

        spinSThreadPoolAddMinQSize = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.SThreadPoolAddMinQSize, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadPoolAddMinQSize.grid(row=5, column=5)
        lr_lib.gui.widj.tooltip.createToolTip(
            spinSThreadPoolAddMinQSize,
            'SThreadPool - минимальная длина очереди, для добавления, более чем одного потока, за раз',
        )

        spinSThreadPooMaxAddThread = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.SThreadPooMaxAddThread, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadPooMaxAddThread.grid(row=5, column=6)
        lr_lib.gui.widj.tooltip.createToolTip(
            spinSThreadPooMaxAddThread,
            'SThreadPool - max число потоков, для добавления за один раз(до SThreadPoolSizeMax)',
        )

        spinSThreadExitTimeout = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars.SThreadExitTimeout, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadExitTimeout.grid(row=5, column=1)
        lr_lib.gui.widj.tooltip.createToolTip(
            spinSThreadExitTimeout,
            'SThreadPool таймаут(сек) выхода, бездействующих потоков(до SThreadPoolSizeMin)',
        )
        spinSThreadMonitorUpdate = tk.Spinbox(
            self, from_=0, to=(10 ** 5), textvariable=lr_vars._SThreadMonitorUpdate, width=4, font=lr_vars.DefaultFont,
        )
        spinSThreadMonitorUpdate.grid(row=5, column=7)
        lr_lib.gui.widj.tooltip.createToolTip(
            spinSThreadMonitorUpdate,
            'SThreadPool (мс) время обновления Window.pool_wind текста состояния пула',
        )

        if lr_vars.T_POOL_NAME == 'SThreadPool(threading.Thread)':
            self.pool_state_updater()

        lr_lib.gui.etc.gui_other.center_widget(self)
        return

    def set_pool(self, pool) -> None:
        """
        установить новый пул
        """
        pool.reset()
        self.action.last_frame_text_set()
        return

    @lr_lib.core.var.vars_other.T_POOL_decorator
    def pool_state_updater(self) -> None:
        """
        SThreadPool(threading.Thread) текст состояния пула
        """

        def pool_state_string(st=lambda i: '{0:<6} : {1}'.format(*i)) -> str:
            """
            инфо о потоках T_POOL
            """
            i = '\n'.join((t.task.to_str() if t.task else 'sleep') for t in lr_vars.T_POOL.threads)
            return i

        def thread_info_updater(y: lr_lib.gui.widj.dialog.YesNoCancel) -> None:
            """
            перезапуск инфо
            """
            (t1, t2) = y.label1['text'].split('\n', 1)
            t1 = '{0}: size({1})'.format(t1.split(':', 1)[0], len(lr_vars.T_POOL.threads))
            y.label1.config(text='{0}\n{1}'.format(t1, t2))
            y.new_text(pool_state_string())
            if y.alive_:
                y.after(lr_vars._SThreadMonitorUpdate.get(), thread_info_updater, y)
            return

        y = lr_lib.gui.widj.dialog.YesNoCancel(
            ['выйти', ],
            'T_POOL\nмонитор',
            'инфо о задачах, выполняющихся в SThread потоках',
            title=lr_vars.VERSION,
            parent=self.action,
            is_text=pool_state_string(),
        )
        y.after(100, thread_info_updater, y)
        y.ask()
        return
