from Source.Core.Objects import Objects
from Source.CLI.Commands import *

from dublib.CLI.Terminalyzer import Command, ParametersTypes, Terminalyzer
from dublib.Methods.System import CheckPythonMinimalVersion, Shutdown

import sys

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Инициализация коллекции объектов.
SystemObjects = Objects()
# Запись в лог информации: инициализация.
SystemObjects.logger.info("====== Preparing to starting ======")
SystemObjects.logger.info(f"Starting with Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} on {sys.platform}.")
SystemObjects.logger.info("Command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: build.
Com = Command("build", "Build readable content.")
ComPos = Com.create_position("FILENAME", "Source file.", important = True)
ComPos.add_argument(description = "Filename of locally saved title.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("cbz", "Make *.CBZ archives.")
CommandsList.append(Com)

# Создание команды: collect.
Com = Command("collect", "Collect titles slugs into Collection.txt file.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
Com.add_flag("sort", "Enable slugs sorting.")
Com.add_key("filters", description = "Query string for filtering titles.")
Com.add_key("pages", ParametersTypes.Number, "Count of pages to collecting.")
CommandsList.append(Com)

# Создание команды: get.
Com = Command("get", "Download image.")
ComPos = Com.create_position("URL", "Image source.")
ComPos.add_argument(ParametersTypes.URL, "Link to image.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
ComPos = Com.create_position("NAME", "Type of naming.")
ComPos.add_key("fullname", description = "Full name of file.")
ComPos.add_key("name", "Name of file without type.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
Com.add_flag("sid", "Disable custom imege downloader.")
Com.add_key("dir", ParametersTypes.ValidPath, "Output directory.")
CommandsList.append(Com)

# Создание команды: list.
Com = Command("list", "Print list of installed parsers.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

# Создание команды: parse.
Com = Command("parse", "Start titles parsing.")
ComPos = Com.create_position("TARGET", "Target for parsing.", important = True)
ComPos.add_argument(description = "Title slug.")
ComPos.add_flag("collection", "Parse slugs from Collection.txt file.")
ComPos.add_flag("local", "Parse all locally saved titles.")
ComPos.add_flag("updates", "Parse titles updated for last 24 hours.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_key("period", ParametersTypes.Number, "Period in hours for parsing updates.")
Com.add_flag("f", "Enable force mode.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

# Создание команды: repair.
Com = Command("repair", "Repair chapter content in locally saved title.")
ComPos = Com.create_position("FILENAME", "Source file.", important = True)
ComPos.add_argument(description = "Filename of locally saved title.")
ComPos = Com.create_position("TARGET", "Target for repairing.", important = True)
ComPos.add_key("chapter", ParametersTypes.Number, "Chapter ID.")
ComPos = Com.create_position("PARSER", "Used parser.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Parser name.")
Com.add_flag("s", "Shutdown PC after script finish.")
CommandsList.append(Com)

# Инициализация обработчика консольных аргументов.
Analyzer = Terminalyzer()
# Дополнительная настройка анализатора.
Analyzer.enable_help(True)
# Получение информации о проверке команд.
CommandDataStruct = Analyzer.check_commands(CommandsList)

# Если не удалось определить команду.
if CommandDataStruct == None:
	# Удаление файла лога.
	SystemObjects.logger.close(clean = True)
	# Вывод в лог: ошибка распознания команды.
	print("Unknown command.")
	# Выброс исключения.
	exit(0)

#==========================================================================================#
# >>>>> ОБРАБОТКА НЕСПЕЦИФИЧЕСКИХ ФЛАГОВ <<<<< #
#==========================================================================================#

# Обработка флага: режим перезаписи.
if "f" in CommandDataStruct.flags:
	# Включение режима перезаписи.
	SystemObjects.FORCE_MODE = True
	# Запись в лог информации: включён режим перезаписи.
	SystemObjects.logger.info("Force mode: ON.")
	# Установка сообщения для внутренних функций.
	SystemObjects.MSG_FORCE_MODE = "Force mode: ON\n"

# Обработка флага: выключение ПК после завершения работы скрипта.
if "s" in CommandDataStruct.flags:
	# Включение режима.
	SystemObjects.SHUTDOWN = True
	# Запись в лог информации: ПК будет выключен после завершения работы.
	SystemObjects.logger.info("Computer will be turned off after script is finished!")
	# Установка сообщения для внутренних функций.
	SystemObjects.MSG_SHUTDOWN = "Computer will be turned off after script is finished!\n"

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: build.
if "build" == CommandDataStruct.name: com_build(SystemObjects, CommandDataStruct)

# Обработка команды: collect.
if "collect" == CommandDataStruct.name: com_collect(SystemObjects, CommandDataStruct)

# Обработка команды: get.
if "get" == CommandDataStruct.name: com_get(SystemObjects, CommandDataStruct)

# Обработка команды: list.
if "list" == CommandDataStruct.name: com_list(SystemObjects)

# Обработка команды: parse.
if "parse" == CommandDataStruct.name: com_parse(SystemObjects, CommandDataStruct)

# Обработка команды: repair.
if "repair" == CommandDataStruct.name: com_repair(SystemObjects, CommandDataStruct)

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

# Если лог нужно удалить.
if SystemObjects.REMOVE_LOG:
	# Удаление файла лога.
	SystemObjects.logger.close(clean = True)

else:
	# Закрытие лога.
	SystemObjects.logger.close()

# Если задан флаг выключения.
if SystemObjects.SHUTDOWN:
	# Выключение ПК.
	Shutdown()