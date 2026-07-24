import traceback
from json import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, cast

import orjson

from dublib.Methods.Filesystem import WriteJSON

from Source import Utils
from Source.Core import Exceptions
from Source.Core.Base.Formats.Components.Enums import By
from Source.Core.Base.Parsers.Components.Manifest import ContentTypes
from Source.Core.Builders.MangaBuilder import MangaBuilder, MangaOutputFormats
from Source.Core.Builders.RanobeBuilder import RanobeBuilder

from . import Functions

if TYPE_CHECKING:
	from dublib.CLI.Terminalyzer import ParsedCommandData

	from Source.Core.Base.Parsers.BaseParser import BaseParser
	from Source.Core.SystemObjects import SystemObjects

def com_build_manga(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Строит читаемый контент манги из описательного файла.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Filename: str = command.get_important_position_value("FILE", expected_type = str)
	ParserName: str = command.get_important_position_value("PARSER", expected_type = str)

	TargetID: int = command.get_important_position_value("TARGET", expected_type = int)
	IsTargetChapter: bool = command.check_key("--chapter")

	OutputFormat: str | None = command.get_position_value("FORMAT", expected_type = str)
	if OutputFormat: OutputFormat = OutputFormat.lstrip("-")

	ChapterTemplate: str | None = command.get_key_value("--ct", expected_type = str)
	VolumeTemplate: str | None = command.get_key_value("--vt", expected_type = str)

	SortByVolumes: bool = command.check_flag("-s")

	if not Filename.endswith(".json"):
		Filename += ".json"

	if ParserName not in system_objects.driver.parsers_names:
		raise Exceptions.System.ParserNotFound(ParserName)

	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	EntryPoint = system_objects.driver.get_entry_point(ParserName)
	SourceOperator = EntryPoint.source_operator
	TypingResult = EntryPoint.get_content_type_by_file(Filename)
	Parser: BaseParser = SourceOperator.launch_parser(TypingResult.content_type)
	Title = Parser.init_empty_title(TypingResult.slug)

	if Title.load(Filename, By.Filename):
		system_objects.printer.emit(f"Loaded file: <i>{Filename}</i>.")
	else:
		system_objects.printer.error(f"Unable load file: <b>{Filename}</b>.")
		exit(1)

	Builder = MangaBuilder(Parser, Title)
	if OutputFormat: Builder.select_output_format(MangaOutputFormats(OutputFormat))
	if ChapterTemplate: Builder.set_chapter_name_template(ChapterTemplate)
	if VolumeTemplate: Builder.set_volume_name_template(VolumeTemplate)
	Builder.switch_volumes_sorting(SortByVolumes)

	if IsTargetChapter:
		Builder.build_chapter(TargetID)
	elif command.check_key("--branch"):
		Builder.build_branch(TargetID)
	else:
		Builder.build_branch()

	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_build_ranobe(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Строит читаемый контент ранобэ из описательного файла.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Filename: str = command.get_important_position_value("FILE", expected_type = str)
	ParserName: str = command.get_important_position_value("PARSER", expected_type = str)
	BranchID: int | None = command.get_key_value("--branch", expected_type = int)

	if not Filename.endswith(".json"):
		Filename += ".json"

	if ParserName not in system_objects.driver.parsers_names:
		raise Exceptions.System.ParserNotFound(ParserName)

	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	EntryPoint = system_objects.driver.get_entry_point(ParserName)
	SourceOperator = EntryPoint.source_operator
	TypingResult = EntryPoint.get_content_type_by_file(Filename)
	Parser: BaseParser = SourceOperator.launch_parser(TypingResult.content_type)
	Title = Parser.init_empty_title(TypingResult.slug)

	if Title.load(Filename, By.Filename):
		system_objects.printer.emit(f"Loaded file: <i>{Filename}</i>.")
	else:
		system_objects.printer.error(f"Unable load file: <b>{Filename}</b>.")
		exit(1)

	Builder = RanobeBuilder(Parser, Title)
	Builder.build(BranchID)

	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_cacher(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Кэширует пары ID-алиас для ускорения файловых операций.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	KeyValue: str | None = command.get_key_value("--use", expected_type = str)
	Parsers: tuple[str, ...] = Functions.GetParsersNamesFromKey(system_objects, KeyValue)
			
	#---> Выполнение команды.
	#==========================================================================================#
	TimerObject = Utils.Timer(start = True)

	for CurrentParser in Parsers:
		system_objects.printer.emit(f"Caching titles for <b>{CurrentParser}</b>…")
		EntryPoint = system_objects.driver.get_entry_point(CurrentParser)
		Cacher = Utils.Cacher(EntryPoint)

		Result = Cacher.cache_parser_output()
		system_objects.printer.templates.caching_summary(Result)
	
	system_objects.printer.emit(f"Done in {TimerObject.ends()}.")

def com_classify(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Определяет тип классификатора и требуемые для него операции преобразования.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Target: str = command.get_important_position_value("VALUE", expected_type = str)
	IsOutputJSON: bool = command.check_flag("-j")
	FileToWrite: Path | None = command.get_key_value("--file", expected_type = Path)
	IgnoreCase: bool = command.check_flag("-i")

	#---> Выполнение команды.
	#==========================================================================================#
	ScriptPath: Path = Path("Configs/classificator.ini")

	if not ScriptPath.exists():
		system_objects.printer.critical(f"Script file \"{ScriptPath}\" doesn't exists.")
		return None
	
	ClassificatorObject = Utils.Classificator(ScriptPath)
	ExecutableLines = ClassificatorObject.read_script()
	ScriptValidationErrors = ClassificatorObject.validate_script(ExecutableLines)

	for ErrorData in ScriptValidationErrors:
		system_objects.printer.error(f"[{ErrorData.line.file.name}:{ErrorData.line.number}] {ErrorData.message}")

	if ScriptValidationErrors:
		system_objects.printer.critical("Script failure due to validation errors.")
		return None

	try:
		Procedures = ClassificatorObject.parse_procedures(ExecutableLines)
	except Exceptions.Utils.Classificator.ScriptRuntimeError as ExecutionData:
		system_objects.printer.critical(str(ExecutionData))
		return None
	
	ClassificationResult = ClassificatorObject.classify(Target, Procedures, ignore_case = IgnoreCase)

	if IsOutputJSON:
		system_objects.printer.emit(orjson.dumps(ClassificationResult.to_dict()).decode())
	else:
		system_objects.printer.templates.classification_result(ClassificationResult)

	if FileToWrite:
		WriteJSON(FileToWrite, ClassificationResult.to_dict())
		system_objects.printer.emit(f"Classification result dumped in file: \"{FileToWrite}\".")

def com_collect(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Собирает алиасы тайтлов в файл _Collection.txt_ во временном каталоге парсера.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Parser: str = cast(str, command.get_key_value("--use", expected_type = str))
	ForceMode: bool = command.check_flag("-f")
	CollectLocal: bool = command.check_flag("-local")
	IsSortingEnabled: bool = not command.check_flag("-no-sort")

	Period: int | None = command.get_key_value("--period", expected_type = int)
	Filters: str | None = command.get_key_value("--filters", expected_type = str)
	Pages: int | None = command.get_key_value("--pages", expected_type = int)

	if Parser not in system_objects.driver.parsers_names:
		raise Exceptions.System.ParserNotFound(Parser)	
			
	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	EntryPoint = system_objects.driver.get_entry_point(Parser)
	Collector = Utils.Collector(EntryPoint)
	if not ForceMode: Collector.load()
	AddedSlugs: int = 0

	if CollectLocal:
		AddedSlugs = Collector.scan_local()
	elif EntryPoint.source_operator.is_collector_implemented:
		CollectedSlugs = EntryPoint.source_operator.collect_slugs(Period, Filters, Pages)
		AddedSlugs = Collector.add(CollectedSlugs)
	else:
		system_objects.printer.critical("Collector method not implemented.")
		return

	Collector.save(sort = IsSortingEnabled)

	if AddedSlugs:
		system_objects.printer.emit(f"Slugs collected: {AddedSlugs}.")
	else:
		system_objects.printer.emit("No new slugs in collection.")

	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_fid(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Ищет ID тайтла по алиасу в кэше.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Slug: str = command.get_important_position_value("SLUG", expected_type = str)
	Parsers: tuple[str, ...] = Functions.GetParsersNamesFromKey(system_objects, command.get_key_value("--use", expected_type = str))
	SearchAll: bool = command.check_flag("-all")

	#---> Выполнение команды.
	#==========================================================================================#
	ResultsCount: int = 0
	Timer = Utils.Timer(start = True)

	for CurrentParser in Parsers:
		EntryPoint = system_objects.driver.get_entry_point(CurrentParser)
		ID = EntryPoint.shared_data.journal.get_id_by_slug(Slug)

		if ID:
			ResultsCount += 1
			system_objects.printer.emit(f"Found ID {ID} for parser \"{CurrentParser}\".")

			if not SearchAll:
				break

	if ResultsCount:
		system_objects.printer.emit(f"Total ID found in cache: {ResultsCount}.")
	else:
		system_objects.printer.emit("Tite with same slug not found in cache.")
	
	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_get(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Скачивает изображение.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Link: str = cast(str, command.get_position_value("URL", expected_type = str))
	Parser: str = cast(str, command.get_key_value("--use", expected_type = str))
	Directory: Path | None = command.get_key_value("--dir", expected_type = Path)
	ForceMode: bool = command.check_flag("-f")

	FullName: str | None = command.get_key_value("--fullname", expected_type = str)
	Name: str | None = command.get_key_value("--name", expected_type = str)

	if Parser not in system_objects.driver.parsers_names:
		raise Exceptions.System.ParserNotFound(Parser)

	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	EntryPoint = system_objects.driver.get_entry_point(Parser)
	Result = EntryPoint.source_operator.download_image(Link, Directory, FullName or Name, bool(FullName), ForceMode)

	if Result.error_message:
		system_objects.printer.error(Result.error_message)
	elif Result.is_already_exists and not Result.is_downloaded:
		system_objects.printer.emit("Image already exists.")
	elif Result.is_already_exists and Result.is_downloaded:
		system_objects.printer.emit("Image overwritten.")
	
	if Result.path:
		system_objects.printer.emit(f"Image path: \"{Result.path}\".")

	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_list(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Выводит список парсеров.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Выполнение команды.
	#==========================================================================================#
	TableData: dict[str, list[str]] = {
		"NAME": [],
		"VERSION": [],
		"TYPES": [],
		"SITE": [],
		"collect": []
	}

	for ParserName in system_objects.driver.parsers_names:
		EntryPoint = system_objects.driver.get_entry_point(ParserName)
		TypesEmoji = {
			ContentTypes.Manga: "m",
			ContentTypes.Ranobe: "r"
		}

		ParserVersion = EntryPoint.version or ""
		ParserContentTypes: list[str] = [TypesEmoji[CurrentType] for CurrentType in EntryPoint.manifest.content_types]
		ParserSite: str = "https://" + EntryPoint.manifest.site

		TableData["NAME"].append(ParserName)
		TableData["VERSION"].append(ParserVersion)
		TableData["TYPES"].append(", ".join(ParserContentTypes))
		TableData["SITE"].append(ParserSite)
		TableData["collect"].append(str(EntryPoint.source_operator.is_collector_implemented))

	system_objects.printer.templates.parsers_table(TableData)

def com_new(system_objects: SystemObjects, command: ParsedCommandData):
	"""
	Иницилизирует новый парсер для разработки.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	ParserName: str = command.get_important_position_value("NAME", expected_type = str)
	Domain: str = command.get_important_position_value("DOMAIN", expected_type = str)
	UseGit: bool = command.check_flag("-git")
	ContentTypesString: str = command.get_important_position_value("CONTENT_TYPES", expected_type = str)
	ContentTypesValues = Utils.DevelopmeptAssistant.parse_content_types(ContentTypesString)

	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	Developer = Utils.DevelopmeptAssistant(system_objects)
	Developer.create_parser(ParserName, Domain, ContentTypesValues, UseGit)
	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_parse(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Парсит тайтлы.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Парсинг параметров команды.
	#==========================================================================================#
	Target: str = command.get_important_position_value("TARGET", expected_type = str)
	ParserName: str = cast(str, command.get_key_value("--use", expected_type = str))

	ForceMode: bool = command.check_flag("-f")
	ParseFrom: str | None = command.get_key_value("--from", expected_type = str)
	IsSortingEnabled: bool = command.check_flag("-sort")
	IsAmendingEnabled: bool = not command.check_flag("-no-amend")

	ParseLastTitle: bool = command.check_flag("-last")
	ParseCollection: bool = command.check_flag("-collection")
	ParseUpdates: bool = command.check_flag("-updates")
	UpdatesPeriod: int | None = command.get_key_value("--period", expected_type = int)
	ParseLocal: bool = command.check_flag("-local")
	ParseByID: int | None = command.get_key_value("--id", expected_type = int)
	DownloadImages: bool = not command.check_flag("-no-images")

	if ParserName not in system_objects.driver.parsers_names:
		raise Exceptions.System.ParserNotFound(ParserName)
	
	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	EntryPoint = system_objects.driver.get_entry_point(ParserName)
	SourceOperator = EntryPoint.source_operator

	Slugs: list[str] = list()

	if ParseLastTitle:
		LastParsedSlug = SourceOperator.shared_data.last_parsed_slug

		if LastParsedSlug:
			Slugs.append(LastParsedSlug)
		else:
			system_objects.printer.warning("Last slug undefined. Parse anything firstly.")

	elif ParseCollection:
		Collector = Utils.Collector(EntryPoint)
		Slugs = list(Collector.load())
		system_objects.printer.emit(f"Titles in collection: {len(Slugs)}.")

	elif ParseUpdates:
		system_objects.printer.emit("Collecting updates…")
		Slugs = list(EntryPoint.source_operator.collect_slugs(period = UpdatesPeriod or 24))
		system_objects.printer.emit(f"Updates collected: {len(Slugs)}.")

	elif ParseLocal:
		Collector = Utils.Collector(EntryPoint)
		SlugsCount = Collector.scan_local()
		Slugs = list(Collector.slugs)
		system_objects.printer.emit(f"Local titles to parsing: {SlugsCount}.")

	elif ParseByID:
		SlugByID = SourceOperator.shared_data.journal.get_slug_by_id(ParseByID)

		if SlugByID:
			Slugs.append(SlugByID)
		else:
			system_objects.printer.warning(f"Title with ID {SlugByID} uncached.")

	else:
		TargetSlug = EntryPoint.source_operator.parse_slug_from_string(Target)

		if TargetSlug:
			Slugs.append(TargetSlug)
		else:
			system_objects.printer.warning("Unable to parse title slug from target.")

	if ParseFrom:
		if ParseFrom in Slugs:
			system_objects.printer.emit(f"Parsing started from title: \"{ParseFrom}\".")
			StartIndex = Slugs.index(ParseFrom)
			Slugs = Slugs[StartIndex:]
		else:
			system_objects.printer.warning("Starting slug not found in targets. Ignored.")

	if not Slugs:
		system_objects.printer.error("No slugs for parsing.")
		system_objects.printer.emit(f"Done in {Timer.ends()}.")
		return

	ParsedCount: int = 0
	NotFoundCount: int = 0
	ErrorsCount: int = 0
	TotalCount: int = len(Slugs)

	CurrentContentType: ContentTypes | None = None
	Parser: BaseParser = SourceOperator.launch_parser()

	for Index in range(len(Slugs)):
		Slug = Slugs[Index]
		SourceOperator.shared_data.set_last_parsed_slug(Slug)
		
		ContentType = SourceOperator.get_content_type_by_slug(Slug)
		if ContentType is not CurrentContentType:
			CurrentContentType = ContentType
			Parser = SourceOperator.launch_parser(ContentType)

		Title = Parser.init_empty_title(Slug)
		system_objects.printer.stages.parsing_start(Title, Index, TotalCount)

		ChaptersLoaded = Title.chapters_count
		if ChaptersLoaded:
			BranchesCount = len(Title.branches)
			system_objects.printer.emit(f"Loaded {ChaptersLoaded} chapters on {BranchesCount} branches.")
		
		try:
			Parser.parse()

			if not ForceMode:
				MergedChaptersCount = Title.merge()
				if MergedChaptersCount: system_objects.printer.emit(f"Merged {MergedChaptersCount} chapters.")

			if IsAmendingEnabled:
				if Title.empty_chapters_count: Parser.amend()
				else: system_objects.printer.emit("No empty chapters. Amending skipped.")
			else:
				system_objects.printer.emit("Amending skipped by flag.")

		except Exceptions.Parsers.AuthorizationRequired:
			break

		except Exceptions.Parsers.ParsingError:
			ErrorsCount += 1
			continue

		except Exceptions.Parsers.TitleNotFound:
			NotFoundCount += 1
			continue

		except (JSONDecodeError, Exceptions.Parsers.UnsupportedFormat):
			system_objects.printer.error("Unsupported JSON format or decoding error.")
			ErrorsCount += 1
			continue

		except Exception:
			Traceback = traceback.format_exc().rstrip()
			system_objects.printer.error(f"Current title skipped due to exception: \"{Traceback}\".")
			ErrorsCount += 1
			continue

		if DownloadImages: Parser.download_images(ForceMode)
		else: system_objects.printer.emit("Images downloading skipped by flag.")

		if Parser.save(IsSortingEnabled): system_objects.printer.emit("Saved.")
		else: system_objects.printer.emit("No changes. Saving skipped.")
		ParsedCount += 1

	system_objects.printer.templates.parsing_summary(ParsedCount, NotFoundCount, ErrorsCount)
	system_objects.printer.emit(f"Done in {Timer.ends()}.")

def com_repair(system_objects: "SystemObjects", command: "ParsedCommandData"):
	"""
	Заново получает элемент контента с сервера.
		
	:param system_objects: Коллекция системных объектов.
	:type system_objects: SystemObjects
	:param command: Данные команды.
	:type command: ParsedCommandData
	"""

	#---> Выполнение команды.
	#==========================================================================================#
	Filename: str = command.get_important_position_value("FILE", expected_type = str)
	ParserName: str = command.get_important_position_value("PARSER", expected_type = str)
	TargetID: int = command.get_important_position_value("TARGET", expected_type = int)

	IsTargetChapter: bool = command.check_key("--chapter")

	if not IsTargetChapter:
		system_objects.printer.error("For now only chapters supported as target to repairing.")
		exit(1)

	if not Filename.endswith(".json"):
		Filename += ".json"

	if ParserName not in system_objects.driver.parsers_names:
		raise Exceptions.System.ParserNotFound(ParserName)
	
	#---> Выполнение команды.
	#==========================================================================================#
	Timer = Utils.Timer(start = True)
	EntryPoint = system_objects.driver.get_entry_point(ParserName)
	SourceOperator = EntryPoint.source_operator
	TypingResult = EntryPoint.get_content_type_by_file(Filename)
	Parser: BaseParser = SourceOperator.launch_parser(TypingResult.content_type)
	Title = Parser.init_empty_title(TypingResult.slug)

	if Title.load(Filename, By.Filename):
		system_objects.printer.emit(f"Loaded file: <i>{Filename}</i>.")
	else:
		system_objects.printer.error(f"Unable load file: <b>{Filename}</b>.")
		exit(1)

	system_objects.printer.emit(f"Repairing chapter <b>{TargetID}</b>… ", end_line = False)

	if Parser.repair(TargetID): system_objects.printer.emit("Done.")
	else: system_objects.printer.warning("Chapter is empty. Repairing failure?")

	if Parser.save(): system_objects.printer.emit("Saved.")
	else: system_objects.printer.emit("No changes. Saving skipped.")

	system_objects.printer.emit(f"Done in {Timer.ends()}.")