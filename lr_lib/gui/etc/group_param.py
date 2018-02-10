# -*- coding: UTF-8 -*-
# команды из меню мыши - нахождение и замена group_param

import sys
import queue
import contextlib

import lr_lib.gui.etc.gui_other

import lr_lib.core.var.vars as lr_vars
import lr_lib.core.wrsp.param as lr_param
import lr_lib.etc.excepthook as lr_excepthook
import lr_lib.gui.widj.dialog as lr_dialog


@lr_vars.T_POOL_decorator
def group_param(event, widget=None, params=None, ask=True) -> None:
    '''gui - нахождение и замена для группы web_reg_save_param's'''
    if widget is None:
        widget = event.widget

    # найти params
    if params is None:
        params = widget.action.group_param_search(widget.selection_get())
    elif params is False:
        params = widget.action.session_params(lb_list=[widget.selection_get()], ask=False)
    if not params:
        return lr_vars.Logger.warning('param не найдены! %s' % params, parent=widget.action)

    _len_params = len(params)
    if ask:
        y = lr_dialog.YesNoCancel(
            buttons=['Найти', 'Отменить', 'Пропуск'], text_before='найти group param', text_after='%s шт.' % _len_params,
            is_text='\n'.join(params), title='group param', parent=widget.action, default_key='Найти')
        ask = y.ask()
        if ask == 'Найти':
            params = sorted(filter(bool, y.text.split('\n')), key=len, reverse=True)
        elif ask == 'Пропуск':
            params = []
        else:
            return

    len_params = len(params)
    lr_vars.Logger.info('Имеется {l} ранее созданных param.\nДля создания выбрано/найдено {p}/{_p} param.\n'.format(
        _p=_len_params, p=len_params, l=len(widget.action.web_action.websReport.wrsp_and_param_names)))

    def progressbar(p1=((len_params/100) or 1), update_time=lr_vars.MainThreadUpdateTime.get()) -> None:
        '''progressbar выполнения, из vars'''
        if wrsp_dict:  # прогресс работы
            lu = len(unsuccess)
            widget.action.toolbar['text'] = '{p} : {counter}/{len_params} : {w} %{u}\n{wrsp}'.format(
                counter=counter, len_params=len_params, u=(' | fail: %s' % lu if lu else ''), w=round(counter / p1),
                p=wrsp_dict['param'], wrsp=wrsp)
            widget.action.background_color_set(color=None)  # action цвет по кругу
            # перезапуск progressbar
            widget.action.after(update_time, progressbar)

        else:  # выход - результаты работы
            pl = widget.action.param_counter(all_param_info=False)
            lr_vars.Logger.debug(pl)
            widget.action.toolbar['text'] = pl
            widget.action.set_combo_len()

            if unsuccess:
                err = len(unsuccess)
                widget.action.toolbar['text'] = '{s}: {e} param не созданы {u}\nсозданы {p} param\n{pl}'.format(
                    s=str(not err).upper(), pl=pl, e=err, u=(', '.join(unsuccess) if err else ''), p=(len_params-err))
                lr_vars.Logger.error('{} param не были обработаны:\n\t{}'.format(
                    err, '\n\t'.join(unsuccess)), parent=widget.action)

            if widget.action.final_wnd_var.get():
                lr_lib.gui.etc.gui_other.repA(widget)
            widget.action.background_color_set(color='')  # action оригинальный цвет

    # заменить params
    widget.action.backup()
    unsuccess = []  # params, обработанные с ошибкой
    with lr_vars.Window.block(force=True), widget.action.block(highlight=False):
        (counter, wrsp_dict, wrsp) = (0, {'param': None}, 'старт...')  # начальные vars для progressbar
        widget.action.after(0, progressbar)  # progressbar
        for (counter, wrsp_dict, wrsp) in _group_param_iter(params, unsuccess, widget.action):  # заменить
            continue  # vars для progressbar
        wrsp_dict = None  # выход progressbar


def _group_param_iter(params: [str, ], unsuccess, action) -> iter((int, dict, str, [str, ]),):
    '''ядро - найти и заменить группу web_reg_save_param'''
    wrsp_dicts = queue.Queue()
    # для param's, в фоне, создавать wrsp_dict's
    _thread_wrsp_dict_creator(wrsp_dicts, params, unsuccess, action)

    replace = action.web_action.replace_bodys_iter()  # сопрограмма-заменить
    next(replace)
    try:
        for counter, wrsp_dict in enumerate(iter(wrsp_dicts.get, None), start=1):
            wrsp = lr_param.create_web_reg_save_param(wrsp_dict)

            # вставить web_reg_save_param перед web
            action.web_action.web_reg_save_param_insert(wrsp_dict, wrsp)
            # заменить param на web_reg_save_param
            replace.send((wrsp_dict['param'], lr_param.param_bounds_setter(wrsp_dict['web_reg_name'])))

            with contextlib.suppress(UserWarning, AssertionError):  # продолжать
                action.param_inf_checker(wrsp_dict, wrsp)  # inf запроса <= inf web_reg_save_param
            yield (counter, wrsp_dict, wrsp)  # для progressbar
    finally:
        action.web_action_to_tk_text(websReport=True)  # вставить в action.c


@lr_vars.T_POOL_decorator
def _thread_wrsp_dict_creator(wrsp_dicts: queue.Queue, params: [str, ], unsuccess: [], action) -> None:
    '''ядро - создать wrsp_dicts в фоне, чтобы не терять время, при показе popup окон'''
    for param in params:
        try:
            lr_vars.VarParam.set(param, action=action, set_file=True)  # найти и создать
        except Exception:
            unsuccess.append(param)
            lr_excepthook.excepthook(*sys.exc_info())
        else:
            wrsp_dicts.put_nowait(lr_vars.VarWrspDict.get())  # wrsp_dict

    wrsp_dicts.put_nowait(None)  # exit
