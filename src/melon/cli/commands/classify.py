from dataclasses import dataclass
from pathlib import Path

import orjson

from dublib.CLI.Terminalyzer import Command, ParsedCommandData, ValidableTypes
from dublib.Functions.Filesystem import WriteJSON

from ... import utils
from ...core import exceptions
from ..base_processor import BaseCommandProcessor, PreparedData, ProcessorOptions

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class Parameters:
	"""Параметры, требуемые обработчиком."""

	target: str
	is_output_json: bool
	file_to_write: Path | None
	is_ignore_case: bool

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

		return "Process titles classificators."

	def _ExportOptions(self) -> ProcessorOptions:
		"""
		Возвращает контейнер настроек обработчика.

		:return: Контейнер настроек обработчика.
		:rtype: ProcessorOptions
		"""

		return ProcessorOptions(use_timer = False)

	def _GenerateCommand(self, command: Command) -> Command:
		"""
		Генерирует команду.
		
		:param command: Шаблон для команды.
		:type command: Command
		:return: Команда.
		:rtype: Command
		"""

		ComPos = command.create_position("VALUE", "Input value to classification.", important = True)
		ComPos.set_argument()

		ComPos = command.create_position("MODE", "Output mode. By default styled print to terminal.")
		ComPos.add_flag("-j", aliases = ("--json",), description = "Prints JSON-string in terminal.")
		ComPos.add_key("--file", type = ValidableTypes.Path, description = "Path to dump JSON file.")

		command.base.add_flag("-i", aliases = ("--ignorecase",), description = "Ignore characters case in procedures searching.")

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

		Target: str = data.get_important_position_value("VALUE", expected_type = str)
		IsOutputJSON: bool = data.check_flag("-j")
		FileToWrite: Path | None = data.get_key_value("--file", expected_type = Path)
		IgnoreCase: bool = data.check_flag("-i")

		return Parameters(
			target = Target,
			is_output_json = IsOutputJSON,
			file_to_write = FileToWrite,
			is_ignore_case = IgnoreCase
		)

	def _Process(self, parameters: Parameters):
		"""
		Выполняет команду.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		"""

		ScriptPath: Path = Path(f"{self.system_objects.options.CONFIGS_DIR}/classificator.ini")
		
		if not ScriptPath.exists():
			self.printer.critical(f"Script file \"{ScriptPath}\" doesn't exists.")
			return None
		
		ClassificatorObject = utils.Classificator(ScriptPath)
		ExecutableLines = ClassificatorObject.read_script()
		ScriptValidationErrors = ClassificatorObject.validate_script(ExecutableLines)
		
		for ErrorData in ScriptValidationErrors:
			self.printer.error(f"[{ErrorData.line.file.name}:{ErrorData.line.number}] {ErrorData.message}")
		
		if ScriptValidationErrors:
			self.printer.critical("Script failure due to validation errors.")
			return None
		
		try:
			Procedures = ClassificatorObject.parse_procedures(ExecutableLines)
		except exceptions.utils.classificator.ScriptRuntimeError as ExecutionData:
			self.printer.critical(str(ExecutionData))
			return None
		
		ClassificationResult = ClassificatorObject.classify(parameters.target, Procedures, ignore_case = parameters.is_ignore_case)
		
		if parameters.is_output_json:
			self.printer.emit(orjson.dumps(ClassificationResult.to_dict()).decode())
		else:
			self.printer.templates.classification_result(ClassificationResult)
		
		if parameters.file_to_write:
			WriteJSON(parameters.file_to_write, ClassificationResult.to_dict())
			self.printer.emit(f"Classification result dumped in file: \"{parameters.file_to_write}\".")