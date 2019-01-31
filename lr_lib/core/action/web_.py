# -*- coding: UTF-8 -*-
# классы lr web_ запросов

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars as lr_vars


class Snapshot:
    """
    Снапшоты могут располагатся не по порядку, например пользователь перенес снапшот из начала скрипта, в середину.
    Т.о. необходимо использовать два номера:
        1) оригинальный номер inf - для связи с файлами ответов
        2) новый порядковый номер - для определения порядка снапшотов в скрипте
    """
    SERIAL = 0  # порядковый номер Snapshot, для автонумеровки

    def __init__(self, inf: int, serial=None):
        # порядковый Snapshot номер
        if serial is None:
            Snapshot.SERIAL += 1
            self.serial = Snapshot.SERIAL
        else:  # вручную, например для замены
            self.serial = serial

        # оригинальный Snapshot номер
        self.inf = inf
        return


def read_web_type(first_line: str, s1='("', s2='(') -> str:
    """
    найти тип web_
    """
    s = (s1 if (s1 in first_line) else s2)
    t = first_line.split(s, 1)
    if len(t) == 2:
        s = t[0].strip()
        return s

    u = '{fl} не содержит {s}'.format(fl=first_line, s=[s1, s2])
    raise UserWarning(u)


def _body_replace(body_split: [str, ], len_body_split: int, search: str, replace: str, is_wrsp=True) -> iter((str,)):
    """
    замена search в body
    """
    fst = body_split[0]
    yield fst

    if is_wrsp:
        replace = lr_lib.core.wrsp.param.param_bounds_setter(replace)

    for indx in range(1, len_body_split):
        left = body_split[indx - 1]
        right = body_split[indx]

        if lr_lib.core.etc.lbrb_checker.check_bound_lb_rb(left, right):
            s = (replace + right)
        else:
            s = (search + right)

        yield s
        continue
    return


def body_replace(body: str, search: str, replace: str, is_wrsp=True) -> str:
    """
    замена search в body
    """
    body_split = body.split(search)
    len_body_split = len(body_split)

    if len_body_split > 1:
        b = _body_replace(body_split, len_body_split, search, replace, is_wrsp=is_wrsp)
        body = ''.join(b)
    return body


def bodys_replace(replace_args: ({int: str}, [(str, str), ]), is_wrsp=True) -> [str, ]:
    """
    замена param's в body's
    """
    (body_portion, replace_list) = replace_args
    for i in body_portion:
        for (search, replace) in replace_list:
            pi = body_portion[i]
            bp = body_replace(pi, search, replace, is_wrsp=is_wrsp)
            body_portion[i] = bp
            continue
        continue
    return body_portion


class WebAny:
    """
    любые web_
    """
    count = 0

    def __init__(
            self,
            parent_: 'lr_lib.core.action.main_awal.ActionWebsAndLines',
            lines_list: list,
            comments: str,
            transaction: str,
            _type='',
    ):
        self.ActionWebsAndLines = parent_
        self.tk_text = self.ActionWebsAndLines.action.tk_text
        self.lines_list = lines_list

        WebAny.count += 1
        self.unique_num = WebAny.count

        self.transaction = transaction
        t = self.lines_list[0]
        self.type = _type or read_web_type(t)
        self.name = self._read_name()

        snapshot = self._read_snapshot()
        self.snapshot = Snapshot(snapshot)

        self.comments = comments.lstrip('\n').rstrip()
        if self.comments:
            self.comments = '\n{}'.format(self.comments)

        # print('\n{w}({n}):\n\tSnap={sn}, lines={l}, symb={s}, {t}'.format(w=self.type, n=self.name, l=len(self.lines_list), s=len(tuple(itertools.chain(*self.lines_list))), sn=self.snapshot, t=self.transaction))
        return

    def _read_snapshot(self) -> int:
        """
        Snapshot inf номер
        """
        try:
            for line in self.lines_list[1:-1]:
                strip = line.strip()
                if strip.startswith(lr_lib.core.wrsp.param.Snap1) and strip.endswith(lr_lib.core.wrsp.param.Snap2):
                    inf_num = line.split(lr_lib.core.wrsp.param.Snap1, 1)
                    inf_num = inf_num[-1]
                    inf_num = inf_num.rsplit(lr_lib.core.wrsp.param.Snap2, 1)
                    inf_num = inf_num[0]
                    assert all(map(str.isnumeric, inf_num))
                    inf_num = int(inf_num)
                    return inf_num
                continue
        except Exception as ex:
            pass
        return 0

    def to_str(self, _all_stat=False) -> str:
        """
        весь текст web_
        """
        comments = self.comments  # str copy

        if lr_vars.VarWebStatsWarn.get() or _all_stat:
            if self.snapshot.inf in self.ActionWebsAndLines.websReport.rus_webs:
                s = '\n\t{} WARNING: NO ASCII Symbols(rus?)'.format(lr_lib.core.wrsp.param.LR_COMENT)
                comments += s
            if (len(self.lines_list) > 2) and (not self.snapshot.inf):
                s = '\n\t{} WARNING: no "Snapshot=t.inf" (del?)'.format(lr_lib.core.wrsp.param.LR_COMENT)
                comments += s

        warn = self.check_for_warnings()
        st = '\n'.join(self.lines_list)

        t = '{warn}\n{coment}\n{snap_text}'
        text = t.format(coment=comments, snap_text=st, warn=warn).strip('\n')
        return text

    def _read_name(self, name='') -> str:
        """
        ParamName
        """
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
                    name = sline[1]
                    name = name.split('"', 1)[0]
                    break
                continue

        return name

    def ask_replace(
            self,
            param: str,
            replace: str,
            left: str,
            right: str,
            ask_dict: dict,
    ) -> bool:
        """
        спросить о замене param
        """
        buttons = (ys, yta, no, nta, rais) = ('Да', 'Да, для Всех', 'Нет', 'Нет, для Всех', 'Преврать',)
        dk = (nta, yta, rais)

        if ask_dict and (a in ask_dict for a in dk):
            if ask_dict.get(rais):
                e = 'Прервано!\n{}'.format('\n\t###\n'.join((param, replace, left, right, ask_dict)))
                raise UserWarning(e)
            r = (ask_dict.get(nta) or ask_dict.get(yta))
            return r

        t2 = 'хотя строка и содержит param-имя "{p}"\nоно является частью другого, более длинного имени:\n' \
             'Заменить на "{r}" ?'.format(p=param, r=replace)
        t1 = 'заменяемая строка:\n{prev}{p}{part}'.format(
            prev=left[-lr_vars.AskLbRbMaxLen:].rsplit('\n', 1)[-1].lstrip(),
            p=param,
            part=right[:lr_vars.AskLbRbMaxLen].split('\n', 1)[0].rstrip(),
        )
        y = lr_lib.gui.widj.dialog.YesNoCancel(
            buttons=buttons,
            text_before=t1,
            text_after=t2,
            title='автозамена "{s}" на "{r}"'.format(s=param, r=replace),
            parent=self.ActionWebsAndLines.action,
            default_key=nta,
            focus=self.ActionWebsAndLines.action.tk_text,
        )
        a = y.ask()

        if ask_dict and (a in dk):
            ask_dict[a] = True
        r = (a in (ys, yta))
        return r

    def param_find_replace(self, param: str, replace=None, ask_dict=None) -> (int, int):
        """
        поиск или замена
        """
        b = self.get_body()
        body_split = b.split(param)
        len_body_split = len(body_split)
        if not len_body_split:
            it = (0, 0)
            return it
        action = self.ActionWebsAndLines.action
        chunk_indxs = []

        def force_ask_replace(indx: int, left: str, right: str) -> None:
            """всегда спрашивать о замене"""
            bs = body_split[:indx]
            w = param.join(bs)
            action.search_in_action(word=w, hist=False)
            if self.ask_replace(param, replace, left, right, ask_dict):
                chunk_indxs.append(indx)
            return

        def normal_replace(indx: int, left: str, right: str, ask=(not action.no_var.get())) -> None:
            """спрашивать о замене только при необходимости"""
            ch1 = lr_lib.core.etc.lbrb_checker.check_bound_lb_rb(left, right)
            if ch1 or (ask and self.ask_replace(param, replace, left, right, ask_dict)):
                chunk_indxs.append(indx)
            return

        add_index = (force_ask_replace if action.force_ask_var.get() else normal_replace)
        for indx in range(1, len_body_split):
            left = body_split[indx - 1]
            right = body_split[indx]
            if left and right:
                add_index(indx, left, right)
            continue

        if chunk_indxs and replace:
            replace = lr_lib.core.wrsp.param.param_bounds_setter(replace)
            contains = chunk_indxs.__contains__

            body_chunks = [body_split.pop(0), ]
            for (indx, body_chunk) in enumerate(body_split, start=1):
                splitter = (replace if contains(indx) else param)
                sc = (splitter + body_chunk)
                body_chunks.append(sc)
                continue

            b = ''.join(body_chunks)
            self.set_body(b)  # замена

        param_count = len(chunk_indxs)
        skiped = (len_body_split - param_count - 1)
        item = (param_count, skiped)
        return item

    def _get_body(self, a: int, b: int) -> str:
        """
        тело web_ - поиск и замену делать тут
        """
        la = self.lines_list[a:b]
        bs = '\n'.join(la)
        return bs

    def _set_body(self, body: str, a: int, b: int) -> None:
        """
        задать новое тело web_
        """
        bs = body.split('\n')
        self.lines_list[a:b] = bs
        return

    def get_body(self, mx=2) -> str:
        """
        тело web_ - поиск и замену делать тут
        """
        if len(self.lines_list) > mx:
            b = self._get_body(1, -1)
        else:
            b = self._get_body(0, mx)
        return b

    def set_body(self, body: str, mx=2) -> None:
        """
        задать новое тело web_
        """
        if len(self.lines_list) > mx:
            self._set_body(body, 1, -1)
        else:
            self._set_body(body, 0, mx)
        return

    def check_for_warnings(self) -> str:
        """
        wrsp могут быть неправильно заменены, например кем-то внучную или LR, в виде '{wrsp_name}_1'
        """
        warnings = []
        for w in self.ActionWebsAndLines.websReport.wrsp_and_param_names:
            wn = ('{%s}' % w)
            body = self.get_body()

            if wn in body:
                bs = body.split(wn)
                if len(body) == 2:
                    if not lr_lib.core.etc.lbrb_checker.check_bound_lb_rb(*bs):
                        s = 'Неправильное использование WRSP: {lb}{w}{rb}'
                        a = s.format(w=wn, lb=bs[0][-3:], rb=bs[1][:3])
                        warnings.append(a)
                else:
                    for sb in zip(bs, bs[1:]):
                        if not lr_lib.core.etc.lbrb_checker.check_bound_lb_rb(*sb):
                            s = 'Неправильное использование WRSP: {lb}{w}{rb}'
                            a = s.format(w=wn, lb=bs[0][-3:], rb=bs[1][:3])
                            warnings.append(a)
                        continue
            continue

        if warnings:
            s = '\n\t{c} WARNING: '.format(c=lr_lib.core.wrsp.param.LR_COMENT, )
            warn = s.join(warnings)
            warn = (s + warn)
        else:
            warn = ''
        return warn


class WebSnapshot(WebAny):
    """
    web со snapshot > 0, те содержащие файлы ответов
    """

    def __init__(
            self,
            parent_: 'lr_lib.core.action.main_awal.ActionWebsAndLines',
            lines_list: list,
            comments: str,
            transaction='',
            _type='',
            web_reg_save_param_list=None,
    ):
        super().__init__(parent_, lines_list, comments, transaction=transaction, _type=_type)

        if web_reg_save_param_list is None:
            self.web_reg_save_param_list = []
        else:
            self.web_reg_save_param_list = web_reg_save_param_list
            for wrsp in self.web_reg_save_param_list:
                wrsp.snapshot = self.snapshot
                continue
            # print('\tweb_reg_save_param={} шт'.format(len(self.web_reg_save_param_list)))
        return

    def to_str(self, _all_stat=False) -> str:
        """
        весь текст web_
        """
        if lr_vars.VarWebStatsTransac.get() or _all_stat:
            _tr = self.ActionWebsAndLines.websReport.stats_transaction_web(self)
        else:
            _tr = ''

        if lr_vars.VarWebStatsOut.get() or _all_stat:
            _out = self.ActionWebsAndLines.websReport.stats_out_web(self.snapshot.inf)
        else:
            _out = ''

        if lr_vars.VarWebStatsIn.get() or _all_stat:
            _in = self.ActionWebsAndLines.websReport.stats_in_web(self.snapshot.inf)
        else:
            _in = ''

        if any((_tr, _out, _in)):
            stat_string = '{t}{o}{i}'.format(t=_tr, o=_out, i=_in)
        else:
            stat_string = ''

        text = super().to_str(_all_stat=_all_stat)

        if lr_vars.VarWebStatsWarn.get() or _all_stat:
            bad_wrsp = []
            for w in self.web_reg_save_param_list:
                if self.snapshot.inf in self.ActionWebsAndLines.websReport.param_statistic[w.name]['snapshots']:
                    bad_wrsp.append(w.param)
                continue
            if bad_wrsp:
                t = '\t{c} WARNING: WrspInAndOutUsage: {lp}={p}\n{t}'
                text = t.format(t=text, c=lr_lib.core.wrsp.param.LR_COMENT, p=bad_wrsp, lp=len(bad_wrsp),)

        wrsps = ''.join(map(WebRegSaveParam.to_str, self.web_reg_save_param_list))
        txt = '{wrsp}{stat_string}\n{text}'.format(stat_string=stat_string, text=text, wrsp=wrsps).strip('\n')
        return txt

    def get_body(self, a=1, b=-1) -> str:
        """
        тело web_ - поиск и замену делать тут
        """
        s = super()._get_body(a, b)
        return s

    def set_body(self, body: str, a=1, b=-1) -> None:
        """
        задать новое тело web_
        """
        super()._set_body(body, a, b)
        return


class WebRegSaveParam(WebAny):
    """web web_reg_save_param*"""

    def __init__(
            self,
            parent_: 'lr_lib.core.action.main_awal.ActionWebsAndLines',
            lines_list: list,
            comments: str,
            transaction='',
            _type='',
            parent_snapshot=None,
    ):
        self.parent_snapshot = parent_snapshot  # WebSnapshot
        super().__init__(parent_, lines_list, comments, transaction=transaction, _type=_type)
        if self.parent_snapshot is not None:
            self.snapshot = self.parent_snapshot.snapshot

        self.param = self._read_param()
        # print('\tparam:{}'.format(self.param))
        return

    def _read_param(self, param='') -> str:
        """
        найти исходное имя param из wrsp
        """
        try:
            if lr_lib.core.wrsp.param.wrsp_start in self.comments:
                p = self.comments.split(lr_lib.core.wrsp.param.wrsp_start, 1)
                param = p[1].split(lr_lib.core.wrsp.param.wrsp_end, 1)[0]
            elif 'PARAM["' in self.comments:
                param = self.comments.split('PARAM["', 1)[1].split(lr_lib.core.wrsp.param.wrsp_end, 1)[0]

            if not param:  # если param создавал LoadRunner
                srch = '{%s} = "' % self.name
                for line in self.comments.split('\n'):
                    if srch in line:
                        line_list = line.split(srch, 1)
                        if len(line_list) > 1:
                            line_list = line_list[1].rsplit('"', 1)
                            if len(line_list) > 1:
                                param = line_list[0]
                    continue
        except Exception as ex:
            s = 'найти исходное имя param из {t}.\n{w}\n{e}\n{cm}'
            t = s.format(e=ex, w=self.name, t=self.type, cm=self.comments)
            lr_vars.Logger.debug(t)

        return param

    def to_str(self, _all_stat=False) -> str:
        """
        web_reg_save_param текст + //lr:Usage коментарий
        """
        comments = self.comments

        if lr_vars.VarWebStatsWarn.get() or _all_stat:
            rep = self.ActionWebsAndLines.websReport.param_statistic[self.name]
            if not rep['param_count']:
                s = '\n{c} WARNING: NoWebRegSaveParamUsage?'
                comments += s.format(c=lr_lib.core.wrsp.param.LR_COMENT)
            elif self.snapshot.inf >= min(filter(bool, rep['snapshots'])):
                s = '\n{c} WARNING: WrspInAndOutUsage wrsp.snapshot >= usage.snapshot'
                comments += s.format(c=lr_lib.core.wrsp.param.LR_COMENT)

        if lr_vars.VarWRSPStatsTransac.get() or _all_stat:
            usage_string = self.usage_string(_all_stat=_all_stat)
        else:
            usage_string = ''

        txt = '{usage_string}{coment_text}\n{snap_text}'.format(
            usage_string=usage_string, coment_text=comments, snap_text='\n'.join(self.lines_list),
        )
        ts = '\n{}\n'.format(txt.strip('\n'))
        return ts

    def usage_string(self, _all_stat=False) -> str:
        """
        статистика использования wrsp
        """
        rep = self.ActionWebsAndLines.websReport
        ps = rep.param_statistic[self.name]
        wt = rep.web_transaction[self.transaction]
        t_snap = (wt['minmax_snapshots'] if self.transaction else '')

        if lr_vars.VarWRSPStatsTransacNames.get() or _all_stat:
            tn = sorted(ps['transaction_names'], key=rep.web_transaction_sorted.index)
        else:
            tn = ''

        s = '{c} ({w_tr}: {t_snap}) -> Param:{p_all} | Snapshots:{snap} | Transactions={len_tr}:{tr_names}'.format(
            wrsp_name=self.transaction,
            p_all=ps['param_count'],
            snap=ps['minmax_snapshots'],
            c=lr_lib.core.wrsp.param.LR_COMENT,
            len_tr=ps['transaction_count'],
            tr_names=tn,
            w_tr=self.transaction,
            t_snap=t_snap,
        )
        return s
