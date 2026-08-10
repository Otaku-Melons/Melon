import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Protocol, TypeVar

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from ... import utils
from ...core import exceptions

if TYPE_CHECKING:
	from ...core.base.entry_point import BaseEntryPoint
	from ...core.base.source_operator import (
		BaseSourceOperator,
		ParserManifest,
		ParserSettings,
	)
	from ...core.system_objects import SystemObjects
	from ...core.system_objects.printer import Printer
	
#==========================================================================================#
# >>>>> КОНСТРУКЦИИ АННОТАЦИЙ ТИПОВ <<<<< #
#==========================================================================================#

class AnyDataclass(Protocol):
	"""Протокол типизации: любой объект **dataclass**."""
	
	__dataclass_fields__: ClassVar[dict[str, Any]]

_PARAMS = TypeVar("_PARAMS", bound = AnyDataclass)

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class DataclassStub:
	"""Заглушка для команд, не требующих параметров."""

	pass

@dataclass(frozen = True)
class ProcessorOptions:
	"""Контейнер настроек обработчика."""

	use_timer: bool = True

@dataclass(frozen = True)
class RequiredParser:
	"""Коллекция управляющих объектов трубемого парсера."""

	name: str
	entry_point: "BaseEntryPoint"
	source_operator: "BaseSourceOperator"
	manifest: "ParserManifest"
	settinngs: "ParserSettings"

@dataclass(frozen = True)
class PreparedData:
	"""Предподготолвенные данные."""

	required_parsers: tuple[RequiredParser, ...]
	is_force_mode_enabled: bool
	mirror: str | None

#==========================================================================================#
# >>>>> ШАБЛОНЫ ПАРАМЕТРОВ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class T_ForceModeRequired:
	"""Шаблон: присутствует режим перезаписи."""

	is_force_mode_enabled: bool

@dataclass(frozen = True)
class T_MultipleParsersRequired:
	"""Шаблон: требуется несколько парсеров."""

	required_parsers: tuple[RequiredParser, ...]

@dataclass(frozen = True)
class T_SingleParserRequired:
	"""Шаблон: требуется один парсер."""

	required_parser: RequiredParser

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseCommandProcessor(ABC, Generic[_PARAMS]):
	"""Базовый обработчик команды."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def command(self) -> Command:
		"""Описание команды."""

		return self._Command

	@property
	def options(self) -> ProcessorOptions:
		"""Контейнер настроек обработчика."""

		return self._ProcessorOptions

	@property
	def printer(self) -> "Printer":
		"""Оператор вывода."""

		return self._SystemObjects.printer

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self._SystemObjects

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GetParser(self, parser: str) -> RequiredParser:
		"""
		Инициализирует требуемый парсер.

		:param parser: Имя парсера.
		:type parser: str
		:return: Коллекция управляющих объектов трубемого парсера.
		:rtype: RequiredParser
		"""

		EntryPoint = self.system_objects.driver.get_entry_point(parser)
		SourceOperator = EntryPoint.source_operator

		return RequiredParser(parser, EntryPoint, SourceOperator, SourceOperator.manifest, SourceOperator.settings)

	def _IsMultipleParsersRequired(self, data: ParsedCommandData) -> bool:
		"""
		Проверяет, разрешено ли команде выбирать несколько парсеров.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Возвращает `True`, если команде разрешено выбирать несколько парсеров.
		:rtype: bool
		"""

		try:
			data.get_position_parameter("PARSERS")
			return True

		except Exception:
			return False

	def _LoadRequiredParsers(self, required_parsers: tuple[str, ...]) -> tuple[RequiredParser, ...]:
		"""
		Загружает управляющие объекты затребованных парсеров.

		:param required_parsers: Последовательность имён парсеров.
		:type required_parsers: tuple[str, ...]
		:return: Последовательность управляющих объектов затребованных парсеров.
		:rtype: tuple[RequiredParser, ...]
		"""

		Parsers: list = []
		for Name in required_parsers: Parsers.append(self._GetParser(Name))

		return tuple(Parsers)

	def _CheckRequiredParsers(self, data: ParsedCommandData) -> tuple[str, ...]:
		"""
		Проверяет наличие требуемых парсеров в системе.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Последовательность имён затребованых парсеров.
		:rtype: tuple[str, ...]
		:raises ParserNotFound: Парсер не найден.
		:raises MultipleParsersDenienForCommand: Команде запрещено использование нескольких парсеров.
		"""
		
		ParsersNames: str | None = data.get_key_value("--use", expected_type = str)

		if not ParsersNames:
			return ()

		Parsers: tuple[str, ...] = tuple(Element.strip() for Element in ParsersNames.split(","))
		AllParsers: tuple[str, ...] = self._SystemObjects.driver.parsers_names
	
		if not Parsers:
				Parsers = AllParsers
		else:
			for CurrentParser in Parsers:
				if CurrentParser not in AllParsers:
					raise exceptions.system.ParserNotFound(CurrentParser)

		if not self._IsMultipleParsersRequired(data) and len(Parsers) > 1:
			raise exceptions.cli.MultipleParsersDenienForCommand(data.name)

		return tuple(Parsers)

	def _SetMirror(self, parsers: tuple[RequiredParser, ...], mirror: str):
		"""
		Задаёт зеркало для парсера. Необходимо затребовать конкретный парсер для применения.

		:param parsers: Последовательность имён парсеров (содержит только один конкретный парсер).
		:type parsers: tuple[RequiredParser, ...]
		:param mirror: Домен зеркала.
		:type mirror: str
		"""

		if len(parsers) > 1:
			self.printer.warning("Unable to set mirror in multiple parsers.")
			return

		if not parsers:
			self.printer.critical("Parsers not loaded, mirror can't be setted.")
			sys.exit(-1)
			return

		parsers[0].source_operator.set_mirror(mirror)

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ГЕНЕРАЦИИ КОМАНДЫ <<<<< #
	#==========================================================================================#

	def _AddForceModeFlag(self):
		"""Добавляет флаг переключения режима перезаписи."""

		self._Command.base.add_flag("-f", description = "Enable force mode.")

	def _AddMirrorKey(self):
		"""Добавляет ключ подключения зеркала."""

		self._Command.base.add_key("--mirror", type = ValidableTypes.Domain, description = "Source mirror to requests.")

	def _AddParserPositionForPXM(self):
		"""Добавляет позицию имени парсера, используюмую **pxm**."""

		ComPos = self._Command.create_position("PARSER", "Parser name.", important = True)
		ComPos.set_argument()

	def _AddParserUsePosition(self, multiple: bool = False):
		"""
		Добавляет позицию для имени парсера(ов).

		:param multiple: Указывает, должна ли позиция поддерживать множественное указание парсеров.
		:type multiple: bool
		"""

		if multiple:
			ComPos = self._Command.create_position("PARSERS", "One or more parsers names separated by comma. By default all.")
			ComPos.add_key("--use")

		else:
			ComPos = self._Command.create_position("PARSER", "Name of parser.", important = True)
			ComPos.add_key("--use")

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return ""

	def _ExportOptions(self) -> ProcessorOptions:
		"""
		Возвращает контейнер настроек обработчика.

		:return: Контейнер настроек обработчика.
		:rtype: ProcessorOptions
		"""

		return ProcessorOptions()

	@abstractmethod
	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		return command

	@abstractmethod
	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> _PARAMS:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedData
		:return: Структура **dataclass**.
		:rtype: AnyDataclass | DataclassStub
		"""

		pass

	@abstractmethod
	def _Process(self, parameters: _PARAMS):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: AnyDataclass
		"""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Базовый обработчик команды.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""

		self._SystemObjects: "SystemObjects" = system_objects

		self._Command: Command = Command(self.__class__.__module__.split(".")[-1].replace("_", "-"), self._ExportCommandDescription())
		self._GenerateCommand(self._Command)

		self._ProcessorOptions: ProcessorOptions = self._ExportOptions()

	def process(self, data: ParsedCommandData):
		"""
		Выполняет команду.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		"""

		Timer: utils.Timer | None = None
		if self.options.use_timer: Timer = utils.Timer(start = True)

		RequiredParsersNames: tuple[str, ...] = self._CheckRequiredParsers(data)
		RequiredParsers = self._LoadRequiredParsers(RequiredParsersNames)
		IsForceModeEnabled: bool = data.check_flag("-f")
		Mirror: str | None = data.get_key_value("--mirror", expected_type = str)

		if Mirror: self._SetMirror(RequiredParsers, Mirror)

		PreparedDataContainer = PreparedData(RequiredParsers, IsForceModeEnabled, Mirror)
		
		Parameters = self._ParseParameters(data, PreparedDataContainer)
		self._Process(Parameters)

		if Timer: self.printer.emit(f"Done in {Timer.ends()}.")
