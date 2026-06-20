from .Components.WordsDictionary import Presets, WordsDictionary

from Source.Core.Base.Formats.BaseFormat import BaseBranch, BaseTitle
from Source.Core import Exceptions

from dublib.Methods.Decorators import run_before_method

from typing import Any, cast, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
	from Source.Core.Base.Parsers.Components.ImagesDownloader import ImagesDownloader
	from Source.Core.Base.Parsers.Components import ParserManifest, ParserSettings
	from Source.Core.Base.SourceOperator import BaseSourceOperator
	from Source.Core.SystemObjects.Logger import Portals

	from dublib.WebRequestor import WebRequestor

	from pathlib import Path

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
	def temp_directory(self) -> "Path":
		"""Путь ко временному каталогу парсера."""

		return self._SourceOperator.system_objects.temper.get_parser_temp_directory(self.manifest.parser_name)

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._SourceOperator.entry_point.portals

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

	@property
	def words_dictionary(self) -> WordsDictionary:
		"""Словарь ключевых локализованных определений."""

		return self._WordsDictionary

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _RequireTitle(self):
		"""
		Проверяет, задан ли тайтл.

		:raises Exceptions.Parsers.TitleNotSetted: Не задан тайтл.
		"""

		if not self._Title:
			raise Exceptions.Parsers.TitleNotSetted()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _Amend(self, branch: BaseBranch, chapter: Any):
		"""
		Дополняет главу дайными о контенте.

		:param branch: Ветвь.
		:type branch: BaseBranch
		:param chapter: Глава.
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

		self._WordsDictionary: WordsDictionary = WordsDictionary(None)
		self._Title: BaseTitle | None = None

		self._PostInitMethod()

	@abstractmethod
	def amend(self):
		"""Дополняет главы дайными о контенте."""

		pass

	def load_words_dictionary_preset(self, language_code: str) -> WordsDictionary | None:
		"""
		Загружает готовый словарь локализованных определений. Словарь будет установлен в качестве рабочего для парсера.

		:param language_code: Код языка по стандарту ISO 639-3.
		:type language_code: str
		:return: Пресет словаря для определённого языка или `None` при его отсутствии.
		:rtype: WordsDictionary | None
		"""

		Preset = Presets.GetDictionaryPreset(language_code)

		if Preset:
			self._WordsDictionary = Preset

		return Preset

	@abstractmethod
	def load_title(self, slug: str, empty: bool = False) -> BaseTitle:
		"""
		Загружает и устанавливает тайтл в парсер.

		:param slug: Алиас тайтла.
		:type slug: str
		:param empty: Указывает, что нужно инициалазировать пустой тайтл, минуя операцию чтения локальных данных.
		:type empty: bool
		:return: Тайтл.
		:rtype: BaseTitle
		"""
		
		pass

	@run_before_method("_RequireTitle")
	def parse(self):
		"""Получает основные данные тайтла."""

		self._Parse()

	@abstractmethod
	def repair(self, chapter_id: int) -> bool:
		"""
		Восстанавливает содержимое главы, заново получая его из источника.

		:param chapter_id: Уникальный идентификатор целевой главы.
		:type chapter_id: int
		:raises ChapterNotFound: В локальном JSON не найдена глава с указанным ID.
		:return: Возвращает `True`, если глава содержит контент после восстановления.
		:rtype: bool
		"""

		pass

	@run_before_method("_RequireTitle")
	def save(self, sorting: bool = False):
		"""
		Сохраняет тайтл и выгружает его из парсера.

		:param sorting: Указывает, нужно ли провести сортировку глав на основе их нумерации.
		:type sorting: bool
		"""

		self._Title = cast(BaseTitle, self._Title)

		self._PreSaver()
		self._Title.save(sorting)
		self._Title = None