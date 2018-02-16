# -*- coding: UTF-8 -*-
# внутреннее предсталление action.c текста

import lr_lib.core.action.transac as lr_transac
import lr_lib.core.etc.other as lr_other
import lr_lib.core.action.report as lr_report
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.action.web_ as lr_web_
import lr_lib.core.wrsp.param as lr_param


class ActionWebsAndLines:
    '''внутреннее представление action.c текста, как список web_ объектов, и "неважного" текста между ними'''
    def __init__(self, action):
        self.action = action  # lr_lib.gui.action.main_action.ActionWindow
        self.webs_and_lines = []  # представление
        self.websReport = lr_report.WebReport(parent_AWAL=self)
        self.transactions = lr_transac.Transactions(self)

    def get_web_all(self) -> iter((lr_web_.WebAny,)):
        '''все объекты'''
        for web in self.webs_and_lines:
            if not isinstance(web, str):
                yield web

    def get_web_by(self, webs, **kwargs) -> iter((lr_web_.WebAny,)):
        '''объекты по kwargs условию: kwargs={'abc': [123]} -> web's.abc == [123]'''
        attrs = kwargs.items()
        for web in webs:
            if all((getattr(web, attr) == value) for (attr, value) in attrs):
                yield web

    def get_web_snapshot_all(self) -> iter((lr_web_.WebSnapshot,)):
        '''snapshot объекты'''
        for web in self.get_web_all():
            if web.snapshot:
                yield web

    def get_web_snapshot_by(self, **kwargs) -> iter((lr_web_.WebSnapshot,)):
        '''snapshot объекты по kwargs условию'''
        for web in self.get_web_by(self.get_web_snapshot_all(), **kwargs):
            yield web

    def get_web_reg_save_param_all(self) -> iter((lr_web_.WebRegSaveParam,)):
        '''web_reg_save_param объекты'''
        for web in self.get_web_snapshot_all():
            yield from web.web_reg_save_param_list

    def get_web_reg_save_param_by(self, **kwargs) -> iter((lr_web_.WebRegSaveParam,)):
        '''web_reg_save_param объекты по kwargs условию'''
        for web_wrsp in self.get_web_by(self.get_web_reg_save_param_all(), **kwargs):
            yield web_wrsp

    def replace_bodys(self, replace_list: [(str, str), ], is_wrsp=True) -> None:
        '''заменить группу param, во всех web_ body'''
        web_actions = tuple(self.get_web_snapshot_all())
        lr_vars.Logger.trace('web_actions={lw}, replace_list={lrl}:{rl}'.format(
            rl=replace_list, lrl=len(replace_list), lw=len(web_actions)))

        for web_ in web_actions:
            body = web_.get_body()

            for search, replace in replace_list:
                body = lr_web_.body_replace(body, search, replace, is_wrsp=is_wrsp)

            web_.set_body(body)

    def replace_bodys_iter(self, is_wrsp=True) -> None:
        '''заменить группу param, во всех web_ body - сопрограмма'''
        web_actions = tuple(self.get_web_snapshot_all())

        search_replace = yield
        while search_replace is not None:
            search, replace = search_replace

            for web_ in web_actions:
                body = web_.get_body()
                new_body = lr_web_.body_replace(body, search, replace, is_wrsp=is_wrsp)
                if body != new_body:
                    web_.set_body(new_body)

            search_replace = yield

    def add_to_text_list(self, element: (str or object)) -> None:
        '''объединять строки, идущие подряд'''
        last_ = self.webs_and_lines[-1]

        if isinstance(element, str) and isinstance(last_, str):
            self.webs_and_lines[-1] = '{tl}\n{et}'.format(tl=last_, et=element)
        else:
            self.webs_and_lines.append(element)

    @lr_other.exec_time
    def set_text_list(self, text: str, websReport=True) -> None:
        '''создать все web_action объекты'''
        with self.action.block():
            self.transactions = lr_transac.Transactions(self)
            self._set_text_list(text)

            if websReport:
                self.websReport.create()

    def _set_text_list(self, text: str) -> None:
        '''создать все web_action объекты'''
        iter_lines = iter(text.split('\n'))
        line = next(iter_lines, None)
        line_num = 1

        self.webs_and_lines = [line]

        reg_param_list = []  # web_reg_save_param's, для добавления в web_.web_reg_save_param_list
        comments = ''  # //
        _multiline_comment = []  # // /**/
        _OldPComment = lr_param.LR_COMENT + ' PARAM'
        lw_end = (lr_param.Web_LAST, lr_param._block_endswith3, )
        comment_format = '{}\n{}'.format

        for line in iter_lines:
            strip_line = line.strip()
            line_num += 1

            if not strip_line:
                continue

            elif _multiline_comment or strip_line.startswith('/*'):
                _multiline_comment.append(line)

                if strip_line.startswith('*/') or strip_line.endswith('*/'):
                    comments = comment_format(comments, '\n'.join(_multiline_comment)).rstrip()
                    _multiline_comment = []
                continue

            elif strip_line.startswith(lr_param.LR_COMENT) and (not strip_line.startswith(_OldPComment)):
                continue

            elif strip_line.startswith('//'):
                comments = comment_format(comments, line).rstrip()
                continue

            elif strip_line.startswith(lr_param._block_startswith):  # начало блока web_
                web_list = [line]  # web_ текст Snapshot запроса
                w_type = lr_web_.read_web_type(line)

                if strip_line.endswith(lr_param._block_endswith) or strip_line.endswith('('):  # тело запроса

                    for web_line in iter_lines:
                        line_num += 1
                        web_list.append(web_line)
                        if any(map(web_line.rstrip().endswith, lw_end)):
                            break

                    transaction = self.transactions._current()

                    if w_type.startswith('web_reg_save_param'):
                        web_ = lr_web_.WebRegSaveParam(self, web_list, comments, transaction=transaction, _type=w_type)
                        reg_param_list.append(web_)

                    else:
                        if (len(web_list) < 3) or (not any(lr_param.Snap1 in ln for ln in web_list)):
                            web_ = lr_web_.WebAny(self, web_list, comments, transaction=transaction, _type=w_type)
                            self.add_to_text_list(web_)

                        else:
                            web_ = lr_web_.WebSnapshot(self, web_list, comments, transaction=transaction, _type=w_type)
                            web_.web_reg_save_param_list = reg_param_list
                            reg_param_list = []
                            self.add_to_text_list(web_)

                    comments = ''
                    continue

                elif any(map(strip_line.endswith, lw_end)):  # однострочные web_
                    web_ = lr_web_.WebAny(self, web_list, comments, transaction=self.transactions._current(), _type=w_type)
                    self.add_to_text_list(web_)
                    comments = ''
                    continue

                else:
                    lr_vars.Logger.critical('вероятно ошибка распознавания\n{line}\n{lwl}\n{web_list}'.format(
                        line=line, lwl=len(web_list), web_list=web_list))
                    self.add_to_text_list(line)
                    continue

            elif strip_line:  # не web_ текст
                self.set_transaction_name(strip_line)

                if comments:
                    line = comment_format(comments, line)
                    comments = ''

                self.add_to_text_list(line)
                continue

        if comments:
            self.add_to_text_list(comments)
        if _multiline_comment:
            self.add_to_text_list('\n'.join(_multiline_comment))

        if reg_param_list:
            lr_vars.Logger.critical('Ненайден web_* запрос, которому принадлежат web_reg_save_param:\n{}'.format(
                [w.name for w in reg_param_list]))
            self.add_to_text_list('\n// ERROR web_reg_save_param !\n{}'.format(
                '\n\n'.join(map(lr_web_.WebRegSaveParam.to_str, reg_param_list))))

    def set_transaction_name(self, strip_line: str) -> (str or None):
        '''проверить линию, сохранить имя transaction'''
        if strip_line.startswith('lr_'):  # lr_start_transaction("login");
            if strip_line.startswith('lr_start_transaction'):
                transac = strip_line.split('"', 2)
                transac = transac[1]
                self.transactions.start_transaction(transac)

            elif strip_line.startswith('lr_end_transaction'):
                transac = strip_line.split('"', 2)
                transac = transac[1]
                self.transactions.stop_transaction(transac)

    def web_reg_save_param_insert(self, wrsp_dict_or_snapshot: (dict or int), wrsp='') -> lr_web_.WebRegSaveParam:
        '''вставить web_reg_save_param'''
        if isinstance(wrsp_dict_or_snapshot, dict):
            inf = wrsp_dict_or_snapshot['inf_nums'][0]
            if not wrsp:
                wrsp = lr_param.create_web_reg_save_param(wrsp_dict_or_snapshot)
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
        ws = wrsp.split(lr_param.wrsp_lr_start, 1)
        if len(ws) == 2:
            comments, w_lines = ws
            w_lines = lr_param.wrsp_lr_start + w_lines
        else:
            comments = ''
            w_lines = wrsp

        w_lines = w_lines.split('\n')
        wrsp_web_ = lr_web_.WebRegSaveParam(self, w_lines, comments, transaction=web_.transaction, parent_snapshot=web_)
        web_.web_reg_save_param_list.append(wrsp_web_)

        return wrsp_web_

    def web_reg_save_param_remove(self, name: str, keys=('param', 'name'), param=None, is_wrsp=False) -> str:
        '''удалить web_reg_save_param, is_wrsp=False'''
        for web_request in self.get_web_snapshot_all():
            for wrsp_web in list(web_request.web_reg_save_param_list):

                if any((getattr(wrsp_web, k) == name) for k in keys):
                    web_request.web_reg_save_param_list.remove(wrsp_web)
                    param = wrsp_web.param
                    wn = lr_param.param_bounds_setter(wrsp_web.name)
                    replace_list = [(wn, param), ]

                    self.replace_bodys(replace_list, is_wrsp=is_wrsp)  # удалить из всех web
                    break

        return param

    @lr_other.exec_time
    def to_str(self, websReport=False) -> str:
        '''весь action текст как строка'''
        if websReport:
            self.websReport.create()
        return ''.join(self._to_str()).strip()

    def _to_str(self, sep=True) -> iter((str,)):
        '''итератор - весь action текст как строка'''
        for line in self.webs_and_lines:
            is_str = isinstance(line, str)
            if is_str != sep:
                yield '\n'  # смена str/WEB_

            if is_str:
                yield '\n{}'.format(line.strip('\n'))
            elif isinstance(line, lr_web_.WebSnapshot):
                yield '\n\n{}\n'.format(line.to_str())
            else:
                yield '\n{}'.format(line.to_str())

            sep = is_str
