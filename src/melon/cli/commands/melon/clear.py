from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from dublib.cli.terminalyzer import Command, ParsedCommandData
from dublib.functions.filesystem import RemoveDirectoryContent

from .... import utils
from ..base_processor import PreparedData
from ..base_processor.parameters_templates import T_SingleParserRequired
from ._base import CommandProcessorTemplate

if TYPE_CHECKING:
	from ....core.structs import TitleDescriptor

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ClearingRules(Enum):
	"""Правила очистки."""

	All = "-all"
	Broken = "-broken"
	NotFound = "-not-found"

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	rule: ClearingRules

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Callback_NotFound(self, descriptor: "TitleDescriptor"):
		"""
		Callback-метод: вывод результата проверки существования тайтла.

		:param descriptor: Дескриптор тайтла.
		:type descriptor: TitleDescriptor
		"""

		IsTitleExists: bool | None = descriptor.extra.get("is_title_exists")
		
		if IsTitleExists is False:
			self.printer.emit(f"Title <i>{descriptor.full_filename}</i> marked to remove.")

	def __RemoveFilesInDirectory(self, directory: Path, files: Sequence[str]) -> int:
		"""
		Удаляет файлы из директории по списку.

		:param directory: Путь к директории.
		:type directory: Path
		:param files: Список имён файлов.
		:type files: list[str]
		:return: Количество удалённых файлов.
		:rtype: int
		"""

		FilesRemoved: int = 0

		for File in files:
			FilePath = directory / File

			if FilePath.exists() and FilePath.is_file():
				FilePath.unlink()
				FilesRemoved += 1
		
		return FilesRemoved

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ РЕАЛИЗАЦИИ ПРАВИЛ <<<<< #
	#==========================================================================================#

	def __ClearAll(self, parameters: Parameters) -> bool:
		"""
		Реализует стратегию очистки: удалить всё.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		ParserSettings = parameters.required_parser.settings
		RemoveDirectoryContent(ParserSettings.directories.titles)
		self.printer.emit("All files removed.")

		return True

	def __ClearBroken(self, parameters: Parameters) -> bool:
		"""
		Реализует стратегию очистки: повреждённый файлы.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		SourceOperator = parameters.required_parser.source_operator
		Collector = utils.Collector(SourceOperator)
		self.printer.emit("Search broken files…", flush = True)

		Result = Collector.collect_broken()
		FilesToRemove: tuple[str, ...] = tuple(Descriptor.full_filename for Descriptor in Result.descriptors if Descriptor.full_filename)
		RemovedFilesCount: int = self.__RemoveFilesInDirectory(SourceOperator.settings.directories.titles, FilesToRemove)

		if RemovedFilesCount: self.printer.emit(f"Removed {RemovedFilesCount} files.")
		else: self.printer.emit("No broken files found.")
		
		return True

	def __ClearNotFound(self, parameters: Parameters) -> bool:
		"""
		Реализует стратегию очистки: файлы, описывающие тайтлы, не найденные по алиасу на сервере.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""
		
		SourceOperator = parameters.required_parser.source_operator
		Collector = utils.Collector(SourceOperator)
		self.printer.emit("Check titles existing…", flush = True)

		Result = Collector.collect_not_found(callback = self.__Callback_NotFound)
		FilesToRemove: tuple[str, ...] = tuple(Descriptor.full_filename for Descriptor in Result.descriptors if Descriptor.full_filename)
		RemovedFilesCount: int = self.__RemoveFilesInDirectory(SourceOperator.settings.directories.titles, FilesToRemove)

		if RemovedFilesCount: self.printer.emit(f"Removed {RemovedFilesCount} files.")
		else: self.printer.emit("No files to remove.")

		return True

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Clear local JSON files by rule."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		self._AddParserPosition()

		ComPos = command.create_position(name = "RULE", description = "Rule to clearing files.", important = True)
		ComPos.add_flag(ClearingRules.All.value, description = "Delete all files.")
		ComPos.add_flag(ClearingRules.Broken.value, description = "Delete broken JSON files.")
		ComPos.add_flag(ClearingRules.NotFound.value, description = "Delete files for titles that not found on server by slug.")

		self._AddMirrorKey()

		return command

	def _ParseParameters(self, data: ParsedCommandData, prepared_data: PreparedData) -> Parameters:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:param prepared_data: Предподготолвенные данные.
		:type prepared_data: PreparedData
		:return: Структура **dataclass**.
		:rtype: Parameters
		"""

		Rule: ClearingRules = ClearingRules(data.get_important_position_value("RULE", expected_type = str))

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			rule = Rule
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Result: bool = True

		match parameters.rule:
			case ClearingRules.All: Result = self.__ClearAll(parameters)
			case ClearingRules.Broken: Result = self.__ClearBroken(parameters)
			case ClearingRules.NotFound: Result = self.__ClearNotFound(parameters)

		return Result