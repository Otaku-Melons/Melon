from telebot.types import InputMediaDocument
from dublib.WebRequestor import WebResponse
from dublib.Polyglot import Markdown
from dublib.Methods import ReadJSON
from datetime import datetime
from time import sleep

import logging
import telebot
import time
import sys
import os

class Logger:
	"""Менеджер логов."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadSettings(self) -> dict:
		"""Считвает настройки логов для конкретного парсера."""

		# Настройки.
		Settings = dict()
		# Если файл логов существует, прочитать его содержимое.
		if os.path.exists(f"Parsers/{self.__ParserName}/logger.json"): Settings = ReadJSON(f"Parsers/{self.__ParserName}/logger.json")
		
		return Settings

	def __SendReport(self, description: str):
		"""
		Отправляет сообщение в чат Telegram.
			description – описание ошибки.
		"""

		# Если заданы настройки и включено получение отчётов через Telegram.
		if self.__LoggerSettings and "telebot" in self.__LoggerSettings.keys() and self.__LoggerSettings["telebot"]["enable"]:
			# Токен бота.
			Token = self.__LoggerSettings["telebot"]["bot_token"]
			# Экранирование описания.
			description = Markdown(description).escaped_text
			# Инициализация бота.
			Bot = telebot.TeleBot(Token)
			# Очистка параметров запуска.
			LaunchArguments = list(sys.argv)
			LaunchArguments.pop(0)
			# Команда запуска.
			Command = Markdown(" ".join(LaunchArguments)).escaped_text
			# Комментарий.
			Comment = ("*Comment:* " + self.__LoggerSettings["telebot"]["comment"] + "\n") if self.__LoggerSettings["telebot"]["comment"] else ""
			# Описание ошибки.
			Message = f"*Parser:* {self.__ParserName}\n{Comment}*Command:* `{Command}`\n\n_{description}_"

			# Если сообщение не кэшировано.
			if Message != self.__ErrorCache:
				# Кэширование сообщения.
				self.__ErrorCache = Message

				# Если нужно прикрепить файл лога.
				if self.__LoggerSettings["telebot"]["attach_log"]:
					# Отправка лога с данными.
					Bot.send_document(
						self.__LoggerSettings["telebot"]["chat_id"],
						document = open(self.__LogFilename, "rb"), 
						caption = Message,
						parse_mode = "MarkdownV2"
					)

				else:
					# Отправка сообщения.
					Bot.send_message(
						self.__LoggerSettings["telebot"]["chat_id"],
						Message,
						parse_mode = "MarkdownV2"
					)

		# Отключение тихого режима.
		self.__SilentMode = False

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Менеджер логов."""
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Путь к файлу лога.
		self.__LogFilename = None
		# Название парсера.
		self.__ParserName = None
		# Название точки CLI.
		self.__PointName = None
		# Текущие настройки логгирования.
		self.__LoggerSettings = dict()
		# Кэш описания ошибки.
		self.__ErrorCache = None
		# Состояние: включён ли тихий режим.
		self.__SilentMode = False

		#---> Настройка логов.
		#==========================================================================================#
		# Если каталог логов не существует, создать его.
		if not os.path.exists("Logs"): os.makedirs("Logs")
		# Получение текущей даты.
		CurrentDate = datetime.now()
		# Время запуска скрипта.
		StartTime = time.time()
		# Формирование пути к файлу лога.
		self.__LogFilename = "Logs/" + str(CurrentDate)[:-7] + ".log"
		self.__LogFilename = self.__LogFilename.replace(":", "-")
		# Установка конфигнурации.
		logging.basicConfig(filename = self.__LogFilename, encoding = "utf-8", level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")		

	def select_cli_point(self, point_name: str):
		"""
		Задаёт точку CLI для обработки фильтров логов.
			point_name – название точки.
		"""

		# Сохранение названия.
		self.__PointName = point_name

	def select_parser(self, parser_name: str):
		"""
		Задаёт парсер, для которого будут применены настройки логгирования.
			parser_name – название парсера.
		"""

		# Сохранение названия.
		self.__ParserName = parser_name
		# Чтение настроек логов.
		self.__LoggerSettings = self.__ReadSettings()

	#==========================================================================================#
	# >>>>> БАЗОВЫЕ ТИПЫ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def critical(self, text: str):
		"""
		Записывает в лог критическую ошибку.
			text – данные.
		"""

		# Запись в лог критической ошибки.
		logging.critical(text)
		# Если не включен тихий режим, отправить отчёт.
		if not self.__SilentMode: self.__SendReport(text)

	def error(self, text: str):
		"""
		Записывает в лог ошибку.
			text – данные.
		"""

		# Запись в лог ошибки.
		logging.error(text)
		# Если не включен тихий режим, отправить отчёт.
		if not self.__SilentMode: self.__SendReport(text)

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

		logging.warning(text)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ТИПОВ ЗАПИСЕЙ <<<<< #
	#==========================================================================================#

	def amending_end(self, slug: str, title_id: int, chapters_cont: int):
		"""
		Записывает в лог информацию о количестве дополненных глав.
			slug – алиас;
			title_id – целочисленный идентификатор тайтла;
			chapters_cont – количество дополненных глав.
		"""

		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\" (ID: {title_id}). Amended chapters count: {chapters_cont}.")

	def chapter_amended(self, slug: str, title_id: int, chapter_id: int, is_paid: bool):
		"""
		Записывает в лог данные дополненной главы.
			slug – алиас;
			title_id – целочисленный идентификатор тайтла;
			chapter_id – идентификатор главы;
			is_paid – является ли глава платной.
		"""

		# Составление типа главы.
		Chapter = "Paid chapter" if is_paid else "Chapter"
		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\" (ID: {title_id}). {Chapter} {chapter_id} amended.")

	def chapter_repaired(self, slug: str, title_id: int, chapter_id: int, is_paid: bool):
		"""
		Записывает в лог данные дополненной главы.
			slug – алиас;
			title_id – целочисленный идентификатор тайтла;
			chapter_id – идентификатор главы;
			is_paid – является ли глава платной.
		"""

		# Составление типа главы.
		Chapter = "Paid chapter" if is_paid else "Chapter"
		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\" (ID: {title_id}). {Chapter} {chapter_id} repaired.")

	def chapter_skipped(self, slug: str, title_id: int, chapter_id: int, is_paid: bool):
		"""
		Записывает в лог данные дополненной главы.
			slug – алиас;
			title_id – целочисленный идентификатор тайтла;
			chapter_id – идентификатор главы;
			is_paid – является ли глава платной.
		"""

		# Составление типа главы.
		Chapter = "Paid chapter" if is_paid else "Chapter"
		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\" (ID: {title_id}). {Chapter} {chapter_id} skipped.")

	def covers_unstubbed(self, slug: str, title_id: int):
		"""
		Записывает в лог информацию об удалении обложек по причине того, что те являются заглушками.
			title_id – целочисленный идентификатор тайтла;
			slug – алиас.
		"""

		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\" (ID: {title_id}). Stubs detected. Covers downloading will be skipped.")

	def parsing_start(self, slug: str, title_id: int):
		"""
		Записывает в лог сообщение об успешном парсинге данных тайтла.
			title_id – целочисленный идентификатор тайтла;
			slug – алиас.
		"""

		# Запись в лог информации.
		logging.info(f"Title: \"{slug}\" (ID: {title_id}). Parsing...")

	def request_error(self, response: WebResponse, text: str | None = None):
		"""
		Обрабатывает ошибку сети.
			response – объект WEB-ответа;
			text – описание ошибки.
		"""

		# Если не передано описание, использовать стандартное.
		if not text: text = "Request error."
		# Если ошибка игнорируется, включить тихий режим.
		if response.status_code in self.__LoggerSettings["rules"][self.__PointName]["ignored_requests_errors"]: self.__SilentMode = True
		# Запись в лог ошибки.
		self.error(f"{text} Response code: {response.status_code}.")

	def titles_collected(self, titles_count: int):
		"""
		Записывает в лог количество собранных из каталога тайтлов.
			titles_count – количество тайтлов.
		"""

		# Запись в лог информации.
		logging.info(f"Titles collected: {titles_count}.")

	def updates_collected(self, updates_count: int):
		"""
		Записывает в лог количество полученных обновлений.
			updates_count – количество обновлений.
		"""

		# Запись в лог информации.
		logging.info(f"Updates found: {updates_count}.")

	#==========================================================================================#
	# >>>>> МЕТОДЫ УПРАВЛЕНИЯ ЛОГАМИ <<<<< #
	#==========================================================================================#

	def close(self, clean: bool = False):
		"""
		Закрывает логи.
			clean – Указывает, нужно ли удалить файл лога.
		"""

		# Запись в лог: заголовок конца лога.
		logging.info("====== End ======")
		# Отключение логов.
		logging.shutdown()
		# Если указано и файл существует, удалить его.
		if clean and os.path.exists(self.__LogFilename): os.remove(self.__LogFilename)