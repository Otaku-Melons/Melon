import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dublib.functions.filesystem import ReadJSON

from ..core import exceptions

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
	cached_files: int
	errors: tuple[str, ...]

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Cacher:
	"""Оператор кэширования пар ID-алиас."""

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
		CachedFiles: int = 0
		Errors: list[str] = []

		TitlesDirectory = self.__SourceOperator.settings.directories.titles
		Files: list[str] = []
		SuffixCharactersCount: int = len(".json") * -1

		for Element in os.scandir(TitlesDirectory):
			if not Element.is_file() or not Element.name.endswith(".json"):
				continue
			else:
				Files.append(Element.name[:SuffixCharactersCount])

		TotalFiles = len(Files)

		for CurrentFile in Files:
				try:
					Data = ReadJSON(TitlesDirectory / f"{CurrentFile}.json")
				except exceptions.parsers.UnsupportedFormat:
					Errors.append(CurrentFile)
					continue

				DataID: int | None = Data.get("id")
				DataSlug: str | None = Data.get("slug")

				if not DataID or not DataSlug:
					Errors.append(CurrentFile)
					continue

				if self.__SourceOperator.shared_data.journal.get_slug_by_id(DataID):
					FoundInCache += 1

				else:
					self.__SourceOperator.shared_data.journal.update(DataID, DataSlug)
					CachedFiles += 1

		return CachingResult(TotalFiles, FoundInCache, CachedFiles, tuple(Errors))