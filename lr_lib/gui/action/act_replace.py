# -*- coding: UTF-8 -*-
# action.с окно - замена и удаление текста

import tkinter as tk

from tkinter import messagebox

import lr_lib.gui.widj.dialog as lr_dialog
import lr_lib.gui.action.act_search as lr_act_search
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.action.main_awal as lr_main_awal
import lr_lib.etc.template as lr_template


class ActReplaceRemove(lr_act_search.ActSearch):
    """замена и удаление текста"""

    def __init__(self):
        lr_act_search.ActSearch.__init__(self)

        self.lr_think_time = tk.Button(
            self.toolbar, text='lr_think_time', font=lr_vars.DefaultFont + ' bold', command=self.thinktime_remove)

        self.transaction_rename = tk.Button(
            self.toolbar, text='rename\ntransaction', font=lr_vars.DefaultFont + ' bold', background='orange',
            command=self.all_transaction_rename)

        self.dummy_button = tk.Button(
            self.toolbar, text="Snapshot remove", font=lr_vars.DefaultFont + ' bold', background='orange',
            command=self.remove_web_dummy_template)

    @lr_vars.T_POOL_decorator
    def remove_web_dummy_template(self, *args, force=True) -> None:
        """для WebDummyTemplate_List - удалить все dummy web_"""
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
                        parent=self, is_text=wt, title=sn).ask()
                    del_all = yask.startswith('Удалить все')
                if del_all or yask.startswith('Удалить'):
                    self.web_action.webs_and_lines.remove(web)
                    is_del = True
                elif yask == 'Выход':
                    break
        if is_del:
            self.web_action_to_tk_text(websReport=True)

    def tk_text_dummy_remove(self, force=False, mode='') -> bool:
        with self.block():
            return self._tk_text_dummy_remove(force=force, mode=mode)

    def _tk_text_dummy_remove(self, force=False, mode='') -> bool:
        """удалить все dummy web_"""
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
            ltn = (len(text.split('\n')) - 1)
            ldn = (len(text_without_dummy.split('\n')) - 1)

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
                new_text = _web_action.to_str(websReport=False)
                self.backup()
                self.tk_text_to_web_action(text=new_text, websReport=True)

            if y in buttons[:2]:
                return True

    def thinktime_remove(self, *args, word='lr_think_time') -> None:
        """удалить thinktime"""
        text = self.tk_text.get(1.0, tk.END)
        assert text
        num = 0

        def filter_lines() -> iter((str,)):
            nonlocal num
            for line in text.split('\n'):
                if line.lstrip().startswith(word):
                    num += 1
                    continue
                else:
                    yield line

        lines = list(filter_lines())
        if lines:
            if messagebox.askokcancel('thinktime', 'удалить thinktime из action?\n{} шт.'.format(num), parent=self):
                self.backup()
                self.tk_text_to_web_action('\n'.join(lines), websReport=True)

    @lr_vars.T_POOL_decorator
    def all_transaction_rename(self, *args) -> None:
        """переименавать все транзакции"""
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

            self.backup()
            self.tk_text_to_web_action(text, websReport=True)

