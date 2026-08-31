from dublib.cli.terminalyzer import ValidableTypes

from ..base_processor import PARAMS, BaseCommandProcessor

class CommandProcessorTemplate(BaseCommandProcessor[PARAMS]):
	"""Контейнер шаблонов генерации команд."""
	
	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ ГЕНЕРАЦИИ КОМАНДЫ <<<<< #
	#==========================================================================================#

	def _AddMirrorKey(self):
		"""Добавляет ключ подключения зеркала."""

		self._Command.base.add_key("--mirror", value_type = ValidableTypes.Domain, description = "Source mirror to requests.")
