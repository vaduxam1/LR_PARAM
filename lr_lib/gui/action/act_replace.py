# -*- coding: UTF-8 -*-
# action.с окно - замена и удаление текста

import tkinter as tk
from tkinter import messagebox

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_other
import lr_lib.core.var.vars_param
import lr_lib.etc.template
import lr_lib.gui.action.act_search
import lr_lib.gui.widj.dialog


WT0 = '''
web_submit_data("
    "Method=POST",
    "Snapshot=
    "Mode=HTML",
    ITEMDATA,
    "Name=cmd_0", "Value=dummy", ENDITEM,
    LAST);
'''  # пример шаблона web, для удаления

IsTextA = '''
Отображенный пример Template необходимо заменить своим. Сравнивает Template построчно со всеми web_ из action.c. Найденные web_ удаляются.
'''.strip()

IsTextB = '''
Template_Line считается эквивалентной ActionWeb_Line, если AW_Line начинается на T_Line: AW.startswith(T).
Для выбора web, содержаших различающиеся строки, например номер в "Snapshot=t5.inf", необходимо обрезать эту строку в Template так: "Snapshot=t
Порядок самих строк внутри Action.Web_ и Template может быть любым.

Выбрать в комбобоксе:
 1) Нестрогое соответствие: web_ содержит все отображенные линии, и любые другие.
 2) Строгое соответствие: web_ содержит только отображенные линии, т.е. кол-во линий web_ и Template должно совпадать.
'''.strip()


class ActReplaceRemove(lr_lib.gui.action.act_search.ActSearch):
    """
    замена и удаление текста
    """

    def __init__(self):
        lr_lib.gui.action.act_search.ActSearch.__init__(self)

        # Button
        self.lr_think_time = tk.Button(
            self.toolbar, text='lr_think_time', font=(lr_vars.DefaultFont + ' bold'), command=self.thinktime_remove,
        )

        # Button
        self.transaction_rename = tk.Button(
            self.toolbar, text='rename\ntransaction', font=(lr_vars.DefaultFont + ' bold'), background='orange',
            command=self.all_transaction_rename,
        )

        # Button
        self.dummy_button = tk.Button(
            self.toolbar, text="Snapshot remove", font=(lr_vars.DefaultFont + ' bold'), background='orange',
            command=self.remove_web_dummy_template,
        )
        return

    @lr_lib.core.var.vars_other.T_POOL_decorator
    def remove_web_dummy_template_new(self, template='', **kwargs) -> None:
        """
        удалить web_(например dummy или google) по пользовательскому шаблону - расширенный вариант.
        работает примерно как раньше, но можно искать даже по одной строке,
            например любые с этим адресом:
                "URL=http://ssl.elk.minfin.ru:8080/",
            или например любые с этим адресом и имеющие snapsot
                 "URL=http://ssl.elk.minfin.ru:8080/",
                 "Snapshot=
        """
        if not template:
            template = WT0

        template_dt = lambda: dict.fromkeys(map(str.strip, ync.text_get().strip().split('\n')))

        # -- func --
        def is_eq(web_find_mode: bool) -> str:
            """
            поиск и удаление web
            :param web_find_mode: bool: Нестрогий/Строгий поиск web_
            :return: str: вывод нового текста в диалог ync.tk_text - но тут это никак не используется, вернуть тот же
            """
            text = self.tk_text.get(1.0, tk.END).strip()
            _web_action = lr_lib.core.action.main_awal.ActionWebsAndLines(self)
            _web_action.set_text_list(text)

            al = tuple(_web_action.get_web_all())
            web_remove_count = 0
            wrsp_remove_count = 0

            for web_ in al:
                wls = web_.lines_list
                wls = tuple(map(str.strip, wls))
                tdt = template_dt()

                for wl in wls:
                    for tl in tdt:
                        if (not tdt[tl]) and wl.startswith(tl):
                            tdt[tl] = True
                            break
                        continue
                    continue

                need_delete = all(tdt.values())
                if need_delete and web_find_mode:
                    ln1 = len(web_.lines_list)
                    ln2 = len(tdt)
                    need_delete = (ln1 == ln2)

                if need_delete:  # delete
                    try:  # если у web есть wrsp, нужно удалить все эти wrsp, и все ссылки на них в остальных web
                        wrsp_list = web_.web_reg_save_param_list
                    except AttributeError:
                        pass  # не snapshot web
                    else:
                        for wr in wrsp_list:
                            _web_action.web_reg_save_param_remove(wr.name)  # удалить wrsp

                            wrsp_remove_count += 1
                            lr_vars.Logger.info('delete {} | {}'.format(wr.name, wr.param))
                            a = 'delete web:\n{p}\n{w}\n{p}\n name="{s}" | param="{n}"'
                            a = a.format(w=wr.to_str(), s=wr.name, n=wr.param, p=lr_vars.PRINT_SEPARATOR, )
                            lr_vars.Logger.info(a)
                            continue

                    # web
                    _web_action.webs_and_lines.remove(web_)  # удалить web

                    web_remove_count += 1
                    a = 'delete web:\n{p}\n{w}\n{p}\n snapshot={s} | num={n}'
                    a = a.format(w=web_.to_str(), s=web_.snapshot.inf, n=web_.snapshot.serial, p=lr_vars.PRINT_SEPARATOR, )
                    lr_vars.Logger.info(a)
                continue

            # сформировать новый action.c
            self.web_action_to_tk_text()

            r = 'web={w} шт., wrsp={r} шт.'.format(w=web_remove_count, r=wrsp_remove_count, )
            lr_vars.Logger.info(r)

            if messagebox.askokcancel(title='удаление web_', message='Удалить {} ?'.format(r), parent=ync, ):
                new_text = _web_action.to_str(websReport=False)
                self.backup()
                self.tk_text_to_web_action(text=new_text, websReport=True)

            t = ync.text_get().strip()  # для ync - вернуть тот же текст что и был
            return t
        # -- func --

        # удаление
        combo_dict = {
            '1) Нестрогое': lambda: is_eq(False),
            '2) Строгое': lambda: is_eq(True),
        }

        ync = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=['Выход', ],
            text_before=IsTextA,
            text_after=IsTextB,
            title='Template:',
            parent=self,
            is_text=template.strip(),
            combo_dict=combo_dict,
        )
        ync.ask()
        return

    @lr_lib.core.var.vars_other.T_POOL_decorator
    def remove_web_dummy_template(self, *args, force=True) -> None:
        """
        для WebDummyTemplate_List - удалить все dummy web_
        """
        lr_lib.etc.template.Dummy.setattrs(lr_lib.etc.template.WebDummyTemplate_Part_Endswith)
        ok = self.tk_text_dummy_remove(force=force, mode='endswith')

        for template in lr_lib.etc.template.WebDummyTemplate_List:
            lr_lib.etc.template.Dummy.setattrs(template)
            if ok:
                ok = self.tk_text_dummy_remove(force=False)
            continue

        del_all = yask = is_del = False
        al = self.web_action.get_web_snapshot_all()

        for web in al:
            gv = self.web_action.websReport.google_webs
            if web.snapshot.inf in gv:

                if not del_all:
                    gws = str(self.web_action.websReport.google_webs)[:50]
                    wt = ''.join(web.to_str())
                    dw = {k: wt.count(k) for k in lr_lib.core.var.vars_param.DENY_WEB_}
                    sn = '"Snapshot=t{}.inf"'.format(web.snapshot.inf)

                    y = lr_lib.gui.widj.dialog.YesNoCancel(
                        buttons=['Удалить текущий', "Удалить все Snapshot's {}".format(gws), 'Пропустить', 'Выход'],
                        text_before="удалить {sn} содержащий {d}".format(d=dw, sn=sn),
                        text_after='всего можно удалить {} шт'.format(len(self.web_action.websReport.google_webs)),
                        parent=self,
                        is_text=wt,
                        title=sn,
                    )

                    yask = y.ask()
                    del_all = yask.startswith('Удалить все')

                if del_all or yask.startswith('Удалить'):
                    self.web_action.webs_and_lines.remove(web)
                    is_del = True

                elif yask == 'Выход':
                    break
            continue

        if is_del:
            self.web_action_to_tk_text(websReport=True)
        return

    def tk_text_dummy_remove(self, force=False, mode='') -> bool:
        """
        удалить все dummy web_ - запуск
        """
        with self.block():
            b = self._tk_text_dummy_remove(force=force, mode=mode)
        return b

    def _tk_text_dummy_remove(self, force=False, mode='') -> bool:
        """
        удалить все dummy web_ - ядро
        """
        text = self.tk_text.get(1.0, tk.END).strip()
        _web_action = lr_lib.core.action.main_awal.ActionWebsAndLines(self)
        _web_action.set_text_list(text)

        if mode == 'endswith':
            is_remove = lr_lib.etc.template.dummy_endswith_remove
        else:
            is_remove = lr_lib.etc.template.dummy_remove

        rem = 0
        al = tuple(_web_action.get_web_all())
        for web_ in al:
            if is_remove(web_.lines_list):
                _web_action.webs_and_lines.remove(web_)
                rem += 1
            continue

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
                _type = lr_lib.etc.template.Dummy.web_dummy_template.split('("', 1)[0].strip()
                lwnt = len(tuple(w for w in text_t if w.type == _type))
                lwnd = len(tuple(w for w in text_w if w.type == _type))

            cd = max((t1 - t2, lwnt - lwnd))
            buttons = ['Удалить/Пересканировать', 'Пропустить', 'Выход']
            n1, n2, n3, n4 = '{}|Snapshot|строк|символов'.format(_type).split('|')

            tx1 = 'Удалить {cd} шт. "dummy" - {web_name} из action.c текста?\n' \
                  'Если изменить web_dummy_template текст,\n' \
                  'action.c пересканируется, с повторным показом диалог окна.\n' \
                  'inf удаляется, если его строки, начинаются\n' \
                  'на соответствующие им строки, в web_dummy_template,\n' \
                  'без учета начальных пробелов.'
            tx2 = 'action.c до и после удаления {web_name}:\n' \
                  '{n1:>20} {n2:>20} {n3:>20} {n4:>20}\n' \
                  '{lwnt:>20} | {t1:>20} | {ltn:>20} | {d:>20} |\n' \
                  '{lwnd:>20} | {t2:>20} | {ldn:>20} | {nd:>20} |'

            ync = lr_lib.gui.widj.dialog.YesNoCancel(
                buttons=buttons,
                text_before=tx1.format(web_name=_type, cd=cd),
                text_after=tx2.format(n1=n1, n2=n2, n3=n3, n4=n4, lwnt=lwnt, lwnd=lwnd, d=dum_len, nd=no_dum_len,
                                      t1=t1, t2=t2, ltn=ltn, ldn=ldn, web_name=_type),
                title='web_dummy_template | удалить {rem} шт ?'.format(rem=rem),
                is_text=lr_lib.etc.template.Dummy.web_dummy_template,
                parent=self,
            )

            y = ync.ask()
            if y == buttons[2]:
                return False

            template = ync.text.strip()
            if ((len(template) != lr_lib.etc.template.Dummy.web_len) or
                    (len(template.split('\n')) != lr_lib.etc.template.Dummy.dummy_len)):
                lr_lib.etc.template.Dummy.setattrs(template)
                self.tk_text_dummy_remove()
                return

            if y == buttons[0]:
                new_text = _web_action.to_str(websReport=False)
                self.backup()
                self.tk_text_to_web_action(text=new_text, websReport=True)

            if y in buttons[:2]:
                return True
        return

    def thinktime_remove(self, *args, word='lr_think_time') -> None:
        """
        удалить thinktime
        """
        text = self.tk_text.get(1.0, tk.END)
        assert text
        num = 0

        def filter_lines() -> iter((str,)):
            nonlocal num
            for line in text.split('\n'):
                if line.lstrip().startswith(word):
                    num += 1
                else:
                    yield line
                continue
            return

        lines = list(filter_lines())
        if lines:
            if messagebox.askokcancel('thinktime', 'удалить thinktime из action?\n{} шт.'.format(num), parent=self):
                self.backup()
                ls = '\n'.join(lines)
                self.tk_text_to_web_action(ls, websReport=True)
        return

    @lr_lib.core.var.vars_other.T_POOL_decorator
    def all_transaction_rename(self, *args) -> None:
        """
        переименавать все транзакции
        """
        _transactions = [t.split('"', 1)[1] for t in self.transaction]
        transactions = list(sorted(set(_transactions), key=_transactions.index))

        mx = max(map(len, transactions or ['']))
        m = '"{:<%s}" -> "{}"' % mx
        z2 = zip(transactions, transactions)
        all_transaction = '\n'.join(m.format(old, new) for old, new in z2)

        key = 'Переименовать'
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=[key, 'Отмена'],
            text_before='Переименовать transaction слева',
            text_after='в transaction справа',
            title='transaction',
            parent=self,
            is_text=all_transaction,
        )

        if y.ask() == key:
            new_transaction = [t.split('-> "', 1)[1].split('"', 1)[0].strip() for t in y.text.strip().split('\n')]
            assert (len(transactions) == len(new_transaction))

            text = self.tk_text.get('1.0', tk.END)
            for old, new in zip(transactions, new_transaction):
                text = text.replace((st + old), (st + new))
                text = text.replace((en + old), (en + new))
                continue

            self.backup()
            self.tk_text_to_web_action(text, websReport=True)
        return


st = 'lr_start_transaction("'
en = 'lr_end_transaction("'
