from dublib.WebRequestor import WebConfig, WebLibs, WebRequestor
from Source.Core.Formats.Manga import Statuses, Types
from dublib.Methods import ReadJSON

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = ""
NAME = ""

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Parser:
	"""Модульный парсер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def site(self) -> str:
		"""Домен целевого сайта."""

		return None

	@property
	def id(self) -> int:
		"""Целочисленный идентификатор."""

		return None

	@property
	def slug(self) -> int:
		"""Алиас."""

		return None

	@property
	def ru_name(self) -> str | None:
		"""Название на русском."""

		return None

	@property
	def en_name(self) -> str | None:
		"""Название на английском."""

		return None

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return None

	@property
	def covers(self) -> list[dict]:
		"""Список описаний обложки."""

		return None

	@property
	def authors(self) -> list[str]:
		"""Список авторов."""

		return None

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return None

	@property
	def description(self) -> str | None:
		"""Описание."""

		return None

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return None

	@property
	def genres(self) -> list[str]:
		"""Список жанров."""

		return None

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return None

	@property
	def franchises(self) -> list[str]:
		"""Список франшиз."""

		return None

	@property
	def type(self) -> Types | None:
		"""Тип тайтла."""

		return None

	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return None

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return None

	@property
	def content(self) -> dict:
		"""Содержимое тайтла."""

		return None

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		# Инициализация и настройка объекта.
		Config = WebConfig()
		Config.select_lib(WebLibs.curl_cffi)
		Config.generate_user_agent("pc")
		Config.curl_cffi.enable_http2(True)
		WebRequestorObject = WebRequestor(Config)

		return WebRequestorObject

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, slug: str, global_settings: dict):
		"""
		Модульный парсер.
			slug – алиас ресурса.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки парсера.
		self.__Settings = ReadJSON(f"Source/Parsers/{NAME}/settings.json")
		# Менеджер WEB-запросов.
		self.__Requestor = self.__InitializeRequestor()
		# Структура данных.
		self.__Title = None
		# Алиас тайтла.
		self.__Slug = None

	def amend(self, content: dict | None = None):
		"""
		Дополняет содержимое подробной информацией.
			content – содержимое тайтла для дополнения.
		"""

		# Если содержимое не указано, использовать текущее.
		if content == None: content = self.content
		
		# Скрипт дополнения содержимого...

		# Запись дополненного содержимого.
		self.__Title["content"] = content

	def parse(self, slug: str):
		"""
		Получает основные данные тайтла.
			slug – алиас ресурса.
		"""

		# Заполнение базовых данных.
		self.__Title = BaseStructs().manga
		self.__Slug = slug

		# Скрипт парсинга основных данных...

		pass