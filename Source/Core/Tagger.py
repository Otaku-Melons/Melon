from dublib.CLI.Terminalyzer import Command, ParsedCommandData, Terminalyzer
from dublib.CLI.TextStyler import FastStyler, GetStyledTextFromHTML
from dublib.Methods.Filesystem import ReadTextFile, WriteTextFile

import shlex
import enum
import json
import os

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ ТИПОВ <<<<< #
#==========================================================================================#

class ClassificatorsTypes(enum.Enum):
	"""Перечисление типов классификаторов."""

	Classificator = "classificator"
	Franchise = "franchise"
	Genre = "genre"
	Person = "person"
	Tag = "tag"

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
	def rule(self) -> bool:
		"""Состояние: найдено ли правило."""

		return self.__IsRuleActive

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

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__OriginalName = classificator
		self.__Name = classificator
		self.__IsDeleted = False
		self.__IsRuleActive = False
		self.__OriginalType = type
		self.__Type = type
	
	def __str__(self) -> str:
		"""Преобразует операцию в строковое представление словаря."""

		return str(self.to_dict())

	def activate(self):
		"""Указывает, что правило для этой операции было найдено."""

		self.__IsRuleActive = True

	def change_type(self, type: ClassificatorsTypes):
		"""
		Изменяет тип классификатора.
			type – тип.
		"""

		self.__Type = type

	def delete(self):
		"""Удаляет классификатор."""

		self.__IsDeleted = True
	
	def lower(self):
		"""Переводит в нижний регистр."""

		self.__Name = self.__Name.lower()

	def print(self):
		"""Выводит операцию в консоль."""

		Data = self.to_dict()
		for Key in Data.keys(): print(GetStyledTextFromHTML(f"<b>{Key}:</b>"), Data[Key])

	def rename(self, text: str):
		"""Переименовывает классификатор."""

		self.__Name = text

	def to_dict(self) -> dict:
		"""Преобразует операцию в словарь."""

		return {"name": self.name, "type": self.type.value, "delete": self.is_deleted, "rule": self.rule}

	def to_json(self) -> str:
		"""Преобразует операцию в JSON-строку."""

		return json.dumps(self.to_dict(), ensure_ascii = False).encode("utf8").decode()

	def upper(self):
		"""Переводит в верхний регистр."""

		self.__Name = self.__Name.upper()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Tagger:
	"""Обработчик жанров и тегов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def command(self) -> Command:
		"""Описание команды интерпретации операции."""

		TaggerCommand = Command("tagger", "Determine classificator operation.")

		TaggerInputPosition = TaggerCommand.create_position("CLASSIFICATOR", "Input data.", important = True)
		TaggerInputPosition.add_key("classificator", description = "Unknown type of classificator.")
		TaggerInputPosition.add_key("genre", description = "Genre.")
		TaggerInputPosition.add_key("franchise", description = "Franchise.")
		TaggerInputPosition.add_key("tag", description = "Tag.")

		TaggerTypePosition = TaggerCommand.create_position("TYPE", "New type of classificator.")
		TaggerTypePosition.add_flag("p", "Make classificator a person.")
		TaggerTypePosition.add_flag("t", "Make classificator a tag.")
		TaggerTypePosition.add_flag("g", "Make classificator a genre.")
		TaggerTypePosition.add_flag("f", "Make classificator a franchise.")

		TaggerCasePosition = TaggerCommand.create_position("CASE", "Case directive.")
		TaggerCasePosition.add_flag("low", "Convert to lower case.")
		TaggerCasePosition.add_flag("up", "Convert to upper case.")

		TaggerCommand.base.add_flag("del", "Delete classificator.")
		TaggerCommand.base.add_key("rename", description = "Rename classificator.")

		return TaggerCommand

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckParameters(self, rule: list[str], indicator: str, parameters: list[str]) -> bool:
		"""
		Проверяет, находится ли хотя бы один из параметров в правиле.
			rule – правило обработки;\n
			indicator – индикатор флага или ключа;\n
			parameters – список параметров.
		"""

		for Parameter in parameters:
			if f"{indicator}{Parameter}" in rule: return True

		return False

	def __FindOperation(self, operations: list[Operation], classificator: str, type: ClassificatorsTypes | None) -> Operation | None:
		"""
		Ищет операцию в списке по имени и типу классификатора.
			operations – список операций;\n
			classificator – классификатор;\n
			type – тип классификатора.
		"""

		SearchResult = None

		for CurrentOperation in operations:
			
			if type:
				if CurrentOperation.original_type == type and CurrentOperation.original_name.lower() == classificator.lower(): SearchResult = CurrentOperation

			else:
				if CurrentOperation.original_name == classificator: SearchResult = CurrentOperation

		return SearchResult

	def __ReadScript(self):
		"""Считывает скрипт обработки жанров и тегов и преобразует его в набор команд."""

		Path = "Configs/tagger.ini"
		Script = list()

		if not os.path.exists(Path): WriteTextFile(Path, "# Melon tagger ruleset.\n")
		else: Script = ReadTextFile(Path, split = "\n")

		Source = None
		Directives = list()

		for Line in Script:
			Line = Line.strip()

			if not Line or Line[0] in "#;\\/": pass

			elif Line.startswith("[") and Line.endswith("]"):
				Source = Line[1:-1].strip()
				if Source not in self.__Script.keys(): self.__Script[Source] = list()
				Directives = list()

			elif Line.startswith("@"):
				Directive = Line[1:].strip().upper()
				Directives = self.__RemoveTypesDirectives(Directives, Directive)
				Directives.append(Directive)
				if Directive == "DROP": Directives = list()

			else:
				if "IGNORE" in Directives: continue

				Parts = shlex.split(Line)

				for Index in range(len(Parts)):
					if Parts[Index] in ["franchise", "genre", "tag", "rename"]: Parts[Index] = "--" + Parts[Index]
					elif Parts[Index] == "*": Parts[Index] = "--classificator"
					elif Parts[Index] in ["del"]: Parts[Index] = "-" + Parts[Index]

				if "LOW" in Directives and not self.__CheckParameters(Parts, "-", ["low", "up"]): Parts.append("-low")
				elif "UP" in Directives and not self.__CheckParameters(Parts, "-", ["low", "up"]): Parts.append("-up")
				
				if "GENRES" in Directives and not self.__CheckParameters(Parts, "-", ["g", "f", "p", "t"]): Parts.append("-g")
				elif "FRANCHISES" in Directives and not self.__CheckParameters(Parts, "-", ["g", "f", "p", "t"]): Parts.append("-f")
				elif "PERSONS" in Directives and not self.__CheckParameters(Parts, "-", ["g", "f", "p", "t"]): Parts.append("-p")
				elif "TAGS" in Directives and not self.__CheckParameters(Parts, "-", ["g", "f", "p", "t"]): Parts.append("-t")

				self.__Script[Source].append(Parts)

	def __RemoveTypesDirectives(self, directives: list[str], type: str) -> list[str]:
		"""
		Удаляет директивы типов при обновлении.
			directives – список активных директив;\n
			type – тип из директивы.
		"""

		TypesDirectives = ["GENRES", "FRANCHISES", "PERSONS", "TAGS"]

		if type in TypesDirectives:
			Buffer = directives.copy()

			for Element in Buffer:
				if Element in TypesDirectives: directives.remove(Element)

		return directives

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик жанров и тегов."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Script = {
			None: []
		}

		self.__ReadScript()

	def get_classificator_data(self, command: ParsedCommandData) -> tuple[ClassificatorsTypes | None, str]:
		"""
		Определяет заданные тип и имя классификатора исходя из команды.
			command – данные команды.
		"""

		Type = None
		Name = None

		for CurrentType in [Element for Element in ClassificatorsTypes]:
			CurrentType: ClassificatorsTypes

			if command.check_key(CurrentType.value):
				Type = CurrentType
				Name = command.get_key_value(CurrentType.value)

		return Type, Name

	def interprete(self, command: ParsedCommandData) -> Operation:
		"""
		Интерпретирует команду в операцию.
			command – данные команды.
		"""

		Type, Name = self.get_classificator_data(command)
		NewOperation = Operation(Name, Type)

		if command.check_flag("del"): NewOperation.delete()
		if command.check_key("rename"): NewOperation.rename(command.get_key_value("rename"))

		if command.check_flag("g"): NewOperation.change_type(ClassificatorsTypes.Genre)
		elif command.check_flag("f"): NewOperation.change_type(ClassificatorsTypes.Franchise)
		elif command.check_flag("p"): NewOperation.change_type(ClassificatorsTypes.Person)
		elif command.check_flag("t"): NewOperation.change_type(ClassificatorsTypes.Tag)
		
		if command.check_flag("up"): NewOperation.upper()
		if command.check_flag("low"): NewOperation.lower()

		return NewOperation

	def process(self, classificator: str, type: ClassificatorsTypes | None, parser: str | None = None) -> Operation:
		"""
		Обрабатывает классификатор и возвращает требуемую операцию.
			classificator – классификатор;\n
			type – тип классификатора;\n
			parser – название парсера для определение списка директив.
		"""

		Levels = [parser, None] if parser else [None]
		Script = self.__Script.copy()
		Directives: list[list] = list()
		ParsedDirectives: list[ParsedCommandData] = list()
		Operations: list[Operation] = list()

		for Key in Script.keys(): 
			if Key in Levels: Directives += Script[Key]

		for Line in Directives:
			Analyzer = Terminalyzer(["tagger"] + Line)
			ParsedDirectives.append(Analyzer.check_commands([self.command]))

		ParsedDirectives = [Value for Value in ParsedDirectives if Value is not None]
		for Directive in ParsedDirectives: Operations.append(self.interprete(Directive))
		TargetOperation = self.__FindOperation(Operations, classificator, type)
		if not TargetOperation: TargetOperation = Operation(classificator, type)
		else: TargetOperation.activate()

		return TargetOperation