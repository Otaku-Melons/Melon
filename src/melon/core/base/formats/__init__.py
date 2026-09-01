from enum import Enum

from .manga.controller import Manga
from .ranobe.controller import Ranobe

__all__ = ["ContentTypes", "Manga", "Ranobe"]

class ContentTypes(Enum):
	"""Перечисление типов контента."""

	manga = Manga
	ranobe = Ranobe