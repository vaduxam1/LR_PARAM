# -*- coding: UTF-8 -*-
# action.с окно - родитель lr_lib.gui.action.main_action.ActionWindow

import os
import tkinter as tk

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.etc.vars_other
import lr_lib.core_gui.action_lib
import lr_lib.core_gui.group_param.core_gp
import lr_lib.core_gui.group_param.gp_act_re
import lr_lib.core_gui.run.run_setting
import lr_lib.gui.action.act_any
import lr_lib.gui.etc.gui_other
import lr_lib.gui.etc.sub_menu
import lr_lib.gui.widj.dialog
import lr_lib.gui.widj.legend
import lr_lib.gui.widj.wrsp_setting
import lr_lib.gui.wrsp.top.top_allfiles


class ActWin(lr_lib.gui.action.act_any.ActAny):
    """
    родитель lr_lib.gui.action.main_action.ActionWindow
        main_action.ActionWindow
      + act_win.ActWin
        act_any.ActAny
        act_goto.ActGoto
        act_font.ActFont
        act_replace.ActReplaceRemove
        act_search.ActSearch
        act_serializ.TkTextWebSerialization
        act_backup.ActBackup
        act_block.ActBlock
        act_scroll.ActScrollText
        act_widj.ActWidj
        act_var.ActVar
        act_toplevel.ActToplevel
        tk.Toplevel
    """

    def __init__(self):
        lr_lib.gui.action.act_any.ActAny.__init__(self)

        # Button
        cmd1 = lambda: lr_lib.core.etc.other.openTextInEditor(self.tk_text.get(1.0, tk.END))
        self.editor_button = tk.Button(
            self.file_bar, text='editor', font=(lr_vars.DefaultFont + ' bold'),
            command=cmd1,
        )

        # Button
        cmd2 = lambda: lr_lib.core_gui.run.run_setting.RunSettingWindow(self)
        self.auto_param_creator_button = tk.Button(
            self.toolbar, text='Найти и Создать\nparam WRSP', background='orange', font=(lr_vars.DefaultFont + ' bold'),
            command=cmd2,
        )

        # Checkbutton
        self.final_wnd_cbx = tk.Checkbutton(
            self.toolbar, text='final', font=lr_vars.DefaultFont, variable=self.final_wnd_var,
        )

        # Button
        cmd3 = lambda *a: lr_lib.gui.widj.wrsp_setting.WrspSettingWindow(parent=self)
        self.wrsp_setting = tk.Button(
            self.toolbar, text='wrsp_setting', font=(lr_vars.DefaultFont + ' bold'), command=cmd3,
        )

        # Button
        cmd4 = lambda *a: lr_lib.core_gui.action_lib.snapshot_files(self.tk_text, i_num=1)
        self.resp_btn = tk.Button(
            self.toolbar, text='файлы ответов', font=lr_vars.DefaultFont, command=cmd4,
        )

        # Checkbutton
        self.force_ask_cbx = tk.Checkbutton(
            self.toolbar, text='Ask', font=lr_vars.DefaultFont, variable=self.force_ask_var, command=self.force_ask_cmd,
        )

        # Checkbutton
        self.no_cbx = tk.Checkbutton(
            self.toolbar, text='NoAsk', font=lr_vars.DefaultFont, variable=self.no_var, command=self.no_var_cmd,
        )

        # Checkbutton
        self.max_inf_cbx = tk.Checkbutton(
            self.toolbar, text='ограничить max inf', font=(lr_vars.DefaultFont + ' bold'),
            variable=self.max_inf_cbx_var, command=self.max_inf_set,
        )

        # Checkbutton
        self.add_inf_cbx = tk.Checkbutton(
            self.toolbar, anchor=tk.E, text='max inf mode', font=lr_vars.DefaultFont, variable=self.add_inf_cbx_var,
        )

        # Checkbutton
        self.force_yes_inf_checker_cbx = tk.Checkbutton(
            self.toolbar, text='fYes', font=lr_vars.DefaultFont, variable=self.force_yes_inf,
        )

        # Button
        cmd5 = lambda *a: lr_lib.gui.etc.gui_other.repB(self.tk_text)
        self.lr_report_B = tk.Button(
            self.toolbar, text='reportB', font=lr_vars.DefaultFont, command=cmd5,
        )

        # Button
        def cmd6(*a) -> None:
            """report_A"""
            lr_lib.gui.etc.gui_other.repA(self.tk_text)
            return
        self.lr_report_A = tk.Button(
            self.toolbar, text='reportA', font=lr_vars.DefaultFont, command=cmd6,
        )

        # Button
        self.lr_legend = tk.Button(
            self.toolbar, text='web_legend', font=lr_vars.DefaultFont, command=self.legend,
        )

        # Button
        cmd7 = lambda *a: lr_lib.gui.wrsp.top.top_allfiles.TopFolder(self)
        self.btn_all_files = tk.Button(
            self.toolbar, text='все файлы', font=lr_vars.DefaultFont, command=cmd7,
        )

        # запускать в конце
        self.post_init()
        return

    def post_init(self) -> None:
        """
        выполнять после создания всех виджетов
        """
        widjs = (self.search_res_combo, self.SearchReplace_searchCombo, self.SearchReplace_replaceCombo,
                 self.search_entry,)
        for w in widjs:
            try:  # виджетам доступно меню мыши
                self.bind_class(w, sequence='<Button-3>', func=lr_lib.gui.etc.sub_menu.rClicker, add='')
            except Exception as ex:
                pass
            continue

        self.widj_reset()
        return

    def open_action(self, **kwargs) -> None:
        """
        сформировать action.c
        """
        super().open_action(callback=self._open_action_final, **kwargs)
        return

    def param_inf_checker(self, wrsp_dict: dict, wrsp: str) -> None:
        """
        inf-номер запроса <= inf-номер web_reg_save_param
        """
        if not wrsp_dict:
            return

        max_action_inf = wrsp_dict['param_max_action_inf']
        if lr_vars.VarIsSnapshotFiles.get():
            try:
                if not max_action_inf:
                    raise UserWarning('Перед param, не найдено никаких блоков c inf запросами.')
                elif max_action_inf <= min(wrsp_dict['inf_nums']):
                    infs = (wrsp_dict['inf_nums'] or [-2])
                    e = ERR2.format(prm=wrsp_dict['param'], p=max_action_inf, w=infs[0], inf_nums=infs, )
                    raise UserWarning(e)
            except Exception as ex:
                w = lr_lib.core.wrsp.param.Snap.format(num=max_action_inf)
                self.search_in_action(word=w, hist=False)
                i = 'param: "{p}"\nweb_reg_save_param: "{n}"'
                qb = i.format(p=wrsp_dict['param'], n=('{%s}' % wrsp_dict['web_reg_name']), )

                if self.force_yes_inf.get():
                    lr_vars.Logger.warning('{q}\n\n{e}{wrsp}'.format(e=ex, q=qb, wrsp=wrsp))
                else:
                    yc = lr_lib.gui.widj.dialog.YesNoCancel(
                        buttons=['Создать', 'Пропустить'],
                        text_after=qb,
                        text_before=str(ex),
                        title='создать web_reg_save_param ?',
                        parent=self,
                    )
                    y = yc.ask()
                    if y == 'Пропустить':
                        raise
                    else:
                        lr_vars.Logger.info('{q}\n\n{e}'.format(e=ex, q=qb))
        return

    def SearchAndReplace(
            self,
            search: str,
            replace='',
            wrsp_dict=None,
            wrsp=None,
            backup=False,
            is_wrsp=True,
            replace_callback=None,
            rep_stat=False,
    ) -> None:
        """
        VarWrspDict автозамена: [заменить param на {web_reg_save_param}]
            + [добавить блок с // web_reg_save_param, перед блоком c inf_line]
        """
        assert search, 'пустой search "{s}" {ts}'.format(s=search, ts=type(search))

        if is_wrsp:
            if not wrsp_dict:  # текущий
                wrsp_dict = lr_vars.VarWrspDict.get()
            if not wrsp:
                wrsp = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict)

        if not replace:
            replace = wrsp_dict['web_reg_name']

        self.param_inf_checker(wrsp_dict, wrsp)
        if backup:
            self.backup()

        # заменить
        if replace_callback:  # групповая замена
            replace_callback((search, replace))
        elif lr_vars.ReplaceParamDialogWindow:  # заменять с диалоговыми окнами, но без пула
            ask_dict = {}
            stats = {}

            for web_ in self.web_action.get_web_snapshot_all():
                res = web_.param_find_replace(search, replace, ask_dict)
                if rep_stat and any(res):
                    stats[web_.snapshot.inf] = res
                continue

            if rep_stat:
                s = '{} inf: заменено [да|нет] раз: [{}|{}]'
                i = (search + ':\n')
                i += '\n'.join(s.format(k, *stats[k]) for k in sorted(stats))
                lr_vars.Logger.debug(i)

        else:  # "быстрая" замена
            b = (search, replace)
            self.web_action.replace_bodys([b, ])

        if is_wrsp:  # вставить web_reg_save_param
            self.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)

        if not replace_callback:
            self.web_action_to_tk_text(websReport=True)
        return

    def get_result_folder(self, results_xml='Results.xml') -> str:
        """
        директория файлов ответов
        """
        result_folder = self.usr_config['General']['LastResultDir']
        folder = os.path.join(os.getcwd(), result_folder)
        results_xml = os.path.join(folder, results_xml)  # 'C:\\SCR\\LR_10\\LR_PARAM\\result1\\Results.xml'

        if not os.path.isfile(results_xml):
            lr_vars.Logger.error(ERR1)

        with open(results_xml) as f:
            text = f.read()

        text = text.rsplit('.inf]]></Path>', 1)
        text = text[0]
        text = text.rsplit('t', 1)
        rdir = text[0].rsplit('\\', 2)
        rdir = rdir[1]
        ps = os.path.join(folder, rdir)
        return ps

    def no_var_cmd(self, *args) -> None:
        """
        force_ask_var
        """
        if self.no_var.get():
            self.force_ask_var.set(0)
        return

    def force_ask_cmd(self, *args) -> None:
        """
        no_var
        """
        if self.force_ask_var.get():
            self.no_var.set(0)
        return

    def max_inf_set(self, *args) -> None:
        """
        max_inf_cbx_var вкл/выкл
        """
        if self.max_inf_cbx_var.get():
            self.add_inf_cbx.configure(state='normal')
        else:
            self.add_inf_cbx.configure(state='disabled')
        return

    def legend(self) -> None:
        """
        окно легенды
        """
        t = lr_lib.gui.widj.legend.WebLegend(self)
        t.add_web_canavs()
        t.print()
        return

    def _start_auto_update_action_info_lab(self) -> None:
        """
        автообновление self.scroll_lab2
        """
        lr_lib.gui.action._other.auto_update_action_info_lab(
            self=self,
            config=self.scroll_lab2.config,
            tk_text=self.tk_text,
            id_=self.id_,
            timeout=lr_vars.InfoLabelUpdateTime.get(),
            check_run=lr_vars.Window.action_windows.__contains__,
            title=self.title,
            _set_title=self._set_title,
        )
        return


ERR1 = '''
Не найдены LoadRunner файлы, ответов при воспроизведении, например "LR_scr\\result1\\Results.xml".
Для появления файлов ответов, необходимо хотябы один раз, запустить action.c скрипт в LoadRunner.
Путь директории последнего воспроизведения, берется из "LR_scr\\имя_скрипта.usr" LoadRunner файла.
'''.strip()

ERR2 = '''
Snapshot=t{p}.inf, в котором расположен,\nпервый заменяемый "{prm}"

не может быть({p} <= {inf_nums}) меньше или равен,

Snapshot=t{w}.inf, перед которым вставляется:
'''.strip()
