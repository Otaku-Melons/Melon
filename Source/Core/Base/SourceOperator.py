from Source.Core.Base.Parsers.Components.ImagesDownloader import ImageDownloadingResult, ImagesDownloader

from dublib.WebRequestor import WebConfig, WebLibs, WebRequestor
from dublib.CLI.Validators import Validator_URL

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .EntryPoint import BaseEntryPoint
	
	from Source.Core.Base.Parsers.Components import ParserManifest, ParserSettings
	from Source.Core.SystemObjects.Temper import SharedData
	from Source.Core.SystemObjects import SystemObjects

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
	def manifest(self) -> "ParserManifest":
		"""Манифест парсера."""

		return self._Manifest

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

		return None

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _TempImage(self, url: str) -> ImageDownloadingResult:
		"""
		Скачивает изображение по ссылке и сохраняет во временный каталог парсера.

		:param url: Ссылка на изображение.
		:type url: str
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		return self._ImagesDownloader.temp_image(url)

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
		self._Portals = self._SystemObjects.logger.portals

		self._Settings = entry_point.settings
		self._Manifest = entry_point.manifest

		self._Requestor = self._InitializeRequestor()
		self._ImagesDownloader = ImagesDownloader(self)

		self._PostInitMethod()

	def parse_slug_from_string(self, string: str) -> str | None:
		"""
		Парсит алиас тайтла из переданной строки. Может использоваться для обработки тайтлов по ссылкам.

		:param string: Строка, из которой требуется получить алиас.
		:type string: str
		:return: Алиас или `None` в случае неудачи или отсутствия имплементации.
		:rtype: str | None
		"""

		return self._ParseSlugFromString(string)

	def image(self, url: str) -> ImageDownloadingResult:
		"""
		Скачивает изображение по ссылке и сохраняет во временный каталог парсера.

		:param url: Ссылка на изображение.
		:type url: str
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		:raises ValidationError: Неверный формат ссылки.
		"""

		url = Validator_URL.parse(url)
		
		return self._TempImage(url)