from Source.Core.Formats.Manga import BaseStructs, Manga, Statuses, Types
from Source.Core.ParserSettings import ParserSettings
from Source.Core.SystemObjects import Objects

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = None
NAME = None
SITE = None
STRUCT = Manga(NAME)

#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class MangaParser:
	"""Базовый парсер манги."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def site(self) -> str:
		"""Домен целевого сайта."""

		return self._Title["site"]

	@property
	def id(self) -> int:
		"""Целочисленный идентификатор."""

		return self._Title["id"]

	@property
	def slug(self) -> int:
		"""Алиас."""

		return self._Title["slug"]

	@property
	def content_language(self) -> str | None:
		"""Код языка контента по стандарту ISO 639-3."""

		return self._Title["content_language"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Title["localized_name"]

	@property
	def en_name(self) -> str | None:
		"""Название на английском."""

		return self._Title["en_name"]

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self._Title["another_names"]

	@property
	def covers(self) -> list[dict]:
		"""Список описаний обложки."""

		return self._Title["covers"]

	@property
	def authors(self) -> list[str]:
		"""Список авторов."""

		return self._Title["authors"]

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return self._Title["publication_year"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self._Title["description"]

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return self._Title["age_limit"]

	@property
	def genres(self) -> list[str]:
		"""Список жанров."""

		return self._Title["genres"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return self._Title["tags"]

	@property
	def franchises(self) -> list[str]:
		"""Список франшиз."""

		return self._Title["franchises"]

	@property
	def type(self) -> Types | None:
		"""Тип тайтла."""

		return self._Title["type"]

	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return self._Title["status"]

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return self._Title["is_licensed"]

	@property
	def content(self) -> dict:
		"""Содержимое тайтла."""

		return self._Title["content"]

	#==========================================================================================#
	# >>>>> ВСПОМОГАТЕЛЬНЫЕ НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _CalculateEmptyChapters(self, content: dict) -> int:
		"""
		Подсчитывает количество глав без слайдов.
			content – контент тайтла.
		"""

		EmptyChaptersCount = 0

		for BranchID in content.keys():

			for Chapter in content[BranchID]:
				if not Chapter["slides"]: EmptyChaptersCount += 1

		return EmptyChaptersCount

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		WebRequestorObject = WebRequestor(Config)
		
		if self.__Settings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = self.__Settings.proxy.host,
			port = self.__Settings.proxy.port,
			login = self.__Settings.proxy.login,
			password = self.__Settings.proxy.password
		)

		return WebRequestorObject

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: Objects, settings: ParserSettings):
		"""
		Базовый парсер манги.
			system_objects – коллекция системных объектов;\n
			settings – настройки парсера.
		"""

		system_objects.logger.select_parser(NAME)

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self._Settings = settings
		self._Requestor = self._InitializeRequestor()
		self._Title = None
		self._Slug = None
		self._SystemObjects = system_objects

	def amend(self, content: dict | None = None, message: str = "") -> dict:
		"""
		Дополняет каждую главу в кажой ветви информацией о содержимом.
			content – содержимое тайтла для дополнения;\n
			message – сообщение для портов CLI.
		"""

		pass

	def parse(self, slug: str, message: str = ""):
		"""
		Получает основные данные тайтла.
			slug – алиас тайтла, использующийся для идентификации оного в адресе;\n
			message – сообщение для портов CLI.
		"""

		pass