from Source.CLI.Templates import *

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from Source.Core.Formats.Manga import Statuses, Types
from dublib.Methods import ReadJSON

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = ""
NAME = ""
SITE = ""
STRUCT = Manga()

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

		return self.__Title["site"]

	@property
	def id(self) -> int:
		"""Целочисленный идентификатор."""

		return self.__Title["id"]

	@property
	def slug(self) -> int:
		"""Алиас."""

		return self.__Title["slug"]

	@property
	def ru_name(self) -> str | None:
		"""Название на русском."""

		return self.__Title["ru_name"]

	@property
	def en_name(self) -> str | None:
		"""Название на английском."""

		return self.__Title["en_name"]

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Title["another_names"]

	@property
	def covers(self) -> list[dict]:
		"""Список описаний обложки."""

		return self.__Title["covers"]

	@property
	def authors(self) -> list[str]:
		"""Список авторов."""

		return self.__Title["authors"]

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return self.__Title["publication_year"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self.__Title["description"]

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return self.__Title["age_limit"]

	@property
	def genres(self) -> list[str]:
		"""Список жанров."""

		return self.__Title["genres"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return self.__Title["tags"]

	@property
	def franchises(self) -> list[str]:
		"""Список франшиз."""

		return self.__Title["franchises"]

	@property
	def type(self) -> Types | None:
		"""Тип тайтла."""

		return self.__Title["type"]

	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return self.__Title["status"]

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return self.__Title["is_licensed"]

	@property
	def content(self) -> dict:
		"""Содержимое тайтла."""

		return self.__Title["content"]

	#==========================================================================================#
	# >>>>> СТАНДАРТНЫЕ ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CalculateEmptyChapters(self, content: dict) -> int:
		"""Подсчитывает количество глав без слайдов."""

		# Количество глав.
		ChaptersCount = 0

		# Для каждой ветви.
		for BranchID in content.keys():

			# Для каждой главы.
			for Chapter in content[BranchID]:
				# Если глава не содержит слайдов, подсчитать её.
				if not Chapter["slides"]: ChaptersCount += 1

		return ChaptersCount

	def __InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		# Инициализация и настройка объекта.
		Config = WebConfig()
		Config.select_lib(WebLibs.curl_cffi)
		Config.generate_user_agent("pc")
		Config.curl_cffi.enable_http2(True)
		WebRequestorObject = WebRequestor(Config)
		# Установка прокси.
		if self.__Settings["proxy"]["enable"]: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = self.__Settings["proxy"]["host"],
			port = self.__Settings["proxy"]["port"],
			login = self.__Settings["proxy"]["login"],
			password = self.__Settings["proxy"]["password"]
		)

		return WebRequestorObject

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	# В разработке...

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: Objects):
		"""
		Модульный парсер.
			system_objects – коллекция системных объектов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки парсера.
		self.__Settings = ReadJSON(f"Parsers/{NAME}/settings.json")
		# Менеджер WEB-запросов.
		self.__Requestor = self.__InitializeRequestor()
		# Структура данных.
		self.__Title = None
		# Алиас тайтла.
		self.__Slug = None
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects

		# Выбор парсера для системы логгирования.
		self.__SystemObjects.logger.select_parser(NAME)

	def amend(self, content: dict | None = None, message: str = "") -> dict:
		"""
		Дополняет каждую главу в кажой ветви информацией о содержимом.
			content – содержимое тайтла для дополнения;
			message – сообщение для портов CLI.
		"""

		# Если содержимое не указано, использовать текущее.
		if content == None: content = self.content
		# Подсчёт количества глав для дополнения.
		ChaptersToAmendCount = self.__CalculateEmptyChapters(content)
		# Количество дополненных глав.
		AmendedChaptersCount = 0
		# Индекс прогресса.
		ProgressIndex = 0
		
		# Скрипт дополнения содержимого...

		# Запись дополненного содержимого.
		self.__Title["content"] = content

	def parse(self, slug: str, message: str = ""):
		"""
		Получает основные данные тайтла.
			slug – алиас тайтла, использующийся для идентификации оного в адресе;
			message – сообщение для портов CLI.
		"""

		# Заполнение базовых данных.
		self.__Title = BaseStructs().manga
		self.__Slug = slug
		# Вывод в лог: статус парсинга.
		PrintStatus(message)

		# Скрипт парсинга основных данных...