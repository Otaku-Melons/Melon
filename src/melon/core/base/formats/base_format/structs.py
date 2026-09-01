from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
	from .branch import Branch
	from .chapter import BaseChapter

@dataclass(frozen = True)
class ChapterSearchResult:
	"""Результат поиска главы."""
	
	branch: "Branch"
	chapter: "BaseChapter"

@dataclass(frozen = True)
class ExtraField:
	"""Дополнительное поле данных."""

	after_key: str
	name: str
	value: Any