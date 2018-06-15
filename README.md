## Системные требования

1. Python версии не ниже 3.5 ([ссылка для скачивания](https://www.python.org/ftp/python/3.6.5/python-3.6.5.exe))

Использование ресурсов:

* Размер лог-файла: 1.74Гб
* Использованная память: 70Мб
* Время обработки (данные на SSD): 36с
* Размер результата: 17Мб
* Загрузка CPU 25% (Core i5-4460 3.2GHz)

## Использование парсера (как модуль)

```
import converter

converter.convert(
    course_file,     # Путь к файлу со структурой курса
    answers_file,    # Путь к файлу с ответами
    courses_file,    # Путь к файлу с названиями курсов
    logs_file,       # Путь к файлу с логами
    encoding,        # Кодировка файлов
    output           # Каталог, в который выводить результат
)
```

Если какие-то файлы отсутствуют, необходимо передать пустую строку.

Кодировку желательно указывать `utf8`.

Каталог, в который будет выводиться результат, должен быть предварительно создан.

## Использование парсера (как отдельное приложение)

Парсер преобразует логи EdX в формат 5CSV.

### Формат данных

Парсер работает со следующими данными:

1. Лог-файл EdX

    Описание формата файла доступно по [ссылке](http://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/tracking_logs.html).

1. Структура курсов

    Файл имеет текстовый формат. Строки выглядят следующим образом:

    `course_id+type@chapter+block@block_id;...;Название_модуля`

1. Файл ответов студентов

    Файл имеет текстовый формат. Строки выглядят следующим образом:

    `1;course_id+type@problem+block@block_id;block_id_4_1;user_id;username;answer_time;correct;...;question;process_time`

1. Файл с названиями курсов

    Файл имеет текстовый формат. Строки выглядят следующим образом:

    `course_id;Название_курса[;roo_course_id]`
    
    Параметр roo_course_id не обязательный. Каждая строка может состоять только из 2х значений:  `course_id;Название_курса`

### Запуск

1. Запустить парсер

    ```
    $ python main.py --logs ../data/logs --course ../data/course --answers ../data/answers --courses ../data/course_names csv
    ```

    * Файл `../data/logs` — лог-файл EdX (в текстовом формате)
    * Файл `../data/course` — файл структуры курсов (в текстовом формате). Может отсутствовать.
    * Файл `../data/answers` — файл ответов студентов (в текстовом формате). Может отсутствовать.
    * Фаёл `../data/course_names` — файл с названиями курсов (в текстовом формате). Может отсутствовать.

1. Результатом работы будут файлы `csv{1..5}.csv` в текущем каталоге и файл `course.json` с названием курса.

### Настройка каталога для вывода результатов

Для изменения каталога вывода результата его нужно передать последним аргументом при запуске:
```
$ python main.py --logs ../data/logs --course ../data/course --answers ../data/answers --courses ../data/course_names my/catalog/
```

Результатом будут файлы `my/catalog/csv{1..5}.csv` и `my/catalog/course.json`.
