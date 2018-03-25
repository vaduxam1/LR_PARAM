# -*- coding: UTF-8 -*-
# всякое для gui

import lr_lib
import lr_lib.core.var.vars as lr_vars


def center_widget(widget) -> None:
    """center window on screen"""
    widget.withdraw()
    widget.update_idletasks()
    x = (widget.winfo_screenwidth() - widget.winfo_reqwidth()) / 2
    y = (widget.winfo_screenheight() - widget.winfo_reqheight()) / 2
    widget.geometry("+%d+%d" % (x, y))
    widget.deiconify()
    return


def repA(widget) -> None:
    """отчет сокращенный"""
    rep = widget.action.web_action.websReport.all_in_one
    t = 'transac_len={}, param_len={}'.format(len(rep), len(widget.action.web_action.websReport.wrsp_and_param_names))
    y = lr_lib.gui.widj.dialog.YesNoCancel(buttons=['OK'], text_before='repA', text_after='websReport.all_in_one',
                                           is_text=lr_lib.core.etc.other.get_json(rep), title=t, parent=widget.action, t_enc=True, )
    lr_vars.T_POOL_decorator(y.ask)()
    return


def repB(widget, counter=None, st='\n----\n') -> None:
    """отчет полный"""
    wr = widget.action.web_action.websReport
    if counter is None:
        counter = len(wr.wrsp_and_param_names)

    obj = [wr.wrsp_and_param_names, wr.rus_webs, wr.google_webs, wr.bad_wrsp_in_usage,
           widget.action.web_action.transactions.sub_transaction, wr.web_transaction_sorted,
           wr.param_statistic, wr.web_snapshot_param_in_count, wr.web_transaction]

    ao = ['wrsp_and_param_names', 'rus_webs', 'google_webs', 'bad_wrsp_in_usage', 'sub_transaction',
          'web_transaction_sorted', 'param_statistic', 'web_snapshot_param_in_count', 'web_transaction']

    tb = ' | '.join('{}:{}'.format(e, a) for e, a in enumerate(ao, start=1))

    ta = ('\n\n' + st).join('{e}:{ao}{st}{ob}'.format(
        e=e, ao=ao[e - 1], st=st, ob=lr_lib.core.etc.other.get_json(ob)) for (e, ob) in enumerate(obj, start=1))

    y = lr_lib.gui.widj.dialog.YesNoCancel(
        buttons=['OK'], text_before=tb, text_after='{} шт'.format(counter), is_text='\n\n{}'.format(ta),
        title='создано: {} шт.'.format(counter), parent=widget.action, t_enc=True,
    )
    lr_vars.T_POOL_decorator(y.ask)()
    # lr_vars.Logger.trace('{}\n\n{}'.format(tb, ta))
    return


def get_transaction(text: str) -> iter((str,)):
    """имена транзакций"""
    for line in filter(bool, map(str.strip, text.split('\n'))):
        if line.startswith('lr_') and line.endswith(');') and ('_transaction("' in line):
            t_name = line.rsplit('"', 1)[0]
            yield t_name[3:]
