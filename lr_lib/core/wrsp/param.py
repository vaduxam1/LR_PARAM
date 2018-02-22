# -*- coding: UTF-8 -*-
# формирование web_reg_save_param

import copy
import time
import random
import string

import lr_lib.core.etc.other as lr_other
import lr_lib.core.etc.lbrb_checker as lr_lbrb_checker
import lr_lib.core.var.vars as lr_vars
import lr_lib.etc.help as lr_help

LR_COMENT = '//lr:'

# имя web_reg_save_param
WEB_REG_NUM = '{letter}_{wrsp_rnd_num}_{infs}__{transaction}__{lb_name}__{wrsp_name}__{rb_name}'

_web_reg_save_param = """
// PARAM["{param}"] // Snap{inf_nums}
web_reg_save_param("{web_reg_name}",
    "LB={lb}",
    "RB={rb}",
    "Ord={param_ord}",
    "Search={search_key}",
    LAST); 
"""

web_reg_save_param = """
// Snap{inf_nums}, [{param_inf_min}:{param_inf_max}]={search_inf_len} -> [{_param_inf_min}:{_param_inf_max}]={_param_inf_all} | FILE["{Name}"], with_param = {file_index}/{param_files} | {create_time}
// PARAM["{param}"], count={param_part}/{param_count}, NA={param_NotPrintable} | LB[{Lb_len}~{lb_len}] NA={lb_NotPrintable}, RB[{Rb_len}~{rb_len}] NA={rb_NotPrintable}
web_reg_save_param("{web_reg_name}",
    "LB={lb}",
    "RB={rb}",
    "Ord={param_ord}",
    "Search={search_key}",
    LAST); 
"""

# !!! при редактировании web_reg_save_param, учесть что придется изменить wrsp_start/end, чтобы при автозамене, не заменялся param в коментарии // PARAM[{param}], и тд
wrsp_file_start = '| FILE["'
wrsp_file_end = '"],'

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
Snap = '%s{num}%s' % (Snap1, Snap2)
Web_LAST = 'LAST);'


def param_bounds_setter(param: str, start='{', end='}') -> str:
    """web_reg_save_param имя "P_1212_2_z_kau_1" -> "{P_1212_2_z_kau_1}" """
    if not param.startswith(start):
        param = start + param
    if not param.endswith(end):
        param += end
    return param


def create_web_reg_save_param(wrsp_dict=None) -> str:
    """сформировать web_reg_save_param"""
    if wrsp_dict is None:
        wrsp_dict = lr_vars.VarWrspDict.get()
    else:
        lr_vars.VarWrspDict.set(wrsp_dict)

    if lr_vars.VarWRSPStats.get():
        wrsp_string = web_reg_save_param
    else:
        wrsp_string = _web_reg_save_param

    return wrsp_string.format(**wrsp_dict)


def create_web_reg_save_param_and_dict(wrsp_dict=None) -> (str, dict):
    """сформировать web_reg_save_param и его словарь"""
    if wrsp_dict is None:
        wrsp_dict = lr_vars.VarWrspDict.get()

    return create_web_reg_save_param(wrsp_dict=wrsp_dict), wrsp_dict


wrsp_allow_symb = string.ascii_letters + string.digits + lr_vars.AddAllowParamSymb  # из каких символов, может состоять param
allow_lrb = set(
    string.ascii_letters + string.digits)  # из каких символов, может состоять lb rb части имени web_reg_save_param
wrsp_deny_punctuation = {ord(c): '' for c in string.punctuation.replace('_',
                                                                        '')}  # из каких символов, не может состоять имя web_reg_save_param
wrsp_deny_punctuation.update(
    {ord(c): '' for c in string.whitespace})  # из каких символов, не может состоять имя web_reg_save_param


def wrsp_dict_creator(is_param=True) -> dict:
    """сформировать данные для web_reg_save_param"""
    all_infs = tuple(lr_other.get_files_infs(lr_vars.AllFiles))
    param_infs = tuple(lr_other.get_files_infs(lr_vars.FilesWithParam))
    len_param_files = len(lr_vars.FilesWithParam)
    file = lr_vars.VarFile.get()
    param_num = lr_vars.VarPartNum.get() + 1  # нумерация с 0
    param_count = file['Param']['Count']
    Lb = lr_vars.VarLB.get()
    Rb = lr_vars.VarRB.get()

    # экранирование
    lb = screening_wrsp(Lb)
    rb = screening_wrsp(Rb)

    param = lr_vars.VarParam.get()
    if is_param:
        param_ord, param_index = find_param_ord()
    else:
        param_ord, param_index = -1, -1

    snapshots = file['Snapshot']['Nums']
    wrsp_name = wrsp_name_creator(param, Lb, Rb, snapshots[0])

    search_key = 'All'
    # if file['Snapshot']['inf_key'] == 'ResponseHeaderFile':
    #     search_key = 'Headers'

    web_reg_save_param_dict = dict(
        lb=lb,
        rb=rb,
        param_ord=param_ord,
        web_reg_name=wrsp_name,
        param_part=param_num,
        param_count=param_count,
        param_files=len_param_files,
        file_index=lr_vars.FilesWithParam.index(file) + 1,
        files_all=len(lr_vars.AllFiles),
        param_all=sum(f['Param']['Count'] for f in lr_vars.FilesWithParam),
        create_time=time.strftime('%H:%M:%S-%d/%m/%y'),
        inf_nums=snapshots,
        Lb_len=len(Lb),
        Rb_len=len(Rb),
        lb_len=len(lb),
        rb_len=len(rb),
        lb_NotPrintable=lr_other.not_printable(lb),
        rb_NotPrintable=lr_other.not_printable(rb),
        param_text_index=param_index,
        all_inf_min=min(all_infs),
        all_inf_max=max(all_infs),
        all_inf_len=len(all_infs),
        _param_inf_min=min(param_infs),
        _param_inf_max=max(param_infs),
        _param_inf_all=len(param_infs),
        search_key=search_key,
        param=param,
    )

    m1, m2 = file['Param']['inf_min'], file['Param']['inf_max']
    web_reg_save_param_dict['search_inf_len'] = len(list(i for i in all_infs if m1 <= i <= m2))
    # file['File'] ключи
    web_reg_save_param_dict.update(file['File'])
    # param_* ключи - file['Param']
    web_reg_save_param_dict.update({'param_{}'.format(k): v for k, v in file['Param'].items() if k != 'Name'})

    return web_reg_save_param_dict


def wrsp_name_creator(param: str, Lb: str, Rb: str, snapshot: int) -> str:
    """сформировать имя для web_reg_save_param(6)"""
    MaxLbWrspName = lr_vars.MaxLbWrspName.get()
    MaxRbWrspName = lr_vars.MaxRbWrspName.get()
    infs = (snapshot if lr_vars.SnapshotInName.get() else '')

    if MaxLbWrspName and (len(Lb) > 2):
        lbn = ['']
        for b in Lb:
            if b in allow_lrb:
                lbn[-1] += b
            elif lbn[-1]:
                lbn.append('')
        lbn = [b for b in filter(bool, lbn) if (b not in lr_vars.LRB_rep_list)]
        lb_name = '_'.join(sorted(set(lbn), key=lbn.index))[-MaxLbWrspName:]
    else:
        lb_name = ''

    if MaxRbWrspName and (len(Rb) > 2):
        rbn = ['']
        for b in Rb:
            if b in allow_lrb:
                rbn[-1] += b
            elif rbn[-1]:
                rbn.append('')
        rbn = [b for b in filter(bool, rbn) if (b not in lr_vars.LRB_rep_list)]
        rb_name = '_'.join(sorted(set(rbn), key=rbn.index))[:MaxRbWrspName]
    else:
        rb_name = ''

    p = tuple(filter(allow_lrb.__contains__, param))  # печатные символы искомого param
    jp = [p[0], ''.join(p[1:-1]), p[-1]]
    wrsp_param_name = lr_vars.wrsp_name_splitter.get().join(jp)
    MaxParamWrspName = lr_vars.MaxParamWrspName.get()
    if MaxParamWrspName:
        wrsp_param_name = wrsp_param_name[:MaxParamWrspName]

    MaxWrspRnum = lr_vars.MaxWrspRnum.get()
    wrsp_rnd_num = (random.randrange(lr_vars.MinWrspRnum.get(), MaxWrspRnum) if MaxWrspRnum else '')

    TransactionInNameMax = lr_vars.TransactionInNameMax.get()
    if TransactionInNameMax and lr_vars.Window:
        action = lr_vars.Window.get_main_action()
        web_action = action.web_action
        w = next(web_action.get_web_by(web_action.get_web_snapshot_all(), snapshot=snapshot))

        if w and w.transaction and (not w.transaction.startswith(web_action.transactions._no_transaction_name)):
            transaction = '_'.join(''.join(filter(str.isalnum, t)).translate(lr_help.TRANSLIT_DT)
                                   for t in w.transaction.split())
            transaction = transaction[:TransactionInNameMax]
        else:
            transaction = ''
    else:
        transaction = ''

    wrsp_name = WEB_REG_NUM.format(wrsp_rnd_num=wrsp_rnd_num, wrsp_name=wrsp_param_name, lb_name=lb_name,
                                   rb_name=rb_name,
                                   infs=infs, letter=lr_vars.WrspNameFirst.get(), transaction=transaction)

    wrsp_name = str.translate(wrsp_name, wrsp_deny_punctuation).rstrip('_')
    while '___' in wrsp_name:
        wrsp_name = wrsp_name.replace('___', '__')

    return wrsp_name


def screening_wrsp(s: str, t={ord(c): '\\{}'.format(c) for c in lr_vars.Screening}) -> str:
    """экранирование для web_reg_save_param"""
    return str.translate(s, t)


def _search_param_in_file(file: dict) -> dict:
    """найти кол-во {param} в файле, count - те все, без проверки на корректность"""
    File = file['File']
    Param = file['Param']
    param = Param['Name']

    with open(File['FullName'], encoding=File['encoding'], errors='ignore') as text:
        count = sum(line.count(param) for line in text)
        if count:
            Param['Count'] = count
            return file


def search_param_in_file(file: dict) -> (dict or None):
    """найти кол-во {param} в файле, с контролем LB RB"""
    File = file['File']
    Param = file['Param']
    param = Param['Name']
    Param['Count'] = 0
    Param['Count_indexs'] = []

    with open(File['FullName'], encoding=File['encoding'], errors='ignore') as text:
        split_line = text.read().split(param)
        split_len = len(split_line)
        if split_len < 2:
            return

        indx = 0
        for indx in range(1, split_len):
            i = indx - 1
            left = split_line[i]
            right = split_line[indx]
            if lr_lbrb_checker.check_bound_lb_rb(left, right):
                Param['Count_indexs'].append(i)

    if Param['Count_indexs']:
        Param['Count'] = indx
        Param['Count_indexs_len'] = len(Param['Count_indexs'])
        return file


def create_files_with_search_data(files: (dict,), search_data: dict, action=None, action_infs=()) -> iter((dict,)):
    """с учетом inf - создать копию файла и обновить search_data"""
    d = search_data['Param']
    inf_min = d['inf_min']
    inf_max = d['inf_max']

    if action:
        d['action_id'] = action.id_
        action_infs = action.web_action.action_infs

        inf_min = d['inf_min'] = min(action_infs or [-1])
        inf_max = d['inf_max'] = max(action_infs or [-1])
        d['max_action_inf'] = param_inf = set_param_in_action_inf(action, d['Name'])
        if not action.add_inf_cbx_var.get():
            param_inf -= 1  # inf, педшествующий номеру inf, где первый раз встречается pram
        if action.max_inf_cbx_var.get() and param_inf and (inf_max > param_inf):
            inf_max = d['inf_max'] = param_inf

    for __file in files:
        inf_list = []

        for n in __file['Snapshot']['Nums']:
            if ((n in action_infs) or (not action_infs)) and (inf_min <= n <= inf_max):
                inf_list.append(n)

        if inf_list:
            file = copy.deepcopy(__file)  # не изменять оригинальный файл
            file['Snapshot']['Nums'] = sorted(inf_list)
            for data in search_data:  # обновить(не заменить) ключи
                file[data].update(search_data[data])

            yield file


def set_param_in_action_inf(action, param: str) -> int:
    """первый action-inf в котором расположен param, тк inf-номер запроса <= inf-номер web_reg_save_param"""
    for web_ in action.web_action.get_web_snapshot_all():
        allow, deny = web_.param_find_replace(param)
        if allow:
            return web_.snapshot
    return 0


def get_search_data(param: str) -> dict:
    """данные, для поиска param в AllFiles"""
    search_data = dict(
        Param=dict(
            Name=param,
            inf_min=lr_vars.VarSearchMinSnapshot.get(),
            len=(len(param) if hasattr(param, '__len__') else None),
            inf_max=lr_vars.VarSearchMaxSnapshot.get(),
            NotPrintable=lr_other.not_printable(param),
        ),
        File=dict(
            encoding=lr_vars.VarEncode.get(),
        ),
    )
    return search_data


def get_files_with_param(param: str, action=None, set_file=True) -> None:
    """найти файлы с param"""
    param = param or lr_vars.VarParam.get()  # (1)
    search_data = get_search_data(param)

    files = tuple(create_files_with_search_data(lr_vars.AllFiles, search_data, action=action))
    assert files, 'Не найдены файлы, подходящие, под условия поиска. {}\nsearch_data: {}'.format(action, search_data)

    param_searcher = (search_param_in_file if lr_vars.VarStrongSearchInFile.get() else _search_param_in_file)
    execute = (lr_vars.M_POOL.imap_unordered if lr_vars.FindParamPOOLEnable else map)

    lr_vars.FilesWithParam = sorted(filter(bool, execute(param_searcher, files)), key=lr_other.sort_files)  # (2) поиск
    if not lr_vars.FilesWithParam:
        raise UserWarning(param_not_found_err_text(action, files, search_data, param))

    if set_file:
        file = lr_vars.FilesWithParam[-1 if lr_vars.VarFirstLastFile.get() else 0]
        assert isinstance(file, dict), len(lr_vars.FilesWithParam)
        lr_vars.VarFileName.set(file['File']['Name'])  # (3)

    if lr_vars.VarFileNamesNumsShow.get():
        lr_vars.Logger.info(lr_other.param_files_info())


def param_not_found_err_text(action, files: [dict, ], search_data: dict, param: str) -> str:
    """текст ошибки - param не найден"""
    if action:
        action_infs = action.web_action.action_infs
        lai, a_min, a_max, afa = (len(action_infs), min(action_infs), max(action_infs),
                                  (len(lr_vars.AllFiles) - len(action.web_action.drop_files)))
    else:
        lai = a_min = a_max = afa = None

    if files:
        min_iaf = files[0]['Param']['inf_min']
        max_iaf = files[0]['Param']['inf_max']
    else:
        min_iaf = max_iaf = '?'

    files_infs = len(tuple(lr_other.get_files_infs(lr_vars.AllFiles)))
    lenfi = len(tuple(lr_other.get_files_infs(files)))

    error = 'Не найдены файлы содержащие param "{param}"\n\nsearch_data: {d}\n\n' \
            'Всего Snapshot {i}=[ t{ai_min}:t{ai_max} ]/файлов={f}\n' \
            'В action.c: Snapshot {ai}=[ t{a_min}:t{a_max} ] / Файлов={afa}\n' \
            'Поиск происходил в: Snapshot {lf}=[ t{min_iaf}:t{max_iaf} ] / файлах={f_}\n' \
            'Директория поиска: {folder}\nоткл чекб "strong", вероятно может помочь найти варианты'.format(
        ai_min=min(tuple(lr_other.get_files_infs(lr_vars.AllFiles))), ai=lai, afa=afa, f_=len(files), param=param,
        ai_max=max(lr_other.get_files_infs(lr_vars.AllFiles)), folder=lr_vars.VarFilesFolder.get(), i=files_infs,
        min_iaf=min_iaf, max_iaf=max_iaf, a_min=a_min, a_max=a_max, d=search_data, f=len(lr_vars.AllFiles), lf=lenfi,)
    
    return error


def find_param_ord() -> (int, int):
    """получить Ord"""
    if lr_vars.VarOrdVersion.get():
        ord_index = new_find_param_ord()
    else:  # можно сравнить результат, при изменении алгоритма
        ord_index = old_find_param_ord()

    if ord_index:
        return ord_index

    raise UserWarning('Ord не найден\n{f}\n{w}'.format(f=lr_vars.VarFile.get(), w=lr_vars.VarWrspDict.get()))


def new_find_param_ord() -> (int, int):
    """получить Ord, версия после 7.2.0"""
    Items = param, lb, rb, text = (
        lr_vars.VarParam.get(), lr_vars.VarLB.get(), lr_vars.VarRB.get(), lr_vars.VarFileText.get()
    )

    lb_text_index = [len(part) for part in text.split(lb)]  # индексы для определения param в тексте
    len_lbti = len(lb_text_index)

    assert all(Items), 'Формирование Ord для web_reg_save_param невозможно, тк поле пусто\n' \
                       '[param, lb, rb, text] == {empty}\n' \
                       'VarWrspDict={wrsp}\nVarPartNum={pn}, max={len_lbti}\n' \
                       'VarFile={fl}'.format(
        wrsp=lr_vars.VarWrspDict.get(), empty=list(map(bool, Items)), pn=lr_vars.VarPartNum.get(), len_lbti=len_lbti,
        fl=lr_vars.VarFile.get(), )

    assert len_lbti > 1, 'Формирование web_reg_save_param невозможно, тк файл не содержит LB(5)\n' \
                         '{wrsp}'.format(wrsp=lr_vars.VarWrspDict.get())

    Ord, index = 0, 0  # искомый Ord, текущий LB index
    iter_index = iter(lb_text_index)  # следующий LB index
    next(iter_index, None)  # тк следующий
    param_rb = param + rb
    param_rb_len, len_lb = len(param_rb), len(lb)

    for i in lb_text_index:
        index += (i + len_lb)  # нижняя граница
        add_index = next(iter_index, 0)  # верхняя граница
        if add_index < param_rb_len:
            add_index = param_rb_len

        part = text[index:index + add_index]  # text[текущий : следующий] LB index
        if rb in part:
            Ord += 1
            if part.startswith(param_rb):
                return Ord, index


def old_find_param_ord() -> (int, int):
    """получить Ord, версия до 7.2.0 - не ищет ord если символы LB(начало) и RB(конец) пересекаются"""
    lb = lr_vars.VarLB.get()
    assert lb, 'Формирование web_reg_save_param невозможно, тк поле LB(5) пусто'
    rb = lr_vars.VarRB.get()
    assert rb, 'Формирование web_reg_save_param невозможно, тк поле RB(5) пусто'
    text = lr_vars.VarFileText.get()
    assert text, 'Формирование web_reg_save_param невозможно, тк файл пустой {}'.format(lr_vars.VarFile.get())
    param = lr_vars.VarParam.get()
    assert param, 'Формирование web_reg_save_param невозможно, тк param пустой'
    split_lb_text = text.split(lb)  # разбить по левой(LB) части
    split_len = len(split_lb_text)
    assert split_len > 1, 'Формирование web_reg_save_param невозможно, тк файл не содержит LB( {lb} )'.format(lb=lb)
    param_rb = param + rb
    Ord = 0
    for part in split_lb_text[1:]:  # слева, от первой LB части, не может быть RB
        if rb in part:
            Ord += 1
            if part.startswith(param_rb):
                _param_text_index = text.index(lb + param_rb) + len(lb)
                return Ord, _param_text_index
