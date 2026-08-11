import traceback
from dataclasses import dataclass
from enum import Enum
from json import JSONDecodeError
from typing import TYPE_CHECKING

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.cli.text_styler import GetStyledTextFromHTML

from .... import utils
from ....core import exceptions
from ....core.base.parsers.components.manifest import ContentTypes
from ..base_processor import (
	PreparedData,
	T_ForceModeRequired,
	T_SingleParserRequired,
)
from ._base import CommandProcessorTemplate

if TYPE_CHECKING:
	from ....core.base.entry_point import BaseEntryPoint
	from ....core.base.formats.base_format import BaseTitle
	from ....core.base.parsers.base_parser import BaseParser
	from ....core.base.source_operator import BaseSourceOperator

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class ParsingStatistics:
	"""Статистика парсинга."""

	parsed: int
	not_found: int
	errors: int

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired, T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	target: str
	parse_from: str | None
	updates_period: int | None
	parse_by_id: int | None

	is_sorting_enabled: bool
	is_amending_enabled: bool
	is_download_images: bool

	is_parse_last_title: bool
	is_parse_collection: bool
	is_parse_updates: bool
	is_parse_local: bool

class ParsingSignals(Enum):
	"""Сигналы парсинга."""

	OK = 0
	Break = 1
	NotFound = 2
	Error = 3

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetSlugsToParsing(self, parameters: Parameters, entry_point: "BaseEntryPoint") -> tuple[str, ...]:
		"""
		Определяет последовательность алиасов тайтлов для парсинга.

		:param parameters: Параметры, требуемые обработчиком.
		:type parameters: Parameters
		:param entry_point: Точка входа в парсер.
		:type entry_point: BaseEntryPoint
		:return: Последовательность алиасов.
		:rtype: tuple[str, ...]
		"""

		SourceOperator = entry_point.source_operator
		Slugs: list[str] = []
			
		if parameters.is_parse_last_title:
			LastParsedSlug = SourceOperator.shared_data.last_parsed_slug
	
			if LastParsedSlug:
				Slugs.append(LastParsedSlug)
			else:
				self.printer.warning("Last slug undefined. Parse anything firstly.")
	
		elif parameters.is_parse_collection:
			Collector = utils.Collector(entry_point)
			Slugs = list(Collector.load())
			self.printer.emit(f"Titles in collection: {len(Slugs)}.")
	
		elif parameters.is_parse_updates:
			self.printer.emit("Collecting updates…")
			Slugs = list(SourceOperator.collect_slugs(period = parameters.updates_period or 24))
			self.printer.emit(f"Updates collected: {len(Slugs)}.")
	
		elif parameters.is_parse_local:
			Collector = utils.Collector(entry_point)
			SlugsCount = Collector.scan_local()
			Slugs = list(Collector.slugs)
			self.printer.emit(f"Local titles to parsing: {SlugsCount}.")
	
		elif parameters.parse_by_id:
			SlugByID = SourceOperator.shared_data.journal.get_slug_by_id(parameters.parse_by_id)
	
			if SlugByID:
				Slugs.append(SlugByID)
			else:
				self.printer.warning(f"Title with ID {SlugByID} uncached.")
	
		else:
			TargetSlug = SourceOperator.parse_slug_from_string(parameters.target)
	
			if TargetSlug:
				Slugs.append(TargetSlug)
			else:
				self.printer.warning("Unable to parse title slug from target.")

		return tuple(Slugs)

	def __ParseSlugs(self, parameters: Parameters, source_operator: "BaseSourceOperator", slugs: tuple[str, ...]) -> ParsingStatistics:
		"""
		Парсит набор алиасов тайтлов.

		:param parameters: Параметры, требуемые обработчиком.
		:type parameters: Parameters
		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		:param slugs: Последовательность алиасов.
		:type slugs: tuple[str, ...]
		:return: Статистика парсинга.
		:rtype: ParsingStatistics
		"""

		ParsedCount: int = 0
		NotFoundCount: int = 0
		ErrorsCount: int = 0
		TotalCount: int = len(slugs)
	
		CurrentContentType: ContentTypes | None = None
		Parser = source_operator.launch_parser()
	
		for Index in range(len(slugs)):
			Slug = slugs[Index]
			source_operator.shared_data.set_last_parsed_slug(Slug)
			
			ContentType = source_operator.get_content_type_by_slug(Slug)
			if ContentType is not CurrentContentType:
				CurrentContentType = ContentType
				Parser = source_operator.launch_parser(ContentType)
	
			Title = Parser.init_empty_title(Slug)
			self.printer.stages.parsing_start(Title, Index, TotalCount)
	
			ChaptersLoaded = Title.chapters_count
			if ChaptersLoaded:
				BranchesCount = len(Title.branches)
				self.printer.emit(f"Loaded {ChaptersLoaded} chapters on {BranchesCount} branches.")
	
			match self.__ParseAndCatchExceptions(parameters, Parser, Title):

				case ParsingSignals.Break:
					break

				case ParsingSignals.NotFound:
					NotFoundCount += 1
					continue

				case ParsingSignals.Error:
					ErrorsCount += 1
					continue

			if parameters.is_download_images: Parser.download_images(parameters.is_force_mode_enabled)
			else: self.printer.emit("Images downloading skipped by flag.")
	
			if Parser.save(parameters.is_sorting_enabled): self.printer.emit("Saved.")
			else: self.printer.emit("No changes. Saving skipped.")
			ParsedCount += 1

		return ParsingStatistics(ParsedCount, NotFoundCount, ErrorsCount)

	def __ParseAndCatchExceptions(self, parameters: Parameters, parser: "BaseParser", title: "BaseTitle") -> ParsingSignals:

		try:
			parser.parse()
			
			if not parameters.is_force_mode_enabled:
				MergedChaptersCount = title.merge()
				if MergedChaptersCount: self.printer.emit(f"Merged {MergedChaptersCount} chapters.")

			if parameters.is_amending_enabled:
				if title.empty_chapters_count: parser.amend()
				else: self.printer.emit("No empty chapters. Amending skipped.")
			else:
				self.printer.emit("Amending skipped by flag.")

		except exceptions.parsers.AuthorizationRequired:
			return ParsingSignals.Break

		except exceptions.parsers.ParsingError:
			return ParsingSignals.Error

		except exceptions.parsers.TitleNotFound:
			return ParsingSignals.NotFound

		except (JSONDecodeError, exceptions.parsers.UnsupportedFormat):
			self.printer.error("Unsupported JSON format or decoding error.")
			return ParsingSignals.Error

		except Exception:
			Traceback = traceback.format_exc().rstrip()
			self.printer.error(f"Current title skipped due to exception: \"{Traceback}\".")
			return ParsingSignals.Error

		return ParsingSignals.OK

	def __SkipSlugsBefore(self, slugs: tuple[str, ...], starting_slug: str) -> tuple[str, ...]:
		"""
		Пропускает алиасы из последовательности до указанного методом среза. Если целевой алиас не найден, возвращает всю последовательность.

		:param slugs: Алиасы тайтлов для парсинга.
		:type slugs: tuple[str, ...]
		:param starting_slug: Алиас, с которого необходимо начать парсинг.
		:type starting_slug: str
		:return: Последовательность алиасов.
		:rtype: tuple[str, ...]
		"""

		if starting_slug not in slugs:
			self.printer.warning("Starting slug not found in targets. Ignored.")
			return slugs

		self.printer.emit(f"Parsing started from title: \"{starting_slug}\".")
		StartIndex = slugs.index(starting_slug)
		slugs = slugs[StartIndex:]

		return slugs

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Parse titles."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("TARGET", "Target for parsing.", important = True)
		ComPos.set_argument(description = "Title slug.")
		ComPos.add_flag("-collection", description = GetStyledTextFromHTML("Parse slugs from <i>collection.txt</i> file."))
		ComPos.add_flag("-local", description = "Parse all locally saved titles.")
		ComPos.add_flag("-updates", description = "Parse titles updated for last 24 hours. Use key \"--period\" to change it.")
		ComPos.add_flag("-last", description = "Parse last parsed title.")
		ComPos.add_key("--id", type = ValidableTypes.UnsignedInteger, description = "Title ID.")

		self._AddParserPosition()

		self._AddForceModeFlag()

		command.base.add_flag("-no-amend", description = "Disable chapters content amending.")
		command.base.add_flag("-no-images", description = "Disable covers and persons portraits downloading.")
		command.base.add_flag("-sort", description = "Enable chapters sorting after parsing.")
		
		self._AddMirrorKey()

		command.base.add_key("--period", type = ValidableTypes.UnsignedInteger, description = "Period in hours for parsing. Use with \"-updates\" flag.")
		command.base.add_key("--from", description = "Skip titles before this slug.")

		return command

	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> Parameters:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedData
		:return: Структура **dataclass**.
		:rtype: Parameters
		"""

		Target: str = data.get_important_position_value("TARGET", expected_type = str)
	
		ParseFrom: str | None = data.get_key_value("--from", expected_type = str)
		IsSortingEnabled: bool = data.check_flag("-sort")
		IsAmendingEnabled: bool = not data.check_flag("-no-amend")
	
		ParseLastTitle: bool = data.check_flag("-last")
		ParseCollection: bool = data.check_flag("-collection")
		ParseUpdates: bool = data.check_flag("-updates")
		UpdatesPeriod: int | None = data.get_key_value("--period", expected_type = int)
		ParseLocal: bool = data.check_flag("-local")
		ParseByID: int | None = data.get_key_value("--id", expected_type = int)
		DownloadImages: bool = not data.check_flag("-no-images")

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			target = Target,
			parse_from = ParseFrom,
			updates_period = UpdatesPeriod,
			parse_by_id = ParseByID,
			
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			is_sorting_enabled = IsSortingEnabled,
			is_amending_enabled = IsAmendingEnabled,
			is_download_images = DownloadImages,
		
			is_parse_last_title = ParseLastTitle,
			is_parse_collection = ParseCollection,
			is_parse_updates = ParseUpdates,
			is_parse_local = ParseLocal
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Slugs: tuple[str, ...] = self.__GetSlugsToParsing(parameters, parameters.required_parser.entry_point)

		if parameters.parse_from:
			Slugs = self.__SkipSlugsBefore(Slugs, parameters.parse_from)
	
		if not Slugs:
			self.printer.error("No slugs for parsing.")
			return False

		Statistics = self.__ParseSlugs(parameters, parameters.required_parser.source_operator, tuple(Slugs))
		self.printer.templates.parsing_summary(Statistics.parsed, Statistics.not_found, Statistics.errors)

		return True