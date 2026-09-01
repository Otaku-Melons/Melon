from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Sequence, override

from dublib.cli.terminalyzer import Command, ParsedCommandData
from dublib.functions.filesystem import clear_directory

from .... import utils
from ..base_processor import PreparedData
from ..base_processor.templates import T_SingleParserRequired
from ..melon._base import CommandProcessorTemplate

if TYPE_CHECKING:
	from ....core.base.structs.title import TitleDescriptor

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ClearingRules(Enum):
	"""Правила очистки."""

	All = "-all"
	Broken = "-broken"
	Collection = "--collection"
	NotFound = "-not-found"

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	rule: ClearingRules
	collection_file: str | None

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
		clear_directory(ParserSettings.directories.titles)
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

	def __ClearCollection(self, parameters: Parameters) -> bool:
		"""
		Реализует стратегию очистки: по алиасам из коллекции.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		SourceOperator = parameters.required_parser.source_operator
		Collector = utils.Collector(SourceOperator, parameters.collection_file)

		if not Collector.is_collection_file_exists:
			self.printer.error("Collection not found.")
			return False

		SlugsCount: int = Collector.load()
		Slugs = Collector.slugs
		self.printer.emit(f"Slugs in collection: {SlugsCount}.")
		if not Slugs: return True

		Filenames: list[str] = []

		if SourceOperator.settings.common.use_id_as_filename:
			for Slug in Slugs:
				ID: int | None = SourceOperator.shared_data.journal.get_id_by_slug(Slug)

				if ID is None:
					self.printer.warning(f"ID for \"{Slug}\" missing in cache. Skipped.")
					continue

				Filenames.append(f"{ID}.json")

		else: Filenames = [f"{Slug}.json" for Slug in Slugs]

		RemovedFilesCount: int = self.__RemoveFilesInDirectory(SourceOperator.settings.directories.titles, Filenames)
		if RemovedFilesCount: self.printer.emit(f"Removed {RemovedFilesCount} files.")
		
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

	@override
	def _ExportCommandDescription(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Clear local JSON files by rule."

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

		ComPos = command.create_position(name = "RULE", description = "Rule to clearing files.", important = True)
		ComPos.add_flag(ClearingRules.All.value, description = "Delete all files.")
		ComPos.add_flag(ClearingRules.Broken.value, description = "Delete broken JSON files.")
		ComPos.add_flag(ClearingRules.NotFound.value, description = "Delete files for titles that not found on server by slug.")
		ComPos.add_key(ClearingRules.Collection.value, description = "Delete files from collection.")

		self._AddMirrorKey()

		return command

	@override
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

		Parameter = data.get_important_position_named_parameter("RULE")
		Rule: ClearingRules = ClearingRules(Parameter.name)
		CollectionFile: str | None = None

		if Rule is ClearingRules.Collection: 
			CollectionFile = data.get_key_value(ClearingRules.Collection.value, expected_type = str)
		
		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			rule = Rule,
			collection_file = CollectionFile
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

		Result: bool = True

		match parameters.rule:
			case ClearingRules.All: Result = self.__ClearAll(parameters)
			case ClearingRules.Broken: Result = self.__ClearBroken(parameters)
			case ClearingRules.Collection: Result = self.__ClearCollection(parameters)
			case ClearingRules.NotFound: Result = self.__ClearNotFound(parameters)

		return Result