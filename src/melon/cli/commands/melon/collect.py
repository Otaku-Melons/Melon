from dataclasses import dataclass

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.cli.text_styler import GetStyledTextFromHTML

from .... import utils
from ..base_processor import PreparedData, T_ForceModeRequired, T_SingleParserRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired, T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	file: str | None

	is_collect_local: bool
	is_sorting_enabled: bool

	period: int | None
	filters: str | None
	pages: int | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

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

		ComPos = command.create_position(
			name = "FILE",
			description = GetStyledTextFromHTML("Collection filename without filetype. By default <i>collection</i>.")
		)
		ComPos.add_key("--file")

		self._AddForceModeFlag()

		command.base.add_flag("-local", description = "Scan local titles and put into collection.")
		command.base.add_flag("-no-sort", description = "Disable slugs sorting.")

		self._AddMirrorKey()

		command.base.add_key("--filters", description = "Query string for filtering titles.")
		command.base.add_key("--pages", type = ValidableTypes.UnsignedInteger, description = "Count of pages to collecting.")
		command.base.add_key("--period", type = ValidableTypes.UnsignedInteger, description = "Period in hours for parsing updates.")

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

		CollectLocal: bool = data.check_flag("-local")
		IsSortingEnabled: bool = not data.check_flag("-no-sort")
	
		Period: int | None = data.get_key_value("--period", expected_type = int)
		Filters: str | None = data.get_key_value("--filters", expected_type = str)
		Pages: int | None = data.get_key_value("--pages", expected_type = int)

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			file = File,
			is_collect_local = CollectLocal,
			is_sorting_enabled = IsSortingEnabled,
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

		if not parameters.is_force_mode_enabled:
			Collector.load()

		AddedSlugs: int = 0
	
		if parameters.is_collect_local:
			self.printer.emit("Scanning local titles… ", end_line = False)
			AddedSlugs = len(Collector.scan_local())
			self.printer.emit("Done.", end_line = False)
		elif parameters.required_parser.source_operator.is_collector_implemented:
			CollectedSlugs = parameters.required_parser.source_operator.collect_slugs(parameters.period, parameters.filters, parameters.pages)
			AddedSlugs = Collector.add(CollectedSlugs)
		else:
			self.printer.critical("Collector method not implemented.")
			return False
	
		Collector.save(sort = parameters.is_sorting_enabled)
	
		if AddedSlugs:
			self.printer.emit(f"Slugs collected: {AddedSlugs}.")
		else:
			self.printer.emit("No new slugs in collection.")

		return True