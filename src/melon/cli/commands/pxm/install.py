from dataclasses import dataclass

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ....parsers_manager import ConfigInstallationResult, ParsersManager
from ..base_processor import BaseCommandProcessor, PreparedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	parser: str

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

		self._AddParserPositionForPXM()
		
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

		return Parameters(parser = Parser)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		Installer = ParsersManager(self.system_objects)
		RepositoryURL: str | None = Installer.repositories.get(parameters.parser)

		if not RepositoryURL:
			self.printer.error(f"Repository for parser \"{parameters.parser}\" not found.")
			return

		self.printer.emit(f"Repository: <i>{RepositoryURL}</i>.")

		Installer.clone_parser(parameters.parser)
		self.printer.emit(f"Parser clonned.")

		RequirementsCount: int = Installer.install_requirements(parameters.parser)
		if RequirementsCount: self.printer.emit(f"Installed {RequirementsCount} requirements.")

		Result: ConfigInstallationResult = Installer.install_config(parameters.parser)
		
		match Result:
			case ConfigInstallationResult.Missing: self.printer.emit("Parser doesn't provide configuration.")
			case ConfigInstallationResult.Installed: self.printer.emit("Parser configuration installed.")
			case ConfigInstallationResult.AlreadyExists: self.printer.emit("Parser configuration already exists. Skipped.")
			case ConfigInstallationResult.Overwtitten: self.printer.emit("Parser configuration overwritten.")