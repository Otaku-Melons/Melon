import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dublib.Functions.Filesystem import ReadJSON

from ..core import exceptions

if TYPE_CHECKING:
	from ..core.base.entry_point import BaseEntryPoint

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

	def __init__(self, entry_point: "BaseEntryPoint"):
		"""
		Оператор кэширования пар ID-алиас.

		:param entry_point: Точка входа в модуль парсера.
		:type entry_point: BaseEntryPoint
		"""

		self.__EntryPoint = entry_point

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

		TitlesDirectory = self.__EntryPoint.settings.directories.titles
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

				if self.__EntryPoint.shared_data.journal.get_slug_by_id(DataID):
					FoundInCache += 1

				else:
					self.__EntryPoint.shared_data.journal.update(DataID, DataSlug)
					CachedFiles += 1

		return CachingResult(TotalFiles, FoundInCache, CachedFiles, tuple(Errors))