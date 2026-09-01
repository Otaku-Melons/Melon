from dataclasses import dataclass
from typing import override

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ....core.system_objects.manager.parsers import ExportStrategies
from ..base_processor import PreparedData
from ..base_processor.templates import T_SingleParserRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	config_strategy: ExportStrategies

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

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

		return "Export and merge parser config."

	@override
	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddParserPosition()
		self._AddSettingsExportStrategyPosition()
		
		return command

	@override
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

		Strategy: str | None = data.get_position_value("STRATEGY", expected_type = str)
		if not Strategy: Strategy = "-s"

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			config_strategy = ExportStrategies(Strategy)
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

		Result = parameters.required_parser.parser_operator.export_settings(parameters.config_strategy)
		self.printer.templates.manager.exported(Result)
		
		return True