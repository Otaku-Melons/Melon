from enum import Enum

class By(Enum):
	"""Типы идентификаторов описательных файлов."""
	
	Filename = None
	Slug = "slug"
	ID = "id"
	
class ImagesTypes(Enum):
	"""Перечисление типов изображения тайтлов."""

	Cover = "covers"
	Person = "persons"
	Slide = "slides"
	Illustration = "illustration"

class Statuses(Enum):
	"""Перечисление статусов тайтла."""

	announced = "announced"
	ongoing = "ongoing"
	completed = "completed"
	dropped = "dropped"