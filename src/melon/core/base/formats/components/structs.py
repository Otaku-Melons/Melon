from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..base_format import BaseBranch, BaseChapter

@dataclass
class ChapterSearchResult:
	"""Результат поиска главы."""
	
	branch: "BaseBranch"
	chapter: "BaseChapter"