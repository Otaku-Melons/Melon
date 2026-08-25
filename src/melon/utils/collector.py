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
	- **added** – количество уникальных добавленных в коллекцию алиасов;
	- **descriptors** – последовательность дескрипторов тайтлов, из которых собраны алиасы.
	"""

	slugs: tuple[str, ...]
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
	def is_collection_file_exists(self) -> bool:
		"""Состояние: существует ли файл коллекции."""

		return self.__CollectionFile.exists()

	@property
	def slugs(self) -> tuple[str, ...]:
		"""Последовательность алиасов коллекции."""

		return tuple(self.__Collection)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuldResultFormDescriptors(self, descriptors: Sequence[TitleDescriptor]) -> CollectingResult:
		"""
		Строит результат коллекционирования из дескрипторов тайтлов.

		:param descriptors: Последовательность дескрипторов тайтлов.
		:type descriptors: Sequence[TitleDescriptor]
		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""

		Slugs = tuple(Descriptor.slug for Descriptor in descriptors if Descriptor.slug)

		return CollectingResult(
			slugs = Slugs,
			added = self.add(Slugs),
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

		if self.__SourceOperator.settings.common.use_id_as_filename:
			for Descriptor in Descriptors:
				self.__TryGetSlugFromFile(Descriptor)

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

		В экстра-данные дескриптора тайтла добавляет поле _is_broken_ с соответствующим статусом.

		:param descriptor: Дескриптор тайтла.
		:type descriptor: TitleDescriptor
		"""

		if not all((not descriptor.slug, descriptor.path)):
			return

		try:
			Title = ReadJSON(cast(Path, descriptor.path)) 
			descriptor.extra["is_broken"] = False
			Slug = Title.get("slug")
			if Slug: descriptor.set_slug(Slug)

		except JSONDecodeError: descriptor.extra["is_broken"] = True
		except FileNotFoundError: pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator", filename: str | None = None):
		"""
		Сборщик алиасов. Все изменения синхронизируются с представляющим коллекцию файлом.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		:param filename: Имя файла коллекции без расширения. По умолчанию _collection_.
		:type filename: str | None
		"""

		self.__SourceOperator = source_operator
		self.__Filename: str = filename or "collection"

		if not self.__Filename.endswith(".txt"): self.__Filename = f"{self.__Filename}.txt"

		self.__CollectionFile = self.__SourceOperator.system_objects.temper.get_parser_collections_directory(self.__SourceOperator.parser_name) / self.__Filename
		self.__Collection: list[str] = []

	def add(self, slugs: str | Sequence[str]) -> int:
		"""
		Добавляет один или несколько алиасов в коллекцию и сохраняет её в файл.

		:param slugs: Добавляемые алиасы.
		:type slugs: str | Sequence[str]
		:return: Количество уникальных добавленыых алиасов.
		:rtype: int
		"""

		SlugsSet = ToSequence(slugs, target_type = set)
		CollectionSet = set(self.__Collection)
		UniqueSlugsSet = SlugsSet - CollectionSet
		
		self.__Collection = sorted(CollectionSet | SlugsSet)
		self.save()

		return len(UniqueSlugsSet)

	def clear(self):
		"""Очищает коллекцию и удаляет её файл."""

		self.__Collection.clear()

		if self.is_collection_file_exists:
			self.__CollectionFile.unlink()

	def load(self) -> int:
		"""
		Считывает алиасы из файла коллекции.

		:return: Количество уникальных добавленных во внутреннюю коллекцию алиасов.
		:rtype: int
		"""

		if self.__CollectionFile.exists():
			CollectionSlugs: list[str] = ReadTextFile(self.__CollectionFile, split = True, strip = True)
			return self.add(CollectionSlugs)
		
		return 0

	def save(self):
		"""
		Сохраняет коллекцию в файл.

		:param sort: Указывает, требуется ли сортировка по алфавиту.
		:type sort: bool
		"""

		WriteTextFile(self.__CollectionFile, self.__Collection)
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ СБОРКИ ПО КРИТЕРИЯМ <<<<< #
	#==========================================================================================#

	def collect_broken(self) -> CollectingResult:
		"""
		Собирает из локальной директории тайтлов алиасы по правилу: повреждённые файлы.

		Поскольку из повреждённых файлов невозможно извлечь алиас, при использовании ID в качестве имён описательных файлов никогда ничего не добавляет во внутреннюю коллекцию.

		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""

		Descriptors: tuple[TitleDescriptor, ...] = self.__CollectDescriptors()

		for Descriptor in Descriptors:
			if not Descriptor.extra.get("is_broken"):
				self.__TryGetSlugFromFile(Descriptor)

		Descriptors = tuple(Descriptor for Descriptor in Descriptors if Descriptor.extra.get("is_broken"))

		return self.__BuldResultFormDescriptors(Descriptors)

	def collect_local(self) -> CollectingResult:
		"""
		Собирает из локальной директории тайтлов алиасы по правилу: все файлы.

		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""

		return self.__BuldResultFormDescriptors(self.__CollectDescriptors())

	def collect_not_found(self, autosave: bool = True, callback: Callable[[TitleDescriptor], None] | None = None) -> CollectingResult:
		"""
		Собирает из локальной директории тайтлов алиасы по правилу: не найденные на сервере тайтлы.

		Для проверки использует метод оператора источника `is_title_exists()`. Если алиас найден во внутренней коллекции, проверка будет пропущена.

		В экстра-данные дескрипторов тайтлов добавляет поле _is_title_exists_ со статусом проверки существования.

		:param autosave: Сохраняет файл коллекции после каждого изменения.
		:type autosave: bool
		:param callback: Функция, принимающая проверенный дескриптор.
		:type callback: Callable[[TitleDescriptor], None] | None
		:return: Результат сборки тайтлов из каталога.
		:rtype: CollectingResult
		"""

		NotFoundDescriptors: list[TitleDescriptor] = []
		Added: int = 0

		for Descriptor in self.__CollectDescriptors():
			if not Descriptor.slug or Descriptor.slug in self.__Collection: continue

			IsTitleExists: bool | None = self.__SourceOperator.is_title_exists(Descriptor.slug)
			Descriptor.extra["is_title_exists"] = IsTitleExists

			if IsTitleExists is False:
				NotFoundDescriptors.append(Descriptor)
				if autosave:
					self.add(Descriptor.slug)
					Added += 1

			if callback: callback(Descriptor)

		Slugs = tuple(Descriptor.slug for Descriptor in NotFoundDescriptors if Descriptor.slug)
		
		return CollectingResult(
			slugs = Slugs,
			added = Added if autosave else self.add(Slugs),
			descriptors = tuple(NotFoundDescriptors)
		)