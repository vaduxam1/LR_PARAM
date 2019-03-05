# -*- coding: UTF-8 -*-
# автоустановка VarSplitListNum

import string  # для eval
from typing import Iterable, Tuple, List, Callable, Any

import lr_lib
from lr_lib.core.var import vars as lr_vars


def lb_rb_split_list_set(__lb: str, __rb: str, lb: str, rb: str, r_min=1, r_max=3) -> Tuple[str, str]:
    """
    автоустановка VarSplitListNum, если param находится внутри {} или [] скобок
    lr_vars.VarSplitListNumRB.set(1) если {}: {...,'value':'param',...} / или .set(1) если []
    """
    VarSplitListNumRB = lr_vars.VarSplitListNumRB.get()

    vlb1 = lr_vars.VarLbB1.get()
    vlb2 = lr_vars.VarLbB2.get()
    vrb1 = lr_vars.VarRbB1.get()
    vrb2 = lr_vars.VarRbB2.get()

    _l = (__lb if (vlb1 or vrb1) else '')
    _r = (__rb if (vlb2 or vrb2) else '')
    if _l or _r:
        # проверить внутри ли скобок
        bound1 = is_mutable_bound(_l, _r, b1='{', b2='}')
        bound2 = is_mutable_bound(_l, _r, b1='[', b2=']')

        vb1 = [vlb1, vrb1, ]
        vb2 = [vlb2, vrb2, ]
        zi = zip(bound1, bound2, vb1, vb2, )
        for (indx_1, indx_2, allow_1, allow_2) in zi:

            if allow_1 and indx_1:
                if indx_2:
                    if indx_1 < indx_2:
                        lr_vars.VarSplitListNumRB.set(r_min)
                    elif allow_2:
                        lr_vars.VarSplitListNumRB.set(r_max)
                else:
                    lr_vars.VarSplitListNumRB.set(r_min)
                break

            elif allow_2 and indx_2:
                lr_vars.VarSplitListNumRB.set(r_max)
                break

            else:
                pass
            continue

    try:
        lb_combo = splitters_combo(lr_vars.Window.LBent_SplitList)
    except AttributeError:
        lb_combo = lr_lib.core.var.vars_param.SplitList
    try:
        rb_combo = splitters_combo(lr_vars.Window.RBent_SplitList)
    except AttributeError:
        rb_combo = lr_lib.core.var.vars_param.SplitList

    # LB обрезать из SplitList
    if lr_vars.VarSplitListLB.get():
        i_lb = lr_vars.VarSplitListNumLB.get()
        for word in lb_combo:
            lb_add = lb[:-i_lb]
            lb_main = lb[-i_lb:]

            lb_add = lb_add.rsplit(word, 1)
            lb_add = lb_add[-1]

            lb = (lb_add + lb_main)  # add_main_lb_{param}_rb_main_add
            continue

    # RB обрезать из SplitList
    if lr_vars.VarSplitListRB.get():
        check = False

        for bound in lr_lib.core.var.vars_param.RbStartswithBoundFixed:
            if rb.startswith(bound):
                rb = bound
                check = True
                break
            continue

        if not check:
            i_rb = lr_vars.VarSplitListNumRB.get()
            for word in rb_combo:
                rb_main = rb[:i_rb]
                rb_add = rb[i_rb:]

                rb_add = rb_add.split(word, 1)
                rb_add = rb_add[0]

                rb = (rb_main + rb_add)  # add_main_lb_{param}_rb_main_add
                continue

    lr_vars.VarSplitListNumRB.set(VarSplitListNumRB)  # вернуть

    item = (lb, rb)
    return item


def is_mutable_bound(left: str, right: str, b1='{', b2='}') -> Tuple[int, int]:
    """
    находится ли внутри bound скобок, для lb и rb
    """
    left_ = left[::-1]
    ml = _is_mutable_bound(left_, b2, b1)
    mr = _is_mutable_bound(right, b1, b2)
    item = (ml, mr)
    return item


def _is_mutable_bound(
        stri: str,
        bound_left: '{',
        bound_right: '}',
        _equation=0,
        _indx=0,
) -> int:
    """
    находится ли внутри bound скобок, для lb или rb
    """
    for (_indx, symb) in enumerate(stri, start=1):
        if symb == bound_left:
            _equation += 1
        elif symb == bound_right:
            if _equation:
                _equation -= 1

            else:
                return _indx  # внутри скобок
        else:
            pass
        continue
    return _indx  # не внутри скобок


def splitters_combo(combo: 'tkinter.ttk.Combobox') -> List[str, ]:
    """
    eval разделителей из gui
    """
    splitter = combo.get()
    all_splitters = list(combo['values'])

    if splitter not in all_splitters:
        all_splitters.append(splitter)
        all_splitters.reverse()
        combo['values'] = all_splitters

    splitter = eval(splitter)  # например для string.ascii_letters
    return splitter
