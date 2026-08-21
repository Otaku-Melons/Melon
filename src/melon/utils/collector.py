import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from json import JSONDecodeError
from typing import TYPE_CHECKING, Sequence

from dublib.functions.data import ToSequence
from dublib.functions.filesystem import ReadJSON, ReadTextFile, WriteTextFile

if TYPE_CHECKING:
	from ..core.base.source_operator import BaseSourceOperator

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class LocalScanningResult:
	"""Результат сканирования каталогов тайтла."""

	found: int
	unique_added: int
	slugs: tuple[str, ...]
	files: tuple[str, ...]

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ <<<<< #
#==========================================================================================#

def _ReadLocalFile(entry: os.DirEntry) -> tuple[str, str] | None:
	"""
	Считывает локальный файл.

	:param entry: Представление файла.
	:type entry: os.DirEntry
	:return: Кортеж из алиаса и имени файла или `None`.
	:rtype: tuple[str, str] | None
	"""

	try:
		Title = ReadJSON(entry.path) 
		Slug = Title.get("slug")
		if Slug: return (Slug, entry.name)
	except (JSONDecodeError, FileNotFoundError): pass
	
	return None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

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

	def __init__(self, source_operator: "BaseSourceOperator", filename: str | None = None):
		"""
		Сборщик алиасов.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		:param filename: Имя файла коллекции без расширения. По умолчанию 
		:type filename: str | None
		"""

		self.__SourceOperator = source_operator
		self.__Filename: str = filename or "collection"

		if not self.__Filename.endswith(".txt"): self.__Filename = f"{self.__Filename}.txt"

		self.__CollectionPath = self.__SourceOperator.system_objects.temper.get_parser_collections_directory(self.__SourceOperator.parser_name) / self.__Filename
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
	
	def scan_local(self, allow_filenames: bool = True) -> LocalScanningResult:
		"""
		Сканирует директорию тайтлов парсера и добавляет алиасы из неё в коллекцию.

		:param allow_filenames: Разрешает считать названия файлов без расширения алиасами при активации соответствующего параметра в настройках парсера. Не требует чтения файла.
		:type allow_filenames: bool
		:return: Контейнер результата сканирования.
		:rtype: LocalScanningResult
		"""
		
		TitlesDirectoryPath = self.__SourceOperator.settings.directories.titles
		LocalSlugs: dict[str, str] = {}
		Entries: tuple[os.DirEntry, ...] = tuple(Entry for Entry in os.scandir(TitlesDirectoryPath) if Entry.is_file() and Entry.name.endswith(".json"))

		if allow_filenames and not self.__SourceOperator.settings.common.use_id_as_filename:
			for Entry in Entries: 
				LocalSlugs[Entry.name[:-5]] = Entry.path

		else:
			with ThreadPoolExecutor() as Executor:
				Results = Executor.map(_ReadLocalFile, Entries)
				
				for Result in Results:
					if Result:
						Slug, Filename = Result
						LocalSlugs[Slug] = Filename

		Slugs: tuple[str, ...] = tuple(LocalSlugs.keys())
		UniqueAdded: int = self.add(Slugs)

		return LocalScanningResult(
			found = len(LocalSlugs.keys()),
			unique_added = UniqueAdded,
			slugs = Slugs,
			files = tuple(LocalSlugs.values())
		)
