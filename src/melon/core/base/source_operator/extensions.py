from typing import TYPE_CHECKING

from dublib.functions.filesystem import json

from ... import exceptions

if TYPE_CHECKING:
	from ..extensions import BaseExtension
	from . import BaseSourceOperator

class ExtensionsOperator:
	"""Оператор расширений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def names(self) -> tuple[str, ...]:
		"""Имена доступных расширений."""

		return self.__parser_operator.extensions_names

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __load_activation_states(self) -> dict[str, bool]:
		"""
		Загружает состояния активации расширений.

		:return: Словарь состояний, в котором ключ – имя расширения, а значение – статус активации.
		:rtype: dict[str, bool]
		"""

		enabled_file = self.__source_operator.temp_directory / "extensions" / "enabled.json"
		file_states: dict = json.read(enabled_file)
		activation_states: dict[str, bool] = {}

		for name in self.names:
			is_enabled = file_states.get(name, False)
			activation_states[name] = is_enabled

		return activation_states

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Оператор расширений.

		:param source_operator: Базовый оператор источника.
		:type source_operator: BaseSourceOperator
		"""

		self.__source_operator = source_operator

		self.__parser_name = self.__source_operator.parser_name
		self.__parser_operator = self.__source_operator.system_objects.manager.parsers.get_operator(self.__parser_name)

		self.__activation_states: dict[str, bool] = self.__load_activation_states()

	def is_enabled[E: "BaseExtension"](self, extension: type[E]) -> bool:
		"""
		Проверяет, включено ли расширение.

		:param extension: Тип расширения.
		:type extension: type[BaseExtension]
		:return: Состояние: включено ли расширение.
		:rtype: bool
		:raises ExtensionNotFound: Расширение не найдено.
		"""

		extension_name: str = extension.__module__.split(".")[-1]

		if extension_name not in self.__activation_states:
			raise exceptions.extensions.ExtensionNotFound(extension_name)

		return self.__activation_states[extension_name]
		
	def run[E: "BaseExtension"](self, extension: type[E]) -> E:
		"""
		Запускает расширение.

		:param extension: Тип расширения.
		:type extension: type[BaseExtension]
		:return: Расширение.
		:rtype: BaseExtension
		"""

		return extension(self.__source_operator)
