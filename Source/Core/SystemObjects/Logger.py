from Source.Core.Exceptions import ParsingError, TitleNotFound
from Source.Core.Formats import BaseChapter, BaseTitle
from Source.CLI import Templates

from dublib.Methods.Filesystem import ReadJSON
from dublib.CLI.TextStyler import TextStyler
from dublib.WebRequestor import WebResponse
from dublib.Polyglot import Markdown
from datetime import datetime

import logging
import telebot
import enum
import sys
import os
import re

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class LoggerRules(enum.Enum):
	"""Правила очистки логов."""

	Save = 0
	SaveIfHasErrors = 1
	SaveIfHasWarnings = 2
	Remove = 3

#==========================================================================================#
# >>>>> КОНТЕЙНЕРЫ НАСТРОЕК <<<<< #
#==========================================================================================#

class CleanerSettings:
	"""Правила очистки логов."""

	def __init__(self, data: dict):
		"""
		Правила очистки логов.
			data – словарь прафил очистки.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Rules = data.copy()

	def __getitem__(self, command: str) -> LoggerRules:
		"""Возвращает правило очистки логов."""

		Rule = LoggerRules(0)
		if command in self.__Rules.keys(): Rule = LoggerRules(self.__Rules[command])

		return Rule

class ReportsRules:
	"""Набор правил отправки отчётов."""

	@property 
	def attach_log(self) -> bool:
		"""Состояние: требуется ли прикреплять файл лога к отчёту."""

		return self.__Data["attach_log"]
	
	@property 
	def forbidden_commands(self) -> list[str]:
		"""Список команд, для которых запрещена отправка отчётов."""

		return self.__Data["forbidden_commands"]
	
	@property 
	def ignored_requests_errors(self) -> list[int, None]:
		"""Список кодов HTTP, не вызывающих отправку отчётов."""

		return self.__Data["ignored_requests_errors"]
	
	@property 
	def title_not_found(self) -> bool:
		"""Указывает, нужно ли отправлять отчёт для данного типа записи."""

		return self.__Data["title_not_found"]
	
	@property 
	def chapter_not_found(self) -> bool:
		"""Указывает, нужно ли отправлять отчёт для данного типа записи."""

		return self.__Data["chapter_not_found"]
	
	@property 
	def downloading_error(self) -> bool:
		"""Указывает, нужно ли отправлять отчёт для данного типа записи."""

		return self.__Data["downloading_error"]
	
	@property 
	def critical(self) -> bool:
		"""Указывает, нужно ли отправлять отчёт для данного типа записи."""

		return self.__Data["critical"]
	
	@property 
	def errors(self) -> bool:
		"""Указывает, нужно ли отправлять отчёт для данного типа записи."""

		return self.__Data["errors"]
	
	@property 
	def warnings(self) -> bool:
		"""Указывает, нужно ли отправлять отчёт для данного типа записи."""

		return self.__Data["warnings"]
	
	def __init__(self, data: dict):
		"""
		Набор правил отправки отчётов.
			data – словарь правил.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Data = data.copy()
		
		Default = {
			"attach_log": True,

			"forbidden_commands": [],
			"ignored_requests_errors": [],

			"title_not_found": True,
			"chapter_not_found": True,
			"downloading_error": True,

			"critical": True,
			"errors": True,
			"warnings": True
		}

		for Rule in Default.keys():
			if Rule not in self.__Data.keys(): self.__Data[Rule] = Default[Rule]

class TelebotSettings:
	"""Настройки бота Telegram."""

	@property 
	def enable(self) -> bool:
		"""Состояние: включена ли отправка отчётов в Telegram."""

		return self.__Data["enable"]
	
	@property 
	def bot_token(self) -> str | None:
		"""Токен бота Telegram."""

		return self.__Data["bot_token"]
	
	@property 
	def chat_id(self) -> int | None:
		"""Идентификатор чата Telegram."""

		return self.__Data["chat_id"]
	
	@property 
	def comment(self) -> str | None:
		"""Комментарий для отчёта."""

		return self.__Data["comment"]
	
	@property 
	def rules(self) -> ReportsRules:
		"""Набор правил отправки отчётов."""

		return self.__Rules
	
	def __init__(self, data: dict | None = None):
		"""
		Настройки бота Telegram
			data – словарь настроек для парсинга.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Data = data or {
			"enable": False,
			"bot_token": None,
			"chat_id": None,
			"comment": None,
			"rules": {}
		}

		self.__Rules = ReportsRules(self.__Data["rules"])

class LoggerSettings:
	"""Настройки логов."""

	@property 
	def cleaner(self) -> CleanerSettings:
		"""Правила очистки логов."""

		return self.__Cleaner
	
	@property 
	def telebot(self) -> TelebotSettings:
		"""Настройки бота Telegram."""

		return self.__Telebot

	def __init__(self, data: dict | None = None):
		"""
		Настройки логов.
			data – словарь настроек для парсинга.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Data = data or {
			"telebot": {},
			"cleaner": {}
		}

		self.__Telebot = None
		self.__Cleaner = None

		#---> Парсинг настроек.
		#==========================================================================================#
		for Key in ["telebot", "cleaner"]:
			if Key not in self.__Data.keys(): self.__Data[Key] = dict()

		self.__Telebot = TelebotSettings(self.__Data["telebot"])
		self.__Cleaner = CleanerSettings(self.__Data["cleaner"])

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Portals:
	"""Коллекция порталов CLI/логов для парсеров."""

	def __init__(self, logger: "Logger"):
		"""
		Коллекция порталов CLI/логов для парсеров.
			logger – менеджер портов CLI и логов.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Logger = logger

	#==========================================================================================#
	# >>>>> БАЗОВЫЕ ТИПЫ ПОРТАЛОВ <<<<< #
	#==========================================================================================#

	def critical(self, text: str):
		"""
		Портал критической ошибки.
			text – данные.
		"""

		self.__Logger.critical(text, stdout = True)

	def error(self, text: str):
		"""
		Портал ошибки.
			text – данные.
		"""

		self.__Logger.error(text, stdout = True)

	def info(self, text: str):
		"""
		Портал информациию
			text – данные.
		"""

		self.__Logger.info(text, stdout = True)

	def warning(self, text: str):
		"""
		Портал предупреждения.
			text – данные.
		"""

		self.__Logger.warning(text, stdout = True)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПОРТАЛОВ ОШИБОК <<<<< #
	#==========================================================================================#

	def chapter_not_found(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Шаблон ошибки: глава не найдена.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		self.__Logger.chapter_not_found(title, chapter)

	def request_error(self, response: WebResponse, text: str | None = None, exception: bool = True):
		"""
		Портал ошибки запроса.
			response – WEB-ответ;\n
			text – описание ошибки;\n
			exception – указывает, выбрасывать ли исключение.
		"""

		self.__Logger.request_error(response, text, exception)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПОРТАЛОВ ПРЕДУПРЕЖДЕНИЙ <<<<< #
	#==========================================================================================#

	def title_not_found(self, title: BaseTitle, exception: bool = True):
		"""
		Портал предупреждения: тайтл не найден.
			title – данные тайтла;\n
			exception – указывает, выбрасывать ли исключение.
		"""

		self.__Logger.title_not_found(title, exception)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПОРТАЛОВ <<<<< #
	#==========================================================================================#

	def chapter_skipped(self, title: BaseTitle, chapter: BaseChapter, comment: str | None = None):
		"""
		Портал уведомления о пропуске главы.
			title – данные тайтла;\n
			chapter – данные главы;\n
			comment – комментарий о причине пропуска главы.
		"""

		ChapterType = "Paid chapter" if chapter.is_paid else "Chapter"
		ChapterID = chapter.id if chapter.id else chapter.slug
		if ChapterID: ChapterID = " " + str(ChapterID)
		else: ChapterID = ""
		comment = f" {comment}" if comment else ""

		self.__Logger.info(f"Title: \"{title.slug}\" (ID: {title.id}). {ChapterType}{ChapterID} skipped.{comment}")
		print(f"{ChapterType}{ChapterID} skipped.{comment}")

	def collect_progress_by_page(self, page: int):
		"""
		Портал индикации прогресса сбора коллекции.
			page – номер обработанной страницы каталога.
		"""

		Text = f"Titles on page {page} collected."
		self.__Logger.info(Text)
		print(Text)

	def covers_unstubbed(self, title: BaseTitle):
		"""
		Портал уведомления о фильтрации заглушек обложек.
			title – данные тайтла.
		"""

		self.__Logger.info(f"Title: \"{title.slug}\" (ID: {title.id}). Stubs detected. Covers downloading will be skipped.")
		print("Stubs detected. Covers downloading will be skipped.")

class Logger:
	"""Коллекция порталов CLI/логов для парсеров."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def portals(self) -> Portals:
		"""Набор шаблонов ввода-вывода."""

		return self.__Portals

	@property
	def templates(self) -> Templates:
		"""Набор шаблонов ввода-вывода."""

		return Templates

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadSettings(self) -> LoggerSettings:
		"""Считвает настройки логов для конкретного парсера."""
		
		LoggerSettingsObject = LoggerSettings()

		if self.__ParserName:
			Path = f"Configs/{self.__ParserName}/logger.json"
			if os.path.exists(Path): LoggerSettingsObject = LoggerSettings(ReadJSON(Path))

		return LoggerSettingsObject

	def __RemoveControlCodes(self, text: str) -> str:
		"""
		Удаляет управляющие последовательности ANSI.
			text – обрабатываемый текст.
		"""

		Regex = r'\x1b(' \
             r'(\[\??\d+[hl])|' \
             r'([=<>a-kzNM78])|' \
             r'([\(\)][a-b0-2])|' \
             r'(\[\d{0,2}[ma-dgkjqi])|' \
             r'(\[\d+;\d+[hfy]?)|' \
             r'(\[;?[hf])|' \
             r'(#[3-68])|' \
             r'([01356]n)|' \
             r'(O[mlnp-z]?)|' \
             r'(/Z)|' \
             r'(\d+)|' \
             r'(\[\?\d;\d0c)|' \
             r'(\d;\dR))'
		CompiledRegex = re.compile(Regex, flags = re.IGNORECASE)

		return CompiledRegex.sub("", text)

	def __SendReport(self, description: str):
		"""
		Отправляет сообщение в чат Telegram.
			description – описание ошибки.
		"""

		if self.__LoggerSettings.telebot.enable and self.__PointName not in self.__LoggerSettings.telebot.rules.forbidden_commands:
			Token = self.__LoggerSettings.telebot.bot_token
			description = Markdown(description).escaped_text
			Bot = telebot.TeleBot(Token)
			LaunchArguments = list(sys.argv)
			LaunchArguments.pop(0)
			Command = Markdown(" ".join(LaunchArguments)).escaped_text
			Comment = ("*Comment:* " + self.__LoggerSettings.telebot.comment + "\n") if self.__LoggerSettings.telebot.comment else ""
			Message = f"*Parser:* {self.__ParserName}\n{Comment}*Command:* `{Command}`\n\n_{description}_"

			if Message != self.__ErrorCache:
				self.__ErrorCache = Message
				
				try:
					if self.__LoggerSettings.telebot.rules.attach_log:
						Bot.send_document(
							self.__LoggerSettings.telebot.chat_id,
							document = open(self.__LogFilename, "rb"), 
							caption = Message,
							parse_mode = "MarkdownV2"
						)

					else:
						Bot.send_message(
							self.__LoggerSettings.telebot.chat_id,
							Message,
							parse_mode = "MarkdownV2"
						)

				except: logging.error("TeleBot error occurs during sending report.")

		self.__SilentMode = False

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: "SystemObjects"):
		"""
		Менеджер портов CLI и логов
			system_objects – коллекция системных объектов.
		"""
		
		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__SystemObjects = system_objects

		self.__Portals = Portals(self)
		self.__LoggerSettings = LoggerSettings()

		self.__LogFilename = None
		self.__ParserName = None
		self.__PointName = None
		self.__ErrorCache = None
		self.__SilentMode = False
		self.__LoggerRule = LoggerRules.Save
		self.__IsLogHasError = False
		self.__IsLogHasWarning = False

		#---> Настройка логов.
		#==========================================================================================#
		if not os.path.exists("Logs"): os.makedirs("Logs")
		CurrentDate = datetime.now()
		self.__LogFilename = "Logs/" + str(CurrentDate)[:-7] + ".log"
		self.__LogFilename = self.__LogFilename.replace(":", "-")
		logging.basicConfig(filename = self.__LogFilename, encoding = "utf-8", level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")

	def select_cli_point(self, point_name: str):
		"""
		Задаёт точку CLI для обработки фильтров логов.
			point_name – название точки.
		"""

		self.__PointName = point_name

	def select_parser(self, parser_name: str):
		"""
		Задаёт парсер, для которого будут применены настройки логгирования.
			parser_name – название парсера.
		"""

		self.__ParserName = parser_name
		self.__LoggerSettings = self.__ReadSettings()

	def set_rule(self, rule: int | LoggerRules):
		"""
		Задаёт правило обработки логов.
			rule – индекс правила или само правило.
		"""

		if type(rule) == int: self.__LoggerRule = LoggerRules(rule)
		else: self.__LoggerRule = rule

	#==========================================================================================#
	# >>>>> БАЗОВЫЕ ТИПЫ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def critical(self, text: str, stdout: bool = False, log: bool = True):
		"""
		Записывает в лог критическую ошибку.
			text – текст критической ошибки;\n
			stdout – указывает, помещать ли данные в поток стандартного вывода;\n
			log – указывает, делать ли запись в лог.
		"""

		if stdout: print(TextStyler("[CRITICAL]").colorize.red, TextStyler(text).colorize.red)
		text = self.__RemoveControlCodes(text)

		if log:
			logging.critical(text)
			self.__IsLogHasError = True

		if not self.__SilentMode and self.__LoggerSettings.telebot.rules.critical: self.__SendReport(text)

	def error(self, text: str, stdout: bool = False, log: bool = True):
		"""
		Записывает в лог ошибку.
			text – текст ошибки;\n
			stdout – указывает, помещать ли данные в поток стандартного вывода;\n
			logs – указывает, делать ли запись в лог.
		"""

		if stdout: print(TextStyler("[ERROR]").colorize.red, TextStyler(text).colorize.red)
		text = self.__RemoveControlCodes(text)

		if log:
			logging.error(text)
			self.__IsLogHasError = True

		if not self.__SilentMode and self.__LoggerSettings.telebot.rules.errors: self.__SendReport(text)

	def info(self, text: str, stdout: bool = False, log: bool = True):
		"""
		Записывает в лог информацию.
			text – информация;\n
			stdout – указывает, помещать ли данные в поток стандартного вывода;\n
			log – указывает, делать ли запись в лог.
		"""

		if stdout: print(text)
		text = self.__RemoveControlCodes(text)
		if log: logging.info(text)

	def warning(self, text: str, stdout: bool = False, log: bool = True):
		"""
		Записывает в лог предупреждение.
			text – описание предупреждения;\n
			stdout – указывает, помещать ли данные в поток стандартного вывода;\n
			log – указывает, делать ли запись в лог.
		"""

		if stdout: print(TextStyler("[WARNING]").colorize.yellow, TextStyler(text).colorize.yellow)
		text = self.__RemoveControlCodes(text)

		if log:
			logging.warning(text)
			self.__IsLogHasWarning = True
		
		if not self.__SilentMode and self.__LoggerSettings.telebot.rules.warnings: self.__SendReport(text)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ОШИБОК <<<<< #
	#==========================================================================================#

	def chapter_not_found(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Шаблон ошибки: глава не найдена.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Chapter {chapter.id} not found.")
		print(f"Chapter {chapter.id} not found.")

	def request_error(self, response: WebResponse, text: str | None = None, exception: bool = True):
		"""
		Шаблон ошибки запроса.
			response – WEB-ответ;\n
			text – описание ошибки;\n
			exception – указывает, выбрасывать ли исключение.
		"""

		if not text: text = "Request error."
		Text = f"{text} Response code: {response.status_code}."

		if response.status_code not in self.__LoggerSettings.telebot.rules.ignored_requests_errors:
			self.__SendReport(Text)
			self.__SilentMode = True

		self.error(Text, stdout = True)
		self.__SilentMode = False
		if exception: raise ParsingError()

	def unsupported_format(self, title: BaseTitle, exception: bool = False):
		"""
		Шаблон ошибки: неподдерживаемый формат JSON.
			title – данные тайтла;\n
			exception – указывает, выбрасывать ли исключение.
		"""

		Text = "Unsupported JSON format. Will be overwritten."
		self.warning(f"Title: \"{title.slug}\" (ID: {title.id}). {Text}")
		print(TextStyler("[WARNING] " + Text).colorize.yellow)
		if exception: raise ParsingError()

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПРЕДУПРЕЖДЕНИЙ <<<<< #
	#==========================================================================================#

	def title_not_found(self, title: BaseTitle, exception: bool = True):
		"""
		Шаблон предупреждения: тайтл не найден.
			title – данные тайтла;\n
			exception – указывает, выбрасывать ли исключение.
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""
		Text = f"Title: \"{title.slug}\"{NoteID}. Not found."

		if self.__LoggerSettings.telebot.rules.title_not_found:
			self.__SendReport(Text)
			self.__SilentMode = True

		self.warning(Text)
		print(TextStyler("[WARNING] Title not found.").colorize.yellow)
		self.__SilentMode = False
		if exception: raise TitleNotFound(title)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def amending_end(self, title: BaseTitle, amended_chapter_count: int):
		"""
		Шаблон: дополнение глав завершено.
			title – данные тайтла;\n
			amended_chapter_count – количество дополненных глав.
		"""

		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Amended chapters count: {amended_chapter_count}.")
		print(f"Amended chapters count: {amended_chapter_count}.")

	def chapter_amended(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Шаблон: глава дополнена.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). {ChapterNote} {chapter.id} amended.")
		print(f"{ChapterNote} {chapter.id} amended.")

	def chapter_repaired(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Шаблон: глава восстановлена.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). {ChapterNote} {chapter.id} repaired.")
		print(f"{ChapterNote} {chapter.id} repaired.")
		
	def merging_end(self, title: BaseTitle, merged_chapter_count: int):
		"""
		Шаблон: слияние глав завершено.
			title – данные тайтла;\n
			merged_chapter_count – количество дополненных глав.
		"""

		if self.__SystemObjects.FORCE_MODE:
			self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Local data will be removed.")
			print("Local data will be removed.")

		else:
			self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Merged chapters count: {merged_chapter_count}.")
			print(f"Merged chapters count: {merged_chapter_count}.")

	def parsing_start(self, title: BaseTitle, index: int, titles_count: int):
		"""
		Шаблон: начат парсинг.
			title – данные тайтла;\n
			index – индекс текущего тайтла;\n
			titles_count – количество тайтлов в задаче.
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""
		self.info(f"Title: \"{title.slug}\"{NoteID}. Parsing...")
		BoldSlug = TextStyler(title.slug).decorate.bold
		if titles_count > 1: Templates.parsing_progress(index, titles_count)
		print(f"Parsing {BoldSlug}{NoteID}...")

	def titles_collected(self, count: int):
		"""
		Шаблон: коллекция собрана.
			count – количество собранных алиасов.
		"""

		self.info(f"Collected titles count: {count}.")
		print(f"Titles collected: {count}.")

	#==========================================================================================#
	# >>>>> МЕТОДЫ УПРАВЛЕНИЯ ЛОГАМИ <<<<< #
	#==========================================================================================#

	def close(self):
		"""Закрывает логи."""

		if not self.__LoggerRule: self.set_rule(self.__LoggerSettings.cleaner[self.__PointName])

		self.info("====== End ======")
		logging.shutdown()

		IsClean = False

		if self.__LoggerRule == LoggerRules.Remove: IsClean = True
		if self.__LoggerRule == LoggerRules.SaveIfHasErrors and not self.__IsLogHasError: IsClean = True
		if self.__LoggerRule == LoggerRules.SaveIfHasWarnings and not self.__IsLogHasWarning and not self.__IsLogHasError: IsClean = True

		if IsClean and os.path.exists(self.__LogFilename): os.remove(self.__LogFilename)

		try: os.rmdir("Logs")
		except: pass