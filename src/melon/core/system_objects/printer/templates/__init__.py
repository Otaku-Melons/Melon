from typing import TYPE_CHECKING

from .cacher import CacherTemplates
from .classificator import ClassificatorTemplates
from .collector import CollectorTemplates
from .images import ImagesTemplates
from .manager import ManagerTemplates
from .parsing import ParsingTemplates

if TYPE_CHECKING:
	from ...printer import Printer

class Templates:
	"""Расширенные шаблоны вывода."""
	
	@property
	def cacher(self) -> CacherTemplates:
		"""Расширенные шаблоны вывода: оператор кэширования пар ID-алиас."""

		return self.__Cacher

	@property
	def classificator(self) -> ClassificatorTemplates:
		"""Расширенные шаблоны вывода: оператор обработки классификаторов."""

		return self.__Classificator

	@property
	def collector(self) -> CollectorTemplates:
		"""Расширенные шаблоны вывода: сборщик алиасов."""

		return self.__Collector

	@property
	def images(self) -> ImagesTemplates:
		"""Расширенные шаблоны вывода: обработка изображений."""

		return self.__Images
	
	@property
	def manager(self) -> ManagerTemplates:
		"""Расширенные шаблоны вывода: системный менеджер."""

		return self.__Manager
	
	@property
	def parsing(self) -> ParsingTemplates:
		"""Расширенные шаблоны вывода: процесс парсинга."""

		return self.__Parsing

	def __init__(self, printer: "Printer"):
		"""
		Расширенные шаблоны вывода.

		:param printer: Оператор вывода.
		:type printer: Printer
		"""

		self.__Printer = printer

		self.__Cacher = CacherTemplates(self.__Printer)
		self.__Classificator = ClassificatorTemplates(self.__Printer)
		self.__Collector = CollectorTemplates(self.__Printer)
		self.__Images = ImagesTemplates(self.__Printer)
		self.__Manager = ManagerTemplates(self.__Printer)
		self.__Parsing = ParsingTemplates(self.__Printer)
