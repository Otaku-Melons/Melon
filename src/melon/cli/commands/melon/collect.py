from dataclasses import dataclass
from enum import Enum

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.cli.text_styler import GetStyledTextFromHTML

from .... import utils
from ..base_processor import PreparedData
from ..base_processor.parameters_templates import (
	T_ForceModeRequired,
	T_SingleParserRequired,
)
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class CollectingTargets(Enum):
	"""Альтернативный цели для сборки коллекции."""

	FromServer = None
	Local = "-local"
	NotFound = "-not-found"

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired, T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	file: str | None
	collecting_target: CollectingTargets

	period: int | None
	filters: str | None
	pages: int | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CollectFromServer(self, collector: utils.Collector, parameters: Parameters) -> int:
		"""
		Собирает алиасы тайтлов: с сервера источника по заданным параметрам.

		:param collector: Сборщик алиасов.
		:type collector: utils.Collector
		:param parameters: Параметры, требуемые обработчиком.
		:type parameters: Parameters
		:return: Количество уникальных добавленных в коллекцию тайтлов.
		:rtype: int
		"""

		CollectedSlugs = parameters.required_parser.source_operator.collect_slugs(parameters.period, parameters.filters, parameters.pages)

		return collector.add(CollectedSlugs)

	def __CollectLocal(self, collector: utils.Collector, parameters: Parameters) -> int:
		"""
		Собирает алиасы тайтлов: локальные файлы.

		:param collector: Сборщик алиасов.
		:type collector: utils.Collector
		:param parameters: Параметры, требуемые обработчиком.
		:type parameters: Parameters
		:return: Количество уникальных добавленных в коллекцию тайтлов.
		:rtype: int
		"""

		self.printer.templates.local_titles_scanning_start()

		return collector.collect_local().added

	def __CollectNotFound(self, collector: utils.Collector, parameters: Parameters) -> int:
		"""
		Собирает алиасы тайтлов: не найденные на сервере источника тайтлы.

		:param collector: Сборщик алиасов.
		:type collector: utils.Collector
		:param parameters: Параметры, требуемые обработчиком.
		:type parameters: Parameters
		:return: Количество уникальных добавленных в коллекцию тайтлов.
		:rtype: int
		"""

		self.printer.emit("Checking titles existing…", flush = True)

		return collector.collect_not_found().added

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Collect titles slugs into file in parser's temporary directory."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddParserPosition()

		ComPos = command.create_position("TARGETS", "Alternative targets to collecting.")
		ComPos.add_flag(CollectingTargets.Local.value, description = "Scan local titles and put slugs into collection.")
		ComPos.add_flag(CollectingTargets.NotFound.value, description = "Check titles existing on server and collect not found slugs.")

		ComPos = command.create_position(
			name = "FILE",
			description = GetStyledTextFromHTML("Collection filename without filetype. By default <i>collection</i>.")
		)
		ComPos.add_key("--file")

		self._AddForceModeFlag()

		self._AddMirrorKey()

		command.base.add_key("--filters", description = "Query string for filtering titles.")
		command.base.add_key("--pages", value_type = ValidableTypes.UnsignedInteger, description = "Count of pages to collecting.")
		command.base.add_key("--period", value_type = ValidableTypes.UnsignedInteger, description = "Period in hours for parsing updates.")

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

		File: str | None = data.get_position_value("FILE", expected_type = str)

		CollectingTarget: str | None = data.get_position_value("TARGETS", expected_type = str)
	
		Period: int | None = data.get_key_value("--period", expected_type = int)
		Filters: str | None = data.get_key_value("--filters", expected_type = str)
		Pages: int | None = data.get_key_value("--pages", expected_type = int)

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			file = File,
			collecting_target = CollectingTargets(CollectingTarget),
			period = Period,
			filters = Filters,
			pages = Pages
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""
		
		Collector = utils.Collector(parameters.required_parser.source_operator, parameters.file)
		if not parameters.is_force_mode_enabled: Collector.load()
		AddedSlugs: int = 0

		match parameters.collecting_target:

			case CollectingTargets.FromServer:

				if not parameters.required_parser.source_operator.is_collector_implemented:
					self.printer.critical("Collector method not implemented.")
					return False

				AddedSlugs = self.__CollectFromServer(Collector, parameters)

			case CollectingTargets.Local: AddedSlugs = self.__CollectLocal(Collector, parameters)
			case CollectingTargets.NotFound: AddedSlugs = self.__CollectNotFound(Collector, parameters)

		Collector.save()
	
		if AddedSlugs: self.printer.emit(f"Unique slugs added: {AddedSlugs}.")
		else: self.printer.emit("No new slugs in collection.")

		return True