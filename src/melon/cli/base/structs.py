from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...core.base.source_operator import BaseSourceOperator
	from ...core.system_objects.manager.parsers import ParserOperator
	
@dataclass
class _InternalStorage:
	"""Внутренние данные обработчика."""

	mirror: str | None = None
	source_operators: dict[str, "BaseSourceOperator"] = field(default_factory = dict)
	
	is_json_output: bool = False
	is_force_mode: bool = False
	is_multiple_parsers_allowed: bool = False

@dataclass(frozen = True)
class PreparedData:
	"""Подготовленные шаблонные параметры команды."""

	required_parsers: tuple["ParserOperator", ...]
	force_mode: bool
	is_json_output: bool

@dataclass(frozen = True)
class ProcessorOptions:
	"""Настройки обработчика."""

	use_timer: bool = True
