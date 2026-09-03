from dataclasses import dataclass

@dataclass(frozen = True)
class SourceProperties:
	"""
	Свойства источника.
	
	- **one_cover** – указывает, являются ли все изображения обложек модификациями одного изображения. Если включено, при фильтрации одной обложки будут удалены все изображения.
	"""

	one_cover: bool