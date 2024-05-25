from Source.Core.Downloader import Downloader
from Source.Core.Objects import Objects

from dublib.Terminalyzer import CommandData
from dublib.Methods import Cls

def com_get(system_objects: Objects, command: CommandData):
	"""
	Скачивает изображение.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	# Запись в лог информации: заголовок парсинга.
	system_objects.logger.info("====== Downloading ======")
	# Определение каталога и имени файла.
	Directory = command.values["dir"] if "dir" in command.keys else None
	Filename = command.values["name"] if "name" in command.keys else None
	if "fullname" in command.keys: Filename = command.values["fullname"]
	FullName = True if "fullname" in command.keys else False
	# Вывод в консоль: загрузка.
	print(f"URL: {command.arguments[0]}\nDownloading... ", end = "")
	# Загрузка изображения.
	Downloader(system_objects, exception = True).image(command.arguments[0], command.values["site"], Directory, Filename, FullName)
	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Вывод в консоль: завершение загрузки.
	print("Done.")

def com_list(system_objects: Objects):
	"""
	Выводит список парсеров в консоль.
		system_objects – коллекция системных объектов.
	"""

	# Список названий.
	ParsersList = system_objects.manager.parsers_names
	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 

	# Для каждого парсера.
	for Parser in ParsersList:
		# Получение данных парсера.
		Version = system_objects.manager.get_parser_version(Parser)
		Site = system_objects.manager.get_parser_site(Parser)
		# Вывод в консоль: название и версия парсера.
		print(f"{Parser} ({Site}) – {Version}")

def com_parse(system_objects: Objects, command: CommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	# Очистка консоли.
	Cls()
	# Название парсера.
	ParserName = command.values["use"]
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName, system_objects)
	# Настройки парсера.
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	# Запись в лог информации: заголовок парсинга.
	system_objects.logger.info("====== Parsing ======")
	# Алиасы тайтлов.
	Slugs = list()
	# Индекс стартового алиаса.
	StartIndex = 0
	
	# Если активирован флаг парсинга коллекции.
	if "collection" in command.flags:
		# Индекс обрабатываемого тайтла.
		CurrentTitleIndex = 0
		
		# Открытие потока чтения.
		with open(f"Source/Parsers/{ParserName}/Collection.txt", "r") as FileReader:
			# Буфер чтения.
			Buffer = FileReader.read().split("\n")
			
			# Для каждой строки.
			for Line in Buffer:
				# Если строка не пуста, добавить её в список алиасов.
				if Line.strip(): Slugs.append(Line)

		# Запись в лог информации: количество тайтлов в коллекции.
		system_objects.logger.collection_size(f"Titles in collection: {len(Slugs)}.")
		
	# Если активирован флаг обновления локальных файлов.
	elif "local" in command.flags:
		# # Вывод в консоль: идёт поиск тайтлов.
		# print("Scanning titles...")
		# # Получение списка файлов в директории.
		# Slugs = os.listdir(Settings["titles-directory"])
		# # Фильтрация только файлов формата JSON.
		# Slugs = list(filter(lambda x: x.endswith(".json"), Slugs))
			
		# # Чтение всех алиасов из локальных файлов.
		# for File in Slugs:
		# 	# Открытие локального описательного файла JSON.
		# 	with open(Settings["titles-directory"] + "/" + File, encoding = "utf-8") as FileRead:
		# 		# JSON файл тайтла.
		# 		LocalTitle = json.load(FileRead)
		# 		# Помещение алиаса в список.
		# 		TitlesList.append(str(LocalTitle["slug"]) if "slug" in LocalTitle.keys() else str(LocalTitle["dir"]))

		# # Запись в лог информации: количество доступных для парсинга тайтлов.
		# logging.info("Local titles to parsing: " + str(len(TitlesList)) + ".")
		pass

	else:
		# Запись аргумента в качестве цели парсинга.
		Slugs.append(command.arguments[0])
		
	# Если указан стартовый тайтл.
	if "from" in command.keys:
		# Запись в лог информации: стартовый тайтл парсинга.
		system_objects.logger.info("Processing will be started from slug: \"" + command.values["from"] + "\".")
				
		# Если стартовый алиас найден.
		if command.values["from"] in Slugs:
			# Указать индекс алиаса в качестве стартового.
			StartIndex = Slugs.index(command.values["from"])
			
		else:
			# Запись в лог предупреждения: стартовый алиас не найден.
			system_objects.logger.warning("No starting slug in collection. Ignored.")

	# Парсинг тайтлов.
	for Index in range(StartIndex, len(Slugs)):

		#---> Парсинг базовых данных.
		#==========================================================================================#
		Title = system_objects.manager.get_parser_struct(ParserName)
		Parser.parse(Slugs[Index])
		Title.set_site(Parser.site)
		Title.set_id(Parser.id)
		Title.set_slug(Parser.slug)
		Title.set_ru_name(Parser.ru_name)
		Title.set_en_name(Parser.en_name)
		Title.set_another_names(Parser.another_names)
		Title.set_covers(Parser.covers)
		Title.set_authors(Parser.authors)
		Title.set_publication_year(Parser.publication_year)
		Title.set_description(Parser.description)
		Title.set_age_limit(Parser.age_limit)
		Title.set_genres(Parser.genres)
		Title.set_tags(Parser.tags)
		Title.set_franchises(Parser.franchises)
		Title.set_type(Parser.type)
		Title.set_status(Parser.status)
		Title.set_is_licensed(Parser.is_licensed)
		Title.set_content(Parser.content)

		#---> Получение дополнительных данных.
		#==========================================================================================#
		# Сообщение для внутреннего обработчика.
		Message = system_objects.MSG_SHUTDOWN + system_objects.MSG_FORCE_MODE
		# Используемое имя файла.
		Filename = Parser.id if ParserSettings["common"]["use_id_as_filename"] else Parser.slug
		# Состояние: используется ли устаревший формат.
		Legacy = True if ParserSettings["common"]["legacy"] else False

		#---> Обработка содержимого.
		#==========================================================================================#
		Title.merge(system_objects, ParserSettings["common"]["titles_directory"], Filename)
		Title.amend(Parser.amend, Message)
		Title.download_covers(system_objects, ParserSettings["common"]["covers_directory"], Filename, Message)
		Title.save(system_objects, ParserSettings["common"]["titles_directory"], Filename, Legacy)

	# Очистка консоли.
	Cls()

def com_repair(system_objects: Objects, command: CommandData):
	"""
	Выполняет парсинг тайтла.
		system_objects – коллекция системных объектов;
		command – объект представления консольной команды.
	"""

	# Очистка консоли.
	Cls()
	# Название парсера.
	ParserName = command.values["use"]
	# Инициализация парсера.
	Parser = system_objects.manager.launch(ParserName, system_objects)
	# Настройки парсера.
	ParserSettings = system_objects.manager.get_parser_settings(ParserName)
	# Запись в лог информации: заголовк восстановления.
	system_objects.logger.info("====== Repairing ======")
	# Имя описательного файла.
	Filename = Filename[:-5] if command.arguments[0].endswith(".json") else command.arguments[0]
	# Вывод в консоль: идёт процесс восстановления главы.
	print("Repairing...")

	#---> Восстановление главы.
	#==========================================================================================#
	Title = system_objects.manager.get_parser_struct(ParserName)
	Title.open(system_objects, ParserSettings["common"]["titles_directory"], Filename)
	Parser.parse(Title.slug)
	Title.repair(Parser.repair, int(command.values["chapter"]))
	Title.save(system_objects, ParserSettings["common"]["titles_directory"], Filename)

	# Включение удаление лога.
	system_objects.REMOVE_LOG = True 
	# Очистка консоли.
	Cls()