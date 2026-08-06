from dataclasses import dataclass
from pathlib import Path

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, ValidableTypes

from ... import utils
from ...core.base.parsers.components.manifest import ContentTypes
from ..base_processor import BaseCommandProcessor, PreparedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	parser_name: str
	domain: str
	is_use_git: bool
	content_types: tuple[ContentTypes, ...]

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

		return "Create new parser to development."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("NAME", "Parser name.", important = True)
		ComPos.set_argument()

		ComPos = command.create_position("DOMAIN", "Source site domain.", important = True)
		ComPos.set_argument(ValidableTypes.Domain)

		ComPos = command.create_position("CONTENT_TYPES", "Types of content separated by comma: manga, ranobe.", important = True)
		ComPos.set_argument()

		command.base.add_flag("-git", description = "Initialize Git repository.")

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

		ParserName: str = data.get_important_position_value("NAME", expected_type = str)
		Domain: str = data.get_important_position_value("DOMAIN", expected_type = str)
		UseGit: bool = data.check_flag("-git")
		ContentTypesString: str = data.get_important_position_value("CONTENT_TYPES", expected_type = str)
		ContentTypesValues = utils.DevelopmeptAssistant.parse_content_types(ContentTypesString)

		return Parameters(
			parser_name = ParserName,
			domain = Domain,
			is_use_git = UseGit,
			content_types = ContentTypesValues
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		Developer = utils.DevelopmeptAssistant(self.system_objects)
		Developer.create_parser(parameters.parser_name, parameters.domain, parameters.content_types, parameters.is_use_git)
