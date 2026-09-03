from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Sequence, cast

from dublib.functions.decorators import run_before_method

from ....core import exceptions
from ....core.base.formats.base_format.branch import Branch
from ....core.base.formats.base_format.controller import BaseTitleController
from ....core.base.formats.base_format.data import BaseTitleData
from ....core.base.parsers.components.images_downloader import (
	ImageDownloadingResult,
	ImagesDownloader,
)
from ..structs.image import ImageData
from .components.words_dictionary import WordsDictionary, presets

if TYPE_CHECKING:
	from dublib.web_requestor import WebRequestor

	from ....core.base.formats.base_format.data import BaseTitleData
	from ....core.base.parsers.components.manifest import ParserManifest
	from ....core.base.parsers.components.settings import (
		CustomSettingsTemplate,
		ParserSettings,
	)
	from ....core.system_objects.printer import Portals
	from ..source_operator import BaseSourceOperator

class BaseParser[SO: "BaseSourceOperator", CSM: "CustomSettingsTemplate"](ABC):
	"""Базовый парсер."""

	_Title: "BaseTitleController[BaseTitleData] | None"

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def images_downloader(self) -> "ImagesDownloader":
		"""Оператор скачивания изображений."""

		return self._source_operator.images_downloader

	@property
	def manifest(self) -> "ParserManifest":
		"""Манифест парсера."""

		return self._source_operator.manifest

	@property
	def temp_directory(self) -> Path:
		"""Путь ко временному каталогу парсера."""

		return self._source_operator.system_objects.temper.get_parser_temp_directory(self.manifest.parser_name)

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._source_operator.portals

	@property
	def requestor(self) -> "WebRequestor":
		"""Менеджер запросов."""

		return self._source_operator.requestor

	@property
	def settings(self) -> "ParserSettings[CSM]":
		"""Настройки парсера."""

		return self._source_operator.settings
	
	@property
	def source_operator(self) -> SO:
		"""Оператор источника."""

		return self._source_operator

	@property
	def title(self) -> "BaseTitleController[BaseTitleData] | None":
		"""Тайтл."""

		return self._title

	@property
	def words_dictionary(self) -> WordsDictionary:
		"""Словарь ключевых локализованных определений."""

		return self._words_dictionary

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	@run_before_method("_require_title")
	def _download_images(self, images_data: Sequence[ImageData], image_type: Literal["cover", "person"], force_mode: bool) -> list[ImageDownloadingResult]:
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

		Title = cast(BaseTitleController, self._title)
		ImageDirecory: Path = self.settings.directories.images / Title.used_filename / image_type
		ImageDirecory.mkdir(parents = True, exist_ok = True)
		Results: list = []
		ImagesCount: int = len(images_data)

		for Index in range(ImagesCount):
			CurrentImageData = images_data[Index]

			Future = self.portals.printer.templates.images.start_downloading(CurrentImageData.filename, image_type)
			Result = self._source_operator.images_downloader.download_image(CurrentImageData.link, ImageDirecory, force_mode = force_mode)
			Results.append(Result)
			
			if Result.resolution:
				CurrentImageData.set_resolution(Result.resolution)

			Future.result(Result)

			if Result.is_already_exists and not Result.is_downloaded:
				continue

		return Results

	def _require_title(self):
		"""
		Проверяет, задан ли тайтл.

		:raises exceptions.parsers.TitleNotSetted: Не задан тайтл.
		"""

		if not self._title:
			raise exceptions.parsers.TitleNotSetted()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕМЕТОДЫ <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _amend(self, branch: Branch, chapter: Any) -> str | None:
		"""
		Дополняет главу дайными о контенте.

		:param branch: Ветвь.
		:type branch: Branch
		:param chapter: Глава.
		:type chapter: BaseChapter
		:return: Дополнительное необязательное сообщение о дополнении.
		:rtype: str | None
		"""

		pass

	@abstractmethod
	def _parse(self):
		"""Получает основные данные тайтла."""

		pass

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _pre_saver(self):
		"""Запускается непосредственно перед сохранением тайтла."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: SO):
		"""
		Базовый парсер.

		:param source_operator: Оператор источника.
		:type source_operator: source_operator
		"""

		self._source_operator = source_operator

		self._words_dictionary: WordsDictionary = WordsDictionary(None)
		self._title: "BaseTitleController[BaseTitleData] | None" = None

		self._post_init()

	@abstractmethod
	def amend(self):
		"""Дополняет главы дайными о контенте."""

		pass

	@run_before_method("_require_title")
	def download_images(self, force_mode: bool) -> "tuple[ImageDownloadingResult, ...]":
		"""
		Скачивает обложки и портреты персонажей.

		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Последовательность результатов скачивания.
		:rtype: tuple[ImageDownloadingResult, ...]
		"""

		Title = cast(BaseTitleController["BaseTitleData"], self._title)
		
		Results = self._download_images(Title.data.covers, "cover", force_mode)

		PersonsImages: list[ImageData] = []
		for CurrentPerson in Title.data.perons:
			PersonsImages += list(CurrentPerson.images)

		Results += self._download_images(PersonsImages, "person", force_mode)

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
			self._words_dictionary = Preset

		return Preset

	@abstractmethod
	def init_empty_title(self, slug: str) -> BaseTitleController:
		"""
		Устанавливает пустой тайтл для парсера.

		:param slug: Алиас тайтла.
		:type slug: str
		:return: Тайтл.
		:rtype: BaseTitleController
		"""
		
		pass

	@run_before_method("_require_title")
	def parse(self):
		"""Получает основные данные тайтла."""

		self._parse()

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

	@run_before_method("_require_title")
	def save(self, sorting: bool = False) -> bool:
		"""
		Сохраняет тайтл и выгружает его из парсера.

		:param sorting: Указывает, нужно ли провести сортировку глав на основе их нумерации.
		:type sorting: bool
		:return: Возвращает `True`, если файл сохранён, и `False`, если изменений из-за отсутствия изменений запись не выполнялась.
		:rtype: bool
		"""

		self._title = cast(BaseTitleController, self._title)

		self._pre_saver()
		IsSaved = self._title.save(sorting)
		self._title = None

		return IsSaved