from enum import Enum

from .Manga import Manga
from .Ranobe import Ranobe

class ContentTypes(Enum):
	"""Перечисление типов контента."""

	manga = Manga
	ranobe = Ranobe