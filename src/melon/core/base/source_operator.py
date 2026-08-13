import importlib
from dataclasses import dataclass
from os import PathLike
from typing import TYPE_CHECKING, Sequence

from dulwich import errors, porcelain

from dublib.functions.filesystem import ReadJSON
from dublib.validators import Validator_Domain, Validator_URL
from dublib.web_requestor import WebConfig, WebLibs, WebRequestor

from ...core import exceptions
from ...core.base.parsers.components import ParserSettings
from ...core.base.parsers.components.images_downloader import (
	ImageDownloadingResult,
	ImagesDownloader,
)
from ...core.base.parsers.components.manifest import ContentTypes, ParserManifest

if TYPE_CHECKING:
	from ...core.base.parsers.base_parser import BaseParser
	from ...core.system_objects import SystemObjects
	from ...core.system_objects.printer import Portals
	from ...core.system_objects.temper import SharedData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class FileTypingResult:
	"""Результат определения типа файла тайтла."""

	slug: str
	content_type: ContentTypes

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseSourceOperator:
	"""Базовый оператор источника."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

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
	def parser_name(self) -> str:
		"""Имя парсера."""

		return self._Manifest.parser_name

	@property
	def parser_version(self) -> str | None:
		"""Версия парсера."""

		try:
			ParserTags = porcelain.tag_list(f"parsers/{self._Manifest.parser_name}")
		except errors.NotGitRepository:
			return None
		
		if ParserTags:
			return ParserTags[-1].decode().lstrip("v")
		
		return None

	@property
	def portals(self) -> "Portals":
		"""Порталы вывода парсера."""

		return self._Portals

	@property
	def requestor(self) -> WebRequestor:
		"""Менеджер запросов."""

		return self._Requestor

	@property
	def settings(self) -> ParserSettings:
		"""Настройки парсера."""

		return self._Settings
	
	@property
	def shared_data(self) -> "SharedData":
		"""Разделяемые в контексте сессий одного парсера данные."""
		
		return self._SharedData

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self._SystemObjects

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

		return ()

	def _InitializeRequestor(self) -> WebRequestor:
		"""
		Инициализирует модуль WEB-запросов.

		:return: Оператор запросов.
		:rtype: WebRequestor
		"""

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_retries_count(self._Settings.common.retries)
		Config.headers.generate_user_agent(("desktop",))
		Config.headers.automatically_accept_client_hints(True)
		Config.headers.add("referer", f"https://{self._Manifest.domain}/")
		Config.enable_proxy_protocol_switching(True)
		WebRequestorObject = WebRequestor(Config)
		WebRequestorObject.add_proxies(self._Settings.proxies)
		
		return WebRequestorObject

	def _IsTitleExists(self, slug: str) -> bool | None:
		"""
		Проверяет, существует ли тайтл на сервере.

		:param slug: Алиас тайтла.
		:type slug: str
		:return: Возвращает статус существования файла на сервере или `None` при невозможности проверки.
		:rtype: bool | None
		"""

		return None

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

	def _PostMirrorChanging(self, mirror: str | None):
		"""
		Выполняется после изменения зеркала.

		:param mirror: Домен зеркала.
		:type mirror: str | None
		"""

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

	def __init__(self, system_objects: "SystemObjects", manifest: "ParserManifest"):
		"""
		Базовый оператор источника.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param manifest: Манифест парсера.
		:type manifest: ParserManifest
		"""

		self._SystemObjects = system_objects
		self._Manifest = manifest

		self._Printer = self._SystemObjects.printer
		self._Temper = self._SystemObjects.temper
		
		self._Settings = ParserSettings(self._SystemObjects, self._Manifest.parser_name)
		self._Requestor = self._InitializeRequestor()
		self._ImagesDownloader = ImagesDownloader(self)
		self._Portals = self._SystemObjects.printer.get_parser_portals(self._Manifest.parser_name)
		self._SharedData = self._SystemObjects.temper.load_parser_shared_data(self._Manifest.parser_name)
		
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

	def get_content_type_by_file(self, filename: str) -> FileTypingResult:
		"""
		Определяет тип контента по файлу.

		:param filename: Имя файла с расширением или без него.
		:type filename: str
		:return: Результат определения типа файла тайтла.
		:rtype: FileTypingResult
		"""

		if not filename.endswith(".json"):
			filename += ".json"

		FilePath = self.settings.directories.titles / filename
		TitleData = ReadJSON(FilePath)
		Type: str = TitleData["format"]
		TypeName: str = Type.split("-")[1]
		
		return FileTypingResult(TitleData["slug"], ContentTypes(TypeName))

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

	def is_title_exists(self, slug: str) -> bool | None:
		"""
		Проверяет, существует ли тайтл на сервере.

		:param slug: Алиас тайтла.
		:type slug: str
		:return: Возвращает статус существования файла на сервере или `None` при невозможности проверки.
		:rtype: bool | None
		"""

		return self._IsTitleExists(slug)

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
			raise exceptions.parsers.UnsupportedContent(content_type)

		Module = importlib.import_module(f"parsers.{self._Manifest.parser_name}.{content_type.value}")
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

	def set_mirror(self, mirror: str | None) -> bool:
		"""
		Задаёт домен зеркала, подменяя его в манифесте. Не сохраняет изменения в файл.
		
		:param mirror: Домен зеркала.
		:type mirror: str | None
		:raises ValueError: Некорректный домен зеркала.
		:return: Возвращает `True`, если зеркало было изменено.
		:rtype: bool
		"""

		if mirror and not Validator_Domain.validate(mirror):
			raise ValueError("Incorrect mirror domain.")

		if mirror == self.manifest.original_domain or mirror == self.manifest.mirror:
			return False

		self.manifest.set_mirror(mirror)
		self.requestor.config.headers.set("referer", f"https://{self._Manifest.domain}/")
		self._PostMirrorChanging(mirror)

		return True