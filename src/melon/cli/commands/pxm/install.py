from dataclasses import dataclass

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ....core.system_objects.parsers_manager import (
	ConfigInstallationResult,
	ConfigInstallationStrategies,
	ParsersManager,
)
from ..base_processor import PreparedData
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	parser: str
	config_strategy: ConfigInstallationStrategies

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

		return "Install parser."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddParserPosition()
		self._AddConfigConflictStrategyPosition()
		
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
		Strategy: str | None = data.get_position_value("STRATEGY", expected_type = str)
		if not Strategy: Strategy = "-s"

		return Parameters(
			parser = Parser,
			config_strategy = ConfigInstallationStrategies(Strategy)
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
		RepositoryURL: str | None = Installer.repositories.get(parameters.parser)

		if not RepositoryURL:
			self.printer.error(f"Repository for parser \"{parameters.parser}\" not found.")
			return False

		self.printer.emit(f"Repository: <i>{RepositoryURL}</i>.")

		Installer.clone_parser(parameters.parser)
		self.printer.emit("Parser clonned.")

		Installer.install_requirements(parameters.parser)

		Result: ConfigInstallationResult = Installer.install_config(parameters.parser, parameters.config_strategy)
		self.printer.templates.config_installation_result(Result)

		return True