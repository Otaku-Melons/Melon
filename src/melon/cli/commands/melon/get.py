from dataclasses import dataclass
from pathlib import Path

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from ..base_processor import PreparedData
from ..base_processor.parameters_templates import (
	T_ForceModeRequired,
	T_SingleParserRequired,
)
from ._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_ForceModeRequired, T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	link: str
	directory: Path | None
	full_name: str | None
	name: str | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
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

		return "Download image by URL."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""
		
		ComPos = command.create_position("URL", "Link to image.", important = True)
		ComPos.set_argument(ValidableTypes.URL)

		self._AddParserPosition()

		ComPos = command.create_position("NAME", "Naming operation. By default save original.")
		ComPos.add_key("--fullname", description = "Set full name with filename extension.")
		ComPos.add_key("--name", description = "Rename, but save original filename extension.")

		self._AddForceModeFlag()

		command.base.add_key("--dir", type = ValidableTypes.ValidPath, description = "Output directory.")

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

		Link: str = data.get_important_position_value("URL", expected_type = str)
		Directory: Path | None = data.get_key_value("--dir", expected_type = Path)

		FullName: str | None = data.get_key_value("--fullname", expected_type = str)
		Name: str | None = data.get_key_value("--name", expected_type = str)

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			link = Link,
			directory = Directory,
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			full_name = FullName,
			name = Name
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Filename: str = parameters.required_parser.source_operator.images_downloader.build_target_filename(
			url = parameters.link,
			filename = parameters.full_name or parameters.name,
			is_full_filename = bool(parameters.full_name),
		)

		self.printer.emit(f"Downloading \"{Filename}\"… ", end_line = False)

		Result = parameters.required_parser.source_operator.download_image(
			url = parameters.link,
			directory = parameters.directory,
			filename = parameters.full_name or parameters.name,
			is_full_filename = bool(parameters.full_name),
			force_mode = parameters.is_force_mode_enabled
		)
	
		self.printer.templates.image_downloading_result(Result)

		return True
	