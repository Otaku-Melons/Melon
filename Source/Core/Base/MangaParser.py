from Source.Core.Formats.Manga import Chapter, Manga
from Source.Core.SystemObjects import SystemObjects

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = None
NAME = None
SITE = None
TYPE = Manga

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class MangaParser:
	"""Базовый парсер манги."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def title(self) -> Manga:
		"""Данные тайтла."""

		return self._Title

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _CalculateEmptyChapters(self) -> int:
		"""Подсчитывает количество глав без контента во всех ветвях."""

		EmptyChaptersCount = 0
		for Branch in self._Title.branches: EmptyChaptersCount += Branch.empty_chapters_count

		return EmptyChaptersCount

	def _FindChapterByID(self, chapter_id: int) -> Chapter | None:
		"""
		Возвращает главу с указанным ID.
			chapter_id – уникальный идентификатор главы.
		"""

		SearchResult = None

		for Branch in self._Title.branches:

			for CurrentChapter in Branch.chapters:

				if CurrentChapter.id == chapter_id:
					SearchResult = CurrentChapter
					break

		return SearchResult

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

	def __init__(self, system_objects: SystemObjects, title: Manga):
		"""
		Базовый парсер манги.
			system_objects – коллекция системных объектов;\n
			settings – настройки парсера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._SystemObjects = system_objects
		self._Title = title

		self._Settings = self._SystemObjects.manager.get_parser_settings()
		self._Requestor = self._InitializeRequestor()

		self._PostInitMethod()

	def amend(self, message: str = ""):
		"""
		Дополняет каждую главу в кажой ветви информацией о содержимом.
			message – сообщение для портов CLI.
		"""

		pass

	def parse(self):
		"""Получает основные данные тайтла."""

		pass