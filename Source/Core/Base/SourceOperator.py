from Source.Core.Base.Parsers.Components.ImagesDownloader import ImageDownloadingResult, ImagesDownloader
from Source.Core.Base.Parsers.Components.Manifest import ContentTypes, ParserManifest
from Source.Core import Exceptions

from dublib.WebRequestor import WebConfig, WebLibs, WebRequestor
from dublib.CLI.Validators import Validator_URL

from typing import Sequence, TYPE_CHECKING
from os import PathLike
import importlib

if TYPE_CHECKING:
	from .EntryPoint import BaseEntryPoint

	from Source.Core.Base.Parsers.Components import ParserSettings
	from Source.Core.Base.Parsers.BaseParser import BaseParser
	from Source.Core.SystemObjects.Temper import SharedData
	from Source.Core.SystemObjects.Printer import Portals
	from Source.Core.SystemObjects import SystemObjects

class BaseSourceOperator:
	"""Базовый оператор источника."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def entry_point(self) -> "BaseEntryPoint":
		"""Точка входа в модуль парсера."""

		return self._EntryPoint

	@property
	def images_downloader(self) -> ImagesDownloader:
		"""Оператор скачивания изображений."""

		return self._ImagesDownloader

	@property
	def is_collector_implemented(self) -> bool:
		"""Состояние: переопределён ли метод `_CollectSlugs()`."""

		return type(self)._CollectSlugs is not BaseSourceOperator._CollectSlugs

	@property
	def manifest(self) -> ParserManifest:
		"""Манифест парсера."""

		return self._Manifest

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._EntryPoint.portals

	@property
	def settings(self) -> "ParserSettings":
		"""Настройки парсера."""

		return self._Settings
	
	@property
	def shared_data(self) -> "SharedData":
		"""Разделяемые в контексте сессий одного парсера данные."""
		
		return self._EntryPoint.shared_data

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self._SystemObjects

	@property
	def requestor(self) -> WebRequestor:
		"""Менеджер запросов."""

		return self._Requestor

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _CollectSlugs(self, period: int | None = None, filters: str | None = None, pages: int | None = None) -> Sequence[str]:
		"""
		Собирает список алиасов тайтлов по заданным параметрам.

		:param period: Количество часов до текущего момента, составляющее период получения данных.
		:type period: int | None
		:param filters: Строка, описывающая параметры фильтрации.
		:type filters: str | None
		:param pages: Количество запрашиваемых страниц каталога.
		:type pages: int | None
		:return: Набор собранных алиасов.
		:rtype: Sequence[str]
		"""

		return tuple()

	def _InitializeRequestor(self) -> WebRequestor:
		"""
		Инициализирует модуль WEB-запросов.

		:return: Оператор запросов.
		:rtype: WebRequestor
		"""

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_retries_count(self._Settings.common.retries)
		Config.generate_user_agent()
		Config.add_header("Referer", f"https://{self._Manifest.site}/")
		Config.enable_proxy_protocol_switching(True)
		WebRequestorObject = WebRequestor(Config)
		WebRequestorObject.add_proxies(self._Settings.proxies)
		
		return WebRequestorObject

	def _ParseSlugFromString(self, string: str) -> str | None:
		"""
		Парсит алиас тайтла из переданной строки. Может использоваться для обработки тайтлов по ссылкам.

		:param string: Строка, из которой требуется получить алиас.
		:type string: str
		:return: Алиас или `None` в случае неудачи или отсутствия имплементации.
		:rtype: str | None
		"""

		return string

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _TempImage(self, url: str, force_mode: bool = False) -> ImageDownloadingResult:
		"""
		Скачивает изображение по ссылке и сохраняет во временный каталог парсера.

		:param url: Ссылка на изображение.
		:type url: str
		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		return self._ImagesDownloader.temp_image(url, force_mode = force_mode)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, entry_point: "BaseEntryPoint"):
		"""
		Базовый оператор источника.

		:param entry_point: Точка входа в парсер.
		:type entry_point: BaseEntryPoint
		"""

		self._EntryPoint = entry_point

		self._SystemObjects = entry_point.system_objects
		self._Temper = self._SystemObjects.temper

		self._Settings = entry_point.settings
		self._Manifest = entry_point.manifest

		self._Requestor = self._InitializeRequestor()
		self._ImagesDownloader = ImagesDownloader(self)

		self._PostInitMethod()

	def collect_slugs(self, period: int | None = None, filters: str | None = None, pages: int | None = None) -> tuple[str, ...]:
		"""
		Собирает список алиасов тайтлов по заданным параметрам.

		:param period: Количество часов до текущего момента, составляющее период получения данных.
		:type period: int | None
		:param filters: Строка, описывающая параметры фильтрации.
		:type filters: str | None
		:param pages: Количество запрашиваемых страниц каталога.
		:type pages: int | None
		:return: Набор собранных алиасов.
		:rtype: tuple[str, ...]
		"""

		return tuple(self._CollectSlugs(period, filters, pages))
	
	def download_image(self, url: str, directory: str | PathLike[str] | None = None, filename: str | None = None, is_full_filename: bool = False, force_mode: bool = False) -> ImageDownloadingResult:
		"""
		Скачивает изображение.

		:param url: Ссылка на изображение.
		:type url: str
		:param directory: Путь к каталогу, в который нужно сохранить файл. По умолчанию будет использован временный каталог парсера.
		:type directory: str | PathLike[str] | None
		:param filename: Имя файла. По умолчанию будет сгенерировано на основе URL.
		:type filename: str | None
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		url = Validator_URL.parse(url)
		ImageTargetPath = self._ImagesDownloader.build_target_path(url, directory, filename, is_full_filename)
		
		if ImageTargetPath.exists() and not force_mode:
			return ImageDownloadingResult(
				is_already_exists = True,
				is_downloaded = False,
				is_replaced_by_stub = False,
				resolution = None,
				path = ImageTargetPath,
				error_message = None
			)

		Result = self._TempImage(url, force_mode)
		if Result.error_message or not Result.path:
			return Result
		
		if directory:
			self._ImagesDownloader.move_from_temp(directory, Result.path.name, filename, is_full_filename, force_mode)
		else:
			Result.path.replace(ImageTargetPath)
		
		return ImageDownloadingResult(
			is_already_exists = False,
			is_downloaded = True,
			is_replaced_by_stub = Result.is_replaced_by_stub,
			resolution = Result.resolution,
			path = ImageTargetPath,
			error_message = None
		)

	def get_content_type_by_slug(self, slug: str) -> ContentTypes:
		"""
		Определяет тип контента по алиасу тайтла.

		:param slug: Алиас тайтла.
		:type slug: str
		:return: Тип контента.
		:rtype: ContentTypes
		"""

		# To-Do: метод для определения типа контента по алиасу.
		return self._Manifest.content_types[0]

	def launch_parser(self, content_type: ContentTypes | None = None) -> "BaseParser":
		"""
		Инициализирует парсер для контента определённого типа.

		:param content_type: Тип контента. По умолчанию берётся первый описанный.
		:type content_type: ContentTypes | None
		:raises UnsupportedContent: Неподдерживаемый тип контента.
		:return: Парсер.
		:rtype: BaseParser
		"""

		if not content_type:
			content_type = self._Manifest.content_types[0]
		elif content_type not in self._Manifest.content_types:
			raise Exceptions.Parsers.UnsupportedContent(content_type)

		Module = importlib.import_module(f"Parsers.{self._Manifest.parser_name}.{content_type.value}")
		Parser: "BaseParser" = Module.Parser(self)

		return Parser

	def parse_slug_from_string(self, string: str) -> str | None:
		"""
		Парсит алиас тайтла из переданной строки. Может использоваться для обработки тайтлов по ссылкам.

		:param string: Строка, из которой требуется получить алиас.
		:type string: str
		:return: Алиас или `None` в случае неудачи или отсутствия имплементации.
		:rtype: str | None
		"""

		return self._ParseSlugFromString(string)