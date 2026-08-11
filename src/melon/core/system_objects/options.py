import os
import sys
from os import PathLike
from pathlib import Path

from dotenv import load_dotenv

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

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
		"""Путь."""

		return self.__Path

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str | PathLike[str], is_overrided: bool = True):
		"""
		Опция, представляющая путь.

		:param path: Путь в файловой системе.
		:type path: str | PathLike[str]
		:param is_default: Указывает, переопределено ли значение переменной среды.
		:type is_default: bool
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
	# >>>>> СВОЙСТВА ПУТЕЙ <<<<< #
	#==========================================================================================#

	@property
	def CONFIGS_DIR(self) -> PathOption:
		"""Путь к каталогу конфигураций парсеров."""

		return self.__Paths[sys._getframe(0).f_code.co_name]

	@property
	def DEFAULT_OUTPUT_DIR(self) -> PathOption:
		"""Путь к каталогу собранного контента."""

		return self.__Paths[sys._getframe(0).f_code.co_name]

	@property
	def TEMP_DIR(self) -> PathOption:
		"""Путь ко временному каталогу парсеров."""

		return self.__Paths[sys._getframe(0).f_code.co_name]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __LoadEnviromentPathVariables(self):
		"""Загружает опции на основе переменных сред, представляющих пути, и создаёт каталоги."""

		for Name in self.__Paths.keys():
			Value: str | None = os.environ.get(f"MELON_{Name}")
			if Value: self.__Paths[Name] = PathOption(Value)
			else: self.__Paths[Name].value.mkdir(exist_ok = True)

	def __LoadEnviromentVariables(self):
		"""Загружает и парсит переменные среды."""

		load_dotenv()
		self.__LoadEnviromentPathVariables()
		
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер переменных среды парсера."""

		self.__Paths: dict[str, PathOption] = {
			"CONFIGS_DIR": PathOption("configs", is_overrided = False),
			"DEFAULT_OUTPUT_DIR": PathOption("output", is_overrided = False),
			"TEMP_DIR": PathOption("temp", is_overrided = False)
		}

		self.__LoadEnviromentVariables()