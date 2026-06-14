from Source.Core.Base.Formats.Components.Enums import By

from dublib.Methods.Filesystem import ReadJSON, ReadTextFile
from dublib.Methods.Data import ToSequence

from typing import cast, Literal, Sequence, TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
	from Source.Core.SystemObjects import SystemObjects

class Collector:
	"""Менеджер коллекций."""

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

	def __init__(self, system_objects: "SystemObjects", merge: bool = True):
		"""
		Менеджер коллекций.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		:param merge: Указывает, нужно ли читать файл коллекции. По умолчанию `True`.
		:type merge: boolt
		"""

		self.__SystemObjects: "SystemObjects" = system_objects

		self.__Path: Path = Path(f"{system_objects.temper.parser_temp}/Collection.txt")
		self.__Collection: list[str] = list(ReadTextFile(self.__Path, split = True, strip = True)) if self.__Path.exists() and merge else list()

	def append(self, slugs: str | Sequence[str]):
		"""
		Добавляет один или несколько алиасов в коллекцию.

		:param slugs: Добавляемые алиасы.
		:type slugs: str | Sequence[str]
		"""

		slugs = ToSequence(slugs)
		self.__Collection += [Slug for Slug in slugs if Slug not in self.__Collection]

	def get_local_identificators(self, identificator_type: Literal[By.ID, By.Slug]) -> list[int] | list[str]:
		"""
		Сканирует директорию татйлов текущего парсера и считывает из них идентификаторы.

		:param identificator_type: Тип идентификаторов в возвращаемом списке.
		:type identificator_type: Literal[By.ID, By.Slug]
		:return: Список идентификаторов указанного типа.
		:rtype: list[int] | list[str]
		"""
		
		ParserSettings = self.__SystemObjects.controller.current_parser_settings

		LocalTitles = tuple(Entry.name for Entry in os.scandir(ParserSettings.common.titles_directory) if Entry.is_file() and Entry.name.endswith(".json"))
		Identificators = list()

		for Filename in LocalTitles:

			try:
				Title = ReadJSON(f"{ParserSettings.common.titles_directory}/{Filename}") 
				Identificators.append(Title[identificator_type.value])

			except KeyError: pass

		return Identificators

	def save(self, sort: bool = False):
		"""
		Сохраняет коллекцию в файл.

		:param sort: Указывает, требуется ли сортировка по алфавиту.
		:type sort: bool
		"""

		self.__Collection = list(set(self.__Collection))
		if sort: self.__Collection = sorted(self.__Collection)

		with open(self.__Path, "w") as FileWriter:
			for Slug in self.__Collection: FileWriter.write(Slug + "\n")

	def from_local(self) -> int:
		"""Сканирует директорию тайтлов и сторит из неё коллекцию."""
		
		LocalTitles = cast(list[str], self.get_local_identificators(By.Slug))
		TitlesCount = len(LocalTitles)
		self.append(LocalTitles)

		return TitlesCount