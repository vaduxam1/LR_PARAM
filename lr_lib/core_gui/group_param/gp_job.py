# -*- coding: UTF-8 -*-
# нахождение param
# Есть 4 основных источника, где можно найти param, в action.c и файлах каталога "data"::
# 1) "action.c"  файл - находятся только используемые param.
# 2) "Request" файлы - находятся используемые + немного неиспользуемых param, например из удаленных в action.c snapshot
# 3) "Response" файлы - находятся используемые + очень много неиспользуемых param, все затронутые при записи теста
# 4) "Остальные" файлы - какието файлы, возможно ошибочно отсеяные как ненужные. Или, например ненайденный param упоминается в логе, с другими lb/rb, и уже от туда его можно вытащить
#
# Есть 4 основных способа, как можно найти param:
# 1) Абстрактный: по param-LB, причем в action.c и Request/Response файлах, для одного и того же param могут быть разные LB
# 2) Абстрактный: Вытаскивать слова с помощью регулярных выражений
# 3) Специальный: Объединенный 1)-2)
# 4) Абстрактный: По началу имени, почти всегда, в рамках одного скрипта, начало(bJsPt)
#         части имен param повторяются - 'bJsPt3', 'bJsPt4'. Лучше всегда запускать в конце.
#
# Абстрактный - те просто ищет слова в любом тексте, по какамуто шаблону, может быть много лишнего
# Специальный - те расчитан на то что текст имеет определенный синтаксис, чтото вроде {"item": ['zul.sel.Treecell': {'bJsPt3', 'bJsPt4'}]}
#           за счет синтаксиса, можно вытаскивать только то что надо

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core
import lr_lib.core.var.vars_param
from lr_lib.core.var import vars as lr_vars
from lr_lib.core_gui.group_param.gp_var import responce_files_texts
from lr_lib.gui.widj.dialog import K_FIND, K_SKIP


def _get_text_for_web(mode: str, action: 'lr_lib.gui.action.main_action.ActionWindow') -> iter(([str, str],)):
    """текст для web объектов"""
    if mode == 'snapshot':
        for web_ in action.web_action.get_web_snapshot_all():
            n = str(web_.snapshot.inf)
            item = (n, web_.get_body())
            yield item
            continue
    elif mode == 'web':
        for web_ in action.web_action.get_web_all():
            n = str(web_.snapshot.inf)
            item = (n, web_.get_body())
            yield item
            continue
    else:
        n = ''
        items = action.web_action._to_str()
        yield from ((n, t) for t in items)
    return


name_check1 = lambda file_name: ('Request' in file_name)
name_check2 = lambda file_name: (file_name in (f['File']['Name'] for f in lr_vars.AllFiles))  # 'Response'
name_check3 = lambda file_name: (not (name_check1(file_name) or name_check2(file_name)))  # не Req/Resp


def _text_from_params_source(
        params_source: 'str or lr_lib.gui.action.main_action.ActionWindow',
) -> iter(([str, str], )):
    """тексты для поиска param"""
    if isinstance(params_source, str):
        params_source = [params_source, ]

    for ps in params_source:
        if ps == 'Request':
            texts = responce_files_texts(name_check=name_check1)
        elif ps == 'Response':
            texts = responce_files_texts(name_check=name_check2)
        elif ps == 'any':
            texts = responce_files_texts(name_check=name_check3)
        elif ps == 'all':
            texts = responce_files_texts(name_check=bool)
        else:  # action
            (ps, action) = ps
            texts = _get_text_for_web(ps, action)

        yield from texts
        continue
    return


def _group_param_search_by_exist_param(
        exist_params: [str, ],
        params_source,
        **kwargs,
) -> iter((str,)):
    """поиск по началу имени - взять n первых символов для повторного поиска param по началу имени"""
    param_spin = lr_vars.SecondaryParamLen.get()
    if param_spin:
        param_parts = [param[:param_spin] for param in exist_params]
    else:
        return

    yield from _group_param_search_by_param_part(param_parts, params_source, **kwargs)
    return


def _group_param_search_by_lb(lb_items: [str, ], params_source) -> iter((str, )):
    """поиск по LB"""
    yield from _group_param_search_by_param_part(lb_items, params_source, part_mode=False)
    return


def _group_param_search_by_param_part(
        param_parts: ["zkau_", ],
        params_source,
        **kwargs,
) -> iter(("zkau_5650", "zkau_5680",)):
    """
    для группы parts
    """
    param_texts = _text_from_params_source(params_source)
    for (name, text) in param_texts:
        for param_part in param_parts:
            yield from _params_by_part(param_part, text, **kwargs)
            continue
        continue
    return


def _params_by_part(
        param_part: "zkau_",
        text: str,
        part_mode=True,
        allow=lr_lib.core.var.vars_param.param_valid_letters,
) -> iter(("zkau_5650", "zkau_5680",)):
    """
    поиск в action.c, всех param, в имени которых есть param_part / или по LB
    part_mode=False - поиск param в action, по LB=
    """
    split_text = text.split(param_part)
    len_split = len(split_text)

    for index in range(len_split - 1):
        left = split_text[index]
        left = left.rsplit('\n', 1)
        left = left[-1].lstrip()

        right = split_text[index + 1]
        right = right.split('\n', 1)
        right = right[0].rstrip()
        if not right:
            continue

        if part_mode:
            state = lr_lib.core.etc.lbrb_checker.check_bound_lb(left)
        else:
            state = (right[0] in allow)

        if not state:
            continue

        param_chars = []  # "5680"
        for s in right:
            if s in allow:
                param_chars.append(s)
            else:
                break
            continue

        if not param_chars:
            continue

        param = ''.join(param_chars)
        if part_mode:  # param_part или по LB
            param = (param_part + param)

        yield param  # "zkau_5680"

        continue
    return


def all_lb_from(text: str, param: str) -> iter((str, )):
    checks = lr_lib.core.etc.lbrb_checker.check_in_text_param_all_bound_lb_rb(text=text, param=param)

    for (index, check) in enumerate(checks, start=1):
        if not check:
            continue

        lb_ = text.split(param, index)
        lb_full = lb_[index - 1]
        lb = _lb_get(lb_full)

        yield lb
        continue
    return


def _lb_get(lb_full: str) -> str:
    """забрать lb"""
    check = False
    lb = []

    for ch in reversed(lb_full):
        if check:
            if ch in lr_lib.core.var.vars_param.param_valid_letters:
                lb.append(ch)
            else:
                break
        elif ch in lr_lib.core.var.vars_param.param_splitters:
            lb.append(ch)
        else:
            break
        continue

    lb = ''.join(reversed(lb))
    return lb
