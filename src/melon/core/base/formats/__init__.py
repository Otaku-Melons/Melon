from enum import Enum

from .manga import Manga
from .ranobe import Ranobe

class ContentTypes(Enum):
	"""Перечисление типов контента."""

	manga = Manga
	ranobe = Ranobe