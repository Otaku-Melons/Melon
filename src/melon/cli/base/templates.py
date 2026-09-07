from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...core.system_objects.manager.parsers import ParserOperator

@dataclass(frozen = True)
class BaseParameters:
	"""Базовые требуемые параметры."""

	pass

@dataclass(frozen = True)
class T_ForceModeRequired(BaseParameters):
	"""Шаблон: присутствует режим перезаписи."""

	force_mode: bool

@dataclass(frozen = True)
class T_MultipleParsersRequired(BaseParameters):
	"""Шаблон: требуется несколько парсеров."""

	required_parsers: tuple["ParserOperator", ...]

@dataclass(frozen = True)
class T_OptionalSingleParser(BaseParameters):
	"""Шаблон: возможен один необязательный парсер."""

	required_parser: "ParserOperator | None"

@dataclass(frozen = True)
class T_SingleParserRequired(BaseParameters):
	"""Шаблон: требуется один парсер."""

	required_parser: "ParserOperator"
