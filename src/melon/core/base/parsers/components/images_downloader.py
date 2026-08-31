import shutil
from dataclasses import dataclass
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse, urlunparse

from PIL import Image

if TYPE_CHECKING:
	from dublib.web_requestor import WebRequestor

	from .....core.base.source_operator import BaseSourceOperator

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
	is_downloaded: bool
	resolution: ImageResolution | None
	path: Path | None
	error_message: str | None

class ImageData:
	"""Данные изображения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def filename(self) -> str:
		"""Имя файла."""

		return Path(self._Link.split("?", maxsplit = 1)[0]).name

	@property
	def link(self) -> str:
		"""Ссылка на изображение."""

		return self._Link

	@property
	def resolution(self) -> ImageResolution | None:
		"""Разрешение изображения."""

		return self._Resolution

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, link: str):
		"""
		Данные изображения.

		:param link: Ссылка на изображение.
		:type link: str
		"""

		self._Link: str = link

		self._Resolution: ImageResolution | None = None

	def create_resolution(self, width: int | None, height: int | None):
		"""
		Создаёт и устанавливает разрешение изображения. Если одно или оба значения `None`, операция пропускается.

		:param width: Ширина изображения.
		:type width: int | None
		:param height: Высота изображения.
		:type height: int | None
		"""

		if not all((width, height)):
			return None

		self.set_resolution(ImageResolution(cast(int, width), cast(int, height)))

	def set_link(self, link: str):
		"""
		Задаёт ссылку.

		:param link: Ссылка на изображение.
		:type link: str
		"""

		self._Link = link

	def set_resolution(self, resolution: ImageResolution | None):
		"""
		Указывает разрешение изображения.

		:param resolution: Разрешение изображения.
		:type resolution: ImageResolution | None
		"""

		self._Resolution = resolution

	def to_dict(self, add_filename: bool = False, sizing: bool = True) -> dict:
		"""
		Возвращает словарное представление объекта.

		:param add_filename: Указывает, нужно ли добавлять ключ с именем файла.
		:type add_filename: bool
		:param sizing: Указывает, нужно ли сохранять ключи с разрешением изображения.
		:type sizing: bool
		:return: Словарное представление объекта.
		:rtype: dict
		"""

		Buffer: dict = {
			"link": self._Link,
			"filename": self.filename,
			"width": self._Resolution.width if self._Resolution else None,
			"height": self._Resolution.height if self._Resolution else None
		}

		if not sizing:
			del Buffer["width"]
			del Buffer["height"]

		if not add_filename:
			del Buffer["filename"]

		return Buffer

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ImagesDownloader:
	"""Оператор загрузки изображений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_custom_requestor_used(self) -> bool:
		"""Состояние: используется ли кастомный оператор запросов."""

		return bool(self.__CustomRequestor)

	@property
	def requestor(self) -> "WebRequestor":
		"""Используемый оператор запросов."""

		return self.__CustomRequestor or self.__Requestor

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

		self.__CustomRequestor: "WebRequestor | None" = None

	def build_target_filename(self, url: str, filename: str | None = None, is_full_filename: bool = True) -> str:
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

		ParsedUrl = Path(url.split("?", maxsplit = 1)[0])

		if filename:
			if is_full_filename:
				return ParsedUrl.with_name(filename).name
			else:
				return ParsedUrl.with_stem(filename).name
			
		return ParsedUrl.name

	def build_target_path(self, url: str, directory: str | PathLike[str] | None = None, filename: str | None = None, is_full_filename: bool = True) -> Path:
		"""
		Строит целевой путь изображения.

		:param url: Ссылка на изображение.
		:type url: str
		:param directory: Целевая директория. По умолчанию будет проверен временный каталог парсера.
		:type directory: str | PathLike[str] | None
		:param filename: Имя файла. По умолчанию будет сгенерировано на основе URL.
		:type filename: str | none
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:return: Целевой путь изображения.
		:rtype: Path
		"""

		ImageDirectory: Path = Path(directory) if directory else self.__Temper.get_parser_temp_directory(self.__SourceOperator.manifest.parser_name)
		ImagePath = ImageDirectory / self.build_target_filename(url, filename, is_full_filename)

		return ImagePath

	def download_image(self, url: str, directory: str | PathLike[str] | None = None, filename: str | None = None, is_full_filename: bool = False, force_mode: bool = False) -> ImageDownloadingResult:
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
		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		TempDirectory = self.__Temper.get_parser_temp_directory(self.__SourceOperator.manifest.parser_name)
		ImageDirectory = Path(directory) if directory else TempDirectory
		ImageFilename = self.build_target_filename(url, filename, is_full_filename)
		ImagePath = ImageDirectory / ImageFilename

		IsAlreadyExists: bool = ImagePath.exists()
		Resolution: ImageResolution | None = None
		IsDownloaded: bool = False
		ErrorMessage: str | None = None

		#---> Подстановка доменов зеркал.
		#==========================================================================================#
		ImagesMirrors: dict[str, str] = self.__SourceOperator.settings.network.images_mirrors
		if ImagesMirrors:
			url = self.replace_url_domain(url, ImagesMirrors)

		#---> Скачивание файла.
		#==========================================================================================#
		if not IsAlreadyExists or force_mode:
			Response = self.requestor.get(url)

			if Response.ok and Response.content:
				Resolution = self.get_image_resolution(Response.content)
				MinImageSize: int = self.__SourceOperator.settings.filters.image.min_size
				
				if len(Response.content) > MinImageSize:
					with open(ImagePath, "wb") as FileWriter: FileWriter.write(Response.content)
					IsDownloaded = True

				else: ErrorMessage = f"Image is {MinImageSize} bytes or less."

			else: ErrorMessage = f"Response code: {Response.status_code}."

		return ImageDownloadingResult(IsAlreadyExists, IsDownloaded, Resolution, ImagePath, ErrorMessage)

	def get_image_resolution(self, data: bytes) -> ImageResolution | None:
		"""
		Вычисляется на основе бинарного представления разрешение изображения.

		:return: Разрешение изображения или `None` при ошибке вычисления или отключении получения размера настройками парсера.
		:rtype: ImageResolution | None
		"""

		if not self.__ParserSettings.common.sizing_images:
			return None
		
		if not data:
			return None

		Resolution = None

		try:
			Buffer = Image.open(BytesIO(data))
			Resolution = ImageResolution(Buffer.size[0], Buffer.size[1])
		except Exception:
			return None

		return Resolution
	
	def move_from_temp(self, directory: str | PathLike[str], original_filename: str, filename: str | None = None, is_full_filename: bool = True, force_mode: bool = False) -> Path:
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
		:return: Путь к изображению после перемещения.
		:rtype: Path
		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:raises FileNotFoundError: Не найден оригинальный файл.
		"""

		ImageOriginalDirectory = self.__Temper.get_parser_temp_directory(self.__SourceOperator.manifest.parser_name)
		ImageOriginalFilename = original_filename
		ImageOriginalPath = ImageOriginalDirectory / ImageOriginalFilename

		ImageTargetDirectory = Path(directory)
		ImageTargetFilename = self.build_target_filename(original_filename, filename, is_full_filename)
		ImageTargetPath = ImageTargetDirectory / ImageTargetFilename

		if not ImageOriginalPath.exists():
			raise FileNotFoundError(ImageOriginalPath)

		if ImageTargetPath.exists() and force_mode:
			ImageTargetPath.unlink()

		shutil.move(ImageOriginalPath, ImageTargetPath)

		return ImageTargetPath
	
	def replace_url_domain(self, url: str, rules: dict[str, str] | None = None) -> str:
		"""
		Заменяет домен в ссылке по набору правил.

		:param url: Ссылка.
		:type url: str
		:param rules: Словарь правил, где ключ – заменяемый домен, а значение – подставляемый.
		:type rules: dict[str, str] | None
		:return: Изменённая ссылка или оригинальная, если правила не сработали.
		:rtype: str
		"""

		if rules is None:
			rules = self.__SourceOperator.settings.network.images_mirrors

		ParsedURL = urlparse(url)
		Domain: str = ParsedURL.netloc

		if Domain in rules:
			ParsedURL = ParsedURL._replace(netloc = rules[Domain])

		return urlunparse(ParsedURL)

	def set_requestor(self, requestor: "WebRequestor | None"):
		"""
		Задаёт иной оператор запросов, подменяющий собой предоставляемый оператором источника.

		:param requestor: Собственный оператор запросов или `None` для отключения подмены.
		:type requestor: WebRequestor | None
		"""

		self.__CustomRequestor = requestor

	def temp_image(self, url: str, filename: str | None = None, is_full_filename: bool = False, force_mode: bool = False) -> ImageDownloadingResult:
		"""
		Скачивает изображение во временный каталог парсера..

		:param url: Ссылка на изображение.
		:type url: str
		:param filename: Имя файла. По умолчанию будет использовано оригинальное.
		:type filename: str | None
		:param is_full_filename: Указывает, является ли имя файла полным. Если имя неполное, то расширение для файла будет сгенерировано автоматически (например, для имени *image* будет создан файл *image.jpg* на основе ссылки), в ином случае имя файла задаётся жёстко. 
		:type is_full_filename: bool
		:param force_mode: Переключает режим перезаписи существующих изображений.
		:type force_mode: bool
		:return: Результат скачивания изображения.
		:rtype: ImageDownloadingResult
		"""

		return self.download_image(url, filename = filename, is_full_filename = is_full_filename, force_mode = force_mode)