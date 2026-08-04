from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Protocol, TypeVar

from dublib.CLI.Terminalyzer import Command, ParsedCommandData

from Source import Utils
from Source.Core import Exceptions

if TYPE_CHECKING:
	from Source.Core.SystemObjects import Printer, SystemObjects

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
class PreparedData:
	"""Предподготолвенные данные."""

	required_parsers_names: tuple[str, ...]
	is_force_mode_enabled: bool

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
					raise Exceptions.System.ParserNotFound(CurrentParser)

		if not self._IsMultipleParsersRequired(data) and len(Parsers) > 1:
			raise Exceptions.CLI.MultipleParsersDenienForCommand(data.name)

		return tuple(Parsers)

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ГЕНЕРАЦИИ КОМАНДЫ <<<<< #
	#==========================================================================================#

	def _AddForceModeFlag(self):
		"""Добавляет флаг переключения режима перезаписи."""

		self._Command.base.add_flag("-f", description = "Enable force mode.")

	def _AddParserPosition(self, multiple: bool = False):
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

		self._Command: Command = Command(self.__class__.__module__.split(".")[-1], self._ExportCommandDescription())
		self._GenerateCommand(self._Command)

		self._ProcessorOptions: ProcessorOptions = self._ExportOptions()

	def process(self, data: ParsedCommandData):
		"""
		Выполняет команду.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		"""

		Timer: Utils.Timer | None = None
		if self.options.use_timer: Timer = Utils.Timer(start = True)

		RequiredParsersNames: tuple[str, ...] = self._CheckRequiredParsers(data)
		IsForceModeEnabled: bool = data.check_key("-f")
		PreparedDataContainer = PreparedData(RequiredParsersNames, IsForceModeEnabled)
		
		Parameters = self._ParseParameters(data, PreparedDataContainer)
		self._Process(Parameters)

		if Timer: self.printer.emit(f"Done in {Timer.ends()}.")
