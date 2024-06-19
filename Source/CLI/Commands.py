from Source.CLI.ParsersTable import ParsersTable
from Source.Core.Downloader import Downloader
from Source.Core.Collector import Collector
from Source.Core.Objects import Objects
from Source.Core.Exceptions import *

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Terminalyzer import CommandData
from dublib.Methods import Cls, ReadJSON

import os

def com_collect(system_objects: Objects, command: CommandData):
	"""
	Собирает алиасы тайтлов из каталога и помещает их в список.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Название парсера.
	ParserName = command.values["use"]
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName)
	# Инициализация менеджера коллекции.
	CollectorObject = Collector(system_objects, ParserName)
	# Получение параметров команды.
	Filters = command.values["filters"] if "filters" in command.keys else None
	PagesCount = int(command.values["pages"]) if "pages" in command.keys else None
	Sort = True if "sort" in command.flags else False

	#---> Вывод данных.
	#==========================================================================================#
	# Запись в лог информации: заголовк сбора.
	system_objects.logger.info("====== Collecting ======")
	# Очистка консоли.
	Cls()
	# Вывод в консоль: идёт сбор.
	print("Collecting...")

	#---> Получение коллекции.
	#==========================================================================================#
	# Парсинг каталога.
	Collection = Parser.collect(filters = Filters, pages_count = PagesCount)
	# Обновление и сохранение коллекци.
	CollectorObject.append(Collection)
	CollectorObject.save(sort = Sort)
	
	#---> Завершающий этап.
	#==========================================================================================#
	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Очистка консоли.
	Cls()

def com_get(system_objects: Objects, command: CommandData):
	"""
	Скачивает изображение.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Получение данных парсера.
	ParserName = command.values["use"]
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	ParserSite = system_objects.manager.get_parser_site(ParserName)
	# Получение параметров команды.
	Directory = command.values["dir"] if "dir" in command.keys else system_objects.temper.path
	Filename = command.values["name"] if "name" in command.keys else None
	if "fullname" in command.keys: Filename = command.values["fullname"]
	FullName = True if "fullname" in command.keys else False

	#---> Вывод данных.
	#==========================================================================================#
	# Выбор в менеджере логов используемого парсера.
	system_objects.logger.select_parser(command.values["use"])
	# Запись в лог информации: заголовок парсинга.
	system_objects.logger.info("====== Downloading ======")
	# Вывод в консоль: загрузка.
	print(f"URL: {command.arguments[0]}\nDownloading... ", end = "")
	
	#---> Скачивание изображения.
	#==========================================================================================#
	# Инициализация загрузчика.
	Config = WebConfig()
	Config.select_lib(WebLibs.requests)
	Config.generate_user_agent("pc")
	WebRequestorObject = WebRequestor(Config)
	# Установка прокси.
	if ParserSettings["proxy"]["enable"]: WebRequestorObject.add_proxy(
		Protocols.HTTP,
		host = ParserSettings["proxy"]["host"],
		port = ParserSettings["proxy"]["port"],
		login = ParserSettings["proxy"]["login"],
		password = ParserSettings["proxy"]["password"]
	)
	# Загрузка изображения.
	Result = Downloader(system_objects, WebRequestorObject, exception = True).image(command.arguments[0], ParserSite, Directory, Filename, FullName)

	#---> Завершающий этап.
	#==========================================================================================#
	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Вывод в консоль: завершение загрузки.
	print(Result)

def com_list(system_objects: Objects):
	"""
	Выводит список парсеров в консоль.
		system_objects – коллекция системных объектов.
	"""

	# Список названий.
	ParsersList = system_objects.manager.parsers_names
	# Включение удаление лога.
	system_objects.REMOVE_LOG = True
	# Словарь для построения таблицы.
	TableData = {
		"NAME": [],
		"VERSION": [],
		"SITE": [],
		"collect": [],
		"get_updates": [],
		"repair": []
	}

	# Для каждого парсера.
	for Parser in ParsersList:
		# Получение данных парсера.
		Version = system_objects.manager.get_parser_version(Parser)
		Site = system_objects.manager.get_parser_site(Parser)
		# Заполнение данных.
		TableData["NAME"].append(Parser)
		TableData["VERSION"].append(Version)
		TableData["SITE"].append(Site)
		TableData["collect"].append(system_objects.manager.check_method_collect(Parser))
		TableData["get_updates"].append(system_objects.manager.check_method_get_updates(Parser))
		TableData["repair"].append(system_objects.manager.check_method_repair(Parser))

	# Вывод таблицы.
	ParsersTable(TableData)

def com_parse(system_objects: Objects, command: CommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Очистка консоли.
	Cls()
	# Название парсера.
	ParserName = command.values["use"]
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName)
	# Настройки парсера.
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	# Запись в лог информации: заголовок парсинга.
	system_objects.logger.info("====== Parsing ======")
	# Алиасы тайтлов.
	Slugs = list()
	# Индекс стартового алиаса.
	StartIndex = 0
	
	# Если активирован флаг парсинга коллекции.
	if "collection" in command.flags:
		# Индекс обрабатываемого тайтла.
		CurrentTitleIndex = 0
		
		# Открытие потока чтения.
		with open(f"Parsers/{ParserName}/Collection.txt", "r") as FileReader:
			# Буфер чтения.
			Buffer = FileReader.read().split("\n")
			
			# Для каждой строки.
			for Line in Buffer:
				# Если строка не пуста, добавить её в список алиасов.
				if Line.strip(): Slugs.append(Line)

		# Запись в лог информации: количество тайтлов в коллекции.
		system_objects.logger.info(f"Titles in collection: {len(Slugs)}.")

	# Если активирован флаг парсинга обновлений.
	elif "updates" in command.flags:
		# Период поиска обновлений.
		Period = int(command.values["period"]) if "period" in command.keys else 24
		# Вывод в консоль: идёт получение обновлений.
		print("Collecting updates...")
		# Получение обновлений.
		Slugs = Parser.get_updates(Period)
		
	# Если активирован флаг обновления локальных файлов.
	elif "local" in command.flags:
		# Вывод в консоль: идёт поиск тайтлов.
		print("Scanning titles...")
		# Получение списка файлов в директории.
		LocalTitles = os.listdir(ParserSettings["common"]["titles_directory"])
		# Фильтрация только файлов формата JSON.
		LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))
		
		# Для каждого алиаса.
		for Slug in LocalTitles:
			# Чтение тайтла.
			Title = ReadJSON(ParserSettings["common"]["titles_directory"] + "/" + Slug) 
			# Помещение алиаса тайтла в список.
			Slugs.append(Title["slug"])

		# Запись в лог информации: количество тайтлов для парсинга.
		system_objects.logger.info("Local titles to parsing: " + str(len(Slugs)) + ".")

	else:
		# Запись аргумента в качестве цели парсинга.
		Slugs.append(command.arguments[0])
		
	# Если указан стартовый тайтл.
	if "from" in command.keys:
		# Запись в лог информации: стартовый тайтл парсинга.
		system_objects.logger.info("Processing will be started from slug: \"" + command.values["from"] + "\".")
				
		# Если стартовый алиас найден.
		if command.values["from"] in Slugs:
			# Указать индекс алиаса в качестве стартового.
			StartIndex = Slugs.index(command.values["from"])
			
		else:
			# Запись в лог предупреждения: стартовый алиас не найден.
			system_objects.logger.warning("No starting slug in collection. Ignored.")

	# Парсинг тайтлов.
	for Index in range(StartIndex, len(Slugs)):
		# Сообщение для внутреннего обработчика.
		Message = system_objects.MSG_SHUTDOWN + system_objects.MSG_FORCE_MODE + f"Parsing: {Index + 1} / {len(Slugs)}\nCurrent title: {Slugs[Index]}\n"

		try:
			#---> Парсинг базовых данных.
			#==========================================================================================#
			Title = system_objects.manager.get_parser_struct(ParserName)
			Parser.parse(Slugs[Index], Message)
			Title.set_site(Parser.site)
			Title.set_id(Parser.id)
			Title.set_slug(Parser.slug)
			Title.set_ru_name(Parser.ru_name)
			Title.set_en_name(Parser.en_name)
			Title.set_another_names(Parser.another_names)
			Title.set_covers(Parser.covers)
			Title.set_authors(Parser.authors)
			Title.set_publication_year(Parser.publication_year)
			Title.set_description(Parser.description)
			Title.set_age_limit(Parser.age_limit)
			Title.set_genres(Parser.genres)
			Title.set_tags(Parser.tags)
			Title.set_franchises(Parser.franchises)
			Title.set_type(Parser.type)
			Title.set_status(Parser.status)
			Title.set_is_licensed(Parser.is_licensed)
			Title.set_content(Parser.content)

			#---> Получение дополнительных данных.
			#==========================================================================================#
			# Используемое имя файла.
			Filename = Parser.id if ParserSettings["common"]["use_id_as_filename"] else Parser.slug
			# Состояние: используется ли устаревший формат.
			Legacy = True if ParserSettings["common"]["legacy"] else False

			#---> Обработка содержимого.
			#==========================================================================================#
			Title.merge(system_objects, ParserSettings["common"]["titles_directory"], Filename)
			Title.amend(Parser.amend, Message)
			Title.download_covers(system_objects, ParserSettings["common"]["covers_directory"], Filename, Message, ParserSettings["proxy"])
			Title.save(system_objects, ParserSettings["common"]["titles_directory"], Filename, Legacy)

		except TitleNotFound: pass

	# Очистка консоли.
	Cls()

def com_repair(system_objects: Objects, command: CommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Очистка консоли.
	Cls()
	# Название парсера.
	ParserName = command.values["use"]
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName)
	# Настройки парсера.
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	# Запись в лог информации: заголовк восстановления.
	system_objects.logger.info("====== Repairing ======")
	# Имя описательного файла.
	Filename = Filename[:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	# Состояние: используется ли устаревший формат.
	Legacy = True if ParserSettings["common"]["legacy"] else False
	# Вывод в консоль: идёт процесс восстановления главы.
	print("Repairing...")

	#---> Восстановление главы.
	#==========================================================================================#
	Title = system_objects.manager.get_parser_struct(ParserName)
	Title.open(system_objects, ParserSettings["common"]["titles_directory"], Filename)
	Parser.parse(Title.slug)
	Title.repair(Parser.repair, int(command.values["chapter"]))
	Title.save(system_objects, ParserSettings["common"]["titles_directory"], Filename, Legacy)

	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Очистка консоли.
	Cls()