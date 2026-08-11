import os
from json import JSONDecodeError
from typing import TYPE_CHECKING, Sequence

from dublib.functions.data import ToSequence
from dublib.functions.filesystem import ReadJSON, ReadTextFile, WriteTextFile

from ..core import exceptions

if TYPE_CHECKING:
	from ..core.base.entry_point import BaseEntryPoint

class Collector:
	"""Сборщик алиасов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def slugs(self) -> tuple[str, ...]:
		"""Последовательность алиасов в коллекции."""

		return tuple(self.__Collection)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, entry_point: "BaseEntryPoint", filename: str | None = None):
		"""
		Сборщик алиасов.

		:param entry_point: Точка входа в модуль парсера.
		:type entry_point: BaseEntryPoint
		:param filename: Имя файла коллекции без расширения. По умолчанию 
		:type filename: str | None
		"""

		self.__EntryPoint = entry_point
		self.__Filename: str = filename or "collection"

		if not self.__Filename.endswith(".txt"): self.__Filename = f"{self.__Filename}.txt"

		self.__CollectionPath = self.__EntryPoint.system_objects.temper.get_parser_collections_directory(self.__EntryPoint.parser_name) / self.__Filename
		self.__Collection: list[str] = []

	def add(self, slugs: str | Sequence[str]) -> int:
		"""
		Добавляет один или несколько алиасов в коллекцию.

		:param slugs: Добавляемые алиасы.
		:type slugs: str | Sequence[str]
		:return: Количество уникальных добавленыых алиасов.
		:rtype: int
		"""

		SlugsSet = ToSequence(slugs, target_type = set)
		CollectionSet = set(self.__Collection)
		UniqueSlugsSet = SlugsSet - CollectionSet
		
		self.__Collection = list(CollectionSet | SlugsSet)

		return len(UniqueSlugsSet)

	def load(self) -> tuple[str, ...]:
		"""
		Считывает файл _collection.txt_ во временном каталоге парсера.

		:return: Последовательность считанных алиасов.
		:rtype: tuple[str, ...]
		"""

		if self.__CollectionPath.exists():
			CollectionSlugs: list[str] = ReadTextFile(self.__CollectionPath, split = True, strip = True)
			self.add(CollectionSlugs)
			return tuple(CollectionSlugs)
		
		return ()

	def save(self, sort: bool = True):
		"""
		Сохраняет коллекцию в файл.

		:param sort: Указывает, требуется ли сортировка по алфавиту.
		:type sort: bool
		"""

		CollectionToWrite: Sequence[str] = self.__Collection

		if sort:
			CollectionToWrite = tuple(sorted(self.__Collection))

		WriteTextFile(self.__CollectionPath, CollectionToWrite)
	
	def scan_local(self, allow_filenames: bool = True) -> int:
		"""
		Сканирует директорию тайтлов парсера и добавляет алиасы из неё в коллекцию.

		:param allow_filenames: Разрешает считать названия файлов без расширения алиасами при активации соответствующего параметра в настройках парсера. Не требует чтения файла.
		:type allow_filenames: bool
		:return: Количество уникальных добавленыых алиасов.
		:rtype: int
		"""
		
		TitlesDirectoryPath = self.__EntryPoint.settings.directories.titles
		LocalSlugs: list[str] = []

		for Entry in os.scandir(TitlesDirectoryPath):
			if not Entry.is_file() or not Entry.name.endswith(".json"):
				continue

			if allow_filenames and not self.__EntryPoint.settings.common.use_id_as_filename:
				LocalSlugs.append(Entry.name[:-5])
				continue

			try:
				Title = ReadJSON(TitlesDirectoryPath / Entry.name) 
				Slug = Title.get("slug")

				if Slug:
					LocalSlugs.append(Slug)

			except (JSONDecodeError, exceptions.parsers.UnsupportedFormat):
				pass

		return self.add(LocalSlugs)
