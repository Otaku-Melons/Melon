from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...base.parsers.components.settings import BaseExtensionOptions

if TYPE_CHECKING:
	from pathlib import Path

	from ....core.system_objects import SystemObjects
	from ....core.system_objects.printer import Portals
	from ..source_operator import BaseSourceOperator

class BaseExtension[T: BaseExtensionOptions](ABC):
	"""Базовое расширение."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def name(self) -> str:
		"""Имя расширения."""

		return self._Name

	@property
	def options(self) -> T:
		"""Настройки расширения."""

		return self._Options

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._SourceOperator.portals

	@property
	def source_operator(self) -> "BaseSourceOperator":
		"""Оператор источника."""

		return self._SourceOperator

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self._SourceOperator.system_objects

	@property
	def temp_directory(self) -> "Path":
		"""Путь ко временной директории расширения."""

		return self._TempDirectory

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	@abstractmethod
	def _ReturnOptionsType(self) -> type[T]:
		"""
		Возвращает тип контейнера опций.

		:return: Тип контейнера опций.
		:rtype: type[T]
		"""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Базовое расширение.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		:param name: Имя расширения.
		:type name: str
		:raises FileNotFoundError: Каталог расширения не найден.
		"""

		self._SourceOperator: "BaseSourceOperator" = source_operator
		self._Name: str = self.__module__.split(".")[-1]
		
		self._Options: T = self.source_operator.settings.extensions.get(self._Name, self._ReturnOptionsType())
		self._TempDirectory: "Path" = self._SourceOperator.system_objects.temper.get_extension_temp_directory(self._SourceOperator.parser_name, self._Name)

		self._PostInitMethod()