import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from dulwich.repo import Repo

from dublib.engine.patcher import Patch
from dublib.functions.data import ToSequence
from dublib.functions.filesystem import WriteJSON, WriteTextFile

from ...core import exceptions
from ...core.base.parsers.components.manifest import _BASE_MANIFEST, ContentTypes
from ...core.base.parsers.components.settings import ParserSettings

if TYPE_CHECKING:
	from ...core.system_objects import SystemObjects

class DevelopmeptAssistant:
	"""Ассистент разработчика."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __InitFiles(self, path: Path, types: Sequence[ContentTypes], parser_name: str, domain: str):
		"""
		Инициализирует скриптовые файлы парсера.

		:param path: Путь к каталогу парсера.
		:type path: Path
		:param types: Поддерживаемые типы контента.
		:type types: Sequence[ContentTypes]
		:param domain: Домен сайта-источника.
		:type domain: str
		"""

		shutil.copy("Source/Utils/Development/main.py", path / "__init__.py")

		for SupportedType in types:
			shutil.copy(f"Source/Utils/Development/{SupportedType.value}.py", path / f"{SupportedType.value}.py")

		shutil.copy("Source/Utils/Development/README.md", path / "README.md")

		Patcher = Patch(path / "README.md")
		Patcher.replace("{MELON_REPOS_URL}", self.__SystemObjects.options.REPOS_URL.value)
		Patcher.replace("{NAME}", parser_name)
		Patcher.replace("{DOMAIN}", domain)
		Patcher.replace("{SITE}", f"https://{domain}")
		Patcher.save()

	def __InitGitRepository(self, path: Path):
		"""
		Инициализирует репозиторий Git.

		:param path: Путь к каталогу парсера.
		:type path: Path
		"""

		Repo.init(path)
		WriteTextFile(path / ".gitignore", "__pycache__")

	def __InitManifest(self, path: Path, domain: str, types: Sequence[ContentTypes]):
		"""
		Инициализирует манифест парсера.

		:param path: Путь к каталогу парсера.
		:type path: Path
		:param domain: Домен сайта-источника.
		:type domain: str
		:param types: Поддерживаемые типы контента.
		:type types: Sequence[ContentTypes]
		"""
		
		ManifestDict: dict = _BASE_MANIFEST.copy()
		ManifestDict["domain"] = domain
		ManifestDict["content_types"] = tuple(CurrentType.value for CurrentType in types)
		ManifestDict["version"] = "$last_git_tag"
		ManifestDict["melon_required_version"] = f">={self.__SystemObjects.MELON_VERSION}" if self.__SystemObjects.MELON_VERSION else None
		WriteJSON(f"{path}/manifest.json", ManifestDict)

	def __InitSettings(self, path: Path):
		"""
		Инициализирует настройки парсера.

		:param path: Путь к каталогу парсера.
		:type path: Path
		"""

		WriteJSON(path / "settings.json", ParserSettings.get_base_settings(self.__SystemObjects, path.name))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Ассистент разработчика.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""

		self.__SystemObjects = system_objects

	def create_parser(self, name: str, domain: str, content_types: ContentTypes | Sequence[ContentTypes], git: bool = True):
		"""
		Создаёт каталог с фалйами для разработки парсера.

		:param name: Имя парсера.
		:type name: str
		:param domain: Домен сайта-источника.
		:type domain: str
		:param content_types: Типы поддерживаемого контента.
		:type content_types: str | Sequence[str]
		:param git: Указывает, инициализировать ли репозиторий **Git**.
		:type git: bool
		:raises ParserAlreadyExists: Парсер уже существует.
		"""

		if domain.startswith("http"): domain = urlparse(domain).netloc
		content_types = ToSequence(content_types)

		ParsersDirectoryPath = Path("parsers")
		ParsersDirectoryPath.mkdir(exist_ok = True)

		ParserPath = ParsersDirectoryPath / name

		if ParserPath.exists():
			raise exceptions.system.ParserAlreadyExists(name)

		ParserPath.mkdir(parents = True)

		if git: self.__InitGitRepository(ParserPath)
		self.__InitSettings(ParserPath)
		self.__InitManifest(ParserPath, domain, content_types)
		self.__InitFiles(ParserPath, content_types, name, domain)

	@staticmethod
	def parse_content_types(data: str) -> tuple[ContentTypes, ...]:
		"""
		Получает последовательность типов контента из строкового представления.

		:param data: Строка из имён типов, раздедённых запятой. Пробелы удаляются. Например: `manga, ranobe`.
		:type data: str
		:return: Набор типов контента.
		:rtype: tuple[ContentTypes]
		"""

		data = data.replace(" ", "")

		Types = []
		for TypeName in data.split(","):
			Types.append(ContentTypes(TypeName))

		return tuple(Types)