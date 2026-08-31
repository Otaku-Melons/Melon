from dataclasses import dataclass

from .structs import RequiredParser

@dataclass(frozen = True)
class T_ForceModeRequired:
	"""Шаблон: присутствует режим перезаписи."""

	is_force_mode_enabled: bool

@dataclass(frozen = True)
class T_MultipleParsersRequired:
	"""Шаблон: требуется несколько парсеров."""

	required_parsers: tuple[RequiredParser, ...]

@dataclass(frozen = True)
class T_SingleParserRequired:
	"""Шаблон: требуется один парсер."""

	required_parser: RequiredParser

@dataclass(frozen = True)
class T_OptionalSingleParser:
	"""Шаблон: возможен один необязательный парсер."""

	required_parser: RequiredParser | None

