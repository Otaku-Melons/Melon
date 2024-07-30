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
Com = Command("build", "Строит читаемый контент из описательного файла.")
CommandsList.append(Com)

# Создание команды: collect.
Com = Command("collect", "Собирает алиасы тайтлов в файл Collection.txt.")
ComPos = Com.create_position("PARSER", "Используемый парсер.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Название парсера.")
Com.add_flag("f", "Включает режим перезаписи.")
Com.add_flag("s", "Выключает ПК после завершения работы.")
Com.add_flag("sort", "Включает сортировку алиасов.")
Com.add_key("filters", description = "Строка с запросом для фильтрации тайтлов.")
Com.add_key("pages", ParametersTypes.Number, "Количество страниц каталога для сбора тайтлов.")
CommandsList.append(Com)

# Создание команды: get.
Com = Command("get", "Скачивает изображение.")
ComPos = Com.create_position("URL", "Источник.")
ComPos.add_argument(ParametersTypes.URL, "Ссылка на изображение.")
ComPos = Com.create_position("PARSER", "Используемый парсер.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Название парсера.")
ComPos = Com.create_position("NAME", "Способ именования.")
ComPos.add_key("fullname", description = "Полное имя файла.")
ComPos.add_key("name", description = "Имя файла без расширения.")
Com.add_flag("f", "Включает режим перезаписи.")
Com.add_flag("s", "Выключает ПК после завершения работы.")
Com.add_flag("sid", "Отключает кастомные загрузчики изображений.")
Com.add_key("dir", ParametersTypes.ValidPath, "Выходная директория.")
CommandsList.append(Com)

# Создание команды: list.
Com = Command("list", "Выводит список установленных парсеров.")
Com.add_flag("s", "Выключает ПК после завершения работы.")
CommandsList.append(Com)

# Создание команды: parse.
Com = Command("parse", "Запускает парсинг.")
ComPos = Com.create_position("TARGET", "Цель для парсинга.", important = True)
ComPos.add_argument(description = "Алиас тайтла.")
ComPos.add_flag("collection", "Парсить алиасы из файла Collection.txt.")
ComPos.add_flag("local", "Парсить все локально описанные файлы.")
ComPos.add_flag("updates", "Парсить тайтлы, обновлённые на сайте за последние 24 часа.")
ComPos.add_argument(ParametersTypes.URL, "Ссылка на изображение.")
ComPos = Com.create_position("PARSER", "Используемый парсер.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Название парсера.")
Com.add_key("period", ParametersTypes.Number, "Период в часах для получения обновлений.")
Com.add_flag("f", "Включает режим перезаписи.")
Com.add_flag("s", "Выключает ПК после завершения работы.")
CommandsList.append(Com)

# Создание команды: repair.
Com = Command("repair", "Заново получает содержимое главы в локально описанном файле.")
ComPos = Com.create_position("FILENAME", "Файл.", important = True)
ComPos.add_argument(description = "Имя файла с расширением или без него.")
ComPos = Com.create_position("TARGET", "Цель для восстановления.", important = True)
ComPos.add_key("chapter", ParametersTypes.Number, "ID главы.")
ComPos = Com.create_position("PARSER", "Используемый парсер.", important = True)
ComPos.add_key("use", ParametersTypes.Text, "Название парсера.")
Com.add_flag("s", "Выключает ПК после завершения работы.")
CommandsList.append(Com)

# Инициализация обработчика консольных аргументов.
Analyzer = Terminalyzer()
# Дополнительная настройка анализатора.
Analyzer.enable_help(True)
Analyzer.help_translation.important_note = "\nОбязательные параметры помечены символом *."
# Получение информации о проверке команд.
CommandDataStruct = Analyzer.check_commands(CommandsList)

# Если не удалось определить команду.
if CommandDataStruct == None:
	# Удаление файла лога.
	SystemObjects.logger.close(clean = True)
	# Вывод в лог: ошибка распознания команды.
	print("Неизвестная команда!")
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

# Обработка команд: collect.
if "collect" == CommandDataStruct.name: com_collect(SystemObjects, CommandDataStruct)

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