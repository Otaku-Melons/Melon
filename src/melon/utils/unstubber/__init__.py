import hashlib
import io
from os import PathLike
from typing import Sequence

import imagehash
from PIL.Image import open as open_image
from PIL.ImageFile import ImageFile

from dublib.functions.data import to_sequence

from .enums import SignaturesVersions

class Unstubber:
	"""Фильтр заглушек."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetImagePixelHashSHA256(self, image: ImageFile) -> str:
		"""
		Получает строковое представление хэша пикселей изображения в формате **SHA256**.

		:param image: Изображение.
		:type image: ImageFile
		:return: Строковое представление хэша пикселей изображения в формате **SHA256**.
		:rtype: str
		"""

		PixelBytes: bytes = image.convert("RGB").tobytes()
		
		return hashlib.sha256(PixelBytes).hexdigest()

	def __GetUsedSignaturesVersions(self, signatures: Sequence[str]) -> tuple[SignaturesVersions, ...]:
		"""
		Получает список используемых в последовательности сигнатур версий.

		:param signatures: Последовательность сигнатур.
		:type signatures: Sequence[str]
		:return: Последовательность использованных версий сигнатур.
		:rtype: tuple[SignaturesVersions, ...]
		"""

		UsedVersions: list[SignaturesVersions] = []

		for Signature in signatures:
			Version = self.get_siqnature_version(Signature)

			if Version not in UsedVersions:
				UsedVersions.append(Version)
				if len(UsedVersions) == len(SignaturesVersions): break

		return tuple(UsedVersions)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def build_image(self, image: bytes) -> ImageFile:
		"""
		Строит изображение из бинарного представления.

		:param image: Бинарное представление изображения.
		:type image: bytes
		:return: Изображение.
		:rtype: ImageFile
		"""
		
		return open_image(io.BytesIO(image))

	def generate_signature(self, image: ImageFile, signature_version: SignaturesVersions) -> str:
		"""
		Генерирует сигнатуру изображения определённой версии.

		:param image: Изображение.
		:type image: ImageFile
		:param signature_version: Версия сигнатуры.
		:type signature_version: SignaturesVersions
		:return: Сигнатура изображения.
		:rtype: str
		"""

		Data: dict[str, int | str | None] = {
			"version": signature_version.name,

			"width": None,
			"height": None,
			"sha256": None,

			"phash": None,
			"similarity": 100
		}

		match signature_version:

			case SignaturesVersions.v1:
				Resolution: tuple[int, int] = image.size
				Data["width"] = str(Resolution[0])
				Data["height"] = str(Resolution[1])
				Data["sha256"] = self.__GetImagePixelHashSHA256(image)

			case SignaturesVersions.v2:
				Data["phash"] = str(imagehash.phash(image))

		Template: str = "{version}." + signature_version.value

		return Template.format(**Data)

	def get_siqnature_version(self, signatrue: str) -> SignaturesVersions:
		"""
		Определяет версию сигнатуры.

		:param signatrue: Сигнатура.
		:type signatrue: str
		:return: Версия сигнатуры.
		:rtype: SignaturesVersions
		"""

		VersionPart: str = signatrue.split(".")[0]

		return SignaturesVersions[VersionPart]

	def filter_image(self, image: ImageFile, signatures: str | Sequence[str]) -> bool:
		"""
		Проверяет соответствие сигнатуры изображения сигнатурам фильтров.

		:param image: Изображение.
		:type image: ImageFile
		:param signatures: Одна или несколько сигнатур для сравнения.
		:type signatures: str | Sequence[str]
		:return: Возвращает `True`, если изображение соответствует одной из переданных сигнатур.
		:rtype: bool
		"""

		Signatures: tuple[str, ...] = to_sequence(signatures)
		TargetSignatures: list[str] = []

		for Version in self.__GetUsedSignaturesVersions(Signatures):
			TargetSignatures.append(self.generate_signature(image, Version))

		for TargetSignature in TargetSignatures:
			if TargetSignature in Signatures:
				return True

		return False

	def load_image(self, image_path: PathLike[str] | str) -> ImageFile:
		"""
		Загружает изображение в ОЗУ и строит его объектное представление.

		:param image_path: Путь к изображению.
		:type image_path: PathLike[str] | str
		:return: Изображение.
		:rtype: ImageFile
		"""

		return open_image(image_path)