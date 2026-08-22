from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
	from ..core.base.source_operator import BaseSourceOperator

class TitleDescriptor:
	"""Дескриптор тайтла."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def extra(self) -> dict[str, Any]:
		"""Словарь дополнительных данных тайтла."""

		return self._Extra

	@property
	def filename(self) -> str | None:
		"""Имя описательного файла тайтла без расширения."""

		return self._Filename

	@property
	def full_filename(self) -> str | None:
		"""Имя описательного файла тайтла с расширением."""

		return f"{self._Filename}.json" if self._Filename else None 

	@property
	def id(self) -> int | None:
		"""ID тайтла."""

		return self._ID

	@property
	def is_local_file_exists(self) -> bool | None:
		"""Состояние: существует ли описательный файл тайтла. `None` при невозможности определения."""

		FilePath: Path | None = self.path

		return FilePath.exists() if FilePath else None

	@property
	def path(self) -> Path | None:
		"""Путь к описательному файлу тайтла."""

		FullFilename: str | None = self.full_filename

		return self._SourceOperator.settings.directories.titles / FullFilename if FullFilename else None 

	@property
	def slug(self) -> str | None:
		"""Алиас тайтла."""

		return self._Slug

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Дескриптор тайтла.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		"""

		self._SourceOperator: "BaseSourceOperator" = source_operator

		self._IsFilenameID: bool = self._SourceOperator.settings.common.use_id_as_filename

		self._ID: int | None = None
		self._Slug: str | None = None
		self._Filename: str | None = None
		self._Extra: dict[str, Any] = {}

	def set_filename(self, filename: str):
		"""
		Задаёт имя файла. Если содержит расширение, последнее будет удалено.

		:param filename: Имя файла.
		:type filename: str
		"""

		self._Filename = Path(filename).stem if filename.endswith(".json") else filename

		if self._ID is None and self._IsFilenameID and self._Filename.isdigit():
			self._ID = int(self._Filename)
			return

		if self._Slug is None and not self._IsFilenameID:
			self._Slug = self._Filename
			return

	def set_id(self, title_id: int):
		"""
		Задаёт ID тайтла.

		:param title_id: ID тайтла.
		:type title_id: int
		"""

		self._ID = title_id

		if self._IsFilenameID and not self._Filename:
			self._Filename = str(self._ID)

	def set_slug(self, slug: str):
		"""
		Задаёт алиас тайтла.

		:param slug: Алиас тайтла.
		:type slug: str
		"""

		self._Slug = slug

		if not self._IsFilenameID and not self._Filename:
			self._Filename = self._Slug

