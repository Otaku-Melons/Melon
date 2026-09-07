from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ...core.base.source_operator import BaseSourceOperator
	from ...core.system_objects.manager.parsers import ParserOperator
	
@dataclass
class _GeneratorOptions:
	"""Настройки генератора модели."""

	is_mirror_available: bool = False
	is_multiple_parsers_allowed: bool = False
	is_force_mode_available: bool = False

@dataclass
class _InternalStorage:
	"""Внутренние данные обработчика."""

	mirror: str | None = None
	source_operators: dict[str, "BaseSourceOperator"] = {}
	json_output: bool = False

@dataclass(frozen = True)
class PreparedData:
	"""Подготовленные шаблонные параметры команды."""

	required_parsers: tuple["ParserOperator", ...]
	force_mode: bool


@dataclass(frozen = True)
class ProcessorOptions:
	"""Настройки обработчика."""

	use_timer: bool = True
