import io
import shutil
import subprocess
from difflib import get_close_matches
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Sequence, overload
from urllib.parse import urlparse

from deepmerge import always_merger
from dulwich import errors, porcelain
from dulwich.porcelain import clone, default_bytes_err_stream

from dublib.functions.filesystem import (
	ListDir,
	ReadJSON,
	ReadTextFile,
	WriteJSON,
	WriteTextFile,
)
from dublib.validators import Validator_URL

from ..core import exceptions
from ..core.base.parsers.components.settings import _BASE_SETTINGS

if TYPE_CHECKING:
	from ..core.system_objects import Printer, SystemObjects

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ <<<<< #
#==========================================================================================#

class ConfigInstallationResult(Enum):
	"""Результат установки конфигурации."""

	Missing = 0
	Installed = 1
	AlreadyExists = 2
	Overwtitten = 3

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Repositories:
	"""Менеджер репозиториев."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def availabel_parsers(self) -> tuple[str, ...]:
		"""Последовательность имён доступных в репозиториях парсеров."""

		return tuple(self.__Repositories.keys())

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckURL(self, url: str, is_available: bool = False) -> str:
		"""
		Проверяет валидность URL репозитория.

		:param url: Ссылка на удалённый Git-репозиторий.
		:type url: str
		:param is_available: Переключает проверку доступности репозитория.
		:type is_available: bool
		:return: Ссылка на удалённый Git-репозиторий.
		:rtype: str
		:raises ValidationError: Некорректный URL репозитория.
		:raises ReposError: Репозиторий недоступен.
		"""

		url = url.split("?", maxsplit = 1)[0]

		if is_available and not self.__IsRepositoryAvailable(url):
			raise exceptions.system.ReposError("Remote repository is't available.")

		return Validator_URL.parse(url)

	def __IsRepositoryAvailable(self, url: str) -> bool:
		"""
		Проверяет, доступен ли удалённый Git репозиторий.

		:param url: Ссылка на удалённый Git-репозиторий.
		:type url: str
		:return: Возвращает `True`, если репозиторий доступен.
		:rtype: bool
		"""

		try:
			porcelain.ls_remote(url)
			return True
		except (errors.GitProtocolError, Exception):
			return False

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер репозиториев."""

		self.__StorageFilePath: Path = Path("repositories.txt")
		self.__Repositories: dict[str, str] = {}

		self.load()

	def add(self, url: str, exists_ok: bool = False) -> str:
		"""
		Добавляет репозиторий.

		:param url: Ссылка на удалённый Git-репозиторий.
		:type url: str
		:param exists_ok: Если включено, попытка установки уже установленного репозитория будет считаться нормальным поведением.
		:type exists_ok: bool
		:return: Имя парсера, для которого добавлен репозиторий.
		:rtype: str
		:raises ReposError: Ошибка работы с репозиториями.
		"""

		url = self.__CheckURL(url, is_available = True)
		ParserName: str = self.get_parser_name_from_repository_url(url)

		if ParserName in self.__Repositories:
			if not exists_ok: raise exceptions.system.ReposError(f"Repository for parser \"{ParserName}\" already exists.")
			return ParserName

		self.__Repositories[ParserName] = url
		self.save()

		return ParserName

	@overload
	def get(self, parser: str, exception: Literal[True]) -> str: ...

	@overload
	def get(self, parser: str, exception: Literal[False] = False) -> str | None: ...

	def get(self, parser: str, exception: bool = False) -> str | None:
		"""
		Получает репозиторий по имени парсера.

		:param parser: Имя парсера.
		:type parser: str
		:param exception: Указывает, нужно ли выбрасывать исключение `KeyError` при неудаче.
		:type exception: bool
		:return: URL репозитория.
		:rtype: str | None
		:raises ReposError: Репозиторий не найден.
		"""

		RepositoryURL: str | None = self.__Repositories.get(parser)

		if not RepositoryURL and exception:
			raise exceptions.system.ReposError(f"Repository for parser \"{parser}\" not found.")
		
		return RepositoryURL

	def get_parser_name_from_repository_url(self, url: str) -> str:
		"""
		Возвращает имя парсера по ссылке на его Git репозиторий.

		:param url: Ссылка на удалённый Git-репозиторий.
		:type url: str
		:return: Имя парсера.
		:rtype: str
		:raises ValidationError: Передан некорректный URL.
		"""
		
		url = Validator_URL.parse(url)
		URL: str = urlparse(url).path
		ParserName: str = Path(URL).name

		return ParserName

	def load(self) -> int:
		"""
		Загружает установленные репозитории из файла _repositories.txt_.

		:return: Количество загруженных репозиториев.
		:rtype: int
		:raises ValidationError: Некорректный URL репозитория.
		"""

		self.__Repositories.clear()
		
		if not self.__StorageFilePath.exists():
			return 0

		Links: list[str] = ReadTextFile(self.__StorageFilePath, split = True, strip = True)
		Links = [Element for Element in Links if Element]

		for URL in Links:
			URL = Validator_URL.parse(URL)
			Name = Path(URL).name
			self.__Repositories[Name] = URL

		return len(self.__Repositories.keys())

	def remove(self, parser: str):
		"""
		Удаляет репозиторий.

		:param parser: Имя парсера.
		:type parser: str
		:raises ReposError: Репозиторий не найден.
		"""

		if parser not in self.__Repositories:
			raise exceptions.system.ReposError(f"Repository for parser \"{parser}\" not found.")

		del self.__Repositories[parser]
		self.save()

	def save(self):
		"""Сохраняет репозитории в файл _repositories.txt_."""

		WriteTextFile(self.__StorageFilePath, tuple(sorted(self.__Repositories.values())))

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ParsersManager:
	"""Менеджер парсеров."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def printer(self) -> "Printer":
		"""Оператор вывода."""

		return self.__SystemObjects.printer

	#==========================================================================================#
	# >>>>> СПИСКИ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	@property
	def installed_parsers(self) -> tuple[str, ...]:
		"""Список названий доступных парсеров."""

		return tuple(ListDir("parsers"))

	@property
	def repositories(self) -> Repositories:
		"""Менеджер репозиториев."""

		return self.__Repositories

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __GetBestParserMatch(self, data: str, sequence: Sequence[str]) -> str | None:
		"""
		Возвращает лучшее совпадение имени парсера по отношению к переданной строке.

		:param data: Проверяемая строка.
		:type data: str
		:param sequence: Последовательность имён парсеров.
		:type sequence: Sequence[str]
		:return: Возвращает лучшее совпадение или `None` при отсутствии подходящих вариантов.
		:rtype: str | None
		"""

		BestMatch = get_close_matches(data, sequence, n = 1)

		if BestMatch:
			return BestMatch[0]
		
		return None

	def __IsParserValid(self, parser: str) -> bool:
		"""
		Проверяет валидность парсера методом оценки файловой структуры.

		:param parser: Имя парсера.
		:type parser: str
		:return: Возвращает `True`, если парсер валиден.
		:rtype: bool
		"""

		return all((
			Path(f"parsers/{parser}").exists(),
			Path(f"parsers/{parser}/manifest.json").exists(),
			Path(f"parsers/{parser}/__init__.py").exists(),
			Path(f"parsers/{parser}/manga.py").exists() or Path(f"parsers/{parser}/ranobe.py").exists()
		))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ БАЗОВЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Менеджер парсеров.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""

		self.__SystemObjects: "SystemObjects" = system_objects

		self.__Repositories: Repositories = Repositories()

	def clone_parser(self, parser_name: str, hide_output: bool = True) -> bool:
		"""
		Клонирует файлы парсера из репозитория.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param hide_output: Указывает, перехватывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:return: Возвращает `True`, если парсер успешно клонирован, и `False`, если репозиторий не найден.
		:rtype: bool
		"""

		ParsersRootModulePath: Path = Path("parsers")
		ParsersRootModulePath.mkdir(exist_ok = True)

		RepositoryURL: str | None = self.__Repositories.get(parser_name)
		if not RepositoryURL: return False

		Repository = clone(
			source = RepositoryURL,
			target = f"parsers/{parser_name}",
			errstream = io.BytesIO() if hide_output else default_bytes_err_stream,
			recurse_submodules = True
		)

		return bool(Repository)
		
	def install_config(self, parser: str, force_mode: bool = False) -> ConfigInstallationResult:
		"""
		Устанавливает зависимости парсера.

		:param parser: Имя парсера.
		:type parser: str
		:param force_mode: Переключает режим перезаписи
		:type force_mode: bool
		:return: Результат установки конфигурации.
		:rtype: ConfigInstallationResult
		"""

		Config: dict = _BASE_SETTINGS.copy()

		ConfigStoragePath: Path = Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{parser}")
		ConfigStoragePath.mkdir(parents = not self.__SystemObjects.options.CONFIGS_DIR.is_overrrided, exist_ok = True)

		ConfigPresetFilePath: Path = Path(f"parsers/{parser}/settings.json")
		ConfigStorageFilePath: Path = ConfigStoragePath / "settings.json"

		if ConfigPresetFilePath.exists():
			Buffer: dict = ReadJSON(ConfigPresetFilePath)
			Config = always_merger.merge(Config, Buffer)
		else:
			return ConfigInstallationResult.Missing

		if ConfigStorageFilePath.exists():
			if force_mode:
				WriteJSON(ConfigStorageFilePath, Config)
				return ConfigInstallationResult.Overwtitten
			else:
				return ConfigInstallationResult.AlreadyExists

		WriteJSON(ConfigStorageFilePath, Config)

		return ConfigInstallationResult.Installed

	def install_requirements(self, parser_name: str) -> int:
		"""
		Устанавливает зависимости парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Количество установленных пакетов зависимостей.
		:rtype: int
		"""

		RequirementsPath: Path = Path(f"parsers/{parser_name}/requirements.txt")

		if not RequirementsPath.exists():
			return 0

		subprocess.run(("uv", "pip", "install", "-r", RequirementsPath.as_posix()), check = True)

		Requirements: list[str] = ReadTextFile(RequirementsPath, split = True, strip = True)
		Requirements = [Element for Element in Requirements if Element]

		return len(Requirements)

	def uninstall_parser(self, parser_name: str, clear: bool = False):
		"""
		Удаляет парсер.

		:param parser: Имя парсера.
		:type parser: str
		:param clear: Указывает, нужно ли удалить временные данные и конфигурацию парсера.
		:type clear: bool
		:raises ParserNotFound: Парсер не найден.
		"""
		
		if parser_name not in self.installed_parsers:
			raise exceptions.system.ParserNotFound(parser_name)

		DirectoriesToRemove = [Path(f"parsers/{parser_name}")]

		if clear:
			DirectoriesToRemove += [
				Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{parser_name}"),
				Path(f"{self.__SystemObjects.options.TEMP_DIR}/{parser_name}")
			]

		for Directory in DirectoriesToRemove:
			if Directory.exists():
				shutil.rmtree(Directory)
