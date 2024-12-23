# Поставка расширений
Расширениями считаются дополнительные скрипты, выводящие функционал базовых парсеров за пределы парсинга используемых в Melon данных. Они получают все привелегии парсеров (настройки и порталы), а также могут иметь свой собственный файл параметров _settings.json_.

Рекомендации по использованию только одних лишь порталов для общения с пользователем в меньшей мере касаются расширений, поскольку заранее заготовить шаблоны под все возможные случаи использования невозможно.

### 1. Базовые файлы
Домашний каталог расширения обязан содержать следующие файлы:
* **main.py** – главный модуль и точка входа в расширение;
* **README.md** – описание расширения и его настроек;
* **.gitignore** – игнорируйте кэш Python и другие временные файлы Runtime и разработки.

Опциональны следующие файлы:
* **install.sh** или **install.bat** – скрипт, выполняющийся после клонирования репозитория;
* **requirements.txt** – если расширение имеет специфические зависимости PyPI, не определённые в [dublib](https://github.com/DUB1401/dublib/blob/main/pyproject.toml) или [Melon](https://github.com/Otaku-Melons/Melon/blob/main/requirements.txt), укажите их здесь;
* **LICENSE** или **LICENSE.txt** – поставляйте лицензию для вашего Open Source модуля, чтобы явно указать все аспекты использования;
* **settings.json** – настройки расширения.

### 2. Инициализация каталога
Воспользуйтесь командой `melon init -e {EXTENSION_NAME}` для автоматической генерации всех необходимых файлов расширения, где `EXTENSION_NAME` – название расширения в полном формате. Название расширения обязательно начинается с названия парсера и отделяется точкой по шаблону: `{PARSER}.{EXTENSION}`, а также может содержать минусы или нижние подчёркивания, иметь символы любого регистра.

В _main.py_ появится класс **Extension**, унаследованный от типа **BaseExtension**, импортируются константы парсера и создадутся собственные. Определите их самостоятельно:

```Python
from ...main import VERSION as PARSER_VERSION
from ...main import NAME as PARSER_NAME
from ...main import TYPE as PARSER_TYPE
from ...main import SITE

# Версия расширения.
VERSION = "1.0.0"
# Уникальное название расширения. Заполняется автоматически.
NAME = "parser.extension"
```

### 3. Внедрение функционала
Работа любого расширения начинается с публичного метода **run()**. Он определён в **BaseExtension**: принимает строку с командой запуска расширения или ничего в случае отстутствия таковой.

По умолчанию метод содержит в себе обработку строки через [Terminalyzer](https://github.com/DUB1401/dublib/blob/main/docs/CLI/Terminalyzer.md) и передаёт результат в **_ProcessCommand()**. При необходимости собственной обработки параметров вы можете переопределять его по шаблону ниже.

```Python
def run(self, command: str | None) -> ExecutionStatus | ExecutionError:
		"""
		Запускает расширение.
			command – передаваемая для обработки команда.
		"""

		Status = ExecutionStatus(0)

		pass

		return Status
```

Расширения уже содержат множество встроенных инструментов разработки, унаследованных от родительского класса. Вы можете переопределить следующие методы:

```Python
# Возвращает список дескрипторов команд для Terminalyzer.
def _GenerateCommandsList(self) -> list[Command]: pass

# Возвращает объект для выполнения WEB-запросов.
def _InitializeRequestor(self) -> WebRequestor: pass

# Выполняется сразу после __init__.
def _PostInitMethod(self): pass

# Сюда передаются данные команд из Terminalyzer,
def _ProcessCommand(self, command: ParsedCommandData): pass
```

### 4. Порталы
Расширениям доступны все те же [порталы](./DEVELOPMENT.md#4-порталы), что и парсерам, но настройки парсера помещаются в **_ParserSettings**, а настройки расширения в словарь **_Settings**. 

### 5. Работа с расширением
Запуск расширения происходит следующим образом.
```Bash
melon run --extension parser.extension --command "help"
```