from .Manga import Manga
from .Ranobe import Ranobe

from enum import Enum

class ContentTypes(Enum):
	"""Перечисление типов контента."""

	manga = Manga
	ranobe = Ranobe