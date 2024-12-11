from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Engine.Bus import ExecutionError, ExecutionStatus
from dublib.Methods.Filesystem import NormalizePath
from dublib.WebRequestor import WebRequestor
from dublib.Methods.Data import Zerotify

import shutil
import os

class ImagesDownloader:
	"""Загрузчик изображений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def requestor(self) -> WebRequestor:
		"""Заданный менеджер запросов."""

		return self.__Requestor

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetFilename(self, url: str) -> str:
		"""
		Определяет имя файла.
			url – ссылка на изображение.
		"""

		Filename = url.split("/")[-1]
		Filetype = self.__GetFiletype(url)
		if Filetype: Filename = Filename[:len(Filetype) * -1]

		return Filename

	def __GetFiletype(self, url: str) -> str:
		"""
		Определяет расширение файла.
			url – ссылка на изображение.
		"""

		Filetype = ""
		ServerFilename = url.split("/")[-1]
		if "." in ServerFilename: Filetype = "." + ServerFilename.split(".")[-1]

		return Filetype

	def __InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.generate_user_agent()
		Config.set_retries_count(self.__ParserSettings.common.retries)
		Config.add_header("Authorization", self.__ParserSettings["custom"]["token"])
		WebRequestorObject = WebRequestor(Config)

		if self.__ParserSettings["proxy"]["enable"]: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = self.__ParserSettings["proxy"]["host"],
			port = self.__ParserSettings["proxy"]["port"],
			login = self.__ParserSettings["proxy"]["login"],
			password = self.__ParserSettings["proxy"]["password"]
		)
			
		return WebRequestorObject
			
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, system_objects: "SystemObjects", requestor: WebRequestor | None = None, logging: bool = True):
		"""
		Загрузчик изображений.
			system_objects – коллекция системных объектов;\n
			requestor – менеджер запросов;\n
			logging – указывает, нужно ли обрабатывать ошибку через системный объект логгирования.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__SystemObjects = system_objects
		self.__ParserSettings = self.__SystemObjects.manager.parser_settings
		self.__Requestor = requestor or self.__InitializeRequestor()
		self.__Logging = logging

	def image(self, url: str, directory: str | None = "", filename: str | None = None, is_full_filename: bool = False) -> ExecutionStatus:
		"""
		Скачивает изображение.
			url – ссылка на изображение;\n
			directory – путь к каталогу загрузки;\n
			filename – имя файла;\n
			is_full_filename – указывает, является ли имя файла полным.
		"""

		Status = ExecutionStatus(0)
		if directory == None: directory = ""
		directory = NormalizePath(directory)
		IsStubUsed = bool(self.__ParserSettings.common.bad_image_stub) if self.__ParserSettings.common.bad_image_stub else False

		#---> Определение параметров файла.
		#==========================================================================================#
		Filetype = ""
		if not is_full_filename: Filetype = self.__GetFiletype(url)
		if not filename: filename = self.__GetFilename(url)

		#---> Выполнение загрузки.
		#==========================================================================================#
		Path = f"{directory}/{filename}{Filetype}"
		IsFileExists = os.path.exists(Path)
		
		if not IsFileExists or self.__SystemObjects.FORCE_MODE:
			Response = self.__Requestor.get(url)
			
			if Response.status_code == 200:
				
				if len(Response.content) > 1000:
				
					with open(Path, "wb") as FileWriter:
						FileWriter.write(Response.content)
						Status = ExecutionStatus(200)
						Status.value = filename + Filetype
						Status.message = "Done."

				elif IsStubUsed:
					shutil.copy2(self.__ParserSettings.common.bad_image_stub, Path)
					if self.__Logging: self.__SystemObjects.logger.warning(f"Image doesn't contain enough bytes: \"{url}\". Replaced by stub.")
					Status = ExecutionError(200)
					Status.value = filename + Filetype
					Status.message = "Bad image. Replaced by stub."

				else:
					if self.__Logging: self.__SystemObjects.logger.error(f"Image doesn't contain enough bytes: \"{url}\".")
					Status = ExecutionError(204)
					Status.message = "Error! Image doesn't contain enough bytes."

			else:
				if self.__Logging: self.__SystemObjects.logger.request_error(Response, f"Unable to download image: \"{url}\".", exception = False)
				Status = ExecutionError(Response.status_code)
				Status.message = f"Error! Response code: {Response.status_code}."

		elif IsFileExists:
			Status.value = filename + Filetype
			Status.message = "Already exists."
		
		return Status
	
	def move_from_temp(self, directory: str, original_filename: str, filename: str | None = None, is_full_filename: bool = True) -> bool:
		"""
		Перемещает изображение из временного каталога парсера в другое расположение.
			directory – путь к каталогу загрузки;\n
			original_filename – имя файла во временном каталоге парсера;\n
			filename – имя файла в целевом каталоге;\n
			is_full_filename – указывает, является ли имя файла полным.
		"""
		
		try:
			OriginalPath = f"Temp/{self.__SystemObjects.parser_name}/" + original_filename
			directory = NormalizePath(directory)
			Filetype = ""
			
			if filename and not is_full_filename:
				Filetype = self.__GetFiletype(original_filename)
				filename = self.__GetFilename(filename)
				
			elif not filename: filename = original_filename

			os.replace(OriginalPath, f"{directory}/{filename}{Filetype}")

		except: return False

		return True
	
	def temp_image(self, url: str, filename: str | None = None, is_full_filename: bool = False) -> str | None:
		"""
		Скачивает изображение во временный каталог парсера.
			url – ссылка на изображение;\n
			filename – имя файла;\n
			is_full_filename – указывает, является ли имя файла полным.
		"""

		Result = self.image(
			url = url,
			directory = self.__SystemObjects.temper.parser_temp,
			filename = filename,
			is_full_filename = is_full_filename
		)

		return Zerotify(Result.value)