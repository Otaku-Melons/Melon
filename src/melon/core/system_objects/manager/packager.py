import io
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from dulwich import porcelain
from dulwich.porcelain import clone
from dulwich.repo import Repo

if TYPE_CHECKING:
	from . import Manager

class Packager:
	"""Пакетный оператор."""

	def __init__(self, manager: "Manager"):
		"""
		Пакетный оператор.

		:param manager: Системный менеджер.
		:type manager: Manager
		"""

		self.__Manager = manager

	def clone(self, directory: Path, remote: str, hide_output: bool = True):
		"""
		Клонирует репозиторий в указанную директорию. Также автоматически клонирует подмодули.

		:param directory: Путь к директории.
		:type directory: str
		:param remote: URL удалённого репозитория Git.
		:type remote: str
		:param hide_output: Указывает, скрывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:raises NotADirectoryError: Объект по переданному пути не является директорией.
		:raises FileNotFoundError: Директория не найдена.
		"""

		if not directory.exists():
			raise FileNotFoundError(directory)

		if directory.is_file():
			raise NotADirectoryError(directory)

		clone(
			source = remote,
			target = directory,
			errstream = io.BytesIO() if hide_output else sys.stdout.buffer,
			recurse_submodules = True
		)

	def install_requirements(self, file: Path):
		"""
		Устанавливает зависимости из переданного файла.

		:param file: Путь к файлу зависимостей.
		:type file: Path
		:raises CalledProcessError: Ошибка установки.
		:raises FileNotFoundError: Файл зависимостей не найден.
		"""

		if not file.exists():
			raise FileNotFoundError(file)

		subprocess.run(("uv", "pip", "install", "-r", file.as_posix()), check = True)

	def has_changes(self, directory: Path) -> bool:
		"""
		Проверяет наличие локальных изменений в каталоге парсера.

		:param directory: Путь к директории парсера.
		:type directory: Path
		:raises FileNotFoundError: Директория не найдена.
		:return: Возвращает `True`, если директория с Git-репозиторием содержит локальные изменения.
		:rtype: bool
		"""

		if not directory.exists():
			raise FileNotFoundError(directory)

		Status = porcelain.status(directory)

		return any((
			Status.staged["add"],
			Status.staged["modify"],
			Status.staged["delete"],
			Status.unstaged
		))

	def pull(self, repository: Path, remote: str, force_mode: bool = False, hide_output: bool = True) -> bool:
		"""
		Обновляет Git репозиторий.

		:param repository: Путь к репощиторию.
		:type repository: Path
		:param remote: URL удалённого репозитория Git.
		:type remote: str
		:param force_mode: Указывает, перезаписывать ли изменения в репозитории.
		:type force_mode: bool
		:param hide_output: Указывает, скрывать ли вывод в терминал из библиотеки клонирования.
		:type hide_output: bool
		:return: Возвращает `True`, если состояние каталога парсера изменилось.
		:rtype: bool
		"""

		LocalRepo = Repo(repository.as_posix())
		HeadCommitHash = LocalRepo.head()

		porcelain.pull(
			repo = LocalRepo.path,
			remote_location = remote,
			outstream = io.BytesIO() if hide_output else sys.stdout.buffer,
			force = force_mode
		)

		return LocalRepo.head() != HeadCommitHash
