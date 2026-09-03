import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Protocol, Sequence, TypeVar

from dublib.cli.terminalyzer import Command, ParsedCommandData

from .... import utils
from ....core import exceptions
from .structs import PreparedData, ProcessorOptions, RequiredParser

if TYPE_CHECKING:
	from ....core.system_objects import SystemObjects
	from ....core.system_objects.printer import Printer
	
#==========================================================================================#
# >>>>> КОНСТРУКЦИИ АННОТАЦИЙ ТИПОВ <<<<< #
#==========================================================================================#

class AnyDataclass(Protocol):
	"""Протокол типизации: любой объект **dataclass**."""
	
	__dataclass_fields__: ClassVar[dict[str, Any]]

PARAMS = TypeVar("PARAMS", bound = AnyDataclass)

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseCommandProcessor(ABC, Generic[PARAMS]):
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

	def _CheckRequiredParsers(self, parsers_names: Sequence[str]):
		"""
		Проверяет наличие требуемых парсеров в системе.

		:param parsers_names: Последовательность имён парсеров.
		:type parsers_names: Sequence[str]
		:raises ParserNotFound: Парсер не найден.
		:raises MultipleParsersDenienForCommand: Команде запрещено использование нескольких парсеров.
		"""

		if not parsers_names:
			return ()

		AllParsers = self._SystemObjects.manager.parsers.installed

		for CurrentParser in parsers_names:
			if CurrentParser not in AllParsers:
				raise exceptions.parsers.ParserNotFound(CurrentParser)

	def _GetRequiredParsers(self, data: ParsedCommandData) -> tuple[RequiredParser, ...]:
		"""
		Загружает последовательность управляющих структур затребованных парсеров.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Последовательность управляющих структур затребованных парсеров.
		:rtype: tuple[RequiredParser, ...]
		:raises exceptions.cli.MultipleParsersDenienForCommand: Запрашивание нескольких парсеров запрещено.
		"""

		ParsersQuery: str | None = self._GetParsersQuery(data)

		if not ParsersQuery:
			return ()

		RequiredParsersNames: Sequence[str] = tuple(Element.strip() for Element in ParsersQuery.split(","))

		if not RequiredParsersNames:
			if self.system_objects.options.DEBUG:
				self.printer.debug("Parsers not selected. All will be loaded.")

			RequiredParsersNames = self._SystemObjects.manager.parsers.installed

		if not self.options.allow_multiple_parsers and len(RequiredParsersNames) > 1:
			raise exceptions.cli.MultipleParsersDenienForCommand(data.name)

		self._CheckRequiredParsers(RequiredParsersNames)

		return tuple(self._GetParser(Name) for Name in RequiredParsersNames)

	def _GetParser(self, parser: str) -> RequiredParser:
		"""
		Инициализирует требуемый парсер.

		:param parser: Имя парсера.
		:type parser: str
		:return: Коллекция управляющих объектов трубемого парсера.
		:rtype: RequiredParser
		"""

		ParserOperator = self.system_objects.manager.parsers.get_operator(parser)
		SourceOperator = ParserOperator.launch()

		return RequiredParser(parser, ParserOperator, SourceOperator, SourceOperator.manifest, SourceOperator.settings)

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

	def _AddParserPosition(self):
		"""Добавляет позицию для имени парсера(ов): `PARSER` или `PARSERS` в зависимости от параметров обработчика."""

		if self.options.allow_multiple_parsers:
			ComPos = self._Command.create_position("PARSERS", "One or more parsers names separated by comma. By default all.")
			ComPos.add_key("--use")

		else:
			ComPos = self._Command.create_position("PARSER", "Parser name.", important = True)
			ComPos.add_key("--use")

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GetParsersQuery(self, data: ParsedCommandData) -> str | None:
		"""
		Возвращает строку, представляющую последовательность имён затребованных парсеров, разделённых запятой.

		По умолчанию берёт данные из позиций `PARSER` или `PARSERS`.
		
		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Строка с именами парсеров или `None`, если не требуются.
		:rtype: str | None
		"""

		PositionName: str = "PARSERS" if self.options.allow_multiple_parsers else "PARSER"

		try:
			return data.get_position_value(PositionName, expected_type = str)

		except KeyError:
			return None

	def _ProcessAndCatchExceptions(self, parameters: PARAMS) -> bool:
		"""
		Оборачивает метод `_Process()` для отлова исключений.
		
		:param parameters: Параметры команды.
		:type parameters: AnyDataclass
		:return: Возвращает `True`, если выполнение успешно и прерывание не требуется.
		:rtype: bool
		"""

		try:
			return self._Process(parameters)

		except exceptions.parsers.ParserAlreadyExists as ExceptionData:
			self.printer.error(f"Parser <b>{ExceptionData}</b> already exists.")
			
		except exceptions.parsers.ParserNotFound as ExceptionData:
			self.printer.error(f"Parser <b>{ExceptionData}</b> not found.")

		except exceptions.parsers.RepositoryError as ExceptionData:
			self.printer.error(str(ExceptionData))

		return False

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
	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> PARAMS:
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
	def _Process(self, parameters: PARAMS) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: AnyDataclass
		:return: Возвращает `True`, если выполнение успешно и прерывание не требуется.
		:rtype: bool
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

		self._ProcessorOptions: ProcessorOptions = self._ExportOptions()

		self._Command: Command = Command(self.__class__.__module__.split(".")[-1].replace("_", "-"), self._ExportCommandDescription())
		self._GenerateCommand(self._Command)

	def process(self, data: ParsedCommandData):
		"""
		Выполняет команду.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		"""

		Timer: utils.Timer | None = utils.Timer(start = True) if self.options.use_timer else None

		RequiredParsers: tuple[RequiredParser, ...] = self._GetRequiredParsers(data)
		IsForceModeEnabled: bool = data.check_flag("-f")
		Mirror: str | None = data.get_key_value("--mirror", expected_type = str)

		if Mirror: self._SetMirror(RequiredParsers, Mirror)

		PreparedDataContainer = PreparedData(RequiredParsers, IsForceModeEnabled, Mirror)
		
		Parameters = self._ParseParameters(data, PreparedDataContainer)
		Status: bool = self._ProcessAndCatchExceptions(Parameters)

		if not Status: sys.exit(1)
		if Timer: self.printer.emit(f"Done in {Timer.ends()}.")
