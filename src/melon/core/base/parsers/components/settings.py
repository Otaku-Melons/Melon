import re
from collections import ChainMap
from pathlib import Path
from time import sleep
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, cast

from dublib.functions.data import Zerotify
from dublib.functions.filesystem import ReadJSON
from dublib.web_requestor import Proxy

if TYPE_CHECKING:
	from .....core.system_objects import SystemObjects

#==========================================================================================#
# >>>>> СТАНДАРТНЫЕ НАСТРОЙКИ <<<<< #
#==========================================================================================#

_BASE_SETTINGS = MappingProxyType({
	"directories": {
		"content": None,
		"images": None,
		"titles": None
	},
	"common": {
		"bad_image_stub": None,
		"pretty": True,
		"use_id_as_filename": False,
		"sizing_images": True,
		"retries": 1,
		"delay": 1.0
	},
	"filters": {
		"text_regexs": [],
		"text_strings": [],
		"image_min_height": None,
		"image_min_width": None,
		"image_max_height": None,
		"image_max_width": None
	},
	"proxies": [],
	"custom": {}
})

#==========================================================================================#
# >>>>> ВНУТРЕННИЕ СТРУКТУРЫ ДАННЫХ КАТЕГОРИЙ <<<<< #
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
		"""
		Фильтры текста.

		:param data: Словарь фильтров текста.
		:type data: dict
		"""

		self.__Regexs = []
		self.__Strings = []

		if "text_regexs" in data.keys() and type(data["text_regexs"]) is list: self.__Regexs = data["text_regexs"]
		if "text_strings" in data.keys() and type(data["text_strings"]) is list: self.__Strings = data["text_strings"]

	def clear(self, text: str) -> str:
		"""
		Очищает текст согласно фильтрам.

		:param text: Обрабатываемый текст.
		:type text: str
		:return: Обработанный текст.
		:rtype: str
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
		"""
		Фильтры изображений.

		:param data: Словарь фильтров изображений.
		:type data: dict
		"""

		self.__Data = data

		if "image_md5" not in self.__Data.keys() or type(self.__Data["image_md5"]) is not list: self.__Data["image_md5"] = []
		Keys = ["image_min_height", "image_min_width", "image_max_height", "image_max_width"]

		for Key in Keys:
			if Key not in self.__Data.keys() or type(self.__Data[Key]) is not int: self.__Data[Key] = None

	def check_sizes(self, width: int, height: int) -> bool:
		"""
		Проверяет, выходит ли размер изображения за пределы разрешённых значений.

		:param width: Ширина изображения.
		:type width: int
		:param height: Высота изображения.
		:type height: int
		:return: Возвращает `True` при превышении одного из размеров.
		:rtype: bool
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

class Directories:
	"""Директории."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def content(self) -> Path:
		"""Путь к директории контента."""

		return self.__GetDirectory("content")
	
	@property
	def images(self) -> Path:
		"""Путь к директории изображений."""

		return self.__GetDirectory("images")
	
	@property
	def titles(self) -> Path:
		"""Путь к директории файлов тайтлов."""

		return self.__GetDirectory("titles")
	
	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetDirectory(self, dir_type: Literal["content", "images", "titles"]) -> Path:
		"""
		Возвращает путь к каталогу. Автоматически создаёт его при отсутствии.

		:param dir_type: Тип каталога.
		:type dir_type: Literal["content", "images", "titles"]
		:return: Путь к каталогу.
		:rtype: Path
		"""

		Directory: str | None = Zerotify(self.__DirectoriesDict.get(dir_type))
		
		DirectoryPath: Path = Path(Directory) if Directory else Path(f"{self.__SystemObjects.options.DEFAULT_OUTPUT_DIR}/{self.__ParserName}/{dir_type}")
		if Directory in (None, "Output"): DirectoryPath.mkdir(parents = True, exist_ok = True)

		return DirectoryPath

	def __init__(self, system_objects: "SystemObjects", parser_name: str, settings: dict[str, str | None]):
		"""
		Директории.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param parser_name: Имя парсера.
		:type parser_name: str
		:param settings: Словарь настроек парсера.
		:type settings: dict[str, Any]
		"""

		self.__SystemObjects: "SystemObjects" = system_objects
		self.__ParserName: str = parser_name
		self.__DirectoriesDict: dict[str, str | None] = settings or {}

class Common:
	"""Базовые настройки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bad_image_stub(self) -> Path | None:
		"""Путь к заглушке плохого изображения."""

		StubPath: Path | None = Path(self.__CommonSettings["bad_image_stub"]) if self.__CommonSettings["bad_image_stub"] else None

		return StubPath
	
	@property
	def delay(self) -> float:
		"""Интервал ожидания между последовательными запросами."""

		return self.__CommonSettings["delay"]

	@property
	def pretty(self) -> bool:
		"""Состояние: включено ли улучшение качества контента."""

		return self.__CommonSettings["pretty"]
	
	@property
	def retries(self) -> int:
		"""Количество повторов запроса при неудачном выполнении."""

		return self.__CommonSettings["retries"]
	
	@property
	def sizing_images(self) -> bool:
		"""Указывает, нужно ли пытаться определить размер изображений."""

		return self.__CommonSettings["sizing_images"]

	@property
	def use_id_as_filename(self) -> bool:
		"""Указывает, нужно ли использовать ID в качестве имени описательного файла."""

		return self.__CommonSettings["use_id_as_filename"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, settings: dict[str, Any]):
		"""
		Базовые настройки.

		:param settings: Словарь базовых настроек.
		:type settings: dict
		"""

		self.__CommonSettings: dict[str, Any] = cast(dict, _BASE_SETTINGS.copy().get("common")) | settings

	def sleep_delay(self):
		"""Приостанавливает исполнение на указанный в настройках интервал времени."""

		sleep(self.delay)

class Filters:
	"""Фильтры контента."""

	@property
	def text(self) -> TextFilters:
		"""Фильтры текста."""

		return self.__TextFilters
	
	@property
	def image(self) -> ImageFilters:
		"""Фильтры изображений."""

		return self.__ImageFilters

	def __init__(self, settings: dict):
		"""
		Фильтры контента.

		:param settings: Словарь настроек.
		:type settings: dict
		"""

		if "filters" not in settings.keys() or type(settings["filters"]) is not dict: settings["filters"] = {}
		self.__TextFilters = TextFilters(settings["filters"])
		self.__ImageFilters = ImageFilters(settings["filters"])

class Custom:
	"""Собственные настройки парсера."""

	def __init__(self, settings: dict[str, Any]):
		"""
		Собственные настройки парсера.

		:param settings: Словарь настроек парсера.
		:type settings: dict[str, Any]
		"""

		self.__CustomSettings: dict = settings.get("custom") or {}

	def __getitem__(self, key: str) -> Any:
		"""
		Возвращает значение настройки.

		:param key: Ключ настройки.
		:type key: str
		:return: Значение настройки.
		:rtype: Any
		:raises KeyError: Настройка не найдена.
		"""

		return self.__CustomSettings[key]

	def get(self, key: str, exception: bool = False) -> Any:
		"""
		Возвращает значение настройки.

		:param key: Ключ настройки.
		:type key: str
		:param exception: Указывает, нужно ли выбрасывать исключение типа `KeyError`.
		:type exception: bool
		:return: Значение настройки.
		:rtype: Any
		:raises KeyError: Настройка не найдена.
		"""

		if exception: 
			return self.__CustomSettings[key]

		return self.__CustomSettings.get(key)

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ParserSettings:
	"""Настройки парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	def is_loaded_from_repository(self) -> bool:
		"""Состояние: загружены ли настройки из репозитория."""

		return self.__IsLoadedFromRepository

	#==========================================================================================#
	# >>>>> КАТЕГОРИИ НАСТРОЕК <<<<< #
	#==========================================================================================#

	@property
	def directories(self) -> Directories:
		"""Пути к директориям."""

		return self.__Directories

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
	def proxies(self) -> tuple[Proxy, ...]:
		"""Набор прокси."""

		return self.__Proxies

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseProxies(self) -> tuple[Proxy, ...]:
		"""
		Парсит строковые представления прокси.

		:return: Набор объектов данных прокси.
		:rtype: tuple[Proxy, ...]
		"""

		Proxies = []

		if "proxies" in self.__Settings:
			for String in self.__Settings["proxies"]:
				Proxies.append(Proxy().parse(String))
			
		return tuple(Proxies)

	def __ReadSettings(self) -> dict:
		"""
		Считывает настройки парсера из JSON в порядке приоритета: сначала из каталога конфигураций, затем из домашнего каталога парсера.

		:return: Словарь настроек парсера. При отстутствии таковых возвращает стандартный набор.
		:rtype: dict
		"""

		Settings: dict = _BASE_SETTINGS.copy()
		ConfigsPaths: tuple[Path, Path] = (
			Path(f"parsers/{self.__ParserName}/settings.json"),
			Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{self.__ParserName}/settings.json")
		)

		for ConfigPath in ConfigsPaths:
			if ConfigPath.exists():
				Buffer: dict = ReadJSON(ConfigPath)
				Settings = {
					Key: dict(ChainMap(Buffer.get(Key, {}), Settings.get(Key, {})))
					for Key in set(Settings) | set(Buffer)
				}

		return Settings

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects", parser_name: str):
		"""
		Настройки парсера.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param parser_name: Имя парсера.
		:type parser_name: str
		"""
		
		self.__SystemObjects: "SystemObjects" = system_objects
		self.__ParserName: str = parser_name

		self.__Settings: dict = self.__ReadSettings()
		self.__IsLoadedFromRepository = False

		self.__Directories = Directories(self.__SystemObjects, self.__ParserName, self.__Settings.get("directories") or {})
		self.__Common: Common = Common(self.__Settings.get("common") or {})
		self.__Filters = Filters(self.__Settings)
		self.__Proxies: tuple[Proxy, ...] = self.__ParseProxies()
		self.__Custom: Custom = Custom(self.__Settings)