from Source.Core.Formats import BaseChapter, BaseTitle
from Source.Core.Exceptions import ParsingError

from dublib.WebRequestor import WebResponse
from dublib.Methods.JSON import ReadJSON
from dublib.Polyglot import Markdown
from datetime import datetime

import logging
import telebot
import enum
import sys
import os

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

class Command:
	"""Фильтры вывода команды."""

	@property
	def rule(self) -> LoggerRules:
		"""Правило обработки логов."""

		return self.__Data["rule"]
	
	@property
	def ignored_requests_errors(self) -> list[any]:
		"""Список игнорируемых кодов ошибок запросов."""

		return self.__Data["ignored_requests_errors"]
	
	@property
	def warnings(self) -> LoggerRules:
		"""Указывает, стоит ли обращать внимание на предупреждения при обработке ошибок."""

		return self.__Data["rule"]
	
	@property
	def title_not_found(self) -> LoggerRules:
		"""Указывает, стоит ли обращать внимание на ошибки типа: TitleNotFound."""

		return self.__Data["title_not_found"]

	def __init__(self, data: dict | None = None):
		"""
		Фильтры вывода команды.
			data – словарь фильтров для парсинга.
		"""

		Default = {
			"rule": LoggerRules.Remove,
			"warnings": True,

			"ignored_requests_errors": [],
			"title_not_found": True
		}

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Data = data or dict()

		for Key in Default.keys():
			if Key not in self.__Data.keys(): self.__Data[Key] = Default[Key]

class CommandsSettings:
	"""Фильтры вывода команд."""

	def __init__(self, data: dict | None = None):
		"""
		Настройки бота Telegram
			data – словарь настроек для парсинга.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Filters = dict()

		for Key in data.keys(): self.__Filters[Key] = Command(data[Key])

	def __getitem__(self, command: str) -> Command:
		"""Возвращает контейнер фильтров вывода."""

		if command in self.__Filters.keys(): return self.__Filters[command]

		return Command()

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
	def attach_log(self) -> bool:
		"""Указывает, нужно ли прикреплять лог к отчёту."""

		return self.__Data["attach_log"]
	
	def __init__(self, data: dict | None = None):
		"""
		Настройки бота Telegram
			data – словарь настроек для парсинга.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Data = data or {
			"enable": False,
			"bot_token": None,
			"chat_id": None,
			"comment": None,
			"attach_log": True
		}

class LoggerSettings:
	"""Настройки логов."""

	@property 
	def commands(self) -> CommandsSettings:
		"""Фильтры вывода команд."""

		return self.__Commands
	@property 
	def telebot(self) -> TelebotSettings:
		"""Настройки бота Telegram."""

		return self.__Telebot

	def __init__(self, data: dict | None = None):
		"""
		Настройки логов.
			data – словарь настроек для парсинга.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Data = data or {
			"telebot": {},
			"commands": {}
		}

		self.__Telebot = None
		self.__Commands = None

		#---> Парсинг настроек.
		#==========================================================================================#
		for Key in ["telebot", "commands"]:
			if Key not in self.__Data.keys(): self.__Data[Key] = dict()

		self.__Telebot = TelebotSettings(self.__Data["telebot"])
		self.__Commands = CommandsSettings(self.__Data["commands"])

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Logger:
	"""Менеджер логов."""

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

	def __SendReport(self, description: str):
		"""
		Отправляет сообщение в чат Telegram.
			description – описание ошибки.
		"""

		if self.__LoggerSettings.telebot.enable:
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

				if self.__LoggerSettings.telebot.attach_log:
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

		self.__SilentMode = False

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер логов."""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
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

	def critical(self, text: str):
		"""
		Записывает в лог критическую ошибку.
			text – данные.
		"""

		self.__IsLogHasError = True
		logging.critical(text)
		if not self.__SilentMode: self.__SendReport(text)

	def error(self, text: str, exception: bool = False):
		"""
		Записывает в лог ошибку.
			text – данные;\n
			exception – указывает, нужно ли выбрасывать исключение.
		"""

		self.__IsLogHasError = True
		logging.error(text)
		if not self.__SilentMode: self.__SendReport(text)
		if exception: raise ParsingError()

	def info(self, text: str):
		"""
		Записывает в лог информацию.
			text – данные.
		"""

		logging.info(text)

	def warning(self, text: str):
		"""
		Записывает в лог предупреждение.
			text – данные.
		"""

		self.__IsLogHasWarning = True
		logging.warning(text)

		try: 
			if self.__LoggerSettings.commands[self.__PointName].warnings: self.__SendReport(text)
			
		except KeyError: pass

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ПРЕДУПРЕЖДЕНИЙ <<<<< #
	#==========================================================================================#

	def collect_filters_ignored(self):
		"""Записывает в лог предупреждение: игнорирование фильтров."""

		self.warning(f"Filters will be ignored.")

	def collect_pages_ignored(self):
		"""Записывает в лог предупреждение: игнорирование страниц."""

		self.warning(f"Pages will be ignored.")

	def collect_period_ignored(self):
		"""Записывает в лог предупреждение: игнорирование периода."""

		self.warning(f"Period will be ignored.")

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ОШИБОК <<<<< #
	#==========================================================================================#

	def request_error(self, response: WebResponse, text: str | None = None, exception: bool = True):
		"""
		Обрабатывает ошибку сети.
			response – объект WEB-ответа;\n
			text – описание ошибки;\n
			exception – указывает, выбрасывать ли исключение.
		"""

		if not text: text = "Request error."
		if response.status_code in self.__LoggerSettings.commands[self.__PointName].ignored_requests_errors: self.__SilentMode = True
		self.error(f"{text} Response code: {response.status_code}.", exception = exception)

	def title_not_found(self, title: BaseTitle):
		"""
		Записывает в лог предупреждение о том, что тайтл не найден в источнике.
			title – данные тайтла.
		"""

		NoteID = f" (ID: {title.id})" if title.id else ""
		if not self.__LoggerSettings.commands[self.__PointName].title_not_found: self.__SilentMode = True
		self.error(f"Title: \"{title.slug}\"{NoteID}. Not found.")

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def amending_end(self, title: BaseTitle, amended_chapter_count: int):
		"""
		Записывает в лог информацию о количестве дополненных глав.
			title – данные тайтла;\n
			amended_chapter_count – количество дополненных глав.
		"""

		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Amended chapters count: {amended_chapter_count}.")

	def chapter_amended(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Записывает в лог отчёт о дополнении главы.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). {ChapterNote} {chapter.id} amended.")

	def chapter_repaired(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Записывает в лог отчёт о восстановлении главы.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). {ChapterNote} {chapter.id} repaired.")

	def chapter_skipped(self, title: BaseTitle, chapter: BaseChapter):
		"""
		Записывает в лог отчёт о пропуске главы.
			title – данные тайтла;\n
			chapter – данные главы.
		"""

		ChapterNote = "Paid chapter" if chapter.is_paid else "Chapter"
		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). {ChapterNote} {chapter.id} skipped.")

	def collect_filters(self, filters: str):
		"""
		Записывает в лог сообщение: используемые фильтры коллекции.
			filters – фильтры.
		"""

		self.info(f"Filters: \"{filters}\".")

	def collect_pages(self, pages: int):
		"""
		Записывает в лог сообщение: используемые страницы коллекции.
			pages – страницы.
		"""

		self.info(f"Pages: {pages}.")

	def collect_period(self, period: int):
		"""
		Записывает в лог сообщение: используемый период коллекции.
			period – период.
		"""

		self.info(f"Period: {period} hours.")

	def covers_unstubbed(self, title: BaseTitle):
		"""
		Записывает в лог информацию об удалении обложек по причине того, что те являются заглушками.
			title – данные тайтла.
		"""

		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Stubs detected. Covers downloading will be skipped.")

	def parsing_start(self, title: BaseTitle):
		"""
		Записывает в лог сообщение об успешном парсинге данных тайтла.
			title – данные тайтла.
		"""

		self.info(f"Title: \"{title.slug}\" (ID: {title.id}). Parsing...")

	def titles_collected(self, collected_titles_count: int):
		"""
		Записывает в лог количество собранных из каталога тайтлов.
			titles_count – количество тайтлов.
		"""

		self.info(f"Titles collected: {collected_titles_count}.")

	#==========================================================================================#
	# >>>>> МЕТОДЫ УПРАВЛЕНИЯ ЛОГАМИ <<<<< #
	#==========================================================================================#

	def close(self):
		"""Закрывает логи."""

		if not self.__LoggerRule: self.set_rule(self.__LoggerSettings.commands[self.__PointName].rule)

		self.info("====== End ======")
		logging.shutdown()

		IsClean = False

		if self.__LoggerRule == LoggerRules.Remove: IsClean = True
		if self.__LoggerRule == LoggerRules.SaveIfHasErrors and not self.__IsLogHasError: IsClean = True
		if self.__LoggerRule == LoggerRules.SaveIfHasWarnings and not self.__IsLogHasWarning and not self.__IsLogHasError: IsClean = True

		if IsClean and os.path.exists(self.__LogFilename): os.remove(self.__LogFilename)

		try: os.rmdir("Logs")
		except: pass