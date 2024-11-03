from Source.Core.SystemObjects.Logger import Logger
from Source.Core.Exceptions import BadSettings

from dublib.Methods.Filesystem import NormalizePath
from dublib.Methods.JSON import ReadJSON
from dublib.Methods.Data import Zerotify

import os
import re

#==========================================================================================#
# >>>>> СТАНДАРТНЫЕ НАСТРОЙКИ <<<<< #
#==========================================================================================#

Settings = {
	"common": {
		"archives_directory": "",
		"covers_directory": "",
		"images_directory": "",
		"titles_directory": "",
		"bad_image_stub": "",
		"pretty": True,
		"use_id_as_filename": False,
		"sizing_images": False,
		"legacy": False,
		"retries": 1,
		"delay": 1
	},
	"filters": {
		"text_regexs": [],
		"text_strings": [],
		"image_md5": [],
		"image_min_height": None,
		"image_min_width": None,
		"image_max_height": None,
		"image_max_width": None
	},
	"proxy": {
		"enable": False,
		"host": "",
		"port": "",
		"login": "",
		"password": ""
	},
	"custom": {
		"token": "",
		"unstub": False,
		"add_free_publication_date": False
	}
}

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class TextFilters:
	"""Фильтры текста."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def regexs(self) -> list[str]:
		"""Список регулярных выражений фильтрации."""

		return self.__Regexs
	
	@property
	def strings(self) -> list[str]:
		"""Список удаляемых строк."""

		return self.__Strings

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, data: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Regexs = list()
		self.__Strings = list()

		if "text_regexs" in data.keys() and type(data["text_regexs"]) == list: self.__Regexs = data["text_regexs"]
		if "text_strings" in data.keys() and type(data["text_strings"]) == list: self.__Strings = data["text_strings"]

	def clear(self, text: str) -> str:
		"""
		Очищает текст согласно фильтрам.
			text – текст.
		"""

		for Regex in self.__Regexs: text = re.sub(Regex, "", text)
		for String in self.__Strings: text = text.replace(String, "")

		return text

class ImageFilters:
	"""Фильтры изображений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def md5(self) -> list[str]:
		"""Список MD5-хэшей нежелательных изображений."""

		return self.__Data["image_md5"]

	@property
	def min_height(self) -> int | None:
		"""Минимальная высота изображения."""

		return self.__Data["image_min_height"]
	
	@property
	def min_width(self) -> int | None:
		"""Минимальная ширина изображения."""

		return self.__Data["image_min_width"]
	
	@property
	def max_height(self) -> int | None:
		"""Максимальная высота изображения."""

		return self.__Data["image_max_height"]
	
	@property
	def max_width(self) -> int | None:
		"""Максимальная ширина изображения."""

		return self.__Data["image_max_width"]
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, data: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Data = dict()

		if "image_md5" not in self.__Data.keys() or type(self.__Data["image_md5"]) != list: self.__Data["image_md5"] = list()
		Keys = ["image_min_height", "image_min_width", "image_max_height", "image_max_width"]

		for Key in Keys:
			if Key not in self.__Data.keys() or type(self.__Data[Key]) != int: self.__Data[Key] = None

	def check_sizes(self, width: int, height: int) -> bool:
		"""
		Проверяет, выходит ли размер изображения за пределы разрешённых значений.
			width – ширина;\n
			height – высота.
		"""

		IsFiltered = False

		if self.min_width and width < self.min_width: IsFiltered = True
		if self.min_height and height < self.min_height: IsFiltered = True
		if self.max_width and height > self.max_width: IsFiltered = True
		if self.max_height and height > self.max_height: IsFiltered = True

		return IsFiltered

#==========================================================================================#
# >>>>> КАТЕГОРИИ НАСТРОЕК <<<<< #
#==========================================================================================#

class Common:
	"""Базовые настройки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def archives_directory(self) -> str:
		"""Директория читаемого контента."""

		return self.__Settings["archives_directory"]
	
	@property
	def bad_image_stub(self) -> str | None:
		"""Путь к заглушке плохого изображения."""

		return self.__Settings["bad_image_stub"]
	
	@property
	def covers_directory(self) -> str:
		"""Директория обложек."""

		return self.__Settings["covers_directory"]
	
	@property
	def images_directory(self) -> str:
		"""Директория изображений."""

		return self.__Settings["images_directory"]
	
	@property
	def titles_directory(self) -> str:
		"""Директория описательных файлов."""

		return self.__Settings["titles_directory"]
	
	@property
	def use_id_as_filename(self) -> bool:
		"""Указывает, нужно ли использовать ID в качестве имени описательного файла."""

		return self.__Settings["use_id_as_filename"]
	
	@property
	def sizing_images(self) -> bool:
		"""Указывает, нужно ли пытаться определить размер изображений."""

		return self.__Settings["sizing_images"]
	
	@property
	def pretty(self) -> bool:
		"""Состояние: включено ли улучшение качества контента."""

		return self.__Settings["pretty"]
	
	@property
	def retries(self) -> int:
		"""Количество повторов запроса при неудачном выполнении."""

		return self.__Settings["retries"]
	
	@property
	def delay(self) -> float:
		"""Интервал ожидания между последовательными запросами."""

		return self.__Settings["delay"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __PutDefaultDirectories(self, parser_name: str):
		"""
		Подстанавливает стандартные директории на пустые места.
			parser_name – название парсера.
		"""

		Directories = ["archives", "covers", "images", "titles"]

		for Directory in Directories:
			Key = f"{Directory}_directory"
			if not self.__Settings[Key]: self.__Settings[Key] = f"Output/{parser_name}/{Directory}"
			else: self.__Settings[Key] = NormalizePath(self.__Settings[Key])

	def __init__(self, parser_name: str, settings: dict, logger: Logger):
		"""
		Базовые настройки.
			parser_name – название парсера;\n
			settings – словарь настроек;\n
			logger – менеджер логов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Settings = {
			"archives_directory": "",
			"covers_directory": "",
			"images_directory": "",
			"titles_directory": "",
			"bad_image_stub": None,
			"pretty": False,
			"use_id_as_filename": False,
			"sizing_images": False,
			"retries": 0,
			"delay": 1.0
		}

		if "common" in settings.keys():
			if "delay" in settings["common"].keys(): settings["common"]["delay"] = float(settings["common"]["delay"])
			
			for Key in self.__Settings.keys():
				if Key in settings["common"].keys(): self.__Settings[Key] = settings["common"][Key]
				else: logger.warning(f"Setting \"{Key}\" has been reset to default.")

			if self.__Settings["bad_image_stub"] != None:
				BadImageStub = NormalizePath(self.__Settings["bad_image_stub"])
				if not os.path.exists(BadImageStub): self.__Settings["bad_image_stub"] = None
				else: self.__Settings["bad_image_stub"] = BadImageStub

			elif not self.__Settings["bad_image_stub"]: self.__Settings["bad_image_stub"] = None

			self.__PutDefaultDirectories(parser_name)

		else: raise BadSettings(parser_name)

class Filters:
	"""Фильтры контента."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def text(self) -> TextFilters:
		"""Фильтры текста."""

		return self.__TextFilters
	
	@property
	def image(self) -> ImageFilters:
		"""Фильтры изображений."""

		return self.__ImageFilters
	
	def __init__(self, settings: dict):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		if "filters" not in settings.keys() or type(settings["filters"]) != dict: settings["filters"] = dict()
		self.__TextFilters = TextFilters(settings["filters"])
		self.__ImageFilters = ImageFilters(settings["filters"])

class Proxy:
	"""Настройки прокси."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def enable(self) -> bool:
		"""Указывает, нужно ли использовать прокси."""

		return self.__Settings["enable"]
	
	@property
	def host(self) -> str:
		"""Хост."""

		return self.__Settings["host"]
	
	@property
	def port(self) -> int:
		"""Порт."""

		return self.__Settings["port"]
	
	@property
	def login(self) -> str | None:
		"""Логин для авторизации прокси."""

		return Zerotify(self.__Settings["login"])
	
	@property
	def password(self) -> str | None:
		"""Пароль для авторизации прокси."""

		return Zerotify(self.__Settings["password"])

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict, logger: Logger):
		"""
		Настройки прокси.
			settings – словарь настроек;\n
			logger – менеджер логов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Settings = {
			"enable": False,
			"host": "",
			"port": 0,
			"login": "",
			"password": ""
		}

		if "proxy" in settings.keys():
			if "port" in settings["proxy"].keys(): settings["proxy"]["port"] = int(settings["proxy"]["port"]) if settings["proxy"]["port"] else 0

			for Key in self.__Settings.keys():
				if Key in settings["proxy"].keys() and type(self.__Settings[Key]) == type(settings["proxy"][Key]): self.__Settings[Key] = settings["proxy"][Key]
				else: logger.warning(f"Proxy setting \"{Key}\" has been reset to default.")

class Custom:
	"""Собственные настройки парсера."""

	def __init__(self, settings: dict, logger: Logger):
		"""
		Настройки прокси.
			settings – словарь настроек;\n
			logger – менеджер логов.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Settings = settings["custom"] if "custom" in settings.keys() else dict()
		self.__Logger = logger

	def __getitem__(self, key: str) -> any:
		"""
		Возвращает значение настройки.
			key – ключ настройки.
		"""

		if key not in self.__Settings.keys(): self.__Logger.warning(f"No custom setting: \"{key}\".")
		
		return self.__Settings[key]

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ParserSettings:
	"""Настройки парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def common(self) -> Common:
		"""Базовые настройки."""

		return self.__Common
	
	@property
	def filters(self) -> Filters:
		"""Фильтры контента."""

		return self.__Filters

	@property
	def custom(self) -> Custom:
		"""Собственные настройки парсера."""

		return self.__Custom
	
	@property
	def proxy(self) -> Proxy:
		"""Данные прокси."""

		return self.__Proxy

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadSettings(self, parser_name: str) -> dict:
		"""
		Считывает настройки в порядке приоритета.
			parser_name – название парсера.
		"""

		ParserSettingsDict = None
		Paths = [
			f"Configs/{parser_name}/settings.json",
			f"Parsers/{parser_name}/settings.json"
		]

		for Path in Paths:

			if os.path.exists(Path):
				ParserSettingsDict = ReadJSON(Path)
				break

		if not ParserSettingsDict:
			self.__Logger.warning("Settings dropped to default values.")
			ParserSettingsDict = Settings.copy()

		return ParserSettingsDict

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, parser_name: str, logger: Logger):
		"""
		Настройки парсера.
			parser_name – название парсера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Logger = logger
		self.__Settings = self.__ReadSettings(parser_name)
		self.__Common = Common(parser_name, self.__Settings, logger)
		self.__Filters = Filters(self.__Settings)
		self.__Proxy = Proxy(self.__Settings, logger)
		self.__Custom = Custom(self.__Settings, logger)

	def __getitem__(self, category: str) -> dict:
		"""
		Возвращает словарь категории настроек.
			category – название категории.
		"""

		if category not in self.__Settings.keys(): self.__Logger.warning(f"No settings category: \"{category}\".")
		
		return self.__Settings[category].copy()