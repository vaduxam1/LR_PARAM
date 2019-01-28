# -*- coding: UTF-8 -*-
# внутреннее предсталление action.c текста

import lr_lib
import lr_lib.core.action.report
import lr_lib.core.action.transac
import lr_lib.core.action.web_
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param


class ActionWebsAndLines:
    """внутреннее представление action.c текста, как список web_ объектов, и "неважного" текста между ними"""

    def __init__(self, action: 'lr_lib.gui.action.main_action.ActionWindow'):
        self.action = action

        self.webs_and_lines = []  # представление

        self.websReport = lr_lib.core.action.report.WebReport(parent_=self)
        self.transactions = lr_lib.core.action.transac.Transactions(self)

        self.action_infs = []  # номера inf в action
        self.drop_infs = set()  # отсутствующие номера inf в action
        self.drop_files = []  # файлы из отсутствующих inf
        return

    def drop_file_none_inf_num_in_action(self) -> None:
        """в LoadRunner могут быть inf-файлы, которых нету в action.c(например удалили лишний код),
        такие файлы надо отсеять, тк web_reg_save_param потом может на него сослатся"""
        self.action_infs.clear()
        self.drop_infs.clear()
        self.drop_files.clear()

        self.action_infs.extend(a.snapshot.inf for a in self.get_web_snapshot_all())

        for file in lr_vars.AllFiles:
            check = False

            for inf in file['Snapshot']['Nums']:
                if inf in self.action_infs:
                    check = True
                else:
                    self.drop_infs.add(inf)
                continue

            if not check:
                self.drop_files.append(file['File']['Name'])
            continue
        return

    def get_web_all(self) -> iter((lr_lib.core.action.web_.WebAny,)):
        """все объекты"""
        for web in self.webs_and_lines:
            if not isinstance(web, str):
                yield web
            continue
        return

    def get_web_by(self, webs: (lr_lib.core.action.web_.WebAny,), **kwargs) -> iter((lr_lib.core.action.web_.WebAny,)):
        """объекты по kwargs условию: kwargs={'abc': [123]} -> web's.abc == [123]"""
        snapshot = kwargs.pop('snapshot', None)
        attrs = kwargs.items()
        for web in webs:
            if all((getattr(web, attr) == value) for (attr, value) in attrs):
                if snapshot and (getattr(web, 'snapshot').inf != snapshot):
                    continue
                yield web
            continue
        return

    def get_web_snapshot_all(self) -> iter((lr_lib.core.action.web_.WebSnapshot,)):
        """snapshot объекты"""
        for web in self.get_web_all():
            if web.snapshot.inf:
                yield web
            continue
        return

    def get_web_snapshot_by(self, **kwargs) -> iter((lr_lib.core.action.web_.WebSnapshot,)):
        """snapshot объекты по kwargs условию"""
        for web in self.get_web_by(self.get_web_snapshot_all(), **kwargs):
            yield web
            continue
        return

    def get_web_reg_save_param_all(self) -> iter((lr_lib.core.action.web_.WebRegSaveParam,)):
        """web_reg_save_param объекты"""
        for web in self.get_web_snapshot_all():
            yield from web.web_reg_save_param_list
            continue
        return

    def get_web_reg_save_param_by(self, **kwargs) -> iter((lr_lib.core.action.web_.WebRegSaveParam,)):
        """web_reg_save_param объекты по kwargs условию"""
        for web_wrsp in self.get_web_by(self.get_web_reg_save_param_all(), **kwargs):
            yield web_wrsp
            continue
        return

    def replace_bodys(self, replace_list: [(str, str), ], is_wrsp=True) -> None:
        """заменить группу param, во всех web_ body"""
        web_actions = tuple(self.get_web_snapshot_all())
        lr_vars.Logger.trace('web_actions={lw}, replace_list={lrl}:{rl}'.format(
            rl=replace_list, lrl=len(replace_list), lw=len(web_actions)))

        for web_ in web_actions:
            body = web_.get_body()

            for (search, replace) in replace_list:
                body = lr_lib.core.action.web_.body_replace(body, search, replace, is_wrsp=is_wrsp)
                continue

            web_.set_body(body)
            continue
        return

    def replace_bodys_iter(self, web_actions: (lr_lib.core.action.web_.WebAny,), is_wrsp=True) -> None:
        """заменить группу param, во всех web_ body - сопрограмма"""
        search_replace = yield
        while search_replace is not None:
            (search, replace) = search_replace

            for web_ in web_actions:
                body = web_.get_body()
                new_body = lr_lib.core.action.web_.body_replace(body, search, replace, is_wrsp=is_wrsp)
                if body != new_body:
                    web_.set_body(new_body)
                continue

            search_replace = yield
            continue
        return

    def _add_to_text_list(self, element: (str or lr_lib.core.action.web_.WebAny)) -> None:
        """объединять строки, идущие подряд"""
        last_ = self.webs_and_lines[-1]

        if isinstance(element, str) and isinstance(last_, str):
            self.webs_and_lines[-1] = '{tl}\n{et}'.format(tl=last_, et=element)
        else:
            self.webs_and_lines.append(element)

    def set_text_list(self, text_list: [str, ], websReport=True) -> None:
        """создать все web_action объекты"""
        self.transactions = lr_lib.core.action.transac.Transactions(self)

        if isinstance(text_list, str):
            text_list = text_list.split('\n')

        self._set_text_list(iter_lines=text_list)

        if websReport:  # статистика использования WRSP
            self.websReport.create()
        self.drop_file_none_inf_num_in_action()
        return

    def _set_text_list(self, iter_lines: (str,)) -> None:
        """создать все web_action объекты"""
        iter_lines = map(str.rstrip, iter_lines)
        self.webs_and_lines.clear()

        RegParamList = []  # web_reg_save_param's, для добавления в web_.web_reg_save_param_list
        COMMENT = ''  # //
        MultiLine_COMMENT = []  # // /**/
        _OldPComment = (lr_lib.core.wrsp.param.LR_COMENT + ' PARAM')
        lw_end = (lr_lib.core.wrsp.param.Web_LAST, lr_lib.core.wrsp.param._block_endswith3,)
        comment_format = '{}\n{}'.format

        # первая линия(всегда как str)
        LINE = next(iter_lines, None)
        self.webs_and_lines.append(LINE)

        for LINE in iter_lines:
            SLINE = LINE.lstrip()

            if not SLINE:
                continue

            elif MultiLine_COMMENT or SLINE.startswith('/*'):
                MultiLine_COMMENT.append(LINE)

                if SLINE.startswith('*/') or SLINE.endswith('*/'):
                    COMMENT = comment_format(COMMENT, '\n'.join(MultiLine_COMMENT))
                    MultiLine_COMMENT = []

            elif SLINE.startswith(lr_lib.core.wrsp.param.LR_COMENT) and (not SLINE.startswith(_OldPComment)):
                continue

            elif SLINE.startswith('//'):
                COMMENT = comment_format(COMMENT, LINE)

            elif SLINE.startswith(lr_lib.core.wrsp.param._block_startswith):  # начало блока web_
                web_list = [LINE]  # web_ текст Snapshot запроса
                w_type = lr_lib.core.action.web_.read_web_type(LINE)

                if SLINE.endswith(lr_lib.core.wrsp.param._block_endswith) or SLINE.endswith('('):  # тело запроса

                    for web_line in iter_lines:
                        web_list.append(web_line)
                        if any(map(web_line.endswith, lw_end)):
                            break
                        continue

                    transaction = self.transactions._current()

                    if w_type.startswith('web_reg_save_param'):
                        web_ = lr_lib.core.action.web_.WebRegSaveParam(
                            self, web_list, COMMENT, transaction=transaction, _type=w_type,
                        )
                        RegParamList.append(web_)

                    else:
                        if (len(web_list) < 3) or (not any(lr_lib.core.wrsp.param.Snap1 in ln for ln in web_list)):
                            web_ = lr_lib.core.action.web_.WebAny(
                                self, web_list, COMMENT, transaction=transaction, _type=w_type,
                            )
                            self._add_to_text_list(web_)

                        else:
                            web_ = lr_lib.core.action.web_.WebSnapshot(
                                self, web_list, COMMENT, transaction=transaction, _type=w_type,
                            )
                            web_.web_reg_save_param_list = RegParamList
                            RegParamList = []
                            self._add_to_text_list(web_)

                    COMMENT = ''

                elif any(map(SLINE.endswith, lw_end)):  # однострочные web_
                    web_ = lr_lib.core.action.web_.WebAny(
                        self, web_list, COMMENT, transaction=self.transactions._current(), _type=w_type,
                    )
                    self._add_to_text_list(web_)
                    COMMENT = ''

                else:
                    lr_vars.Logger.critical('вероятно ошибка распознавания\n{line}\n{lwl}\n{web_list}'.format(
                        line=LINE, lwl=len(web_list), web_list=web_list))
                    self._add_to_text_list(LINE)

            elif SLINE:  # не web_ текст
                self.set_transaction_name(SLINE)

                if COMMENT:
                    LINE = comment_format(COMMENT, LINE)
                    COMMENT = ''

                self._add_to_text_list(LINE)

            continue

        # на всякий, но ничего не должно остатся
        if COMMENT:
            self._add_to_text_list(COMMENT)
        if MultiLine_COMMENT:
            self._add_to_text_list('\n'.join(MultiLine_COMMENT))
        if RegParamList:
            self._add_to_text_list('\n// ERROR web_reg_save_param !\n{}'.format(
                '\n\n'.join(map(lr_lib.core.action.web_.WebRegSaveParam.to_str, RegParamList))))
            lr_vars.Logger.critical('Ненайден web_* запрос, которому принадлежат web_reg_save_param:\n{}'.format(
                [w.name for w in RegParamList]))
        return

    def set_transaction_name(self, strip_line: str) -> (str or None):
        """проверить линию, сохранить имя transaction"""
        if strip_line.startswith('lr_'):  # lr_start_transaction("login");
            if strip_line.startswith('lr_start_transaction'):
                transac = strip_line.split('"', 2)
                transac = transac[1]
                self.transactions.start_transaction(transac)

            elif strip_line.startswith('lr_end_transaction'):
                transac = strip_line.split('"', 2)
                transac = transac[1]
                self.transactions.stop_transaction(transac)
        return

    def web_reg_save_param_insert(self, wrsp_dict_or_snapshot: (dict or int),
                                  wrsp='') -> lr_lib.core.action.web_.WebRegSaveParam:
        """вставить web_reg_save_param"""
        if isinstance(wrsp_dict_or_snapshot, dict):
            inf = wrsp_dict_or_snapshot['inf_nums'][0]
            if not wrsp:
                wrsp = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict_or_snapshot)
        elif isinstance(wrsp_dict_or_snapshot, int):
            inf = wrsp_dict_or_snapshot
            if not wrsp:
                raise UserWarning('пустой wrsp {} | {} | {} | {}'.format(
                    wrsp_dict_or_snapshot, type(wrsp_dict_or_snapshot), wrsp, type(wrsp)))
        else:
            raise UserWarning('тип wrsp_dict_or_snapshot {} | {} | {} | {}'.format(
                wrsp_dict_or_snapshot, type(wrsp_dict_or_snapshot), wrsp, type(wrsp)))

        web_ = next(self.get_web_snapshot_by(snapshot=inf))

        # разделить каменты и web текст
        ws = wrsp.split(lr_lib.core.wrsp.param.wrsp_lr_start, 1)
        if len(ws) == 2:
            (comments, w_lines) = ws
            w_lines = (lr_lib.core.wrsp.param.wrsp_lr_start + w_lines)
        else:
            comments = ''
            w_lines = wrsp

        w_lines = w_lines.split('\n')
        wrsp_web_ = lr_lib.core.action.web_.WebRegSaveParam(
            self, w_lines, comments, transaction=web_.transaction, parent_snapshot=web_,
        )
        web_.web_reg_save_param_list.append(wrsp_web_)

        return wrsp_web_

    def web_reg_save_param_remove(self, name: str, keys=('param', 'name'), param=None, is_wrsp=False) -> str:
        """удалить web_reg_save_param, is_wrsp=False"""
        for web_request in self.get_web_snapshot_all():
            for wrsp_web in list(web_request.web_reg_save_param_list):

                if any((getattr(wrsp_web, k) == name) for k in keys):
                    web_request.web_reg_save_param_list.remove(wrsp_web)
                    param = wrsp_web.param
                    wn = lr_lib.core.wrsp.param.param_bounds_setter(wrsp_web.name)
                    replace_list = [(wn, param), ]

                    self.replace_bodys(replace_list, is_wrsp=is_wrsp)  # удалить из всех web
                continue
            continue
        return param

    def to_str(self, websReport=False) -> str:
        """весь action текст как строка"""
        if websReport:
            self.websReport.create()
        return ''.join(self._to_str()).strip()

    def _to_str(self, sep=True) -> iter((str,)):
        """итератор - весь action текст как строка"""
        for line in self.webs_and_lines:
            is_str = isinstance(line, str)
            if is_str != sep:
                yield '\n'  # смена str/WEB_

            if is_str:
                yield '\n{}'.format(line.strip('\n'))
            elif isinstance(line, lr_lib.core.action.web_.WebSnapshot):
                yield '\n\n{}\n'.format(line.to_str())
            else:
                yield '\n{}'.format(line.to_str())

            sep = is_str
            continue
        return

    def _all_web_body_text(self) -> str:
        """текст body всех web"""
        text = '\n'.join(w.get_body() for w in self.get_web_all())
        return text
