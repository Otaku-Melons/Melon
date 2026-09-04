from dataclasses import dataclass
from typing import override

import orjson

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ..base_processor import PreparedData
from ..base_processor.templates import T_SingleParserRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	slug: str
	is_json_output: bool

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __PrintResult(self, parameters: Parameters, title_id: int | None):
		"""
		Выводит результат поиска ID.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:param title_id: Результат поиска.
		:type title_id: int | None
		"""

		if parameters.is_json_output:
			OutputDictionary: dict[str, int | str | None] = {
				"parser": parameters.required_parser.name,
				"slug": parameters.slug,
				"id": title_id
			}
			self.printer.emit(orjson.dumps(OutputDictionary).decode())

		else:
			if title_id:
				self.printer.emit(f"Found ID {title_id} for parser \"{parameters.required_parser.name}\".")
			else:
				self.printer.emit(f"ID not foind in \"{parameters.required_parser.name}\" cache.")

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

		return "Find title ID by slug in cache."

	@override
	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""
		
		ComPos = command.create_position("SLUG", "Title slug.", important = True)
		ComPos.set_argument()

		self._AddParserPosition(key = "--use")

		command.base.add_flag("-j", description = "Print result in JSON format.")

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
			slug = data.get_important_position_value("SLUG", expected_type = str),
			is_json_output = data.check_flag("-j")
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

		ID = parameters.required_parser.source_operator.shared_data.journal.get_id_by_slug(parameters.slug)
		self.__PrintResult(parameters, ID)

		return False if parameters.is_json_output else True