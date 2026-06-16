import enum

class By(enum.Enum):
	"""Типы идентификаторов описательных файлов."""
	
	Filename = None
	Slug = "slug"
	ID = "id"
	
class Statuses(enum.Enum):
	"""Определения статусов."""

	announced = "announced"
	ongoing = "ongoing"
	completed = "completed"
	dropped = "dropped"