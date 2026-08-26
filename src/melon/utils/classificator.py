import shlex
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Literal, Sequence, cast

from dublib.functions.filesystem import ReadTextFile

from ..core.exceptions.utils import classificator as classificator_exceptions

#==========================================================================================#
# >>>>> ВСОПОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ClassificatorsTypes(Enum):
	"""Перечисление типов классификаторов."""

	Franchise = "franchises"
	Genre = "genres"
	Person = "persons"
	Tag = "tags"

@dataclass(frozen = True)
class ClassificationResult:
	"""Результат обработки классификатора."""

	input: str
	is_procedure_found: bool
	name: str | None = None
	type: ClassificatorsTypes | None = None
	delete: bool | None = None
	is_renamed: bool = False

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"input": self.input,
			"is_procedure_found": self.is_procedure_found,
			"name": self.name,
			"type": self.type.value if self.type else None,
			"delete": self.delete,
			"is_renamed": self.is_renamed
		}

@dataclass(frozen = True)
class DirectiveValidationData:
	"""
	Данные валидации директивы.
	
	* **values** – последовательность принимаемых значений или `None` для любого значения;
	* **allow_list** – разрешено ли указание нескольких значений;
	* **allow_empty** – разрешено ли не указывать значения.
	"""

	values: tuple[str, ...] | None
	allow_list: bool
	allow_empty: bool

class Directives(Enum):
	"""Перечисление директив."""

	DROP = DirectiveValidationData(values = ("format", "operation", "type"), allow_list = True, allow_empty = True)
	FORMAT = DirectiveValidationData(values = ("low", "up"), allow_list = False, allow_empty = True)
	OPERATION = DirectiveValidationData(values = ("delete",), allow_list = False, allow_empty = False)
	INCLUDE = DirectiveValidationData(values = None, allow_list = False, allow_empty = False)
	TYPE = DirectiveValidationData(values = ("franchises", "genres", "persons", "tags"), allow_list = False, allow_empty = False)

@dataclass(frozen = True)
class ExecutableLine:
	"""Исполняемая строка скрипта."""

	file: Path
	number: int
	value: str

@dataclass(frozen = True)
class OperationData:
	"""Данные операции обработки классификатора."""

	target: str
	operator: Literal[">", "-"] | None = None
	value: str | None = None

@dataclass(frozen = True)
class Procedure:
	"""Процедура над классификатором."""

	name: str
	type: ClassificatorsTypes | None
	delete: bool | None
	rename: str | None

@dataclass(frozen = True)
class ScriptValidationError:
	"""Данные ошибки валидации скрипта."""

	line: ExecutableLine
	message: str

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Classificator:
	"""Оператор обработки классификаторов."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ ПАРСИНГА <<<<< #
	#==========================================================================================#

	def __ExtractDirectiveValues(self, line: ExecutableLine) -> tuple[str, ...]:
		"""
		Извлекает значения директивы без валидации.

		:param line: Исполняемая строка скрипта.
		:type line: ExecutableLine
		:return: Значения директивы.
		:rtype: tuple[str, ...]
		"""

		Parts = line.value.split("[", maxsplit = 1)
		if len(Parts) == 1: return ()

		ValueString = Parts[1].rstrip("]")
		ValueStringElements = ValueString.split(",")
		Result: list[str] = []

		for Element in ValueStringElements:
			Result.append(Element.strip())

		return tuple(Result)

	def __IncludeScriptFile(self, line: ExecutableLine) -> list[ExecutableLine]:
		"""
		Обрабатывает директиву `@INCLUDE`.

		:param line: Исполняемая строка скрипта.
		:type line: ExecutableLine
		:return: Список исполняемых строк из включаемого файла.
		:rtype: list[ExecutableLine]
		:raises FileNotFoundError: Включаемый файл скрипта не найден.
		"""

		Filename: str = self.__ExtractDirectiveValues(line)[0]
		if not Filename.endswith(".ini"): Filename += ".ini"
		ScriptFile: Path = self.__ScriptDirectory / Filename
		if not ScriptFile.exists(): raise FileNotFoundError(ScriptFile)

		return self.__ReadScriptFile(ScriptFile)

	def __ParseOperation(self, line: ExecutableLine) -> OperationData:
		"""
		Парсит операцию обработки.

		:param line: Исполняемая строка скрипта.
		:type line: ExecutableLine
		:return: Данные операции обработки классификатора.
		:rtype: OperationData
		:raises ScriptRuntimeError: Ошибка исполнения скрипта.
		"""

		Parts: list[str] = shlex.split(line.value.lstrip("*"))

		if len(Parts) == 1:
			return OperationData(target = Parts[0])
		
		Operator = Parts[1]

		if len(Parts) == 2:
			if Operator not in (">", "-"):
				raise classificator_exceptions.ScriptRuntimeError(line, f"Unknown operator: \"{Operator}\".")
			
			if Operator == ">":
				raise classificator_exceptions.ScriptRuntimeError(line, "Renaming operator requires value.")
			
			return OperationData(target = Parts[0], operator = "-")
		
		if len(Parts) == 3:
			if Operator == "-":
				raise classificator_exceptions.ScriptRuntimeError(line, "Deleting operator is unary.")
			
		return OperationData(target = Parts[0], operator = ">", value = Parts[2])

	def __ReadScriptFile(self, script_file: str | PathLike[str], include: bool = True) -> list[ExecutableLine]:
		"""
		Считывает исполняемые строки из файла скрипта, фильтруя пустые и комментарии.

		В конец каждого файла автоматически добавляется директива `@DROP` при её отсутствии.

		:param script_file: Путь к файлу скрипта.
		:type script_file: str | PathLike[str]
		:param include: Указывает, следует ли обрабатывать директивы `@INCLUDE`.
		:type include: bool
		:return: Список данных исполняемых строк.
		:rtype: list[ExecutableLine]
		"""

		ScriptPath: Path = Path(script_file)
		ScriptLines: list[str] = ReadTextFile(ScriptPath, split = True)
		FileOperationsLines: list[ExecutableLine] = []

		for Index in range(len(ScriptLines)):
			Line = ScriptLines[Index].strip()

			if not Line:
				continue
			
			if Line.startswith("#"):
				continue

			if Line.startswith(f"@{Directives.INCLUDE.name}"):
				if not include: raise classificator_exceptions.IncludeDirectiveDenied(ScriptPath, Index + 1)
				CurrentExecutableLine = ExecutableLine(ScriptPath, Index + 1, Line)
				FileOperationsLines += self.__IncludeScriptFile(CurrentExecutableLine)
				continue

			if not Line.startswith("*") and "=" in Line:
				Parts: list[str] = Line.split("=", maxsplit = 1)
				Line = "=".join(Parts)

			FileOperationsLines.append(ExecutableLine(ScriptPath, Index + 1, Line))

		if FileOperationsLines and FileOperationsLines[-1].value != "@DROP":
			FileOperationsLines.append(ExecutableLine(ScriptPath, -1, "@DROP"))

		return FileOperationsLines
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ ВАЛИДАЦИИ <<<<< #
	#==========================================================================================#

	def __ValidateDirective(self, line: ExecutableLine) -> list[ScriptValidationError]:
		"""
		Производит валидацию директивы.

		:param line: Исполняемая строка скрипта.
		:type line: ExecutableLine
		:return: Список ошибок валидации.
		:rtype: list[ScriptValidationError]
		"""

		ERRORS: list[ScriptValidationError] = []

		if "[" in line.value and "]" not in line.value:
			ERRORS.append(ScriptValidationError(line, "Unclosed values declaration."))
		if "]" in line.value and "[" not in line.value:
			ERRORS.append(ScriptValidationError(line, "Unopened values array."))

		DirectiveElements: list[str] = line.value.split("[", maxsplit = 1)

		Name = DirectiveElements[0][1:].rstrip()

		if Name not in tuple(Element.name for Element in Directives):
			ERRORS.append(ScriptValidationError(line, f"Unknown directive: \"@{Name}\"."))
		
		Directive: Directives | None = None

		for Element in Directives:
			if Element.name == Name:
				Directive = Element
				break

		Directive = cast(Directives, Directive)

		ValidationData = Directive.value
		Values = self.__ExtractDirectiveValues(line)

		if not Values and not ValidationData.allow_empty:
			ERRORS.append(ScriptValidationError(line, f"Directive \"@{Directive.name}\" must have values."))
		
		if len(Values) > 1 and not ValidationData.allow_list:
			ERRORS.append(ScriptValidationError(line, f"Directive \"@{Directive.name}\" must have only one value."))
		
		if ValidationData.values:
			for Value in Values:
				if Value not in ValidationData.values:
					ERRORS.append(ScriptValidationError(line, f"Unknown value \"{Value}\" for directive \"@{Directive.name}\"."))
				
		return ERRORS
		
	def __ValidateOperation(self, line: ExecutableLine) -> list[ScriptValidationError]:
		"""
		Производит валидацию операции.

		:param line: Исполняемая строка скрипта.
		:type line: ExecutableLine
		:return: Список ошибок валидации.
		:rtype: list[ScriptValidationError]
		"""

		ERRORS: list[ScriptValidationError] = []
		
		OperationString: str = line.value.lstrip("*").lstrip()
		OperationParts: tuple[str, ...] = tuple(shlex.split(OperationString))

		if len(OperationParts) == 2:
			
			if OperationParts[1] not in ("-", ">"):
				Operator: str = OperationParts[1]
				ERRORS.append(ScriptValidationError(line, f"Unknown operator: \"{Operator}\"."))
			
			if OperationParts[1] == ">":
				ERRORS.append(ScriptValidationError(line, "Renaming operator requires value."))
		
		elif len(OperationParts) == 3:

			if OperationParts[1] != ">":
				ERRORS.append(ScriptValidationError(line, "Only renaming operator supports two values."))
			
		return ERRORS

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, main_file: str | PathLike[str]):
		"""
		Оператор обработки скрипта классификации.

		:param main_file: Путь к точке входа скрипта классификации.
		:type main_file: str | PathLike[str]
		"""

		self.__MainFilePath: Path = Path(main_file)
		self.__ScriptDirectory: Path = self.__MainFilePath.parent

	def classify(self, target: str, procedures: Sequence[Procedure], ignore_case: bool = False) -> ClassificationResult:
		"""
		Обрабатывает классификатор.

		:param target: Цель для обработки.
		:type target: str
		:param procedures: Набор процедур.
		:type procedures: Sequence[Procedure]
		:param ignore_case: Указывает, нужно ли игнорировать регистр.
		:type ignore_case: bool
		:return: Результат обработки.
		:rtype: ClassificationResult
		"""

		ProceduresCache: dict[str, Procedure] = {}

		if ignore_case:
			ProceduresCache = {CurrentProcedure.name.lower(): CurrentProcedure for CurrentProcedure in procedures}
		else:
			ProceduresCache = {CurrentProcedure.name: CurrentProcedure for CurrentProcedure in procedures}
		
		TargetProcedure: Procedure | None = ProceduresCache.get(target.lower() if ignore_case else target)

		

		if TargetProcedure:
			NewName: str | None = TargetProcedure.rename if TargetProcedure.rename != target else None
			return ClassificationResult(
				input = target,
				is_procedure_found = True,
				name = NewName or TargetProcedure.name,
				type = TargetProcedure.type,
				delete = TargetProcedure.delete,
				is_renamed = bool(NewName)
			)
		
		return ClassificationResult(input = target, is_procedure_found = False)

	def parse_procedures(self, script_lines: Sequence[ExecutableLine]) -> tuple[Procedure, ...]:
		"""
		Парсит процедуры обработки классификаторов.

		:param script_lines: Последовательность исполняемых строк скрипта.
		:type script_lines: Sequence[ExecutableLine]
		:return: Последовательность процедур обработки классификаторов.
		:rtype: tuple[Procedure, ...]
		:raises ScriptRuntimeError: Ошибка исполнения скрипта.
		"""

		Procedures: list[Procedure] = []

		Type: ClassificatorsTypes | None = None
		Format: Literal["low", "up"] | None = None
		Operation: Literal[-1] | None = None

		for Line in script_lines:

			if Line.value.startswith(f"@{Directives.DROP.name}"):
				Values = self.__ExtractDirectiveValues(Line)
				if not Values: Values = ("type", "format", "operation")

				for Value in Values:
					match Value:
						case "type": Type = None
						case "format": Format = None
						case "operation": Operation = None
						case _: raise classificator_exceptions.ScriptRuntimeError(Line, f"Unknown drop value: \"{Value}\".")

				continue

			if Line.value.startswith(f"@{Directives.FORMAT.name}"):
				Values = self.__ExtractDirectiveValues(Line)
				FirstValue = Values[0]

				if FirstValue in ("low", "up"):
					Format = cast(Literal["low", "up"], FirstValue)
				else:
					raise classificator_exceptions.ScriptRuntimeError(Line, f"Unknown format value: \"{Format}\".")
				
				continue

			if Line.value.startswith(f"@{Directives.OPERATION.name}"):
				Operation = -1
				continue

			if Line.value.startswith(f"@{Directives.TYPE.name}"):
				Values = self.__ExtractDirectiveValues(Line)
				FirstValue = Values[0]

				try:
					Type = ClassificatorsTypes(FirstValue)
				except ValueError:
					raise classificator_exceptions.ScriptRuntimeError(Line, f"Unknown type: \"{FirstValue}\".")

				continue

			if Line.value.startswith("*"):
				LineOperation = self.__ParseOperation(Line)
				
				if Operation and LineOperation.operator:
					raise classificator_exceptions.ScriptRuntimeError(Line, f"Using operator with \"@{Directives.OPERATION.name}\" directive is denied.")

				NewName: str | None = None
				if LineOperation.value:
					NewName = LineOperation.value
				else:
					Buffer = LineOperation.target
					if Format == "low": Buffer = LineOperation.target.lower()
					elif Format == "up": Buffer = LineOperation.target.upper()
					if LineOperation.target == Buffer: NewName = None
					else: NewName = Buffer
				
				Procedures.append(Procedure(LineOperation.target, Type, Operation == -1, NewName))

		return tuple(Procedures)

	def read_script(self) -> tuple[ExecutableLine, ...]:
		"""
		Считывает строки операций из файла скрипта, фильтруя пустые строки и комментарии.

		:return: Последовательность исполняемых строк скрипта.
		:rtype: tuple[ExecutableLine, ...]
		"""

		return tuple(self.__ReadScriptFile(self.__MainFilePath))
	
	def validate_script(self, script_lines: Sequence[ExecutableLine]) -> tuple[ScriptValidationError, ...]:
		"""
		Производит построчную валидацию скрипта.

		:param script_lines: Последовательность исполняемых строк скрипта.
		:type script_lines: Sequence[ExecutableLine]
		:return: Список ошибок валидации.
		:rtype: tuple[ScriptValidationError, ...]
		"""

		ERRORS: list[ScriptValidationError] = []

		for Line in script_lines:
			if Line.value.startswith("@"):
				self.__ValidateDirective(Line)
			elif Line.value.startswith("*"):
				self.__ValidateOperation(Line)
			else:
				ERRORS.append(ScriptValidationError(Line, "Unknown string assignment."))
			
		return tuple(ERRORS)