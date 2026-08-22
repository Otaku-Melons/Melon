import os
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Sequence, cast

from dublib.functions.data import ToSequence
from dublib.functions.filesystem import ReadJSON, ReadTextFile, WriteTextFile

from ..core.structs import TitleDescriptor

if TYPE_CHECKING:
	from ..core.base.source_operator import BaseSourceOperator

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class CollectingResult:
	"""
	Результат сборки тайтлов из каталога.
	
	- **slugs** – последовательность собранных алиасов;
	- **collected** – количество собранных алиасов;
	- **added** – количество уникальных добавленных во внутреннюю коллекцию `Collector` алиасов;
	- **descriptors** – последовательность дескрипторов тайтлов, из которых собраны алиасы.
	"""

	slugs: tuple[str, ...]
	collected: int
	added: int
	descriptors: tuple[TitleDescriptor, ...]

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
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuldResultFormDescriptors(self, descriptors: Sequence[TitleDescriptor], add: bool = True) -> CollectingResult:
		
		AddedSlugs: int = 0
		Slugs = tuple(Descriptor.slug for Descriptor in descriptors if Descriptor.slug)
		CollectedSlugs: int = len(Slugs)
		if add: AddedSlugs = self.add(Slugs)

		return CollectingResult(
			slugs = Slugs,
			collected = CollectedSlugs,
			added = AddedSlugs,
			descriptors = tuple(descriptors)
		)

	def __CollectDescriptors(self) -> tuple[TitleDescriptor, ...]:
		"""
		Строит последовательность дескрипторов локальных тайтлов.

		:return: Последовательность дескрипторов локальных тайтлов.
		:rtype: tuple[TitleDescriptor, ...]
		"""

		Directory: Path = self.__SourceOperator.settings.directories.titles
		Descriptors: list[TitleDescriptor] = []

		for Entry in os.scandir(Directory):
			if Entry.is_file() and Entry.name.endswith(".json"):
				Buffer = TitleDescriptor(self.__SourceOperator)
				Buffer.set_filename(Entry.name)
				Descriptors.append(Buffer)

		return self.__SortDescriptors(Descriptors)

	def __SortDescriptors(self, descriptors: Sequence[TitleDescriptor]) -> tuple[TitleDescriptor, ...]:
		"""
		Сортирует последовательность дескрипторов тайтлов по их алиасам (`None` в начале).

		:param descriptors: Последовательность дескрипторов тайтлов.
		:type descriptors: Sequence[TitleDescriptor]
		:return: Отсортированная последовательность дескрипторов тайтлов.
		:rtype: tuple[TitleDescriptor, ...]
		"""
		return tuple(sorted(descriptors, key = lambda Descriptor: (Descriptor.slug is not None, Descriptor.slug)))

	def __TryGetSlugFromFile(self, descriptor: TitleDescriptor):
		"""
		Пытается получить алиас тайтла из ключа _slug_ JSON-файла.

		:param descriptor: Дескриптор тайтла.
		:type descriptor: TitleDescriptor
		"""

		if not all((not descriptor.slug, descriptor.path)):
			return

		try:
			Title = ReadJSON(cast(Path, descriptor.path)) 
			Slug = Title.get("slug")
			if Slug: descriptor.set_slug(Slug)

		except JSONDecodeError: descriptor.extra["is_broken"] = True
		except FileNotFoundError: pass

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
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ СБОРКИ ПО КРИТЕРИЯМ <<<<< #
	#==========================================================================================#

	def collect_broken(self, add: bool = True) -> CollectingResult:
		"""
		Собирает из локальной директории тайтлов алиасы по правилу: повреждённые файлы.

		Поскольку из сломанных файлов невозможно извлечь алиас, при использовании ID в качестве имён описательных файлов никогда ничего не добавляет во внутреннюю коллекцию.

		:param add: Указывает, добавлять ли полученные алиасы во внутреннюю коллекцию.
		:type add: bool
		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""
		
		Result = self.collect_local(add = False)
		Descriptors: tuple[TitleDescriptor, ...] = tuple(Descriptor for Descriptor in Result.descriptors if Descriptor.extra.get("is_broken"))

		return self.__BuldResultFormDescriptors(Descriptors, add)

	def collect_local(self, add: bool = True) -> CollectingResult:
		"""
		Собирает из локальной директории тайтлов алиасы по правилу: все файлы.

		:param add: Указывает, добавлять ли полученные алиасы во внутреннюю коллекцию.
		:type add: bool
		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""
		
		Descriptors: tuple[TitleDescriptor, ...] = self.__CollectDescriptors()

		if self.__SourceOperator.settings.common.use_id_as_filename:
			for Descriptor in Descriptors:
				self.__TryGetSlugFromFile(Descriptor)

		return self.__BuldResultFormDescriptors(Descriptors, add)

	def collect_not_found(self, add: bool = True, callback: Callable[[TitleDescriptor], None] | None = None) -> CollectingResult:
		"""
		Собирает из локальной директории тайтлов алиасы по правилу: не найденные на сервере тайтлы.

		Для проверки использует метод оператора источника `is_title_exists()`.

		:param add: Указывает, добавлять ли полученные алиасы во внутреннюю коллекцию.
		:type add: bool
		:param callback: Функция, принимающая проверенный дескриптор. В экстра-данных последнего появляется флаг _is_title_exists_ с результатом проверки существования.
		:type callback: Callable[[TitleDescriptor], None] | None
		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""

		NotFoundDescriptors: list[TitleDescriptor] = []
		
		for Descriptor in self.collect_local(add = False).descriptors:
			if not Descriptor.slug: continue

			IsTitleExists: bool | None = self.__SourceOperator.is_title_exists(Descriptor.slug)
			Descriptor.extra["is_title_exists"] = IsTitleExists
			if IsTitleExists is False: NotFoundDescriptors.append(Descriptor)

			if callback: callback(Descriptor)
			self.__SourceOperator.settings.common.sleep_delay()

		return self.__BuldResultFormDescriptors(NotFoundDescriptors, add)
