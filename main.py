from Source.Core.Objects import Objects
from Source.CLI.Commands import *

from dublib.Terminalyzer import ArgumentsTypes, Command, Terminalyzer
from dublib.Methods import CheckPythonMinimalVersion, Cls, Shutdown

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Инициализация коллекции объектов.
SystemObjects = Objects()
# Очистка консоли.
Cls()

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: list.
Com = Command("list")
Com.add_flag_position(["s"])
CommandsList.append(Com)

# Создание команды: parse.
Com = Command("parse")
Com.add_argument(ArgumentsTypes.All, important = True, layout_index = 1)
Com.add_argument(ArgumentsTypes.All, important = True, layout_index = 2)
Com.add_flag_position(["collection", "local"], layout_index = 2)
Com.add_flag_position(["f"])
Com.add_flag_position(["s"])
Com.add_key_position(["from"], ArgumentsTypes.All)
CommandsList.append(Com)

# Инициализация обработчика консольных аргументов.
TerminalProcessor = Terminalyzer()
# Получение информации о проверке команд.
CommandDataStruct = TerminalProcessor.check_commands(CommandsList)

# Если не удалось определить команду, выбросить исключение.
if CommandDataStruct == None: raise Exception("Unknown command.")

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
	SystemObjects.logger.info("Computer will be turned off after the script is finished!")
	# Установка сообщения для внутренних функций.
	SystemObjects.MSG_SHUTDOWN = "Computer will be turned off after the script is finished!\n"

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команд: list.
if "list" == CommandDataStruct.name: com_list(SystemObjects)

# Обработка команд: parse.
if "parse" == CommandDataStruct.name: com_parse(SystemObjects, CommandDataStruct)

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ <<<<< #
#==========================================================================================#

# Если лог нужно удалить.
if SystemObjects.REMOVE_LOG:
	# Удаление файла лога.
	SystemObjects.logger.remove()

# Если задан флаг выключения.
if SystemObjects.SHUTDOWN:
	# Запись в лог сообщения: немедленное выключение ПК.
	SystemObjects.logger.info("Turning off computer.")
	# Выключение ПК.
	Shutdown()

# # Запись в лог сообщения: заголовок завершения работы скрипта.
# logging.info("====== Exiting ======")
# # Очистка консоли.
# Cls()
# # Время завершения работы скрипта.
# EndTime = time.time()
# # Запись в лог сообщения: время исполнения скрипта.
# logging.info("Script finished. Execution time: " + SecondsToTimeString(EndTime - StartTime) + ".")

# # Выключение логгирования.
# logging.shutdown()
# # Если указано, удалить файл лога.
# if REMOVE_LOGFILE == True: os.remove(LogFilename)
# # Завершение главного процесса.
# sys.exit(EXIT_CODE)