from Source.Core.Objects import Objects
from Source.CLI.Commands import *

from dublib.Terminalyzer import ArgumentsTypes, Command, Terminalyzer
from dublib.Methods import CheckPythonMinimalVersion, Cls, Shutdown

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

# Создание команды: get.
Com = Command("get")
Com.add_argument(ArgumentsTypes.URL, important = True)
Com.add_flag_position(["f"])
Com.add_flag_position(["s"])
Com.add_key_position(["use"], ArgumentsTypes.Text, important = True)
Com.add_key_position(["fullname", "name"], ArgumentsTypes.All)
Com.add_key_position(["dir"], ArgumentsTypes.All)
CommandsList.append(Com)

# Создание команды: list.
Com = Command("list")
Com.add_flag_position(["s"])
CommandsList.append(Com)

# Создание команды: parse.
Com = Command("parse")
Com.add_argument(ArgumentsTypes.All, important = True, layout_index = 1)
Com.add_flag_position(["collection", "local", "updates"], layout_index = 1)
Com.add_flag_position(["f"])
Com.add_flag_position(["s"])
Com.add_key_position(["use"], ArgumentsTypes.Text, important = True)
Com.add_key_position(["from"], ArgumentsTypes.All)
Com.add_key_position(["period"], ArgumentsTypes.Number)
CommandsList.append(Com)

# Создание команды: repair.
Com = Command("repair")
Com.add_argument(ArgumentsTypes.All, important = True)
Com.add_key_position(["chapter"], ArgumentsTypes.All, important = True)
Com.add_key_position(["use"], ArgumentsTypes.Text, important = True)
Com.add_flag_position(["s"])
CommandsList.append(Com)

# Инициализация обработчика консольных аргументов.
TerminalProcessor = Terminalyzer()
# Получение информации о проверке команд.
CommandDataStruct = TerminalProcessor.check_commands(CommandsList)

# Если не удалось определить команду, выбросить исключение.
if CommandDataStruct == None: raise Exception("Unknown command.")

# # Если не удалось найти парсер.
# if CommandDataStruct.arguments[0] not in SystemObjects.manager.parsers_names:
# 	# Запись в лог критической ошибки: парсер не найден.
# 	SystemObjects.logger.critical(f"No parser named \"{CommandDataStruct.arguments[0]}\".")
# 	# Выброс исключения.
# 	raise Exception("Unkonwn parser.")

# else:
# 	# Запись в лог информации: название и версия парсера.
# 	SystemObjects.logger.info(f"Parser: \"{CommandDataStruct.arguments[0]}\".")

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

# Обработка команд: get.
if "get" == CommandDataStruct.name: com_get(SystemObjects, CommandDataStruct)

# Обработка команд: list.
if "list" == CommandDataStruct.name: com_list(SystemObjects)

# Обработка команд: parse.
if "parse" == CommandDataStruct.name: com_parse(SystemObjects, CommandDataStruct)

# Обработка команд: repair.
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