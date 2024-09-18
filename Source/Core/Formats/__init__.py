import enum

class By(enum.Enum):
	"""Типы идентификаторов описательных файлов."""
	
	Filename = 0
	Slug = 1
	ID = 2

class Statuses(enum.Enum):
	"""Определения статусов."""

	announced = "announced"
	ongoing = "ongoing"
	completed = "completed"
	dropped = "dropped"