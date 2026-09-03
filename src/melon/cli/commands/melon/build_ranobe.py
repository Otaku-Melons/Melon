from dataclasses import dataclass
from typing import override

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from ....builders.ranobe import RanobeBuilder
from ....core import exceptions
from ....core.base.formats.base_format.enums import By
from ..base_processor import PreparedData
from ..base_processor.templates import T_SingleParserRequired
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	filename: str
	branch_id: int | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
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

		return "Build read-ready ranobe content."

	@override
	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("FILE", "Filename of local JSON.", important = True)
		ComPos.set_argument()

		self._AddParserPosition()

		command.base.add_key("--branch", value_type = ValidableTypes.UnsignedInteger, description = "Branch ID to building.")

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

		Filename: str = data.get_important_position_value("FILE", expected_type = str)
		BranchID: int | None = data.get_key_value("--branch", expected_type = int)

		return Parameters(
			filename = Filename,
			required_parser = prepared_data.required_parsers[0],
			branch_id = BranchID
		)

	@override
	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		:raises BuildingError: Алиас тайтла не определён.
		"""

		TypingResult = parameters.required_parser.source_operator.get_content_type_by_file(parameters.filename)

		if not TypingResult.slug:
			raise exceptions.builders.BuildingError("Undefined title slug.")

		Parser = parameters.required_parser.source_operator.launch_parser(TypingResult.content_type)
		
		Title = Parser.init_empty_title(TypingResult.slug)
	
		if Title.load(parameters.filename, By.Filename):
			self.printer.emit(f"Loaded file: <i>{parameters.filename}</i>.")
		else:
			self.printer.error(f"Unable load file: <b>{parameters.filename}</b>.")
			return False
	
		Builder = RanobeBuilder(Parser, Title)
		Builder.build(parameters.branch_id)

		return True