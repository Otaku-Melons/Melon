from dataclasses import dataclass
from pathlib import Path

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.Functions.Filesystem import WriteJSON

from ..BaseProcessor import BaseCommandProcessor, PreparedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	link: str
	parser: str
	directory: Path | None
	is_force_mode_enabled: bool
	full_name: str | None
	name: str | None

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
			link = Link,
			parser = prepared_data.required_parsers_names[0],
			directory = Directory,
			is_force_mode_enabled = prepared_data.is_force_mode_enabled,
			full_name = FullName,
			name = Name
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		EntryPoint = self.system_objects.driver.get_entry_point(parameters.parser)
		Result = EntryPoint.source_operator.download_image(
			url = parameters.link,
			directory = parameters.directory,
			filename = parameters.full_name or parameters.name,
			is_full_filename = bool(parameters.full_name),
			force_mode = parameters.is_force_mode_enabled
		)
	
		if Result.error_message:
			self.printer.error(Result.error_message)
		elif Result.is_already_exists and not Result.is_downloaded:
			self.printer.emit("Image already exists.")
		elif Result.is_already_exists and Result.is_downloaded:
			self.printer.emit("Image overwritten.")
		
		if Result.path:
			self.printer.emit(f"Image path: \"{Result.path}\".")
	