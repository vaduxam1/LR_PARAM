# -*- coding: UTF-8 -*-
# tooltip action.c окна

import os
import lr_lib.gui.widj.tooltip as lr_tooltip
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.help as lr_help


def set_all_action_window_tooltip(self) -> None:
    '''создать все tooltip action окна'''
    lr_tooltip.createToolTip(self.editor_button, 'открыть текст action в блокноте\n\t'
                                                 '# editor_button')
    lr_tooltip.createToolTip(self.wrsp_setting, 'настройки каментов и имени wrsp\n\t'
                                                '# wrsp_setting')
    lr_tooltip.createToolTip(self.backup_entry, 'макс кол-во backup файлов(запись по кругу)\n'
                                                'перед автозаменой, в директорию {}, делается action бэкап\n\t'
                                                '# backup_entry'.format(os.path.join(os.getcwd(), lr_vars.BackupFolder)))
    lr_tooltip.createToolTip(self.buttonColorReset, 'сбросить цвет текста\n\t'
                                                    '# buttonColorReset')
    lr_tooltip.createToolTip(self.highlight_Thread, 'выполнять в фоне, весь код подсветки\n\t'
                                                    '# highlight_Thread')
    lr_tooltip.createToolTip(self.highlight_LineThread, 'выполнять в фоне, код подсветки для одной линии\n\t'
                                                        '# highlight_LineThread')
    lr_tooltip.createToolTip(self.highlight_TagThread, 'выполнять в фоне, код подсветки для одного тега\n\t'
                                                       '# highlight_TagThread')
    lr_tooltip.createToolTip(self.highlight_MThread, 'искать индексы для подсветки линий, в M_POOL\n\t'
                                                     '# highlight_MThread')
    lr_tooltip.createToolTip(self.highlight_LinesPortionSize, 'для скольки линий, искать индексы, за один проход/поток'
                                                              '\n\t# highlight_LinesPortionSize')

    lr_tooltip.createToolTip(self.open_button, 'открыть action.c файл\n\t'
                                               '# open_button')
    lr_tooltip.createToolTip(self.highlight_cbx, 'On - применить подсветку\n'
                                                 'Off - убрать подсветку\n'
                                                 'Чтобы применмть новую подсветку, необходимо снять/установить повторно\n\t'
                                                 '# highlight_cbx')
    lr_tooltip.createToolTip(self.search_res_combo, 'результаты(координаты) поиска слова в тексте action.c:\n'
                                                 '"201.33+2c" - [Строка].[Столбец]+[ДлинаСлова]c\nпри выборе - '
                                                 'переход в область,колесом мыши - переход между областями\n'
                                                 'учной ввод координат по <<Enter>>\n\t# search_res_combo')
    lr_tooltip.createToolTip(self.search_button, 'Поиск слова из search_entry в тексте action\n'
                                                 'результат - заполняет комбобокс координат search_res_combo\n\t'
                                                 '# search_button')
    lr_tooltip.createToolTip(self.search_entry, 'слово для поиска в тексте action\n\t'
                                                '# search_entry')
    lr_tooltip.createToolTip(self.SearchReplace_searchCombo, 'слово, для замены\n\t'
                                                             '# SearchReplace_searchCombo')
    lr_tooltip.createToolTip(self.SearchReplace_replaceCombo, 'слово, на которое заменить\n\t'
                                                              '# SearchReplace_replaceCombo')
    lr_tooltip.createToolTip(self.SearchReplace_button, 'Найти и Заменить, для SearchReplace_комбобоксов\n'
                                                        'Обычная(как в блокноте) автозамена\n\t'
                                                        '# SearchReplace_button')
    lr_tooltip.createToolTip(self.up_search_button, 'перейти вверх, по результатам поиска\n\t'
                                                    '# up_search_button')
    lr_tooltip.createToolTip(self.down_search_button, 'перейти вниз, по результатам поиска\n\t'
                                                      '# down_search_button')
    lr_tooltip.createToolTip(self.backup_open_button, 'открыть бэкап файл, для текущего окна\n\t'
                                                      '# backup_open_button')
    lr_tooltip.createToolTip(self.force_ask_cbx, 'Автозамена - подтверждать любую замену.\n'
                                                 'Те показывать окно диалога подтверждения, для каждой замены.\n\t'
                                                 '# force_ask_cbx')
    lr_tooltip.createToolTip(self.no_cbx, 'Автозамена - Принудительно отвечать "Нет, для Всех" в вопросе замены,\n'
                                          'В обычной ситуации, от пользователя, требуетcя подтверждение,\n'
                                          'если заменяемое слово, является частью другого, более длинного слова\n'
                                          'Например при замене "zkau_2", для "zkau_201", "zkau_20", "Azkau_2",...\n'
                                          'В результате - не показывать окно диалога подтверждения.\n\t'
                                          '# no_cbx')
    lr_tooltip.createToolTip(self.final_wnd_cbx, 'окно результата создания param\n'
                                                 'перед показом окна, будет сделан переход на web_reg_save_param\n'
                                                 'и пока не нажата кнопка OK, можно визуально проконтролировать LR/RB.\n'
                                                 'после закрытия окна, будет сделан переход на первый замененный param\n\t'
                                                 '# final_wnd_cbx')
    lr_tooltip.createToolTip(self.auto_param_creator_button, 'автоматичейский поиск и создание web_reg_save_param\n '
                                                             'для param, имя которых начинается на ...\n'
                                                             'аналог нескольких меню_мыши/web_reg_save_param/группа\n\t'
                                                             '# auto_param_creator_button')
    lr_tooltip.createToolTip(self.help1, lr_help.ACTION1)
    lr_tooltip.createToolTip(self.help2, lr_help.ACTION2)
    lr_tooltip.createToolTip(self.help3, lr_help.ACTION3)
    lr_tooltip.createToolTip(self.save_action_button, 'сохранить текст action окна\n'
                                                      '+ обновить "служебную" инфу об удаленных "inf-блоках", если чтото удаляли вручную\n\t'
                                                      '# save_action_button')

    lr_tooltip.createToolTip(self.selection_font_combo, 'шрифт, для выделения\n\t'
                                                        '# selection_font_combo')
    lr_tooltip.createToolTip(self.selection_font_size_entry, 'размер шрифта, для выделения\n\t'
                                                             '# selection_font_size_entry')
    lr_tooltip.createToolTip(self.selection_bold_cbx, 'жирный шрифт, для выделения\n\t'
                                                      '# selection_bold_cbx')
    lr_tooltip.createToolTip(self.selection_underline_cbx, 'подчеркнутый шрифт, для выделения\n\t'
                                                           '# selection_underline_cbx')
    lr_tooltip.createToolTip(self.selection_overstrike_cbx, 'зачеркнутый шрифт, для выделения\n\t'
                                                            '# selection_overstrike_cbx')
    lr_tooltip.createToolTip(self.selection_slant_cbx, 'курсив шрифт, для выделения\n\t'
                                                       '# selection_slant_cbx')

    lr_tooltip.createToolTip(self.wrsp_combo, 'имя web_reg_save_param\n'
                                              'переход в область action.c текста\n\t'
                                              '# wrsp_combo')
    lr_tooltip.createToolTip(self.param_combo, 'имя param\n'
                                               'переход в область action.c текста\n\t'
                                               '# param_combo')
    lr_tooltip.createToolTip(self.inf_combo, 'номер inf блока\n'
                                             'переход в область action.c текста\n\t'
                                             '# inf_combo')
    lr_tooltip.createToolTip(self.transaction_combo, 'имя транцакции\n'
                                                     'переход в область action.c текста\n\t'
                                                     '# transaction_combo')

    lr_tooltip.createToolTip(self.font_combo, 'шрифт\n\t'
                                              '# font_combo')
    lr_tooltip.createToolTip(self.font_size_entry, 'размер шрифта\n\t'
                                                   '# font_size_entry')
    lr_tooltip.createToolTip(self.bold_cbx, 'жирный шрифт\n\t'
                                            '# bold_cbx')
    lr_tooltip.createToolTip(self.underline_cbx, 'подчеркнутый шрифт\n\t'
                                                 '# underline_cbx')
    lr_tooltip.createToolTip(self.overstrike_cbx, 'зачеркнутый шрифт\n\t'
                                                  '# overstrike_cbx')
    lr_tooltip.createToolTip(self.slant_cbx, 'курсив шрифт\n\t'
                                             '# slant_cbx')
    lr_tooltip.createToolTip(self.dummy_button, 'удалить все dummy web_submit_data из action.c текста\n\t'
                                                '# dummy_button')
    lr_tooltip.createToolTip(self.background_color_combo, 'цвет фона tk.Text\n\t'
                                                          '# background_color_combo')
    lr_tooltip.createToolTip(self.force_yes_inf_checker_cbx, 'принудительно отвечать "Да", при вопросе о создании param\n'
                                                             'если inf-номер запроса <= inf-номер web_reg_save_param\n\t'
                                                             '# force_yes_inf_checker_cbx')
    lr_tooltip.createToolTip(self.unblock, 'разблокировать виджеты, во время работы\n\t'
                                           '# unblock')
    lr_tooltip.createToolTip(self.lr_think_time, 'удалить все lr_think_time\n\t'
                                                 '# lr_think_time')
    lr_tooltip.createToolTip(self.lr_report_A, 'краткий отчет об action.c, с учетом вложенности транзакций\n\t'
                                               '# lr_report_A')
    lr_tooltip.createToolTip(self.lr_report_B, 'полный отчет об action.c\n\t'
                                               '# lr_report_B')
    lr_tooltip.createToolTip(self.transaction_rename, 'переименовать имена транзакций\n\t'
                                                      '# transaction_rename')
    lr_tooltip.createToolTip(self.max_inf_cbx, 'ограничить диапазон поиска param - максимальный номер inf\n'
                                               'Это номер inf, в action.c, где первый раз встречается pram\n\t'
                                               '# max_inf_cbx')
    lr_tooltip.createToolTip(self.add_inf_cbx, 'макс номер inf, для поиска param, в LoadRunner файлах ответов\n '
                                               'On - inf, где первый раз встречается pram, в action.c\n\t'
                                               'что неправильно но необходимо, тк LoadRunner так записывает\n'
                                               'Off - inf, предшествующий, номеру inf, где первый раз встречается pram, в action.c\n\t'
                                               'используется, совместно с чекбоксом last, для поиска inf-ответа,\n\t'
                                               'максимально близкого, к param-inf, те поиску с конца\n\t'
                                               '# add_inf_cbx')