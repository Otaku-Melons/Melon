from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from dublib.cli.terminalyzer import Command, ParsedCommandData
from dublib.functions.filesystem import RemoveDirectoryContent

from .... import utils
from ..base_processor import PreparedData, T_SingleParserRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ClearingRules(Enum):
	"""Правила очистки."""

	All = "-all"
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

	def __RemoveFilesInDirectory(self, directory: Path, files: list[str]) -> int:
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
		ComPos.add_flag(ClearingRules.NotFound.value, description = "Clear titles, that not found on server.")

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

		SourceOperator = parameters.required_parser.source_operator
		ParserSettings = parameters.required_parser.settings
		ProgressIndicator = SourceOperator.portals.printer.progress_indicator

		match parameters.rule:

			case ClearingRules.All:
				RemoveDirectoryContent(ParserSettings.directories.titles)
				self.printer.emit("All files removed.")

			case ClearingRules.NotFound:
				Collector = utils.Collector(SourceOperator)
				self.printer.emit("Scanning local titles… ", end_line = False)
				LocalTitles: dict[str, str] = Collector.scan_local()
				self.printer.emit("Done.", end_line = False)
				SlugsCount: int = len(LocalTitles)
				self.printer.emit(f"Local titles found: {SlugsCount}.")
				
				SlugIndex: int = 0
				FilesToRemove: list[str] = []
				Progress: float = 0.0

				for Slug in Collector.slugs:
					Progress = SlugIndex + 1 / SlugsCount
					ProgressIndicator.set_progress(Progress)

					IsTitleExists: bool | None = SourceOperator.is_title_exists(Slug)

					if IsTitleExists is None:
						if SlugIndex: self.printer.error("Error occurred during the existence checking.")
						else: self.printer.error("Parser doesn't provide existence checker method.")
						return False

					if IsTitleExists is False:
						File = LocalTitles[Slug]
						self.printer.emit(f"File <i>{File}</i> marked for removing.")
						FilesToRemove.append(File)

					SlugIndex += 1
					if SlugIndex != SlugsCount: ParserSettings.common.sleep_delay()

				ProgressIndicator.end()
				FilesRemoved: int = self.__RemoveFilesInDirectory(ParserSettings.directories.titles, FilesToRemove)
				self.printer.emit(f"Files removed: {FilesRemoved}.")

		return True