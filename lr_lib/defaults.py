﻿# -*- coding: UTF-8 -*-
# общие переменные, настройки

import os
import time
import string
import itertools
import multiprocessing
import encodings.aliases
import tkinter as tk

from lr_lib import (
    var_class as lr_var,
    help as lr_help,
)

#####################################
VERSION = 'v9.0.3'
lib_folder = 'lr_lib'
Tk = tk.Tk()

#####################################
FindParamPOOLEnable = True  # использовать M_POOL, для поиска param, в файлах ответов
VarStrongSearchInFile = tk.IntVar(value=True)  # принудительно использовать контроль LB/RB(на недопустимые символы), при поиске param, в файлах ответов
ReplaceParamDialogWindow = True  # вкл диалог окна(автозамены), для одиночной замены param в action.c

VarFileSortKey1 = lr_var.Var(value='Inf')  # сортировка файлов
VarFileSortKey2 = lr_var.Var(value='Nums')  # сортировка файлов
VarFirstLastFile = tk.IntVar(value=0)  # 0=первый, выбрать последний или первый файл из FilesWithParam
VarOrdVersion = tk.IntVar(value=1)  # версия(старая/новая) функции для получения Ord, например если не ищется?
VarFileNamesNumsShow = tk.BooleanVar(value=True)  # показывать инфо о найденых файлах с param
VarSearchMinInf = tk.IntVar(value=-1)  # ограничение(для поиска param) минимального номера inf файла
VarSearchMaxInf = tk.IntVar(value=-1)  # ограничение(для поиска param) максимального номера inf файла

cbxClearShowVar = False  # mainWind: перед (2), очищать центральный виджет текста
cbxWrspClipboard = False  # mainWind: после (2), копировать web_reg_save_param в буфер обмена
cbxWrspAutoCreate = True  # mainWind: после (2), выполнять (3)-(6)
cbxNotepadWrsp = False  # mainWind: после (2), открывать web_reg_save_param в блокноте

#####################################
Params_names = {
    'zkau_', 'Desktop_', 'index_', 'editWindow_', 'zul_', 'z_', 'nV0', 'iEK', 'aFF', 'adv_upload_',
}  # "начало" имен для поиска param(1)

LB_PARAM_FIND_LIST = [
    'sessionid=', 'docSessionId=', 'Value=', 'UID=', 'row.id=', 'row.id="', 'value="', ':[\\"', 'appid=\\"',
    'contentId\\":\\"', 'reference\\":\\"', 'items%22%3A%5B%22', 'reference%22%3A%22', 'dtid=', 'items\\":[\\"',
    'ViewState" value="', 'navigator.id="', '_sn=', 'jdemafjascacheUID=', 'jdemafjasUID=', '_adf.ctrl-state=',
    '_adf.winId=', '_adf.winId=', '_afrLoop=', '_adf.ctrlstate=', '_adfp_rendition_cahce_key=',
    '_adfp_request_hash=', '_adfp_full_page_mode_request=', '_afrLoop=', '_afrWindowMode=', '_afrWindowId=',
    '_afPfm=', '_rtrnId=', 'dfp_request_id=', 'ViewState=', '/consumer/', 'PSI=',
]  # использовать для поиска param(1) по LB=

#####################################
_Tk_WIND_SIZE = [655, 700]  # размер главного окна
_Tk_ActionWIND_SIZE = [1200, 800]  # размер action окна

_Tk_LegendWIND_SIZE = [1200, 600]  # размер legend окна
LegendHight = 500  # расстояние между верхом и низом легенды
Legend_minimal_canvas_size = (25000, 1000)  # перврначальная длина скроллов
Legend_scroll_len_modificator = 75  # модификатор длины скроллов (увеличить, если canvas не умещается в окно)

VarShowPopupWindow = tk.BooleanVar(value=True)  # показ popup - ошибок, финальных и др окон
PRINT_SEPARATOR = '_' * 50  # строка разделитель сообщений
VarToolTipTimeout = tk.StringVar(value=9000)  # время жизни всплывающкй подсказки, в мс

ToolTipFont = ('Arial', '8')  # всплывающие подсказки
DefaultFont = 'Arial 8'  # шрифт кнопок и тд
DefaultLBRBFont = 'Arial 8 bold'  # шрифт LB/RB(5)

DefaultActionHighlightFont = 'Eras Medium ITC'  # шрифт подсвеченного текста action
DefaultActionHighlightFontSize = 9  # размер подсвеченного шрифта текста action
DefaultActionHighlightFontBold = False  #
DefaultHighlightActionFontOverstrike = False  #
DefaultActionHighlightFontUnderline = False  #
DefaultHighlightActionFontSlant = False  #

DefaultActionNoHighlightFont = 'Georgia'  # шрифт текста action
DefaultActionNoHighlightFontSize = 9  # размер шрифта текста action
DefaultActionNoHighlightFontBold = True  #
DefaultActionNoHighlightFontOverstrike = False  #
DefaultActionNoHighlightFontUnderline = False  #
DefaultActionNoHighlightFontSlant = True  #

#####################################
AskLbRbMaxLen = 30  # макс длина LB/RB, в вопросе при автозамене
DEFAULT_LB_RB_MIN_HEIGHT = 3  # высота полей LB/RB(5)
VarActComboLenMin = tk.IntVar(value=5)  # min ширина Listbox виджетов
VarActComboLenMax = tk.IntVar(value=75)  # max ширина Listbox виджетов
VarMaxComboFilesWidth = lr_var.Var(value=50)  # макс ширина combobox выбора файлов(3)
MaxFileStringWidth = 150  # макс ширина подсказки для файлов(3)

DefaultActionForceAsk = False  # Автозамена - подтверждать любую замену
DefaultActionNoVar = True  # Автозамена - Принудительно отвечать "Нет, для Всех" в вопросе замены
DefaultActionMaxInf = True  # ограничить диапазон поиска param - максимальный номер inf
DefaultActionAddInf = True  # ограничить максимальный inf, не номером(param_inf - 1), а самим param-inf номером
DefaultActionForceYes = True  # отвечать "Да", при вопросе о создании param, если inf-номер запроса <= inf-номер web_reg_save_param
DefaultActionFontcp1251 = False  # принудительная перекодировка(могут быть потери unicode текста)
DefaultActionFinalWind = True  # окно результата создания param

VarPartNumEmptyLbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при пустом LB/RB(5)
VarPartNumDenyLbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при недопустимом LB/RB(5)
VarMaxLenLB = tk.IntVar(value=90)  # максимальная длина строк LB
VarReturnLB = tk.BooleanVar(value=True)  # обрезать LB до переноса строки
VarRusLB = tk.BooleanVar(value=True)  # обрезать LB до непечатных либо русских символов

VarLbB1 = tk.BooleanVar(value=True)  # по LB определить, если param находится внутри фигурных скобок
VarLbB2 = tk.BooleanVar(value=True)  # по LB определить, если param находится внутри квадратных скобок
VarLbLstrip = tk.BooleanVar(value=True)  # обрезать LB
VarLEnd = tk.BooleanVar(value=True)  # обрезать LB

VarPartNumEmptyRbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при пустом LB/RB(5)
VarPartNumDenyRbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при недопустимом LB/RB(5)
VarMaxLenRB = tk.IntVar(value=90)  # максимальная длина строк RB
VarReturnRB = tk.BooleanVar(value=True)  # обрезать RB до переноса строки
VarRusRB = tk.BooleanVar(value=True)  # обрезать RB до непечатных либо русских символов

VarRbB1 = tk.BooleanVar(value=True)  # по RB определить, если param находится внутри фигурных скобок
VarRbB2 = tk.BooleanVar(value=True)  # по RB определить, если param находится внутри квадратных скобок
VarRbRstrip = tk.BooleanVar(value=True)  # обрезать RB
VarREnd = tk.BooleanVar(value=True)  # обрезать RB

#####################################
# символя для экранирования слешем
Screening = ['\\', '"', ]
# LB/RB обрежутся до этих строк
SplitList0 = list('{},=$')
SplitList1 = list('{}=$;,')
SplitList2 = ['\\n', '\\', '"']
SplitList_3 = SplitList1 + SplitList2
SplitList = tuple(SplitList0 + SplitList2 + list(string.digits))

VarSplitListLB = tk.BooleanVar(value=True)  # обрезать LB до SplitList строк
VarSplitListRB = tk.BooleanVar(value=True)  # обрезать RB до SplitList строк
VarSplitListNumLB = tk.IntVar(value=3)  # Не учитывать n символов LB(последние), при SplitList обрезке
VarSplitListNumRB = tk.IntVar(value=2)  # Не учитывать n символов RB(первые), при SplitList обрезке

# символы обрезки автозамены
allow_symbols = string.punctuation + string.whitespace
for s in '_!-':
    allow_symbols = allow_symbols.replace(s, '')
allow_symbols = set(allow_symbols)

#####################################
# {web_reg_save_param} имя param
MaxLbWrspName = 20  # макс число символов, взятых из LB, для wrsp имени param
MaxRbWrspName = 20  # макс число символов, взятых из RB, для wrsp имени param
MaxParamWrspName = 20  # макс число символов, взятых из param, для wrsp имени param
MinWrspRnum = 1000  # мин число, для случайного номера, в wrsp имени param
MaxWrspRnum = 9999  # макс число, для случайного номера, в wrsp имени param
LRB_rep_list = [
    'zul', 'path', 'Set', 'wnd', 'sel', 'inp', 'dt', 'wgt', 'imp', 'false', 'true', 'visible', 'cmd', 'label', 'zclass',
    'btn', 'menu', 'tab', 'cmb', 'amp',
]  # не использовать эти слова в LB/RB, для wrsp имени param

#####################################
EDITOR = dict(exe='notepad.exe')  # программа для открытия "в Editor"
FIND_PARAM_HOTKEY = 'ctrl+shift+c'  # хоткей "найти(2) param"

DENY_WEB_ = {
    'google.com', 'yandex.ru', 'mail.ru',
}  # web_ запросы, содержащие эти слова, помечять WARNING
DENY_PARAMS = [
    'UTF-8', 'boot', 'true', 'false', 'i', 'xonLoadUseIndustrialCalendar', 'dummy',
]  # не использовать в качестве параметров

#####################################
HighlightOn = True  # включить подсветку
HighlightThread = tk.BooleanVar(value=False)  # выполнять в фоне, весь код подсветки
LineTagAddThread = tk.BooleanVar(value=True)  # выполнять в фоне, код подсветки для одной линии
TagAddThread = tk.BooleanVar(value=False)  # выполнять в фоне, код подсветки для одного тега
HighlightMPool = tk.BooleanVar(value=False)  # искать индексы для подсветки линий, в M_POOL
HighlightLinesPortionSize = tk.IntVar(value=1)  # для скольки линий, искать индексы, за один проход/поток
Background = 'khaki'

highlight_words_main_file = os.path.join(lib_folder, 'highlight_words.txt')
highlight_words_files_startswith = 'highlight_words'

ColorIterator = itertools.cycle(lr_help.COLORS.keys() - {'black'})
VarColorTeg = lr_var.Var(value=set(lr_help.COLORS.keys()))


def _unpunct(st: str) -> str:
    '''без пунктуации в конце строки'''
    if st:
        if st[-1] in string.punctuation:
            return _unpunct(st[:-1])
        else:
            return st
    return ''

_LB_LIST_highlight = set(_unpunct(s) for s in LB_PARAM_FIND_LIST)
_LB_LIST_highlight.update({
    'uuid_', 'dtid', 'sessionid', 'Snapshot', 'Snapshot=t', 'EXTRARES', '.inf',
})

# слова для подсветки
highlight_words = set()
for file in next(os.walk(lib_folder))[2]:
    if file.startswith(highlight_words_files_startswith):
        with open(os.path.join(lib_folder, file)) as hws:
            for line in hws:
                lr = line.rstrip('\n')
                ls = lr.strip()
                if ls and not ls.startswith('#'):
                    highlight_words.add(lr)

highlight_words.update(lr_help.COLORS.keys())
highlight_words.update(lr_help.HEX)
for s in string.digits:
    highlight_words.add('Value={\\"\\":%s' % s)

tnrvf = set('\\{}'.format(s) for s in 'tnrvf')
highlight_words.update(tnrvf)

rd = {
    '/*', '*/', 'WARNING',
}
rd.update(DENY_WEB_)

VarDefaultColorTeg = {
    'background': {
        'orange': rd,
        'springgreen': {'lr_end_transaction', },
        'yellowgreen': {'lr_think_time',},
        'mediumspringgreen': {'lr_start_transaction', },
    },
    'foreground': {
        'olive': highlight_words,
        'black': {'[t', ':t', '=t', },
        'purple': _LB_LIST_highlight,
    },
}

PunctDigitTag = 'foregroundblack'
RusTag = 'backgroundorange'

ForceOlive = (
    'value=xon', 'value=on', 'value={\\"left\\', 'value=i"', 'value={}', 'value={\\"', 'value=dummy',
    'value={\\"command',
)  # всегда подсвечивать olive цветом

#####################################
BackupActionFile = 100  # 'макс кол-во backup файлов, перед автозаменой, в директорию lr_action_backup
BackupFolder = 'lr_backup'
BackupName = '{i}_backup_{ind}_action.c'

#####################################
# логирование
log_overdrive = 'a'
logFolder = 'lr_logs'
logName = 'server_%s.log' % time.strftime('%d.%m')
logPath = os.path.join(os.getcwd(), logFolder)
logFullName = os.path.join(logPath, logName)

loggingLevels = {
    'TRACE': 1,
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50,
    }

logger_level = 1  # loggingLevels

VarWindowLogger = tk.StringVar(value='INFO')  # минимальный уровень вывода сообщений в gui
EHOME, EEND = [6, 1]  # при ошибке, показать строк выше/ниже, строки в файле-кода

#####################################
DEFAULT_FILES_FOLDER = 'data'  # каталог поиска param
DEFAULT_FILES_FOLDER = os.path.realpath(DEFAULT_FILES_FOLDER) if os.path.isdir(DEFAULT_FILES_FOLDER) else os.getcwd()
FileOptionsStartswith = {
    'FileName', 'ResponseHeaderFile', 'SnapshotXmlFile',
}  # секции в inf-файле, c файлами-ответов

# файлы, исключенные из поиска param
DENY_FILES = {
    'CodeGenerationLog.txt', 'CorrelationLog.txt',
}
DENY_PART_NAMES = {
    '_RequestHeader', '_RequestBody',
}
DENY_EXT = {
    '.inf', '.ico', '.gif', '.jpg', '.jpeg', '.bmp', '.tif', '.png', '.zip', '.rar', '.7z', '.gz', '.tar', '.c', '.css',
}

VarFilesFolder = tk.StringVar(value=DEFAULT_FILES_FOLDER)  # каталог с файлами
VarIsInfFiles = tk.BooleanVar(value=True)  # брать файлы, проаписанные в inf файлах каталога / или все файлы
VarAllowDenyFiles = tk.BooleanVar(value=False)  # разрешить поиск, в DENY_ исключенных из поиска файлах
VarAllFilesStatistic = tk.IntVar(value=True)  # создавать подробную статистику файлов(размер, символы и тд), сильно замедляет старт утилиты
SetFilesPOOLEnable = True  # использовать M_POOL, для создания файлов, при старте программы
FilesCreatePortionSize = 25  # порция, число обрабатываемых файлов, для создания из них файлой ответов, за один вызов/в одном потоке

#####################################
# все кодировки
VarEncode = tk.StringVar(value='cp1251')  # используемая кодировка файлов
ENCODE_LIST = {
    'base64_codec', 'bz2_codec', 'cp1006', 'cp65001', 'cp720', 'cp737', 'cp856', 'cp874', 'cp875', 'hex_codec',
    'hp_roman8', 'koi8_u', 'mbcs', 'quopri_codec', 'rot_13', 'tactis', 'tis_620', 'utf_8_sig', 'uu_codec', 'zlib_codec',
}
ENCODE_LIST.update(set(encodings.aliases.aliases.values()))
ENCODE_LIST = list(sorted(ENCODE_LIST))

#####################################
MainThreadUpdateTime = tk.IntVar(value=500)  # интервал(мс) проверки очереди, для выполнения для главного потока, callback(из потоков)
cpu_count = multiprocessing.cpu_count()
M_POOL_NAME = 'multiprocessing.Pool'  # тип основной пул
T_POOL_NAME = 'SThreadPool(threading.Thread)'  # тип фоновый пул
M_POOL_Size = cpu_count if (cpu_count < 5) else 4  # основной MP пул(int/None)
T_POOL_Size = 4  # фоновый T пул(int>2 / None), кроме SThreadPool

# 'threading.Thread': SThreadPool - auto size
SThreadAutoSizeTimeOut = tk.IntVar(value=1000)  # отзывчивость(мсек) SThreadPool - период опроса, для изменения размера пула
SThreadPoolSizeMin = tk.IntVar(value=2)  # SThreadPool min size
SThreadPoolSizeMax = tk.IntVar(value=T_POOL_Size*2)  # SThreadPool max size (int>2)
SThreadPoolAddMinQSize = tk.IntVar(value=100)  # SThreadPool - минимальная длина очереди, для добавления, более чем одного потока, за раз
SThreadPooMaxAddThread = tk.IntVar(value=2)  # SThreadPool - max число потоков, для добавления за один раз(до SThreadPoolSizeMax)
SThreadExitTimeout = tk.IntVar(value=1)  # SThreadPool таймаут(сек) выхода, бездействующих потоков(до SThreadPoolSizeMin)
_SThreadMonitorUpdate = tk.IntVar(value=1000)  # SThreadPool (мс) время обновления popup окна Window.pool_wind для текста состояния пула

#####################################
Window = None  # класс gui окна
AllFiles = []  # все файлы ответов
FilesWithParam = []  # файлы ответов, с param
VarParam = lr_var.Var(value='')  # {param} для поиска
VarFileName = lr_var.Var(value='')  # выбранное имя файла с {param}
VarFile = lr_var.Var(value={})  # выбранный словарь файла с {param}
VarPartNum = lr_var.Var(value=0)  # номер вхождения param
VarLB = lr_var.Var(value='')  # текст LB
VarRB = lr_var.Var(value='')  # текст RB
VarFileText = lr_var.Var(value='')  # тект файла
VarWrspDict = lr_var.Var(value={})  # текущий web_reg_save_param словарь
VarWrspDictList = []  # все возможные web_reg_save_param словари, для данного param


def clearVars() -> None:
    '''очистка'''
    all_vars = [
        VarParam, VarFileName, VarFile, VarPartNum, VarLB, VarRB, VarFileText, VarWrspDict, VarFileSortKey1,
        VarFileSortKey2,
    ]
    for var in all_vars:
        var.set(var.default_value, callback=False)
    FilesWithParam.clear()