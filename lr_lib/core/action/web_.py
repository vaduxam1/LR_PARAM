# -*- coding: UTF-8 -*-
# классы lr web_ запросов

import contextlib

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.core.etc.lbrb_checker as lr_lbrb_checker
import lr_lib.gui.widj.dialog as lr_dialog


def read_web_type(first_line: str, s1='("', s2='(') -> str:
    '''найти тип web_'''
    s = (s1 if (s1 in first_line) else s2)
    t = first_line.split(s, 1)
    if len(t) == 2:
        return t[0].strip()
    else:
        raise UserWarning('{l} не содержит {s}'.format(l=first_line, s=[s1, s2]))


def _body_replace(body_split, len_body_split, search, replace) -> iter((str, )):
    '''замена search в body'''
    yield body_split[0]

    for indx in range(1, len_body_split):
        left = body_split[indx - 1]
        right = body_split[indx]
        if lr_lbrb_checker.check_bound_lb_rb(left, right):
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
    '''любые web_'''
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

        # print('\n{w}({n}):\n\tSnap={sn}, lines={l}, symb={s}, {t}'.format(w=self.type, n=self.name, l=len(self.lines_list), s=len(tuple(itertools.chain(*self.lines_list))), sn=self.snapshot, t=self.transaction))

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

        if lr_vars.VarWebStatsWarn.get():
            if self.snapshot in self.parent_AWAL.websReport.rus_webs:
                comments += '\n\t{} WARNING: NO ASCII Symbols(rus?)'.format(lr_param.LR_COMENT)
            if (len(self.lines_list) > 2) and (not self.snapshot):
                comments += '\n\t{} WARNING: no "Snapshot=t.inf" (del?)'.format(lr_param.LR_COMENT)

        text = '{coment}\n{snap_text}'.format(coment=comments, snap_text='\n'.join(self.lines_list)).strip('\n')
        return text

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
        buttons = (ys, yta, no, nta, rais) = ('Да', 'Да, для Всех', 'Нет', 'Нет, для Всех', 'Преврать',)
        dk = (nta, yta, rais)

        if ask_dict and (a in ask_dict for a in dk):
            if ask_dict.get(rais):
                raise UserWarning('Прервано!\n{}'.format('\n\t###\n'.join((param, replace, left, right, ask_dict))))
            return ask_dict.get(nta) or ask_dict.get(yta)

        t2 = 'хотя строка и содержит param-имя "{p}"\nоно является частью другого, более длинного имени:\nЗаменить на "{r}" ?'.format(
            p=param, r=replace)
        t1 = 'заменяемая строка:\n{prev}{p}{part}'.format(
            prev=left[-lr_vars.AskLbRbMaxLen:].rsplit('\n', 1)[-1].lstrip(), p=param,
            part=right[:lr_vars.AskLbRbMaxLen].split('\n', 1)[0].rstrip())
        y = lr_dialog.YesNoCancel(buttons=buttons, text_before=t1, text_after=t2, title='автозамена "{s}" на "{r}"'.format(
            s=param, r=replace), parent=self.parent_AWAL.action, default_key=nta, focus=self.parent_AWAL.action.tk_text)
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
            if lr_lbrb_checker.check_bound_lb_rb(left, right) or (ask and self.ask_replace(param, replace, left, right, ask_dict)):
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
    '''web со snapshot > 0, те содержащие файлы ответов'''
    def __init__(self, parent_AWAL, lines_list: list, comments: str, transaction='', _type='', web_reg_save_param_list=None):
        super().__init__(parent_AWAL, lines_list, comments, transaction=transaction, _type=_type)

        if web_reg_save_param_list is None:
            self.web_reg_save_param_list = []
        else:
            self.web_reg_save_param_list = web_reg_save_param_list
            for wrsp in self.web_reg_save_param_list:
                wrsp.snapshot = self.snapshot
            # print('\tweb_reg_save_param={} шт'.format(len(self.web_reg_save_param_list)))

    def to_str(self) -> str:
        '''весь текст web_'''
        if lr_vars.VarWebStatsTransac.get():
            _tr = self.parent_AWAL.websReport.stats_transaction_web(self)
        else:
            _tr = ''

        if lr_vars.VarWebStatsOut.get():
            _out = self.parent_AWAL.websReport.stats_out_web(self.snapshot)
        else:
            _out = ''

        if lr_vars.VarWebStatsIn.get():
            _in = self.parent_AWAL.websReport.stats_in_web(self.snapshot)
        else:
            _in = ''

        if any((_tr, _out, _in)):
            stat_string = '{t}{o}{i}'.format(t=_tr, o=_out, i=_in)
        else:
            stat_string = ''

        text = super().to_str()

        if lr_vars.VarWebStatsWarn.get():
            bad_wrsp = []
            for w in self.web_reg_save_param_list:
                if self.snapshot in self.parent_AWAL.websReport.param_statistic[w.name]['snapshots']:
                    bad_wrsp.append(w.param)
            if bad_wrsp:
                text = '\t{c} WARNING: WrspInAndOutUsage: {lp}={p}\n{t}'.format(
                    t=text, c=lr_param.LR_COMENT, p=bad_wrsp, lp=len(bad_wrsp))

        wrsps = ''.join(map(WebRegSaveParam.to_str, self.web_reg_save_param_list))
        txt = '{wrsp}{stat_string}\n{text}'.format(stat_string=stat_string, text=text, wrsp=wrsps).strip('\n')
        return txt

    def get_body(self, a=1, b=-1) -> str:
        '''тело web_ - поиск и замену делать тут'''
        return super()._get_body(a, b)

    def set_body(self, body: str, a=1, b=-1) -> None:
        '''задать новое тело web_'''
        return super()._set_body(body, a, b)


class WebRegSaveParam(WebAny):
    '''web web_reg_save_param*'''
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

        # print('\tparam:{}'.format(self.param))

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
            lr_vars.Logger.debug('найти исходное имя param из {t}.\n{w}\n{e}\n{cm}'.format(
                e=ex, w=self.name, t=self.type, cm=self.comments))

        return param

    def to_str(self) -> str:
        '''web_reg_save_param текст + //lr:Usage коментарий'''
        comments = self.comments

        if lr_vars.VarWebStatsWarn.get():
            rep = self.parent_AWAL.websReport.param_statistic[self.name]
            if not rep['param_count']:
                comments += '\n{c} WARNING: NoWebRegSaveParamUsage?'.format(c=lr_param.LR_COMENT)
            elif self.snapshot >= min(filter(bool, rep['snapshots'])):
                comments += '\n{c} WARNING: WrspInAndOutUsage wrsp.snapshot >= usage.snapshot'.format(c=lr_param.LR_COMENT)

        if lr_vars.VarWRSPStatsTransac.get():
            usage_string = self.usage_string()
        else:
            usage_string = ''

        txt = '{usage_string}{coment_text}\n{snap_text}'.format(usage_string=usage_string, coment_text=comments,
                                                                snap_text='\n'.join(self.lines_list))
        return '\n{}\n'.format(txt.strip('\n'))

    def usage_string(self) -> str:
        rep = self.parent_AWAL.websReport
        ps = rep.param_statistic[self.name]
        wt = rep.web_transaction[self.transaction]
        t_snap = (wt['minmax_snapshots'] if self.transaction else '')

        if lr_vars.VarWRSPStatsTransacNames.get():
            tn = sorted(ps['transaction_names'], key=rep.web_transaction_sorted.index)
        else:
            tn = ''

        s = '{c} ({w_transac}: {t_snap}) -> Param:{p_all} | Snapshots:{snap} | Transactions={len_transac}:{transac_names}'.format(
            wrsp_name=self.transaction, p_all=ps['param_count'], snap=ps['minmax_snapshots'], c=lr_param.LR_COMENT,
            len_transac=ps['transaction_count'], transac_names=tn, w_transac=self.transaction, t_snap=t_snap)
        return s
