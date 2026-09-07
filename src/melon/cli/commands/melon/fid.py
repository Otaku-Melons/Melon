from dataclasses import dataclass
from typing import TYPE_CHECKING, override

import orjson

from ...base.templates import T_SingleParserRequired
from ._base import CommandProcessorTemplate

if TYPE_CHECKING:
	from dublib.cli.terminalyzer import CommandEntity, CommandModel

	from ...base.structs import PreparedData

@dataclass(frozen = True)
class Parameters(T_SingleParserRequired):
	"""Параметры, требуемые обработчиком."""

	slug: str
	is_json_output: bool

class CommandProcessor(CommandProcessorTemplate[Parameters]):
	"""Обработчик команды."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __print_result(self, parameters: Parameters, title_id: int | None):
		"""
		Выводит результат поиска ID.

		:param parameters: Параметры команды.
		:type parameters: Parameters
		:param title_id: Результат поиска.
		:type title_id: int | None
		"""

		if parameters.is_json_output:
			OutputDictionary: dict[str, int | str | None] = {
				"parser": parameters.required_parser.name,
				"slug": parameters.slug,
				"id": title_id
			}
			self.printer.emit(orjson.dumps(OutputDictionary).decode())

		else:
			if title_id:
				self.printer.emit(f"Found ID {title_id} for parser \"{parameters.required_parser.name}\".")
			else:
				self.printer.emit(f"ID not foind in \"{parameters.required_parser.name}\" cache.")

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@override
	def _build_model(self, model: CommandModel) -> CommandModel:
		"""
		Генерирует модель команды.
		
		:param model: Шаблон модели команды.
		:type model: Command
		:return: Модель команды.
		:rtype: CommandModel
		"""

		position = model.create_position("SLUG", "Title slug.", important = True)
		position.set_argument()

		self._add_parser_position(key = "--use")

		# To-Do: вынести флаг в генераторы.
		model.base.add_flag("-j", description = "Print result in JSON format.")

		return model

	@override
	def _export_description(self) -> str:
		"""
		Возвращает описание команды.
		
		:return: Описание команды.
		:rtype: str
		"""

		return "Find title identificator in cache."

	@override
	def _parse_parameters(self, entity: "CommandEntity", prepared_data: PreparedData) -> Parameters:
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
			required_parser = prepared_data.required_parsers[0],
			slug = entity.get_position_value("SLUG", expected_type = str, important = True),
			is_json_output = entity.check_flag("-j")
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

		source_operator = self._launch_source_operator(parameters.required_parser)
		title_id: int | None = source_operator.shared_data.journal.get_id_by_slug(parameters.slug)
		self.__print_result(parameters, title_id)

		return False if parameters.is_json_output else True
