# -*- coding: UTF-8 -*-
# action.c "ядро"

import copy
import string
import contextlib
import itertools
import collections

from lr_lib import (
    defaults,
    logger as lr_log,
    param as lr_param,
    window_widj as lr_widj,
    other as lr_other,
    window_lib as lr_wlib,
)


buttons = (ys, yta, no, nta, rais) = ('Да', 'Да, для Всех', 'Нет', 'Нет, для Всех', 'Преврать',)
PrintableSet = set(string.printable)
start_transaction = 'lr_start_transaction'
end_transaction = 'lr_end_transaction'


def read_web_type(first_line: str, s1='("', s2='(') -> str:
    s = (s1 if (s1 in first_line) else s2)
    t = first_line.split(s, 1)
    if len(t) == 2:
        return t[0].strip()
    else: raise UserWarning('{l} не содержит {s}'.format(l=first_line, s=[s1, s2]))


def _body_replace(body_split, len_body_split, search, replace) -> iter((str, )):
    '''замена search в body'''
    yield body_split[0]

    for indx in range(1, len_body_split):
        left = body_split[indx - 1]
        right = body_split[indx]
        if lr_other.check_bound_lb_rb(left, right):
            yield replace + right
        else:
            yield search + right


def body_replace(body: str, search: str, replace: str) -> str:
    '''замена search в body'''
    body_split = body.split(search)
    len_body_split = len(body_split)

    if len_body_split < 2:
        return body
    else:
        return ''.join(_body_replace(body_split, len_body_split, search, replace))


def bodys_replace(replace_args: ({int: str}, [(str, str), ])) -> [str, ]:
    '''замена param's в body's'''
    body_portion, replace_list = replace_args
    for i in body_portion:
        for search, replace in replace_list:
            body_portion[i] = body_replace(body_portion[i], search, replace)
    return body_portion


class WebAny:
    count = 0

    def __init__(self, parent_AWAL, lines_list: list, comments: str, transaction: str, _type=''):
        self.parent_AWAL = parent_AWAL  # ActionWebsAndLines
        self.tk_text = self.parent_AWAL.action.tk_text
        self.lines_list = lines_list

        WebAny.count += 1
        self.unique_num = WebAny.count

        self.transaction = transaction
        self.type = _type or read_web_type(self.lines_list[0])
        self.name = self._read_name()
        self.snapshot = self._read_snapshot()

        self.comments = comments.rstrip().lstrip('\n')
        if self.comments:
            self.comments = '\n{}'.format(self.comments)

        print('\n{w}({n}):\n\tSnap={sn}, lines={l}, symb={s}, {t}'.format(w=self.type, n=self.name, l=len(self.lines_list), s=len(tuple(itertools.chain(*self.lines_list))), sn=self.snapshot, t=self.transaction))

    def _read_snapshot(self) -> int:
        '''Snapshot inf номер'''
        with contextlib.suppress(Exception):
            for line in self.lines_list[1:-1]:
                strip_line = line.strip()
                if strip_line.startswith(lr_param.Snap1) and strip_line.endswith(lr_param.Snap2):
                    inf_num = line.split(lr_param.Snap1, 1)
                    inf_num = inf_num[-1]
                    inf_num = inf_num.rsplit(lr_param.Snap2, 1)
                    inf_num = inf_num[0]
                    assert all(map(str.isnumeric, inf_num))
                    return int(inf_num)
        return 0

    def to_str(self) -> str:
        '''весь текст web_'''
        comments = self.comments

        if self.snapshot in self.parent_AWAL.websReport.rus_webs:
            comments += '\n\t{} WARNING: NO ASCII Symbols(rus?)'.format(lr_param.LR_COMENT)
        if (len(self.lines_list) > 2) and (not self.snapshot):
            comments += '\n\t{} WARNING: no "Snapshot=t.inf" (del?)'.format(lr_param.LR_COMENT)

        txt = '{coment_text}\n{snap_text}'.format(
            coment_text=comments, snap_text='\n'.join(self.lines_list))

        return txt.strip('\n')

    def _read_name(self, name='') -> str:
        try:
            n = self.lines_list[0]
            n = n.split('",', 1)
            n = n[0]
            n = n.split('("', 1)
            name = n[1]
        except IndexError:
            pass

        if (not name) and (self.type == 'web_reg_save_param_ex'):
            s = '"ParamName='
            for line in self.lines_list:
                sline = line.strip().split(s, 1)
                if len(sline) == 2:
                    name = sline[1].split('"')[0]
                    break

        return name

    def ask_replace(self, param, replace, left, right, ask_dict) -> bool:
        dk = (nta, yta, rais)
        if ask_dict and (a in ask_dict for a in dk):
            if ask_dict.get(rais):
                raise UserWarning('Прервано!\n{}'.format('\n\t###\n'.join((param, replace, left, right, ask_dict))))
            return ask_dict.get(nta) or ask_dict.get(yta)

        t2 = 'хотя строка и содержит param-имя "{p}"\nоно является частью другого, более длинного имени:\nЗаменить на "{r}" ?'.format(p=param, r=replace)
        t1 = 'заменяемая строка:\n{prev}{p}{part}'.format(prev=left[-defaults.AskLbRbMaxLen:].rsplit('\n', 1)[-1].lstrip(), p=param, part=right[:defaults.AskLbRbMaxLen].split('\n', 1)[0].rstrip())
        y = lr_wlib.YesNoCancel(buttons=buttons, text_before=t1, text_after=t2, title='автозамена "{s}" на "{r}"'.format(s=param, r=replace), parent=self.parent_AWAL.action, default_key=nta, focus=self.parent_AWAL.action.tk_text)
        a = y.ask()
        if ask_dict and (a in dk):
            ask_dict[a] = True
        r = (a in (ys, yta))
        return r

    def param_find_replace(self, param: str, replace=None, ask_dict=None) -> (int, int):
        '''автоматическая замена, c диалоговыми окнами'''
        body_split = self.get_body().split(param)
        len_body_split = len(body_split)
        if not len_body_split:
            return 0, 0
        action = self.parent_AWAL.action
        chunk_indxs = []

        def force_ask_replace(indx: int, left: str, right: str) -> None:
            action.search_in_action(word=param.join(body_split[:indx]), hist=False)
            if self.ask_replace(param, replace, left, right, ask_dict):
                chunk_indxs.append(indx)

        def normal_replace(indx: int, left: str, right: str, ask=(not action.no_var.get())) -> None:
            if lr_other.check_bound_lb_rb(left, right) or (ask and self.ask_replace(param, replace, left, right, ask_dict)):
                chunk_indxs.append(indx)

        add_index = force_ask_replace if action.force_ask_var.get() else normal_replace
        for indx in range(1, len_body_split):
            left = body_split[indx - 1]
            right = body_split[indx]
            if left and right:
                add_index(indx, left, right)

        if chunk_indxs and replace:
            body_chunks = [body_split.pop(0)]
            contains = chunk_indxs.__contains__
            for indx, body_chunk in enumerate(body_split, start=1):
                splitter = (replace if contains(indx) else param)
                body_chunks.append(splitter + body_chunk)
            self.set_body(''.join(body_chunks))  # замена

        param_count = len(chunk_indxs)
        skiped = len_body_split - param_count - 1
        return param_count, skiped

    def _get_body(self, a: int, b: int) -> str:
        '''тело web_ - поиск и замену делать тут'''
        return '\n'.join(self.lines_list[a:b])

    def _set_body(self, body: str, a: int, b: int) -> None:
        '''задать новое тело web_'''
        self.lines_list[a:b] = body.split('\n')

    def get_body(self, mx=2) -> str:
        '''тело web_ - поиск и замену делать тут'''
        if len(self.lines_list) > mx:
            return self._get_body(1, -1)
        else:
            return self._get_body(0, mx)

    def set_body(self, body: str, mx=2) -> None:
        '''задать новое тело web_'''
        if len(self.lines_list) > mx:
            return self._set_body(body, 1, -1)
        else:
            return self._set_body(body, 0, mx)


class WebSnapshot(WebAny):
    def __init__(self, parent_AWAL, lines_list: list, comments: str, transaction='', _type='', web_reg_save_param_list=None):
        super().__init__(parent_AWAL, lines_list, comments, transaction=transaction, _type=_type)

        if web_reg_save_param_list is None:
            self.web_reg_save_param_list = []
        else:
            self.web_reg_save_param_list = web_reg_save_param_list
            for wrsp in self.web_reg_save_param_list:
                wrsp.snapshot = self.snapshot
            print('\tweb_reg_save_param={} шт'.format(len(self.web_reg_save_param_list)))

    def to_str(self) -> str:
        '''весь текст web_'''
        _tr = self.parent_AWAL.websReport.stats_transaction_web(self)
        _out = self.parent_AWAL.websReport.stats_out_web(self.snapshot)
        _in = self.parent_AWAL.websReport.stats_in_web(self.snapshot)

        if any((_tr, _out, _in)):
            stat_string = '{t}{o}{i}'.format(t=_tr, o=_out, i=_in)
        else: stat_string = ''

        text = super().to_str()

        bad_wrsp = []
        for w in self.web_reg_save_param_list:
            if self.snapshot in self.parent_AWAL.websReport.param_statistic[w.name]['snapshots']:
                bad_wrsp.append(w.param)
        if bad_wrsp:
            text = '\t{c} WARNING: WrspInAndOutUsage: {lp}={p}\n{t}'.format(t=text, c=lr_param.LR_COMENT, p=bad_wrsp, lp=len(bad_wrsp))

        txt = '{wrsp}{stat_string}\n{text}'.format(stat_string=stat_string, text=text, wrsp=''.join(map(WebRegSaveParam.to_str, self.web_reg_save_param_list)))
        return txt.strip('\n')

    def get_body(self, a=1, b=-1) -> str:
        '''тело web_ - поиск и замену делать тут'''
        return super()._get_body(a, b)

    def set_body(self, body: str, a=1, b=-1) -> None:
        '''задать новое тело web_'''
        return super()._set_body(body, a, b)


class WebRegSaveParam(WebAny):
    def __init__(self, parent_AWAL, lines_list: list, comments: str, transaction='', _type='', parent_snapshot=None):
        self.parent_snapshot = parent_snapshot  # WebSnapshot
        super().__init__(parent_AWAL, lines_list, comments, transaction=transaction, _type=_type)
        if self.parent_snapshot is not None:
            self.snapshot = self.parent_snapshot.snapshot

        self.param = self._read_param()
        self.LB = ''
        self.RB = ''
        self.Ord = ''
        self.Search = ''

        print('\tparam:{}'.format(self.param))

    def _read_param(self, param='') -> str:
        try:
            if lr_param.wrsp_start in self.comments:
                param = self.comments.split(lr_param.wrsp_start, 1)[1].split(lr_param.wrsp_end, 1)[0]
            elif 'PARAM["' in self.comments:
                param = self.comments.split('PARAM["', 1)[1].split(lr_param.wrsp_end, 1)[0]

            if not param:  # если param создавал LoadRunner
                srch = '{%s} = "' % self.name
                for line in self.comments.split('\n'):
                    if srch in line:
                        line_list = line.split(srch, 1)
                        if len(line_list) > 1:
                            line_list = line_list[1].rsplit('"', 1)
                            if len(line_list) > 1:
                                param = line_list[0]
        except Exception as ex:
            lr_log.Logger.debug('найти исходное имя param из {t}.\n{w}\n{e}\n{cm}'.format(e=ex, w=self.name, t=self.type, cm=self.comments))

        return param

    def to_str(self) -> str:
        '''web_reg_save_param текст + //lr:Usage коментарий'''
        rep = self.parent_AWAL.websReport.param_statistic[self.name]
        comments = self.comments

        if not rep['param_count']:
            comments += '\n{c} WARNING: NoWebRegSaveParamUsage?'.format(c=lr_param.LR_COMENT)
        elif self.snapshot >= min(filter(bool, rep['snapshots'])):
            comments += '\n{c} WARNING: WrspInAndOutUsage wrsp.snapshot >= usage.snapshot'.format(c=lr_param.LR_COMENT)

        txt = '{usage_string}{coment_text}\n{snap_text}'.format(usage_string=self.usage_string(), coment_text=comments, snap_text='\n'.join(self.lines_list))
        return '\n{}\n'.format(txt.strip('\n'))

    def usage_string(self) -> str:
        rep = self.parent_AWAL.websReport
        ps = rep.param_statistic[self.name]
        wt = rep.web_transaction[self.transaction]
        t_snap = (wt['minmax_snapshots'] if self.transaction else '')
        tn = sorted(ps['transaction_names'], key=rep.web_transaction_sorted.index)
        s = '{c} ({w_transac}: {t_snap}) -> Param:{p_all} | Snapshots:{snap} | Transactions={len_transac}:{transac_names}'.format(
            wrsp_name=self.transaction, p_all=ps['param_count'], snap=ps['minmax_snapshots'], c=lr_param.LR_COMENT, len_transac=ps['transaction_count'], transac_names=tn, w_transac=self.transaction, t_snap=t_snap)
        return s


class ActionWebsAndLines:
    def __init__(self, action):
        self.action = action
        self.webs_and_lines = []
        self.websReport = WebReport(parent_AWAL=self)
        self.transactions = Transactions(self)

    def get_web_all(self) -> iter((WebAny,)):
        for web in self.webs_and_lines:
            if isinstance(web, str):
                continue
            yield web

    def get_web_by(self, **kwargs) -> iter((WebAny,)):
        source = kwargs.pop('__source', None)
        if source is None:
            source = self.get_web_all()

        attrs = kwargs.items()
        for web in source:
            if all((getattr(web, attr) == value) for (attr, value) in attrs):
                yield web

    def get_web_snapshot_all(self) -> iter((WebSnapshot,)):
        for web in self.get_web_all():
            if web.snapshot:
                yield web

    def get_web_snapshot_by(self, **kwargs) -> iter((WebSnapshot,)):
        for web in self.get_web_by(__source=self.get_web_snapshot_all(), **kwargs):
            yield web

    def get_web_reg_save_param_all(self) -> iter((WebRegSaveParam,)):
        for web in self.get_web_snapshot_all():
            yield from web.web_reg_save_param_list

    def get_web_reg_save_param_by(self, **kwargs) -> iter((WebRegSaveParam,)):
        for web_wrsp in self.get_web_by(__source=self.get_web_reg_save_param_all(), **kwargs):
            yield web_wrsp

    def replace_bodys(self, replace_list: [(str, str), ]) -> None:
        '''заменить группу param, во всех web_ body'''
        web_actions = tuple(self.get_web_snapshot_all())
        lr_log.Logger.trace('web_actions={lw}, replace_list={lrl}:{rl}'.format(rl=replace_list, lrl=len(replace_list), lw=len(web_actions)))

        for web_ in web_actions:
            body = web_.get_body()

            for search, replace in replace_list:
                body = body_replace(body, search, replace)

            web_.set_body(body)

    def add_to_text_list(self, element: (str or object)) -> None:
        '''объединять строки, идущие подряд'''
        tl = self.webs_and_lines[-1]
        if isinstance(element, str) and isinstance(tl, str):
            self.webs_and_lines[-1] = '{tl}\n{et}'.format(tl=tl, et=element)
        else:
            self.webs_and_lines.append(element)

    @lr_log.exec_time
    def set_text_list(self, text: str, websReport=True) -> None:
        '''создать все web_action объекты'''
        with self.action.block():
            self.transactions = Transactions(self)
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
                w_type = read_web_type(line)

                if strip_line.endswith(lr_param._block_endswith) or strip_line.endswith('('):  # тело запроса

                    for web_line in iter_lines:
                        line_num += 1
                        web_list.append(web_line)
                        if any(map(web_line.rstrip().endswith, lw_end)):
                            break

                    transaction = self.transactions._current()

                    if w_type.startswith('web_reg_save_param'):
                        web_ = WebRegSaveParam(self, web_list, comments, transaction=transaction, _type=w_type)
                        reg_param_list.append(web_)

                    else:
                        if (len(web_list) < 3) or (not any(lr_param.Snap1 in ln for ln in web_list)):
                            web_ = WebAny(self, web_list, comments, transaction=transaction, _type=w_type)
                            self.add_to_text_list(web_)

                        else:
                            web_ = WebSnapshot(self, web_list, comments, transaction=transaction, _type=w_type)
                            web_.web_reg_save_param_list = reg_param_list
                            reg_param_list = []
                            self.add_to_text_list(web_)

                    comments = ''
                    continue

                elif any(map(strip_line.endswith, lw_end)):  # однострочные web_
                    web_ = WebAny(self, web_list, comments, transaction=self.transactions._current(), _type=w_type)
                    self.add_to_text_list(web_)
                    comments = ''
                    continue

                else:
                    lr_log.Logger.critical('вероятно ошибка распознавания\n{line}\n{lwl}\n{web_list}'.format(line=line, lwl=len(web_list), web_list=web_list))
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
            lr_log.Logger.critical('Ненайден web_* запрос, которому принадлежат web_reg_save_param:\n{}'.format([w.name for w in reg_param_list]))
            self.add_to_text_list('\n// ERROR web_reg_save_param !\n{}'.format('\n\n'.join(map(WebRegSaveParam.to_str, reg_param_list))))

    def set_transaction_name(self, strip_line: str, _s='"') -> (str or None):
        '''проверить линию, сохранить имя transaction'''
        if strip_line.startswith('lr_'):
            if strip_line.startswith(start_transaction):
                transac = strip_line.split(_s, 2)
                transac = transac[1]
                self.transactions.start_transaction(transac)

            elif strip_line.startswith(end_transaction):
                transac = strip_line.split(_s, 2)
                transac = transac[1]
                self.transactions.stop_transaction(transac)

    def web_reg_save_param_insert(self, wrsp_dict: dict, wrsp='') -> None:
        '''вставить web_reg_save_param'''
        inf = wrsp_dict['inf_nums'][0]
        web_ = next(self.get_web_snapshot_by(snapshot=inf))
        if not wrsp:
            wrsp = lr_param.web_reg_save_param.format(**wrsp_dict)

        ws = wrsp.split(lr_param.wrsp_lr_start, 1)
        if len(ws) == 2:
            comments, w_lines = ws
            w_lines = lr_param.wrsp_lr_start + w_lines
        else:
            comments = ''
            w_lines = wrsp

        w_lines = w_lines.split('\n')
        wrsp_web_ = WebRegSaveParam(self, w_lines, comments, transaction=web_.transaction, parent_snapshot=web_)
        web_.web_reg_save_param_list.append(wrsp_web_)

    def web_reg_save_param_remove(self, name: str, keys=('param', 'name')) -> str:
        '''удалить web_reg_save_param'''
        _param = ''

        for web in self.get_web_snapshot_all():
            for wrsp_web in list(web.web_reg_save_param_list):
                if any((getattr(wrsp_web, k) == name) for k in keys):
                    web.web_reg_save_param_list.remove(wrsp_web)
                    _param = wrsp_web.param
                    wn = lr_param.param_bounds_setter(wrsp_web.name)
                    self.replace_bodys([(wn, _param), ])  # удалить из всех web
                    break

        return _param

    @lr_log.exec_time
    def to_str(self, websReport=False) -> str:
        '''весь action текст как строка'''
        if websReport:
            self.websReport.create()

        def webs_and_lines(_bool=True) -> str:
            for line in self.webs_and_lines:
                is_str = isinstance(line, str)
                if is_str != _bool:
                    yield '\n'  # смена str/WEB_

                if is_str:
                    yield '\n{}'.format(line.strip('\n'))
                elif isinstance(line, WebSnapshot):
                    yield '\n\n{}\n'.format(line.to_str())
                else:
                    yield '\n{}'.format(line.to_str())

                _bool = is_str

        return ''.join(webs_and_lines()).strip()


is_ascii = set(string.printable).__contains__


class WebReport:
    def __init__(self, parent_AWAL: ActionWebsAndLines):
        self.parent_AWAL = parent_AWAL

        self.wrsp_and_param_names = {}  # {'P_6046_1__z_k62_0': 'z_k620', ...}
        self.param_statistic = {}  # {'P_3396_4_Menupopup__a_FFXc_0__id_mainMenu': {'param_count': 2, 'snapshots': [874, 875], 'snapshots_count': 2, 'minmax_snapshots': '[t874:t875]=2', 'transaction_names': {'logout'}, 'transaction_count': 1}}
        self.web_snapshot_param_in_count = {}  # {1: {'P_6046_1__z_k62_0': 3}, 2: ...}
        self.web_transaction = {}  # {'close_document': {'snapshots': [847, 848, ...], 'minmax_snapshots': '[t847:t857]=11'}, 'logout': {'snapshots': [872, 873, 874, 875], 'minmax_snapshots': '[t872:t875]=4'}}
        self.web_transaction_sorted = []  # ['close_document', 'logout', ]
        self.rus_webs = {}  # web с не ASCII символами {snap: symb_count} {103: 17, 250: 14, 644: 22}
        self.google_webs = {}  # вероятно лишние web {228: {'google.com': 1}}
        self.bad_wrsp_in_usage = []  # ['P_6046_1__z_k62_0', ...]
        self._wrsp = {}  # {'P_6046_1__z_k62_0': <lr_lib.web_.WebRegSaveParam object at 0x09252770>, ...}
        self.all_in_one = {}

    @lr_log.exec_time
    def create(self):
        self.wrsp_and_param_names = {}
        self.param_statistic = {}
        self.web_snapshot_param_in_count = {}
        self.web_transaction = {}
        self.web_transaction_sorted = []
        self.rus_webs = {}
        self.google_webs = {}
        self.bad_wrsp_in_usage = []

        self._wrsp = {}
        self.all_in_one = copy.deepcopy(self.parent_AWAL.transactions.sub_transaction)
        wrsp_all = tuple(self.parent_AWAL.get_web_reg_save_param_all())
        tk_text = self.parent_AWAL.action.tk_text

        for wr in wrsp_all:
            web_add_highlight(wr, tk_text)

            self.wrsp_and_param_names[wr.name] = wr.param
            self._wrsp[wr.name] = wr

        self.param_statistic = {}
        for k in self.wrsp_and_param_names:
            self.param_statistic[k] = {
                'param_count': 0,
                'snapshots': [],
                'snapshots_count': 0,
                'minmax_snapshots': '',
                'transaction_names': [],
                'transaction_count': 0,
            }

        for web in self.parent_AWAL.get_web_all():
            web_add_highlight(web, tk_text)

            snapshot = web.snapshot
            transaction = web.transaction

            if isinstance(web, WebSnapshot):  # проставить родителя wrsp объекта
                for wrsp in web.web_reg_save_param_list:
                    wrsp.snapshot = web.snapshot
                    wrsp.parent_snapshot = web

            if transaction not in self.web_transaction_sorted:
                self.web_transaction_sorted.append(transaction)

            for line in web.lines_list:
                no_ascii = len(line) - len(tuple(filter(is_ascii, line)))
                if no_ascii:
                    self.rus_webs[snapshot] = no_ascii

                for k in defaults.DENY_WEB_:
                    count = line.count(k)
                    if count:
                        self.google_webs.setdefault(snapshot, {})[k] = count

            if snapshot < 1:
                continue

            try:
                self.web_transaction[transaction]['snapshots'].append(snapshot)
            except (AttributeError, KeyError):
                self.web_transaction.setdefault(transaction, {})['snapshots'] = [snapshot]

            body = web.get_body()
            self.web_snapshot_param_in_count[snapshot] = in_count = {}

            for wr_name in self.wrsp_and_param_names:
                param_in_count = body.count(lr_param.param_bounds_setter(wr_name))
                if param_in_count:
                    in_count[wr_name] = param_in_count
                    statistic = self.param_statistic[wr_name]
                    statistic['param_count'] += param_in_count
                    statistic['snapshots'].append(snapshot)
                    statistic['transaction_names'].append(transaction)

        for k in self.wrsp_and_param_names:
            psk = self.param_statistic[k]
            psk['transaction_names'] = sorted(set(psk['transaction_names']), key=self.web_transaction_sorted.index)

        for wr_name in self.param_statistic:
            statistic = self.param_statistic[wr_name]
            statistic['snapshots_count'] = len(statistic['snapshots'])
            statistic['transaction_count'] = len(statistic['transaction_names'])
            statistic['minmax_snapshots'] = snapshot_diapason_string(statistic['snapshots'])

            if (not statistic['param_count']) or (self._wrsp[wr_name].snapshot in statistic['snapshots']):
                self.bad_wrsp_in_usage.append(wr_name)

        for dt in self.web_transaction.values():
            dt['minmax_snapshots'] = snapshot_diapason_string(dt['snapshots'])

        get_web = lambda sn: self.parent_AWAL.get_web_by(snapshot=sn)
        stats = lambda w: {k: v for (k, v) in self.param_statistic[w.name].items() if k not in ('snapshots', 'transaction_names', 'snapshots_count', )}
        for t in self.web_transaction:
            dtt = next(get_sub_transaction_dt(t, self.all_in_one))
            dtt.update(copy.deepcopy(self.web_transaction[t]))
            dtt['snapshots'] = {s: {w.name: {'param': w.param, 'stats': stats(w)} for w in next(get_web(s)).web_reg_save_param_list} for s in dtt['snapshots']}

        self.checker_warn()

        # highlight
        for wr in wrsp_all:
            if not all(self.param_statistic[wr.name].values()):
                lr_widj.highlight_mode(tk_text, wr.name, option='background', color='yellow')

        for t in self.parent_AWAL.transactions.names:
            lr_widj.highlight_mode(tk_text, t, option='foreground', color='darkslategrey')

    def stats_in_web(self, snapshot: int) -> str:
        params_in = self.web_snapshot_param_in_count[snapshot]
        if not params_in:
            return ''

        def get(wr_name, format='{param}(P:{p_in}/{p_all}|S:{snap}|T:{transac})'.format):
            ps = self.param_statistic[wr_name]
            s = format(param=self.wrsp_and_param_names[wr_name], p_in=params_in[wr_name], p_all=ps['param_count'], snap=ps['minmax_snapshots'], transac=ps['transaction_count'])
            return s

        statistic = (get(wr_name) for wr_name in sorted(params_in, key=len))
        s = '\n\t{c} IN({i})<-[{ui}]: {s}'.format(s=', '.join(statistic), c=lr_param.LR_COMENT, i=sum(params_in[w] for w in params_in), ui=len(params_in))
        return s

    def stats_out_web(self, snapshot: int) -> str:
        web = next(self.parent_AWAL.get_web_snapshot_by(snapshot=snapshot))

        if not web.web_reg_save_param_list:
            return ''

        statistic = []
        for wr in sorted(web.web_reg_save_param_list, key=lambda w: len(w.param)):
            ps = self.param_statistic[wr.name]
            pss = '{p}(P:{p_all}|S:{snap}|T:{transac})'.format(p=wr.param, p_all=ps['param_count'], snap=ps['minmax_snapshots'], transac=ps['transaction_count'])
            statistic.append(pss)

        return '\n\t{c} OUT({n})-> {s}'.format(s=', '.join(statistic), c=lr_param.LR_COMENT, n=len(statistic))

    def stats_transaction_web(self, web) -> str:
        transaction = web.transaction
        mm = self.web_transaction[transaction]['minmax_snapshots']
        if isinstance(web, WebSnapshot):
            m = self.web_transaction[transaction]['snapshots'].index(web.snapshot) + 1
            mm = '{m}/{mm}'.format(mm=mm, m=m)

        if transaction:
            t_comment = '\n\t{c} "{t}"({mm})'.format(c=lr_param.LR_COMENT, t=transaction, mm=mm)
            return t_comment
        else:
            return ''

    def checker_warn(self):
        for t in self.parent_AWAL.transactions.names:
            if t not in self.web_transaction:
                lr_log.Logger.debug('Пустая транзакция "{}"'.format(t))
            if t not in self.parent_AWAL.transactions.start_stop['start']:
                lr_log.Logger.warning('Отсутствует транзакция start_transaction("{}")'.format(t))
            if t not in self.parent_AWAL.transactions.start_stop['stop']:
                lr_log.Logger.warning('Отсутствует транзакция stop_transaction("{}")'.format(t))


def snapshot_diapason_string(infs: [int, ]) -> str:
    '''если inf min=max указать только одно'''
    if infs:
        min_inf = min(infs)
        max_inf = max(infs)
    else:
        min_inf = max_inf = 0

    if min_inf == max_inf:
        diapason = '{count}=[{min_inf}]'.format(min_inf=min_inf, count=len(infs))
    else:
        diapason = '{count}=[{min_inf}:{max_inf}]'.format(min_inf=min_inf, max_inf=max_inf, count=len(infs))

    return diapason


class Transactions:
    '''объект хранящий иерархию "транзакций" в action.c'''
    _no_transaction_name = 'NoTransaction_'

    def __init__(self, parent):
        self.parent = parent
        self.names = []  # порядок следования имен
        self.start_stop = dict(start=[], stop=[])
        self.sub_transaction = collections.OrderedDict()  # иерархия
        self._no_transaction_num = 0
        self.__is_no_transaction_name = ''

    def __no_transaction_name(self) -> str:
        '''если нет имени транзакции'''
        self._no_transaction_num += 1
        name = '{a}{u}'.format(a=self._no_transaction_name, u=self._no_transaction_num)
        self.start_transaction(name)
        self.__is_no_transaction_name = name
        return name

    def _current(self) -> str:
        '''для определения где находится web, во время разбора action.c текста'''
        for n in reversed(self.names):
            if n not in self.start_stop['stop']:
                return n
        return self.__no_transaction_name()

    def start_transaction(self, transaction: str) -> None:
        if self.__is_no_transaction_name:
            self.stop_transaction(self.__is_no_transaction_name)
            self.__is_no_transaction_name = ''

        if transaction in self.names:
            lr_log.Logger.error('транзакция: start после start\nПовторное использование start_transaction("{}")'.format(transaction))
        else:
            dt = self.sub_transaction
            for t in self.names:
                if t not in self.start_stop['stop']:
                    dt = dt[t]
            dt[transaction] = collections.OrderedDict()

            self.names.append(transaction)
            self.start_stop['start'].append(transaction)

    def stop_transaction(self, transaction: str) -> None:
        if transaction not in self.names:
            lr_log.Logger.error('транзакция: stop перед start\nОтсутствует start_transaction("{}")'.format(transaction))
        else:
            self.start_stop['stop'].append(transaction)


def get_sub_transaction_dt(transaction, obj) -> dict:
    '''словарь транзакции, внутри вложенного словаря Transactions.sub_transaction'''
    if isinstance(obj, collections.OrderedDict):
        if transaction in obj:
            yield obj[transaction]
        else:
            for t in obj:
                yield from get_sub_transaction_dt(transaction, obj[t])


def web_add_highlight(web_, tk_text) -> None:
    '''подсветить web_'''
    hm = lr_widj.highlight_mode
    hm(tk_text, web_.type)

    for line in web_.comments.split('\n'):
        hm(tk_text, line.strip())

    if isinstance(web_, WebRegSaveParam):
        hm(tk_text, '{}'.format(web_.name[:6]), option='background', color=defaults.wrsp_color1)
        hm(tk_text, web_.name[6:], option='foreground', color=defaults.wrsp_color2)
        hm(tk_text, web_.param, option='foreground', color=defaults.wrsp_color2)
        for line in web_.lines_list[1:]:
            hm(tk_text, line.strip())
    else:
        hm(tk_text, web_.name)