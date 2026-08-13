from prettytable import PLAIN_COLUMNS, PrettyTable

from dublib.cli.terminalyzer import Command, ParsedCommandData
from dublib.cli.text_styler import FastStyler

from ....core.system_objects.parsers_manager import ParsersManager
from ..base_processor import DataclassStub, PreparedData, ProcessorOptions
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

		return "Show list of repositories."

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

		return command

	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> DataclassStub:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedDatas
		:return: Структура **dataclass**.
		:rtype: Parameters
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

		Installer = ParsersManager(self.system_objects)

		TableData: dict[str, list[str]] = {
			"PARSER": [],
			"REPOSITORY": []
		}
	
		for ParserName in Installer.repositories.availabel_parsers:
			RepositoryURL: str = Installer.repositories.get(ParserName, exception = True)
			TableData["PARSER"].append(ParserName)
			TableData["REPOSITORY"].append(FastStyler(RepositoryURL).decorate.italic)

		TableObject = PrettyTable()
		TableObject.set_style(PLAIN_COLUMNS)

		for ColumnName in TableData.keys():
			Buffer = FastStyler(ColumnName).decorate.bold
			TableObject.add_column(Buffer, TableData[ColumnName])

		TableObject.align = "l"
		TableObject.sortby = FastStyler("PARSER").decorate.bold
		TableString = str(TableObject).strip()
		self.printer.emit(TableString)

		return True