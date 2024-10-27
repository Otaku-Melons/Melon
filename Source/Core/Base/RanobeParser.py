from Source.Core.Formats.Ranobe import Chapter, Branch, Ranobe
from Source.Core.SystemObjects import SystemObjects

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Methods.System import Clear

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = None
NAME = None
SITE = None
TYPE = Ranobe

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class RanobeParser:
	"""Базовый парсер ранобэ."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def title(self) -> Ranobe:
		"""Данные тайтла."""

		return self._Title

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PrintCollectingStatus(self, page: int | None):
		"""
		Выводит в консоль прогресс сбора коллекции из каталога.
			page – номер текущей страницы.
		"""

		Clear()
		page = f" titles on page {page}" if page else ""
		print(f"Collecting{page}...")

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		WebRequestorObject = WebRequestor(Config)
		
		if self._Settings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = self._Settings.proxy.host,
			port = self._Settings.proxy.port,
			login = self._Settings.proxy.login,
			password = self._Settings.proxy.password
		)

		return WebRequestorObject

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: SystemObjects, title: Ranobe | None = None):
		"""
		Базовый парсер манги.
			system_objects – коллекция системных объектов;\n
			title – данные тайтла.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._SystemObjects = system_objects
		self._Title = title

		self._Settings = self._SystemObjects.manager.get_parser_settings()
		self._Requestor = self._InitializeRequestor()

		self._PostInitMethod()

	def amend(self, branch: Branch, chapter: Chapter):
		"""
		Дополняет главу дайными о слайдах.
			branch – данные ветви;\n
			chapter – данные главы.
		"""

		pass

	def parse(self):
		"""Получает основные данные тайтла."""

		pass

	def set_title(self, title: Ranobe):
		"""
		Задаёт данные тайтла.
			title – данные тайтла.
		"""

		self._Title = title