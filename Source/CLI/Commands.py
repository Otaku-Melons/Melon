from Source.Core.ImagesDownloader import ImagesDownloader
from Source.Core.SystemObjects import SystemObjects
from Source.Core.Builders import MangaBuilder
from Source.Core.Collector import Collector
from Source.Core.Installer import Installer
from Source.Core.Tagger import Tagger
from Source.Core.Exceptions import *
from Source.Core.Timer import Timer
from Source.Core.Formats import By
from Source.CLI import Templates

from dublib.CLI.Terminalyzer import ParsedCommandData
from dublib.CLI.Templates import PrintExecutionStatus
from dublib.CLI.TextStyler import Styles, TextStyler
from dublib.Methods.Filesystem import WriteJSON
from dublib.Engine.Bus import ExecutionError
from dublib.Methods.System import Clear
from time import sleep

# В разработке!
def com_build(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Строит читаемый контент из описательного файла.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовительный этап.
	#==========================================================================================#
	Clear()
	system_objects.logger.select_cli_point(command.name)

	input("Builder not fully implemented yet! Press ENTER to continue...")
	
	#---> Получение и обработка предварительных данных.
	#==========================================================================================#
	ParserName = command.get_key_value("use")
	Format = "cbz" if command.check_flag("cbz") else None
	Format = "zip" if command.check_flag("zip") else None
	Message = system_objects.MSG_SHUTDOWN + system_objects.MSG_FORCE_MODE

	#---> Обработка команды.
	#==========================================================================================#

	if ParserName != "remanga":
		print("Only \"remanga\" parser supported.")
		exit(-1)
	
	Builder = MangaBuilder(system_objects, com_get, command.arguments[0], Message)
	Builder.set_parameters(Format)
	Builder.build_branch()

	#---> Вывод отчёта.
	#==========================================================================================#
	Clear()
	print("Builded.")

def com_collect(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Собирает алиасы тайтлов из каталога и помещает их в список.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	ParserName = command.get_key_value("use")
	system_objects.logger.select_cli_point(command.name)
	system_objects.select_parser(ParserName)

	#---> Парсинг данных команды.
	#==========================================================================================#
	Filters = command.get_key_value("filters") if command.check_key("filters") else None
	PagesCount = int(command.get_key_value("pages")) if command.check_key("pages") else None
	Sort = command.check_flag("sort")
	Period = int(command.get_key_value("period")) if command.check_key("period") else None

	#---> Выполнение команды.
	#==========================================================================================#
	Title = system_objects.manager.get_parser_type()
	Title = Title(system_objects)
	Parser = system_objects.manager.launch()
	CollectedTitlesCount = 0
	Collection = list()
	CollectorObject = Collector(system_objects)

	if system_objects.FORCE_MODE: system_objects.logger.warning("Collection will be overwritten.", stdout = True)

	if command.check_flag("local"):
		system_objects.logger.info("====== Collecting ======")
		TimerObject = Timer()
		TimerObject.start()
		print("Scanning titles... ", end = "", flush = True)
		CollectedTitlesCount = CollectorObject.from_local()
		ElapsedTime = TimerObject.ends()
		print(f"Done in {ElapsedTime}.")

	elif not system_objects.manager.check_method_collect():
		print("Parser doesn't support " + TextStyler("collect", decorations = [Styles.Decorations.Bold]) + " method.")
		return

	else:
		system_objects.logger.info("====== Collecting ======")
		Collection = Parser.collect(filters = Filters, period = Period, pages = PagesCount)
		CollectedTitlesCount = len(Collection)
		CollectorObject.append(Collection)

	CollectorObject.save(sort = Sort)
	
	#---> Вывод отчёта.
	#==========================================================================================#
	system_objects.logger.titles_collected(CollectedTitlesCount)

def com_get(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Скачивает изображение.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	ParserName = command.get_key_value("use")
	system_objects.logger.select_cli_point(command.name)
	system_objects.select_parser(ParserName)

	#---> Парсинг данных команды.
	#==========================================================================================#
	Link = command.arguments[0]
	Directory = command.get_key_value("dir") if command.check_key("dir") else system_objects.temper.parser_temp
	Filename = command.get_key_value("name") if command.check_key("name") else None
	FullName = command.check_key("fullname")
	if FullName: Filename = command.get_key_value("fullname")
	
	#---> Выполнение команды.
	#==========================================================================================#
	ResultMessage = "Download failed."
	system_objects.logger.info("====== Downloading ======")
	Parser = system_objects.manager.launch()
	print(f"URL: {command.arguments[0]}\nDownloading... ", end = "")
	
	TempFilename = Parser.image(Link)
	if TempFilename and ImagesDownloader(system_objects).move_from_temp(Directory, TempFilename, Filename, True): ResultMessage = "Done."	

	#---> Вывод отчёта.
	#==========================================================================================#
	print(ResultMessage)

def com_help(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Заглушка для обработки помощи.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	pass

def com_install(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Производит установку парсеров.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	system_objects.logger.select_cli_point(command.name)

	#---> Парсинг данных команды.
	#==========================================================================================#
	FullInstallation = command.check_flag("all")
	
	#---> Выполнение команды.
	#==========================================================================================#
	system_objects.logger.info("====== Insrallation ======")
	print("Running installation...")
	InstallerObject = Installer(system_objects)
	TimerObject = Timer(start = True)

	if command.check_flag("a") or FullInstallation: InstallerObject.alias()
	if command.check_flag("r") or FullInstallation: InstallerObject.requirements()
	if command.check_flag("s") or FullInstallation: InstallerObject.scripts()
	if command.check_flag("c") or FullInstallation: InstallerObject.configs()

	#---> Вывод отчёта.
	#==========================================================================================#
	print("Done in " + TimerObject.ends() + ".")

def com_list(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Выводит список парсеров в консоль.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	system_objects.logger.select_cli_point(command.name)

	#---> Выполнение команды.
	#==========================================================================================#
	TableData = {
		"NAME": [],
		"VERSION": [],
		"TYPE": [],
		"SITE": [],
		"collect": [],
		"image": []
	}

	for Parser in system_objects.manager.all_parsers_names:

		try:
			Version = system_objects.manager.get_parser_version(Parser)
			Site = system_objects.manager.get_parser_site(Parser)
			Type = system_objects.manager.get_parser_type_name(Parser)

		except:
			TableData["NAME"].append(Parser)
			TableData["VERSION"].append("")
			TableData["TYPE"].append("")
			TableData["SITE"].append("")
			TableData["collect"].append(None)
			TableData["image"].append(None)

		else:
			TableData["NAME"].append(Parser)
			TableData["VERSION"].append(Version)
			TableData["TYPE"].append(Type)
			TableData["SITE"].append(Site)
			TableData["collect"].append(system_objects.manager.check_method_collect(Parser))
			TableData["image"].append(system_objects.manager.check_method_image(Parser))

	#---> Вывод отчёта.
	#==========================================================================================#
	Templates.parsers_table(TableData)

def com_parse(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	ParserName = command.get_key_value("use")
	system_objects.logger.select_cli_point(command.name)
	system_objects.select_parser(ParserName)

	#---> Парсинг данных команды.
	#==========================================================================================#
	Slugs = list()
	StartIndex = 0
	system_objects.logger.info("====== Parsing ======")
	
	ContentType = system_objects.manager.get_parser_type()
	Title = ContentType(system_objects)
	Parser = system_objects.manager.launch()
	ParserSettings = system_objects.manager.parser_settings

	if command.check_flag("collection"):
		Slugs = Collector(system_objects, merge = True).slugs
		system_objects.logger.info(f"Titles in collection: {len(Slugs)}.")

	elif command.check_flag("updates"):
		Period = int(command.get_key_value("period")) if command.check_key("period") else 24
		print("Collecting updates...")
		Slugs = Parser.collect(period = Period)
		
	elif command.check_flag("local"):
		TimerObject = Timer(start = True)
		print("Scanning titles... ", end = "", flush = True)
		CollectorObject = Collector(system_objects)
		CollectorObject.from_local()
		Slugs += CollectorObject.slugs
		ElapsedTime = TimerObject.ends()
		print(f"Done in {ElapsedTime}.")
		Text = "Local titles to parsing: " + str(len(Slugs)) + "."
		system_objects.logger.info(Text, stdout = True)

	else: Slugs.append(command.arguments[0])
		
	if command.check_key("from"):
		system_objects.logger.info("Processing will be started from slug: \"" + command.get_key_value("from") + "\".")
			
		if command.get_key_value("from") in Slugs: StartIndex = Slugs.index(command.get_key_value("from"))
		else: system_objects.logger.warning("No starting slug in collection. Ignored.")

	#---> Выполнение команды.
	#==========================================================================================#
	ParsedCount = 0
	NotFoundCount = 0
	ErrorsCount = 0
	TotalCount = len(Slugs)

	for Index in range(StartIndex, TotalCount):
		Title = ContentType(system_objects)
		Title.set_slug(Slugs[Index])
		Title.set_parser(Parser)

		try:
			Title.open(Slugs[Index], By.Slug, exception = False)
			Title.parse(Index, TotalCount)
			Title.merge()
			Title.amend()
			Title.download_covers()
			Title.save()
			ParsedCount += 1

		except TitleNotFound:
			try: Title.open(Slugs[Index], By.Slug)
			except: pass
			NotFoundCount += 1

		except ParsingError:
			ErrorsCount += 1

		if Index != len(Slugs) - 1: sleep(ParserSettings.common.delay)

	#---> Вывод отчёта.
	#==========================================================================================#
	Templates.parsing_summary(ParsedCount, NotFoundCount, ErrorsCount)

def com_repair(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Восстанавливает содержимое главы, заново получая его из источника.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	ParserName = command.get_key_value("use")
	system_objects.logger.select_cli_point(command.name)
	system_objects.select_parser(ParserName)

	#---> Парсинг данных команды.
	#==========================================================================================#
	ChapterID = command.get_key_value("chapter")

	#---> Выполнение команды.
	#==========================================================================================#
	Title = system_objects.manager.get_parser_type()
	Title = Title(system_objects)
	Parser = system_objects.manager.launch()

	system_objects.logger.info("====== Repairing ======")

	Filename = Filename[:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	ResultMessage = "Done."

	try:
		Title.set_parser(Parser)
		Title.open(Filename)
		Title.parse()
		Title.repair(ChapterID)
		Title.save()

	except TitleNotFound:
		ResultMessage = "Error! Title not found."
		system_objects.logger.title_not_found(Title, exception = False)
		system_objects.EXIT_CODE = -1

	except ChapterNotFound:
		ResultMessage = "Error! Chapter not found."
		system_objects.EXIT_CODE = -1

	except ParsingError:
		ResultMessage = "Error! Unable access title data."
		system_objects.EXIT_CODE = -1

	#---> Вывод отчёта.
	#==========================================================================================#
	# print(ResultMessage)

def com_run(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Восстанавливает содержимое главы, заново получая его из источника.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	ParserName = command.get_key_value("use", exception = True)
	ExtensionName = command.get_key_value("extension", exception = True)
	system_objects.logger.select_cli_point(command.name)
	system_objects.select_extension(ExtensionName)
	system_objects.select_parser(ParserName)

	#---> Парсинг данных команды.
	#==========================================================================================#
	ExtensionCommand = command.get_key_value("command")

	#---> Выполнение команды.
	#==========================================================================================#
	Extension = system_objects.manager.launch_extension(ParserName, ExtensionName)
	system_objects.logger.info(f"====== {ParserName}:{ExtensionName} ======", stdout = True)
	Status = ExecutionError(-1, "Unkown error while running extension.")
	Status = Extension.run(ExtensionCommand)

	#---> Вывод отчёта.
	#==========================================================================================#
	PrintExecutionStatus(Status)

def com_tagger(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Запускает обработчик классификаторов тайтлов.
		system_objects – коллекция системных объектов;\n
		command – объект представления консольной команды.
	"""

	#---> Подготовка к выполнению.
	#==========================================================================================#
	ParserName = command.get_key_value("use")
	system_objects.logger.select_cli_point(command.name)
	if ParserName: system_objects.select_parser(ParserName)

	#---> Парсинг данных команды.
	#==========================================================================================#
	TaggerObject = Tagger()
	Type, Name = TaggerObject.get_classificator_data(command)
	
	#---> Выполнение команды.
	#==========================================================================================#
	Operation = TaggerObject.process(Name, Type, ParserName)

	#---> Вывод отчёта.
	#==========================================================================================#
	if command.check_flag("json"): print(Operation.to_json())
	elif command.check_key("file"): WriteJSON(command.get_key_value("file"), Operation.to_dict())
	else: Operation.print()