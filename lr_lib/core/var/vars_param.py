# -*- coding: UTF-8 -*-
# общие переменные, настройки - param, web и файлы

import itertools
import string
import tkinter as tk

import lr_lib.core
import lr_lib.core.var.vars_highlight

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


DENY_ENABLE = tk.BooleanVar(value=True)  # использовать ли фильтры DENY


DENY_Startswitch_PARAMS = (
    'opt_', 'cmd_', 'data_', 'uuid_',
)  # не использовать в качестве параметров, если начинаются так + цифры

DENY_Force_Startswitch_PARAMS = (
    'X-Atmosphere', 'Accept-', 'Adf-', 'X-Cache', 'click', 'selected', 'content-', 'doc-content', 'suppress', 'book_',
    'disclosed', '_adfp_', '_afrLocal', 'viewport', 'adfport', 'User-', 'Transfer-', 'vertical', 'z-slider', 'ico_',
    'z-paging', 'padding', 'fixed', 'eb-arp', 'eb-core', 'notif-', 'Qwerty', 'marker_', 'FK', 'paging', 'message',
    'document_', 'table_', 'combo_', 'scroller', 'import', 'export', 'service', 'copy_', 'details', 'Print', 'filter',
    'dropdown', 'expand_', 'arrow-', 'apply_', 'sufd-', 'groupbox', 'collapse_', 'x-www', 'funnel_', 'selecting_',
    'to_', 'miscel', 'doc_', 'id_', 'Cache-Control', 'notification', 'form-', 'after',
)  # не использовать в качестве параметров, если начинаются так

DENY_Force_Endswitch_PARAMS = set()  # не использовать в качестве параметров, если заканчивается так
DENY_Force_Contains_PARAMS = set()  # не использовать в качестве параметров, если содержит это
DENY_Force_Contains_Lower_PARAMS = set()  # не использовать в качестве параметров, если содержит это
DENY_Force_Contains_Lower_PARAMS = set(map(str.lower, DENY_Force_Contains_Lower_PARAMS))  # не использовать в качестве параметров, если содержит это
DENY_PARAMS_EQ = set()  # не использовать в качестве параметров, если ==

DENY_PARAMS_LOWER = {
    'UTF-8', 'boot', 'true', 'false', 'i', 'xonLoadUseIndustrialCalendar', 'dummy', 'CPAGE', 'null', 'pt1', 'itSearch',
    'cb1', 'f1', 'POST', 'HTML', 'Yes', 'dtid', 'compId', 'this', 'left', 'right', 'top', 'bottom', 'open', 'unique',
    'pageY', 'pageX', 'value', 'which', 'items', 'reference', 'selectAll', 'clearFirst', 'Referer', 'text', 'advradio',
    'otr', 'zul', 'user_name', 'user', 'name', 'password', 'jsessionid', 'sessionid', 'horizontal', 'inprogress',
    'fromServer', 'undefined', 'maximized', 'isLoaded', 'keypress', 'function', 'complete', 'textarea', 'ViewState',
    'checkbox', 'tabpanel', 'embedded', 'dblclick', 'boolean', 'checked', 'option', 'hidden', 'string',
    'normal', 'script', 'newPos', 'inline', 'number', 'before', 'radio', 'input', 'popup', 'self', 'cmd', 'advcheckbox',
    'margin', 'windowY', 'windowX', 'formatBlock', 'propertychange', 'plugin_resolved', 'uploadInfo', 'granted',
    'tmpobj', 'QTWeb', 'nodom', 'day', 'toolbar', 'Accept-Language', 'print_scroller', 'installCheckResult', 'javax',
    'timeZoneOffset', 'mouseleave', 'cls', 'setConstraint', 'dialog-edit', 'exitFullscreen', 'scrollable', 'between',
    'insertChildHTML_', 'zmousedown', '_target', '_minsize', 'DOMMouseScroll', 'resetSize_', 'shortName', 'context',
    'webkitRequestFullscreen', '_columns', 'loadCertificateContent', 'doFocus_', 'ZK-SID', 'before_center', 'Trim',
    'table-wrapper', '_closable', 'PATCH', '_posInfo', '_resizable', 'dialog', '056_Ispolnitely', '_adf', 'xmlns',
    '_columnsgroup', 'beforeSize', 'common-scroller', 'item-content', '_running', 'expand', 'resourceproxy', 'en-US',
    'timezone', 'DOMContentLoaded', 'mouseover', 'overrideTooltip', 'z-renderdefer', 'mailCount', 'multipart', 'annul',
    'zIndex', '_rows', 'head', 'Italic', 'getValue', 'zk_download', 'udu-webcenter', 'natural', 'checkJinn', 'add_line',
    'visibility', 'rowspan', '_doClick', 'ZK-Error', '_visible', 'onload', 'ru_RU', 'unlink', 'cryptoProPlugin',
    'Bold', '_src', 'icon', 'year', 'west', 'Blob', 'rows', 'Busy', 'Host', 'color', 'panel', 'outer', 'zhtml', 'forms',
    'unload', 'content_script', 'woff', 'ARP', 'signAttributes', 'MODApplet', 'selectedRowKeys', '_afrVblRws', 'bear',
    'getValueFromArrayById', 'zkau', 'username', 'styleClass', 'desktop', 'Content-Type', 'Resource', 'zk', 'rollback',
    'json', 'styles', 'sortDirection', 'charCode', 'autoSubmit', 'polling', 'xonLoadCal', 'valueChange', 'message',
    'combobox', 'blank', 'outcome', 'renderOnly', 'clientKey', 'clientId', 'editWindow', 'zkTheme', 'landscape',
    'portrait', 'keyCode', 'WebkitTransform', 'ZKClientInfo', 'ZKMatchMedia', 'images', 'doTooltipOver_', 'no-cache',
    'current', 'resultsOFcontrols', 'taskmanager', 'metadata', 'userProfile', 'ssl', 'loader', 'templates',
    'Navigation', '', 'None', 'Dropdown', 'AP', 'portlet', 'request_id', 'richClient', 'update', '177_Nikolaev',
    'javascript', 'fileSize', 'fileName', 'files', 'signature', 'upload',
}  # не использовать в качестве параметров, если lower соосветствие


def DENY_PARAMS_update_and_lower() -> None:
    """
    обновить DENY_PARAMS из highlight_words, после инита highlight_words
    """
    DENY_PARAMS_LOWER.update(lr_lib.core.var.vars_highlight.highlight_words)
    ldp = list(map(str.lower, map(str.strip, itertools.chain(DENY_PARAMS_LOWER, LRB_rep_list, LB_PARAM_FIND_LIST, ))))
    DENY_PARAMS_LOWER.clear()
    DENY_PARAMS_LOWER.update(ldp)
    return


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
_SplitList0 = list('{},=$?')
_SplitList1 = list('{}=$;,')
_SplitList2 = ['\\n', '\\', '"', ]
_SplitList_3 = (_SplitList1 + _SplitList2)
SplitList = tuple(_SplitList0 + _SplitList2 + list(string.digits))  # LB/RB обрежутся до этих строк

RbStartswithBoundFixed = [
    '&',
]  # если RB начинается так, дальше не брать, оставить это же

StripLBEnd1 = ['{', '}', '[', ']', ]
StripLBEnd2 = ['},', ]
StripLBEnd3 = ['{', ',', ]
StripRBEnd1 = ['{', '}', '[', ']', ]
StripRBEnd2 = [',{', ]
StripRBEnd3 = ['{', ',']  # символы обрезки для конца строка LB/RB

Screening = ['\\', '"', ]  # символы для экранирования слешем
AddAllowParamSymb = '_!-'  # символы, которые могут входить в имя param, кроме букв и цифр

param_valid_letters = (string.ascii_letters + string.digits + AddAllowParamSymb)  # символы из которых, может состоять param

# символы обрезки автозамены
param_splitters = (string.punctuation + string.whitespace)
for s in AddAllowParamSymb:
    param_splitters = param_splitters.replace(s, '')
    continue
param_splitters = set(param_splitters)  # символы обрезки автозамены

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
)  # секции ini LoarRunner файла для Response файлов

FileOptionsStartswith = set(map(str.lower, _FileOptions))  # секции в inf-файле, c файлами-ответов

DENY_FILES = {
    'CodeGenerationLog.txt', 'CorrelationLog.txt',
}  # файлы, исключенные из поиска param
DENY_PART_NAME = {
    '_RequestHeader', '_RequestBody',
}  # не испоьлзовать как файлы ответов

DENY_EXT = {
    '.inf', '.ico', '.gif', '.jpg', '.jpeg', '.bmp', '.tif', '.png', '.zip', '.rar', '.7z', '.gz', '.tar', '.c',
    '.css',
}  # запрещенные расширения файлов, для файлов-ответов
