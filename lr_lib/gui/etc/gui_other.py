# -*- coding: UTF-8 -*-
# всякое для gui

from typing import Iterable

import lr_lib
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.etc.vars_other
from lr_lib.core.etc.other import get_json


def center_widget(widget) -> None:
    """
    center window on screen
    """
    widget.withdraw()
    widget.update_idletasks()

    w1 = widget.winfo_screenwidth()
    w2 = widget.winfo_reqwidth()
    x = (w1 - w2)
    x /= 2

    w3 = widget.winfo_screenheight()
    w4 = widget.winfo_reqheight()
    y = (w3 - w4)
    y /= 2

    xy = "+%d+%d"
    widget.geometry(xy % (x, y))
    widget.deiconify()
    return


def repA(widget) -> None:
    """
    отчет сокращенный
    """
    lwpn = len(widget.action.web_action.websReport.wrsp_and_param_names)
    lr = len(widget.action.web_action.websReport.all_in_one)
    t = 'transac_len={}, param_len={}'.format(lr, lwpn)
    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=['OK', ],
        text_before='repA',
        text_after='websReport.all_in_one',
        is_text=get_json(widget.action.web_action.websReport.all_in_one),
        title=t,
        parent=widget.action,
        t_enc=True,
    )
    func = lr_lib.core.var.etc.vars_other.T_POOL_decorator(y.ask)
    func()
    return


def repB(widget, counter=None, st='\n----\n') -> None:
    """
    отчет полный
    """
    wr = widget.action.web_action.websReport
    if counter is None:
        counter = len(wr.wrsp_and_param_names)

    obj = [wr.wrsp_and_param_names, wr.rus_webs, wr.google_webs, wr.bad_wrsp_in_usage,
           widget.action.web_action.transactions.sub_transaction, wr.web_transaction_sorted,
           wr.param_statistic, wr.web_snapshot_param_in_count, wr.web_transaction]

    ao = ['wrsp_and_param_names', 'rus_webs', 'google_webs', 'bad_wrsp_in_usage', 'sub_transaction',
          'web_transaction_sorted', 'param_statistic', 'web_snapshot_param_in_count', 'web_transaction']

    tb = ' | '.join('{}:{}'.format(e, a) for e, a in enumerate(ao, start=1))

    s = ('\n\n' + st)
    i = '{e}:{ao}{st}{ob}'
    ta = s.join(i.format(e=e, ao=ao[e - 1], st=st, ob=get_json(ob)) for (e, ob) in enumerate(obj, start=1))

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=['OK', ],
        text_before=tb,
        text_after='{} шт'.format(counter),
        is_text='\n\n{}'.format(ta),
        title='создано: {} шт.'.format(counter),
        parent=widget.action,
        t_enc=True,
    )
    func = lr_lib.core.var.etc.vars_other.T_POOL_decorator(y.ask)
    func()
    # lr_vars.Logger.trace('{}\n\n{}'.format(tb, ta))
    return


def get_transaction(text: str) -> Iterable[str]:
    """
    имена транзакций
    """
    m = map(str.strip, text.split('\n'))
    for line in filter(bool, m):
        if line.startswith('lr_') and line.endswith(');') and ('_transaction("' in line):
            t_name = line.rsplit('"', 1)
            t_name = t_name[0][3:]
            yield t_name
        continue
    return


def wordBreakAfter(tcl_wordchars=lr_vars.tcl_wordchars, tcl_nonwordchars=lr_vars.tcl_nonwordchars) -> None:
    """
    область выделения двойным кликом мыши
    this first statement triggers tcl to autoload the library # that defines the variables we want to override.
    this defines what tcl considers to be a "word". For more
    # information see http://www.tcl.tk/man/tcl8.5/TclCmd/library.htm#M19
    """
    lr_vars.Tk.tk.call('tcl_wordBreakAfter', '', 0)
    lr_vars.Tk.tk.call('set', 'tcl_wordchars', tcl_wordchars)
    lr_vars.Tk.tk.call('set', 'tcl_nonwordchars', tcl_nonwordchars)
    return
