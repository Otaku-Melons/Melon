from dataclasses import dataclass

from dulwich.porcelain import DivergedBranches

from dublib.cli.terminalyzer import Command, ParsedCommandData

from ....core.system_objects.parsers_manager import ParsersManager
from ..base_processor import PreparedData
from ..base_processor.parameters_templates import T_ForceModeRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired):
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

	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Upgrade Melon."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddForceModeFlag()
		
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

		return Parameters(
			is_force_mode_enabled = data.check_flag("-f")
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
		IsUpdated: bool = False

		try:
			IsUpdated = Installer.upgrade_melon(force_mode = parameters.is_force_mode_enabled)
		except DivergedBranches:
			self.printer.error("Melon has local unpushed commits or branches diverged.")
			return False

		if IsUpdated: self.printer.emit("Upgraded.")
		else: self.printer.emit("No changes.")

		return True