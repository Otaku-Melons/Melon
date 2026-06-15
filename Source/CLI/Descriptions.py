from dublib.CLI.Terminalyzer import Command, ValidableTypes

COMMANDS: list[Command] = list()

Com = Command("classify", "Process titles classificators.")
ComPos = Com.create_position("VALUE", "Input value to classification.", important = True)
ComPos.set_argument()
ComPos = Com.create_position("MODE", "Output mode. By default styled print to terminal.")
ComPos.add_flag("-j", aliases = ("--json",), description = "Prints JSON-string in console.")
ComPos.add_key("--file", type = ValidableTypes.Path, description = "Path to dump JSON file.")
Com.base.add_flag("-i", aliases = ("--ignorecase",), description = "Ignore characters case in procedures searching.")
COMMANDS.append(Com)