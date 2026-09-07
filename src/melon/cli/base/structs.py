from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...core.system_objects.manager.parsers import ParserOperator

@dataclass(frozen = True)
class PreparedData:
	"""Подготовленные шаблонные параметры команды."""

	required_parsers: tuple["ParserOperator", ...]
	force_mode: bool
	mirror: str | None
