from Source.CLI.ParsersTable import ParsersTable
from Source.Core.Downloader import Downloader
from Source.Core.Builders import MangaBuilder
from Source.Core.Collector import Collector
from Source.Core.Objects import Objects
from Source.Core.Exceptions import *
from Source.Core.Formats import By

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.CLI.Terminalyzer import ParsedCommandData
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import Clear
from time import sleep

import os

def com_build(system_objects: Objects, command: ParsedCommandData):
	"""
	Строит читаемый контент из описательного файла.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Название парсера.
	ParserName = command.get_key_value("use")
	# Формат архива.
	Format = "cbz" if command.check_flag("cbz") else "zip"

	# Если указан неподдерживаемый парсер.
	if ParserName != "remanga":
		# Вывод в лог: преупреждение.
		print("Only \"remanga\" parser supported.")
		# Завершение работы.
		exit(-1)

	# Вывод в консоль: предупреждение.
	input("Builder not fully implemented yet! Press ENTER to continue...")
	# Построение ветви с наибольшим количеством глав.
	BuilderObject = Builder(Format, command.arguments[0])
	BuilderObject.build_branch()

def com_collect(system_objects: Objects, command: ParsedCommandData):
	"""
	Собирает алиасы тайтлов из каталога и помещает их в список.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Название парсера.
	ParserName = command.get_key_value("use")
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName)
	# Инициализация менеджера коллекции.
	CollectorObject = Collector(system_objects, ParserName)
	# Получение параметров команды.
	Filters = command.get_key_value("filters") if command.check_key("filters") else None
	PagesCount = int(command.get_key_value("pages")) if command.check_key("pages") else None
	Sort = command.check_flag("sort")
	Period = int(command.get_key_value("period")) if command.check_key("period") else None

	#---> Вывод данных.
	#==========================================================================================#
	# Запись в лог информации: заголовк сбора.
	system_objects.logger.info("====== Collecting ======")
	# Очистка консоли.
	Clear()
	# Вывод в консоль: идёт сбор.
	print("Collecting...")

	#---> Получение коллекции.
	#==========================================================================================#
	# Парсинг каталога.
	Collection = Parser.collect(filters = Filters, period = Period, pages = PagesCount)
	# Обновление и сохранение коллекци.
	CollectorObject.append(Collection)
	CollectorObject.save(sort = Sort)
	
	#---> Завершающий этап.
	#==========================================================================================#
	# Включение удаление лога.
	system_objects.REMOVE_LOG = False 
	# Очистка консоли.
	Clear()

def com_get(system_objects: Objects, command: ParsedCommandData, is_cli: bool = True):
	"""
	Скачивает изображение.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	# Установка названия точки CLI.
	if is_cli: system_objects.logger.select_cli_point(command.name)
	# Получение данных парсера.
	ParserName = command.get_key_value("use")
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	ParserSite = system_objects.manager.get_parser_site(ParserName)
	# Получение параметров команды.
	Link = command.arguments[0]
	Directory = command.get_key_value("dir") if command.check_key("dir") else system_objects.temper.path
	Filename = command.get_key_value("name") if command.check_key("name") else None
	FullName = command.check_key("fullname")
	StandartDownloader = command.check_key("sid")
	if FullName: Filename = command.get_key_value("fullname")

	#---> Вывод данных.
	#==========================================================================================#
	# Выбор в менеджере логов используемого парсера.
	if is_cli: system_objects.logger.select_parser(ParserName)
	# Запись в лог информации: заголовок парсинга.
	if is_cli: system_objects.logger.info("====== Downloading ======")
	# Вывод в консоль: загрузка.
	print(f"URL: {command.arguments[0]}\nDownloading... ", end = "")
	
	#---> Скачивание изображения.
	#==========================================================================================#
	# Результат загрузки.
	ResultMessage = None

	# Если у парсера есть кастомный метод загрузки.
	if system_objects.manager.check_method_image(ParserName) and not StandartDownloader:
		# Запись в лог информации: использование кастомного загрузчика.
		if is_cli: system_objects.logger.info("Using custom image downloader.")
		# Инициализация парсера.
		Parser = system_objects.manager.launch(ParserName)
		# Скачивание изображения.
		OriginalFilename = Parser.image(Link)

		# Если скачивание и пермещение в целевой каталог успешно.
		if OriginalFilename and Downloader(system_objects).move_from_temp(ParserName, Directory, OriginalFilename, Filename, FullName):
			# Установка результата.
			ResultMessage = "Done."
			
		else:
			# Установка результата.
			ResultMessage = "Custom downloader failed."

	else:
		# Инициализация загрузчика.
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_retries_count(2)
		Config.requests.enable_proxy_protocol_switching(True)
		WebRequestorObject = WebRequestor(Config)

		# Установка прокси.
		if ParserSettings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = ParserSettings.proxy.host,
			port = ParserSettings.proxy.port,
			login = ParserSettings.proxy.login,
			password = ParserSettings.proxy.password
		)

		# Загрузка изображения.
		ResultMessage = Downloader(system_objects, WebRequestorObject).image(
			url = Link,
			directory = Directory,
			filename = Filename,
			is_full_filename = FullName,
			referer = ParserSite
		).message

	#---> Завершающий этап.
	#==========================================================================================#
	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Вывод в консоль: завершение загрузки.
	print(ResultMessage)
	# Логическое состояние успешности.
	ResultStatus = True if ResultMessage == "Done." else False

	return ResultStatus

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
		"image": [],
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
		TableData["image"].append(system_objects.manager.check_method_image(Parser))
		TableData["repair"].append(system_objects.manager.check_method_repair(Parser))

	# Вывод таблицы.
	ParsersTable(TableData)

def com_parse(system_objects: Objects, command: ParsedCommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Очистка консоли.
	Clear()
	# Название парсера.
	ParserName = command.get_key_value("use")
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
	if command.check_flag("collection"):
		
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
	elif command.check_flag("updates"):
		# Период поиска обновлений.
		Period = int(command.get_key_value("period")) if command.check_key("period") else 24
		# Вывод в консоль: идёт получение обновлений.
		print("Collecting updates...")
		# Получение обновлений.
		Slugs = Parser.collect(period = Period)
		
	# Если активирован флаг обновления локальных файлов.
	elif command.check_flag("local"):
		# Вывод в консоль: идёт поиск тайтлов.
		print("Scanning titles...")
		# Получение списка файлов в директории.
		LocalTitles = os.listdir(ParserSettings.common.titles_directory)
		# Фильтрация только файлов формата JSON.
		LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))
		
		# Для каждого алиаса.
		for Slug in LocalTitles:
			# Чтение тайтла.
			Title = ReadJSON(f"{ParserSettings.common.titles_directory}/{Slug}") 
			# Помещение алиаса тайтла в список.
			Slugs.append(Title["slug"])

		# Запись в лог информации: количество тайтлов для парсинга.
		system_objects.logger.info("Local titles to parsing: " + str(len(Slugs)) + ".")

	else:
		# Запись аргумента в качестве цели парсинга.
		Slugs.append(command.arguments[0])
		
	# Если указан стартовый тайтл.
	if command.check_flag("from"):
		# Запись в лог информации: стартовый тайтл парсинга.
		system_objects.logger.info("Processing will be started from slug: \"" + command.get_key_value("from") + "\".")
				
		# Если стартовый алиас найден.
		if command.get_key_value("from") in Slugs:
			# Указать индекс алиаса в качестве стартового.
			StartIndex = Slugs.index(command.get_key_value("from"))
			
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
			Title.set_content_language(Parser.content_language)
			Title.set_localized_name(Parser.localized_name)
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
			Filename = Parser.id if ParserSettings.common.use_id_as_filename else Parser.slug
			# Состояние: используется ли устаревший формат.
			Legacy = True if ParserSettings.common.legacy else False

			#---> Обработка содержимого.
			#==========================================================================================#
			Title.merge(system_objects, ParserSettings.common.titles_directory, Filename)
			Title.amend(Parser.amend, Message)
			Title.download_covers(system_objects, ParserSettings.common.covers_directory, Filename, Message, ParserSettings.proxy)
			Title.save(system_objects, ParserSettings.common.titles_directory, Filename, Legacy)

		except TitleNotFound:
			# Попытка получения ID из локальных данных.
			Title = system_objects.manager.get_parser_struct(ParserName)
			Title.open(system_objects, ParserSettings.common.titles_directory, Slugs[Index], By.Slug)
			# Запись в лог ошибки: не удалось найти тайтл в источнике.
			system_objects.logger.title_not_found(Slugs[Index], Title.id)

		except TypeError: pass

		if Index != len(Slugs) - 1: sleep(ParserSettings.common.delay)

	# Очистка консоли.
	Clear()

def com_repair(system_objects: Objects, command: ParsedCommandData):
	"""
	Заново получает информацию о содержимом главы.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	# Установка названия точки CLI.
	system_objects.logger.select_cli_point(command.name)
	# Очистка консоли.
	Clear()
	# Название парсера.
	ParserName = command.get_key_value("use")
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName)
	# Настройки парсера.
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	# Запись в лог информации: заголовк восстановления.
	system_objects.logger.info("====== Repairing ======")
	# Имя описательного файла.
	Filename = Filename[:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	# Состояние: используется ли устаревший формат.
	Legacy = True if ParserSettings.common.legacy else False
	# Вывод в консоль: идёт процесс восстановления главы.
	print("Repairing... ", end = None)

	#---> Восстановление главы.
	#==========================================================================================#

	try:
		Title = system_objects.manager.get_parser_struct(ParserName)
		Title.open(system_objects, ParserSettings.common.titles_directory, Filename)
		Parser.parse(Title.slug)
		Title.repair(Parser.repair, int(command.get_key_value("chapter")))
		Title.save(system_objects, ParserSettings.common.titles_directory, Filename, Legacy)

	except TitleNotFound:
		# Вывод в консоль: тайт не найден.
		print("Error! Title not found.")
		# Завершение работы.
		exit(-1)

	except:
		# Вывод в консоль: не удалось восстановить главу.
		print("Error!")
		# Завершение работы.
		exit(-1)

	else:
		# Вывод в консоль: успешно.
		print("Done.")

	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Очистка консоли.
	Clear()