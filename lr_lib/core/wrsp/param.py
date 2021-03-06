# -*- coding: UTF-8 -*-
# формирование web_reg_save_param

import copy
import random
import string
import time
from typing import Iterable, Tuple, List, Callable, Any

import lr_lib
import lr_lib.core.etc.lbrb_checker
import lr_lib.core.var.vars as lr_vars
import lr_lib.core.var.etc.vars_other
import lr_lib.core.var.vars_param

LR_COMENT = '//lr:'  # определять как комментарий утилиты

# имя web_reg_save_param
WEB_REG_NUM = '{letter}_{wrsp_rnd_num}_{infs}__{transaction}__{lb_name}__{wrsp_name}__{rb_name}'

# WRSP с коротким комментарием
_web_reg_save_param = """
// PARAM["{param}"] // Snap{inf_nums} // FILE["{Name}"]
web_reg_save_param("{web_reg_name}",
    "LB={lb}",
    "RB={rb}",
    "Ord={param_ord}",
    "Search={search_key}",
    LAST); 
"""

# WRSP с полным комментарием
web_reg_save_param = """
// Snap{inf_nums}, [{param_inf_min}:{param_inf_max}]={search_inf_len} -> [{_param_inf_min}:{_param_inf_max}]={_param_inf_all} | FILE["{Name}"], with_param = {file_index}/{param_files} | {create_time}
// PARAM["{param}"], count={param_part}/{param_count}, NA={param_NotPrintable} | LB[{Lb_len}~{lb_len}] NA={lb_NotPrintable}, RB[{Rb_len}~{rb_len}] NA={rb_NotPrintable}
web_reg_save_param("{web_reg_name}",
    "LB={lb}",
    "RB={rb}",
    "Ord={param_ord}",
    "Search={search_key}",
    "NotFound=ERROR",
    LAST); 
"""

# !!! при редактировании web_reg_save_param, учесть что придется изменить wrsp_start/end, чтобы при автозамене, не заменялся param в коментарии // PARAM[{param}], и тд
wrsp_file_start = 'FILE["'
wrsp_file_end = '"]'

wrsp_LB_start = '"LB='
wrsp_LB_end = '",\n'
wrsp_RB_start = '"RB='
wrsp_RB_end = '",\n'

wrsp_start = '// PARAM["'
wrsp_end = '"'
wrsp_start_end = '// PARAM["{param}"]'

wrsp_lr_start = 'web_reg_save_param("'
wrsp_lr_end = '",'

_block_startswith = 'web_'
_block_endswith = '",'
_block_endswith2 = '("'
_block_endswith3 = '");'

SnapInComentS = 'Snap['
SnapInComentE = ']'
Snap1 = '"Snapshot=t'
Snap2 = '.inf",'
_Snap = '%s{num}%s'
Snap = (_Snap % (Snap1, Snap2))
Web_LAST = 'LAST);'  #


def param_bounds_setter(param: str, start='{', end='}') -> str:
    """
    web_reg_save_param имя "P_1212_2_z_kau_1" -> "{P_1212_2_z_kau_1}"
    """
    if not param.startswith(start):
        param = (start + param)
    if not param.endswith(end):
        param += end
    return param


def create_web_reg_save_param(wrsp_dict=None) -> str:
    """
    сформировать web_reg_save_param
    """
    if wrsp_dict is None:
        wrsp_dict = lr_vars.VarWrspDict.get()
    else:
        lr_vars.VarWrspDict.set(wrsp_dict)

    if lr_vars.VarWRSPStats.get():
        wrsp_string = web_reg_save_param
    else:
        wrsp_string = _web_reg_save_param

    s = wrsp_string.format(**wrsp_dict)
    return s


def create_web_reg_save_param_and_dict(wrsp_dict=None) -> Tuple[str, dict]:
    """
    сформировать web_reg_save_param и его словарь
    """
    if wrsp_dict is None:
        wrsp_dict = lr_vars.VarWrspDict.get()

    s = create_web_reg_save_param(wrsp_dict=wrsp_dict)
    item = (s, wrsp_dict)
    return item


# из каких символов, может состоять lb rb части имени web_reg_save_param
allow_lrb = set(string.ascii_letters + string.digits)
# из каких символов, не может состоять имя web_reg_save_param
wrsp_deny_punctuation = {ord(c): '' for c in string.punctuation.replace('_', '')}
# из каких символов, не может состоять имя web_reg_save_param
wrsp_deny_punctuation.update({ord(c): '' for c in string.whitespace})


def wrsp_dict_creator(is_param=True) -> dict:
    """
    сформировать данные для web_reg_save_param
    """
    all_infs = tuple(lr_lib.core.etc.other.get_files_infs(lr_vars.AllFiles))
    param_infs = tuple(lr_lib.core.etc.other.get_files_infs(lr_vars.FilesWithParam))
    len_param_files = len(lr_vars.FilesWithParam)
    file = lr_vars.VarFile.get()
    Lb = lr_vars.VarLB.get()
    Rb = lr_vars.VarRB.get()
    param_count = file['Param']['Count']
    param_num = lr_vars.VarPartNum.get()
    param_num += 1  # нумерация с 0

    # экранирование
    lb = screening_wrsp(Lb)
    rb = screening_wrsp(Rb)

    param = lr_vars.VarParam.get()
    if is_param:
        (param_ord, param_index) = find_param_ord()
    else:
        (param_ord, param_index) = (-1, -1)

    snapshots = file['Snapshot']['Nums']
    s0 = snapshots[0]
    wrsp_name = wrsp_name_creator(param, Lb, Rb, s0)

    search_key = 'All'
    # if file['Snapshot']['inf_key'] == 'ResponseHeaderFile':
    #     search_key = 'Headers'

    fi = lr_vars.FilesWithParam.index(file)
    fi += 1
    files_all = len(lr_vars.AllFiles)
    param_all = sum(f['Param']['Count'] for f in lr_vars.FilesWithParam)
    create_time = time.strftime('%H:%M:%S-%d/%m/%y')
    Lb_len = len(Lb)
    Rb_len = len(Rb)
    lb_len = len(lb)
    rb_len = len(rb)
    lb_NotPrintable = lr_lib.core.etc.other.not_printable(lb)
    rb_NotPrintable = lr_lib.core.etc.other.not_printable(rb)
    all_inf_min = min(all_infs)
    all_inf_max = max(all_infs)
    all_inf_len = len(all_infs)
    _param_inf_min = min(param_infs)
    _param_inf_max = max(param_infs)
    _param_inf_all = len(param_infs)

    web_reg_save_param_dict = dict(
        lb=lb,
        rb=rb,
        param_ord=param_ord,
        web_reg_name=wrsp_name,
        param_part=param_num,
        param_count=param_count,
        param_files=len_param_files,
        file_index=fi,
        files_all=files_all,
        param_all=param_all,
        create_time=create_time,
        inf_nums=snapshots,
        Lb_len=Lb_len,
        Rb_len=Rb_len,
        lb_len=lb_len,
        rb_len=rb_len,
        lb_NotPrintable=lb_NotPrintable,
        rb_NotPrintable=rb_NotPrintable,
        param_text_index=param_index,
        all_inf_min=all_inf_min,
        all_inf_max=all_inf_max,
        all_inf_len=all_inf_len,
        _param_inf_min=_param_inf_min,
        _param_inf_max=_param_inf_max,
        _param_inf_all=_param_inf_all,
        search_key=search_key,
        param=param,
    )

    m1 = file['Param']['inf_min']
    m2 = file['Param']['inf_max']
    li = list(i for i in all_infs if (m1 <= i <= m2))
    web_reg_save_param_dict['search_inf_len'] = len(li)
    # file['File'] ключи
    fd = file['File']
    web_reg_save_param_dict.update(fd)
    # param_* ключи - file['Param']
    pd = file['Param']
    d = {'param_{}'.format(k): v for (k, v) in pd.items() if (k != 'Name')}
    web_reg_save_param_dict.update(d)

    return web_reg_save_param_dict


def wrsp_name_creator(param: str, Lb: str, Rb: str, snapshot: int) -> str:
    """
    сформировать имя для web_reg_save_param(6)
    """
    MaxLbWrspName = lr_vars.MaxLbWrspName.get()
    MaxRbWrspName = lr_vars.MaxRbWrspName.get()
    g = lr_vars.SnapshotInName.get()
    infs = (snapshot if g else '')

    if (MaxLbWrspName >= 0) and (len(Lb) > 2):
        lbn = ['']
        for b in Lb:
            if b in allow_lrb:
                lbn[-1] += b
            elif lbn[-1]:
                lbn.append('')
            continue

        lbn = filter(bool, lbn)
        lbn = [b for b in lbn if (b not in lr_lib.core.var.vars_param.LRB_rep_list)]
        sd = sorted(set(lbn), key=lbn.index)
        lb_name = '_'.join(sd)[-MaxLbWrspName:]
    else:
        lb_name = ''

    if (MaxRbWrspName >= 0) and (len(Rb) > 2):
        rbn = ['']
        for b in Rb:
            if b in allow_lrb:
                rbn[-1] += b
            elif rbn[-1]:
                rbn.append('')
            continue

        rbn = filter(bool, rbn)
        rbn = [b for b in rbn if (b not in lr_lib.core.var.vars_param.LRB_rep_list)]
        rd = sorted(set(rbn), key=rbn.index)
        rb_name = '_'.join(rd)[:MaxRbWrspName]
    else:
        rb_name = ''

    p = tuple(filter(allow_lrb.__contains__, param))  # печатные символы искомого param
    s = ''.join(p[1:-1])
    jp = [p[0], s, p[-1]]
    ns = lr_vars.wrsp_name_splitter.get()
    wrsp_param_name = ns.join(jp)
    pma = lr_vars.MaxParamWrspName.get()
    if pma >= 0:
        wrsp_param_name = wrsp_param_name[:pma]

    maw = lr_vars.MaxWrspRnum.get()
    miw = lr_vars.MinWrspRnum.get()
    wrsp_rnd_num = (random.randrange(miw, maw) if (maw and (miw >= 0)) else '')

    tma = lr_vars.TransactionInNameMax.get()
    if (tma >= 0) and lr_vars.Window and lr_vars.Window.action_windows:
        action = lr_vars.Window.get_main_action()
        web_action = action.web_action
        al = web_action.get_web_snapshot_all()
        wa = web_action.get_web_by(al, snapshot=snapshot)
        w = next(wa)

        if w and w.transaction and (not w.transaction.startswith(web_action.transactions._no_transaction_name)):
            wts = w.transaction.split()
            s = (''.join(filter(str.isalnum, t)).translate(lr_lib.etc.help.TRANSLIT_DT) for t in wts)
            transaction = '_'.join(s)
            transaction = transaction[:tma]
        else:
            transaction = ''
    else:
        transaction = ''

    wrsp_name = WEB_REG_NUM.format(
        wrsp_rnd_num=wrsp_rnd_num,
        wrsp_name=wrsp_param_name,
        lb_name=lb_name,
        rb_name=rb_name,
        infs=infs,
        letter=lr_vars.WrspNameFirst.get(),
        transaction=transaction,
    )

    wrsp_name = str.translate(wrsp_name, wrsp_deny_punctuation).rstrip('_')
    while '___' in wrsp_name:
        wrsp_name = wrsp_name.replace('___', '__')
        continue

    return wrsp_name


# экранирование символов для WRSP LB/RB
ScrWrspSymbol = {ord(s): '\\{0}'.format(s) for s in lr_lib.core.var.vars_param.Screening}


def screening_wrsp(lbrb: str) -> str:
    """
    экранирование для web_reg_save_param LB/RB
    :param lbrb: str: 'value=/'
    :return: str: 'value=//'
    """
    lbrb = str.translate(lbrb, ScrWrspSymbol)
    return lbrb


def un_screening_wrsp(lbrb: str) -> str:
    """
    раз-экранирование для web_reg_save_param LB/RB
    :param lbrb: str: 'value=//'
    :return: str: 'value=/'
    """
    for s in lr_lib.core.var.vars_param.Screening:
        sc = '\\{}'.format(s)
        lbrb = lbrb.replace(sc, s)
        continue
    return lbrb


def _search_param_in_file(file: dict) -> dict:
    """
    найти кол-во {param} в файле, count - те все, без проверки на корректность
    """
    File = file['File']
    Param = file['Param']
    param = Param['Name']

    ff = File['FullName']
    with open(ff, encoding=File['encoding'], errors='ignore') as text:
        count = sum(line.count(param) for line in text)

    if count:
        Param['Count'] = count
        return file
    return


def search_param_in_file(file: dict) -> 'dict or None':
    """
    найти кол-во {param} в файле, с контролем LB RB
    """
    File = file['File']
    Param = file['Param']
    param = Param['Name']
    Param['Count'] = 0
    Param['Count_indexs'] = []

    ff = File['FullName']
    with open(ff, encoding=File['encoding'], errors='ignore') as text:
        tx = text.read()

    split_line = tx.split(param)
    split_len = len(split_line)
    if split_len < 2:
        return

    indx = 0
    for indx in range(1, split_len):
        i = (indx - 1)
        left = split_line[i]
        right = split_line[indx]
        if lr_lib.core.etc.lbrb_checker.check_bound_lb_rb(left, right):
            ci = Param['Count_indexs']
            ci.append(i)
        continue

    if Param['Count_indexs']:
        Param['Count'] = indx
        ci = Param['Count_indexs']
        Param['Count_indexs_len'] = len(ci)
        return file
    return


def create_files_with_search_data(files: Tuple[dict], search_data: dict, action=None, action_infs=()) -> Iterable[dict]:
    """
    с учетом inf - создать копию файла и обновить search_data
    """
    dt = search_data['Param']
    inf_min = dt['inf_min']
    inf_max = dt['inf_max']

    if action:
        dt['action_id'] = action.id_
        action_infs = action.web_action.action_infs

        inf_min = dt['inf_min'] = min(action_infs or [-1])
        inf_max = dt['inf_max'] = max(action_infs or [-1])
        n = dt['Name']
        sp = set_param_in_action_inf(action, n)
        dt['max_action_inf'] = param_inf = next(sp, -1)

        ai = action.add_inf_cbx_var.get()
        if (not ai) and (param_inf > 1):
            param_inf -= 1  # inf, педшествующий номеру inf, где первый раз встречается pram

        mi = action.max_inf_cbx_var.get()
        if mi and param_inf and (param_inf > 0) and (inf_max > param_inf):
            inf_max = dt['inf_max'] = param_inf

    for __file in files:
        inf_list = []

        ns = __file['Snapshot']['Nums']
        for n in ns:
            if ((n in action_infs) or (not action_infs)) and (inf_min <= n <= inf_max):
                inf_list.append(n)
            continue

        if inf_list:
            file = copy.deepcopy(__file)  # не изменять оригинальный файл
            file['Snapshot']['Nums'] = sorted(inf_list)

            for data in search_data:  # обновить(не заменить) ключи
                dt = search_data[data]
                file[data].update(dt)
                continue

            yield file
            continue

        continue
    return


def set_param_in_action_inf(action: 'lr_lib.gui.action.main_action.ActionWindow', param: str) -> Iterable[int]:
    """
    первый action-inf в котором расположен param, тк inf-номер запроса <= inf-номер web_reg_save_param
    """
    webs = action.web_action.get_web_snapshot_all()
    for web_ in webs:
        wr = web_.param_find_replace(param)
        (allow, deny) = wr
        if allow:
            i = web_.snapshot.inf
            yield i
        continue
    return 0


def get_search_data(param: str) -> dict:
    """
    данные, для поиска param в AllFiles
    """
    search_data = dict(
        Param=dict(
            Name=param,
            inf_min=lr_vars.VarSearchMinSnapshot.get(),
            len=(len(param) if hasattr(param, '__len__') else None),
            inf_max=lr_vars.VarSearchMaxSnapshot.get(),
            NotPrintable=lr_lib.core.etc.other.not_printable(param),
        ),
        File=dict(
            encoding=lr_lib.core.var.etc.vars_other.VarEncode.get(),
        ),
    )
    return search_data


def get_files_with_param(param: str, action=None, set_file=True, execute=None,) -> None:
    """
    найти файлы с param
    """
    param = (param or lr_vars.VarParam.get())  # (1)
    search_data = get_search_data(param)

    files = tuple(create_files_with_search_data(lr_vars.AllFiles, search_data, action=action))
    assert files, 'Не найдены файлы, подходящие, под условия поиска. {}\nsearch_data: {}'.format(action, search_data)

    g = lr_vars.VarStrongSearchInFile.get()
    param_searcher = (search_param_in_file if g else _search_param_in_file)
    if execute is None:
        execute = (lr_vars.M_POOL.imap_unordered if lr_vars.FindParamPOOLEnable else map)

    # (2) поиск
    executer = execute(param_searcher, files)
    executer = filter(bool, executer)
    p_files = sorted(executer, key=lr_lib.core.etc.other.sort_files)
    lr_vars.FilesWithParam = p_files

    if not lr_vars.FilesWithParam:
        p = param_not_found_err_text(action, files, search_data, param)
        raise UserWarning(p)

    if lr_vars.VarFirstLastFile.get():
        lr_vars.FilesWithParam.reverse()
        ff = lr_vars.FilesWithParam[0]
        mai = ff['Param']['max_action_inf']

        files_list = []
        warn_inf = []
        for f in lr_vars.FilesWithParam:  # z_k620
            s = f['Snapshot']['Nums']
            s = s[0]
            ob = (warn_inf if (s == mai) else files_list)
            ob.append(f)
            continue
        files_list.extend(warn_inf)
        lr_vars.FilesWithParam = files_list

    if set_file:  # VarFileName.set
        file = lr_vars.FilesWithParam[0]
        assert isinstance(file, dict), len(lr_vars.FilesWithParam)
        name = file['File']['Name']
        lr_vars.VarFileName.set(name)  # (3)

    if lr_vars.VarFileNamesNumsShow.get():
        i = lr_lib.core.etc.other.param_files_info()
        lr_vars.Logger.info(i)
    return


Err = '''
'Не найдены файлы содержащие param "{param}"

search_data: {d}

Всего Snapshot {i}=[ t{ai_min}:t{ai_max} ]/файлов={f}
В action.c: Snapshot {ai}=[ t{a_min}:t{a_max} ] / Файлов={afa}
Поиск происходил в: Snapshot {lf}=[ t{min_iaf}:t{max_iaf} ] / файлах={f_}
Директория поиска: {folder}
откл чекб "strong", вероятно может помочь найти варианты
'''  #


def param_not_found_err_text(action, files: Tuple[dict], search_data: dict, param: str) -> str:
    """
    текст ошибки - param не найден
    """
    laf = len(lr_vars.AllFiles)
    if action:
        action_infs = action.web_action.action_infs
        lai = len(action_infs),
        a_min = min(action_infs),
        a_max = max(action_infs),
        law = len(action.web_action.drop_files)
        afa = (laf - law)
    else:
        lai = a_min = a_max = afa = None

    if files:
        f0 = files[0]
        fp = f0['Param']
        min_iaf = fp['inf_min']
        max_iaf = fp['inf_max']
    else:
        min_iaf = max_iaf = '?'

    tal = tuple(lr_lib.core.etc.other.get_files_infs(lr_vars.AllFiles))
    files_infs = len(tal)
    mt = max(tal)
    mit = min(tal)
    tu = tuple(lr_lib.core.etc.other.get_files_infs(files))
    lenfi = len(tu)
    fld = lr_vars.VarFilesFolder.get()
    lf = len(files)

    error = Err.format(
        ai_min=mit,
        ai=lai,
        afa=afa,
        f_=lf,
        param=param,
        ai_max=mt,
        folder=fld,
        i=files_infs,
        min_iaf=min_iaf,
        max_iaf=max_iaf,
        a_min=a_min,
        a_max=a_max,
        d=search_data,
        f=laf,
        lf=lenfi,
    )
    return error


def find_param_ord() -> Tuple[int, int]:
    """
    получить Ord
    """
    if lr_vars.VarOrdVersion.get():
        ord_index = find_param_ord_new()
    else:  # можно сравнить результат, при изменении алгоритма
        ord_index = find_param_ord_old()

    if ord_index:
        return ord_index

    t = 'Ord не найден\n{f}\n{w}'.format(f=lr_vars.VarFile.get(), w=lr_vars.VarWrspDict.get())
    raise UserWarning(t)


#
AIE1 = '''
Формирование Ord для web_reg_save_param невозможно, тк поле пусто
[param, lb, rb, text] == {empty}
VarWrspDict={wrsp}
VarPartNum={pn}, max={len_lbti}
VarFile={fl}
'''.strip()

AIE2 = '''
Формирование web_reg_save_param невозможно, тк файл не содержит LB(5)
{wrsp}
'''.strip()


def find_param_ord_old() -> Tuple[int, int]:
    """
    получить Ord, версия после 7.2.0
    """
    param = lr_vars.VarParam.get()
    lb = lr_vars.VarLB.get()
    rb = lr_vars.VarRB.get()
    text = lr_vars.VarFileText.get()
    items = (param, lb, rb, text, )

    lb_text_index = list(map(len, text.split(lb)))  # индексы для определения param в тексте
    len_lbti = len(lb_text_index)

    assert all(items), AIE1.format(
        wrsp=lr_vars.VarWrspDict.get(),
        empty=list(map(bool, items)),
        pn=lr_vars.VarPartNum.get(),
        len_lbti=len_lbti,
        fl=lr_vars.VarFile.get(),
    )
    assert (len_lbti > 1), AIE2.format(wrsp=lr_vars.VarWrspDict.get(),)

    (Ord, index) = (0, 0)  # искомый Ord, текущий LB index
    iter_index = iter(lb_text_index)  # следующий LB index
    next(iter_index, None)  # тк следующий
    param_rb = (param + rb)
    param_rb_len = len(param_rb)
    len_lb = len(lb)

    for i in lb_text_index:
        index += (i + len_lb)  # нижняя граница
        add_index = next(iter_index, 0)  # верхняя граница
        if add_index < param_rb_len:
            add_index = param_rb_len

        end = (index + add_index)
        part = text[index:end]  # text[текущий : следующий] LB index
        if rb in part:
            Ord += 1
            if part.startswith(param_rb):
                item = (Ord, index)
                return item
        continue
    return


def find_param_ord_new() -> Tuple[int, int]:
    """
    получить Ord, НОВАЯ!!! test - исправлена ошибка при проске ord
    """
    param = lr_vars.VarParam.get()
    lb = lr_vars.VarLB.get()
    rb = lr_vars.VarRB.get()
    text = lr_vars.VarFileText.get()
    items = (param, lb, rb, text,)

    len_lbti = len(text.split(lb))
    assert all(items), AIE1.format(
        wrsp=lr_vars.VarWrspDict.get(),
        empty=list(map(bool, items)),
        pn=lr_vars.VarPartNum.get(),
        len_lbti=len_lbti,
        fl=lr_vars.VarFile.get(),
    )
    assert (len_lbti > 1), AIE2.format(wrsp=lr_vars.VarWrspDict.get(), )

    Ord = 0
    for line in text.split('\n'):
        line += '\n'

        if (lb in line) and (rb in line):
            try:
                (other, data_) = line.split(lb, 1)
            except:
                continue
            else:
                if rb in data_:
                    try:
                        (_data, other) = data_.split(rb, 1)
                    except:
                        continue
                    else:
                        Ord += 1
                        if _data == param:
                            return Ord, 0
                        else:
                            while data_:
                                try:
                                    (other, data_) = data_.split(lb, 1)
                                except:
                                    break
                                else:
                                    if rb in data_:
                                        try:
                                            (_data, other) = data_.split(rb, 1)
                                        except:
                                            break
                                        else:
                                            Ord += 1
                                            if _data == param:
                                                return Ord, 0
                                    else:
                                        break
                                continue
        continue

    return find_param_ord_old()  # иначе старый способ
