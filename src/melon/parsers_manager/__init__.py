import io
import shutil
import subprocess
from difflib import get_close_matches
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Sequence

from deepmerge import always_merger
from dulwich import errors, porcelain
from dulwich.porcelain import clone

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

	Installed = 0
	Overwtitted = 1
	Skipped = 2

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

	def add(self, url: str) -> str:
		"""
		Добавляет репозиторий.

		:param url: Ссылка на удалённый Git-репозиторий.
		:type url: str
		:raises ReposError: Ошибка работы с репозиториями.
		:return: Имя парсера, для которого добавлен репозиторий.
		:rtype: str
		"""

		url = self.__CheckURL(url, is_available = True)
		ParserName: str = Path(url).name

		if ParserName in self.__Repositories:
			raise exceptions.system.ReposError(f"Repository for parser \"{ParserName}\" already exists.")

		self.__Repositories[ParserName] = url
		self.save()

		return ParserName

	def get(self, parser: str, exception: bool = False) -> str | None:
		"""
		Получает репозиторий по имени парсера.

		:param parser: Имя парсера.
		:type parser: str
		:param exception: Указывает, нужно ли выбрасывать исключение `KeyError` при неудаче.
		:type exception: bool
		:return: URL репозитория.
		:rtype: str | None
		:raises KeyError: Репозиторий не найден.
		"""

		if exception:
			return self.__Repositories[parser]
		
		return self.__Repositories.get(parser)

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

		WriteTextFile(self.__StorageFilePath, tuple(self.__Repositories.values()))

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

		ParsersNames = []

		for ParserName in ListDir("parsers"):
			if self.__IsParserValid(ParserName): ParsersNames.append(ParserName)

		return tuple(ParsersNames)

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

	def __InstallConfig(self, parser: str, force_mode: bool = False) -> ConfigInstallationResult:
		"""
		Устанавливает зависимости парсера.

		:param parser: Имя парсера.
		:type parser: str
		:param force_mode: Переключает режим перезаписи
		:type force_mode: bool
		:return: Результат установки конфигурации.
		:rtype: ConfigInstallationResult
		"""

		Result: ConfigInstallationResult = ConfigInstallationResult.Skipped

		Config: dict = _BASE_SETTINGS.copy()
		ConfigPresetPath: Path = Path(f"parsers/{parser}/settings.json")
		ConfigStoragePath: Path = Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{parser}")
		ConfigStoragePath.mkdir(parents = not self.__SystemObjects.options.CONFIGS_DIR.is_overrrided, exist_ok = True)
		ConfigTargetFile: Path = ConfigStoragePath / "settings.json"

		if ConfigPresetPath.exists():
			Buffer: dict = ReadJSON(ConfigPresetPath)
			Config = always_merger.merge(Config, Buffer)

		WriteJSON(ConfigTargetFile, Config)

		return Result

	def __InstallRequirements(self, parser: str) -> int:
		"""
		Устанавливает зависимости парсера.

		:param parser: Имя парсера.
		:type parser: str
		:return: Количество установленных пакетов зависимостей.
		:rtype: int
		"""

		RequirementsPath: Path = Path(f"parsers/{parser}/requirements.txt")

		if not RequirementsPath.exists():
			return 0

		subprocess.run(("uv", "pip", "install", "-r", RequirementsPath.as_posix()), check = True)

		Requirements: list[str] = ReadTextFile(RequirementsPath, split = True, strip = True)
		Requirements = [Element for Element in Requirements if Element]

		return len(Requirements)

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
			Path(f"parsers/{parser}/__init__.json").exists(),
			Path(f"parsers/{parser}/manga.json").exists() or Path(f"parsers/{parser}/ranobe.json").exists()
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
		
	def delete(self, parser: str, clear: bool = False):
		"""
		Удаляет парсер.

		:param parser: Имя парсера.
		:type parser: str
		:param clear: Указывает, нужно ли удалить временные данные и конфигурацию парсера.
		:type clear: bool
		"""

		DirectoriesToRemove = [Path(f"parsers/{parser}")]

		if clear:
			DirectoriesToRemove += [
				Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{parser}"),
				Path(f"{self.__SystemObjects.options.TEMP_DIR}/{parser}")
			]

		for Directory in DirectoriesToRemove:
			if Directory.exists():
				shutil.rmtree(Directory)

	def install_by_name(self, parser: str):
		"""
		Устанавливает парсер по его имени.

		:param parser: Имя парсера.
		:type parser: str
		:raises ReposError: Репозиторий парсера не найден.
		"""

		URL: str | None = self.__Repositories.get(parser)

		if not URL:
			raise exceptions.system.ReposError(f"Repository for parser \"{parser}\" not found.")

		self.install_by_url(URL)

	def install_by_url(self, url: str):
		"""
		Устанавливает парсер по ссылке на репозиторий.

		:param url: Ссылка на удалённый Git-репозиторий.
		:type url: str
		"""

		ParserName: str = url.split("/")[-1].split("?", maxsplit = 1)[0]
		Repository: str | None = self.__Repositories.get(ParserName)
		if not Repository: self.__Repositories.add(url)

		clone(url, f"parsers/{ParserName}", errstream = io.BytesIO(), recurse_submodules = True)
		self.printer.emit("Git repository clonned.")

		RequirementsCount: int = self.__InstallRequirements(ParserName)
		if RequirementsCount: self.printer.emit(f"Installed {RequirementsCount} requirements.")

		self.__InstallConfig(ParserName)
