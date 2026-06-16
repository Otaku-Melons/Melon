from Source.Core.Base.Builders.RanobeBuilder import RanobeBuilder
from Source.Core.Base.Formats.Components import By, ContentTypes
from Source.Core.Base.Builders.MangaBuilder import MangaBuilder
from Source.Utils.Development import DevelopmeptAssistant
from Source.Core.SystemObjects import SystemObjects
from Source.Utils.Collector import Collector
from Source.Utils.Installer import Installer
from Source.Utils.Cacher import Cacher
from Source import Utils
from Source.Utils.Timer import Timer
from Source.Core import Exceptions
from Source.CLI.Legacy import Templates

from dublib.CLI.TextStyler import FastStyler, GetStyledTextFromHTML
from dublib.CLI.Templates.Bus import PrintError, PrintWarning
from dublib.CLI.Terminalyzer import ParsedCommandData
from dublib.Methods.Filesystem import WriteJSON
from dublib.Engine.Bus import ExecutionResult

from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING
from time import sleep
import traceback

if TYPE_CHECKING:
	from Source.Core.Base.Parsers.RanobeParser import RanobeParser
	from Source.Core.Base.Parsers.MangaParser import MangaParser
	from Source.Core.Base.Formats.Ranobe import Ranobe
	from Source.Core.Base.Formats.Manga import Manga

def com_build_manga(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Строит читаемый контент манги из описательного файла.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	Filename = command.arguments[0][:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	TimerObject = Timer(start = True)
	system_objects.logger.header("Building")
	BuildSystemName = None

	for MangaBuilderSystem in ("simple", "zip", "cbz"):
		if command.check_flag(MangaBuilderSystem):
			BuildSystemName = MangaBuilderSystem
			break

	EntryPoint = system_objects.controller.get_entry_point()
	Title: "Manga" = Title(system_objects)
	Title.open(Filename, By.Filename)
	Parser: "RanobeParser" = EntryPoint.launch_parser(ContentTypes.Ranobe)
	Title.set_parser(Parser)

	Builder = MangaBuilder(system_objects, Parser)
	Builder.select_build_system(BuildSystemName)
	if command.check_key("ch-template"): Builder.set_chapter_name_template(command.get_key_value("ch-template"))
	if command.check_key("vol-template"): Builder.set_volume_name_template(command.get_key_value("vol-template"))
	Title.open(Filename)
	
	if command.check_key("chapter"): Builder.build_chapter(Title, command.get_key_value("chapter"))
	elif command.check_key("branch"): Builder.build_branch(Title, command.get_key_value("branch"))
	else: Builder.build_branch(Title)
	TimerObject.done()

def com_build_ranobe(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Строит читаемый контент ранобэ из описательного файла.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	Filename = command.arguments[0][:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	TimerObject = Timer(start = True)
	system_objects.logger.header("Building")

	EntryPoint = system_objects.controller.get_entry_point()
	Title: "Ranobe" = Title(system_objects)
	Title.open(Filename, By.Filename)
	Parser: "RanobeParser" = EntryPoint.launch_parser(ContentTypes.Ranobe)
	Title.set_parser(Parser)

	Builder = RanobeBuilder(system_objects, Parser)
	if command.check_key("ch-template"): Builder.set_chapter_name_template(command.get_key_value("ch-template"))
	if command.check_key("vol-template"): Builder.set_volume_name_template(command.get_key_value("vol-template"))
	Title.open(Filename)
	Builder.build_branch(Title)
	TimerObject.done()





def com_init(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Производит инициализацию новых модулей для начала разработки.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	system_objects.logger.header("Initializing")
	Name = command.arguments[0]
	Assistant = DevelopmeptAssistant(system_objects)
	Types = Assistant.parse_content_types(command.get_key_value("content"))

	if command.check_flag("p"): Assistant.init_parser(Name, Types, git = command.check_flag("git"))
	else: Assistant.init_extension(Name)

def com_install(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Производит установку парсеров.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	FullInstallation = command.check_flag("all")
	HaveFalgs = bool(command.flags)
	system_objects.logger.header("Installation")
	print("Running installation…")
	InstallerObject = Installer(system_objects)
	TimerObject = Timer(start = True)

	if not HaveFalgs: 
		print("No installation options.")
		return

	if command.check_flag("a") or FullInstallation: InstallerObject.alias()
	if command.check_flag("r") or FullInstallation: InstallerObject.requirements()
	if command.check_flag("s") or FullInstallation: InstallerObject.scripts()
	if command.check_flag("c") or FullInstallation: InstallerObject.configs()
	if command.check_flag("t") or FullInstallation: InstallerObject.releases()
	TimerObject.done()



def com_parse(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Выполняет парсинг тайтла.

	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	Slugs = list()
	StartIndex = 0
	system_objects.logger.header("Parsing")

	IS_AMENDING_ENABLED = not command.check_flag("no-amend")
	IS_SORTING_ENABLED = command.check_flag("sort")
	if not IS_AMENDING_ENABLED: system_objects.logger.warning("Amending chapters content disabled.")
	if IS_SORTING_ENABLED: system_objects.logger.info("Sorting chapters enabled.")
	
	EntryPoint = system_objects.controller.get_entry_point()

	if command.check_flag("last"):

		if not system_objects.CACHING:
			Status = ExecutionResult()
			Status.push_error("Caching disabled. Last slug unavailable.")
			Status.print_messages()
			return

		if not system_objects.temper.shared_data.last_parsed_slug:
			Status = ExecutionResult()
			Status.push_error("Last slug undefined. Parse anything firstly.")
			Status.print_messages()
			return
		
		else: Slugs.append(system_objects.temper.shared_data.last_parsed_slug)
			
	elif command.check_flag("collection"):
		Slugs = Collector(system_objects).slugs
		system_objects.logger.info(f"Titles in collection: {len(Slugs)}.")

	elif command.check_flag("updates"):
		Period = int(command.get_key_value("period")) if command.check_key("period") else 24
		print("Collecting updates…")
		Slugs = EntryPoint.source_operator.collect(period = Period)
		
	elif command.check_flag("local"):
		TimerObject = Timer(start = True)
		print("Scanning titles… ", end = "", flush = True)
		CollectorObject = Collector(system_objects)
		CollectorObject.from_local()
		Slugs += CollectorObject.slugs
		ElapsedTime = TimerObject.ends()
		print(f"Done in {ElapsedTime}.")
		Text = "Local titles to parsing: " + str(len(Slugs)) + "."
		system_objects.logger.info(Text, stdout = True)

	elif command.check_key("id"):
		TitleID = command.get_key_value("id")
		TitleSlug = system_objects.temper.shared_data.journal.get_slug_by_id(TitleID)
		if TitleSlug: Slugs.append(TitleSlug)

	else:
		Data = command.arguments[0]
		Slug = EntryPoint.source_operator.get_slug_from_string(Data).value

		if not Slug: 
			PrintError(f"Unable to parse slug from: \"{Data}.\"")
			return
		
		Slugs.append(Slug)
		
	if command.check_key("from"):
		system_objects.logger.info("Processing will be started from slug: \"" + command.get_key_value("from") + "\".")
			
		if command.get_key_value("from") in Slugs: StartIndex = Slugs.index(command.get_key_value("from"))
		else: system_objects.logger.warning("No starting slug in collection. Ignored.")

	ParsedCount = 0
	NotFoundCount = 0
	ErrorsCount = 0
	TotalCount = len(Slugs)
	Parser: "MangaParser | RanobeParser" = None

	for Index in range(StartIndex, TotalCount):
		if system_objects.CACHING: system_objects.temper.shared_data.set_last_parsed_slug(Slugs[Index])
		ContentType = EntryPoint.get_content_type_by_slug(Slugs[Index])
		if not Parser or ContentType != Parser.content_type: Parser = EntryPoint.launch_parser(ContentType)
		Title = EntryPoint.create_title(ContentType, Slugs[Index])
		Title.set_parser(Parser)

		try:
			TimerObject = Timer(start = True)
			
			Title.parse(Index, TotalCount)
			if not system_objects.FORCE_MODE: Title.merge()
			if IS_AMENDING_ENABLED: Title.amend()
			Title.download_images()
			Title.save(sorting = IS_SORTING_ENABLED)

			TimerObject.done()
			ParsedCount += 1

		except JSONDecodeError as ExceptionData:
			system_objects.logger.error(str(ExceptionData))
			ErrorsCount += 1

		except Exceptions.UnsupportedFormat as ExceptionData:
			system_objects.logger.error(str(ExceptionData))
			ErrorsCount += 1

		except Exceptions.AuthorizationRequired: break
		except Exceptions.ParsingError: ErrorsCount += 1
		except Exceptions.TitleNotFound: NotFoundCount += 1
		
		except Exception as ExceptionData:
			print(FastStyler(traceback.format_exc().rstrip()).colorize.red)
			system_objects.logger.error(f"Raised exception: \"{ExceptionData}\".", stdout = False)
			system_objects.logger.warning("Current title skipped due to exception.")
			ErrorsCount += 1

		if Index != len(Slugs) - 1: sleep(EntryPoint.settings.common.delay)

	Templates.ParsingSummary(ParsedCount, NotFoundCount, ErrorsCount)

def com_repair(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Восстанавливает содержимое главы, заново получая его из источника.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	Filename = command.arguments[0][:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	ChapterID = command.get_key_value("chapter")
	EntryPoint = system_objects.controller.get_entry_point()
	ContentType = EntryPoint.get_content_type_by_file(Filename)
	Parser = EntryPoint.launch_parser(ContentType)
	Title = EntryPoint.create_title(ContentType)
	Title.set_parser(Parser)
	system_objects.logger.header("Repairing")
	system_objects.EXIT_CODE = -1

	try:
		TimerObject = Timer(start = True)

		Title.open(Filename)
		Title.repair(ChapterID)
		Title.save(sorting = False)

		TimerObject.done()

	except Exceptions.ChapterNotFound: system_objects.logger.error(f"Chapter with ID {ChapterID} not found in JSON.")
	except FileNotFoundError: system_objects.logger.error(f"File \"{Filename}.json\" not found in titles directory.")
	except (Exceptions.TitleNotFound, Exceptions.ParsingError): pass
	else: system_objects.EXIT_CODE = 0