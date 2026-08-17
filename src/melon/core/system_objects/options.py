import os
import sys
from os import PathLike
from pathlib import Path

from dotenv import load_dotenv

from dublib.validators import Validator_Bool, Validator_URL

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class BoolOption:
	"""Опция, представляющая логическое значение."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_overrrided(self) -> bool:
		"""Состояние: переопределено ли значение переменной среды."""

		return self.__IsOverrided

	@property
	def value(self) -> bool:
		"""Значение."""

		return self.__Value

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, value: bool, is_overrided: bool = True):
		"""
		Опция, представляющая логическое значение.

		:param value: Значенние опции.
		:type value: bool
		:param is_overrided: Указывает, переопределено ли значение переменной среды.
		:type is_overrided: bool
		"""

		self.__Value: bool = value
		self.__IsOverrided: bool = is_overrided

	def __bool__(self) -> bool:
		"""
		Возвращает логическое представление объекта.

		:return: Логическое представление объекта.
		:rtype: bool
		"""

		return self.__Value

	def __str__(self) -> str:
		"""
		Возвращает строковое представление объекта.

		:return: Строковое представление объекта.
		:rtype: str
		"""

		return str(self.__Value)

class LinkOption:
	"""Опция, представляющая URL."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_overrrided(self) -> bool:
		"""Состояние: переопределено ли значение переменной среды."""

		return self.__IsOverrided

	@property
	def value(self) -> str:
		"""Значение."""

		return self.__Link

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, link: str, is_overrided: bool = True):
		"""
		Опция, представляющая URL.

		:param link: Ссылка.
		:type link: str
		:param is_overrided: Указывает, переопределено ли значение переменной среды.
		:type is_overrided: bool
		"""

		self.__Link: str = link
		self.__IsOverrided: bool = is_overrided

	def __str__(self) -> str:
		"""
		Возвращает строковое представление объекта.

		:return: Строковое представление объекта.
		:rtype: str
		"""

		return self.__Link

class PathOption:
	"""Опция, представляющая путь."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_overrrided(self) -> bool:
		"""Состояние: переопределено ли значение переменной среды."""

		return self.__IsOverrided

	@property
	def value(self) -> Path:
		"""Значение."""

		return self.__Path

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str | PathLike[str], is_overrided: bool = True):
		"""
		Опция, представляющая путь.

		:param path: Путь в файловой системе.
		:type path: str | PathLike[str]
		:param is_overrided: Указывает, переопределено ли значение переменной среды.
		:type is_overrided: bool
		"""

		self.__Path: Path = Path(path)
		self.__IsOverrided: bool = is_overrided

	def __str__(self) -> str:
		"""
		Возвращает строковое представление объекта.

		:return: Строковое представление объекта.
		:rtype: str
		"""

		return self.__Path.as_posix()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Options:
	"""Менеджер переменных среды парсера."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def CONFIGS_DIR(self) -> PathOption:
		"""Путь к каталогу конфигураций парсеров."""

		return self.__Paths[sys._getframe(0).f_code.co_name]

	@property
	def DEBUG(self) -> BoolOption:
		"""Состояние: включен ли режим отладки."""

		return self.__Bools[sys._getframe(0).f_code.co_name]

	@property
	def DEFAULT_OUTPUT_DIR(self) -> PathOption:
		"""Путь к каталогу собранного контента."""

		return self.__Paths[sys._getframe(0).f_code.co_name]

	@property
	def REPOS_URL(self) -> LinkOption:
		"""URL репозитория Melon."""

		return self.__Links[sys._getframe(0).f_code.co_name]

	@property
	def TEMP_DIR(self) -> PathOption:
		"""Путь ко временному каталогу парсеров."""

		return self.__Paths[sys._getframe(0).f_code.co_name]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __LoadEnviromentBoolVariables(self):
		"""Загружает опции на основе переменных сред, представляющих логические значения."""

		for Name in self.__Bools.keys():
			Value: str | None = os.environ.get(f"MELON_{Name}")
			if Value: self.__Bools[Name] = BoolOption(self.__StringToBool(Value))

	def __LoadEnviromentLinkVariables(self):
		"""Загружает опции на основе переменных сред, представляющих URL."""

		for Name in self.__Links.keys():
			Value: str | None = os.environ.get(f"MELON_{Name}")
			if Value: self.__Links[Name] = LinkOption(Validator_URL.parse(Value))

	def __LoadEnviromentPathVariables(self):
		"""Загружает опции на основе переменных сред, представляющих пути, и создаёт каталоги."""

		for Name in self.__Paths.keys():
			Value: str | None = os.environ.get(f"MELON_{Name}")
			if Value: self.__Paths[Name] = PathOption(Value)
			else: self.__Paths[Name].value.mkdir(exist_ok = True)

	def __LoadEnviromentVariables(self):
		"""Загружает и парсит переменные среды."""

		load_dotenv()
		self.__LoadEnviromentBoolVariables()
		self.__LoadEnviromentLinkVariables()
		self.__LoadEnviromentPathVariables()
		
	def __StringToBool(self, data: str) -> bool:
		"""
		Преобразует строку в `bool` по правилам логических опций.

		:param data: Обрабатываемая строка.
		:type data: str
		:return: Результат преобразования.
		:rtype: bool
		:raises ValueError: Некорректное значение переменной среды.
		"""

		if Validator_Bool.validate(data):
			return Validator_Bool.convert(data)

		if data.isdigit():
			return bool(int(data))

		raise ValueError("Incorrect enviroment variable value.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер переменных среды парсера."""

		self.__Bools: dict[str, BoolOption] = {
			"DEBUG": BoolOption(False, is_overrided = False)
		}
		self.__Links: dict[str, LinkOption] = {
			"REPOS_URL": LinkOption("https://github.com/otaku-melons/melon", is_overrided = False)
		}
		self.__Paths: dict[str, PathOption] = {
			"CONFIGS_DIR": PathOption("configs", is_overrided = False),
			"DEFAULT_OUTPUT_DIR": PathOption("output", is_overrided = False),
			"TEMP_DIR": PathOption("temp", is_overrided = False)
		}

		self.__LoadEnviromentVariables()