from Source.Core import Exceptions
from Source.CLI import Templates

from dublib.CLI.Templates.Bus import GenerateMessage, MessagesTypes
from dublib.CLI.TextStyler import GetStyledTextFromHTML
from dublib.WebRequestor import WebResponse

from typing import cast, TYPE_CHECKING
from datetime import datetime
from pathlib import Path
import logging
import enum
import os
import re

if TYPE_CHECKING:
	from Source.Core.Base.Formats.BaseFormat import BaseChapter, BaseTitle
	from Source.Core.SystemObjects import SystemObjects

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ <<<<< #
#==========================================================================================#

class LoggerRules(enum.Enum):
	"""Правила очистки логов."""

	Save = 0
	SaveIfHasErrors = 1
	SaveIfHasWarnings = 2
	Remove = 3

#==========================================================================================#
# >>>>> ПОРТАЛЫ ВЫВОДА ПАРСЕРА <<<<< #
#==========================================================================================#

class Portals:
	"""Порталы вывода парсера."""

	def __init__(self, logger: "Logger", parser_name: str):
		"""
		Порталы вывода парсера.

		:param logger: Оператор вывода и логов.
		:type logger: Logger
		:param parser_name: Имя парсера.
		:type parser_name: str
		"""

		self.__Logger = logger
		self.__ParserName = parser_name

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ОШИБОК <<<<< #
	#==========================================================================================#

	def authorization_required(self, text: str | None = None, exception: bool = True):
		"""
		Портал ошибки: требуется авторизация.

		:param text: Описание ошибки. Следует указать краткую инструкцию по авторизации, если таковая поддерживается.
		:type text: str | None
		:param exception: Указывает, выбрасывать ли исключение.
		:type exception: bool
		:raises ParsingError: Активирована опция выброса исключения.
		"""

		if not text:
			text = "Should use authorization method for selected parser."

		self.__Logger.critical(text)

		if exception:
			raise Exceptions.Parsers.AuthorizationRequired(text)

	def request_error(self, response: WebResponse, text: str | None = None, exception: bool = True):
		"""
		Портал ошибки: неудачный запрос.

		:param response: Контейнер ответа.
		:type response: WebResponse
		:param text: Описание ошибки.
		:type text: str | None
		:param exception: Указывает, выбрасывать ли исключение.
		:type exception: bool
		:raises ParsingError: Выбрасывается при активации соответствующего аргумента.
		"""

		if not text:
			text = "Request error."

		Text = f"{text} Response code: {response.status_code}."

		self.__Logger.error(Text)

		if exception:
			raise Exceptions.Parsers.ParsingError(text)

	def unsupported_format(self, format: str | None = None, exception: bool = True):
		"""
		Шаблон предупреждения: неподдерживаемый формат JSON.

		:param format: Имя формата.
		:type format: str | Non
		:param exception: Указывает, следует ли выбросить исключение.
		:type exception: bool
		:raises UnsupportedFormat: Выбрасывается при активации соответствующего аргумента.
		"""

		Format = f": \"{format}\"" if format else ""
		Text = f"Unsupported JSON format{Format}."

		self.__Logger.error(Text)

		if exception:
			raise Exceptions.Parsers.UnsupportedFormat(Text)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПРЕДУПРЕЖДЕНИЙ <<<<< #
	#==========================================================================================#

	def chapter_not_found(self, chapter: "BaseChapter", exception: bool = True):
		"""
		Портал предупреждения: глава не найдена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:param exception: Указывает, выбрасывать ли исключение.
		:type exception: bool
		:raise ChapterNotFound: Выбрасывается в качестве исключения портала.
		"""

		Text = f"Chapter {chapter.id} not found."
		self.__Logger.error(Text)

		if exception:
			raise Exceptions.Parsers.ChapterNotFound(id = chapter.id, slug = chapter.slug)

	def title_not_found(self, title: "BaseTitle", exception: bool = True):
		"""
		Портал предупреждения: тайтл не найден.

		:param title: Данные тайтла.
		:type title: BaseTitle
		:param exception: Указывает, следует ли выбросить исключение.
		:type exception: bool
		:raises TitleNotFound: Выбрасывается в качестве исключения портала.
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""
		Text = f"Title: \"{title.slug}\"{NoteID}. Not found."

		self.__Logger.warning(Text)

		if exception:
			raise Exceptions.Parsers.TitleNotFound(title)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ СООБЩЕНИЙ <<<<< #
	#==========================================================================================#

	def amending_end(self, amended_chapter_count: int):
		"""
		Шаблон сообщения: дополнение глав завершено.

		:param amended_chapter_count: Количество дополненных глав.
		:type amended_chapter_count: int
		"""

		Text = f"Amended chapters count: {amended_chapter_count}."
		self.__Logger.info(Text)

	def chapter_amended(self, chapter: "BaseChapter"):
		"""
		Шаблон сообщения: глава дополнена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		Text = f"{ChapterNote} {chapter.id} amended."
		self.__Logger.info(Text)

	def chapter_skipped(self, chapter: "BaseChapter", comment: str | None = None):
		"""
		Портал сообщения: дополнение главы пропущено.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		:param comment: Комментарий о причине пропуска.
		:type comment: str | None
		"""

		ChapterType = "Paid chapter " if chapter.is_paid else "Chapter "
		ChapterIdentificator = ""

		if chapter.id:
			ChapterIdentificator = str(chapter.id)
		elif chapter.slug:
			ChapterIdentificator = f"\"{chapter.slug}\""

		comment = f" {comment}" if comment else ""
		Text = f"{ChapterType}{ChapterIdentificator} skipped.{comment}"

		self.__Logger.info(Text)

	def collect_progress_by_page(self, page: int):
		"""
		Портал сообщения: индикация прогресса сбора коллекции.

		:param page: Номер страницы каталога, с которого собраны данные.
		:type page: int
		"""

		self.__Logger.info(f"Titles on page {page} collected.")

	def covers_unstubbed(self):
		"""Портал сообщения: обложки отфильтрованы, так как являются заглушками."""

		self.__Logger.info("Stubs detected. Covers downloading skipped.")

	def chapter_repaired(self, chapter: "BaseChapter"):
		"""
		Шаблон сообщения: глава восстановлена.

		:param chapter: Данные главы.
		:type chapter: BaseChapter
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		Text = f"{ChapterNote} {chapter.id} repaired."
		self.__Logger.info(Text)

	def header(self, header: str, stdout: bool = True, log: bool = True):
		"""
		Шаблон сообщения: заголовок.

		:param header: Текст заголовка.
		:type header: str
		:param stdout: Указывает, выводить ли данные в терминал.
		:type stdout: bool
		:param log: Указывает, записывать ли данные в логи.
		:type log: bool
		"""

		header = header.upper()
		header = f"===== {header} ====="
		self.__Logger.info(header, stdout, log)

	def merging_end(self, merged_chapter_count: int):
		"""
		Шаблон сообщения: объединение данных завершено.

		:param merged_chapter_count: Количество полученных при слиянии глав.
		:type merged_chapter_count: int
		"""

		if self.__Logger.system_objects.FORCE_MODE:
			self.__Logger.info("Merging skipped by force mode.")
		else:
			self.__Logger.info(f"Merged chapters count: {merged_chapter_count}.")

	def parsing_start(self, title: "BaseTitle", index: int, titles_count: int):
		"""
		Шаблон сообщения: парсинг начат.

		:param title: Данные тайтла.
		:type title: BaseTitle
		:param index: Индекс текущей операции парсинга.
		:type index: int
		:param titles_count: Количество тайтлов.
		:type titles_count: int
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""

		if titles_count > 1:
			Templates.PrintParsingProgress(index, titles_count)

		self.__Logger.info(f"Parsing <b>{title.slug}</b>{NoteID}…")

	def titles_collected(self, count: int):
		"""
		Шаблон сообщения: коллекция собрана.

		:param count: Количество добавленных в коллекцию тайтлов.
		:type count: int
		"""

		self.__Logger.info(f"Titles collected: {count}.")

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Logger:
	"""Оператор вывода и логов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def system_objects(self) -> "SystemObjects":
		"""Коллекция системных объектов."""

		return self.__SystemObjects

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReplaceTags(self, text: str) -> str:
		"""
		Заменяет теги HTML на двойные кавычки.

		:param text: Обрабатываемый текст.
		:type text: str
		:return: Обработанный текст.
		:rtype: str
		"""

		return re.sub(r"<[^>]+>", "\"", text)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Оператор вывода и логов.

		:param system_objects: Коллекция системных объектов.
		:type system_objects: SystemObjects
		"""
		
		self.__SystemObjects = system_objects

		self.__LoggerRule = LoggerRules.SaveIfHasErrors
		self.__IsLogHasError = False
		self.__IsLogHasWarning = False

		#---> Настройка логов.
		#==========================================================================================#
		self.__LogsDirectoryPath = Path("Logs")
		self.__LogsDirectoryPath.mkdir(exist_ok = True)
		self.__LogFilePath = self.__LogsDirectoryPath / datetime.now().strftime("%Y-%m-%d %H-%M-%S.log")
		logging.basicConfig(
			filename = self.__LogFilePath,
			encoding = "utf-8",
			level = logging.INFO,
			format = "%(asctime)s %(levelname)s: %(message)s",
			datefmt = "%Y-%m-%d %H:%M:%S"
		)

	def close(self):
		"""Закрывает логи и обрабатывает правило очистки."""

		logging.shutdown()

		IsClean = False

		if self.__LoggerRule == LoggerRules.Remove: IsClean = True
		if self.__LoggerRule == LoggerRules.SaveIfHasErrors and not self.__IsLogHasError: IsClean = True
		if self.__LoggerRule == LoggerRules.SaveIfHasWarnings and not self.__IsLogHasWarning and not self.__IsLogHasError: IsClean = True

		if IsClean: 
			try:
				self.__LogFilePath.unlink()
			except Exception: pass

		try: 
			os.rmdir("Logs")
		except Exception:
			pass

	def emit_in_log(self, text: str, message_type: MessagesTypes | None = None, replace_html_tags: bool = True):
		"""
		Отправляет сообщение в лог.

		:param text: Текст сообщения.
		:type text: str
		:param message_type: Тип сообщения.
		:type message_type: MessagesTypes | None
		:param replace_html_tags: Указывает, следует ли замещать теги HTML в строки на символы кавычек `"`.
		:type replace_html_tags: bool
		"""

		if replace_html_tags: text = self.__ReplaceTags(text)

		match message_type:

			case MessagesTypes.Critical: 
				self.__IsLogHasError = True
				logging.critical(text)

			case MessagesTypes.Error: 
				self.__IsLogHasError = True
				logging.error(text)

			case MessagesTypes.Warning: 
				self.__IsLogHasWarning = True
				logging.warning(text)

			case MessagesTypes.Info | None:
				logging.info(text)

	def emit_in_stdout(self, text: str, message_type: MessagesTypes | None = None, end_line: bool = True, parse_html: bool = True):
		"""
		Отправляет сообщение в поток вывода.

		:param text: Текст сообщения.
		:type text: str
		:param message_type: Тип сообщения.
		:type message_type: MessagesTypes | None
		:param parse_html: Указывает, парсить HTML теги для применения стилей в терминале.
		:type parse_html: bool
		"""

		if parse_html: text = GetStyledTextFromHTML(text)
		MessageText = GenerateMessage(text, message_type)
		print(MessageText, end = "\n" if end_line else "")

	def get_parser_portals(self, parser_name: str) -> Portals:
		"""
		Возвращает порталы вывода парсера.

		:param parser_name: Имя парсера.
		:type parser_name: str
		:return: Порталы вывода парсера.
		:rtype: Portals
		"""

		return Portals(self, parser_name)

	def set_rule(self, rule: int | LoggerRules):
		"""
		Задаёт правило обработки логов.

		:param rule: Индекс правила или само правило.
		:type rule: int | LoggerRules
		:raises ValueError: Неверный индекс правила.
		"""

		ValueType = type(rule)

		if ValueType is int:
			self.__LoggerRule = LoggerRules(rule)
		elif ValueType is LoggerRules:
			self.__LoggerRule = cast(LoggerRules, rule)
		else: 
			raise TypeError(rule)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ВЫВОДА БАЗОВЫХ ТИПОВ СООБЩЕНИЙ <<<<< #
	#==========================================================================================#

	def critical(self, text: str, stdout: bool = True, log: bool = True):
		"""
		Обрабатывает вывод критической ошибки.

		:param text: Текст сообщения.
		:type text: str
		:param stdout: Указывает, нужно ли отправлять данные в поток вывода.
		:type stdout: bool
		:param log: Указывает, нужно ли делать запись в логи.
		:type log: bool
		"""

		if stdout: self.emit_in_stdout(text, MessagesTypes.Critical)
		if log: self.emit_in_log(text, MessagesTypes.Critical)

	def error(self, text: str, stdout: bool = True, log: bool = True):
		"""
		Обрабатывает вывод ошибки.

		:param text: Текст сообщения.
		:type text: str
		:param stdout: Указывает, нужно ли отправлять данные в поток вывода.
		:type stdout: bool
		:param log: Указывает, нужно ли делать запись в логи.
		:type log: bool
		"""

		if stdout: self.emit_in_stdout(text, MessagesTypes.Error)
		if log: self.emit_in_log(text, MessagesTypes.Error)

	def warning(self, text: str, stdout: bool = True, log: bool = True):
		"""
		Обрабатывает вывод предупреждения.

		:param text: Текст сообщения.
		:type text: str
		:param stdout: Указывает, нужно ли отправлять данные в поток вывода.
		:type stdout: bool
		:param log: Указывает, нужно ли делать запись в логи.
		:type log: bool
		"""

		if stdout: self.emit_in_stdout(text, MessagesTypes.Warning)
		if log: self.emit_in_log(text, MessagesTypes.Warning)

	def info(self, text: str, stdout: bool = True, log: bool = True):
		"""
		Обрабатывает вывод сообщения.

		:param text: Текст сообщения.
		:type text: str
		:param stdout: Указывает, нужно ли отправлять данные в поток вывода.
		:type stdout: bool
		:param log: Указывает, нужно ли делать запись в логи.
		:type log: bool
		"""

		if stdout: self.emit_in_stdout(text, None)
		if log: self.emit_in_log(text, MessagesTypes.Info)
