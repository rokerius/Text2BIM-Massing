# Запуск и API

Команды выполняются из корня checkout Text2BIM-Massing. Минимальный пример
без LLM — в [README](../README.md), окружение и полные проверки — в
[CONTRIBUTING](../CONTRIBUTING.md).

Внешний проект в документации называется **massing-generation**.
Имена `maslov` в extras, `--maslov-repo` в CLI и `integrations/maslov/`
в путях сохранены для совместимости существующих команд и конфигураций.

## Установка и зависимости

Python 3.11–3.13. Для окружения с закреплёнными версиями использовать Python
3.12 и `requirements-dev.txt`; для обычной установки доступны extras:

| Установка | Для чего |
| --- | --- |
| `python -m pip install -e .` | Сцена, геометрия, инструменты и ядро. |
| `python -m pip install -e '.[llm]'` | OpenAI SDK исходной версии 1.82.0. Codex CLI устанавливается отдельно. |
| `python -m pip install -e '.[maslov]'` | Зависимости базовых внешних компонентов massing-generation; сам checkout передаётся отдельно. |
| `python -m pip install -e '.[mesh]'` | Mesh-компилятор и связанные геометрические зависимости. |
| `python -m pip install -e '.[dev,llm,mesh,maslov]'` | Полное окружение разработки и интеграционных тестов. |

Wheel содержит рабочий пакет и vendor-ресурсы. Sdist дополнительно содержит
исходные материалы, документацию, примеры, тесты и аудит.

## CLI: одна задача

Пакет предоставляет эквивалентные точки входа:

```bash
text2bim-massing generate --help
python -m text2bim_massing generate --help
```

Задача задаётся через `--task` или JSON-файл с `instruction` и `context`:

```bash
python -m text2bim_massing generate \
  --config examples/codex_maslov.json \
  --task-file examples/feedback_task.json \
  --maslov-repo /path/to/massing-generation \
  --output runs/feedback-01
```

Второй пример — `examples/courtyard_task.json`: он проверяет запрос Architect
и отверстие. `--task` можно дополнить `--context /path/to/context.json`.
С `--task-file` контекст берётся из самого файла.

`--maslov-repo` проверяет точный HEAD
`607ff1fcf80477787409522d93e18e42ac1436cf` и совпадение `src/` с ним.
Альтернатива — переменная `MASSING_GENERATION_REPO`. Для собственного evaluator
этот аргумент необязателен, если его Python-модуль доступен окружению.

Каталог `--output` должен отсутствовать или быть пустым. Каждый запуск независим;
resume не реализован. CLI печатает JSON-сводку; подробности сохраняются в файлах.

## Конфигурация

Конфиг CLI состоит из `llm`, `evaluator`, `run`.
Готовый пример — [codex_maslov.json](../examples/codex_maslov.json).

### LLM

`provider=codex` использует установленный Codex CLI и сохранённый ChatGPT login.
API-ключи в CLI не передаются. Проверьте существующий login командой
`codex login status`; если вход ещё не выполнен, используйте `codex login`.
Проверенные живые запуски использовали CLI 0.164.0.

У клиента есть `model`, `reasoning_effort`, `timeout`, `executable`. Без model
выбор делается CLI и записывается как `codex-cli-default`. Такой режим подходит
для smoke-проверки; в конфиге сравнительного эксперимента нужна явная модель.
У Codex собственный служебный контекст; вызов Architect передаётся через
JSON-конверт, stop-последовательности этим транспортом не реализованы.

`provider=openai` использует OpenAI Chat Completions. Задайте model и
`OPENAI_API_KEY`; при необходимости — `base_url`, timeout и параметры генерации.
Model также может поступить из `TEXT2BIM_MODEL` / `OPENAI_MODEL`, endpoint —
из `OPENAI_BASE_URL`. `.env` автоматически не загружается. Параметр `send_stop`
по умолчанию false; retries внутри бюджетированного workflow отключаются.
Этот transport проверен настоящим SDK через локальный HTTP transport;
живые API-прогоны в отчёте не заявлены.

### Внешний evaluator

`factory` задаёт `module:object`, `kwargs` — параметры компонента.

| `kind` | Контракт и дополнительные поля |
| --- | --- |
| `callable` | `evaluator(massing, context) -> dict`; без kwargs объект используется напрямую, с kwargs factory вызывается для получения evaluator. |
| `metric` | Исходный `SampleMetric`, `report_key`, `layout`, при необходимости `building_key` и `building_id`. |
| `processor` | Исходный `SampleProcessor`, список `report_keys` и те же параметры вложенности. |

| `layout` | Значение в `sample[building_key]` |
| --- | --- |
| `extrusions` | `[extrusion, ...]` |
| `building` | `{"id": building_id, "massing": [extrusion, ...]}` |
| `buildings` | `[{"id": building_id, "massing": [extrusion, ...]}]` |

Контекст и геометрия копируются. Report должен быть JSON-словарём без NaN и
Infinity. `SampleMetricAdapter` преобразует значение metric в float;
`SampleProcessorAdapter` возвращает только явно заданные поля. Направление
улучшения и желаемые значения должны быть указаны во внешнем задании.

### Бюджеты `RunConfig`

| Параметры | Значение по умолчанию |
| --- | --- |
| `max_iterations` | 3 итерации Programmer → Reviewer. |
| `max_llm_calls`, `max_evaluations` | 20 вызовов LLM, 6 оценок. |
| `max_seconds` | 300 с на workflow. |
| `execution_timeout`, `evaluation_timeout` | 15 с на код, 60 с на evaluator. |
| `max_repairs` | 2 исправления после первой неудачной попытки. |
| `tool_units` | `mm`; доступно также `m`. |
| `max_code_bytes`, `max_output_bytes` | По 65 536 байт. |
| `max_state_bytes` | 2 000 000 байт. |
| `memory_limit_mb` | 1024 MiB адресного пространства code worker на Linux. |
| `input_price_per_million`, `output_price_per_million` | Не заданы; стоимость `null`. |

Конфиг примера или эксперимента переопределяет эти значения. Учитываются также
неудачные LLM-вызовы и оценки. Чтение готового отчёта и выбор кандидата не
расходуют новую оценку. Денежная стоимость считается только при явно заданных
ценах и полном usage; подписочные прогоны сохраняют токены и число вызовов.

## Python API

Пример собственного внешнего отчёта; его критерий остаётся в коде вызывающей стороны:

```python
from text2bim_massing import GenerationTask, RunConfig, generate
from text2bim_massing.codex_client import CodexCLIClient, CodexConfig


def evaluate_height(massing, context):
    height = max(e["top_elevation"] for e in massing) - min(
        e["bottom_elevation"] for e in massing
    )
    return {"height_m": height, "target_height_m": context["target_height_m"]}


client = CodexCLIClient(CodexConfig(model="gpt-6.1-sol", reasoning_effort="low"))
try:
    result = generate(
        GenerationTask(
            "Create a 10 by 8 metre massing, bottom 0 m, top 6 m. "
            "The external report height_m should equal target_height_m. "
            "Relay all dimensions to Programmer; tool units are millimetres.",
            {"target_height_m": 6},
        ),
        evaluator=evaluate_height,
        llm=client,
        config=RunConfig(max_llm_calls=8, max_evaluations=3),
        output_dir="runs/python-api-01",
    )
    print(result.status, result.selected_candidate)
finally:
    client.close()
```

`task` также принимает строку или словарь `{instruction, context}`. Каждый
`generate` создаёт собственный архив и бюджеты. Для scene-only API доступны
`Scene`, `SceneSnapshot`, `MassingTools`; законченный пример без LLM —
[scene_without_llm.py](../examples/scene_without_llm.py).

## Геометрия и единицы

Внешний массинг:

```json
[
  {
    "polygons": [[[0, 0], [10, 0], [10, 8], [0, 8]]],
    "bottom_elevation": 0,
    "top_elevation": 6
  }
]
```

Всё в этом JSON — метры. `Scene` всегда принимает метры. Прямой API
`MassingTools(scene)` по умолчанию использует `m`; `units="mm"` задаётся явно.
В агентном workflow `RunConfig.tool_units` по умолчанию равен `mm`.
`get_object` и чтение вершин используют единицы
инструментов, `read_scene` / `export_massing` — метры. Повороты — в градусах.
`tools.documentation()` выдаёт актуальные сигнатуры инструментов.

`polygons` — плоский список колец по семантике massing-generation. Он может описывать
отверстия и отдельные компоненты. Экструзия сохраняет копию профиля;
его последующее изменение не меняет существующий solid. `scene.transaction()`
откатывает сцену, но не обычные Python-переменные вызывающей стороны.

## Результаты и статусы

| Артефакт | Назначение |
| --- | --- |
| `result.json` | Статус, reason, выбранный кандидат, архив, история и расходы. |
| `task.json`, `config.json` | Задание/context и эффективные параметры workflow. |
| `prompts.json`, `provenance.json` | Рабочие промпты, source commits, transport и модель. |
| `history.jsonl` | Последовательность запросов, ответов, ошибок, оценок и выбора. |
| `candidates/<id>/` | Snapshot, massing, state, checkpoint.json, replay code.py, source_code.py и report; ошибки evaluator сохраняются отдельно. |
| `scene.json` | Последняя принятая сцена исполнителя. Может отличаться от выбранного старого кандидата. |
| `selected_massing.json`, `selected_code.py`, `checkpoint.json` | Геометрия и исполняемый комплект воспроизведения выбранного кандидата; появляются только при выборе. |
| `selected_source_code.py` | Исходные попытки Programmer, отдельно от replay: могут содержать хвост после checkpoint. |
| `runner_config.json` | Дополнительный файл CLI с исходной конфигурацией. |

Статусы workflow: `completed`, `budget_exhausted`, `execution_failed`,
`evaluation_failed`, `llm_failed`, `review_failed`, `failed`.
`completed` отражает решение Reviewer, а не универсальную валидность.
У частичного результата может быть архив без выбранного кандидата.

Коды **CLI пакета**: 0 — completed, 2 — budget_exhausted, 1 — ошибка.
Коды **отдельного runner massing-generation**: 0 — все задачи completed, 2 — есть
незавершённые задачи; ошибки до запуска завершаются исключением.

## Диагностика

| Симптом | Что проверить |
| --- | --- |
| Непустой output | Создать новый каталог; resume отсутствует. |
| Несовпадение commit massing-generation | Проверить HEAD и `src/`; не ослаблять проверку ради другого исходника. |
| Нет установленного Codex / ChatGPT login | Проверить PATH и `codex login status`. |
| Programmer не получил контур | Включить полный контур и единицы в инструкции Enhancer, как в конфиге пилота. |
| Пустая сцена после успешного скрипта | Чтение сцены не создаёт экструзии; смотреть ответ Programmer и статус всего workflow. |
| Нет выбранного кандидата | Проверить reason, бюджеты и отчёты архива; отсутствие выбора допустимо в частичном результате. |
| API без ключа / неверные параметры | Проверить env, provider/model и параметры `llm`; автоматической загрузки `.env` нет. |
| Ошибка package pin в пилоте | Следовать способам установки из README интеграции; одной версии `0.1.0` недостаточно для подтверждения Git SHA. |

Отдельный эксперимент с фиксированной моделью, реальным контуром и двумя
исходными метриками описан в [руководстве интеграции](../integrations/maslov/README.md).


## Требования из датасета во внешнем runner

`integrations/maslov/requirements.json` включает task_mode requirements.
Для каждого sample используются его n_floors, floor_height и total_area
(алиас usable_area приводится исходным helper massing-generation). Неизвестные/нулевые
числа отклоняются; цели пилота не подставляются. `--prepare-only` проверяет
все rows, сохраняет task_bindings/provenance и не создаёт LLM-клиент.
Во время генерации binding сохраняется также в каждой задаче.
Схема и команды — в [руководстве requirements](../integrations/maslov/requirements.md).
Это режим runner, не новая команда CLI пакета.
