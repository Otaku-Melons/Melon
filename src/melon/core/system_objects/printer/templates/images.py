from .....utils.timer import Timer
from ....base.formats.base_format.enums import ImagesTypes
from ....base.parsers.components.images_downloader import (
	FilteredBy,
	ImageDownloadingResult,
)
from ._base import _BaseTemplatesSection

#==========================================================================================#
# >>>>> ФУТУРА ВЫВОДА <<<<< #
#==========================================================================================#

class ImageDownloadingFuture(_BaseTemplatesSection):
	"""Футура вывода для результата скачивания изображения."""

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self.__Timer = Timer(start = True)

	def result(self, result: ImageDownloadingResult, show_path: bool = False):
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

		elif result.filtered_by:
			match result.filtered_by:
				case FilteredBy.Resolution: self.printer.emit("Filtered by resolution.")
				case FilteredBy.Size: self.printer.emit("Filtered by size.")
				case FilteredBy.Signature: self.printer.emit("Filtered by signature.")
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
		image_type: ImagesTypes | None = None
	) -> ImageDownloadingFuture:
		"""
		Шаблон вывода: скачивание изображения начато.

		:param filename: Имя файла.
		:type filename: str
		:param image_type: Тип изображения.
		:type image_type: ImagesTypes | None
		:return: Футура вывода для результата скачивания изображения.
		:rtype: ImageDownloadingFuture
		"""

		ImageType: str = "" if image_type is None else f" {image_type.name.lower()}"
		self.printer.emit(f"Downloading{ImageType} \"{filename}\"… ", flush = True, end_line = False)

		return ImageDownloadingFuture(self.printer)

