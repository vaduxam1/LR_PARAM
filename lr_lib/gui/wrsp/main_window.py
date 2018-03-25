# -*- coding: UTF-8 -*-
# основное gui окно

import tkinter as tk

import lr_lib
import lr_lib.gui.wrsp.win_menu


class Window(lr_lib.gui.wrsp.win_menu.WinMenu):
    """главное окно скрипта
    Window
    lr_win_menu.WinMenu
    lr_win_folder.WinFolder
    lr_win_other.WinOther
    lr_win_filesort.WinFileSort
    lr_win_maxmin.WinMaxMin
    lr_win_widj.WinWidj
    lr_win_part_lbrb.WinPartsLbRb
    lr_win_text.WinText
    lr_win_block.WinBlock
    lr_win_act.WinAct
    lr_win_frame.WinFrame
    ttk.Frame
    """

    def __init__(self):
        lr_lib.gui.wrsp.win_menu.WinMenu.__init__(self)

        self.set_tooltip()
        self.set_grid()

    def set_tooltip(self) -> None:
        """создать все tooltip основного gui окна"""
        lr_lib.gui.widj.tooltip.createToolTip(self.t0, lr_lib.etc.help.CODE)
        lr_lib.gui.widj.tooltip.createToolTip(self.t01, lr_lib.etc.help.WORK)
        lr_lib.gui.widj.tooltip.createToolTip(self.t02, lr_lib.etc.help.ADD)

        t0 = '(3) - выбор файла из результатов поиска (2):lr_vars.FilesWithParam\n\t' \
             '# Window.comboFiles == lr_vars.FilesWithParam\n\t' \
             '# lr_vars.VarFileName -> lr_vars.VarFile ->(4):lr_vars.VarFileText\n\t\t\t' \
             '-> lr_vars.VarPartNum'
        t1 = '(1) Поле ввода {param}\n\t' \
             '# Window.comboParam'
        t2 = '(2) найти файлы(3), содержащие {param}(1)\n\t' \
             '# Window.ButtonFindParamFiles\n\t' \
             '# lr_vars.VarParam.set->Window.comboParam->lr_vars.AllFiles->(3):lr_vars.FilesWithParam'
        t4 = '(4) - порядковый номер вхождения {param} в файл(3).\n' \
             'param(1) в файле может встречатся несколько раз,\n' \
             'с разными (5)LB/RB. Нумерация с 0.\n\t' \
             '# Window.comboParts == file["Param"]["Count"]\n\t' \
             '# lr_vars.VarPartNum -> lr_vars.VarLB/lr_vars.VarRB'
        t6 = '(6) получить web_reg_save_param, с учетом (1)-(5)\n\t' \
             '# Window.ButtonShowParam\n\t' \
             '# lr_vars.VarWrspDict' \
             ' -> param.web_reg_save_param'

        lr_lib.gui.widj.tooltip.createToolTip(self.t3, t0)
        lr_lib.gui.widj.tooltip.createToolTip(self.comboFiles, t0)
        lr_lib.gui.widj.tooltip.createToolTip(self.comboParam, t1)
        lr_lib.gui.widj.tooltip.createToolTip(self.t1, t1)
        lr_lib.gui.widj.tooltip.createToolTip(self.t2, t2)
        lr_lib.gui.widj.tooltip.createToolTip(self.ButtonFindParamFiles, t2)
        lr_lib.gui.widj.tooltip.createToolTip(self.comboParts, t4)
        lr_lib.gui.widj.tooltip.createToolTip(self.t4, t4)
        lr_lib.gui.widj.tooltip.createToolTip(self.t6, t6)
        lr_lib.gui.widj.tooltip.createToolTip(self.ButtonShowParam, t6)
        
        lr_lib.gui.widj.tooltip.createToolTip(
            self.sortKey1,
            'sortKey1\nпри выборе - Формирует sortKey2.\nНекоторые ключи формируются после поиска(2)\n\t'
            '# Window.sortKey1\n\t# lr_vars.VarFileSortKey1 -> lr_vars.VarFileSortKey2'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.sortKey2,
            'sortKey2\nпри выборе - Сортировка файлов(3) в соответствие с выбранными sortKey ключами,\n'
            'те ключами файла(всплывающая подсказка для файла в комбобоксе(3), после поиска(2)).\n'
            'Некоторые ключи требуют включения чекбокса Статистика файлов.\n\t# Window.sortKey2\n\t'
            '# lr_vars.VarFileSortKey2 -> lr_vars.VarParam.set'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxOrdVersion,
            'версия функции поиска Ord: param.find_param_ord\n1 - новая(7.2.0)\n'
            '0 - старая - не находит Ord при пересечении LB/RB\n\t'
            '# Windows.cbxOrdVersion\n\t# lr_vars.VarOrdVersion'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.spin_toolTipTimeout,
            'время жизни, всплывающих подсказок, в мсек,\nтк подсказки иногда намертво "зависают"\n'
            ' 0 - "отключить" оборбражение\n\t'
            '# Windows.spin_toolTipTimeout\n\t# lr_vars.VarToolTipTimeout'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.t5l,
            '(5) LB - Левое поле.\nПри необходимости, необходимо отредактировать,\n'
            'если в поле попал "вариативный" параметр, нежелательные спец символы, и тд.\n'
            'После, нажать (6), для получения web_reg_save_param с новым Ord и LB\n'
            'УДАДЯТЬ символы из поля ТОЛЬКО "СЛЕВ"А{param} НАПРАВО,\nте Последний LB символ/ы удалять нельзя.\n\t'
            '# Window.LB\n\t'
            '# lr_vars.VarLB'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.t5r,
            '(5) RB - Правое поле.\nПри необходимости, необходимо отредактировать,\n'
            'если в поле попал "вариативный" параметр, нежелательные спец символы, и тд.\n'
            'После, нажать (6), для получения web_reg_save_param с новым Ord и RB\n'
            'УДАДЯТЬ символы из поля ТОЛЬКО СПРАВА {param}Н"ЕЛЕВО",\n'
            'те Первый RB символ/ы удалять нельзя.\n\t'
            '# Window.RB\n\t'
            '# lr_vars.VarRB'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonNewLB,
            'заново сформировать (5)LB, с учетом (1)-(5)\n\t'
            '# Window.ButtonNewLBRB -> lr_vars.VarPartNum'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonNewRB,
            'заново сформировать (5)RB, с учетом (1)-(5)\n\t# Window.ButtonNewLBRB -> lr_vars.VarPartNum'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LbB1Cbx,
            'по LB определить, если param находится внутри фигурных скобок: {... value="zkau_1", ...}\n'
            'Есди да, установить lr_vars.VarSplitListNumRB.set(1)\n\t'
            '# Window.LbB1Cbx\n\t'
            'lr_vars.VarLbB1'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RbB1Cbx,
            'по RB определить, если param находится внутри фигурных скобок: {... value="zkau_1", ...}\n'
            'Есди да, установить lr_vars.VarSplitListNumRB.set(1)\n\t'
            '# Window.RbB1Cbx\n\t'
            'lr_vars.VarRbB1'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LbB2Cbx,
            'по LB определить, если param находится внутри квадратных скобок: [... value="zkau_1", ...]\n'
            'Есди да, установить lr_vars.VarSplitListNumRB.set(3)\n\t'
            '# Window.LbB2Cbx\n\t'
            'lr_vars.VarLbB2'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RbB2Cbx,
            'по RB определить, если param находится внутри квадратных скобок: [... value="zkau_1", ...]\n'
            'Есди да, установить lr_vars.VarSplitListNumRB.set(3)\n\t'
            '# Window.RbB2Cbx\n\t'
            'lr_vars.VarRbB2'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RbRstripCbx,
            'обрезать Rb справа, до string.whitespace символов\n\t'
            '# Window.RbRstripCbx\n\t'
            'lr_vars.VarRbRstrip'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LbRstripCbx,
            'обрезать Lb слева, до string.whitespace символов\n\t'
            '# Window.LbRstripCbx\n\t'
            'lr_vars.VarLbRstrip'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RbEndCbx,
            'обрезать Rb, справа, до нежелательных символов, например "[]{},"\n\t'
            '# Window.RbEndCbx\n\t'
            'lr_vars.VarREnd'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LbEndCbx,
            'обрезать Lb, слева, до нежелательных символов, например "[]{},"\n\t'
            '# Window.LbEndCbx\n\t'
            'lr_vars.VarLEnd'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.actionButton,
            'открыть action.c файл, для поиска {param} из меню правой кнопки мыши\n\t'
            '# Window.actionButton'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonNote,
            'tk.Text в Блокнот/Editor\n\t'
            '# Window.ButtonNote'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonLog,
            'лог в Блокнот/Editor\n\t'
            '# Window.ButtonLog'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.max_lb,
            'макс кол-во символов в LB(5)\n'
            'нажать Enter\n\t'
            '# Window.max_lb_rb\n\t'
            '# lr_vars.VarMaxLen'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.max_rb,
            'макс кол-во символов в RB(5)\n'
            'нажать Enter\n\t'
            '# Window.max_lb_rb\n\t'
            '# lr_vars.VarMaxLen'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.Button_change_folder,
            'Смена директории поиска {param} файлов\n\t'
            '# Window.Button_change_folder\n\t'
            '# lr_vars.VarFilesFolder -> lr_vars.AllFiles'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonParamFileOpen,
            'файл(3) в Блокнот/Editor\n\t'
            '# Window.ButtonParamFileOpen'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonClearUp,
            'очистить tk.Text\n\t'
            '# Window.ButtonClearUp'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonClearDown,
            'очистить все поля ввода\n\t'
            '# Window.ButtonClearDown'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxClearShow,
            'очищать tk.Text,\n'
            'перед выводом(6)\n\t'
            '# Window.cbxClearShow'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LBcbx_SplitList,
            "обрезать LB(5) до ->>\n\t"
            "# Window.LBcbx_SplitList\n\t"
            "# lr_vars.VarSplitListLB"
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RBcbx_SplitList,
            "обрезать RB(5) до ->>\n\t"
            "# Window.RBcbx_SplitList\n\t"
            "# lr_vars.VarSplitListRB"
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LBent_SplitList,
            "<<- обрезать LB(5) до первого встретившегося значения из eval([ '...', ... ])\n"
            "При необходимости, можно добавить/удалить строки-разделители\n"
            "Делить, Не учитывая последних N символов строки LB(5) ->>\n\t"
            "# Window.ent_SplitList <- Window.LBcbx_SplitList"
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RBent_SplitList,
            "<<- обрезать RB(5) до первого встретившегося значения из "
            "eval([ '...', ... ])\n"
            "При необходимости, можно добавить/удалить строки-разделители\n"
            "Делить, Не учитывая первых N символов строки RB(5) ->>\n\t"
            "# Window.ent_SplitList <- Window.RBcbx_SplitList"
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LBSpinSplitList,
            '<<- Не учитывать N последних символов LB, при SplitList обрезке\nСтратерия использования:\n'
            ' 1 - (не рекомендуется) для формирования короткого и "безопасного" LB=, как следствие очень большой Ord=\n'
            ' 2 - (безопасный вариант) для формирования более короткого, но более "безопасного" LB=, '
            'как следствие большой Ord=\n'
            ' 3 - (основной вариант) для формирования более длинного LB=, как следствие маленький Ord='
            '\n\t# Window.LBSpinSplitList\n\t# lr_vars.VarSplitListNumLB'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RBSpinSplitList,
            '<<- Не учитывать первых N символов RB, при SplitList обрезке\n'
            ' 1 - (безопасный вариант) если param находится внутри фигурных скобок: {... value="zkau_1", ...}\n'
            '  те не гарантируется, что справа от "zkau_1"," будут теже символы.\n'
            '  для формирования короткого и "безопасного" RB=, как следствие очень большой Ord=\n'
            ' 2 - (основной вариант) если неизвестно где находится param\n'
            '  для формирования более короткого, но более "безопасного" RB=, как следствие большой Ord=\n'
            ' 3 и больше - (доп вариант) если param находится внутри квадратных скобок: [... value="zkau_1", ...]\n'
            '   для формирования более длинного RB=, как следствие маленький Ord=\n\t'
            '# Window.LBSpinSplitList\n\t# lr_vars.VarSplitListNumRB'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxClipboard,
            'копировать web_reg_save_param в буфер обмена\n'
            'при выводе(6)\n\t'
            '# Window.cbxClipboard'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LBcbx_return,
            'обрезать (5)LB до переноса строки\n\t'
            '# Window.cbx_return\n\t'
            '# lr_vars.VarReturn -> lr_vars.VarPartNum'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RBcbx_return,
            'обрезать (5)RB до переноса строки\n\t'
            '# Window.cbx_return\n\t'
            '# lr_vars.VarReturn -> lr_vars.VarPartNum'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.LBcbx_rus,
            'обрезать (5)LB до не ASCII либо Русских символов\n\t'
            '# Window.cbx_rus\n\t'
            '# lr_vars.VarRus -> lr_vars.VarPartNum'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.RBcbx_rus,
            'обрезать (5)RB до не ASCII либо Русских символов\n\t'
            '# Window.cbx_rus\n\t'
            '# lr_vars.VarRus -> lr_vars.VarPartNum'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.spin_RB_height,
            'изменить высоту RB\n\t'
            '# Window.spin_RB_height'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonRB_note,
            'RB в Блокнот/Editor\n\t'
            '# Window.ButtonRB_note'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.spin_LB_height,
            'изменить высоту LB\n\t'
            '# Window.spin_LB_height'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.change_folder_cbx,
            'Определить Файлы, для поиска(2)\n'
            ' On - Только файлы прописанные в *.inf - формат LoadRunner\n'
            ' Off - Все файлы каталога\n\t'
            '# Window.change_folder_cbx\n\t'
            '# lr_vars.VarIsSnapshotFiles -> lr_vars.AllFiles'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.ButtonLB_note,
            'LB в Блокнот/Editor\n\t'
            '# Window.ButtonLB_note'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxPopupWindow,
            'показывать popup окна\n'
            'финальные результаты, ошибки и тд\n\t'
            '# Window.cbxPopupWindow\n\t'
            '# lr_vars.VarShowPopupWindow'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.min_inf,
            'min номер inf.\n'
            'нижняя граница t*.inf, при поиске(2)\n\t'
            '# Window.min_inf'
            '\n\t# lr_vars.VarSearchMinSnapshot -> lr_vars.VarParam.set'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.max_inf,
            'max номер inf.\n'
            'верхняя граница t*.inf, при поиске(2)\n\t'
            '# Window.max_inf\n\t'
            '# lr_vars.VarSearchMaxSnapshot -> lr_vars.VarParam.set'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxAutoNoteParam,
            'открыть web_reg_save_param в Блокнот/Editor,\n'
            'при выводе(6)\n\t'
            '# Window.cbxAutoNoteParam'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.deny_file_cbx,
            'Определить Файлы, для поиска(2)\n'
            ' On - Все файлы.\n '
            'Off - Исключить файлы, подходящие под "списк исключения"\n\t'
            'lr_vars.DENY_* : *.c, *.gif, *.zip, ..., "*_Request*" и тд.\n\t'
            '# Window.deny_file_cbx\n\t'
            '# lr_vars.VarAllowDenyFiles -> lr_vars.AllFiles'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxAutoShowParam,
            'формировать web_reg_save_param, после поиска(2)\n'
            ' те выполнять шаги (3)-(6) автоматически\n\t'
            '# Window.cbxWrspAutoCreate'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.StrongSearchInFile_cbx,
            'принудительно использовать контроль LB/RB(на недопустимые символы),\n'
            'при поиске(2) param(1), в файлах(3) ответов\n'
            'вкл - меньше (3) и (4), те только "корректные"\n'
            'выкл - любые доступные (3) и (4), с ним лучше отключать чекб strip и deny\n\t'
            '# Window.StrongSearchInFile_cbx\n\t# lr_vars.VarStrongSearchInFile'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.filesStats_cbx,
            'Статискика файлов\n'
            ' On - создать статистику Сразу, для всех файлов (размер, кол-во символов и тд)\n'
            '       замедляет старт, ускоряет дальнейшую работу\n'
            ' Off - создавать статистику Отдельно, но однократно, для каждого выбранного файла\n'
            '         чтение статистики, однократно замедлит чтение любого выбранного файла\n '
            ' при выкл, сортировка специфическими sortKey1/2, может работать некорректно\n\t'
            '# Window.filesStats_cbx\n\t'
            '# lr_vars.VarAllFilesStatistic -> lr_vars.AllFiles'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxFirstLastFile,
            'автоматически выбирается первый файл из (3)\n'
            ' on - reverse список файлов\n'
            '# Window.cbxFirstLastFile\n\t'
            '# lr_vars.VarFirstLastFile -> lr_vars.VarFileName'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.cbxFileNamesNumsShow,
            'показывать имена найденых файлов и inf номера, после поиска(2)\n\t'
            '# Window.cbxFileNamesNumsShow\n\t'
            '# lr_vars.VarFileNamesNumsShow'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.comboLogger,
            'минимальный уровень вывода сообщений в gui\n\t'
            '# Window.comboLogger\n\t'
            '# lr_vars.VarWindowLogger'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.unblock,
            'разблокировать виджеты, во время работы\n\t'
            '# Window.unblock'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.partNumEmptyLbNext,
            'использовать следующее param вхождение(4) или файл(3)\n'
            'при пустом str.strip(LB(5))\n\t'
            '# Window.partNumEmptyLbNext\n\t'
            '# lr_vars.VarPartNumEmptyLbNext'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.partNumEmptyRbNext,
            'использовать следующее param вхождение(4) или файл(3)\n'
            'при пустом str.strip(RB(5))\n\t'
            '# Window.partNumEmptyRbNext\n\t'
            '# lr_vars.VarPartNumEmptyRbNext'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.partNumDenyLbNext,
            'использовать следующее param вхождение(4) или файл(3)\n'
            'при недопустимом LB(5), если последний cимвол LB:\n'
            'Буква, Цифра, или "_!-"\n\t'
            '# Window.partNumDenyLbNext\n\t'
            '# lr_vars.VarPartNumDenyLbNext'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.partNumDenyRbNext,
            'использовать следующее param вхождение(4) или файл(3)\n'
            'при недопустимом RB(5), если первый cимвол RB:\n'
            'Буква, Цифра, или "_!-"\n\t'
            '# Window.partNumDenyRbNext\n\t'
            '# lr_vars.VarPartNumDenyRbNext'
        )

    def set_grid(self):
        """grid всех виджетов для основного gui окна"""
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
