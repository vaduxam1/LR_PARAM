# -*- coding: UTF-8 -*-
# общие переменные, настройки

import os
import time
import string
import itertools
import functools
import multiprocessing
import encodings.aliases

import tkinter as tk

from lr_lib.core.var.var import (Var, )
from lr_lib.etc.help import (COLORS, HEX, )


#####################################
# главные переменные

VERSION = 'v10.5.0'
lib_folder = 'lr_lib'
Tk = tk.Tk()  # tkinter
original_callback_exception = Tk.report_callback_exception

Window = None  # класс gui окна # lr_lib.gui.wrsp.main_window.Window
AllFiles = []  # все файлы ответов
FilesWithParam = []  # файлы ответов, с param
VarParam = Var(value='')  # {param} для поиска
VarFileName = Var(value='')  # выбранное имя файла с {param}
VarFile = Var(value={})  # выбранный словарь файла с {param}
VarPartNum = Var(value=0)  # номер вхождения param
VarLB = Var(value='')  # текст LB
VarRB = Var(value='')  # текст RB
VarFileText = Var(value='')  # тект файла
VarWrspDict = Var(value={})  # текущий web_reg_save_param словарь
VarWrspDictList = []  # все возможные web_reg_save_param словари, для данного param

#####################################
# статистика в каментах

VarWebStatsTransac = tk.BooleanVar(value=False)  # коментарии с именем транзакции
VarWebStatsIn = tk.BooleanVar(value=False)  # In коментарии
VarWebStatsOut = tk.BooleanVar(value=False)  # Out коментарии
VarWebStatsWarn = tk.BooleanVar(value=False)  # Warning коментарии
VarWRSPStatsTransac = tk.BooleanVar(value=False)  # для wrsp, статистика использования param
VarWRSPStatsTransacNames = tk.BooleanVar(value=False)  # для wrsp, имена транзакций в которых используется param
VarWRSPStats = tk.BooleanVar(value=False)  # для wrsp, создавать подробные/короткие коментарии

DENY_WEB_ = {
    'google.com', 'yandex.ru', 'mail.ru',
}  # web_ запросы, содержащие эти слова, помечять WARNING

#####################################
# поиск web_reg_save_param

Params_names = {
    'zkau_', 'Desktop_', 'index_', 'editWindow_', 'zul_', 'z_', 'nV0', 'iEK', 'aFF', 'adv_upload_',
}  # "начало" имен для поиска param(1)

LB_PARAM_FIND_LIST = [
    'sessionid=',
    'docSessionId=',
    'Value=', 'UID=',
    'row.id=',
    'row.id="',
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
    'POST', 'HTML', 'Yes', 'dtid', 'compId',
]  # не использовать в качестве параметров

REGEXP_PARAMS = [
    '\"(.+?)\"',
    '\"(.+?)\\\\"',
    # '\\\\"(.+?)\\\\"',
    '\'(.+?)\'',
    '=(.+?)\"',
    '=(.+?)\'',
]  # поиск param, на основе регулярных выражений re.findall(regexp, text)

FindParamPOOLEnable = True  # использовать M_POOL, для поиска param, в файлах ответов
VarStrongSearchInFile = tk.IntVar(value=True)  # принудительно использовать контроль LB/RB(на недопустимые символы), при поиске param, в файлах ответов
ReplaceParamDialogWindow = True  # вкл диалог окна(автозамены), для одиночной замены param в action.c

VarFileSortKey1 = Var(value='Snapshot')  # сортировка файлов
VarFileSortKey2 = Var(value='Nums')  # сортировка файлов
VarFirstLastFile = tk.IntVar(value=0)  # 0=первый, выбрать последний или первый файл из FilesWithParam
VarOrdVersion = tk.IntVar(value=1)  # версия(старая/новая) функции для получения Ord, например если не ищется?
VarFileNamesNumsShow = tk.BooleanVar(value=True)  # показывать инфо о найденых файлах с param
VarSearchMinSnapshot = tk.IntVar(value=-1)  # ограничение(для поиска param) минимального номера inf файла
VarSearchMaxSnapshot = tk.IntVar(value=-1)  # ограничение(для поиска param) максимального номера inf файла

cbxClearShowVar = False  # mainWind: перед (2), очищать центральный виджет текста
cbxWrspClipboard = False  # mainWind: после (2), копировать web_reg_save_param в буфер обмена
cbxWrspAutoCreate = True  # mainWind: после (2), выполнять (3)-(6)
cbxNotepadWrsp = False  # mainWind: после (2), открывать web_reg_save_param в блокноте

#####################################
# имя web_reg_save_param

MaxLbWrspName = tk.IntVar(value=25)  # макс число символов, взятых из LB, для wrsp имени param
MaxRbWrspName = tk.IntVar(value=25)  # макс число символов, взятых из RB, для wrsp имени param
MaxParamWrspName = tk.IntVar(value=50)  # макс число символов, взятых из param, для wrsp имени param
MinWrspRnum = tk.IntVar(value=1000)  # мин число, для случайного номера, в wrsp имени param
MaxWrspRnum = tk.IntVar(value=9999)  # макс число, для случайного номера, в wrsp имени param
SnapshotInName = tk.BooleanVar(value=True)  # в wrsp имени param, отображать номер Snapshot, в котором создан wrsp
TransactionInNameMax = tk.IntVar(value=50)  # в wrsp имени param, отображать максимум символов transaction, в которой создан wrsp
WrspNameFirst = tk.StringVar(value='P')  # начало(P) wrsp имени param: {P_11_zkau_22}
wrsp_name_splitter = tk.StringVar(value='')  # символ разделения имени wrsp(для '_'): Win__aFFX9__id -> Win__a_FFX_9__id

LRB_rep_list = [
    'zul', 'path', 'Set', 'wnd', 'sel', 'inp', 'dt', 'wgt', 'imp', 'false', 'true', 'visible', 'cmd', 'label', 'zclass',
    'btn', 'menu', 'tab', 'cmb', 'amp', 'id',
]  # не использовать эти слова в LB/RB, для wrsp имени param

#####################################
# формирование LB RB

AskLbRbMaxLen = 30  # макс длина LB/RB, в вопросе при автозамене
DEFAULT_LB_RB_MIN_HEIGHT = 3  # высота полей LB/RB(5)
VarActComboLenMin = tk.IntVar(value=2)  # min ширина Listbox виджетов
VarActComboLenMax = tk.IntVar(value=75)  # max ширина Listbox виджетов
VarMaxComboFilesWidth = Var(value=75)  # макс ширина combobox выбора файлов(3)
MaxFileStringWidth = 250  # макс ширина подсказки для файлов(3)

DefaultActionForceAsk = False  # Автозамена - подтверждать любую замену
DefaultActionNoVar = True  # Автозамена - Принудительно отвечать "Нет, для Всех" в вопросе замены
DefaultActionMaxSnapshot = True  # ограничить диапазон поиска param - максимальный номер inf
DefaultActionAddSnapshot = True  # ограничить максимальный inf, не номером(param_inf - 1), а самим param-inf номером
DefaultActionForceYes = True  # отвечать "Да", при вопросе о создании param, если inf-номер запроса <= inf-номер web_reg_save_param
DefaultActionFinalWind = True  # окно результата создания param

VarPartNumEmptyLbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при пустом LB/RB(5)
VarPartNumDenyLbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при недопустимом LB/RB(5)
VarMaxLenLB = tk.IntVar(value=100)  # максимальная длина строк LB
VarReturnLB = tk.BooleanVar(value=True)  # обрезать LB до переноса строки
VarRusLB = tk.BooleanVar(value=False)  # обрезать LB до непечатных либо русских символов

VarLbB1 = tk.BooleanVar(value=True)  # по LB определить, если param находится внутри фигурных скобок
VarLbB2 = tk.BooleanVar(value=True)  # по LB определить, если param находится внутри квадратных скобок
VarLbLstrip = tk.BooleanVar(value=True)  # обрезать LB
VarLEnd = tk.BooleanVar(value=True)  # обрезать LB

VarPartNumEmptyRbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при пустом LB/RB(5)
VarPartNumDenyRbNext = tk.BooleanVar(value=True)  # Использовать следующий номер вхождения(4) или файл(3), при недопустимом LB/RB(5)
VarMaxLenRB = tk.IntVar(value=100)  # максимальная длина строк RB
VarReturnRB = tk.BooleanVar(value=True)  # обрезать RB до переноса строки
VarRusRB = tk.BooleanVar(value=False)  # обрезать RB до непечатных либо русских символов

VarRbB1 = tk.BooleanVar(value=True)  # по RB определить, если param находится внутри фигурных скобок
VarRbB2 = tk.BooleanVar(value=True)  # по RB определить, если param находится внутри квадратных скобок
VarRbRstrip = tk.BooleanVar(value=True)  # обрезать RB
VarREnd = tk.BooleanVar(value=True)  # обрезать RB

# LB/RB обрежутся до этих строк
_SplitList0 = list('{},=$')
_SplitList1 = list('{}=$;,')
_SplitList2 = ['\\n', '\\', '"']
_SplitList_3 = _SplitList1 + _SplitList2
SplitList = tuple(_SplitList0 + _SplitList2 + list(string.digits))

StripLBEnd1 = ['{', '}', '[', ']', ]
StripLBEnd2 = ['},', ]
StripLBEnd3 = ['{', ',', ]

StripRBEnd1 = ['{', '}', '[', ']', ]
StripRBEnd2 = [',{', ]
StripRBEnd3 = ['{', ',']

# символы для экранирования слешем
Screening = ['\\', '"', ]

VarSplitListLB = tk.BooleanVar(value=True)  # обрезать LB до SplitList строк
VarSplitListRB = tk.BooleanVar(value=True)  # обрезать RB до SplitList строк
VarSplitListNumLB = tk.IntVar(value=3)  # Не учитывать n символов LB(последние), при SplitList обрезке
VarSplitListNumRB = tk.IntVar(value=2)  # Не учитывать n символов RB(первые), при SplitList обрезке


# символы, которые могут входить в имя param, кроме букв и цифр
AddAllowParamSymb = '_!-'

# символы обрезки автозамены
allow_symbols = string.punctuation + string.whitespace
for s in AddAllowParamSymb:
    allow_symbols = allow_symbols.replace(s, '')
allow_symbols = set(allow_symbols)

#####################################
# gui

_Tk_WIND_SIZE = [420, 600]  # размер главного окна
_Tk_ActionWIND_SIZE = [1100, 600]  # размер action окна

_Tk_LegendWIND_SIZE = [600, 325]  # размер legend окна
LegendHight = 250  # расстояние между верхом и низом легенды
Legend_minimal_canvas_size = (25000, 2500)  # перврначальная длина скроллов
Legend_scroll_len_modificator = 75  # модификатор длины скроллов (увеличить, если canvas не умещается в окно)

VarShowPopupWindow = tk.BooleanVar(value=True)  # показ popup - ошибок, финальных и др окон
PRINT_SEPARATOR = '_' * 50  # строка разделитель сообщений
VarToolTipTimeout = tk.StringVar(value=9000)  # время жизни всплывающкй подсказки, в мс

ToolTipFont = ('Arial', '7', 'bold italic')  # всплывающие подсказки
DefaultFont = 'Arial 7'  # шрифт кнопок и тд
DefaultLBRBFont = 'Arial 8 bold'  # шрифт LB/RB(5)
InfoLabelUpdateTime = tk.IntVar(value=2000)  # (мс) обновление action.label с процентами и пулом

DefaultActionHighlightFont = 'Eras Medium ITC'  # шрифт подсвеченного текста action
DefaultActionHighlightFontSize = 9  # размер подсвеченного шрифта текста action
DefaultActionHighlightFontBold = False  #
DefaultHighlightActionFontOverstrike = False  #
DefaultActionHighlightFontUnderline = False  #
DefaultHighlightActionFontSlant = False  #

DefaultActionNoHighlightFont = 'Georgia'  # шрифт текста action
DefaultActionNoHighlightFontSize = 9  # размер шрифта текста action
DefaultActionNoHighlightFontBold = False  #
DefaultActionNoHighlightFontOverstrike = False  #
DefaultActionNoHighlightFontUnderline = False  #
DefaultActionNoHighlightFontSlant = True  #

var_bar_1 = False  # show/hide main bar
var_bar_2 = False  # show/hide navigation bar
var_bar_3 = False  # show/hide info bar

#####################################
# подсветка

HighlightOn = True  # включить подсветку
HighlightAfter0 = 250  # задержка(мс), перед перезапуском проверки необходимости подсветки
HighlightAfter1 = 45  # задержка(мс), перед стартом подсветки всех линий, отображенных на экране
HighlightAfter2 = 100  # задержка(мс), перед подсветкой одной линии
Background = 'khaki'

highlight_words_folder = os.path.join(lib_folder, 'etc')
highlight_words_main_file = os.path.join(highlight_words_folder, 'highlight_words.txt')
highlight_words_files_startswith = 'highlight_words'

ColorIterator = itertools.cycle(COLORS.keys() - {'black'})
VarColorTeg = Var(value=set(COLORS.keys()))


def _unpunct(st: str) -> str:
    """без пунктуации в конце строки"""
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
for file in next(os.walk(highlight_words_folder))[2]:
    if file.startswith(highlight_words_files_startswith):
        with open(os.path.join(highlight_words_folder, file)) as hws:
            for line in hws:
                lr = line.rstrip('\n')
                ls = lr.strip()
                if ls and not ls.startswith('#'):
                    highlight_words.add(lr)

highlight_words.update(COLORS.keys())
highlight_words.update(HEX)
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
        'purple': _LB_LIST_highlight,
    },
}

DefaultColor = 'olive'  # цвет для "фонового" текста
hex_unicode_ground = 'foreground'  # \\xCE\\xE1
hex_unicode_color = 'olive'  # \\xCE\\xE1
PunctDigitTag = 'foregroundblack'
RusTag = 'backgroundorange'
wrsp_color1 = 'chartreuse'
wrsp_color2 = 'darkblue'

ForceOlive = (
    'value=xon', 'value=on', 'value={\\"left\\', 'value=i"', 'value={}', 'value={\\"', 'value=dummy',
    'value={\\"command',
)  # всегда подсвечивать olive цветом

ColorMainTegStartswith = 'background'  # не подсветит другим тегом, если подсвечено этим
OliveChildTeg = 'foregroundolive'  # не подсветит этим тегом, если подсвечено любым другим
minus_teg = {OliveChildTeg}  # other_tegs = (tegs_indxs.keys() - minus_teg)

web_reg_highlight_len = 6  # выделить начало имени web_reg_save_param

#####################################
# Backup

BackupActionFile = 100  # макс(по кругу) кол-во backup файлов
BackupFolder = 'lr_backup'
BackupName = '{i}_backup_{ind}_action.c'

#####################################
# область выделения двойным кликом мыши

# this first statement triggers tcl to autoload the library # that defines the variables we want to override.
Tk.tk.call('tcl_wordBreakAfter', '', 0)
# this defines what tcl considers to be a "word". For more # information see http://www.tcl.tk/man/tcl8.5/TclCmd/library.htm#M19
Tk.tk.call('set', 'tcl_wordchars', '[a-zA-Z0-9_.!-]')
Tk.tk.call('set', 'tcl_nonwordchars', '[^a-zA-Z0-9_.!-]')

# #####################################
# логирование

Logger = None  # lr_lib.etc.logger.Logger # вывод сообщений во все Handler: Logger.info('m', notepad=True, parent=act)

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
EHOME, EEND = [3, 1]  # при ошибке, показать строк выше/ниже, строки в файле-кода

#####################################
# поиск файлов ответов, при старте

DEFAULT_FILES_FOLDER = 'data'  # каталог поиска
DEFAULT_FILES_FOLDER = os.path.realpath(DEFAULT_FILES_FOLDER) if os.path.isdir(DEFAULT_FILES_FOLDER) else os.getcwd()
FileOptionsStartswith = {s.lower() for s in (
    'FileName', 'ResponseHeaderFile', 'SnapshotXmlFile',
)}  # секции в inf-файле, c файлами-ответов

# файлы, исключенные из поиска param
DENY_FILES = {
    'CodeGenerationLog.txt', 'CorrelationLog.txt',
}
DENY_PART_NAME = {
    '_RequestHeader', '_RequestBody',
}
DENY_EXT = {
    '.inf', '.ico', '.gif', '.jpg', '.jpeg', '.bmp', '.tif', '.png', '.zip', '.rar', '.7z', '.gz', '.tar', '.c', '.css',
}

VarFilesFolder = tk.StringVar(value=DEFAULT_FILES_FOLDER)  # каталог с файлами
VarIsSnapshotFiles = tk.BooleanVar(value=True)  # брать файлы, проаписанные в inf файлах каталога / или все файлы
VarAllowDenyFiles = tk.BooleanVar(value=False)  # разрешить поиск, в DENY_ исключенных из поиска файлах
VarAllFilesStatistic = tk.IntVar(value=False)  # при старте, создавать подробную статистику файлов(размер, символы и тд), сильно замедляет старт утилиты
SetFilesPOOLEnable = True  # использовать M_POOL, для создания файлов, при старте программы
FilesCreatePortionSize = 15  # порция, число обрабатываемых файлов, для создания из них файлой ответов, за один вызов/в одном потоке

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
# пулы

MainThreadUpdater = None  # выполнять callback из main потока # lr_lib.etc.pool.other.MainThreadUpdater
MainThreadUpdateTime = tk.IntVar(value=500)  # интервал(мс) проверки очереди, callback(из потоков) + скорость обновления подсветки

M_POOL = None  # пул процессов  # lr_lib.etc.pool.main_pool.POOL
M_POOL_NAME = 'multiprocessing.Pool'  # тип основной пул
cpu_count = multiprocessing.cpu_count()
M_POOL_Size = cpu_count if (cpu_count < 5) else 4  # основной MP пул(int/None)

T_POOL = None  # пул потоков # lr_lib.etc.pool.main_pool.POOL
T_POOL_NAME = 'SThreadPool(threading.Thread)'  # тип фоновый пул
# T_POOL_NAME = 'concurrent.futures.ThreadPoolExecutor'  # тип фоновый пул
T_POOL_Size = None  # фоновый T пул - любой(int>=2), concurrent.futures(int/None - авто)
# 'threading.Thread': SThreadPool - авто size
SThreadPoolSizeMin = tk.IntVar(value=1)  # SThreadPool min size(int)
SThreadPoolSizeMax = tk.IntVar(value=10)  # SThreadPool max size (int>=2)
SThreadExitTimeout = tk.IntVar(value=5)  # таймаут(сек) выхода, бездействующих потоков(до SThreadPoolSizeMin)
SThreadPoolAddMinQSize = tk.IntVar(value=100)  # мин длина очереди, для добавления, более чем одного потока, за раз
SThreadPooMaxAddThread = tk.IntVar(value=2)  # max число потоков, для добавления за один раз(до SThreadPoolSizeMax
SThreadAutoSizeTimeOut = tk.IntVar(value=1000)  # отзывчивость(мсек) - период опроса, для изменения размера пула
_SThreadMonitorUpdate = tk.IntVar(value=1000)  # мс, время обновления окна Window.pool_wind для текста состояния пула

#####################################
# etc

EDITOR = dict(exe='notepad.exe')  # программа для открытия "в Editor"

FIND_PARAM_HOTKEY = 'ctrl+shift+c'  # хоткей "найти(2) param"

#####################################
# чтото чтобы не импортировать лишнего


def T_POOL_decorator(func: callable):
    """декоратор, выполнения func в T_POOL потоке"""
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if hasattr(T_POOL, 'submit'):
            return T_POOL.submit(func, *args, **kwargs)
        elif hasattr(T_POOL, 'apply_async'):
            return T_POOL.apply_async(func, args, kwargs)
        else:
            raise AttributeError('у пула({p}) нет атрибута submit или apply_async\n{f}\n{a}\n{k}'.format(
                f=func, a=args, k=kwargs, p=T_POOL.pool))
    return wrap


def clearVars() -> None:
    """очистка Var's"""
    v = (VarParam, VarFileName, VarFile, VarPartNum, VarLB, VarRB, VarFileText, VarWrspDict, VarFileSortKey1, VarFileSortKey2, )
    for var in v:
        var.set(var.default_value, callback=False)
    FilesWithParam.clear()
