import io
import os
import shutil
from difflib import get_close_matches
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

import validators
from dulwich import errors
from dulwich.client import get_transport_and_path
from dulwich.porcelain import clone, submodule_list
from dulwich.repo import Repo

from dublib.Engine.Bus import ExecutionResult
from dublib.Methods.Filesystem import ListDir

class ParsersManager:
	"""Менеджер парсеров."""

	#==========================================================================================#
	# >>>>> СПИСКИ ПАРСЕРОВ <<<<< #
	#==========================================================================================#

	@property
	def available_parsers(self) -> list[str]:
		"""Список имён доступных в репозиториях парсеров."""

		ParserNames = list()

		for Repository in self.__Repositories:
			ParserNames.append(Path(Repository).name)

		return ParserNames

	@property
	def installed_parsers(self) -> list[str]:
		"""Список названий доступных парсеров."""

		ParsersNames = list()

		for ParserName in ListDir("Parsers"):
			if self.__IsParserValid(ParserName): ParsersNames.append(ParserName)

		return ParsersNames
	
	@property
	def repositories(self) -> list[str]:
		"""Список репозиториев парсеров."""

		return self.__Repositories.copy()
	
	@property
	def submoduled_parsers(self) -> list[str]:
		"""Список парсеров, поставляемых в качестве подмодулей."""

		ParsersNames = list()
		for SubmoduleData in submodule_list(self.__MelonRepo): ParsersNames.append(Path(SubmoduleData[0]).name)

		return ParsersNames

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

	def __GetRepositoryOwner(self, link: str) -> str:
		"""
		Получает имя владельца репозитория.

		:param link: Ссылка на Git репозиторий.
		:type link: str
		:return: Имя владельца.
		:rtype: str
		"""

		PathString = urlparse(link).path.strip("/")
		Owner, _ = PathString.split("/", 1)

		return Owner

	def __IsLinkToGitRepository(self, url: str) -> bool:
		"""
		Проверяет, ссылается ли ссылка на Git-репозиторий.

		:param url: Проверяемая ссылка.
		:type url: str
		:return: Возвращает `True` в случае успеха.
		:rtype: bool
		"""

		try:
			Client, Path = get_transport_and_path(url)
			Client.get_refs(Path.encode())
			return True
		
		except errors.GitProtocolError: return False

	def __IsParserValid(self, parser: str) -> bool:
		"""
		Проверяет валидность парсера.

		:param parser: Имя парсера.
		:type parser: str
		:return: Возвращает `True`, если парсер валиден.
		:rtype: bool
		"""

		if not bool(Path(f"Parsers/{parser}").iterdir()): return False

		return True

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ БАЗОВЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер парсеров."""

		self.__MelonRepo = Repo("")
		self.__Repositories: list[str] = list()

	def add_repository(self, url: str):
		"""
		Добавляет репозиторий.

		:param url: Ссылка Git-репозиторий парсера.
		:type url: str
		:raises ValueError: Выбрасывается при некорректной ссылке на репозиторий.
		"""

		if not validators.url(url): return ValueError("Incorrect repository URL.")
		if not self.__IsLinkToGitRepository(url): raise ValueError("No git repository found by URL.")

		if url not in self.__Repositories: self.__Repositories.append(url)

	def delete(self, parser: str, clear: bool = False):
		"""
		Удаляет парсер.

		:param parser: Имя парсера.
		:type parser: str
		:param clear: Указывает, нужно ли удалить временные данные и конфигурацию парсера.
		:type clear: bool
		"""

		DirectoriesToRemove = [f"Parsers/{parser}"]
		if clear: DirectoriesToRemove += [f"Configs/{parser}", f"Temp/{parser}"]

		for Directory in DirectoriesToRemove:
			if os.path.exists(Directory): shutil.rmtree(Directory)

	def get_owner_repositories(self, owner: str) -> list[str]:
		"""
		Возвращает список репозиториев, принадлежащих одному владельцу.

		:param owner: Имя владельца.
		:type owner: str
		:return: Список ссылок на Git репозитории.
		:rtype: list[str]
		"""

		return [Repository for Repository in self.__Repositories if self.__GetRepositoryOwner(Repository) == owner]

	def get_parser_repository(self, parser: str) -> str | None:
		"""
		Вовзращает URL репозитория парсера при его наличии.

		:param parser: Имя парсера.
		:type parser: str
		:return: URL репозитория или `None` в случае неудачи.
		:rtype: str | None
		"""

		for Repository in self.__Repositories:
			if Path(Repository).name == parser:
				return Repository
			
		return None

	def install(self, parser: str) -> ExecutionResult:
		"""
		Выполняет установку парсера.

		:param parser: Имя парсера.
		:type parser: str
		:return: Результат установки, содержащий уведомления процесса и состояние успеха.
		:rtype: ExecutionResult
		"""

		Status = ExecutionResult()
		Status.value = False

		Repository = self.get_parser_repository(parser)

		if parser in self.installed_parsers:
			Status.messages.push_info("Parser already installed.")
			Status.value = True
			return Status
		
		if parser not in self.available_parsers or not Repository:
			Status.messages.push_error("Repository not found.")
			return Status

		try:
			clone(Repository, f"Parsers/{parser}", errstream = io.BytesIO(), recurse_submodules = True)
			Status.value = True

		except Exception as ExceptionData: Status.messages.push_error(str(ExceptionData))

		return Status

	def is_parser_installed(self, parser: str) -> bool:
		"""
		Проверяет наличие парсера в системе.

		:param parser: Имя парсера.
		:type parser: str
		:return: Возвращает `True`, если парсер найден в системе.
		:rtype: bool
		"""

		return parser in self.installed_parsers
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ РАСШИРЕННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def install_by_url(self, link: str) -> ExecutionResult:
		"""
		Устанавливает парсер по ссылке на его удалённый Git репозиторий.

		:param link: Ссылка на удалённый Git репозиторий.
		:type link: str
		:return: Результат установки.
		:rtype: ExecutionResult
		"""

		Status = ExecutionResult()
		Status.value = False

		try: self.add_repository(link)
		except ValueError:
			Status.messages.push_error("Link isn't supported Git protocol.")
			return Status
		
		Status += self.install(Path(link).name)

		return Status