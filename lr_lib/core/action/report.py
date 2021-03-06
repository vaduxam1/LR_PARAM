﻿# -*- coding: UTF-8 -*-
# action.c статистика

import collections
import copy
import string
from typing import Iterable, Tuple, List

import lr_lib
import lr_lib.core.action.web_
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.vars_param

is_ascii = set(string.printable)


class WebReport:
    """
    статистика использования web_reg_save_param
    """

    def __init__(self, parent_: 'lr_lib.core.action.main_awal.ActionWebsAndLines'):
        self.ActionWebsAndLines = parent_

        self.wrsp_and_param_names = collections.OrderedDict()  # {'P_6046_1__z_k62_0': 'z_k620', ...}
        self.param_statistic = collections.OrderedDict()  # {'P_3396_4_Menupopup__a_FFXc_0__id_mainMenu': {'param_count': 2, 'snapshots': [874, 875], 'snapshots_count': 2, 'minmax_snapshots': '[t874:t875]=2', 'transaction_names': {'logout'}, 'transaction_count': 1}}
        self.web_snapshot_param_in_count = collections.OrderedDict()  # {1: {'P_6046_1__z_k62_0': 3, }, 2: ...}
        self.web_transaction = collections.OrderedDict()  # {'close_document': {'snapshots': [847, 848, ...], 'minmax_snapshots': '[t847:t857]=11'}, 'logout': {'snapshots': [872, 873, 874, 875], 'minmax_snapshots': '[t872:t875]=4'}}
        self.web_transaction_sorted = []  # ['close_document', 'logout', ]
        self.rus_webs = collections.OrderedDict()  # web с не ASCII символами {snap: symb_count} {103: 17, 250: 14, 644: 22}
        self.google_webs = collections.OrderedDict()  # вероятно лишние web {228: {'google.com': 1}}
        self.bad_wrsp_in_usage = []  # ['P_6046_1__z_k62_0', ...]
        self._wrsp = collections.OrderedDict()  # {'P_6046_1__z_k62_0': <lr_lib.web_.WebRegSaveParam object at 0x09252770>, ...}
        self.all_in_one = collections.OrderedDict()
        return

    def create(self) -> None:
        """
        создать статистику
        """
        self.wrsp_and_param_names = {}
        self.param_statistic = {}
        self.web_snapshot_param_in_count = {}
        self.web_transaction = {}
        self.web_transaction_sorted = []
        self.rus_webs = {}
        self.google_webs = {}
        self.bad_wrsp_in_usage = []

        self._wrsp = {}
        self.all_in_one = copy.deepcopy(self.ActionWebsAndLines.transactions.sub_transaction)
        wrsp_all = tuple(self.ActionWebsAndLines.get_web_reg_save_param_all())

        for wr in wrsp_all:
            try:
                self.ActionWebsAndLines.action.tk_text.web_add_highlight(wr)
            except AttributeError:
                pass

            self.wrsp_and_param_names[wr.name] = wr.param
            self._wrsp[wr.name] = wr
            continue

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
            continue

        wal = self.ActionWebsAndLines.get_web_all()
        for web in wal:
            try:
                self.ActionWebsAndLines.action.tk_text.web_add_highlight(web)
            except AttributeError:
                pass

            snapshot = web.snapshot.inf
            transaction = web.transaction

            if isinstance(web, lr_lib.core.action.web_.WebSnapshot):  # проставить родителя wrsp объекта
                for wrsp in web.web_reg_save_param_list:
                    wrsp.snapshot = web.snapshot
                    wrsp.parent_snapshot = web
                    continue

            if transaction not in self.web_transaction_sorted:
                self.web_transaction_sorted.append(transaction)

            for line in web.lines_list:
                ls = len([s for s in line if (s in is_ascii)])
                no_ascii = (len(line) - ls)
                if no_ascii:
                    self.rus_webs[snapshot] = no_ascii

                for k in lr_lib.core.var.vars_param.DENY_WEB_:
                    count = line.count(k)
                    if count:
                        self.google_webs.setdefault(snapshot, {})[k] = count
                    continue
                continue

            if snapshot < 1:
                continue

            try:
                self.web_transaction[transaction]['snapshots'].append(snapshot)
            except (AttributeError, KeyError):
                self.web_transaction.setdefault(transaction, {})['snapshots'] = [snapshot]

            body = web.get_body()
            self.web_snapshot_param_in_count[snapshot] = in_count = {}
            web.param_in.clear()

            for wr_name in self.wrsp_and_param_names:
                bs = lr_lib.core.wrsp.param.param_bounds_setter(wr_name)
                param_in_count = body.count(bs)
                if param_in_count:
                    in_count[wr_name] = param_in_count
                    web.param_in.add(wr_name)

                    statistic = self.param_statistic[wr_name]
                    statistic['param_count'] += param_in_count
                    statistic['snapshots'].append(snapshot)
                    statistic['transaction_names'].append(transaction)
                continue
            continue

        for k in self.wrsp_and_param_names:
            psk = self.param_statistic[k]
            tn = set(psk['transaction_names'])
            psk['transaction_names'] = sorted(tn, key=self.web_transaction_sorted.index)
            continue

        for wr_name in self.param_statistic:
            statistic = self.param_statistic[wr_name]
            snaps = statistic['snapshots']

            statistic['snapshots_count'] = len(snaps)
            statistic['transaction_count'] = len(statistic['transaction_names'])
            statistic['minmax_snapshots'] = snapshot_diapason_string(snaps)  # для in/out comment

            if (not statistic['param_count']) or (self._wrsp[wr_name].snapshot.inf in snaps):
                self.bad_wrsp_in_usage.append(wr_name)
            continue

        for dt in self.web_transaction.values():
            sn = dt['snapshots']
            dt['minmax_snapshots'] = snapshot_diapason_string(sn)  # для transac comment
            continue

        web_snapshot_all = tuple(self.ActionWebsAndLines.get_web_snapshot_all())

        def get_stats(name: str, deny=('snapshots', 'transaction_names', 'snapshots_count',)) -> Iterable:
            wps = self.param_statistic[name]
            for k in wps:
                if k not in deny:
                    item = (k, wps[k])
                    yield item
                continue
            return

        def web_reg(snapshot: int) -> Iterable[Tuple[str, dict]]:
            web = self.ActionWebsAndLines.get_web_by(web_snapshot_all, snapshot=snapshot)
            web = next(web)
            for wrsp in web.web_reg_save_param_list:
                name = wrsp.name
                gsn = dict(get_stats(name))
                pdt = {'param': wrsp.param, 'stats': gsn}
                item = (name, pdt)
                yield item
                continue
            return

        for t in self.web_transaction:
            gn = self.get_sub_transaction_dt(t, self.all_in_one)
            dtt = next(gn)
            wt = self.web_transaction[t]
            wt_ = copy.deepcopy(wt)
            dtt.update(wt_)
            sn = {s: dict(web_reg(s)) for s in dtt['snapshots']}
            dtt['snapshots'] = sn
            continue

        dt = self.checker_warn()
        for lvl in dt:
            msgs = dt[lvl]
            if msgs:
                m = '\n'.join(msgs)
                ga = getattr(lr_vars.Logger, lvl)
                ga(m)
            continue
        return

    def stats_in_web(self, snapshot: int) -> str:
        """'
        статистика по web_reg_save_param, используемых в теле web.snapshot
        """
        params_in = self.web_snapshot_param_in_count[snapshot]
        if not params_in:
            return ''

        def get(wr_name: str) -> str:
            """param статистика для join в строке"""
            ps = self.param_statistic[wr_name]
            s = '{param}(P:{p_in}/{p_all}|S:{snap}|T:{transac})'.format(
                param=self.wrsp_and_param_names[wr_name],
                p_in=params_in[wr_name],
                p_all=ps['param_count'],
                snap=ps['minmax_snapshots'],
                transac=ps['transaction_count'],
            )
            return s

        spi = sorted(params_in, key=len)
        s = '\n\t{cmnt} IN({sim_params_in})<-[{len_params_in}]: {statistic}'.format(
            statistic=', '.join(map(get, spi)),
            cmnt=lr_lib.core.wrsp.param.LR_COMENT,
            sim_params_in=sum(params_in.values()),
            len_params_in=len(params_in),
        )
        return s

    def stats_out_web(self, snapshot: int) -> str:
        """
        статистика по web_reg_save_param, созданным в web.snapshot
        """
        gn = self.ActionWebsAndLines.get_web_snapshot_by(snapshot=snapshot)
        web = next(gn)

        if not web.web_reg_save_param_list:
            return ''

        statistic = []
        skey = lambda w: len(w.param)
        sd = sorted(web.web_reg_save_param_list, key=skey)

        for wr in sd:
            ps = self.param_statistic[wr.name]
            pss = '{p}(P:{p_all}|S:{snap}|T:{transac})'.format(
                p=wr.param,
                p_all=ps['param_count'],
                snap=ps['minmax_snapshots'],
                transac=ps['transaction_count'],
            )
            statistic.append(pss)
            continue

        s = '\n\t{c} OUT({n})-> {s}'.format(
            s=', '.join(statistic),
            c=lr_lib.core.wrsp.param.LR_COMENT,
            n=len(statistic),
        )
        return s

    def stats_transaction_web(self, web: lr_lib.core.action.web_.WebSnapshot) -> str:
        """
        статистика transaction, для web
        """
        transaction = web.transaction
        mm = self.web_transaction[transaction]['minmax_snapshots']
        if isinstance(web, lr_lib.core.action.web_.WebSnapshot):
            t = self.web_transaction[transaction]
            s = web.snapshot.inf
            m = t['snapshots'].index(s)
            m += 1
            mm = '{m}/{mm}'.format(mm=mm, m=m)

        if transaction:
            t_comment = '\n\t{c} "{t}"({mm})'.format(c=lr_lib.core.wrsp.param.LR_COMENT, t=transaction, mm=mm)
            return t_comment
        return ''

    def checker_warn(self) -> dict:
        """
        проверка на некорректные транзакции
        """
        result = dict(info=[], warning=[], )

        for t in self.ActionWebsAndLines.transactions.names:
            if t.startswith(lr_lib.core.action.transac.Transactions._no_transaction_name):
                continue
            al = self.get_sub_transaction_dt(t, self.all_in_one)
            dtt = next(al)

            # считается пустой(без snapshot), только если не содержит подтранзакций
            if (not dtt) and (t not in self.web_transaction):
                result['info'].append('Пустая транзакция "{}"'.format(t))
            if t not in self.ActionWebsAndLines.transactions.start_stop['start']:
                result['warning'].append('Отсутствует транзакция start_transaction("{}")'.format(t))
            if t not in self.ActionWebsAndLines.transactions.start_stop['stop']:
                result['warning'].append('Отсутствует транзакция stop_transaction("{}")'.format(t))
            continue

        return result

    def get_sub_transaction_dt(self, transaction: str, dt_obj: dict) -> dict:
        """
        словарь транзакции, внутри вложенного словаря Transactions.sub_transaction
        """
        if isinstance(dt_obj, collections.OrderedDict):
            if transaction in dt_obj:
                tt = dt_obj[transaction]
                yield tt
            else:
                for t in dt_obj:
                    v = dt_obj[t]
                    tt = self.get_sub_transaction_dt(transaction, v)
                    yield from tt
                    continue
        return


def snapshot_diapason_string(infs: List[int]) -> str:
    """
    если inf min=max указать только одно
    """
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
