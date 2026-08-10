import enum
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, cast

import img2pdf

from dublib.cli.text_styler import FastStyler
from dublib.functions.data import StringifyFloat
from dublib.functions.filesystem import ListDir

from ...core import exceptions
from ...core.base.builder import BaseBuilder

if TYPE_CHECKING:
	from ...core.base.formats.manga import BaseBranch, Chapter

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class MangaOutputFormats(enum.Enum):
	"""Перечисление форматов сборки манги."""

	CBZ = "cbz"
	PDF = "pdf"
	ZIP = "zip"
	Simple = None

#==========================================================================================#
# >>>>> СБОРЩИКИ ГЛАВ <<<<< #
#==========================================================================================#

class _BaseChapterBuilder(ABC):
	"""Базовый сборщик главы манги."""

	@abstractmethod
	def build_chapter(self, name: str, temp_dir: Path, target_dir: Path) -> Path:
		"""
		Собирает главу в пригодный для чтения формат.

		:param name: Название главы.
		:type name: str
		:param temp_dir: Временный каталог со слайдами.
		:type temp_dir: Path
		:param target_dir: Каталог для размещения результата.
		:type target_dir: Path
		:return: Путь к главе.
		:rtype: Path
		"""

		pass

class _MCBF_Simple(_BaseChapterBuilder):
	"""Формат сборки: каталог с изображениями."""

	def build_chapter(self, name: str, temp_dir: Path, target_dir: Path) -> Path:
		"""
		Собирает главу в пригодный для чтения формат.

		:param name: Название главы.
		:type name: str
		:param temp_dir: Временный каталог со слайдами.
		:type temp_dir: Path
		:param target_dir: Каталог для размещения результата.
		:type target_dir: Path
		:return: Путь к главе.
		:rtype: Path
		"""

		target_dir = target_dir / name
		target_dir.mkdir(exist_ok = True)
		Files = ListDir(temp_dir)

		for File in Files:
			os.replace(temp_dir / File, target_dir / File)

		return target_dir
	
class _MCBF_ZIP(_BaseChapterBuilder):
	"""Формат сборки: архив *.zip."""

	def build_chapter(self, name: str, temp_dir: Path, target_dir: Path) -> Path:
		"""
		Собирает главу в пригодный для чтения формат.

		:param name: Название главы.
		:type name: str
		:param temp_dir: Временный каталог со слайдами.
		:type temp_dir: Path
		:param target_dir: Каталог для размещения результата.
		:type target_dir: Path
		:return: Путь к главе.
		:rtype: Path
		"""

		BaseName = target_dir / name
		shutil.make_archive(BaseName.as_posix(), "zip", temp_dir)

		return target_dir / f"{name}.zip"
	
class _MCBF_CBZ(_MCBF_ZIP):
	"""Формат сборки: архив *.cbz."""

	def build_chapter(self, name: str, temp_dir: Path, target_dir: Path) -> Path:
		"""
		Собирает главу в пригодный для чтения формат.

		:param name: Название главы.
		:type name: str
		:param temp_dir: Временный каталог со слайдами.
		:type temp_dir: Path
		:param target_dir: Каталог для размещения результата.
		:type target_dir: Path
		:return: Путь к главе.
		:rtype: Path
		"""

		ArchivePath = super().build_chapter(name, temp_dir, target_dir)
		ComicArchivePath = ArchivePath.with_suffix(".cbz")
		ArchivePath.rename(ComicArchivePath)
	
		return ComicArchivePath

class _MCBF_PDF(_BaseChapterBuilder):
	"""Формат сборки: файл *.pdf."""

	def build_chapter(self, name: str, temp_dir: Path, target_dir: Path) -> Path:
		"""
		Собирает главу в пригодный для чтения формат.

		:param name: Название главы.
		:type name: str
		:param temp_dir: Временный каталог со слайдами.
		:type temp_dir: Path
		:param target_dir: Каталог для размещения результата.
		:type target_dir: Path
		:return: Путь к главе.
		:rtype: Path
		"""

		FilePath = target_dir / f"{name}.pdf"
		Images = ListDir(temp_dir)
		Images.sort()

		for Index in range(len(Images)):
			Images[Index] = temp_dir.joinpath(Images[Index]).as_posix()

		with open(FilePath, "wb") as FileWriter:
			Buffer = img2pdf.convert(Images)
			if Buffer: FileWriter.write(Buffer)

		return FilePath

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class MangaBuilder(BaseBuilder):
	"""Сборщик манги."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuildChapter(self, chapter: "Chapter", progress: float | None = None):
		"""
		Собирает главу манги.

		:param chapter: Глава.
		:type chapter: Chapter
		:param progress: Доля собранных глав в ветви.
		:type progress: float | None
		:raises BuildingError: Ошибка сборки.
		"""
		
		ProgressString = self.__GetProgressString(progress)
		self._SystemObjects.printer.emit(f"{ProgressString}Building chapter <b>{chapter.id}</b>…")

		with TemporaryDirectory(dir = self._ParserTempDirectory) as TempDir:
			TempDirPath = Path(TempDir)
			Slides = chapter.slides 
			SlidesCount = len(Slides)
			
			for Index in range(SlidesCount):
				SlideInfo = Slides[Index]
				FileIndex = Index + 1

				self._Printer.emit(f"[{FileIndex} / {SlidesCount}] Downloading slide \"{SlideInfo.filename}\"… ", end_line = False, flush = True)

				Filename = str(FileIndex).rjust(len(str(SlidesCount)), "0")
				Result = self._Parser.source_operator.download_image(SlideInfo.link, TempDirPath, filename = Filename)
				self._Parser.images_downloader.print_result(Result)

				if not Result.path or not Result.path.exists():
					raise exceptions.builders.BuildingError("Unable download slide.")

				if FileIndex != SlidesCount:
					self._ParserSettings.common.sleep_delay()

			self.__RunChapterBuilder(chapter, TempDirPath)

	def __GetProgressString(self, progress: float | None) -> str:
		"""
		Возвращает строку, указывающую прогресс сборки ветви.

		:param progress: Прогресс сборки ветви.
		:type progress: float | None
		:return: Строка, указывающая прогресс.
		:rtype: str
		"""

		if progress is None:
			return ""
		
		ProgressString = StringifyFloat(progress * 100.0) + "%"
		ProgressString = FastStyler(ProgressString).colorize.bright_cyan

		return f"[{ProgressString}] "

	def __RunChapterBuilder(self, chapter: "Chapter", temp_dir: Path):
		"""
		Запуаскает сборку главы в определённый формат.

		:param chapter: Глава.
		:type chapter: Chapter
		:param temp_dir: Временный каталог со слайдами.
		:type temp_dir: Path
		"""

		TargetDirectory: Path = self._ParserSettings.directories.content / self._Title.used_filename
		TargetDirectory.mkdir(exist_ok = True)
		ChapterName: str = self._GenerateNameByTemplate(chapter, self._ChapterNameTemplate)

		if self.__SortingByVolumes:
			TargetDirectory = TargetDirectory / self._GenerateNameByTemplate(chapter, self._VolumeNameTemplate)
			TargetDirectory.mkdir(exist_ok = True)

		ChapterPath = self.__FormatsBuilders[self.__OutputFormat]().build_chapter(ChapterName, temp_dir, TargetDirectory)
		self._Printer.emit(f"Chapter <b>{chapter.id}</b> builded in: <i>{ChapterPath}</i>.")

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__OutputFormat: MangaOutputFormats = MangaOutputFormats.Simple
		self.__SortingByVolumes: bool = False

		self.__FormatsBuilders: dict[MangaOutputFormats, type[_BaseChapterBuilder]] = {
			MangaOutputFormats.CBZ: _MCBF_CBZ,
			MangaOutputFormats.PDF: _MCBF_PDF,
			MangaOutputFormats.Simple: _MCBF_Simple,
			MangaOutputFormats.ZIP: _MCBF_ZIP,
		}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def build_chapter(self, chapter_id: int):
		"""
		Собирает главу манги.

		:param chapter_id: ID главы.
		:type chapter_id: int
		:raises ChapterNotFound: Глава не найдена.
		"""

		ChapterSearchResult = self._Title.find_chapter_by_id(chapter_id)

		if not ChapterSearchResult:
			raise exceptions.parsers.ChapterNotFound(chapter_id)

		self.__BuildChapter(cast("Chapter", ChapterSearchResult.chapter))

	def build_branch(self, branch_id: int | None = None):
		"""
		Собирает ветвь манги.

		:param branch_id: ID ветви или `None` для сборки самой длинной.
		:type branch_id: int | None
		:raises BuildingError: Ошибка сборки.
		"""

		Branches = self._Title.branches
		if not Branches:
			raise exceptions.builders.BuildingError("Title hasn't branches.")
		
		BranchToBuild = Branches[0]

		if branch_id:
			SearchResult = self._Title.find_branch_by_id(branch_id)

			if SearchResult:
				raise exceptions.builders.BuildingError(f"Branch {branch_id} not found.")
			
			BranchToBuild = cast("BaseBranch", SearchResult)

		Chapters = BranchToBuild.chapters

		for Index in range(BranchToBuild.chapters_count):
			CurrentChapter = cast("Chapter", Chapters[Index])
			Progress = float(Index) / BranchToBuild.chapters_count
			self.__BuildChapter(CurrentChapter, Progress)

		ProgressString = self.__GetProgressString(1.0)
		self._Printer.emit(f"{ProgressString}In branch <b>{BranchToBuild.id}</b> builded {BranchToBuild.chapters_count} chapters.")

	def select_output_format(self, format: MangaOutputFormats):
		"""
		Выбирает формат для сборки манги.

		:param format: Формат сборки или.
		:type format: MangaOutputFormats
		"""

		self.__OutputFormat = format

	def switch_volumes_sorting(self, status: bool):
		"""
		Переключает сортировку глав по каталогам томов.

		:param status: Состояние сортировки.
		:type status: bool
		"""

		self.__SortingByVolumes = status