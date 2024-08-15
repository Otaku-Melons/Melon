from Source.Core.Objects import Objects

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Engine.Bus import ExecutionError, ExecutionStatus
from dublib.Methods.Filesystem import NormalizePath
from dublib.WebRequestor import WebRequestor

import os

class Downloader:
	"""Загрузчик изображений."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetFilename(self, url: str) -> str:
		"""
		Определяет имя файла.
			url – ссылка на изображение.
		"""

		# Имя файла. 
		Filename = url.split("/")[-1]
		# Расширение фала.
		Filetype = self.__GetFiletype(url)
		# Удаление расширения.
		if Filetype: Filename = Filename[:len(Filetype) * -1]

		return Filename

	def __GetFiletype(self, url: str) -> str:
		"""
		Определяет расширение файла.
			url – ссылка на изображение.
		"""

		# Расширение файла. 
		Filetype = ""
		# Имя файла на сервере.
		ServerFilename = url.split("/")[-1]
		# Если в названии файла есть точка, определить расширение.
		if "." in ServerFilename: Filetype = "." + ServerFilename.split(".")[-1]

		return Filetype

	def __InitializeRequestor(self, parser_name: str) -> WebRequestor:
		"""
		Инициализирует модуль WEB-запросов.
			parser_name – название парсера.
		"""

		# Получение настроек парсера.
		Settings = self.__SystemObjects.manager.get_parser_settings(parser_name)
		# Инициализация и настройка объекта.
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_tries_count(Settings["common"]["tries"])
		Config.add_header("Authorization", Settings["custom"]["token"])
		WebRequestorObject = WebRequestor(Config)

		# Установка прокси.
		if Settings["proxy"]["enable"]: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = Settings["proxy"]["host"],
			port = Settings["proxy"]["port"],
			login = Settings["proxy"]["login"],
			password = Settings["proxy"]["password"]
		)
			
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, system_objects: Objects, requestor: WebRequestor | None = None, exception: bool = False, logging: bool = True):
		"""
		Загрузчик изображений.
			system_objects – коллекция системных объектов;\n
			requestor – менеджер запросов;\n
			exception – указывает, следует ли выбрасывать исключение;\n
			logging – указывает, нужно ли обрабатывать ошибку через системный объект логгирования.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects
		# Состояние: следует ли выбрасывать исключения.
		self.__RaiseExceptions = exception
		# Менеджер запросов.
		self.__Requestor = requestor
		# Состояние: нужно ли обрабатывать ошибку через системный объект логгирования.
		self.__Logging = logging

	def image(
			self,
		   	url: str,
			directory: str = "Temp",
			filename: str | None = None,
			is_full_filename: bool = False,
			referer: str | None = None
		) -> ExecutionStatus:
		"""
		Скачивает изображение.
			url – ссылка на изображение;\n
			directory – путь к каталогу загрузки;\n
			filename – имя файла;\n
			is_full_filename – указывает, является ли имя файла полным;\n
			referer – домен сайта для установка заголовка запроса Referer.
		"""

		# Если запросчик не инициализирован, выбросить исключение.
		if not self.__Requestor: raise Exception("Requestor not initialized.")
		# Состояние загрузки.
		Status = ExecutionStatus(0)
		# Нормализация пути.
		directory = NormalizePath(directory)

		#---> Определение параметров файла.
		#==========================================================================================#
		# Расширение файла.
		Filetype = ""
		# Если имя файла указано и не помечено как полное, получить расширение файла (с точкой).
		if not is_full_filename: Filetype = self.__GetFiletype(url)
		# Если имя файла не указано, получить его из URL.
		if not filename: filename = self.__GetFilename(url)

		#---> Выполнение загрузки.
		#==========================================================================================#
		# Состояние: существует ли файл.
		IsFileExists = os.path.exists(f"{directory}/{filename}{Filetype}")

		# Если файл не существует или включён режим перезаписи.
		if not IsFileExists or self.__SystemObjects.FORCE_MODE:
			# Заголовки запроса.
			Headers = None

			# Если указан домен сайта, добавить его в заголовок.
			if referer: Headers = {
				"Referer": f"https://{referer}/"
			}
				
			# Выполнение запроса.
			Response = self.__Requestor.get(url, headers = Headers)

			# Если запрос успешен
			if Response.status_code == 200:

				# Если получена значимая последовательность байтов.
				if len(Response.content) > 1000:

					# Открытие потока записи.
					with open(f"{directory}{filename}{Filetype}", "wb") as FileWriter:
						# Запись изображения.
						FileWriter.write(Response.content)
						# Изменение статуса.
						Status = ExecutionStatus(200)
						Status.value = filename + Filetype
						Status.message = "Done."

				else:
					# Запись в лог ошибки запроса.
					if self.__Logging: self.__SystemObjects.logger.error(Response, f"Image doesn't contain enough bytes: \"{url}\".")
					# Изменение статуса.
					Status = ExecutionError(204)
					Status.message = f"Error! Image doesn't contain enough bytes."

			else:
				# Запись в лог ошибки запроса.
				if self.__Logging: self.__SystemObjects.logger.request_error(Response, f"Unable to download image: \"{url}\".")
				# Изменение статуса.
				Status = ExecutionError(Response.status_code)
				Status.message = f"Error! Response code: {Response.status_code}."
				# Выброс исключения.
				if self.__RaiseExceptions: raise Exception(f"Unable to download image: \"{url}\". Response code: {Response.status_code}.")

		# Если файл уже существует.
		elif IsFileExists:
			# Изменение статуса.
			Status.message = "Already exists."

		return Status
	
	def move_from_temp(self, parser_name: str, directory: str, original_filename: str, filename: str | None = None, is_full_filename: bool = True) -> bool:
		"""
		Перемещает изображение из временного каталога парсера в другое расположение.
			parser_name – название парсера;\n
			directory – путь к каталогу загрузки;\n
			original_filename – имя файла во временном каталоге парсера;\n
			filename – имя файла в целевом каталоге;\n
			is_full_filename – указывает, является ли имя файла полным.
		"""
		
		try:
			# Оригинальное расположение.
			OriginalPath = f"Temp/{parser_name}/" + original_filename
			# Нормализация пути.
			directory = NormalizePath(directory)
			# Расширение файла.
			Filetype = ""
			
			# Если имя файла указано и не помечено как полное.
			if filename and not is_full_filename:
				# Получение расширение файла (с точкой).
				Filetype = self.__GetFiletype(original_filename)
				# Очистка имени файла от расширения.
				filename = self.__GetFilename(filename)
				
			# Если не указано имя файла, использовать оригинальное.
			elif not filename: filename = original_filename

			# Перемещение файла.
			os.replace(OriginalPath, f"{directory}{filename}{Filetype}")

		except: return False

		return True
	
	def temp_image(self, parser_name: str, url: str, referer: str | None = None):
		"""
		Скачивает изображение во временный каталог парсера.
			parser_name – название парсера;\n
			url – ссылка на изображение;\n
			referer – домен сайта для установка заголовка запроса Referer.
		"""

		# Если не указан загрузчик, инициализировать стандартный.
		if not self.__Requestor: self.__Requestor = self.__InitializeRequestor(parser_name)
		# Запоминание состояния логов.
		Logging = self.__Logging
		self.__Logging = False
		# Загрузка изображения во временный каталог.
		Result = self.image(
			url = url,
			directory = self.__SystemObjects.temper.get_parser_temp(parser_name),
			referer = referer
		)
		# Возвращение состояния логов.
		self.__Logging = Logging

		return Result