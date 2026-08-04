from dataclasses import dataclass

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, ValidableTypes

from Source.Core.Base.Formats.Components.Enums import By
from Source.Core.Builders.RanobeBuilder import RanobeBuilder

from ..BaseProcessor import BaseCommandProcessor, PreparedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	filename: str
	parser_name: str
	branch_id: int | None

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

		return "Build read-ready ranobe content."

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

		command.base.add_key("--branch", type = ValidableTypes.UnsignedInteger, description = "Branch ID to building.")

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
		BranchID: int | None = data.get_key_value("--branch", expected_type = int)

		return Parameters(
			filename = Filename,
			parser_name = prepared_data.required_parsers_names[0],
			branch_id = BranchID
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		EntryPoint = self.system_objects.driver.get_entry_point(parameters.parser_name)
		SourceOperator = EntryPoint.source_operator
		TypingResult = EntryPoint.get_content_type_by_file(parameters.filename)
		Parser = SourceOperator.launch_parser(TypingResult.content_type)
		
		Title = Parser.init_empty_title(TypingResult.slug)
	
		if Title.load(parameters.filename, By.Filename):
			self.printer.emit(f"Loaded file: <i>{parameters.filename}</i>.")
		else:
			self.printer.error(f"Unable load file: <b>{parameters.filename}</b>.")
			exit(1)
	
		Builder = RanobeBuilder(Parser, Title)
		Builder.build(parameters.branch_id)