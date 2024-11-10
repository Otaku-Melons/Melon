from dublib.CLI.Terminalyzer import Command, ParametersTypes, ParsedCommandData, Terminalyzer
from dublib.Methods.Filesystem import ReadTextFile, WriteTextFile
from dublib.CLI.StyledPrinter import Styles, StyledPrinter

import shlex
import enum
import json
import os

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ ТИПОВ <<<<< #
#==========================================================================================#

class ClassificatorsTypes(enum.Enum):
	"""Перечисление типов классификаторов."""

	Franchise = "franchise"
	Genre = "genre"
	Tag = "tag"
	
#==========================================================================================#
# >>>>> ОПИСАНИЕ КОМАНДЫ <<<<< #
#==========================================================================================#

TaggerCommand = Command("tagger", "Process genres and tags.")

TaggerInputPosition = TaggerCommand.create_position("INPUT", "Input data.", important = True)
TaggerInputPosition.add_key("classificator", ParametersTypes.All, "Unknown type of classificator.")
TaggerInputPosition.add_key("genre", ParametersTypes.All, "Genre.")
TaggerInputPosition.add_key("franchise", ParametersTypes.All, "Franchise.")
TaggerInputPosition.add_key("tag", ParametersTypes.All, "Tag.")

TaggerParserPosition = TaggerCommand.create_position("PARSER", "Parser name to determine source rules.")
TaggerParserPosition.add_key("use", ParametersTypes.Text, "Parser name.")

TaggerParserPosition = TaggerCommand.create_position("TYPE", "New type of classificator.")

TaggerCommand.add_flag("del", "Delete classificator.")
TaggerCommand.add_flag("p", "Make classificator a person.")
TaggerCommand.add_flag("t", "Make classificator a tag.")
TaggerCommand.add_flag("g", "Make classificator a genre.")
TaggerCommand.add_flag("f", "Make classificator a franchise.")
TaggerCommand.add_key("rename", ParametersTypes.All, "Rename classificator.")

#==========================================================================================#
# >>>>> ДОПОЛНИТЕЛЬНЫЕ ТИПЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Operation:
	"""Операция обработки классификатора."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_deleted(self) -> bool:
		"""Состояние: требуется ли удалить классификатор."""

		return self.__IsDeleted

	@property
	def original_name(self) -> str:
		"""Оригинальное название классификатора."""

		return self.__OriginalName

	@property
	def original_type(self) -> ClassificatorsTypes | None:
		"""Оригинальный тип классификатора."""

		return self.__OriginalType

	@property
	def name(self) -> str:
		"""Название классификатора."""

		return self.__Name
	
	@property
	def type(self) -> ClassificatorsTypes | None:
		"""Тип классификатора."""

		return self.__Type
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, classificator: str, type: ClassificatorsTypes):
		"""
		Операция обработки классификатора.
			classificator – название классификатора;\n
			type – тип классификатора.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__OriginalName = classificator
		self.__Name = classificator
		self.__IsDeleted = False
		self.__OriginalType = type
		self.__Type = type
	
	def __str__(self) -> str:
		"""Преобразует операцию в строковое представление словаря."""

		return str(self.to_dict())

	def change_type(self, type: ClassificatorsTypes):
		"""
		Изменяет тип классификатора.
			type – тип.
		"""

		self.__Type = type

	def delete(self):
		"""Удаляет классификатор."""

		self.__IsDeleted = True
	
	def print(self):
		"""Выводит операцию в консоль."""

		StyledPrinter("name: ", decorations = [Styles.Decorations.Bold], end = False)
		StyledPrinter(self.name, decorations = [Styles.Decorations.Italic])
		StyledPrinter("type: ", decorations = [Styles.Decorations.Bold], end = False)
		print(self.type.value)
		StyledPrinter("delete: ", decorations = [Styles.Decorations.Bold], end = False)
		if self.is_deleted: StyledPrinter("true", text_color = Styles.Colors.Red)
		else: StyledPrinter("false", text_color = Styles.Colors.Green)

	def rename(self, text: str):
		"""Переименовывает классификатор."""

		self.__Name = text

	def to_dict(self) -> dict:
		"""Преобразует операцию в словарь."""

		return {"name": self.name, "type": self.type.value, "delete": self.is_deleted}

	def to_json(self) -> str:
		"""Преобразует операцию в JSON-строку."""

		return json.dumps(self.to_dict(), ensure_ascii = False).encode("utf8").decode()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Tagger:
	"""Обработчик жанров и тегов."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __DirectiveToOperation(self, directive: ParsedCommandData) -> Operation:
		"""
		Преобразует директиву в операцию.
			directive – спаршенная директива.
		"""

		Type, Name = self.get_data(directive)
		NewOperation = Operation(Name, Type)

		if directive.check_flag("del"): NewOperation.delete()
		if directive.check_key("rename"): NewOperation.rename(directive.get_key_value("rename"))
		if directive.check_flag("g"): NewOperation.change_type(ClassificatorsTypes.Genre)
		if directive.check_flag("f"): NewOperation.change_type(ClassificatorsTypes.Franchise)
		if directive.check_flag("t"): NewOperation.change_type(ClassificatorsTypes.Tag)

		return NewOperation

	def __FindOperation(self, operations: list[Operation], classificator: str, type: ClassificatorsTypes | None) -> Operation | None:
		"""
		Ищет операцию по имени классификатора.
			operations – список операций;\n
			classificator – классификатор;\n
			type – тип классификатора.
		"""

		SearchResult = None

		for CurrentOperation in operations:
			
			if CurrentOperation.original_type == type and CurrentOperation.original_name == classificator: 
				SearchResult = CurrentOperation

		return SearchResult

	def __ReadScript(self):
		"""Считывает скрипт обработки жанров и тегов."""

		Path = "Configs/tagger.ini"
		Script = list()
		Source = None

		if not os.path.exists(Path): WriteTextFile(Path, "# Melon tagger ruleset.\n")
		else: Script = ReadTextFile(Path, split = "\n")

		for Line in Script:
			Line = Line.strip()

			if not Line or Line.startswith("#"): pass

			elif Line.startswith("[") and Line.endswith("]"):
				Source = Line[1:-1].strip()
				if Source not in self.__Script.keys(): self.__Script[Source] = list()

			else:
				Parts = shlex.split(Line)

				for Index in range(len(Parts)):
					if Parts[Index] in ["franchise", "genre", "tag", "rename"]: Parts[Index] = "--" + Parts[Index]
					elif Parts[Index] in ["del"]: Parts[Index] = "-" + Parts[Index]

				self.__Script[Source].append(["tagger"] + Parts)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик жанров и тегов."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Script = {
			None: []
		}

		self.__ReadScript()

	def get_data(self, parsed_command: ParsedCommandData) -> tuple[ClassificatorsTypes | None, str]:
		"""
		Определяет тип классификатора исходя из данных команды.
			parsed_command – данные команды.
		"""

		Type = None
		Name = None

		if parsed_command.check_key("genre"):
			Type = ClassificatorsTypes.Genre
			Name = parsed_command.get_key_value("genre")

		elif parsed_command.check_key("franchise"):
			Type = ClassificatorsTypes.Franchise
			Name = parsed_command.get_key_value("franchise")

		elif parsed_command.check_key("tag"):
			Type = ClassificatorsTypes.Tag
			Name = parsed_command.get_key_value("tag")

		elif parsed_command.check_key("classificator"):
			Name = parsed_command.get_key_value("classificator")

		return Type, Name

	def process(self, classificator: str, type: ClassificatorsTypes | None, parser: str | None = None) -> Operation:
		"""
		Обрабатывает классификатор и возвращает требуемую операцию.
			classificator – классификатор;\n
			type – тип классификатора;\n
			parser – название парсера для определение списка директив.
		"""

		parser = [parser, None] if parser else [None]
		Script = self.__Script.copy()
		Directives: list[str] = list()
		
		for Key in Script.keys(): 
			if Key in parser: Directives += Script[Key]

		ParsedDirectives: list[ParsedCommandData] = list()

		for Line in Directives:
			Analyzer = Terminalyzer(Line)
			ParsedDirectives.append(Analyzer.check_commands([TaggerCommand]))

		ParsedDirectives = [Value for Value in ParsedDirectives if Value is not None]

		Operations: list[Operation] = list()
		
		for Directive in ParsedDirectives: Operations.append(self.__DirectiveToOperation(Directive))
		
		TargetOperation = self.__FindOperation(Operations, classificator, type)
		if not TargetOperation: TargetOperation = Operation(classificator, type)

		return TargetOperation

