﻿# -*- coding: UTF-8 -*-
# общие переменные, настройки

import multiprocessing
import os
import time
import tkinter as tk

import lr_lib.core.var._var

#####################################
# главные переменные

VERSION = 'v11.5.3'  # версия утилиты
lib_folder = 'lr_lib'  # каталог py-файлов утилиты
Tk = tk.Tk()  # tkinter
original_callback_exception = Tk.report_callback_exception  # переопределение обработчика raise

Window = None  # класс gui окна # lr_lib.gui.wrsp.main_window.Window
AllFiles = []  # все файлы ответов
FilesWithParam = []  # файлы ответов, с param
VarParam = lr_lib.core.var._var.Var(value='')  # {param} для поиска
VarFileName = lr_lib.core.var._var.Var(value='')  # выбранное имя файла с {param}
VarFile = lr_lib.core.var._var.Var(value={})  # выбранный словарь файла с {param}
VarPartNum = lr_lib.core.var._var.Var(value=0)  # номер вхождения param
VarLB = lr_lib.core.var._var.Var(value='')  # текст LB
VarRB = lr_lib.core.var._var.Var(value='')  # текст RB
VarFileText = lr_lib.core.var._var.Var(value='')  # тект файла
VarWrspDict = lr_lib.core.var._var.Var(value={})  # текущий web_reg_save_param словарь
VarWrspDictList = []  # все возможные web_reg_save_param словари, для данного param

#####################################
# статистика в каментах
VarWebStatsTransac = tk.BooleanVar(value=False)  # коментарии с именем транзакции
VarWebStatsIn = tk.BooleanVar(value=False)  # In коментарии
VarWebStatsOut = tk.BooleanVar(value=False)  # Out коментарии
VarWebStatsWarn = tk.BooleanVar(value=True)  # Warning коментарии
VarWRSPStatsTransac = tk.BooleanVar(value=False)  # для wrsp, статистика использования param
VarWRSPStatsTransacNames = tk.BooleanVar(value=False)  # для wrsp, имена транзакций в которых используется param
VarWRSPStats = tk.BooleanVar(value=False)  # для wrsp, создавать подробные/короткие коментарии

#####################################
# поиск web_reg_save_param

SecondaryParamLen = tk.IntVar(value=3)  # число первых символов, взятых из param, для использования их при поиске одноименных param

MinParamLen = 3  # минимальная длина param
_MinParamLen = tk.IntVar(value=MinParamLen)  # минимальная длина param
MinParamLen -= 1  # тк нумерация с 0

MinParamNumsOnlyLen = tk.IntVar(value=5)  # минимальная длина param, состоящего только из цифр

FindParamPOOLEnable = True  # использовать M_POOL, для поиска param, в файлах ответов
VarStrongSearchInFile = tk.IntVar(value=True)  # принудительно использовать контроль LB/RB(на недопустимые символы), при поиске param, в файлах ответов
ReplaceParamDialogWindow = True  # вкл диалог окна(автозамены), для одиночной замены param в action.c

AllowOnlyNumericParam = tk.BooleanVar(value=True)  # разрешить имена {param}, состоящие только из цифр

VarFileSortKey1 = lr_lib.core.var._var.Var(value='Snapshot')  # сортировка файлов
VarFileSortKey2 = lr_lib.core.var._var.Var(value='Nums')  # сортировка файлов
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

#####################################
# формирование LB RB

AskLbRbMaxLen = 30  # макс длина LB/RB, в вопросе при автозамене
DEFAULT_LB_RB_MIN_HEIGHT = 3  # высота полей LB/RB(5)
VarActComboLenMin = tk.IntVar(value=2)  # min ширина Listbox виджетов
VarActComboLenMax = tk.IntVar(value=75)  # max ширина Listbox виджетов
VarMaxComboFilesWidth = lr_lib.core.var._var.Var(value=75)  # макс ширина combobox выбора файлов(3)
MaxFileStringWidth = 250  # макс ширина подсказки для файлов(3)

DefaultActionForceAsk = False  # Автозамена - подтверждать любую замену
DefaultActionNoVar = True  # Автозамена - Принудительно отвечать "Нет, для Всех" в вопросе замены
DefaultActionMaxSnapshot = True  # ограничить диапазон поиска param - максимальный номер inf
DefaultActionAddSnapshot = tk.BooleanVar(value=True)  # ограничить максимальный inf, не номером(param_inf - 1), а самим param-inf номером
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

VarSplitListLB = tk.BooleanVar(value=True)  # обрезать LB до SplitList строк
VarSplitListRB = tk.BooleanVar(value=True)  # обрезать RB до SplitList строк
VarSplitListNumLB = tk.IntVar(value=3)  # Не учитывать n символов LB(последние), при SplitList обрезке
VarSplitListNumRB = tk.IntVar(value=2)  # Не учитывать n символов RB(первые), при SplitList обрезке

#####################################
# gui

_Tk_WIND_SIZE = [600, 700]  # размер главного окна
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
InfoLabelUpdateTime = tk.IntVar(value=1500)  # (мс) обновление linenumbers + action.label с процентами и пулом

DefaultActionHighlightFont = 'Eras Medium ITC'  # шрифт подсвеченного текста action
DefaultActionHighlightFontSize = 9  # размер подсвеченного шрифта текста action
DefaultActionHighlightFontBold = False  # шрифт подсвеченного текста action
DefaultHighlightActionFontOverstrike = False  # шрифт подсвеченного текста action
DefaultActionHighlightFontUnderline = False  # шрифт подсвеченного текста action
DefaultHighlightActionFontSlant = False  # шрифт подсвеченного текста action

DefaultActionNoHighlightFont = 'Georgia'  # шрифт текста action
DefaultActionNoHighlightFontSize = 9  # размер шрифта текста action
DefaultActionNoHighlightFontBold = False  # шрифт текста action
DefaultActionNoHighlightFontOverstrike = False  # шрифт текста action
DefaultActionNoHighlightFontUnderline = False  # шрифт текста action
DefaultActionNoHighlightFontSlant = True  # шрифт текста action

var_bar_1 = False  # show/hide main bar
var_bar_2 = False  # show/hide navigation bar
var_bar_3 = False  # show/hide info bar

#####################################
# Backup

BackupActionFile = 100  # макс(по кругу) кол-во backup файлов
BackupFolder = 'lr_backup'
BackupName = '{i}_backup_{ind}_action.c'  # Backup

#####################################
# область выделения двойным кликом мыши
tcl_wordchars = '[a-zA-Z0-9_.!-]'  # область выделения двойным кликом мыши
tcl_nonwordchars = '[^a-zA-Z0-9_.!-]'  # область выделения двойным кликом мыши

# #####################################
# логирование

Logger = None  # lr_lib.etc.logger.Logger # вывод сообщений во все Handler: Logger.info('m', notepad=True, parent=act)
log_overdrive = 'a'
logFolder = 'lr_logs'
logName = 'server_%s.log' % time.strftime('%d.%m')
logPath = os.path.join(os.getcwd(), logFolder)
logFullName = os.path.join(logPath, logName)
logger_level = 1  # logging

VarWindowLogger = tk.StringVar(value='INFO')  # минимальный уровень вывода сообщений в gui
EHE = (EHOME, EEND) = [3, 1]  # при ошибке, показать строк выше/ниже, строки в файле-кода

#####################################
# поиск файлов ответов, при старте

DEFAULT_FILES_FOLDER = 'data'  # каталог поиска
DEFAULT_FILES_FOLDER = (os.path.realpath(DEFAULT_FILES_FOLDER) if os.path.isdir(DEFAULT_FILES_FOLDER) else os.getcwd())

VarFilesFolder = tk.StringVar(value=DEFAULT_FILES_FOLDER)  # каталог с файлами
VarIsSnapshotFiles = tk.BooleanVar(value=True)  # брать файлы, проаписанные в inf файлах каталога / или все файлы
VarAllowDenyFiles = tk.BooleanVar(value=False)  # разрешить поиск, в DENY_ исключенных из поиска файлах
VarAllFilesStatistic = tk.IntVar(value=False)  # при старте, создавать подробную статистику файлов(размер, символы и тд), сильно замедляет старт утилиты
SetFilesPOOLEnable = True  # использовать M_POOL, для создания файлов, при старте программы
FilesCreatePortionSize = 15  # порция, число обрабатываемых файлов, для создания из них файлой ответов, за один вызов/в одном потоке

#####################################
# пулы

MainThreadUpdater = None  # выполнять callback из main потока # lr_lib.etc.pool.other.MainThreadUpdater
_MTUT = 0.5  # сек - влияет на общую отзывчивость интерфейса
MainThreadUpdateTime = tk.IntVar(value=(_MTUT * 1000))  # интервал(мс) проверки очереди, callback(из потоков) + скорость обновления подсветки

M_POOL = None  # пул процессов  # lr_lib.etc.pool.main_pool.POOL
M_POOL_NAME = 'multiprocessing.Pool'  # тип основной пул
cpu_count = multiprocessing.cpu_count()
M_POOL_Size = (cpu_count if (cpu_count < 5) else 4)  # основной MP пул(int/None)

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
SThreadAutoSizeTimeOut = tk.IntVar(value=1500)  # отзывчивость(мсек) - период опроса, для изменения размера пула
_SThreadMonitorUpdate = tk.IntVar(value=1000)  # мс, время обновления окна Window.pool_wind для текста состояния пула

#####################################
# etc
EDITOR = dict(exe='notepad.exe')  # программа для открытия "в Editor"
FIND_PARAM_HOTKEY = 'ctrl+shift+c'  # хоткей "найти(2) param"

#####################################
# проверка наличия обновленной версии
github = 'https://github.com/vaduxam1/LR_PARAM'
github_vars = '/blob/master/lr_lib/core/var/vars.py'
GitHub = (github + github_vars)  #
GitUpdPeriod = (60 * 60 * 4)  # сек, период проверки
githubCheckUpdateEnable = True  # вкл/выкл проверку обновлений утилиты
