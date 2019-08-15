# -*- coding: UTF-8 -*-
# внутреннее предсталление action.c текста

from typing import Iterable, Tuple, List

import lr_lib
import lr_lib.core.action.report
import lr_lib.core.action.transac
import lr_lib.core.action.web_ as lr_web
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param
import lr_lib.gui.action.main_action


class ActionWebsAndLines:
    """
    внутреннее представление action.c текста, как список web_ объектов, и "неважного" текста между ними
    """

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
        """
        в LoadRunner могут быть inf-файлы, которых нету в action.c(например удалили лишний код),
        такие файлы надо отсеять, тк web_reg_save_param потом может на него сослатся
        """
        self.action_infs.clear()
        self.drop_infs.clear()
        self.drop_files.clear()

        al = self.get_web_snapshot_all()
        act_infs = [a.snapshot.inf for a in al]
        self.action_infs.extend(act_infs)

        for file in lr_vars.AllFiles:
            check = False
            nums = file['Snapshot']['Nums']
            for inf in nums:
                if inf in self.action_infs:
                    check = True
                else:
                    self.drop_infs.add(inf)
                continue

            if not check:
                name = file['File']['Name']
                self.drop_files.append(name)
            continue
        return

    def get_web_all(self) -> Iterable[lr_web.WebAny]:
        """
        все объекты
        """
        for web in self.webs_and_lines:
            if not isinstance(web, str):
                yield web
            continue
        return

    def get_web_by(self, webs: Iterable[lr_web.WebAny], **kwargs) -> Iterable[lr_web.WebAny]:
        """
        объекты по kwargs условию: kwargs={'abc': [123]} -> web's.abc == [123]
        """
        snapshot = kwargs.pop('snapshot', None)
        attrs = kwargs.items()
        for web in webs:
            equal = ((getattr(web, attr) == value) for (attr, value) in attrs)
            if all(equal):
                if snapshot:
                    ob = getattr(web, 'snapshot')
                    if ob.inf != snapshot:
                        continue
                yield web
            continue
        return

    def get_web_snapshot_all(self) -> Iterable[lr_web.WebSnapshot]:
        """
        snapshot объекты
        """
        webs = self.get_web_all()
        for web in webs:
            if web.snapshot.inf:
                yield web
            continue
        return

    def get_web_snapshot_by(self, **kwargs) -> Iterable[lr_web.WebSnapshot]:
        """
        snapshot объекты по kwargs условию
        """
        al = self.get_web_snapshot_all()
        webs = self.get_web_by(al, **kwargs)
        for web in webs:
            yield web
            continue
        return

    def get_web_reg_save_param_all(self) -> Iterable[lr_web.WebRegSaveParam]:
        """
        web_reg_save_param объекты
        """
        webs = self.get_web_snapshot_all()
        for web in webs:
            wrsps = web.web_reg_save_param_list
            yield from wrsps
            continue
        return

    def get_web_reg_save_param_by(self, **kwargs) -> Iterable[lr_web.WebRegSaveParam]:
        """
        web_reg_save_param объекты по kwargs условию
        """
        al = self.get_web_reg_save_param_all()
        webs = self.get_web_by(al, **kwargs)
        for web_wrsp in webs:
            yield web_wrsp
            continue
        return

    def replace_bodys(self, replace_list: List[Tuple[str, str]], is_wrsp=True, min_inf=0, max_inf=0) -> None:
        """
        заменить группу param, во всех web_ body
        """
        web_actions = tuple(self.get_web_snapshot_all())
        i = 'web_actions={len_action_web}, replace_list={len_replace}:{replace}'
        i = i.format(replace=replace_list, len_replace=len(replace_list), len_action_web=len(web_actions), )
        lr_vars.Logger.trace(i)

        for web_ in web_actions:
            if max_inf and (web_.snapshot.inf > max_inf):
                break
            elif min_inf and (web_.snapshot.inf < min_inf):
                continue

            body = web_.get_body()

            for (search, replace) in replace_list:
                body = lr_web.body_replace(body, search, replace, is_wrsp=is_wrsp)
                continue

            web_.set_body(body)
            continue
        return

    def replace_bodys_iter(self, web_actions: Iterable[lr_web.WebAny], is_wrsp=True, min_inf=0, max_inf=0) -> None:
        """
        заменить группу param, во всех web_ body - сопрограмма
        """
        search_replace = yield
        while search_replace is not None:
            if len(search_replace) == 4:
                (search, replace, min_inf, max_inf) = search_replace
            else:
                (search, replace) = search_replace

            for web_ in web_actions:
                if max_inf and (web_.snapshot.inf > max_inf):
                    break
                elif min_inf and (web_.snapshot.inf < min_inf):
                    continue

                body = web_.get_body()

                new_body = lr_web.body_replace(body, search, replace, is_wrsp=is_wrsp)
                if body != new_body:
                    web_.set_body(new_body)
                continue

            search_replace = yield
            continue
        return

    def _add_to_text_list(self, element: 'str or lr_web.WebAny') -> None:
        """
        объединять строки, идущие подряд
        """
        last_ = self.webs_and_lines[-1]

        if isinstance(element, str) and isinstance(last_, str):
            s = '{last_}\n{element}'.format(last_=last_, element=element, )
            self.webs_and_lines[-1] = s
        else:
            self.webs_and_lines.append(element)
        return

    def set_text_list(self, text_list: str, websReport=True) -> None:
        """
        создать все web_action объекты
        """
        self.transactions = lr_lib.core.action.transac.Transactions(self)

        if isinstance(text_list, str):
            text_list = text_list.split('\n')

        self._set_text_list(iter_lines=text_list)

        if websReport:  # статистика использования WRSP
            self.websReport.create()

        self.drop_file_none_inf_num_in_action()
        return

    def _set_text_list(self, iter_lines: Iterable[str]) -> None:
        """
        создать все web_action объекты
        """
        self.webs_and_lines.clear()

        RegParamList = []  # web_reg_save_param's, для добавления в web_.web_reg_save_param_list
        COMMENT = ''  # //
        MultiLine_COMMENT = []  # // /**/
        _OldPComment = (lr_lib.core.wrsp.param.LR_COMENT + ' PARAM')
        lw_end = (lr_lib.core.wrsp.param.Web_LAST, lr_lib.core.wrsp.param._block_endswith3,)
        comment_format = '{0}\n{1}'.format

        iter_lines = map(str.rstrip, iter_lines)
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
                w_type = lr_web.read_web_type(LINE)

                if SLINE.endswith(lr_lib.core.wrsp.param._block_endswith) or SLINE.endswith('('):  # тело запроса

                    for web_line in iter_lines:
                        web_list.append(web_line)
                        endswith = map(web_line.endswith, lw_end)
                        if any(endswith):
                            break
                        continue

                    transaction = self.transactions._current()

                    if w_type.startswith('web_reg_save_param'):
                        # создать WebRegSaveParam
                        web_ = lr_web.WebRegSaveParam(
                            self,
                            web_list,
                            COMMENT,
                            transaction=transaction,
                            _type=w_type,
                        )

                        RegParamList.append(web_)

                    else:
                        if (len(web_list) < 3) or (not any(lr_lib.core.wrsp.param.Snap1 in ln for ln in web_list)):
                            # создать WebAny
                            web_ = lr_web.WebAny(
                                self,
                                web_list,
                                COMMENT,
                                transaction=transaction,
                                _type=w_type,
                            )

                            self._add_to_text_list(web_)

                        else:
                            # создать WebSnapshot
                            web_ = lr_web.WebSnapshot(
                                self,
                                web_list,
                                COMMENT,
                                transaction=transaction,
                                _type=w_type,
                            )

                            web_.web_reg_save_param_list = RegParamList
                            RegParamList = []
                            self._add_to_text_list(web_)

                    COMMENT = ''

                elif any(map(SLINE.endswith, lw_end)):  # однострочные web_
                    t = self.transactions._current()

                    # создать WebAny
                    web_ = lr_web.WebAny(
                        self,
                        web_list,
                        COMMENT,
                        transaction=t,
                        _type=w_type,
                    )

                    self._add_to_text_list(web_)
                    COMMENT = ''

                else:
                    self._add_to_text_list(LINE)
                    e = 'вероятно ошибка распознавания\n{line}\n{len_web_list}\n{web_list}'
                    e = e.format(line=LINE, len_web_list=len(web_list), web_list=web_list)
                    lr_vars.Logger.critical(e)

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
            mc = '\n'.join(MultiLine_COMMENT)
            self._add_to_text_list(mc)

        if RegParamList:
            rpl = map(lr_web.WebRegSaveParam.to_str, RegParamList)
            a = '\n// ERROR web_reg_save_param !\n{0}'
            a = a.format('\n\n'.join(rpl))
            self._add_to_text_list(a)

            wpn = [w.name for w in RegParamList]
            e = 'Ненайден web_* запрос, которому принадлежат web_reg_save_param:\n{0}'
            e = e.format(wpn)
            lr_vars.Logger.critical(e)
        return

    def set_transaction_name(self, strip_line: str, sep='"') -> None:
        """
        проверить линию, сохранить имя transaction
        """
        if strip_line.startswith('lr_'):  # lr_start_transaction("login");
            if strip_line.startswith('lr_start_transaction'):
                transac = strip_line.split(sep, 2)
                transac = transac[1]
                self.transactions.start_transaction(transac)

            elif strip_line.startswith('lr_end_transaction'):
                transac = strip_line.split(sep, 2)
                transac = transac[1]
                self.transactions.stop_transaction(transac)
        return

    def web_reg_save_param_insert(
            self,
            wrsp_dict_or_snapshot: 'dict or int',
            wrsp='',
    ) -> lr_web.WebRegSaveParam:
        """
        вставить web_reg_save_param
        """
        if isinstance(wrsp_dict_or_snapshot, dict):
            inf = wrsp_dict_or_snapshot['inf_nums']
            inf = inf[0]
            if not wrsp:
                wrsp = lr_lib.core.wrsp.param.create_web_reg_save_param(wrsp_dict_or_snapshot)
        elif isinstance(wrsp_dict_or_snapshot, int):
            inf = wrsp_dict_or_snapshot
            if not wrsp:
                e = 'пустой wrsp {0} | {1} | {2} | {3}'
                e = e.format(wrsp_dict_or_snapshot, type(wrsp_dict_or_snapshot), wrsp, type(wrsp))
                raise UserWarning(e)
        else:
            e = 'тип wrsp_dict_or_snapshot {0} | {1} | {2} | {3}'
            e = e.format(wrsp_dict_or_snapshot, type(wrsp_dict_or_snapshot), wrsp, type(wrsp))
            raise UserWarning(e)

        w = self.get_web_snapshot_by(snapshot=inf)
        web_ = next(w)

        # разделить каменты и web текст
        ws = wrsp.split(lr_lib.core.wrsp.param.wrsp_lr_start, 1)
        if len(ws) == 2:
            (comments, w_lines) = ws
            w_lines = (lr_lib.core.wrsp.param.wrsp_lr_start + w_lines)
        else:
            comments = ''
            w_lines = wrsp

        w_lines = w_lines.split('\n')
        # создать WebRegSaveParam
        wrsp_web_ = lr_web.WebRegSaveParam(
            self,
            w_lines,
            comments,
            transaction=web_.transaction,
            parent_snapshot=web_,
        )
        web_.web_reg_save_param_list.append(wrsp_web_)

        return wrsp_web_

    def web_reg_save_param_remove(self, name: str, keys=('param', 'name'), param=None, is_wrsp=False) -> str:
        """
        удалить web_reg_save_param, is_wrsp=False
        """
        al = self.get_web_snapshot_all()
        for web_request in al:
            for wrsp_web in web_request.web_reg_save_param_list:

                if any((getattr(wrsp_web, k) == name) for k in keys):
                    web_request.web_reg_save_param_list.remove(wrsp_web)
                    param = wrsp_web.param
                    wn = lr_lib.core.wrsp.param.param_bounds_setter(wrsp_web.name)
                    rl = (wn, param)
                    replace_list = [rl, ]

                    self.replace_bodys(replace_list, is_wrsp=is_wrsp)  # удалить из всех web
                continue
            continue
        return param

    def to_str(self, websReport=False) -> str:
        """
        весь action текст как строка
        """
        if websReport:
            self.websReport.create()

        s = ''.join(self._to_str())
        return s

    def _to_str(self, n_sign=True) -> Iterable[str]:
        """
        Весь action текст как строка.
        Форматирование переносов строк '\n' в блоках текста и между ними.
        """
        no_first = False
        for line in self.webs_and_lines:
            is_line_str = isinstance(line, str)

            # дополнительная линия
            if is_line_str != n_sign:
                _line = '\n'
                yield _line  # перенос, при смене str/WEB_

            # основная линия
            if is_line_str:  # str
                line = line.strip('\n')
                if no_first:
                    line = '\n{0}'.format(line)
                else:
                    no_first = True
                yield line

            elif isinstance(line, lr_web.WebSnapshot):  # snapshot Web
                line = line.to_str()
                line = '\n\n{0}\n'.format(line)
                yield line

            else:  # не snapshot Web
                line = line.to_str()
                line = '\n{0}'.format(line)
                yield line

            n_sign = is_line_str
            continue

        self.action.tk_text.linenumbers.add_linenumbers()
        return

    def _all_web_body_text(self) -> str:
        """
        текст body всех web
        """
        al = self.get_web_all()
        text = '\n'.join(w.get_body() for w in al)
        return text
