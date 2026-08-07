import sys
from dataclasses import dataclass

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from ....core.base.formats.components.enums import By
from ..base_processor import BaseCommandProcessor, PreparedData, T_SingleParserRequired

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	filename: str
	target_id: int
	is_target_chapter: bool

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

		return "Repair chapter chapter in local title."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("FILE", "Title filename with or without type.", important = True)
		ComPos.set_argument()

		ComPos = command.create_position("TARGET", "Target to repairing.", important = True)
		ComPos.add_key("--branch", type = ValidableTypes.UnsignedInteger, description = "Branch ID.")
		ComPos.add_key("--chapter", type = ValidableTypes.UnsignedInteger, description = "Chapter ID.")

		self._AddParserPosition()

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

		Filename: str = data.get_important_position_value("FILE", expected_type = str)
		TargetID: int = data.get_important_position_value("TARGET", expected_type = int)
		IsTargetChapter: bool = data.check_key("--chapter")

		if not Filename.endswith(".json"):
			Filename += ".json"

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			filename = Filename,
			target_id = TargetID,
			is_target_chapter = IsTargetChapter
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		if not parameters.is_target_chapter:
			self.printer.error("For now only chapters supported as target to repairing.")
			sys.exit(1)
	
		TypingResult = parameters.required_parser.entry_point.get_content_type_by_file(parameters.filename)
		Parser = parameters.required_parser.source_operator.launch_parser(TypingResult.content_type)
		Title = Parser.init_empty_title(TypingResult.slug)
	
		if Title.load(parameters.filename, By.Filename):
			self.printer.emit(f"Loaded file: <i>{parameters.filename}</i>.")
		else:
			self.printer.error(f"Unable load file: <b>{parameters.filename}</b>.")
			sys.exit(1)
	
		self.printer.emit(f"Repairing chapter <b>{parameters.target_id}</b>… ", end_line = False)
	
		if Parser.repair(parameters.target_id): self.printer.emit("Done.")
		else: self.printer.warning("Chapter is empty. Repairing failure?")
	
		if Parser.save(): self.printer.emit("Saved.")
		else: self.printer.emit("No changes. Saving skipped.")