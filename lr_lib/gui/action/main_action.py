# -*- coding: UTF-8 -*-
# action.с окно - главный

import os

import tkinter as tk

import lr_lib
import lr_lib.gui.action.act_win
import lr_lib.gui.widj.tooltip
import lr_lib.gui.wrsp.top.top_allfiles
import lr_lib.gui.etc.gui_other
import lr_lib.gui.etc.group_param
import lr_lib.gui.widj.wrsp_setting
import lr_lib.gui.etc.action_lib
import lr_lib.core.var.vars as lr_vars


class ActionWindow(lr_lib.gui.action.act_win.ActWin):
    """окно action.c
    ActionWindow
    lr_act_win.ActWin
    lr_act_any.ActAny
    lr_act_goto.ActGoto
    lr_act_font.ActFont
    lr_act_replace.ActReplaceRemove
    lr_act_search.ActSearch
    lr_act_serializ.TkTextWebSerialization
    lr_act_backup.ActBackup
    lr_act_block.ActBlock
    lr_act_scroll.ActScrollText
    lr_act_widj.ActWidj
    lr_act_var.ActVar
    lr_act_toplevel.ActToplevel
    tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_win.ActWin.__init__(self)

        self.set_grid()  # расположить виджеты
        self.set_tooltip()  # создать tooltip виджетов

        self.open_action()  # открыть action текст
        self.tk_text.init()

        self.menubar = tk.Menu()
        self.config(menu=self.menubar)
        self.set_menu()

        lr_lib.gui.etc.gui_other.center_widget(self)
        return

    def set_menu(self) -> None:
        """menubar"""
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="WRSP Setting", command=lambda: lr_lib.gui.widj.wrsp_setting.WrspSettingWindow(parent=self))
        filemenu.add_command(label="Web Legend Window", command=self.legend)
        filemenu.add_command(label="show/hide main bar", command=self.show_hide_bar_1)
        filemenu.add_command(label="show/hide navigation bar", command=self.show_hide_bar_2)
        filemenu.add_command(label="show/hide info bar", command=self.show_hide_bar_3)
        filemenu.add_command(label="report_A", command=lambda: lr_lib.gui.etc.gui_other.repA(self.tk_text))
        filemenu.add_command(label="report_B", command=lambda: lr_lib.gui.etc.gui_other.repB(self.tk_text))
        filemenu.add_command(label="Exit", command=self.destroy)
        self.menubar.add_cascade(label="Show/Hide", menu=filemenu)

        filemenu2 = tk.Menu(self.menubar, tearoff=0)
        filemenu2.add_command(label="Open", command=lambda: self.open_action_dialog(title=True, folder=lr_vars.BackupFolder))
        filemenu2.add_command(label="Save", command=self.save_action_file)
        filemenu2.add_command(label="Перенести текст_на_экране, во внутр_предсталение", command=self.tk_text_to_web_action)
        filemenu2.add_command(label="Перенести внутр_предсталение, в текст_на_экране", command=self.web_action_to_tk_text)
        self.menubar.add_cascade(label="Open/Save", menu=filemenu2)

        filemenu3 = tk.Menu(self.menubar, tearoff=0)
        filemenu3.add_command(label="Remove dummy", command=self.remove_web_dummy_template)
        filemenu3.add_command(label="Remove thinktime", command=self.thinktime_remove)
        filemenu3.add_command(label="Rename transaction", command=self.all_transaction_rename)
        filemenu3.add_command(label="Rename WRSP", command=lambda: lr_lib.gui.etc.action_lib.all_wrsp_auto_rename(self))
        self.menubar.add_cascade(label="Remove/Rename", menu=filemenu3)

        filemenu4 = tk.Menu(self.menubar, tearoff=0)
        filemenu4.add_command(label="Найти и Создать WRSP", command=lambda: lr_lib.gui.etc.group_param.auto_param_creator(self))
        filemenu4.add_command(label="regexp: найти и создать WRSP", command=lambda: lr_lib.gui.etc.group_param.re_auto_param_creator(self))
        self.menubar.add_cascade(label="Запуск", menu=filemenu4)

        filemenu5 = tk.Menu(self.menubar, tearoff=0)
        filemenu5.add_command(label="по Snapshot inf номерам", command=lambda: lr_lib.gui.etc.action_lib.snapshot_files(self.tk_text, i_num=1))
        filemenu5.add_command(label="подряд", command=lambda: lr_lib.gui.wrsp.top.top_allfiles.TopFolder(self))
        self.menubar.add_cascade(label="Файлы ответов", menu=filemenu5)
        return

    def set_tooltip(self) -> None:
        """создать все tooltip action окна"""
        lr_lib.gui.widj.tooltip.createToolTip(self.help1, lr_lib.etc.help.ACTION1)
        lr_lib.gui.widj.tooltip.createToolTip(self.help2, lr_lib.etc.help.ACTION2)
        lr_lib.gui.widj.tooltip.createToolTip(self.help3, lr_lib.etc.help.ACTION3)

        lr_lib.gui.widj.tooltip.createToolTip(
            self.editor_button,
            'открыть текст action в блокноте\n\t'
            '# editor_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.btn_all_files,
            'список всех файлов\n\t'
            '# btn_all_files'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.lr_legend,
            'окно web_ леленды\n\t'
            '# lr_legend'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.wrsp_setting,
            'настройки каментов и имени wrsp\n\t'
            '# wrsp_setting'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.resp_btn,
            'файлы ответов при записи и воспроизведении\n\t'
            '# resp_btn'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.backup_entry,
            'макс кол-во backup файлов(запись по кругу)\n'
            'перед автозаменой, в директорию {}, делается action бэкап\n\t'
            '# backup_entry'.format(os.path.join(os.getcwd(), lr_vars.BackupFolder))
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.buttonColorReset,
            'сбросить цвет текста\n\t'
            '# buttonColorReset'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.highlight_After0,
            'задержка(мс), перед перезапуском проверки необходимости подсветки\n\t'
            '# highlight_After0'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.highlight_After1,
            'задержка(мс), перед стартом подсветки всех линий, отображенных на экране\n\t'
            '# highlight_After1'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.highlight_After2,
            'задержка(мс), перед подсветкой одной линии\n\t'
            '# highlight_After2'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.open_button,
            'открыть action.c файл\n\t'
            '# open_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.highlight_cbx,
            'On - применить подсветку\n'
            'Off - убрать подсветку\n'
            'Чтобы применмть новую подсветку, необходимо снять/установить повторно\n\t'
            '# highlight_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.search_res_combo,
            'результаты(координаты) поиска слова в тексте action.c:\n'
            '"201.33+2c" - [Строка].[Столбец]+[ДлинаСлова]c\nпри выборе - '
            'переход в область,колесом мыши - переход между областями\n'
            'учной ввод координат по <<Enter>>\n\t# search_res_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.search_button,
            'Поиск слова из search_entry в тексте action\n'
            'результат - заполняет комбобокс координат search_res_combo\n\t'
            '# search_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.search_entry,
            'слово для поиска в тексте action\n\t'
            '# search_entry'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.SearchReplace_searchCombo,
            'слово, для замены\n\t'
            '# SearchReplace_searchCombo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.SearchReplace_replaceCombo,
            'слово, на которое заменить\n\t'
            '# SearchReplace_replaceCombo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.SearchReplace_button,
            'Найти и Заменить, для SearchReplace_комбобоксов\n'
            'Обычная(как в блокноте) автозамена\n\t'
            '# SearchReplace_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.up_search_button,
            'перейти вверх, по результатам поиска\n\t'
            '# up_search_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.down_search_button,
            'перейти вниз, по результатам поиска\n\t'
            '# down_search_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.backup_open_button,
            'открыть бэкап файл, для текущего окна\n\t'
            '# backup_open_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.force_ask_cbx,
            'Автозамена - подтверждать любую замену.\n'
            'Те показывать окно диалога подтверждения, для каждой замены.\n\t'
            '# force_ask_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.no_cbx,
            'Автозамена - Принудительно отвечать "Нет, для Всех" в вопросе замены,\n'
            'В обычной ситуации, от пользователя, требуетcя подтверждение,\n'
            'если заменяемое слово, является частью другого, более длинного слова\n'
            'Например при замене "zkau_2", для "zkau_201", "zkau_20", "Azkau_2",...\n'
            'В результате - не показывать окно диалога подтверждения.\n\t'
            '# no_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.final_wnd_cbx,
            'окно результата создания param\n'
            'перед показом окна, будет сделан переход на web_reg_save_param\n'
            'и пока не нажата кнопка OK, можно визуально проконтролировать LR/RB.\n'
            'после закрытия окна, будет сделан переход на первый замененный param\n\t'
            '# final_wnd_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.auto_param_creator_button,
            'автоматичейский поиск и создание web_reg_save_param\n '
            'для param, имя которых начинается на ...\n'
            'аналог нескольких меню_мыши/web_reg_save_param/группа\n\t'
            '# auto_param_creator_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.re_auto_param_creator_button,
            'автоматичейский поиск и создание web_reg_save_param\n '
            'поиск param, на основе регулярных выражений.\n'
            'аналог нескольких меню_мыши/web_reg_save_param/группа\n\t'
            '# re_auto_param_creator_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.save_action_button,
            'сохранить текст action окна\n'
            '+ обновить "служебную" инфу об удаленных "inf-блоках", если чтото удаляли вручную\n\t'
            '# save_action_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.selection_font_combo,
            'шрифт, для выделения\n\t'
            '# selection_font_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.selection_font_size_entry,
            'размер шрифта, для выделения\n\t'
            '# selection_font_size_entry'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.selection_bold_cbx,
            'жирный шрифт, для выделения\n\t'
            '# selection_bold_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.selection_underline_cbx,
            'подчеркнутый шрифт, для выделения\n\t'
            '# selection_underline_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.selection_overstrike_cbx,
            'зачеркнутый шрифт, для выделения\n\t'
            '# selection_overstrike_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.selection_slant_cbx,
            'курсив шрифт, для выделения\n\t'
            '# selection_slant_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.wrsp_combo,
            'имя web_reg_save_param\n'
            'переход в область action.c текста\n\t'
            '# wrsp_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.param_combo,
            'имя param\n'
            'переход в область action.c текста\n\t'
            '# param_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.inf_combo,
            'номер inf блока\n'
            'переход в область action.c текста\n\t'
            '# inf_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.transaction_combo,
            'имя транцакции\n'
            'переход в область action.c текста\n\t'
            '# transaction_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.font_combo, 'шрифт\n\t'
            '# font_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.font_size_entry,
            'размер шрифта\n\t'
            '# font_size_entry'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.bold_cbx,
            'жирный шрифт\n\t'
            '# bold_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.underline_cbx,
            'подчеркнутый шрифт\n\t'
            '# underline_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.overstrike_cbx,
            'зачеркнутый шрифт\n\t'
            '# overstrike_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.slant_cbx,
            'курсив шрифт\n\t'
            '# slant_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.dummy_button,
            'удалить все dummy web_submit_data из action.c текста\n\t'
            '# dummy_button'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.background_color_combo,
            'цвет фона tk.Text\n\t'
            '# background_color_combo'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.force_yes_inf_checker_cbx,
            'принудительно отвечать "Да", при вопросе о создании param\n'
            'если inf-номер запроса <= inf-номер web_reg_save_param\n\t'
            '# force_yes_inf_checker_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.unblock,
            'разблокировать виджеты, во время работы\n\t'
            '# unblock'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.lr_think_time,
            'удалить все lr_think_time\n\t'
            '# lr_think_time'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.lr_report_A,
            'краткий отчет об action.c, с учетом вложенности транзакций\n\t'
            '# lr_report_A'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.lr_report_B,
            'полный отчет об action.c\n\t'
            '# lr_report_B'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.transaction_rename,
            'переименовать имена транзакций\n\t'
            '# transaction_rename'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.max_inf_cbx,
            'ограничить диапазон поиска param - максимальный номер inf\n'
            'Это номер inf, в action.c, где первый раз встречается pram\n\t'
            '# max_inf_cbx'
        )
        lr_lib.gui.widj.tooltip.createToolTip(
            self.add_inf_cbx,
            'макс номер inf, для поиска param, в LoadRunner файлах ответов\n '
            'On - inf, где первый раз встречается pram, в action.c\n\t'
            'что неправильно но необходимо, тк LoadRunner так записывает\n'
            'Off - inf, предшествующий, номеру inf, где первый раз встречается pram, в action.c\n\t'
            'используется, совместно с чекбоксом last, для поиска inf-ответа,\n\t'
            'максимально близкого, к param-inf, те поиску с конца\n\t'
            '# add_inf_cbx'
        )
        return

    def set_grid(self):
        """grid всех виджетов action.с окна"""
        self.search_entry.grid(row=5, column=0, columnspan=8, sticky=tk.NSEW)
        self.search_button.grid(row=5, column=8, sticky=tk.NSEW)
        self.down_search_button.grid(row=5, column=9, sticky=tk.NSEW)
        self.search_res_combo.grid(row=5, column=10, sticky=tk.NSEW, columnspan=3)
        self.up_search_button.grid(row=5, column=13, sticky=tk.NSEW)

        self.backup_open_button.grid(row=5, column=16, columnspan=2, sticky=tk.NSEW)
        self.save_action_button.grid(row=6, column=17, sticky=tk.NSEW)

        self.highlight_cbx.grid(row=1, column=1, sticky=tk.NSEW, columnspan=5)
        self.background_color_combo.grid(row=2, column=1, sticky=tk.NSEW, columnspan=5)
        self.buttonColorReset.grid(row=3, column=1, sticky=tk.NSEW)
        self.highlight_After0.grid(row=3, column=2, sticky=tk.NSEW)
        self.highlight_After1.grid(row=3, column=3, sticky=tk.NSEW)
        self.highlight_After2.grid(row=3, column=4, sticky=tk.NSEW)

        self.open_button.grid(row=6, column=16, sticky=tk.NSEW)
        self.editor_button.grid(row=7, column=16, sticky=tk.NSEW, columnspan=2)
        self.no_cbx.grid(row=7, column=10, sticky=tk.W)
        self.auto_param_creator_button.grid(row=7, column=8, sticky=tk.NSEW)
        self.re_auto_param_creator_button.grid(row=8, column=8, sticky=tk.NSEW)
        self.force_ask_cbx.grid(row=8, column=10, sticky=tk.W)
        self.unblock.grid(row=9, column=17, sticky=tk.NSEW)
        self.final_wnd_cbx.grid(row=8, column=12, sticky=tk.W)
        self.wrsp_setting.grid(row=7, column=9, sticky=tk.NSEW)
        self.resp_btn.grid(row=7, column=3, sticky=tk.NSEW)

        self.font_size_entry.grid(row=12, column=4, sticky=tk.NSEW)
        self.font_combo.grid(row=10, column=0, columnspan=10, sticky=tk.NSEW)
        self.bold_cbx.grid(row=12, column=5, sticky=tk.NSEW)
        self.overstrike_cbx.grid(row=12, column=6, sticky=tk.NSEW)
        self.underline_cbx.grid(row=12, column=7, sticky=tk.NSEW)
        self.slant_cbx.grid(row=12, column=8, sticky=tk.NSEW)
        self.backup_entry.grid(row=9, column=16, sticky=tk.NSEW)

        self.selection_font_combo.grid(row=11, column=0, columnspan=10, sticky=tk.NSEW)
        self.selection_font_size_entry.grid(row=13, column=4, sticky=tk.NSEW)
        self.selection_bold_cbx.grid(row=13, column=5, sticky=tk.NSEW)
        self.selection_overstrike_cbx.grid(row=13, column=6, sticky=tk.NSEW)
        self.selection_underline_cbx.grid(row=13, column=7, sticky=tk.NSEW)
        self.selection_slant_cbx.grid(row=13, column=8, sticky=tk.NSEW)

        self.SearchReplace_searchCombo.grid(row=6, column=0, columnspan=8, sticky=tk.NSEW)
        self.SearchReplace_replaceCombo.grid(row=6, column=9, columnspan=8, sticky=tk.NSEW)
        self.SearchReplace_button.grid(row=6, column=8, sticky=tk.NSEW)

        # self.toolbar.grid(row=2, column=0, sticky=tk.N, columnspan=100)

        # self.middle_bar.grid(row=3, column=0, sticky=tk.N)
        self.inf_bar.grid(row=3, column=1, sticky=tk.N)
        self.transaction_bar.grid(row=3, column=2, sticky=tk.E)
        self.wrsp_bar.grid(row=3, column=3, sticky=tk.W)

        self.file_bar.grid(row=5, column=20, sticky=tk.NSEW, rowspan=5)
        self.cbx_bar.grid(row=5, column=50, sticky=tk.NSEW, rowspan=5)
        self.font_toolbar.grid(row=5, column=21, sticky=tk.NSEW, rowspan=4)

        self.text_scrolly.grid(row=0, column=201, sticky=tk.NSEW)
        self.text_scrollx.grid(row=1, column=0, sticky=tk.NSEW, columnspan=201)
        # self.scroll_lab.grid(row=1, column=1, sticky=tk.NSEW)
        # self.scroll_lab2.grid(row=2, column=300, sticky=tk.NSEW, rowspan=2)

        self.inf_combo.grid(row=1, column=1, sticky=tk.NSEW)
        self.transaction_combo.grid(row=1, column=2, sticky=tk.NSEW)
        self.wrsp_combo.grid(row=1, column=3, sticky=tk.NSEW)
        self.param_combo.grid(row=1, column=4, sticky=tk.NSEW)

        self.help1.grid(row=1, column=201, sticky=tk.NSEW)
        # self.help2.grid(row=2, column=201, sticky=tk.NSEW)
        # self.help3.grid(row=3, column=201, sticky=tk.NSEW)

        self.tk_text.grid(row=0, column=1, sticky=tk.NSEW, columnspan=201)
        self.tk_text.linenumbers.grid(row=0, column=0, sticky=tk.NSEW)
        self.tk_text.linenumbers.config(width=30)

        self.max_inf_cbx.grid(row=7, column=1, sticky=tk.NSEW)
        self.add_inf_cbx.grid(row=8, column=1, sticky=tk.NSEW)
        self.dummy_button.grid(row=7, column=13, sticky=tk.NSEW)
        self.force_yes_inf_checker_cbx.grid(row=7, column=12, sticky=tk.W)
        self.lr_legend.grid(row=8, column=9, sticky=tk.NSEW)
        self.btn_all_files.grid(row=8, column=3, sticky=tk.NSEW)
        self.lr_think_time.grid(row=8, column=13, sticky=tk.NSEW)
        self.lr_report_B.grid(row=8, column=4, sticky=tk.NSEW)
        self.lr_report_A.grid(row=7, column=4, sticky=tk.NSEW)
        self.transaction_rename.grid(row=7, column=5, sticky=tk.NSEW, rowspan=2)
        return
