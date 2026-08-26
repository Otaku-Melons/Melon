from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Sequence, cast

from dublib.functions.decorators import run_before_method

from ....core import exceptions
from ....core.base.formats.base_format import BaseBranch, BaseTitle
from ....core.base.parsers.components.images_downloader import (
	ImageData,
	ImageDownloadingResult,
	ImagesDownloader,
)
from .components.words_dictionary import WordsDictionary, presets

if TYPE_CHECKING:
	from dublib.web_requestor import WebRequestor

	from ....core.base.parsers.components import ParserManifest, ParserSettings
	from ....core.base.source_operator import BaseSourceOperator
	from ....core.system_objects.printer import Portals

class BaseParser(ABC):
	"""Базовый парсер."""

	_Title: BaseTitle | None

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
	def temp_directory(self) -> Path:
		"""Путь ко временному каталогу парсера."""

		return self._SourceOperator.system_objects.temper.get_parser_temp_directory(self.manifest.parser_name)

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._SourceOperator.portals

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

	@run_before_method("_RequireTitle")
	def _DownloadImages(self, images_data: Sequence[ImageData], image_type: Literal["cover", "person"], force_mode: bool) -> list[ImageDownloadingResult]:
		"""
		Скачивает изображения тайтла определённого типа.

		:param images_data: Данные изображений.
		:type images_data: Sequence[ImageData]
		:param image_type: Тип изображения.
		:type image_type: Literal["cover", "person"]
		:param force_mode: Указывает, перезаписывать ли существующие файлы изображений.
		:type force_mode: bool
		:return: Список результатов скачивания изображений.
		:rtype: list[ImageDownloadingResult]
		"""

		self._Title = cast(BaseTitle, self._Title)
		ImageDirecory: Path = self.settings.directories.images / self._Title.used_filename / image_type
		ImageDirecory.mkdir(parents = True, exist_ok = True)
		Results: list = []
		ImagesCount: int = len(images_data)

		for Index in range(ImagesCount):
			CurrentImageData = images_data[Index]

			self.portals.printer.templates.images.start_downloading(CurrentImageData.filename, image_type)
			Result = self._SourceOperator.images_downloader.download_image(CurrentImageData.link, ImageDirecory, force_mode = force_mode)
			Results.append(Result)
			
			if Result.resolution:
				CurrentImageData.set_resolution(Result.resolution)

			self._SourceOperator.images_downloader.print_result(Result)

			if Result.is_already_exists and not Result.is_downloaded:
				continue

		return Results

	def _RequireTitle(self):
		"""
		Проверяет, задан ли тайтл.

		:raises exceptions.parsers.TitleNotSetted: Не задан тайтл.
		"""

		if not self._Title:
			raise exceptions.parsers.TitleNotSetted()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _Amend(self, branch: BaseBranch, chapter: Any) -> str | None:
		"""
		Дополняет главу дайными о контенте.

		:param branch: Ветвь.
		:type branch: BaseBranch
		:param chapter: Глава.
		:type chapter: BaseChapter
		:return: Дополнительное необязательное сообщение о дополнении.
		:rtype: str | None
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

	@run_before_method("_RequireTitle")
	def download_images(self, force_mode: bool) -> "tuple[ImageDownloadingResult, ...]":
		"""
		Скачивает обложки и портреты персонажей.

		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Последовательность результатов скачивания.
		:rtype: tuple[ImageDownloadingResult, ...]
		"""

		self._Title = cast(BaseTitle, self._Title)
		
		Results = self._DownloadImages(self._Title.covers, "cover", force_mode)

		PersonsImages: list[ImageData] = []
		for CurrentPerson in self._Title.perons:
			PersonsImages += list(CurrentPerson.images)

		Results += self._DownloadImages(PersonsImages, "person", force_mode)

		return tuple(Results)

	def load_words_dictionary_preset(self, language_code: str) -> WordsDictionary | None:
		"""
		Загружает готовый словарь локализованных определений. Словарь будет установлен в качестве рабочего для парсера.

		:param language_code: Код языка по стандарту ISO 639-3.
		:type language_code: str
		:return: Пресет словаря для определённого языка или `None` при его отсутствии.
		:rtype: WordsDictionary | None
		"""

		Preset = presets.GetDictionaryPreset(language_code)

		if Preset:
			self._WordsDictionary = Preset

		return Preset

	@abstractmethod
	def init_empty_title(self, slug: str) -> BaseTitle:
		"""
		Устанавливает пустой тайтл для парсера.

		:param slug: Алиас тайтла.
		:type slug: str
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
	def save(self, sorting: bool = False) -> bool:
		"""
		Сохраняет тайтл и выгружает его из парсера.

		:param sorting: Указывает, нужно ли провести сортировку глав на основе их нумерации.
		:type sorting: bool
		:return: Возвращает `True`, если файл сохранён, и `False`, если изменений из-за отсутствия изменений запись не выполнялась.
		:rtype: bool
		"""

		self._Title = cast(BaseTitle, self._Title)

		self._PreSaver()
		IsSaved = self._Title.save(sorting)
		self._Title = None

		return IsSaved