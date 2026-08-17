import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from dublib.functions.filesystem import ReadJSON

if TYPE_CHECKING:
	from ..core.base.source_operator import BaseSourceOperator

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class CachingResult:
	"""Результат кэширования."""

	total_files: int
	found_in_cache: int
	cached: int
	updated: int
	errors: tuple[str, ...]

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Cacher:
	"""Оператор кэширования пар ID-алиас."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ScanJSON(self, directory: Path) -> tuple[str, ...]:
		"""
		Получает последовательность имён JSON файлов из директории.

		:param directory: Путь к директории.
		:type directory: Path
		:return: Последовательность имён файлов без расширения.
		:rtype: tuple[str, ...]
		"""

		Files: list[str] = []
		SuffixCharactersCount: int = len(".json") * -1

		for Element in os.scandir(directory):
			if not Element.is_file() or not Element.name.endswith(".json"): continue
			else: Files.append(Element.name[:SuffixCharactersCount])

		return tuple(Files)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Оператор кэширования пар ID-алиас.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		"""

		self.__SourceOperator = source_operator

	def cache_parser_output(self) -> CachingResult:
		"""
		Кэширует пары ID-алиас файлов в выходном каталоге парсера.

		:return: Результат кэширования.
		:rtype: CachingResult
		"""

		TotalFiles: int = 0
		FoundInCache: int = 0
		Cached: int = 0
		Updated: int = 0
		Errors: list[str] = []

		TitlesDirectory: Path = self.__SourceOperator.settings.directories.titles
		Files: tuple[str, ...] = self.__ScanJSON(TitlesDirectory)
		TotalFiles: int = len(Files)

		for CurrentFile in Files:
				try:
					Data = ReadJSON(TitlesDirectory / f"{CurrentFile}.json")
				except Exception:
					Errors.append(CurrentFile)
					continue

				DataID: int | None = Data.get("id")
				DataSlug: str | None = Data.get("slug")

				if not DataID or not DataSlug:
					Errors.append(CurrentFile)
					continue

				FoundSlug: str | None = self.__SourceOperator.shared_data.journal.get_slug_by_id(DataID)

				if FoundSlug:
					FoundInCache += 1

					if FoundSlug != DataSlug:
						self.__SourceOperator.shared_data.journal.update(DataID, DataSlug)
						Updated += 1
				else:
					self.__SourceOperator.shared_data.journal.update(DataID, DataSlug)
					Cached += 1

		return CachingResult(TotalFiles, FoundInCache, Cached, Updated, tuple(Errors))