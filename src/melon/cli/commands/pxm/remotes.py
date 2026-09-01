from typing import override

from prettytable import PLAIN_COLUMNS, PrettyTable

from dublib.cli.terminalyzer import Command, ParsedCommandData
from dublib.cli.text_styler import FastStyler

from ..base_processor import PreparedData, ProcessorOptions
from ..base_processor.structs import DataclassStub
from ._base import CommandProcessorTemplate

class CommandProcessor(CommandProcessorTemplate[DataclassStub]):
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

		return "Show list of repositories."

	@override
	def _ExportOptions(self) -> ProcessorOptions:
		"""
		Возвращает контейнер настроек обработчика.

		:return: Контейнер настроек обработчика.
		:rtype: ProcessorOptions
		"""

		return ProcessorOptions(use_timer = False)

	@override
	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		return command

	@override
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

	@override
	def _Process(self, parameters: DataclassStub) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: DataclassStub
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		InstalledParsers: list[str] = self.system_objects.manager.parsers.installed

		TableData: dict[str, list[str]] = {
			"PARSER": [],
			"REPOSITORY": []
		}
	
		for ParserName in self.system_objects.manager.repositories.availabel_parsers:
			RepositoryURL: str = self.system_objects.manager.repositories.get(ParserName, exception = True)
			Status = "✅" if ParserName in InstalledParsers else "❌"
			TableData["PARSER"].append(f"{Status} {ParserName}")
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