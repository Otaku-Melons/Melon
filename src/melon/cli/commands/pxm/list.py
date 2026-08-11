from dublib.cli.terminalyzer import Command, ParsedCommandData

from ....core.base.parsers.components.manifest import ContentTypes
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

		return "List installed parsers."

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

		TableData: dict[str, list[str]] = {
			"NAME": [],
			"VERSION": [],
			"TYPES": [],
			"DOMAIN": [],
			"collect": []
		}
	
		for ParserName in self._SystemObjects.driver.parsers_names:
			EntryPoint = self._SystemObjects.driver.get_entry_point(ParserName)
			TypesEmoji = {
				ContentTypes.Manga: "m",
				ContentTypes.Ranobe: "r"
			}
	
			ParserVersion = EntryPoint.version or ""
			ParserContentTypes: list[str] = [TypesEmoji[CurrentType] for CurrentType in EntryPoint.manifest.content_types]
			ParserSite: str = "https://" + EntryPoint.manifest.domain
	
			TableData["NAME"].append(ParserName)
			TableData["VERSION"].append(ParserVersion)
			TableData["TYPES"].append(", ".join(ParserContentTypes))
			TableData["DOMAIN"].append(ParserSite)
			TableData["collect"].append(str(EntryPoint.source_operator.is_collector_implemented))
	
		self.printer.templates.parsers_table(TableData)

		return True