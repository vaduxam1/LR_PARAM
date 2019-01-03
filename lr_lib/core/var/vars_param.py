# -*- coding: UTF-8 -*-
# общие переменные, настройки - param, web и файлы

import string

########
# param
Params_names = {
    'zkau_', 'Desktop_', 'index_', 'editWindow_', 'zul_', 'z_', 'nV0', 'iEK', 'aFF', 'adv_upload_',
}  # "начало" имен для поиска param(1)

LB_PARAM_FIND_LIST = [
    'sessionid=',
    'docSessionId=',
    'Value=',
    'UID=',
    'row.id=',
    'value="',
    ':[\\"',
    'appid=\\"',
    'contentId\\":\\"',
    'reference\\":\\"',
    'items%22%3A%5B%22',
    'reference%22%3A%22',
    'dtid=',
    'items\\":[\\"',
    'ViewState" value="',
    'navigator.id="',
    '_sn=',
    'jdemafjascacheUID=',
    'jdemafjasUID=',
    '_adf.ctrl-state=',
    '_adf.winId=',
    '_adf.winId=',
    '_afrLoop=',
    '_adf.ctrlstate=',
    '_adfp_rendition_cahce_key=',
    '_adfp_request_hash=',
    '_adfp_full_page_mode_request=',
    '_afrLoop=',
    '_afrWindowMode=',
    '_afrWindowId=',
    '_afPfm=',
    '_rtrnId=',
    'dfp_request_id=',
    'ViewState=',
    '/consumer/',
    'PSI=',
]  # использовать для поиска param(1) по LB=

DENY_Startswitch_PARAMS = [
    'opt_', 'cmd_', 'data_', 'uuid_',
    ]  # не использовать в качестве параметров, если начинаются так

DENY_PARAMS = [
    'UTF-8', 'boot', 'true', 'false', 'i', 'xonLoadUseIndustrialCalendar', 'dummy', 'CPAGE', 'null', 'pt1', 'cb1', 'f1',
    'POST', 'HTML', 'Yes', 'dtid', 'compId', 'this', 'left', 'right', 'top', 'bottom', 'open', 'pageY', 'pageX',
    'value', 'which', 'items', 'reference', 'selectAll', 'clearFirst',
]  # не использовать в качестве параметров

REGEXP_PARAMS = [
    '\"(.+?)\"',
    '\"(.+?)\\\\"',
    # '\\\\"(.+?)\\\\"',
    '\'(.+?)\'',
    '=(.+?)\"',
    '=(.+?)\'',

    '"(.+?)"',
    '=(.+?)&',
]  # поиск param, на основе регулярных выражений re.findall(regexp, text)

LRB_rep_list = [
    'zul', 'path', 'Set', 'wnd', 'sel', 'inp', 'dt', 'wgt', 'imp', 'false', 'true', 'visible', 'cmd', 'label', 'zclass',
    'btn', 'menu', 'tab', 'cmb', 'amp', 'id',
]  # не использовать эти слова в LB/RB, для wrsp имени param

MutableLBRegs = [
    r'uuid_\d=',
    r'p_p_col_count=\d&',
]  # дополнитеные "вариативные" LB для поиска param

# LB/RB обрежутся до этих строк
_SplitList0 = list('{},=$')
_SplitList1 = list('{}=$;,')
_SplitList2 = ['\\n', '\\', '"']
_SplitList_3 = (_SplitList1 + _SplitList2)
SplitList = tuple(_SplitList0 + _SplitList2 + list(string.digits))

StripLBEnd1 = ['{', '}', '[', ']', ]
StripLBEnd2 = ['},', ]
StripLBEnd3 = ['{', ',', ]
StripRBEnd1 = ['{', '}', '[', ']', ]
StripRBEnd2 = [',{', ]
StripRBEnd3 = ['{', ',']

Screening = ['\\', '"', ]  # символы для экранирования слешем
AddAllowParamSymb = '_!-'  # символы, которые могут входить в имя param, кроме букв и цифр

# символы обрезки автозамены
param_splitters = (string.punctuation + string.whitespace)
for s in AddAllowParamSymb:
    param_splitters = param_splitters.replace(s, '')
    continue
param_splitters = set(param_splitters)

########
# web
DENY_WEB_ = {
    'google.com', 'yandex.ru', 'mail.ru',
}  # web_ запросы, содержащие эти слова, помечять WARNING

########
# файлы
_FileOptions = (
    'FileName',
    'ResponseHeaderFile',
    'SnapshotXmlFile',
)
FileOptionsStartswith = set(map(str.lower, _FileOptions))  # секции в inf-файле, c файлами-ответов
DENY_FILES = {
    'CodeGenerationLog.txt', 'CorrelationLog.txt',
}  # файлы, исключенные из поиска param
DENY_PART_NAME = {
    '_RequestHeader', '_RequestBody',
}
DENY_EXT = {
    '.inf', '.ico', '.gif', '.jpg', '.jpeg', '.bmp', '.tif', '.png', '.zip', '.rar', '.7z', '.gz', '.tar', '.c', '.css',
}
