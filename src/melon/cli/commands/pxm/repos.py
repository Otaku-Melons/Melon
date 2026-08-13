from dataclasses import dataclass
from typing import cast

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from ....core import exceptions
from ....core.system_objects.parsers_manager import ParsersManager
from ..base_processor import PreparedData, ProcessorOptions
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	url: str | None
	parser_name: str | None
	is_remove: bool

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

		return "Parsers repositories management."

	def _ExportOptions(self) -> ProcessorOptions:
		"""
		Возвращает контейнер настроек обработчика.

		:return: Контейнер настроек обработчика.
		:rtype: ProcessorOptions
		"""

		return ProcessorOptions(use_timer = False)

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("OPERATION", "Operation with repositories.", important = True)
		ComPos.add_key("--add", type = ValidableTypes.URL, description = "URL of parser Git repository.")
		ComPos.add_key("--remove", description = "Parser name.")
		
		return command

	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> Parameters:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedDatas
		:return: Структура **dataclass**.
		:rtype: Parameters
		"""

		URL: str | None = data.get_key_value("--add", expected_type = str)
		ParserName: str | None = data.get_key_value("--remove", expected_type = str)
		IsRemove: bool = bool(ParserName)

		return Parameters(
			url = URL,
			parser_name = ParserName,
			is_remove = IsRemove
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Manager = ParsersManager(self.system_objects)

		try:
			if parameters.is_remove: Manager.repositories.remove(cast(str, parameters.parser_name))
			elif parameters.url: Manager.repositories.add(cast(str, parameters.url))

		except exceptions.system.ReposError as ExceptionData:
			self.printer.error(str(ExceptionData))
			return False

		return True