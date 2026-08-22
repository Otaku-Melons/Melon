import re
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal

from deepmerge import always_merger

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
		"image_max_width": None,
		"image_min_size": 100
	},
	"proxies": [],
	"custom": {},
	"extensions": {}
})

#==========================================================================================#
# >>>>> ВНУТРЕННИЕ СТРУКТУРЫ ДАННЫХ КАТЕГОРИЙ <<<<< #
#==========================================================================================#

class BaseExtensionOptions:
	"""Базовые настройки расширения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_enabled(self) -> bool:
		"""Состояние: включено ли расширение."""

		return bool(self._Data["is_enabled"])

	@property
	def options(self) -> dict[str, Any]:
		"""Копия словаря опций расширения."""

		return self._Options.copy()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, data: dict | None = None):
		"""
		Настройки расширения.

		:param data: Словарь настроек расширения.
		:type data: dict | None
		"""

		if data is None: data = {}
		
		self._Data: dict = {
			"is_enabled": False,
			"options": {}
		} | data
		self._Options: dict = self._Data["options"]

	def get(self, option: str, exception: bool = False) -> Any:
		"""
		Возвращает значение опции расширения.

		:param option: Имя опции.
		:type option: str
		:param exception: Указывает, выбрасывать ли исключение при отсутствии запрашиваемой опции.
		:type exception: bool
		:raises KeyError: Запрашиваемая опция не найдена.
		:return: Значение опции или `None` при её отсутствии.
		:rtype: Any
		"""

		if option not in self._Options:
			if exception: raise KeyError(option)
			else: return None

		return self._Options[option]

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
	def min_size(self) -> int:
		"""Минимальный размер изображения в байтах."""

		return self.__Data["image_min_size"] or 0

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

		self.__Data = {
			"image_min_height": None,
			"image_min_width": None,
			"image_max_height": None,
			"image_max_width": None,
			"image_min_size": 100
		} | data

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
		if Directory in (None, "output"): DirectoryPath.mkdir(parents = True, exist_ok = True)

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

	def __init__(self, settings: dict[str, Any]):
		"""
		Базовые настройки.

		:param settings: Словарь базовых настроек.
		:type settings: dict
		"""

		self.__CommonSettings: dict[str, Any] = settings

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

		:param settings: Словарь собственных настроек парсера.
		:type settings: dict[str, Any]
		"""

		self.__CustomSettings: dict = settings

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

class Extensions:
	"""Настройки расширений."""

	def __init__(self, settings: dict[str, Any]):
		"""
		Настройки расширений.

		:param settings: Словарь настроек расширений.
		:type settings: dict[str, Any]
		"""

		self.__ExtensionsSettings: dict[str, dict] = settings

	def get[T: BaseExtensionOptions](self, extension_name: str, container: type[T]) -> T:
		"""
		Возвращает упакованные в контейнер опции расширения.

		:param extension_name: Имя расширения.
		:type extension_name: str
		:param container: Тип-контейнер, принимающий `dict | None` и представляющий в дальнейшем интерфейсы доступа к опциям. Наследуется от `BaseExtensionOptions`.
		:type container: type
		:return: Контейнер с опциями расширения.
		:rtype: BaseExtensionOptions
		"""
		
		return container(self.__ExtensionsSettings.get(extension_name))

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ParserSettings:
	"""Настройки парсера."""

	#==========================================================================================#
	# >>>>> КАТЕГОРИИ НАСТРОЕК <<<<< #
	#==========================================================================================#

	@property
	def common(self) -> Common:
		"""Базовые настройки."""

		return self.__Common

	@property
	def directories(self) -> Directories:
		"""Пути к директориям."""

		return self.__Directories

	@property
	def extensions(self) -> Extensions:
		"""Настройки расширений."""

		return self.__Extensions

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

		Settings: dict = self.get_base_settings(self.__SystemObjects, self.__ParserName)
		ConfigsPaths: tuple[Path, Path] = (
			Path(f"parsers/{self.__ParserName}/settings.json"),
			Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{self.__ParserName}.json")
		)

		for ConfigPath in ConfigsPaths:
			if ConfigPath.exists():
				Buffer: dict = ReadJSON(ConfigPath)
				Settings = always_merger.merge(Settings, Buffer)

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

		self.__Directories = Directories(self.__SystemObjects, self.__ParserName, self.__Settings.get("directories", {}))
		self.__Common: Common = Common(self.__Settings.get("common", {}))
		self.__Filters = Filters(self.__Settings)
		self.__Proxies: tuple[Proxy, ...] = self.__ParseProxies()
		self.__Custom: Custom = Custom(self.__Settings.get("custom", {}))
		self.__Extensions: Extensions = Extensions(self.__Settings.get("extensions", {}))

	@staticmethod
	def get_base_settings(system_objects: "SystemObjects", parser_name: str) -> dict:
		"""
		Возвращает словарь базовых настроек. Автоматически создаёт для каждого расширения секцию.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Словарь базовых настроек.
		:rtype: dict
		"""

		BaseSetings: dict = _BASE_SETTINGS.copy()
		Extensions: tuple[str, ...] = system_objects.parsers_manager.get_extensions_names(parser_name)

		for ExtensionName in Extensions:
			BaseSetings["extensions"][ExtensionName] = {
				"is_enabled": False,
				"options": {}
			}

		return BaseSetings