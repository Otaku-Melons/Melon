from typing import TYPE_CHECKING, Literal

from .....utils.timer import Timer
from ._base import _BaseTemplatesSection

if TYPE_CHECKING:
	from .....core.base.parsers.components.images_downloader import (
		ImageDownloadingResult,
	)

#==========================================================================================#
# >>>>> ФУТУРА ВЫВОДА <<<<< #
#==========================================================================================#

class ImageDownloadingFuture(_BaseTemplatesSection):
	"""Футура вывода для результата скачивания изображения."""

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self.__Timer = Timer(start = True)

	def result(self, result: "ImageDownloadingResult", show_path: bool = False):
		"""
		Шаблон вывода: результат скачивания изображения.

		:param result: Результат скачивания изображения.
		:type result: ImageDownloadingResult
		:param show_path: Указывает, выводить ли путь к изображению.
		:type show_path: bool
		"""

		if result.error_message:
			self.printer.error(result.error_message)
			return

		elif result.is_already_exists and not result.is_downloaded: self.printer.emit("Already exists.")
		elif result.is_already_exists and result.is_downloaded: self.printer.emit(f"Overwritten in {self.__Timer.ends()}.")
		else: self.printer.emit(f"Done in {self.__Timer.ends()}.")
		
		if show_path: self.printer.emit(f"Image path: \"{result.path}\".")

#==========================================================================================#
# >>>>> НАБОР ШАБЛОНОВ <<<<< #
#==========================================================================================#

class ImagesTemplates(_BaseTemplatesSection):
	"""Расширенные шаблоны вывода: обработка изображений."""

	def start_downloading(
		self,
		filename: str,
		image_type: Literal["cover", "image", "person", "slide"] | None = None
	) -> ImageDownloadingFuture:
		"""
		Шаблон вывода: скачивание изображения начато.

		:param filename: Имя файла.
		:type filename: str
		:param image_type: Тип изображения.
		:type image_type: Literal["cover", "image", "person", "slide"] | None
		:return: Футура вывода для результата скачивания изображения.
		:rtype: ImageDownloadingFuture
		"""

		ImageType: str = "" if image_type is None else f" {image_type}"
		self.printer.emit(f"Downloading{ImageType} \"{filename}\"… ", flush = True, end_line = False)

		return ImageDownloadingFuture(self.printer)

