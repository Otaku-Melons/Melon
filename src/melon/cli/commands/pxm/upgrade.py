from dublib.cli.terminalyzer import Command, ParsedCommandData

from ..base_processor import PreparedData
from ..base_processor.structs import DataclassStub
from ._base import CommandProcessorTemplate

class CommandProcessor(CommandProcessorTemplate[DataclassStub]):
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

	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> DataclassStub:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: PreparedData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedDatas
		:return: Структура **dataclass**.
		:rtype: DataclassStub
		"""

		return DataclassStub()

	def _Process(self, parameters: DataclassStub) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: DataclassStub
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		self.printer.emit(f"Repository: <i>{self.system_objects.options.REPOS_URL.value}</i>")
		self.system_objects.manager.upgrade()

		return True