from typing import cast

from dublib.functions.decorators import run_before_method

from ....core import exceptions
from ....core.base.formats.ranobe import Chapter, Ranobe
from .base_parser import BaseParser

class BaseRanobeParser(BaseParser):
	"""Базовый парсер ранобэ."""
	
	@run_before_method("_RequireTitle")
	def amend(self):
		"""Дополняет главы дайными о контенте."""

		self._Title = cast("Ranobe", self._Title)

		AmendedChaptersCount: int = 0
		ProgressIndex: int = 0

		for CurrentBranch in self._Title.branches:
			for CurrentChapter in CurrentBranch.chapters:
				CurrentChapter = cast("Chapter", CurrentChapter)

				if not CurrentChapter.paragraphs:
					ProgressIndex += 1
					Message: str | None = self._Amend(CurrentBranch, CurrentChapter)

					if CurrentChapter.paragraphs:
						self.portals.printer.stages.chapter_amended(CurrentChapter, Message)
						AmendedChaptersCount += 1

	def init_empty_title(self, slug: str) -> Ranobe:
		"""
		Устанавливает пустой тайтл для парсера.

		:param slug: Алиас тайтла.
		:type slug: str
		:return: Тайтл.
		:rtype: Ranobe
		"""

		self._Title = Ranobe(self, slug)

		return self._Title

	@run_before_method("_RequireTitle")
	def repair(self, chapter_id: int) -> bool:
		"""
		Восстанавливает содержимое главы, заново получая его из источника.

		:param chapter_id: Уникальный идентификатор целевой главы.
		:type chapter_id: int
		:raises ChapterNotFound: В локальном JSON не найдена глава с указанным ID.
		:return: Возвращает `True`, если глава содержит контент после восстановления.
		:rtype: bool
		"""

		self._Title = cast("Ranobe", self._Title)

		SearchResult = self._Title.find_chapter_by_id(chapter_id)

		if not SearchResult:
			raise exceptions.parsers.ChapterNotFound(chapter_id)

		AmendedChapter = cast("Chapter", SearchResult.chapter)
		AmendedChapter.clear()
		self._Amend(SearchResult.branch, AmendedChapter)
		
		return bool(AmendedChapter.paragraphs)