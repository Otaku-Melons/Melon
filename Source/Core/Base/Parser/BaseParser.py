from Source.Core.Base.Parser.Components.ImagesDownloader import ImagesDownloader
from Source.Core.Base.Parser.Components.ParserSettings import ParserSettings
from Source.Core.Formats import BaseChapter, BaseBranch, BaseTitle
from Source.Core.SystemObjects import SystemObjects

from dublib.WebRequestor import WebConfig, WebLibs, WebRequestor
from dublib.Engine.Bus import ExecutionStatus
	
#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

NAME = None
SITE = None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BaseParser:
	"""Базовый парсер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def images_downloader(self) -> ImagesDownloader:
		"""Оператор скачивания изображений."""

		return self._ImagesDownloader

	@property
	def settings(self) -> ParserSettings:
		"""Настройки парсера."""

		return self._Settings

	@property
	def title(self) -> BaseTitle:
		"""Данные тайтла."""

		return self._Title

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		Site = self._SystemObjects.manager.get_parser_site()

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_retries_count(self._Settings.common.retries)
		Config.generate_user_agent()
		Config.add_header("Referer", f"https://{Site}/")
		Config.enable_proxy_protocol_switching(True)
		WebRequestorObject = WebRequestor(Config)
		WebRequestorObject.add_proxies(self._Settings.proxies)
		
		return WebRequestorObject

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects, title: BaseTitle | None = None):
		"""
		Базовый парсер.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		self._SystemObjects = system_objects
		self._Title = title

		self._Temper = self._SystemObjects.temper
		self._Portals = self._SystemObjects.logger.portals
		self._Settings = self._SystemObjects.manager.parser_settings

		self._Requestor = self._InitializeRequestor()
		self._ImagesDownloader = ImagesDownloader(self._SystemObjects, self._Requestor)

		self._PostInitMethod()

	def amend(self, branch: BaseBranch, chapter: BaseChapter):
		"""
		Дополняет главу дайными о слайдах.
			branch – данные ветви;\n
			chapter – данные главы.
		"""

		pass

	def image(self, url: str) -> ExecutionStatus:
		"""
		Скачивает изображение с сайта во временный каталог парсера и возвращает имя файла.
			url – ссылка на изображение.
		"""
		
		return ImagesDownloader(self._SystemObjects, self._Requestor).temp_image(url)

	def parse(self):
		"""Получает основные данные тайтла."""

		pass

	def set_title(self, title: BaseTitle):
		"""
		Задаёт данные тайтла.
			title – данные тайтла.
		"""

		self._Title = title