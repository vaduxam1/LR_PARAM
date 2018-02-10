# -*- coding: UTF-8 -*-
# tooltip для основного gui окна

import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.etc.help as lr_help


def set_all_main_window_tooltip(self) -> None:
    '''создать все tooltip основного gui окна'''
    t1 = '(1) Поле ввода {param}\n\t# Window.comboParam'
    t6 = '(6) получить web_reg_save_param, с учетом (1)-(5)\n\t# Window.ButtonShowParam\n\t# lr_vars.VarWrspDict' \
         ' -> param.web_reg_save_param'
    t2 = '(2) найти файлы(3), содержащие {param}(1)\n\t# Window.ButtonFindParamFiles\n\t' \
         '# lr_vars.VarParam.set->Window.comboParam->lr_vars.AllFiles->(3):lr_vars.FilesWithParam'
    lr_tooltip.createToolTip(self.t2, t2)
    lr_tooltip.createToolTip(self.t0, lr_help.CODE)
    lr_tooltip.createToolTip(self.t6, t6)
    lr_tooltip.createToolTip(self.comboParam, t1)
    lr_tooltip.createToolTip(self.t1, t1)
    lr_tooltip.createToolTip(self.ButtonFindParamFiles, t2)
    lr_tooltip.createToolTip(self.comboFiles, self._TT_text_comboFiles)
    lr_tooltip.createToolTip(self.sortKey1, 'sortKey1\nпри выборе - Формирует sortKey2.\nНекоторые ключи формируются '
                                         'после поиска(2)\n\t# Window.sortKey1\n\t# lr_vars.VarFileSortKey1 -> '
                                         'lr_vars.VarFileSortKey2')
    lr_tooltip.createToolTip(self.sortKey2, 'sortKey2\nпри выборе - Сортировка файлов(3) в соответствие с выбранными '
                                         'sortKey ключами,\nте ключами файла(всплывающая подсказка для файла в '
                                         'комбобоксе(3), после поиска(2)).\nНекоторые ключи требуют включения '
                                         'чекбокса Статистика файлов.\n\t# Window.sortKey2\n\t'
                                         '# lr_vars.VarFileSortKey2 -> lr_vars.VarParam.set')
    lr_tooltip.createToolTip(self.t3, self._TT_text_comboFiles)
    t4 = '(4) - порядковый номер вхождения {param} в файл(3).\nparam(1) в файле может встречатся несколько раз,\n' \
         'с разными (5)LB/RB. Нумерация с 0.\n\t# Window.comboParts == file["Param"]["Count"]\n\t' \
         '# lr_vars.VarPartNum -> lr_vars.VarLB/lr_vars.VarRB'
    lr_tooltip.createToolTip(self.comboParts, t4)
    lr_tooltip.createToolTip(self.t4, t4)
    lr_tooltip.createToolTip(self.t01, lr_help.WORK)
    lr_tooltip.createToolTip(self.t02, lr_help.ADD)
    lr_tooltip.createToolTip(self.cbxOrdVersion, 'версия функции поиска Ord: param.find_param_ord\n1 - новая(7.2.0)\n'
                                              '0 - старая - не находит Ord при пересечении LB/RB\n\t'
                                              '# Windows.cbxOrdVersion\n\t# lr_vars.VarOrdVersion')
    lr_tooltip.createToolTip(self.spin_toolTipTimeout, 'время жизни, всплывающих подсказок, в мсек,\nтк подсказки '
                                                    'иногда намертво "зависают"\n 0 - "отключить" оборбражение\n\t'
                                                    '# Windows.spin_toolTipTimeout\n\t# lr_vars.VarToolTipTimeout')
    lr_tooltip.createToolTip(self.t5l, '(5) LB - Левое поле.\nПри необходимости, необходимо отредактировать,\n'
                                    'если в поле попал "вариативный" параметр, нежелательные спец символы, и тд.\n'
                                    'После, нажать (6), для получения web_reg_save_param с новым Ord и LB\n'
                                    'УДАДЯТЬ символы из поля ТОЛЬКО "СЛЕВ"А{param} НАПРАВО,\nте Последний LB '
                                    'символ/ы удалять нельзя.\n\t# Window.LB\n\t# lr_vars.VarLB')
    lr_tooltip.createToolTip(self.t5r, '(5) RB - Правое поле.\nПри необходимости, необходимо отредактировать,\n'
                                    'если в поле попал "вариативный" параметр, нежелательные спец символы, и тд.\n'
                                    'После, нажать (6), для получения web_reg_save_param с новым Ord и RB\nУДАДЯТЬ '
                                    'символы из поля ТОЛЬКО СПРАВА {param}Н"ЕЛЕВО",\nте Первый RB символ/ы удалять '
                                    'нельзя.\n\t# Window.RB\n\t# lr_vars.VarRB')
    lr_tooltip.createToolTip(self.ButtonShowParam, t6)
    lr_tooltip.createToolTip(self.ButtonNewLB, 'заново сформировать (5)LB, с учетом (1)-(5)\n\t# Window.ButtonNewLBRB '
                                            '-> lr_vars.VarPartNum')
    lr_tooltip.createToolTip(self.ButtonNewRB, 'заново сформировать (5)RB, с учетом (1)-(5)\n\t# Window.ButtonNewLBRB '
                                            '-> lr_vars.VarPartNum')

    lr_tooltip.createToolTip(self.LbB1Cbx, 'по LB определить, если param находится внутри фигурных скобок: '
                                        '{... value="zkau_1", ...}\nЕсди да, установить '
                                        'lr_vars.VarSplitListNumRB.set(1)\n\t# Window.LbB1Cbx\n\tlr_vars.VarLbB1')
    lr_tooltip.createToolTip(self.RbB1Cbx, 'по RB определить, если param находится внутри фигурных скобок: '
                                        '{... value="zkau_1", ...}\nЕсди да, установить '
                                        'lr_vars.VarSplitListNumRB.set(1)\n\t# Window.RbB1Cbx\n\tlr_vars.VarRbB1')

    lr_tooltip.createToolTip(self.LbB2Cbx, 'по LB определить, если param находится внутри квадратных скобок: '
                                        '[... value="zkau_1", ...]\nЕсди да, установить '
                                        'lr_vars.VarSplitListNumRB.set(3)\n\t# Window.LbB2Cbx\n\tlr_vars.VarLbB2')
    lr_tooltip.createToolTip(self.RbB2Cbx, 'по RB определить, если param находится внутри квадратных скобок: '
                                        '[... value="zkau_1", ...]\nЕсди да, установить '
                                        'lr_vars.VarSplitListNumRB.set(3)\n\t# Window.RbB2Cbx\n\tlr_vars.VarRbB2')

    lr_tooltip.createToolTip(self.RbRstripCbx, 'обрезать Rb справа, до string.whitespace символов\n\t'
                                            '# Window.RbRstripCbx\n\tlr_vars.VarRbRstrip')
    lr_tooltip.createToolTip(self.LbRstripCbx, 'обрезать Lb слева, до string.whitespace символов\n\t'
                                            '# Window.LbRstripCbx\n\tlr_vars.VarLbRstrip')

    lr_tooltip.createToolTip(self.RbEndCbx, 'обрезать Rb, справа, до нежелательных символов, например "[]{},"\n\t'
                                            '# Window.RbEndCbx\n\tlr_vars.VarREnd')
    lr_tooltip.createToolTip(self.LbEndCbx, 'обрезать Lb, слева, до нежелательных символов, например "[]{},"\n\t'
                                            '# Window.LbEndCbx\n\tlr_vars.VarLEnd')

    lr_tooltip.createToolTip(self.actionButton, 'открыть action.c файл, для поиска {param} из меню правой кнопки мыши'
                                             '\n\t# Window.actionButton')
    lr_tooltip.createToolTip(self.ButtonNote, 'tk.Text в Блокнот/Editor\n\t# Window.ButtonNote')
    lr_tooltip.createToolTip(self.ButtonLog, 'лог в Блокнот/Editor\n\t# Window.ButtonLog')
    lr_tooltip.createToolTip(self.max_lb, 'макс кол-во символов в LB(5)\nнажать Enter\n\t# Window.max_lb_rb\n\t'
                                       '# lr_vars.VarMaxLen')
    lr_tooltip.createToolTip(self.max_rb, 'макс кол-во символов в RB(5)\nнажать Enter\n\t# Window.max_lb_rb\n\t'
                                       '# lr_vars.VarMaxLen')
    lr_tooltip.createToolTip(self.Button_change_folder, 'Смена директории поиска {param} файлов\n\t'
                                                     '# Window.Button_change_folder\n\t# lr_vars.VarFilesFolder '
                                                     '-> lr_vars.AllFiles')
    lr_tooltip.createToolTip(self.ButtonParamFileOpen, 'файл(3) в Блокнот/Editor\n\t# Window.ButtonParamFileOpen')
    lr_tooltip.createToolTip(self.ButtonClearUp, 'очистить tk.Text\n\t# Window.ButtonClearUp')
    lr_tooltip.createToolTip(self.ButtonClearDown, 'очистить все поля ввода\n\t# Window.ButtonClearDown')
    lr_tooltip.createToolTip(self.cbxClearShow, 'очищать tk.Text,\nперед выводом(6)\n\t# Window.cbxClearShow')
    lr_tooltip.createToolTip(self.LBcbx_SplitList, "обрезать LB(5) до ->>\n\t# Window.LBcbx_SplitList\n\t"
                                                "# lr_vars.VarSplitListLB")
    lr_tooltip.createToolTip(self.RBcbx_SplitList, "обрезать RB(5) до ->>\n\t# Window.RBcbx_SplitList\n\t"
                                                "# lr_vars.VarSplitListRB")
    lr_tooltip.createToolTip(self.LBent_SplitList, "<<- обрезать LB(5) до первого встретившегося значения из "
                                                "eval([ '...', ... ])\nПри необходимости, можно добавить/удалить "
                                                "строки-разделители\nДелить, Не учитывая последних N символов "
                                                "строки LB(5) ->>\n\t# Window.ent_SplitList <- "
                                                "Window.LBcbx_SplitList")
    lr_tooltip.createToolTip(self.RBent_SplitList, "<<- обрезать RB(5) до первого встретившегося значения из "
                                                "eval([ '...', ... ])\nПри необходимости, можно добавить/удалить "
                                                "строки-разделители\nДелить, Не учитывая первых N символов строки "
                                                "RB(5) ->>\n\t# Window.ent_SplitList <- Window.RBcbx_SplitList")
    lr_tooltip.createToolTip(
        self.LBSpinSplitList,
        '<<- Не учитывать N последних символов LB, при SplitList обрезке\nСтратерия использования:\n'
        ' 1 - (не рекомендуется) для формирования короткого и "безопасного" LB=, как следствие очень большой Ord=\n'
        ' 2 - (безопасный вариант) для формирования более короткого, но более "безопасного" LB=, '
        'как следствие большой Ord=\n'
        ' 3 - (основной вариант) для формирования более длинного LB=, как следствие маленький Ord='
        '\n\t# Window.LBSpinSplitList\n\t# lr_vars.VarSplitListNumLB')
    lr_tooltip.createToolTip(
        self.RBSpinSplitList,
        '<<- Не учитывать первых N символов RB, при SplitList обрезке\n'
        ' 1 - (безопасный вариант) если param находится внутри фигурных скобок: {... value="zkau_1", ...}\n'
        '  те не гарантируется, что справа от "zkau_1"," будут теже символы.\n'
        '  для формирования короткого и "безопасного" RB=, как следствие очень большой Ord=\n'
        ' 2 - (основной вариант) если неизвестно где находится param\n'
        '  для формирования более короткого, но более "безопасного" RB=, как следствие большой Ord=\n'
        ' 3 и больше - (доп вариант) если param находится внутри квадратных скобок: [... value="zkau_1", ...]\n'
        '   для формирования более длинного RB=, как следствие маленький Ord='
        '\n\t# Window.LBSpinSplitList\n\t# lr_vars.VarSplitListNumRB')
    lr_tooltip.createToolTip(self.cbxClipboard, 'копировать web_reg_save_param в буфер обмена\nпри выводе(6)\n\t'
                                             '# Window.cbxClipboard')
    lr_tooltip.createToolTip(self.LBcbx_return, 'обрезать (5)LB до переноса строки\n\t# Window.cbx_return\n\t'
                                             '# lr_vars.VarReturn -> lr_vars.VarPartNum')
    lr_tooltip.createToolTip(self.RBcbx_return, 'обрезать (5)RB до переноса строки\n\t# Window.cbx_return\n\t'
                                             '# lr_vars.VarReturn -> lr_vars.VarPartNum')
    lr_tooltip.createToolTip(self.LBcbx_rus, 'обрезать (5)LB до не ASCII либо Русских символов\n\t# Window.cbx_rus\n\t'
                                          '# lr_vars.VarRus -> lr_vars.VarPartNum')
    lr_tooltip.createToolTip(self.RBcbx_rus, 'обрезать (5)RB до не ASCII либо Русских символов\n\t# Window.cbx_rus\n\t'
                                          '# lr_vars.VarRus -> lr_vars.VarPartNum')
    lr_tooltip.createToolTip(self.spin_RB_height, 'изменить высоту RB\n\t# Window.spin_RB_height')
    lr_tooltip.createToolTip(self.ButtonRB_note, 'RB в Блокнот/Editor\n\t# Window.ButtonRB_note')
    lr_tooltip.createToolTip(self.spin_LB_height, 'изменить высоту LB\n\t# Window.spin_LB_height')
    lr_tooltip.createToolTip(self.change_folder_cbx, 'Определить Файлы, для поиска(2)\n On - Только файлы прописанные '
                                                  'в *.inf - формат LoadRunner\n Off - Все файлы каталога\n\t'
                                                  '# Window.change_folder_cbx\n\t# lr_vars.VarIsSnapshotFiles -> '
                                                  'lr_vars.AllFiles')
    lr_tooltip.createToolTip(self.ButtonLB_note, 'LB в Блокнот/Editor\n\t# Window.ButtonLB_note')
    lr_tooltip.createToolTip(self.cbxPopupWindow, 'показывать popup окна\nфинальные результаты, ошибки и тд\n\t'
                                               '# Window.cbxPopupWindow\n\t# lr_vars.VarShowPopupWindow')
    lr_tooltip.createToolTip(self.min_inf, 'min номер inf.\nнижняя граница t*.inf, при поиске(2)\n\t# Window.min_inf'
                                        '\n\t# lr_vars.VarSearchMinSnapshot -> lr_vars.VarParam.set')
    lr_tooltip.createToolTip(self.max_inf, 'max номер inf.\nверхняя граница t*.inf, при поиске(2)\n\t# Window.max_inf'
                                        '\n\t# lr_vars.VarSearchMaxSnapshot -> lr_vars.VarParam.set')
    lr_tooltip.createToolTip(self.cbxAutoNoteParam, 'открыть web_reg_save_param в Блокнот/Editor,\nпри выводе(6)\n\t'
                                                 '# Window.cbxAutoNoteParam')
    lr_tooltip.createToolTip(self.deny_file_cbx, 'Определить Файлы, для поиска(2)\n On - Все файлы.\n '
                                              'Off - Исключить файлы, подходящие под "списк исключения"\n         '
                                              'lr_vars.DENY_* : *.c, *.gif, *.zip, ..., "*_Request*" и тд.\n\t'
                                              '# Window.deny_file_cbx\n\t# lr_vars.VarAllowDenyFiles -> '
                                              'lr_vars.AllFiles')
    lr_tooltip.createToolTip(self.cbxAutoShowParam, 'формировать web_reg_save_param, после поиска(2)\n те выполнять '
                                                 'шаги (3)-(6) автоматически\n\t# Window.cbxWrspAutoCreate')
    lr_tooltip.createToolTip(
        self.StrongSearchInFile_cbx, 'принудительно использовать контроль LB/RB(на недопустимые символы), '
                                     '\nпри поиске(2) param(1), в файлах(3) ответов\n'
                                     'вкл - меньше (3) и (4), те только "корректные"\n'
                                     'выкл - любые доступные (3) и (4), с ним лучше отключать чекб strip и deny'
                                     '\n\t# Window.StrongSearchInFile_cbx\n\t# lr_vars.VarStrongSearchInFile')
    lr_tooltip.createToolTip(self.filesStats_cbx,
                             'Статискика файлов\n On - создать статистику Сразу, для всех файлов'
                             ' (размер, кол-во символов и тд)\n       замедляет старт, ускоряет '
                             'дальнейшую работу\n Off - создавать статистику Отдельно, но '
                             'однократно, для каждого выбранного файла\n         чтение '
                             'статистики, однократно замедлит чтение любого выбранного файла\n '
                             '        при выкл, сортировка специфическими sortKey1/2, может '
                                               'работать некорректно\n\t# Window.filesStats_cbx\n\t'
                                               '# lr_vars.VarAllFilesStatistic -> lr_vars.AllFiles')
    lr_tooltip.createToolTip(self.cbxFirstLastFile, 'выброр файла в (3)\non - последний\noff - первый\n\t'
                                                 '# Window.cbxFirstLastFile\n\t# lr_vars.VarFirstLastFile -> '
                                                 'lr_vars.VarFileName')
    lr_tooltip.createToolTip(self.cbxFileNamesNumsShow, 'показывать имена найденых файлов и inf номера, после '
                                                     'поиска(2)\n\t# Window.cbxFileNamesNumsShow\n\t'
                                                     '# lr_vars.VarFileNamesNumsShow')
    lr_tooltip.createToolTip(self.comboLogger, 'минимальный уровень вывода сообщений в gui\n\t# Window.comboLogger\n\t'
                                            '# lr_vars.VarWindowLogger')
    lr_tooltip.createToolTip(self.unblock, 'разблокировать виджеты, во время работы\n\t# Window.unblock')
    lr_tooltip.createToolTip(self.partNumEmptyLbNext, 'использовать следующее param вхождение(4) или файл(3)\n'
                                                   'при пустом str.strip(LB(5))\n\t# Window.partNumEmptyLbNext\n\t'
                                                   '# lr_vars.VarPartNumEmptyLbNext')
    lr_tooltip.createToolTip(self.partNumEmptyRbNext, 'использовать следующее param вхождение(4) или файл(3)\n'
                                                   'при пустом str.strip(RB(5))\n\t# Window.partNumEmptyRbNext\n\t'
                                                   '# lr_vars.VarPartNumEmptyRbNext')
    lr_tooltip.createToolTip(self.partNumDenyLbNext, 'использовать следующее param вхождение(4) или файл(3)\n'
                                                  'при недопустимом LB(5), если последний cимвол LB:\nБуква, Цифра,'
                                                  ' или "_!-"\n\t# Window.partNumDenyLbNext\n\t'
                                                  '# lr_vars.VarPartNumDenyLbNext')
    lr_tooltip.createToolTip(self.partNumDenyRbNext, 'использовать следующее param вхождение(4) или файл(3)\nпри '
                                                  'недопустимом RB(5), если первый cимвол RB:\nБуква, Цифра, или '
                                                  '"_!-"\n\t# Window.partNumDenyRbNext\n\t'
                                                  '# lr_vars.VarPartNumDenyRbNext')
