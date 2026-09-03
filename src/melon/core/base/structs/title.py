from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
	from ..parsers.components.manifest import ContentTypes
	from ..source_operator import BaseSourceOperator
	
class TitleDescriptor:
	"""Дескриптор тайтла."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def content_type(self) -> "ContentTypes | None":
		"""Тип контента."""

		return self._content_type

	@property
	def extra(self) -> dict[str, Any]:
		"""Словарь дополнительных данных тайтла."""

		return self._extra

	@property
	def filename(self) -> str | None:
		"""Имя описательного файла тайтла без расширения."""

		return self._filename

	@property
	def full_filename(self) -> str | None:
		"""Имя описательного файла тайтла с расширением."""

		return f"{self._filename}.json" if self._filename else None 

	@property
	def id(self) -> int | None:
		"""ID тайтла."""

		return self._id

	@property
	def is_local_file_exists(self) -> bool | None:
		"""Состояние: существует ли описательный файл тайтла. `None` при невозможности определения."""

		file: Path | None = self.path

		return file.exists() if file else None

	@property
	def path(self) -> Path | None:
		"""Путь к описательному файлу тайтла."""

		full_gilename: str | None = self.full_filename

		return self._source_operator.settings.directories.titles / full_gilename if full_gilename else None 

	@property
	def slug(self) -> str | None:
		"""Алиас тайтла."""

		return self._slug

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Дескриптор тайтла.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		"""

		self._source_operator: "BaseSourceOperator" = source_operator

		self._is_filename_id: bool = self._source_operator.settings.common.use_id_as_filename
		
		self._id: int | None = None
		self._slug: str | None = None
		self._content_type: "ContentTypes | None" = None
		self._filename: str | None = None
		self._extra: dict[str, Any] = {}

	def set_content_type(self, content_type: "ContentTypes | None"):
		"""
		Задаёт тип контента.

		:param content_type: Тип контента.
		:type content_type: ContentTypes | None
		"""

		self._content_type = content_type

	def set_filename(self, filename: str):
		"""
		Задаёт имя файла. Если содержит расширение, последнее будет удалено.

		:param filename: Имя файла.
		:type filename: str
		"""

		self._filename = Path(filename).stem if filename.endswith(".json") else filename

		if self._id is None and self._is_filename_id and self._filename.isdigit():
			self._id = int(self._filename)
			return

		if self._slug is None and not self._is_filename_id:
			self._slug = self._filename
			return

	def set_id(self, title_id: int):
		"""
		Задаёт ID тайтла.

		:param title_id: ID тайтла.
		:type title_id: int
		"""

		self._id = title_id

		if self._is_filename_id and not self._filename:
			self._filename = str(self._id)

	def set_slug(self, slug: str):
		"""
		Задаёт алиас тайтла.

		:param slug: Алиас тайтла.
		:type slug: str
		"""

		self._slug = slug

		if not self._is_filename_id and not self._filename:
			self._filename = self._slug
