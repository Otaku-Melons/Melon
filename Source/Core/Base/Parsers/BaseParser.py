from Source.Core.Base.Formats.BaseFormat import BaseChapter, BaseBranch, BaseTitle
from Source.Core import Exceptions

from typing import Any, cast, TYPE_CHECKING
from abc import ABC, abstractmethod
import functools

if TYPE_CHECKING:
	from Source.Core.Base.Parsers.Components.ImagesDownloader import ImagesDownloader
	from Source.Core.Base.Parsers.Components import ParserManifest, ParserSettings
	from Source.Core.Base.SourceOperator import BaseSourceOperator

	from dublib.WebRequestor import WebRequestor

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseParser(ABC):
	"""Базовый парсер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def images_downloader(self) -> "ImagesDownloader":
		"""Оператор скачивания изображений."""

		return self._SourceOperator.images_downloader

	@property
	def manifest(self) -> "ParserManifest":
		"""Манифест парсера."""

		return self._SourceOperator.manifest

	@property
	def requestor(self) -> "WebRequestor":
		"""Менеджер запросов."""

		return self._SourceOperator.requestor

	@property
	def settings(self) -> "ParserSettings":
		"""Настройки парсера."""

		return self._SourceOperator.settings
	
	@property
	def source_operator(self) -> "BaseSourceOperator":
		"""Оператор источника."""

		return self._SourceOperator

	@property
	def title(self) -> BaseTitle | None:
		"""Тайтл."""

		return self._Title

	#==========================================================================================#
	# >>>>> ДЕКОРАТОРЫ <<<<< #
	#==========================================================================================#

	@staticmethod
	def require_title(function):
		"""
		Декоратор. Проверяет, открыт ли тайтл.

		:param function: Метод объекта.
		:type function: Callable
		:return: Обёрнутая функция.
		:rtype: Callable
		:raises TitleNotSetted: Не задан тайтл.
		"""

		@functools.wraps(function)
		def Wrapper(self: "BaseParser", *args, **kwargs):
			if not self._Title:
				raise Exceptions.Parsers.TitleNotSetted()
			return function(self, *args, **kwargs)
		
		return Wrapper

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _Amend(self, branch: BaseBranch, chapter: BaseChapter):
		"""
		Дополняет главу дайными о контенте.

		:param branch: Данные ветви.
		:type branch: BaseBranch
		:param chapter: Данные главы.
		:type chapter: BaseChapter
		"""

		pass

	@abstractmethod
	def _Parse(self):
		"""Получает основные данные тайтла."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _PreSaver(self):
		"""Запускается непосредственно перед сохранением тайтла."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Базовый парсер.

		:param source_operator: Оператор источника.
		:type source_operator: source_operator
		"""

		self._SourceOperator = source_operator

		self._Title: BaseTitle | None = None

		self._PostInitMethod()

	@abstractmethod
	def amend(self, branch: Any, chapter: Any):
		"""
		Дополняет главу дайными о контенте.

		:param branch: Данные ветви.
		:type branch: Any
		:param chapter: Данные главы.
		:type chapter: Any
		"""

		pass

	@require_title
	def parse(self):
		"""Получает основные данные тайтла."""

		self._Parse()

	@require_title
	def save(self):
		"""Сохраняет тайтл и выгружает его из парсера."""

		self._Title = cast(BaseTitle, self._Title)

		self._PreSaver()
		self._Title.save()
		self._Title = None

	def load_title(self, slug: str):
		"""
		Инициализирует структуру тайтла.

		:param slug: Алиас тайтла.
		:type slug: str
		"""

		self._Title = None