from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, override

import orjson

from dublib.functions.filesystem import json
from dublib.validators import ValidableTypes

from .... import utils
from ....core import exceptions
from ...base.templates import BaseParameters
from ..melon._base import CommandProcessorTemplate

if TYPE_CHECKING:
	from dublib.cli.terminalyzer import CommandEntity, CommandModel

	from ...base.structs import PreparedData

@dataclass(frozen = True)
class Parameters(BaseParameters):
	"""Параметры, требуемые обработчиком."""

	target: str
	is_output_json: bool
	file_to_write: Path | None
	is_ignore_case: bool

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@override
	def _build_model(self, model: "CommandModel") -> "CommandModel":
		"""
		Генерирует модель команды.
		
		:param model: Шаблон модели команды.
		:type model: Command
		:return: Модель команды.
		:rtype: CommandModel
		"""


		position = model.create_position("VALUE", "Input value to classification.", important = True)
		position.set_argument()

		position = model.create_position("MODE", "Output mode. By default styled print to terminal.")
		# To-Do: заменить на шаблон.
		position.add_flag("-j", aliases = ("--json",), description = "Prints JSON-string in terminal.")
		position.add_key("--file", value_type = ValidableTypes.Path, description = "Path to dump JSON file.")

		model.base.add_flag("-i", aliases = ("--ignorecase",), description = "Ignore characters case in procedures searching.")

		return model

	@override
	def _export_description(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Process titles classificators."

	@override
	def _parse_parameters(self, entity: "CommandEntity", prepared_data: "PreparedData") -> Parameters:
		"""
		Парсит данные обработанной команды в структуру **dataclass**.

		:param entity: Сущность команды.
		:type entity: CommandEntity
		:param prepared_data: Подготовленные шаблонные параметры команды.
		:type prepared_data: PreparedData
		:return: Структура **dataclass**.
		:rtype: Parameters
		"""

		return Parameters(
			target = entity.get_position_value("VALUE", expected_type = str, important = True),
			is_output_json = entity.check_flag("-j"),
			file_to_write =  entity.get_key_value("--file", expected_type = Path),
			is_ignore_case = entity.check_flag("-i")
		)

	@override
	def _process(self, parameters: Parameters) -> bool:
		"""
		Выполняет команду.

		:param parameters: Требуемые параметры.
		:type parameters: Parameters
		:return: Возвращает `True`, если выполнение успешно и прерывание не требуется.
		:rtype: bool
		"""

		ScriptPath: Path = Path(f"{self.system_objects.options.CONFIGS_DIR}/classificator.ini")
		
		if not ScriptPath.exists():
			self.printer.critical(f"Script file \"{ScriptPath}\" doesn't exists.")
			return False
		
		ClassificatorObject = utils.Classificator(ScriptPath)
		ExecutableLines = ClassificatorObject.read_script()
		ScriptValidationErrors = ClassificatorObject.validate_script(ExecutableLines)
		
		for ErrorData in ScriptValidationErrors:
			self.printer.error(f"[{ErrorData.line.file.name}:{ErrorData.line.number}] {ErrorData.message}")
		
		if ScriptValidationErrors:
			self.printer.critical("Script failure due to validation errors.")
			return False
		
		try:
			Procedures = ClassificatorObject.parse_procedures(ExecutableLines)
		except exceptions.utils.classificator.ScriptRuntimeError as ExecutionData:
			self.printer.critical(str(ExecutionData))
			return False
		
		ClassificationResult = ClassificatorObject.classify(parameters.target, Procedures, ignore_case = parameters.is_ignore_case)
		
		if parameters.is_output_json:
			self.printer.emit(orjson.dumps(ClassificationResult.to_dict()).decode())
		else:
			self.printer.templates.classificator.result(ClassificationResult)
		
		if parameters.file_to_write:
			json.write(parameters.file_to_write, ClassificationResult.to_dict())
			self.printer.emit(f"Classification result dumped in file: \"{parameters.file_to_write}\".")

		return True
