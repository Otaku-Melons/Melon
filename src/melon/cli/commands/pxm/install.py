from dataclasses import dataclass
from typing import cast

from dublib.cli.templates.bus import PrintError
from dublib.cli.terminalyzer import Command, ParsedCommandData
from dublib.validators import Validator_URL

from ....core import exceptions
from ....parsers_manager import ParsersManager
from ..base_processor import (
	BaseCommandProcessor,
	PreparedData,
	ProcessorOptions,
)

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	target: str

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

		return "Install parser."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("TARGET", "URL of Git repository or parser name if exists.", important = True)
		ComPos.set_argument()
		
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

		Target: str = data.get_important_position_value("TARGET", expected_type = str)

		return Parameters(target = Target)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: DataclassStub
		"""

		Installer = ParsersManager(self.system_objects)

		if Validator_URL.validate(parameters.target):
			Installer.install_by_url(parameters.target)
		else:
			Installer.install_by_name(parameters.target)