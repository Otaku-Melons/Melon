from dataclasses import dataclass
from typing import override

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ..base_processor import PreparedData
from ..base_processor.templates import (
	T_ForceModeRequired,
	T_SingleParserRequired,
)
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired, T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	pass

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

		return "Update parser."

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
		self._AddForceModeFlag()
		
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

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			is_force_mode_enabled = data.check_flag("-f")
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

		RepositoryURL: str = self.system_objects.manager.repositories.get(parameters.required_parser.name, exception = True)
		self.printer.emit(f"Repository: <i>{RepositoryURL}</i>.")
		
		IsUpdated: bool = parameters.required_parser.parser_operator.update(force_mode = parameters.is_force_mode_enabled)

		if IsUpdated: self.printer.emit("Updated.")
		else: self.printer.emit("No changes.")

		return True