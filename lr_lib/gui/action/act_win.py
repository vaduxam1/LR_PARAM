# -*- coding: UTF-8 -*-
# grid виджетов action.с окна

import os
import time
import contextlib
import configparser

import tkinter as tk

from tkinter import messagebox

import lr_lib.gui.action.act_other as lr_act_other
import lr_lib.gui.widj.legend as lr_legend
import lr_lib.gui.widj.dialog as lr_dialog
import lr_lib.gui.etc.group_param as lr_group_param
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.core.action.main_awal as lr_main_awal
import lr_lib.core.etc.other as lr_other
import lr_lib.core.etc.lbrb_checker as lr_lbrb_checker
import lr_lib.etc.template as lr_template


class ActToplevel(tk.Toplevel):
    def __init__(self, id_: int):
        tk.Toplevel.__init__(self, padx=0, pady=0)
        self.id_ = id_
        lr_vars.Window.action_windows[self.id_] = self  # !

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.geometry('{}x{}'.format(*lr_vars._Tk_ActionWIND_SIZE))

        # bars
        self.toolbar = tk.LabelFrame(self, relief='ridge', bd=5, labelanchor=tk.N, font=lr_vars.DefaultFont + ' italic',
                                     text='для корректной работы, раскладку клавиатуры установить в ENG')
        self.middle_bar = tk.LabelFrame(self, relief='ridge', bd=2, text='', labelanchor=tk.S, font=lr_vars.DefaultFont)
        self.transaction_bar = tk.LabelFrame(self.middle_bar, relief='groove', bd=0, text='transaction',
                                             labelanchor=tk.S, font=lr_vars.DefaultFont)
        self.inf_bar = tk.LabelFrame(self.middle_bar, relief='groove', bd=0, text='inf', labelanchor=tk.S,
                                     font=lr_vars.DefaultFont)
        self.wrsp_bar = tk.LabelFrame(self.middle_bar, relief='groove', bd=0, text='web_reg_save_param',
                                      labelanchor=tk.S, font=lr_vars.DefaultFont)
        self.font_toolbar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.S,
                                          font=lr_vars.DefaultFont)
        self.file_bar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.N)
        self.cbx_bar = tk.LabelFrame(self.toolbar, relief='groove', bd=0, text='', labelanchor=tk.S)

    def on_closing(self) -> None:
        '''спросить, при закрытии окна'''
        if messagebox.askokcancel("Закрыть action.c", "Закрыть action.c ?", parent=self):
            self.destroy()

    def destroy(self):
        '''выход'''
        with contextlib.suppress(AttributeError):
            self.backup()
        with contextlib.suppress(KeyError):
            del lr_vars.Window.action_windows[self.id_]

        return super().destroy()


class ActVar:
    def __init__(self):
        self.font_var = tk.StringVar(value=lr_vars.DefaultActionHighlightFont)
        self.background_var = tk.StringVar(value=lr_vars.Background)
        self.size_var = tk.IntVar(value=lr_vars.DefaultActionHighlightFontSize)
        self.SearchReplace_searchVar = tk.StringVar(value='')
        self.SearchReplace_replaceVar = tk.StringVar(value='')
        self.final_wnd_var = tk.BooleanVar(value=lr_vars.DefaultActionFinalWind)
        self.force_ask_var = tk.BooleanVar(value=lr_vars.DefaultActionForceAsk)
        self.no_var = tk.BooleanVar(value=lr_vars.DefaultActionNoVar)
        self.max_inf_cbx_var = tk.BooleanVar(value=lr_vars.DefaultActionMaxSnapshot)
        self.add_inf_cbx_var = tk.BooleanVar(value=lr_vars.DefaultActionAddSnapshot)
        self.force_yes_inf = tk.BooleanVar(value=lr_vars.DefaultActionForceYes)

        self.weight_var = tk.BooleanVar(value=lr_vars.DefaultActionHighlightFontBold)
        self.underline_var = tk.BooleanVar(value=lr_vars.DefaultActionHighlightFontUnderline)
        self.slant_var = tk.BooleanVar(value=lr_vars.DefaultHighlightActionFontSlant)
        self.overstrike_var = tk.BooleanVar(value=lr_vars.DefaultHighlightActionFontOverstrike)


class ActWin(ActToplevel,
             ActVar,
             lr_act_other.ActScrollText,
             lr_act_other.ActBackup,
             lr_act_other.ActSearch,
             lr_act_other.ActBlock):

    def __init__(self):
        self.web_action = lr_main_awal.ActionWebsAndLines(self)
        self.action_file = None

        self.usr_file = '{}.usr'.format(os.path.basename(os.path.dirname(lr_vars.VarFilesFolder.get())))
        self.usr_config = self.get_usr_file()

        self.transaction = []  # имена action transaction
        self._search_index = -1

        self.action_infs = []  # номера inf в action
        self.drop_infs = set()  # отсутствующие номера inf в action
        self.drop_files = []  # файлы из отсутствующих inf

        ActToplevel.__init__(self, id(self))
        ActVar.__init__(self)
        lr_act_other.ActScrollText.__init__(self)
        lr_act_other.ActBackup.__init__(self, self.tk_text, self.file_bar, self.id_)
        lr_act_other.ActSearch.__init__(self, self.tk_text, self.toolbar, self.update)
        lr_act_other.ActBlock.__init__(self, self.tk_text, self.update)

        self.open_action()  # action текст

    def legend(self) -> None:
        '''окно легенды'''
        t = lr_legend.WebLegend(self)
        t.add_web_canavs()
        t.print()

    def max_inf_set(self, *args) -> None:
        '''max_inf_cbx_var вкл/выкл'''
        if self.max_inf_cbx_var.get():
            self.add_inf_cbx.configure(state='normal')
        else:
            self.add_inf_cbx.configure(state='disabled')

    @lr_vars.T_POOL_decorator
    def all_transaction_rename(self, *args) -> None:
        '''переименавать все транзакции'''
        _transactions = [t.split('"', 1)[1] for t in self.transaction]
        transactions = list(sorted(set(_transactions), key=_transactions.index))
        mx = max(map(len, transactions or ['']))
        m = '"{:<%s}" -> "{}"' % mx
        all_transaction = '\n'.join(m.format(old, new) for old, new in zip(transactions, transactions))
        y = lr_dialog.YesNoCancel(['Переименовать', 'Отмена'], 'Переименовать transaction слева',
                                  'в transaction справа', 'transaction',
                                  parent=self, is_text=all_transaction)
        st = 'lr_start_transaction("'
        en = 'lr_end_transaction("'
        if y.ask() == 'Переименовать':
            new_transaction = [t.split('-> "', 1)[1].split('"', 1)[0].strip() for t in y.text.strip().split('\n')]
            assert len(transactions) == len(new_transaction)
            text = self.tk_text.get('1.0', tk.END)
            for old, new in zip(transactions, new_transaction):
                text = text.replace((st + old), (st + new))
                text = text.replace((en + old), (en + new))

            with self.block():
                self.backup()
                self.web_action.set_text_list(text, websReport=True)
                self.web_action_to_tk_text(websReport=False)

    @lr_vars.T_POOL_decorator
    def _replace_button_set(self, *args) -> None:
        '''кнопка замены(обычной как в блокноте) текста'''
        if messagebox.askyesno(str(self), "action.c: Заменить ? :\n\n{s}\n\n на :\n\n{r}".format(
                s=self.SearchReplace_searchVar.get(), r=self.SearchReplace_replaceVar.get()), parent=self):
            with self.block():
                self.backup()
                text = self.tk_text.get(1.0, tk.END)
                text = text.replace(self.SearchReplace_searchVar.get(), self.SearchReplace_replaceVar.get())
                self.web_action.set_text_list(text, websReport=True)
                self.web_action_to_tk_text(websReport=False)

    def thinktime_remove(self, *args) -> None:
        '''удалить thinktime'''
        text = self.tk_text.get(1.0, tk.END)
        counter = 0

        def no_tt_lines() -> iter((str,)):
            nonlocal counter
            for line in text.split('\n'):
                if line.strip().startswith('lr_think_time'):
                    counter += 1
                else:
                    yield line

        new_text = '\n'.join(no_tt_lines())
        if messagebox.askokcancel('thinktime', 'удалить thinktime из action?\n{} шт.'.format(counter), parent=self):
            with self.block():
                self.backup()
                self.web_action.set_text_list(new_text, websReport=True)
                self.web_action_to_tk_text(websReport=False)

    @lr_vars.T_POOL_decorator
    def dummy_btn_cmd(self, *a) -> None:
        '''удалить dummy из action'''
        self.set_template_list(force=True)

    def set_template_list(self, force=True) -> None:
        '''очистить Text для WebDummyTemplate_List'''
        lr_template.Dummy.setattrs(lr_template.WebDummyTemplate_Part_Endswith)
        ok = self.tk_text_dummy_remove(force=force, mode='endswith')

        for template in lr_template.WebDummyTemplate_List:
            lr_template.Dummy.setattrs(template)
            if ok:
                ok = self.tk_text_dummy_remove(force=False)

        del_all = yask = is_del = False
        for web in self.web_action.get_web_snapshot_all():
            if web.snapshot in self.web_action.websReport.google_webs:
                if not del_all:
                    gws = str(self.web_action.websReport.google_webs)[:50]
                    wt = ''.join(web.to_str())
                    sn = '"Snapshot=t{}.inf"'.format(web.snapshot)
                    yask = lr_dialog.YesNoCancel(
                        ['Удалить текущий', "Удалить все Snapshot's {}".format(gws), 'Пропустить', 'Выход'],
                        "удалить {sn} содержащий {d}".format(d={k: wt.count(k) for k in lr_vars.DENY_WEB_}, sn=sn),
                        'всего можно удалить {} шт'.format(len(self.web_action.websReport.google_webs)),
                        parent=self, is_text=wt, title='{i} | {sn}'.format(i=self.id_, sn=sn)).ask()
                    del_all = yask.startswith('Удалить все')
                if del_all or yask.startswith('Удалить'):
                    self.web_action.webs_and_lines.remove(web)
                    is_del = True
                elif yask == 'Выход':
                    break
        if is_del:
            self.web_action_to_tk_text(websReport=True)

    def save_action_file(self, file_name=None, websReport=True) -> None:
        '''текст to WEB_ACTION - сохранить текст action.c окна'''
        with self.block():
            self.web_action.set_text_list(self.tk_text.get(1.0, tk.END), websReport=websReport)
            self.web_action_to_tk_text(websReport=False)

        if file_name is None:
            file_name = tk.filedialog.asksaveasfilename(
                initialdir=os.getcwd(), filetypes=(("action.c", "*.c"), ("all", "*.*")),
                title='сохранить текст action.c окна', parent=self)

        if file_name:
            with open(file_name, 'w', errors='replace', encoding=lr_vars.VarEncode.get()) as act:
                act.write(self.tk_text.get(1.0, tk.END))
        else:
            self.backup()

    def web_action_to_tk_text(self, websReport=False) -> None:
        '''WEB_ACTION to tk_text'''
        new_text = self.web_action.to_str(websReport=websReport)
        self.tk_text.new_text_set(new_text)
        self.tk_text.set_highlight()
        self.widj_reset()

    @lr_vars.T_POOL_decorator
    def open_action(self, file=None) -> None:
        '''сформировать action.c'''
        with self.block(), lr_vars.Window.block():
            self.action_file = file or lr_act_other.get_action_file()

            if os.path.isfile(self.action_file):
                with open(self.action_file, errors='replace', encoding=lr_vars.VarEncode.get()) as iter_lines:
                    self.web_action.set_text_list(iter_lines, websReport=True)
                    self.web_action_to_tk_text(websReport=False)
                    self._open_action_final()

    def _open_action_final(self) -> None:
        '''сообщения и действия, после открытия нового файла'''
        if not self.action_file:
            return
        self.tk_text.reset_highlight(highlight=False)

        info = []
        t = time.strftime('%H:%M:%S %m.%d.%y', time.gmtime(os.path.getmtime(self.action_file)))
        info.append('{f} : size={sa}, id={s}, create={t}'.format(
            f=self.action_file, s=self.id_, sa=os.path.getsize(self.action_file), t=t))

        if self.web_action.websReport.rus_webs:
            info.append('В следующих номерах inf, обнаружены Русские(NoASCII) символы, возможно требуется '
                        'перекодировка(выделение/encoding из меню мыши)\n{}'.format(
                self.web_action.websReport.rus_webs))

        if self.web_action.websReport.google_webs:
            info.append('Возможно следующие номера inf лишние, тк содержат слова {s}\nих можно удалить('
                        '+"commit/backup/обновить action.c" из меню мыши)\n{w}'.format(
                w=self.web_action.websReport.google_webs, s=lr_vars.DENY_WEB_))

        if info:
            lr_vars.Logger.info('\n\n'.join(info))

        self.background_color_set(color='')  # оригинальный цвет
        lr_vars.Window.focus_set()  # почемуто без этого не проходит self.focus_set()
        self.focus_set()

    def get_transaction(self, text: str) -> iter((str,)):
        '''имена транзакций'''
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('lr_') and line.endswith(');') and '_transaction("' in line:
                t_name = line.rsplit('"', 1)[0]
                yield t_name[3:]

    def group_param_search_quotes(self, r=r'=(.+?)\"') -> iter((str,)):
        '''поиск param, внутри кавычек'''

        def get_params() -> iter((str,)):
            for web_ in self.web_action.get_web_snapshot_all():
                params = re.findall(r, web_.get_body())
                yield from filter(bool, map(str.strip, params))

        for param in get_params():
            if all(map(lr_param.wrsp_allow_symb.__contains__, param)):  # не содержит неподходящих символов
                yield param

    @lr_vars.T_POOL_decorator
    def auto_param_creator(self, *a) -> None:
        '''group params по кнопке PARAM'''
        y = lr_dialog.YesNoCancel(['Найти', 'Отменить'], is_text='\n'.join(lr_vars.Params_names), parent=self,
                                  text_before='Будет произведен поиск param, имя которых начинается на указанные имена.',
                                  title='начало param-имен', text_after='При необходимости - добавить/удалить')
        ans = y.ask()
        if ans == 'Найти':
            param_parts = list(filter(bool, map(str.strip, y.text.split('\n'))))

            params = [self.session_params()]  # поиск по LB=
            params.extend(map(self.group_param_search, param_parts))  # поиск по началу имени

            params = set(p for ps in params for p in ps)
            params = [p for p in params if ((p not in lr_vars.DENY_PARAMS) and (
                not (len(p) > 2 and p.startswith('on') and p[2].isupper())))]
            params.sort(key=lambda param: len(param), reverse=True)

            y = lr_dialog.YesNoCancel(['Создать', 'Отменить'], is_text='\n'.join(params), parent=self,
                                      text_before='создание + автозамена. %s шт' % len(params), title='Имена param',
                                      text_after='При необходимости - добавить/удалить')
            ans = y.ask()
            if ans == 'Создать':
                params = list(filter(bool, map(str.strip, y.text.split('\n'))))
                lr_group_param.group_param(None, widget=self.tk_text, params=params, ask=False)

    @lr_vars.T_POOL_decorator
    def re_auto_param_creator(self, *a) -> None:
        '''group params поиск, на основе регулярных выражений'''
        y = lr_dialog.YesNoCancel(['Найти', 'Отменить'], is_text='\n'.join(lr_vars.REGEXP_PARAMS), parent=self,
                                  text_before='Будет произведен поиск param: re.findall(regexp, action_text)',
                                  title='regexp {} шт.'.format(len(lr_vars.REGEXP_PARAMS)),
                                  text_after='При необходимости - добавить/удалить')
        ans = y.ask()
        if ans == 'Найти':
            regexps = list(filter(bool, map(str.strip, y.text.split('\n'))))
        else:
            return

        def deny_params(lst: list) -> [str, ]:
            '''удалить не param-слова'''
            for p in lst:
                check = ((p not in lr_vars.DENY_PARAMS) and (
                    not (len(p) > 2 and p.startswith('on') and p[2].isupper()))) and (len(p) > 2)
                if check:
                    for a in lr_vars.DENY_Startswitch_PARAMS:
                        if p.startswith(a):
                            check = not all(map(str.isnumeric, (p.split(a, 1)[1])))
                            break
                    if check:
                        yield p

        params = []
        for r in regexps:
            prs = list(set(self.group_param_search_quotes(r=r)))
            prs = list(deny_params(prs))
            params.extend(prs)

        params = list(set(params))
        if params:
            params.sort(key=lambda param: len(param), reverse=True)
            y = lr_dialog.YesNoCancel(['создать', 'Отменить'], is_text='\n'.join(params), parent=self,
                                      text_before='Будет произведено создание param',
                                      title='param {} шт.'.format(len(params)),
                                      text_after='При необходимости - добавить/удалить')
            ans = y.ask()
            if ans == 'создать':
                params = list(filter(bool, map(str.strip, y.text.split('\n'))))
                lr_group_param.group_param(None, widget=self.tk_text, params=params, ask=False)

    def param_counter(self, all_param_info=False) -> str:
        '''подсчитать кол-во созданных web_reg_save_param'''
        self.wrsp_combo_set()
        self.param_combo_set()

        if all_param_info:
            lr_vars.Logger.debug(self.web_action.websReport.web_snapshot_param_in_count)
        return 'всего web_reg_save_param : {w}'.format(w=len(self.web_action.websReport.wrsp_and_param_names))

    def param_inf_checker(self, wrsp_dict: dict, wrsp: str) -> None:
        '''inf-номер запроса <= inf-номер web_reg_save_param'''
        if not wrsp_dict:
            return

        max_action_inf = wrsp_dict['param_max_action_inf']
        if lr_vars.VarIsSnapshotFiles.get():
            try:
                if not max_action_inf:
                    raise UserWarning('Перед param, не найдено никаких блоков c inf запросами.')
                elif max_action_inf <= min(wrsp_dict['inf_nums']):
                    inf_nums = wrsp_dict['inf_nums'] or [-2]
                    raise UserWarning('Snapshot=t{p}.inf, в котором расположен,\nпервый заменяемый {_p}\n\n'
                                      'не может быть меньше или равен,\nSnapshot=t{w}.inf, перед которым вставляется\n'
                                      'web_reg_save_param запрос\n\n{p} <= {inf_nums}'.format(
                        _p='{%s}' % wrsp_dict['param'], p=max_action_inf, w=inf_nums[0], inf_nums=inf_nums))
            except Exception as ex:
                self.search_in_action(word=lr_param.Snap.format(num=max_action_inf), hist=False)
                qb = 'param: "{p}"\nweb_reg_save_param: {n}'.format(p=wrsp_dict['param'],
                                                                    n='{%s}' % wrsp_dict['web_reg_name'])

                if self.force_yes_inf.get():
                    lr_vars.Logger.warning('{q}\n\n{e}\n{wrsp}'.format(e=ex, q=qb, wrsp=wrsp))
                else:
                    y = lr_dialog.YesNoCancel(buttons=['Создать', 'Пропустить'], text_after=qb, text_before=str(ex),
                                              title='создать web_reg_save_param ?', parent=self).ask()
                    if y == 'Пропустить':
                        raise
                    else:
                        lr_vars.Logger.info('{q}\n\n{e}'.format(e=ex, q=qb))

    def SearchAndReplace(self, search: str, replace='', wrsp_dict=None, wrsp=None, backup=False, is_wrsp=True,
                         replace_callback=None, rep_stat=False) -> None:
        with self.block():
            self._SearchAndReplace(search, replace, wrsp_dict, wrsp, backup, is_wrsp, replace_callback, rep_stat)

    def _SearchAndReplace(self, search: str, replace='', wrsp_dict=None, wrsp=None, backup=False, is_wrsp=True,
                          replace_callback=None, rep_stat=False) -> None:
        '''VarWrspDict автозамена: [заменить param на {web_reg_save_param}] + [добавить блок с // web_reg_save_param, перед блоком c inf_line]'''
        assert search, 'пустой search "{s}" {ts}'.format(s=search, ts=type(search))

        if is_wrsp:
            if not wrsp_dict:  # текущий
                wrsp_dict = lr_vars.VarWrspDict.get()
            if not wrsp:
                wrsp = lr_param.create_web_reg_save_param(wrsp_dict)

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
                    stats[web_.snapshot] = res
            if rep_stat:
                lr_vars.Logger.debug(search + ':\n' + '\n'.join('{} inf: заменено [да|нет] раз: [{}|{}]'.format(
                    k, *stats[k]) for k in sorted(stats)))
        else:  # "быстрая" замена
            self.web_action.replace_bodys([(search, replace), ])

        if is_wrsp:  # вставить web_reg_save_param
            self.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)

        if not replace_callback:
            self.web_action_to_tk_text(websReport=True)

    def drop_file_none_inf_num_in_action(self) -> None:
        '''в LoadRunner могут быть inf-файлы, которых нету в action.c(например удалили лишний код), такие файлы надо отсеять, тк web_reg_save_param потом может на него сослатся'''
        self.action_infs[:] = [a.snapshot for a in self.web_action.get_web_snapshot_all()]
        self.drop_infs.clear()
        self.drop_files.clear()

        for file in lr_vars.AllFiles:
            check = False
            for inf in file['Snapshot']['Nums']:
                if inf in self.action_infs:
                    check = True
                else:
                    self.drop_infs.add(inf)
            if not check:
                self.drop_files.append(file['File']['Name'])

        self.show_info()

    def show_info(self) -> None:
        '''всякая инфа'''
        ldaf = len(lr_vars.AllFiles)
        lif = len(list(lr_other.get_files_infs(lr_vars.AllFiles)))
        lf = len([f for f in lr_vars.AllFiles if any(i in self.action_infs for i in f['Snapshot']['Nums'])])
        li = len(self.action_infs)
        alw = len(tuple(self.web_action.get_web_all()))

        lr_vars.Window.last_frame['text'] = '{d} > в {i} inf > {f} файлов'.format(
            d=lr_vars.VarFilesFolder.get(), f=len(lr_vars.AllFiles),
            i=len(list(lr_other.get_files_infs(lr_vars.AllFiles))))

        self.middle_bar[
            'text'] = 'В action.c web_*: объектов[любых={alw} шт, snapshot={i} шт], файлов ответов[{f} шт] / ' \
                      'Удалено: объектов[snapshot={ni} шт] -> файлов ответов[{nf} шт]'.format(
            alw=alw, i=li, f=lf, ni=lif - li, nf=ldaf - lf)

        if self.drop_infs or self.drop_files:
            lr_vars.Logger.debug('Отсутствует в action.c: inf: {il}, файлов : {fl} | Найдено: {ai} inf'.format(
                il=len(self.drop_infs), fl=len(self.drop_files), ai=li), parent=self)

    def session_params(self, lb_list=None, ask=True) -> list:
        '''поиск param в action, по LB='''
        if lb_list is None:
            lb_list = lr_vars.LB_PARAM_FIND_LIST

        if ask:
            text = self.tk_text.get(1.0, tk.END)
            lb_uuid = re.findall(r'uuid_\d=', text)
            lb_col_count = re.findall(r'p_p_col_count=\d&', text)

            text = '\n'.join(set(lb_list + lb_uuid + lb_col_count))
            y = lr_dialog.YesNoCancel(buttons=['Найти', 'Пропуск'], text_before='найти param по LB=',
                                      text_after='указать LB, с новой строки', is_text=text,
                                      title='автозамена по LB=',
                                      parent=self, default_key='Найти')
            if y.ask() == 'Найти':
                lb_list = y.text.split('\n')
            else:
                return []

        params = []
        for p in filter(bool, lb_list):
            params.extend(self._group_param_search(p, part_mode=False))
        return list(reversed(sorted(p for p in set(params) if p not in lr_vars.DENY_PARAMS)))

    def group_param_search(self, param_part: "zkau_") -> ["zkau_5650", "zkau_5680", ]:
        '''поиск в action.c, всех уникальных param, в имени которых есть param_part'''
        params = list(set(self._group_param_search(param_part)))  # уникальных
        params.sort(key=lambda param: len(param), reverse=True)
        return params

    def _group_param_search(self, param_part: "zkau_", part_mode=True) -> iter(("zkau_5650", "zkau_5680",)):
        '''поиск в action.c, всех param, в имени которых есть param_part / или по LB'''
        for web_ in self.web_action.get_web_snapshot_all():
            split_text = web_.get_body().split(param_part)

            for index in range(len(split_text) - 1):
                left = split_text[index].rsplit('\n', 1)[-1].lstrip()
                right = split_text[index + 1].split('\n', 1)[0].rstrip()

                if lr_lbrb_checker.check_bound_lb(left) if part_mode else (right[0] in lr_param.wrsp_allow_symb):
                    param = []  # "5680"

                    for s in right:
                        if s in lr_param.wrsp_allow_symb:
                            param.append(s)
                        else:
                            break

                    if param:
                        param = ''.join(param)
                        if part_mode:  # param_part или по LB
                            param = param_part + param
                        yield param  # "zkau_5680"

    def tk_text_dummy_remove(self, force=False, mode='') -> bool:
        '''удалить все dummy web_submit_data'''
        text = self.tk_text.get(1.0, tk.END).strip()
        _web_action = lr_main_awal.ActionWebsAndLines(self)
        _web_action.set_text_list(text)

        if mode == 'endswith':
            is_remove = lr_template.dummy_endswith_remove
        else:
            is_remove = lr_template.dummy_remove

        rem = 0
        for web_ in tuple(_web_action.get_web_all()):
            if is_remove(web_.lines_list):
                _web_action.webs_and_lines.remove(web_)
                rem += 1

        text_without_dummy = _web_action.to_str(websReport=True)
        dum_len = len(text)
        no_dum_len = len(text_without_dummy)

        if force or (dum_len != no_dum_len):
            text_t = tuple(self.web_action.get_web_all())
            text_w = tuple(_web_action.get_web_all())
            t1 = len(tuple(self.web_action.get_web_snapshot_all()))
            t2 = len(tuple(_web_action.get_web_snapshot_all()))
            ltn = len(text.split('\n')) - 1
            ldn = len(text_without_dummy.split('\n')) - 1
            if mode:
                _type = mode
                lwnt = len(text_t)
                lwnd = len(text_w)
            else:
                _type = lr_template.Dummy.web_dummy_template.split('("', 1)[0].strip()
                lwnt = len(tuple(w for w in text_t if w.type == _type))
                lwnd = len(tuple(w for w in text_w if w.type == _type))
            cd = max((t1 - t2, lwnt - lwnd))
            buttons = ['Удалить/Пересканировать', 'Пропустить', 'Выход']
            n1, n2, n3, n4 = '{}|Snapshot|строк|символов'.format(_type).split('|')

            ync = lr_dialog.YesNoCancel(
                buttons=buttons, text_before='Удалить {cd} шт. "dummy" - {web_name} из action.c текста?\n'
                                             'Если изменить web_dummy_template текст,\n'
                                             'action.c пересканируется, с повторным показом диалог окна.\n'
                                             'inf удаляется, если его строки, начинаются\n'
                                             'на соответствующие им строки, в web_dummy_template,\n'
                                             'без учета начальных пробелов.'.format(web_name=_type, cd=cd),
                text_after='action.c до и после удаления {web_name}:\n'
                           '{n1:>20} {n2:>20} {n3:>20} {n4:>20}\n'
                           '{lwnt:>20} | {t1:>20} | {ltn:>20} | {d:>20} |\n'
                           '{lwnd:>20} | {t2:>20} | {ldn:>20} | {nd:>20} |'.format(
                    n1=n1, n2=n2, n3=n3, n4=n4, lwnt=lwnt, lwnd=lwnd, d=dum_len, nd=no_dum_len, t1=t1, t2=t2,
                    ltn=ltn,
                    ldn=ldn, web_name=_type),
                title='web_dummy_template | удалить {rem} шт ?'.format(rem=rem),
                is_text=lr_template.Dummy.web_dummy_template, parent=self)

            y = ync.ask()
            if y == buttons[2]:
                return False

            template = ync.text.strip()
            if ((len(template) != lr_template.Dummy.web_len) or
                    (len(template.split('\n')) != lr_template.Dummy.dummy_len)):
                lr_template.Dummy.setattrs(template)
                return self.tk_text_dummy_remove()

            if y == buttons[0]:
                self.backup()
                self.tk_text.new_text_set(text_without_dummy)
                self.web_action = _web_action
                self.web_action_to_tk_text(websReport=True)

            if y in buttons[:2]:
                return True

    def get_usr_file(self) -> configparser.ConfigParser:
        '''result_folder = self.get_usr_file()['General']['LastResultDir']'''
        config = configparser.ConfigParser()
        config.read(os.path.join(os.getcwd(), self.usr_file))
        return config

    def get_result_folder(self, file='Results.xml') -> str:
        '''директория файлов ответов'''
        result_folder = self.usr_config['General']['LastResultDir']
        folder = os.path.join(os.getcwd(), result_folder)
        file = os.path.join(folder, file)
        with open(file) as f:
            text = f.read()
            text = text.rsplit('.inf]]></Path>', 1)
            text = text[0]
            text = text.rsplit('t', 1)
            rdir = text[0].rsplit('\\', 2)
            rdir = rdir[1]
            return os.path.join(folder, rdir)

            # snap = text[1]
            # last_snapshot = int(snap) - 1

        # max_snap = (max(self.action_infs) if self.action_infs else 0)
        # if last_snapshot < max_snap:
        #     self.inf_combo.set(last_snapshot)
        #     self.goto_inf()
        #     lr_vars.Logger.info('При воспроизведении({r})\nне все Snapshot были выполненны: last:{l} < max:{m}'.format(
        #         r=os.path.join(folder, rdir), l=last_snapshot, m=max_snap))
        #
        # a = lr_param.get_search_data('None')
        # a = next(lr_param.create_files_with_search_data(lr_vars.AllFiles, a, action_infs=[last_snapshot]))
        # with open(os.path.join(folder, rdir, a['File']['Name'])) as f:
        #     print(f.read())
        # y = lr_dialog.YesNoCancel(
        #     ['Переименовать', 'Отмена'], 'Переименовать', 'transactio', 'qwe',
        #     parent=self, is_text='wqw', combo_dict={})
