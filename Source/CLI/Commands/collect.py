from dataclasses import dataclass

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.CLI.TextStyler import GetStyledTextFromHTML

from Source import Utils

from ..BaseProcessor import BaseCommandProcessor, PreparedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	parser: str

	is_force_mode_enabled: bool
	is_collect_local: bool
	is_sorting_enabled: bool

	period: int | None
	filters: str | None
	pages: int | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(BaseCommandProcessor[Parameters]):
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

		return GetStyledTextFromHTML("Collect titles slugs into <i>Collection.txt</i> file in parser's temporary directory.")

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddParserPosition()
		self._AddForceModeFlag()

		command.base.add_flag("-local", description = "Scan local titles and put into collection.")
		command.base.add_flag("-no-sort", description = "Disable slugs sorting.")

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

		CollectLocal: bool = data.check_flag("-local")
		IsSortingEnabled: bool = not data.check_flag("-no-sort")
	
		Period: int | None = data.get_key_value("--period", expected_type = int)
		Filters: str | None = data.get_key_value("--filters", expected_type = str)
		Pages: int | None = data.get_key_value("--pages", expected_type = int)

		return Parameters(
			parser = prepared_data.required_parsers_names[0],
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			is_collect_local = CollectLocal,
			is_sorting_enabled = IsSortingEnabled,
			period = Period,
			filters = Filters,
			pages = Pages
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		EntryPoint = self.system_objects.driver.get_entry_point(parameters.parser)
		Collector = Utils.Collector(EntryPoint)

		if not parameters.is_force_mode_enabled:
			Collector.load()

		AddedSlugs: int = 0
	
		if parameters.is_collect_local:
			AddedSlugs = Collector.scan_local()
		elif EntryPoint.source_operator.is_collector_implemented:
			CollectedSlugs = EntryPoint.source_operator.collect_slugs(parameters.period, parameters.filters, parameters.pages)
			AddedSlugs = Collector.add(CollectedSlugs)
		else:
			self.printer.critical("Collector method not implemented.")
			return
	
		Collector.save(sort = parameters.is_sorting_enabled)
	
		if AddedSlugs:
			self.printer.emit(f"Slugs collected: {AddedSlugs}.")
		else:
			self.printer.emit("No new slugs in collection.")