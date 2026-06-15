from dataclasses import dataclass
from typing import TYPE_CHECKING
from pathlib import Path
from os import PathLike
from io import BytesIO
import shutil
import os

from PIL import Image

if TYPE_CHECKING:
	from Source.Core.Base.SourceOperator import BaseSourceOperator

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class ImageResolution:
	width: int
	height: int

@dataclass(frozen = True)
class ImageDownloadingResult:
	"""Результат скачивания изображения."""

	is_already_exists: bool
	is_replaced_by_stub: bool
	resolution: ImageResolution | None
	is_downloaded: bool
	path: Path | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ImagesDownloader:
	"""Оператор загрузки изображений."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuildFilenameByURL(self, url: str, filename: str | None = None, is_full_filename: bool = True) -> str:
		"""
		Строит имя файла на основе URL по заданным параметрам.

		:param url: Ссылка на изображение или псевдоссылка из оригинального имени файла.
		:type url: str
		:param filename: Имя файла. По умолчанию будет сгенерировано на основе URL.
		:type filename: str | none
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:return: Имя файла.
		:rtype: str
		"""

		ParsedURL = Path(url)
		Filetype = ""

		if not is_full_filename:
			Filetype = ParsedURL.suffix
		if not filename:
			filename = ParsedURL.stem

		return filename + Filetype

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, source_operator: "BaseSourceOperator"):
		"""
		Оператор загрузки изображений.

		:param source_operator: Оператор источника.
		:type source_operator: BaseSourceOperator
		"""
		
		self.__SourceOperator = source_operator

		self.__SystemObjects = self.__SourceOperator.system_objects
		self.__Temper = self.__SystemObjects.temper
		self.__ParserSettings = self.__SourceOperator.settings
		self.__Requestor = self.__SourceOperator.requestor

	def get_image_resolution(self, data: bytes) -> ImageResolution | None:
		"""
		Вычисляется на основе бинарного представления разрешение изображения.

		:return: Разрешение изображения или `None` при ошибке вычисления или отключении получения размера настройками парсера.
		:rtype: ImageResolution | None
		"""

		if not self.__ParserSettings.common.sizing_images: return
		if not data: return

		Resolution = None

		try:
			Buffer = Image.open(BytesIO(data))
			Resolution = ImageResolution(Buffer.size[0], Buffer.size[1])

		except Exception: return

		return Resolution

	def is_exists_by_url(self, url: str, directory: str | PathLike[str] | None = None, filename: str | None = None, is_full_filename: bool = True) -> bool:
		"""
		Проверяет существование изображения в целевой директории по ссылке.

		:param url: Ссылка на изображение.
		:type url: str
		:param directory: Целевая директория. По умолчанию будет проверен временный каталог парсера.
		:type directory: str | PathLike[str] | None
		:param filename: Имя файла. По умолчанию будет сгенерировано на основе URL.
		:type filename: str | none
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:return: Возвращает `True`, если файл изображения уже существует в директории.
		:rtype: bool
		"""

		ImageDirectory: Path = Path(directory) if directory else self.__Temper.get_parser_temp_directory(self.__SourceOperator.manifest.parser_name)
		ImagePath = ImageDirectory / self.__BuildFilenameByURL(url, filename, is_full_filename)

		return ImagePath.exists()
	
	def download_image(self, url: str, directory: str | PathLike[str] | None = None, filename: str | None = None, is_full_filename: bool = False) -> ImageDownloadingResult:
		"""
		Скачивает изображение.

		:param url: Ссылка на изображение.
		:type url: str
		:param directory: Путь к каталогу, в который нужно сохранить файл. По умолчанию будет использован временный каталог парсера.
		:type directory: str | PathLike[str] | None
		:param filename: Имя файла. По умолчанию будет сгенерировано на основе URL.
		:type filename: str | None
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		ImageDirectory = Path(directory) if directory else self.__Temper.get_parser_temp_directory(self.__SourceOperator.manifest.parser_name)
		ImageFilename = self.__BuildFilenameByURL(url, filename, is_full_filename)
		ImagePath = ImageDirectory / ImageFilename

		IsAlreadyExists: bool = self.is_exists_by_url(url, directory, filename, is_full_filename)
		IsReplacedByStub: bool = False
		Resolution: ImageResolution | None = None
		IsDownloaded: bool = False

		#---> Скачивание файла.
		#==========================================================================================#
		if not IsAlreadyExists or self.__SystemObjects.FORCE_MODE:
			Response = self.__Requestor.get(url)

			if Response.ok and Response.content:
				Resolution = self.get_image_resolution(Response.content)
			
				if len(Response.content) > 1000:
					with open(ImagePath, "wb") as FileWriter:
						FileWriter.write(Response.content)
					IsDownloaded = True

		#---> Замена изображения заглушкой.
		#==========================================================================================#
		if all((not IsDownloaded, not IsAlreadyExists)) and self.__ParserSettings.common.bad_image_stub:
			shutil.copy2(self.__ParserSettings.common.bad_image_stub, ImagePath)
			IsReplacedByStub = True

		return ImageDownloadingResult(IsAlreadyExists, IsReplacedByStub, Resolution, IsDownloaded, ImagePath)

	def move_from_temp(self, directory: str | PathLike[str], original_filename: str, filename: str | None = None, is_full_filename: bool = True):
		"""
		Перемещает изображение из временного каталога парсера в друкгую директорию.

		Если в целевой директории уже существует файл с таким именем, в зависимости от состояния режима перезаписи он будет или перезаписан, или временный файл будет удалён.

		:param directory: Целевая директория.
		:type directory: str | PathLike[str]
		:param original_filename: Имя файла во временном каталоге парсера.
		:type original_filename: str
		:param filename: Новое имя файла. По умолчанию будет использовано оригинальное.
		:type filename: str | None
		:param is_full_filename: Указывает, является ли новое имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе оригинального имени), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:raises FileNotFoundError: Не найден оригинальный файл.
		"""

		ImageOriginalDirectory = self.__Temper.get_parser_temp_directory(self.__SourceOperator.manifest.parser_name)
		ImageOriginalFilename = original_filename
		ImageOriginalPath = ImageOriginalDirectory / ImageOriginalFilename

		ImageTargetDirectory = Path(directory)
		ImageTargetFilename = self.__BuildFilenameByURL(original_filename, filename, is_full_filename)
		ImageTargetPath = ImageTargetDirectory / ImageTargetFilename

		if not ImageOriginalPath.exists():
			raise FileNotFoundError(ImageOriginalPath)

		if ImageTargetPath.exists():
			if self.__SystemObjects.FORCE_MODE:
				ImageTargetPath.unlink()
				os.replace(ImageOriginalPath, ImageTargetPath)

		if ImageOriginalPath.exists():
			ImageOriginalPath.unlink()
	
	def temp_image(self, url: str, filename: str | None = None, is_full_filename: bool = False) -> ImageDownloadingResult:
		"""
		Скачивает изображение во временный каталог парсера..

		:param url: Ссылка на изображение.
		:type url: str
		:param filename: Имя файла. По умолчанию будет использовано оригинальное.
		:type filename: str | None
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		return self.download_image(url, filename = filename, is_full_filename = is_full_filename)