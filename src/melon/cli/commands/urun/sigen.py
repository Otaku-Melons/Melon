from dataclasses import dataclass
from pathlib import Path

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes

from .... import utils
from ..base_processor import PreparedData
from ..base_processor.parameters_templates import T_SingleParserRequired
from ..melon._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	image: Path
	signature_version: utils.unstubber.SignaturesVersions

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

		return "Generate image signature."

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("IMAGE", "Path to image.", important = True)
		ComPos.set_argument(ValidableTypes.ValidPath)

		ComPos = command.create_position("VERSION", "Signature version.", important = True)
		ComPos.add_flag("-v1", description = "Based on image sizes and pixels SHA256 hash: exact match.")
		ComPos.add_flag("-v2", description = "Based on perceptual hash: approximate match.")

		command.base.add_key("--export", description = "Exports signature in parser config.")

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

		VersionKey: str = data.get_important_position_value("VERSION", expected_type = str)
		VersionKey = VersionKey.lstrip("-")
		Version = utils.unstubber.SignaturesVersions[VersionKey]

		return Parameters(
			required_parser = prepared_data.required_parsers[0],
			image = data.get_important_position_value("IMAGE", expected_type = Path),
			signature_version = Version
		)

	def _Process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Unstubber = utils.Unstubber()
		Signature: str = Unstubber.generate_signature(parameters.image, parameters.signature_version)

		self.printer.emit(f"Signature: {Signature}")

		return False