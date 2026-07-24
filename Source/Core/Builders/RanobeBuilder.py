from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from bs4 import BeautifulSoup
from ebooklib import epub

from Source.Core import Exceptions
from Source.Core.Base.Builder import BaseBuilder

if TYPE_CHECKING:
	from Source.Core.Base.Formats.Ranobe import BaseBranch, Chapter

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class ChapterItems:
	content: epub.EpubHtml
	images: tuple[epub.EpubImage, ...] = tuple()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class RanobeBuilder(BaseBuilder):
	"""Сборщик ранобэ."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __BuildChapter(self, chapter: "Chapter") -> ChapterItems:
		"""
		Собирает элементы EPUB3 для главы ранобэ.

		:param chapter: Глава.
		:type chapter: Chapter
		:return: Набор элементов EPUB3.
		:rtype: ChapterItems
		"""

		ChapterTitle = ""
		ChapterNumeration = ""
		if chapter.volume: ChapterNumeration = f"Том {chapter.volume}. "
		if chapter.number: ChapterNumeration += f"Глава {chapter.number}. "
		if chapter.name: ChapterTitle = ChapterNumeration + chapter.name

		ChapterImages = list()

		Soup = BeautifulSoup("".join(chapter.paragraphs), "html.parser")
		
		for Image in Soup.find_all("img"):
			ImageSource = str(Image["src"])
			PathObject = Path(ImageSource)
			EpubPath = f"{chapter.id}/{PathObject.name}"

			Buffer = epub.EpubImage(
				file_name = EpubPath,
				media_type = "image/" + PathObject.suffix.lstrip("."),
				content = open(self._ParserSettings.directories.images / PathObject, "rb").read()
			)

			ChapterImages.append(Buffer)
			Image["src"] = EpubPath

		ChapterContent = epub.EpubHtml(
			title = ChapterTitle,
			file_name = f"{chapter.id}.xhtml",
			content = f"<h2>{ChapterNumeration}{chapter.name}</h2>" + str(Soup),
			lang = self._Title.content_language
		)
		
		return ChapterItems(ChapterContent, tuple(ChapterImages))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def build(self, branch_id: int | None = None):
		"""
		Собирает ранобэ.

		:param branch_id: ID ветви или `None` для сборки самой длинной.
		:type branch_id: int | None
		"""

		Branches = self._Title.branches
		if not Branches:
			raise Exceptions.Builders.BuildingError("Title hasn't branches.")
		
		BranchToBuild = Branches[0]

		if branch_id:
			SearchResult = self._Title.find_branch_by_id(branch_id)

			if SearchResult:
				raise Exceptions.Builders.BuildingError(f"Branch {branch_id} not found.")
			
			BranchToBuild = cast("BaseBranch", SearchResult)

		Book = epub.EpubBook()
		Book.set_title(self._Title.localized_name)
		Book.set_language(self._Title.content_language)
		for Author in self._Title.authors: Book.add_author(Author)

		Chapters = list()

		for CurrentChapter in BranchToBuild.chapters:
			ChapterItems = self.__BuildChapter(cast("Chapter", CurrentChapter))
			Chapters.append(ChapterItems.content)
			Book.add_item(ChapterItems.content)
			for Image in ChapterItems.images: Book.add_item(Image)

		Book.toc = Chapters
		Book.spine = ["nav"] + Chapters
		Book.add_item(epub.EpubNav())

		FilePath = self._ParserSettings.directories.content / f"{self._Title.localized_name}.epub"
		epub.write_epub(FilePath, Book)

		self._Printer.emit(f"For <i>{self._Title.slug}</i> builded {BranchToBuild.chapters_count} chapters.")