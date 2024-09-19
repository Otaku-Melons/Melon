from Source.Core.ImagesDownloader import ImagesDownloader
from Source.Core.SystemObjects import SystemObjects
from Source.CLI.ParsersTable import ParsersTable
from Source.Core.Builders import MangaBuilder
from Source.Core.Collector import Collector
from Source.Core.Exceptions import *
from Source.Core.Formats import By

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.CLI.Terminalyzer import ParsedCommandData
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.System import Clear
from time import sleep

import os

def com_build(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Строит читаемый контент из описательного файла.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	system_objects.logger.select_cli_point(command.name)
	ParserName = command.get_key_value("use")
	Format = "cbz" if command.check_flag("cbz") else None
	Format = "zip" if command.check_flag("zip") else None
	Message = system_objects.MSG_SHUTDOWN + system_objects.MSG_FORCE_MODE

	if ParserName != "remanga":
		print("Only \"remanga\" parser supported.")
		exit(-1)

	input("Builder not fully implemented yet! Press ENTER to continue...")
	Builder = MangaBuilder(system_objects, com_get, command.arguments[0], Message)
	Builder.set_parameters(Format)
	Builder.build_branch()

def com_collect(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Собирает алиасы тайтлов из каталога и помещает их в список.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	Clear()
	system_objects.logger.select_cli_point(command.name)

	Title = system_objects.manager.get_parser_type()
	Title = Title(system_objects)

	Parser = system_objects.manager.launch(Title)
	CollectorObject = Collector(system_objects)
	Filters = command.get_key_value("filters") if command.check_key("filters") else None
	PagesCount = int(command.get_key_value("pages")) if command.check_key("pages") else None
	Sort = command.check_flag("sort")
	Period = int(command.get_key_value("period")) if command.check_key("period") else None

	#---> Вывод данных.
	#==========================================================================================#
	system_objects.logger.info("====== Collecting ======")
	print("Collecting... ")

	#---> Получение коллекции.
	#==========================================================================================#
	Collection = Parser.collect(filters = Filters, period = Period, pages = PagesCount)
	CollectorObject.append(Collection)
	CollectorObject.save(sort = Sort)
	Clear()

	#---> Завершающий этап.
	#==========================================================================================#
	system_objects.REMOVE_LOG = False 

def com_get(system_objects: SystemObjects, command: ParsedCommandData, is_cli: bool = True):
	"""
	Скачивает изображение.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	if is_cli: system_objects.logger.select_cli_point(command.name)
	ParserName = command.get_key_value("use")
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	ParserSite = system_objects.manager.get_parser_site(ParserName)
	Link = command.arguments[0]
	Directory = command.get_key_value("dir") if command.check_key("dir") else system_objects.temper.path
	Filename = command.get_key_value("name") if command.check_key("name") else None
	FullName = command.check_key("fullname")
	StandartDownloader = command.check_key("sid")
	if FullName: Filename = command.get_key_value("fullname")

	#---> Вывод данных.
	#==========================================================================================#
	if is_cli: system_objects.logger.select_parser(ParserName)
	if is_cli: system_objects.logger.info("====== Downloading ======")
	print(f"URL: {command.arguments[0]}\nDownloading... ", end = "")
	
	#---> Скачивание изображения.
	#==========================================================================================#
	ResultMessage = None

	if system_objects.manager.check_method_image(ParserName) and not StandartDownloader:
		if is_cli: system_objects.logger.info("Using custom image downloader.")
		Parser = system_objects.manager.launch(ParserName)
		OriginalFilename = Parser.image(Link)
		
		if OriginalFilename and ImagesDownloader(system_objects, ParserName).move_from_temp(Directory, OriginalFilename, Filename, FullName):
			ResultMessage = "Done."
			
		else:
			ResultMessage = "Custom downloader failed."

	else:
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_retries_count(2)
		Config.add_header("Referer", f"https://{ParserSite}/")
		Config.requests.enable_proxy_protocol_switching(True)
		WebRequestorObject = WebRequestor(Config)

		if ParserSettings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = ParserSettings.proxy.host,
			port = ParserSettings.proxy.port,
			login = ParserSettings.proxy.login,
			password = ParserSettings.proxy.password
		)

		ResultMessage = ImagesDownloader(system_objects, ParserName, WebRequestorObject).image(
			url = Link,
			directory = Directory,
			filename = Filename,
			is_full_filename = FullName,
		).message

	#---> Завершающий этап.
	#==========================================================================================#
	system_objects.REMOVE_LOG = False 
	print(ResultMessage)
	ResultStatus = True if ResultMessage == "Done." else False

	return ResultStatus

def com_list(system_objects: SystemObjects):
	"""
	Выводит список парсеров в консоль.
		system_objects – коллекция системных объектов.
	"""

	ParsersList = system_objects.manager.all_parsers_names
	TableData = {
		"NAME": [],
		"VERSION": [],
		"SITE": [],
		"collect": [],
		"image": [],
		"repair": []
	}

	for Parser in ParsersList:
		Version = system_objects.manager.get_parser_version(Parser)
		Site = system_objects.manager.get_parser_site(Parser)
		TableData["NAME"].append(Parser)
		TableData["VERSION"].append(Version)
		TableData["SITE"].append(Site)
		TableData["collect"].append(system_objects.manager.check_method_collect(Parser))
		TableData["image"].append(system_objects.manager.check_method_image(Parser))
		TableData["repair"].append(system_objects.manager.check_method_repair(Parser))

	ParsersTable(TableData)
	system_objects.REMOVE_LOG = True

def com_parse(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	Clear()
	system_objects.logger.select_cli_point(command.name)

	Title = system_objects.manager.get_parser_type()
	Title = Title(system_objects)
	Title.set_slug(command.arguments[0])

	Parser = system_objects.manager.launch(Title)
	ParserSettings = system_objects.manager.get_parser_settings()
	system_objects.logger.info("====== Parsing ======")
	Slugs = list()
	StartIndex = 0
	
	if command.check_flag("collection"):
		
		with open(f"Parsers/{system_objects.parser_name}/Collection.txt", "r") as FileReader:
			Buffer = FileReader.read().split("\n")
			
			for Line in Buffer:
				if Line.strip(): Slugs.append(Line)

		system_objects.logger.info(f"Titles in collection: {len(Slugs)}.")

	elif command.check_flag("updates"):
		Period = int(command.get_key_value("period")) if command.check_key("period") else 24
		print("Collecting updates...")
		Slugs = Parser.collect(period = Period)
		
	elif command.check_flag("local"):
		print("Scanning titles...")
		LocalTitles = os.listdir(ParserSettings.common.titles_directory)
		LocalTitles = list(filter(lambda File: File.endswith(".json"), LocalTitles))
		
		for Slug in LocalTitles:
			Title = ReadJSON(f"{ParserSettings.common.titles_directory}/{Slug}") 
			Slugs.append(Title["slug"])

		system_objects.logger.info("Local titles to parsing: " + str(len(Slugs)) + ".")

	else: Slugs.append(command.arguments[0])
		
	if command.check_flag("from"):
		system_objects.logger.info("Processing will be started from slug: \"" + command.get_key_value("from") + "\".")
			
		if command.get_key_value("from") in Slugs: StartIndex = Slugs.index(command.get_key_value("from"))
		else: system_objects.logger.warning("No starting slug in collection. Ignored.")
	
	for Index in range(StartIndex, len(Slugs)):
		Message = system_objects.MSG_SHUTDOWN + system_objects.MSG_FORCE_MODE + f"Parsing: {Index + 1} / {len(Slugs)}\nCurrent title: {Slugs[Index]}\n"
		
		try:
			Title.parse(Parser.parse, Message)
			Title.merge()
			Title.amend(Parser.amend, Message)
			Title.download_covers(Message)
			Title.save()

		except TitleNotFound:
			Title.open(Slugs[Index], By.Slug)
			system_objects.logger.title_not_found(Slugs[Index], Title.id)

		if Index != len(Slugs) - 1: sleep(ParserSettings.common.delay)

	Clear()

def com_repair(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Восстанавливает содержимое главы, заново получая его из источника.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""


	system_objects.logger.select_cli_point(command.name)

	Title = system_objects.manager.get_parser_type()
	Title = Title(system_objects)

	Parser = system_objects.manager.launch(Title)
	system_objects.logger.info("====== Repairing ======")
	print("Repairing... ", end = "")
	Filename = Filename[:-5] if command.arguments[0].endswith(".json") else command.arguments[0]

	#---> Восстановление главы.
	#==========================================================================================#

	try:
		Title.open(Filename)
		Title.parse(Parser.parse)
		Title.repair(Parser.repair, command.get_key_value("chapter"))
		Title.save()

	except TitleNotFound:
		print("Error! Title not found.")
		exit(-1)

	else:
		print("Done.")

	system_objects.REMOVE_LOG = True 