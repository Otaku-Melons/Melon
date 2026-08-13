from dataclasses import dataclass

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ....core import exceptions
from ....core.system_objects.parsers_manager import ParsersManager
from ..base_processor import PreparedData
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	parser: str
	is_clear: bool

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

		return "Uninstall parser."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddParserPosition()

		command.base.add_key("-c", description = "Clear temp directory and delete config.")
		
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

		Parser: str = data.get_important_position_value("PARSER", expected_type = str)
		IsClear: bool = data.check_flag("-c")

		return Parameters(
			parser = Parser,
			is_clear = IsClear
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Installer = ParsersManager(self.system_objects)
		
		try:
			Installer.uninstall_parser(parameters.parser, parameters.is_clear)
			if parameters.is_clear: self.printer.emit("Temp files and config cleared.")
		except exceptions.system.ParserNotFound:
			self.printer.error(f"Parser <b>{parameters.parser}</b> not found.")
			return False

		return True