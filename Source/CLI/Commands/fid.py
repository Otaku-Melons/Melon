from dataclasses import dataclass

from dublib.CLI.Terminalyzer import Command, ParsedCommandData

from ..BaseProcessor import BaseCommandProcessor, PreparedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	slug: str
	parsers: tuple[str, ...]
	is_search_all: bool

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

		return "Find title ID by slug in cache."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""
		
		ComPos = command.create_position("SLUG", "Title slug.")
		ComPos.set_argument()

		self._AddParserPosition(multiple = True)

		command.base.add_flag("-all", description = "Print all search results instead only first.")

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

		Slug: str = data.get_important_position_value("SLUG", expected_type = str)
		SearchAll: bool = data.check_flag("-all")

		return Parameters(
			slug = Slug,
			parsers = prepared_data.required_parsers_names,
			is_search_all = SearchAll
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		ResultsCount: int = 0
	
		for CurrentParser in parameters.parsers:
			EntryPoint = self.system_objects.driver.get_entry_point(CurrentParser)
			ID = EntryPoint.shared_data.journal.get_id_by_slug(parameters.slug)
	
			if ID:
				ResultsCount += 1
				self.printer.emit(f"Found ID {ID} for parser \"{CurrentParser}\".")
	
				if not parameters.is_search_all:
					break
	
		if ResultsCount:
			self.printer.emit(f"Total ID found in cache: {ResultsCount}.")
		else:
			self.printer.emit("Tite with same slug not found in cache.")