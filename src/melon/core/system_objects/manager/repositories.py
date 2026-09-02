from pathlib import Path
from typing import TYPE_CHECKING, Literal, overload
from urllib.parse import urlparse

from dulwich import errors, porcelain

from dublib.functions.filesystem import text
from dublib.validators import types

from ....core import exceptions

if TYPE_CHECKING:
	from . import Manager

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
		:raises RepositoryError: Репозиторий недоступен.
		"""

		url = url.split("?", maxsplit = 1)[0]

		if is_available and not self.__IsRepositoryAvailable(url):
			raise exceptions.system.RepositoryError("Remote repository is't available.")

		return types.URL.parse(url)

	def __GetParserNameFromRepositoryURL(self, repository: str) -> str:
		"""
		Возвращает имя парсера по ссылке на его Git репозиторий.

		:param repository: Ссылка на удалённый Git-репозиторий.
		:type repository: str
		:return: Имя парсера.
		:rtype: str
		"""
		
		return Path(urlparse(repository).path).name

	def __IsRepositoryAvailable(self, repository: str) -> bool:
		"""
		Проверяет, доступен ли удалённый Git репозиторий.

		:param repository: Ссылка на удалённый Git-репозиторий.
		:type repository: str
		:return: Возвращает `True`, если репозиторий доступен.
		:rtype: bool
		"""

		try:
			porcelain.ls_remote(repository)
			return True
		except (errors.GitProtocolError, Exception):
			return False

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manager: "Manager"):
		"""
		Менеджер репозиториев.

		:param manager: Системный менеджер.
		:type manager: Manager
		"""

		self.__Manager = manager

		self.__StorageFile: Path = Path("repositories.txt")
		self.__Repositories: dict[str, str] = {}

		self.load()

	def add(self, repository: str, exists_ok: bool = False) -> str:
		"""
		Добавляет репозиторий.

		:param repository: Ссылка на удалённый Git-репозиторий.
		:type repository: str
		:param exists_ok: Если включено, попытка установки уже установленного репозитория будет считаться нормальным поведением.
		:type exists_ok: bool
		:return: Имя парсера, для которого добавлен репозиторий.
		:rtype: str
		:raises RepositoryError: Ошибка работы с репозиториями.
		"""

		url = self.__CheckURL(repository, is_available = True)
		ParserName: str = self.__GetParserNameFromRepositoryURL(repository)

		if ParserName in self.__Repositories:
			if not exists_ok: raise exceptions.system.RepositoryError(f"Repository for parser \"{ParserName}\" already exists.")
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
		:raises RepositoryError: Репозиторий не найден.
		"""

		RepositoryURL: str | None = self.__Repositories.get(parser_name)

		if not RepositoryURL and exception:
			raise exceptions.system.RepositoryError(f"Repository for parser \"{parser_name}\" not found.")
		
		return RepositoryURL

	def load(self) -> int:
		"""
		Загружает установленные репозитории из файла _repositories.txt_.

		:return: Количество загруженных репозиториев.
		:rtype: int
		:raises ValidationError: Некорректный URL репозитория.
		"""

		self.__Repositories.clear()
		
		if not self.__StorageFile.exists():
			return 0

		Links: list[str] = text.read(self.__StorageFile, split = True, strip_level = 2)
		Links = [Element for Element in Links if Element]

		for URL in Links:
			URL = types.URL.parse(URL)
			Name = Path(URL).name
			self.__Repositories[Name] = URL

		return len(self.__Repositories.keys())

	def remove(self, parser: str):
		"""
		Удаляет репозиторий.

		:param parser: Имя парсера.
		:type parser: str
		:raises RepositoryError: Репозиторий не найден.
		"""

		if parser not in self.__Repositories:
			raise exceptions.system.RepositoryError(f"Repository for parser \"{parser}\" not found.")

		del self.__Repositories[parser]
		self.save()

	def save(self):
		"""Сохраняет репозитории в файл _repositories.txt_."""

		text.write(self.__StorageFile, tuple(sorted(self.__Repositories.values())))
