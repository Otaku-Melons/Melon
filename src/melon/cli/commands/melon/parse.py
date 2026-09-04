import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from json import JSONDecodeError
from typing import TYPE_CHECKING, Sequence, override

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.cli.text_styler import GetStyledTextFromHTML

from .... import utils
from ....core import exceptions
from ....core.base.parsers.components.manifest import ContentTypes
from ..base_processor import PreparedData
from ..base_processor.templates import (
	T_ForceModeRequired,
	T_SingleParserRequired,
)
from ._base import CommandProcessorTemplate

if TYPE_CHECKING:
	from ....core.base.formats.base_format.controller import BaseTitleController
	from ....core.base.parsers.base_parser import BaseParser
	from ....core.base.source_operator import BaseSourceOperator

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class _BaseParserTarget(ABC):
	"""Базовая цель для парсинга."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@property
	def is_used(self) -> bool:
		"""Состояние: используется ли этот тип цели."""

		return self._IsUsed()

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Список алиасов.
		:rtype: list[str]
		"""

		pass

	@abstractmethod
	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator", data: ParsedCommandData):
		"""
		Базовая цель для парсинга.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		"""

		self._SourceOperator = source_operator
		self._Data = data

		self._Printer = self._SourceOperator.portals.printer

	def get_slugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.

		:return: Список алиасов.
		:rtype: list[str]
		"""

		return self._GetSlugs()

class PasingTarget_Collection(_BaseParserTarget):
	"""Цель для парсинга: коллекция."""

	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Список алиасов.
		:rtype: list[str]
		"""

		Filename: str | None = self._Data.get_key_value("--collection", expected_type = str)
		if Filename == ".": Filename = None
		Collector = utils.Collector(self._SourceOperator, Filename)
		Collector.load()
		Slugs = list(Collector.slugs)
		self._Printer.emit(f"Titles in collection: {len(Slugs)}.")

		return Slugs

	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		return self._Data.check_key("--collection")

class PasingTarget_ID(_BaseParserTarget):
	"""Цель для парсинга: тайтл по ID."""

	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.
		
		:return: Список алиасов.
		:rtype: list[str]
		"""

		ID: int | None = self._Data.get_key_value("--id", expected_type = int)
		if not ID: return []

		SlugByID = self._SourceOperator.shared_data.journal.get_slug_by_id(ID)
		if SlugByID: return [SlugByID]
		self._Printer.warning(f"Title with ID {SlugByID} uncached.")

		return []

	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		return self._Data.check_key("--id")

class PasingTarget_Last(_BaseParserTarget):
	"""Цель для парсинга: последний обработанный тайтл."""

	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.
		
		:return: Список алиасов.
		:rtype: list[str]
		"""

		Slugs: list[str] = []
		LastParsedSlug = self._SourceOperator.shared_data.last_parsed_slug

		if LastParsedSlug: Slugs.append(LastParsedSlug)
		else: self._Printer.warning("Last slug undefined. Parse anything firstly.")

		return Slugs

	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		return self._Data.check_flag("-last")

class PasingTarget_Local(_BaseParserTarget):
	"""Цель для парсинга: локальные тайтлы."""

	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.
		
		:return: Список алиасов.
		:rtype: list[str]
		"""

		Collector = utils.Collector(self._SourceOperator)
		self._SourceOperator.portals.printer.templates.collector.start()
		ScanningResult = Collector.collect_local()
		self._Printer.templates.collector.collected(ScanningResult.added)

		return list(ScanningResult.slugs)

	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		return self._Data.check_flag("-local")

class PasingTarget_Slug(_BaseParserTarget):
	"""Цель для парсинга: тайтл по алиасу."""

	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.
		
		:return: Список алиасов.
		:rtype: list[str]
		"""

		Slug: str = self._Data.get_important_position_value("TARGET", expected_type = str)
		TargetSlug: str | None = self._SourceOperator.parse_slug_from_string(Slug)
		if TargetSlug: return [TargetSlug]
		else: self._Printer.warning("Unable to parse title slug from target.")

		return []

	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		return not any((
			self._Data.check_flag("-last"),
			self._Data.check_flag("-local"),

			self._Data.check_key("--collection"),
			self._Data.check_key("--id"),
			self._Data.check_key("--updates")
		))

class PasingTarget_Updates(_BaseParserTarget):
	"""Цель для парсинга: обновления."""

	def _GetSlugs(self) -> list[str]:
		"""
		Возвращает список алиасов для парсинга.
		
		:return: Список алиасов.
		:rtype: list[str]
		"""

		Period: int = self._Data.get_key_value("--period", expected_type = int) or 24
		self._Printer.emit("Collecting updates…")
		Slugs = list(self._SourceOperator.collect_slugs(Period))
		self._Printer.emit(f"Updates collected: {len(Slugs)}.")

		return Slugs

	def _IsUsed(self) -> bool:
		"""
		Проверяет, используется ли текущий тип цели.

		:return: Возвращает `True`, если используется ли текущий тип цели.
		:rtype: bool
		"""

		return self._Data.check_key("--updates")

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class ParsingStatistics:
	"""Статистика парсинга."""

	parsed: int
	not_found: int
	errors: int

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired, T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	target: _BaseParserTarget
	parse_from: str | None

	is_sorting_enabled: bool
	is_amending_enabled: bool
	is_download_images: bool
	is_cold_saving: bool

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

	def __GetParsingTarget(self, data: ParsedCommandData, prepared_data: PreparedData) -> _BaseParserTarget:
		"""
		Определяет цель для парсинга.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedData
		:return: Цель для парсинга.
		:rtype: _BaseParserTarget
		"""

		Parser = prepared_data.required_parsers[0]
		TargetTypes: tuple[type[_BaseParserTarget], ...] = (
			PasingTarget_Collection,
			PasingTarget_ID,
			PasingTarget_Last,
			PasingTarget_Local,
			PasingTarget_Slug,
			PasingTarget_Updates
		)

		for Type in TargetTypes:
			Target = Type(Parser.source_operator, data)
			if Target.is_used: return Target

		raise exceptions.parsing.ParsingError("Unable determine parsing target.")

	def __ParseSlugs(self, parameters: Parameters, source_operator: "BaseSourceOperator", slugs: Sequence[str], start_index: int) -> ParsingStatistics:
		"""
		Парсит набор алиасов тайтлов.

		:param parameters: Параметры, требуемые обработчиком.
		:type parameters: Parameters
		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		:param slugs: Последовательность алиасов.
		:type slugs: Sequence[str]
		:param start_index: Индекс алиаса для старта парсинга.
		:type start_index: int
		:return: Статистика парсинга.
		:rtype: ParsingStatistics
		"""

		ParsedCount: int = 0
		NotFoundCount: int = 0
		ErrorsCount: int = 0
		TotalCount: int = len(slugs)
	
		CurrentContentType: ContentTypes | None = None
		Parser = source_operator.launch_parser()
	
		for Index in range(start_index, TotalCount):
			Slug = slugs[Index]
			source_operator.shared_data.set_last_parsed_slug(Slug)
			
			ContentType = source_operator.get_content_type_by_slug(Slug)
			if ContentType is not CurrentContentType:
				CurrentContentType = ContentType
				Parser = source_operator.launch_parser(ContentType)
	
			Title = Parser.init_empty_title(Slug)
			self.printer.templates.parsing.start(Title.data, Index, TotalCount)
	
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
	
			if not Title.is_local_file_loaded and not parameters.is_cold_saving:
				self.printer.emit("Cold saving disabled by flag. Skipped.")
			else:
				if Parser.save(parameters.is_sorting_enabled): self.printer.emit("Saved.")
				else: self.printer.emit("No changes. Saving skipped.")
				
			ParsedCount += 1

		return ParsingStatistics(ParsedCount, NotFoundCount, ErrorsCount)

	def __ParseAndCatchExceptions(self, parameters: Parameters, parser: "BaseParser", title: "BaseTitleController") -> ParsingSignals:

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

		except exceptions.parsing.AuthorizationRequired:
			return ParsingSignals.Break

		except exceptions.parsing.ParsingError:
			return ParsingSignals.Error

		except exceptions.parsing.TitleNotFound:
			return ParsingSignals.NotFound

		except (JSONDecodeError, exceptions.parsers.UnsupportedFormat):
			self.printer.error("Unsupported JSON format or decoding error.")
			return ParsingSignals.Error

		except Exception:
			Traceback = traceback.format_exc().rstrip()
			self.printer.error(f"Current title skipped due to exception: \"{Traceback}\".")
			return ParsingSignals.Error

		return ParsingSignals.OK

	def __SkipSlugsBefore(self, slugs: tuple[str, ...], starting_slug: str) -> int:
		"""
		Определяет стартовый индекс последовательности для парсинга.

		:param slugs: Алиасы тайтлов для парсинга.
		:type slugs: tuple[str, ...]
		:param starting_slug: Алиас, с которого необходимо начать парсинг.
		:type starting_slug: str
		:return: Индекс стартового алиаса или `-1`, если алиас не удалось найти.
		:rtype: int
		"""

		if starting_slug not in slugs:
			self.printer.warning("Starting slug not found in targets. Ignored.")
			return -1

		self.printer.emit(f"Parsing started from title: \"{starting_slug}\".")

		return slugs.index(starting_slug)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@override
	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Parse titles."

	@override
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
		ComPos.add_flag("-local", description = "Parse all locally saved titles.")
		ComPos.add_flag("-last", description = "Parse last parsed title.")
		ComPos.add_key("--collection", description = GetStyledTextFromHTML("Name of collection file. Put . to default <i>collection</i>."))
		ComPos.add_key("--id", value_type = ValidableTypes.UnsignedInteger, description = "Title ID.")
		ComPos.add_key("--updates", value_type = ValidableTypes.UnsignedInteger, description = "Parse updates for period in hours.")

		self._AddParserPosition(key = "--use")

		self._AddForceModeFlag()

		command.base.add_flag("-no-amend", description = "Disable chapters content amending.")
		command.base.add_flag("-no-images", description = "Disable covers and persons portraits downloading.")
		command.base.add_flag("-sort", description = "Enable chapters sorting after parsing.")
		command.base.add_flag("-no-cold-save", description = "Disable saving if local file does't exists.")

		self._AddMirrorKey()

		command.base.add_key("--from", description = "Skip titles before this slug.")

		return command

	@override
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

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			target = self.__GetParsingTarget(data, prepared_data),
			parse_from = data.get_key_value("--from", expected_type = str),
			
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			is_sorting_enabled = data.check_flag("-sort"),
			is_amending_enabled = not data.check_flag("-no-amend"),
			is_download_images = not data.check_flag("-no-images"),
			is_cold_saving = not data.check_flag("-no-cold-save")
		)

	@override
	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Slugs: tuple[str, ...] =  tuple(sorted(parameters.target.get_slugs()))
		StartIndex: int = 0

		if parameters.parse_from:
			TargetStartIndex: int = self.__SkipSlugsBefore(Slugs, parameters.parse_from)
			if TargetStartIndex: StartIndex = TargetStartIndex
	
		if not Slugs:
			self.printer.error("No slugs for parsing.")
			return False

		Statistics = self.__ParseSlugs(parameters, parameters.required_parser.source_operator, Slugs, StartIndex)
		self.printer.templates.parsing.summary(Statistics.parsed, Statistics.not_found, Statistics.errors)

		return True