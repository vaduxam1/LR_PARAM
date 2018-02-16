# -*- coding: UTF-8 -*-
# action.c статистика

import copy
import string
import collections

import lr_lib.core.action.transac as lr_transac
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.action.web_ as lr_web_
import lr_lib.core.wrsp.param as lr_param
import lr_lib.gui.etc.action_lib as lr_action_lib


is_ascii = set(string.printable).__contains__


class WebReport:
    '''статистика использования web_reg_save_param'''
    def __init__(self, parent_AWAL):
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

    def create(self):
        '''создать статистику'''
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

        for wr in wrsp_all:
            self.web_add_highlight(wr)

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
            self.web_add_highlight(web)

            snapshot = web.snapshot
            transaction = web.transaction

            if isinstance(web, lr_web_.WebSnapshot):  # проставить родителя wrsp объекта
                for wrsp in web.web_reg_save_param_list:
                    wrsp.snapshot = web.snapshot
                    wrsp.parent_snapshot = web

            if transaction not in self.web_transaction_sorted:
                self.web_transaction_sorted.append(transaction)

            for line in web.lines_list:
                no_ascii = len(line) - len(tuple(filter(is_ascii, line)))
                if no_ascii:
                    self.rus_webs[snapshot] = no_ascii

                for k in lr_vars.DENY_WEB_:
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
            snaps = statistic['snapshots']

            statistic['snapshots_count'] = len(snaps)
            statistic['transaction_count'] = len(statistic['transaction_names'])
            statistic['minmax_snapshots'] = snapshot_diapason_string(snaps)  # для in/out comment

            if (not statistic['param_count']) or (self._wrsp[wr_name].snapshot in snaps):
                self.bad_wrsp_in_usage.append(wr_name)

        for dt in self.web_transaction.values():
            dt['minmax_snapshots'] = snapshot_diapason_string(dt['snapshots'])  # для transac comment

        web_snapshot_all = tuple(self.parent_AWAL.get_web_snapshot_all())

        def get_stats(name, deny=('snapshots', 'transaction_names', 'snapshots_count', )):
            wps = self.param_statistic[name]
            for k in wps:
                if k not in deny:
                    yield k, wps[k]

        def web_reg(snapshot: int) -> iter((str, dict),):
            web = self.parent_AWAL.get_web_by(web_snapshot_all, snapshot=snapshot)
            web = next(web)
            for wrsp in web.web_reg_save_param_list:
                name = wrsp.name
                pdt = {'param': wrsp.param, 'stats': dict(get_stats(name))}
                yield name, pdt

        for t in self.web_transaction:
            dtt = next(self.get_sub_transaction_dt(t, self.all_in_one))
            dtt.update(copy.deepcopy(self.web_transaction[t]))
            dtt['snapshots'] = {s: dict(web_reg(s)) for s in dtt['snapshots']}

        dt = self.checker_warn()
        for lvl in dt:
            msgs = dt[lvl]
            if msgs:
                getattr(lr_vars.Logger, lvl)('\n'.join(msgs))

        # highlight
        t = self.parent_AWAL.action.tk_text
        for wr in wrsp_all:
            if not all(self.param_statistic[wr.name].values()):
                lr_action_lib.highlight_mode(t, wr.name, option='background', color='yellow')

        for n in self.parent_AWAL.transactions.names:
            lr_action_lib.highlight_mode(t, n, option='foreground', color='darkslategrey')

    def web_add_highlight(self, web_) -> None:
        '''подсветить web_'''
        t = self.parent_AWAL.action.tk_text
        lr_action_lib.highlight_mode(t, web_.type)

        for line in web_.comments.split('\n'):
            lr_action_lib.highlight_mode(t, line.strip())

        if isinstance(web_, lr_web_.WebRegSaveParam):
            m = lr_vars.web_reg_highlight_len
            lr_action_lib.highlight_mode(t, '{}'.format(web_.name[:m]), option='background', color=lr_vars.wrsp_color1)
            lr_action_lib.highlight_mode(t, web_.name[m:], option='foreground', color=lr_vars.wrsp_color2)
            lr_action_lib.highlight_mode(t, web_.param, option='foreground', color=lr_vars.wrsp_color2)
            for line in web_.lines_list[1:]:
                lr_action_lib.highlight_mode(t, line.strip())
        else:
            lr_action_lib.highlight_mode(t, web_.name)

    def stats_in_web(self, snapshot: int) -> str:
        ''''статистика по web_reg_save_param, используемых в теле web.snapshot'''
        params_in = self.web_snapshot_param_in_count[snapshot]
        if not params_in:
            return ''

        def get(wr_name, format='{param}(P:{p_in}/{p_all}|S:{snap}|T:{transac})'.format):
            ps = self.param_statistic[wr_name]
            s = format(param=self.wrsp_and_param_names[wr_name], p_in=params_in[wr_name], p_all=ps['param_count'],
                       snap=ps['minmax_snapshots'], transac=ps['transaction_count'])
            return s

        statistic = (get(wr_name) for wr_name in sorted(params_in, key=len))
        s = '\n\t{c} IN({i})<-[{ui}]: {st}'.format(
            st=', '.join(statistic), c=lr_param.LR_COMENT, i=sum(params_in[w] for w in params_in), ui=len(params_in))
        return s

    def stats_out_web(self, snapshot: int) -> str:
        ''''статистика по web_reg_save_param, созданным в web.snapshot'''
        web = next(self.parent_AWAL.get_web_snapshot_by(snapshot=snapshot))

        if not web.web_reg_save_param_list:
            return ''

        statistic = []
        for wr in sorted(web.web_reg_save_param_list, key=lambda w: len(w.param)):
            ps = self.param_statistic[wr.name]
            pss = '{p}(P:{p_all}|S:{snap}|T:{transac})'.format(
                p=wr.param, p_all=ps['param_count'], snap=ps['minmax_snapshots'], transac=ps['transaction_count'])
            statistic.append(pss)

        return '\n\t{c} OUT({n})-> {s}'.format(s=', '.join(statistic), c=lr_param.LR_COMENT, n=len(statistic))

    def stats_transaction_web(self, web) -> str:
        ''''статистика transaction, для web'''
        transaction = web.transaction
        mm = self.web_transaction[transaction]['minmax_snapshots']
        if isinstance(web, lr_web_.WebSnapshot):
            m = self.web_transaction[transaction]['snapshots'].index(web.snapshot) + 1
            mm = '{m}/{mm}'.format(mm=mm, m=m)

        if transaction:
            t_comment = '\n\t{c} "{t}"({mm})'.format(c=lr_param.LR_COMENT, t=transaction, mm=mm)
            return t_comment
        else:
            return ''

    def checker_warn(self) -> dict:
        '''проверка на некорректные транзакции'''
        result = dict(info=[], warning=[], )

        for t in self.parent_AWAL.transactions.names:
            if t.startswith(lr_transac.Transactions._no_transaction_name):
                continue
            dtt = next(self.get_sub_transaction_dt(t, self.all_in_one))

            if (not dtt) and (t not in self.web_transaction):  # считается пустой(без snapshot), только если не содержит подтранзакций
                result['info'].append('Пустая транзакция "{}"'.format(t))
            if t not in self.parent_AWAL.transactions.start_stop['start']:
                result['warning'].append('Отсутствует транзакция start_transaction("{}")'.format(t))
            if t not in self.parent_AWAL.transactions.start_stop['stop']:
                result['warning'].append('Отсутствует транзакция stop_transaction("{}")'.format(t))

        return result

    def get_sub_transaction_dt(self, transaction: str, dt_obj: dict) -> dict:
        '''словарь транзакции, внутри вложенного словаря Transactions.sub_transaction'''
        if isinstance(dt_obj, collections.OrderedDict):
            if transaction in dt_obj:
                yield dt_obj[transaction]
            else:
                for t in dt_obj:
                    yield from self.get_sub_transaction_dt(transaction, dt_obj[t])


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

