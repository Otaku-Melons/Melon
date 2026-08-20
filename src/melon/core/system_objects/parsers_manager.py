import importlib
import io
import shutil
import subprocess
import sys
from difflib import get_close_matches
from enum import Enum
from os import listdir
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Sequence, overload
from urllib.parse import urlparse

from deepmerge import always_merger
from dulwich import errors, porcelain
from dulwich.porcelain import clone
from dulwich.repo import Repo

from dublib.functions.filesystem import (
	ReadJSON,
	ReadTextFile,
	WriteJSON,
	WriteTextFile,
)
from dublib.validators import Validator_URL

from ...core import exceptions
from ..base.parsers.components import ParserManifest
from ..base.parsers.components.settings import _BASE_SETTINGS
from ..base.source_operator import BaseSourceOperator

if TYPE_CHECKING:
	from . import Printer, SystemObjects

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ <<<<< #
#==========================================================================================#

class ConfigInstallationResult(Enum):
	"""Результат установки конфигурации."""

	Missing = 0
	Installed = 1
	AlreadyExists = 2
	Overwtitten = 3
	Merged = 4

class ConfigInstallationStrategies(Enum):
	"""Стратегии установки конфигурации."""

	Skip = "-s"
	Overwrite = "-o"
	Merge = "-m"

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
	def get(self, parser_name: str, exception: Literal[True]) -> str: ...

	@overload
	def get(self, parser_name: str, exception: Literal[False] = False) -> str | None: ...

	def get(self, parser_name: str, exception: bool = False) -> str | None:
		"""
		Получает репозиторий по имени парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param exception: Указывает, нужно ли выбрасывать исключение `KeyError` при неудаче.
		:type exception: bool
		:return: URL репозитория.
		:rtype: str | None
		:raises ReposError: Репозиторий не найден.
		"""

		RepositoryURL: str | None = self.__Repositories.get(parser_name)

		if not RepositoryURL and exception:
			raise exceptions.system.ReposError(f"Repository for parser \"{parser_name}\" not found.")
		
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
		"""Список названий установленных парсеров."""

		return tuple(listdir("parsers"))

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

	def __InstallRequirements(self, requirements_path: Path) -> int:
		"""
		Устанавливает зависимости.

		:param requirements_path: Путь к файлу _requirements.txt_.
		:type requirements_path: Path
		:return: Количество установленных пакетов зависимостей.
		:rtype: int
		"""

		if not requirements_path.exists():
			return 0

		subprocess.run(("uv", "pip", "install", "-r", requirements_path.as_posix()), check = True)

		Requirements: list[str] = ReadTextFile(requirements_path, split = True, strip = True)
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
			Path(f"parsers/{parser}/__init__.py").exists(),
			Path(f"parsers/{parser}/manga.py").exists() or Path(f"parsers/{parser}/ranobe.py").exists()
		))

	def __PullGitRepository(self, repos_path: Path, remote_url: str, force_mode: bool = False, hide_output: bool = True) -> bool:
		"""
		Обновляет Git репозиторий.

		:param repos_path: Путь к репощиторию.
		:type repos_path: Path
		:param remote_url: URL удалённого репозитория Git.
		:type remote_url: str
		:param force_mode: Указывает, перезаписывать ли изменения в репозитории.
		:type force_mode: bool
		:param hide_output: Указывает, скрывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:return: Возвращает `True`, если состояние каталога парсера изменилось.
		:rtype: bool
		"""

		LocalRepo = Repo(repos_path.as_posix())
		HeadCommitHash = LocalRepo.head()

		porcelain.pull(
			repo = LocalRepo.path,
			remote_location = remote_url,
			outstream = io.BytesIO() if hide_output else sys.stdout.buffer,
			force = force_mode
		)

		return LocalRepo.head() != HeadCommitHash

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
		:param hide_output: Указывает, скрывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:return: Возвращает `True`, если парсер успешно клонирован, и `False`, если репозиторий не найден.
		:rtype: bool
		:raises ParserNotFound: Парсер не найден.
		"""

		self.is_parser_installed(parser_name)

		ParsersRootModulePath: Path = Path("parsers")
		ParsersRootModulePath.mkdir(exist_ok = True)

		RepositoryURL: str | None = self.__Repositories.get(parser_name)
		if not RepositoryURL: return False

		Repository = clone(
			source = RepositoryURL,
			target = f"parsers/{parser_name}",
			errstream = io.BytesIO() if hide_output else sys.stdout.buffer,
			recurse_submodules = True
		)

		return bool(Repository)
		
	def is_parser_installed(self, parser_name: str, exception: bool = True) -> bool:
		"""
		Проверяет, установлен ли парсер.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param exception: Указывает, следует ли выбрасывать исключение при отсутствии парсера.
		:type exception: bool
		:return: Возвращает `True`, если парсер установлен.
		:rtype: bool
		:raises ParserNotFound: Парсер не найден.
		"""

		IsInstalled: bool = parser_name in self.installed_parsers

		if not IsInstalled and exception:
			raise exceptions.system.ParserNotFound(parser_name)

		return IsInstalled

	def install_config(self, parser_name: str, conflict_strategy: ConfigInstallationStrategies = ConfigInstallationStrategies.Skip) -> ConfigInstallationResult:
		"""
		Устанавливает зависимости парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param conflict_strategy: Стратегия установки конфигурации при конфликте.
		:type conflict_strategy: ConfigInstallationStrategies
		:return: Результат установки конфигурации.
		:rtype: ConfigInstallationResult
		:raises ParserNotFound: Парсер не найден.
		"""
		
		self.is_parser_installed(parser_name)

		Config: dict = _BASE_SETTINGS.copy()

		ConfigPresetFilePath: Path = Path(f"parsers/{parser_name}/settings.json")
		ConfigStorageFilePath: Path = self.__SystemObjects.options.CONFIGS_DIR.value / f"{parser_name}.json"

		if ConfigPresetFilePath.exists():
			Buffer: dict = ReadJSON(ConfigPresetFilePath)
			Config = always_merger.merge(Config, Buffer)
		else:
			return ConfigInstallationResult.Missing

		if ConfigStorageFilePath.exists():
			
			match conflict_strategy:
				case ConfigInstallationStrategies.Skip:
					return ConfigInstallationResult.AlreadyExists

				case ConfigInstallationStrategies.Overwrite:
					WriteJSON(ConfigStorageFilePath, Config)
					return ConfigInstallationResult.Overwtitten

				case ConfigInstallationStrategies.Merge:
					CurrentConfig: dict = ReadJSON(ConfigStorageFilePath)
					Config = always_merger.merge(Config, CurrentConfig)
					WriteJSON(ConfigStorageFilePath, Config)
					return ConfigInstallationResult.Merged

		WriteJSON(ConfigStorageFilePath, Config)

		return ConfigInstallationResult.Installed

	def install_requirements(self, parser_name: str) -> int | None:
		"""
		Устанавливает зависимости парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Количество установленных пакетов зависимостей или `None`, если файл зависимостей отсутствует.
		:rtype: int | None
		:raises ParserNotFound: Парсер не найден.
		"""

		self.is_parser_installed(parser_name)

		RequirementsPath = Path(f"parsers/{parser_name}/requirements.txt")
		if not RequirementsPath.exists(): return None
 
		return self.__InstallRequirements(RequirementsPath)

	def launch_source_operator(self, parser_name: str) -> "BaseSourceOperator":
		"""
		Инициализирует оператор источника для указанного парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Оператор источника.
		:rtype: BaseSourceOperator
		:raises FileNotFoundError: Файл точки входа в парсер не найден.
		:raises ParserNotFound: Парсер не найден.
		"""

		self.is_parser_installed(parser_name)

		ParserMainPath = Path(f"parsers/{parser_name}/__init__.py")

		if not ParserMainPath.exists():
			raise FileNotFoundError(ParserMainPath)

		Module = importlib.import_module(f"parsers.{parser_name}")
		ParserManifest = self.load_parser_manifest(parser_name)

		return Module.SourceOperator(self.__SystemObjects, ParserManifest)
	
	def load_parser_manifest(self, parser_name: str) -> ParserManifest:
		"""
		Загружает манифест парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Манифест парсера.
		:rtype: ParserManifest
		:raises FileNotFoundError: Файл манифеста не найден.
		:raises ParserNotFound: Парсер не найден.
		"""

		self.is_parser_installed(parser_name)

		ManifestPath = Path(f"parsers/{parser_name}/manifest.json")
		if not ManifestPath.exists():
			raise FileNotFoundError(ManifestPath)
		
		return ParserManifest(self.__SystemObjects, parser_name)

	def uninstall_parser(self, parser_name: str, clear: bool = False):
		"""
		Удаляет парсер.

		:param parser: Имя парсера.
		:type parser: str
		:param clear: Указывает, нужно ли удалить временные данные и конфигурацию парсера.
		:type clear: bool
		:raises ParserNotFound: Парсер не найден.
		"""
		
		self.is_parser_installed(parser_name)
		ElementToRemove = [Path(f"parsers/{parser_name}")]

		if clear:
			ElementToRemove += [
				Path(f"{self.__SystemObjects.options.CONFIGS_DIR}/{parser_name}.json"),
				Path(f"{self.__SystemObjects.options.TEMP_DIR}/{parser_name}")
			]

		for Element in ElementToRemove:
			if Element.exists():
				if Element.is_dir(): shutil.rmtree(Element)
				else: Element.unlink()

	def update_parser(self, parser_name: str, requirements: bool = True, force_mode: bool = False, hide_output: bool = True) -> bool:
		"""
		Обновляет парсер.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:param requirements: Указывает, нужно ли установить зависимости после обновления.
		:type requirements: bool
		:param force_mode: Указывает, перезаписывать ли изменения в репозитории.
		:type force_mode: bool
		:param hide_output: Указывает, скрывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:return: Возвращает `True`, если состояние каталога парсера изменилось.
		:rtype: bool
		:raises ParserNotFound: Парсер не найден.
		"""

		self.is_parser_installed(parser_name)
		RepoPath = Path(f"parsers/{parser_name}")

		IsRepoChanged: bool = self.__PullGitRepository(
			repos_path = RepoPath,
			remote_url = self.repositories.get(parser_name, exception = True),
			force_mode = force_mode,
			hide_output = hide_output
		)

		if IsRepoChanged and requirements:
			self.__InstallRequirements(RepoPath / "requirements.txt")

		return IsRepoChanged

	def upgrade_melon(self, requirements: bool = True, force_mode: bool = False, hide_output: bool = True) -> bool:
		"""
		Обновляет Melon.

		:param requirements: Указывает, нужно ли установить зависимости после обновления.
		:type requirements: bool
		:param force_mode: Указывает, перезаписывать ли изменения в репозитории.
		:type force_mode: bool
		:param hide_output: Указывает, скрывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:return: Возвращает `True`, если состояние каталога парсера изменилось.
		:rtype: bool
		"""

		raise NotImplementedError("Use \"git pull\" instead.")