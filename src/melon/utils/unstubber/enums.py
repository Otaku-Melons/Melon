from enum import Enum

class SignaturesVersions(Enum):
	"""Версии сигнатур фильтрации."""

	v1 = "{width}x{height}.{sha256}"
	v2 = "{similarity}.{phash}"