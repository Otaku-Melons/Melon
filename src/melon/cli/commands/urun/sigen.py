from dataclasses import dataclass
from pathlib import Path

from dublib.cli.terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.functions.filesystem import json

from .... import utils
from ..base_processor import PreparedData, RequiredParser
from ..base_processor.templates import T_OptionalSingleParser
from ..melon._base import CommandProcessorTemplate

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters(T_OptionalSingleParser):
	"""Параметры, требуемые обработчиком."""

	image: Path
	signature_version: utils.unstubber.SignaturesVersions

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ExportSingature(self, signature: str, required_parser: RequiredParser) -> bool:
		"""
		Экспортирует сигнатуру в файл конфигурации парсера.

		:param signature: Сигнатура изображения.
		:type signature: str
		:param required_parser: Коллекция управляющих объектов трубемого парсера.
		:type required_parser: RequiredParser
		:return: Возвращает `False`, если команда требует прерывания выполнения.
		:rtype: bool
		"""

		Config: Path = self.system_objects.options.CONFIGS_DIR.value / f"{required_parser.name}.json"

		if not Config.exists():
			self.printer.emit("Configuration file not found.")
			return False

		ConfigData: dict[str, dict] = json.read(Config)

		if "filters" not in ConfigData: ConfigData["filters"] = {}
		if "images" not in ConfigData["filters"]: ConfigData["filters"]["images"] = {}

		Signatures: list[str] = ConfigData["filters"]["images"].get("signatures", [])

		if signature in Signatures:
			self.printer.warning("Signature already exists. Export skipped.")
			return True

		Signatures.append(signature)
		ConfigData["filters"]["images"]["signatures"] = Signatures
		json.write(Config, ConfigData)
		self.printer.emit(f"Exported in <b>{required_parser.name}</b> config.")

		return True

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GetParsersQuery(self, data: ParsedCommandData) -> str | None:
		"""
		Возвращает строку, представляющую последовательность имён затребованных парсеров, разделённых запятой.

		По умолчанию берёт данные из позиций `PARSER` или `PARSERS`.
		
		:param data: Данные обработанной команды.
		:type data: ParsedCommandData
		:return: Строка с именами парсеров или `None`, если не требуются.
		:rtype: str | None
		"""

		return data.get_key_value("--export", expected_type = str)

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
			required_parser = prepared_data.required_parsers[0] if prepared_data.required_parsers else None,
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
		Image = Unstubber.load_image(parameters.image)
		Signature: str = Unstubber.generate_signature(Image, parameters.signature_version)
		self.printer.emit(f"Signature: <i>{Signature}</i>")

		if parameters.required_parser:
			return self.__ExportSingature(Signature, parameters.required_parser)

		return True