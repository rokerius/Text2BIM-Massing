# Text2BIM-Massing

Адаптация Text2BIM в самостоятельный Python-пакет для генерации
массингов на Linux с внешним оценщиком.

## Статус

Реализованы этапы 1–5 [плана](Text2BIM-Massing-implementation-plan.md):
пакет, сцена и инструменты, перенос ролей Text2BIM, исполнение в отдельном
процессе, внешний оценщик, архив кандидатов и выбор оценённого результата.
Добавлены API/CLI и бюджеты, проверены установка и сквозной запуск в Linux.

Сцена поддерживает отверстия, отдельные компоненты, экструзии, редактирование,
перемещение, поворот, копирование, удаление, стабильные ID и откат ошибок.
Совместимость проверяется на исходном checkout Маслова, commit
`607ff1fcf80477787409522d93e18e42ac1436cf`.

Два независимых сквозных задания проверены с настоящим Codex CLI через подписку
ChatGPT и настоящим `BuildingFloorCount` Маслова: цикл улучшения 1→2 этажа и
трёхэтажный массинг с отверстием и вызовом Architect. Подробности —
[в отчёте проверки](docs/validation.md).

Оба задания дополнительно выполнены целиком в чистом Linux-контейнере
с Linux Codex CLI через ту же подписку. Подтверждены Reviewer-патч,
выбор оценённого кандидата, вызов Architect и сохранение отверстия.

После сверки отличий и добавления внешнего runner все 97 тестов прошли
на macOS и в чистом Linux-контейнере.
Добавлен [тонкий runner/config](integrations/maslov/README.md) отдельного
пилота Маслова: фиксированный commit пакета, модель, исходные метрики и
submission-формат. На реальном участке 1028279 живой Linux-пилот дал
`floor_count=2`, `site_match=1`: 3 LLM-вызова и 1 оценка за 88.86 с.
Поддерживается одна требуемая постройка на задачу.
Параметризация и NSGA-II остаются во внешнем методе Маслова.

## Окружение разработки

Python 3.11–3.13. Проверенное окружение Python 3.12 закреплено в
`requirements-dev.txt`; рабочая версия указана в `.python-version`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Для установки по диапазонам совместимости, включая Python 3.11:

```bash
python -m pip install -e '.[dev,llm,mesh,maslov]'
```

Минимальная установка: `python -m pip install -e .`. OpenAI SDK и mesh-extra
необязательны для работы геометрии и сцены.

Проверки:

```bash
python -m pip check
python tools/audit_adaptation.py --check
ruff check src tests examples tools integrations
ruff format --check src tests examples tools integrations
python -m pytest -c pyproject.toml tests -q
python -m pytest -c pyproject.toml tests -q --maslov-repo /path/to/massing-generation
python -m build
```

Без `--maslov-repo` семь интеграционных тестов пропускаются. Вместо флага можно
задать `MASSING_GENERATION_REPO`. Проверяется точный HEAD и неизменённый `src/`.
Тесты используют реальные конвертеры, mesh-компилятор, metric и processor Маслова.

Проверки: macOS arm64 / Python 3.12.15 и чистый Linux arm64 / Python 3.12.16.
В Linux контейнер устанавливает пакет в site-packages и выполняет все 97 тестов,
включая внешний checkout Маслова, подключённый только для чтения. Добавлен CI
для Ubuntu и Python 3.11–3.13; его удалённый запуск пока не проверен.

Подготовлен Dockerfile: `docker build -t text2bim-massing .`, затем
`docker run --rm text2bim-massing`. Образ выполняет тесты без сетевого LLM.
Для внешних интеграционных тестов checkout Маслова можно примонтировать read-only.

## Генерация через подписку Codex

Требуется установленный Codex CLI, авторизованный командой `codex login` через
ChatGPT. API-ключ для этого транспорта не требуется; сохранённая авторизация
используется штатным `codex exec` — [документация Codex](https://learn.chatgpt.com/docs/non-interactive-mode).

```bash
python -m text2bim_massing generate \
  --config examples/codex_maslov.json \
  --task-file examples/feedback_task.json \
  --maslov-repo /path/to/massing-generation \
  --output runs/feedback-01
```

Каталог результата должен быть пустым. Каждый вызов `generate` независим;
для следующего задания укажите новый каталог. `examples/courtyard_task.json`
проверяет дополнительный путь через Architect и профиль с отверстием.

Провайдер `codex` использует сохранённый ChatGPT login, read-only режим CLI,
временный рабочий каталог и JSON Schema для ответа. API-ключи из окружения в CLI
не передаются. Сам код геометрии исполняется нашим worker через исходный
интерпретатор Text2BIM. CLI не должен использовать собственные инструменты;
такие события отклоняются как ошибка транспорта. `model` можно задать явно
в конфигурации; без него используется default Codex, который записывается
как `codex-cli-default`. Перед сравнением методов модель следует зафиксировать.

Для API-транспорта укажите `"provider": "openai"` и модель в секции `llm`;
ключ берётся из `OPENAI_API_KEY`. Произвольный оценщик задаётся через
`evaluator.factory` (`module:object`), `kwargs` и вид адаптера в JSON-конфиге.
Существующий метод Маслова при этом не изменяется.

## Python API и результаты

```python
from text2bim_massing import GenerationTask, RunConfig, generate
from text2bim_massing.codex_client import CodexCLIClient

result = generate(
    GenerationTask("Create a two-floor massing", context={}),
    evaluator=your_evaluator,
    llm=CodexCLIClient(),
    config=RunConfig(max_llm_calls=10, max_evaluations=4),
    output_dir="runs/task-01",
)
```

Роли: Enhancer → Architect по запросу → Programmer → оценка → Reviewer →
исполняемый патч Programmer. `commit_candidate()` фиксирует неизменяемый
snapshot; `evaluate(candidate_id)` оценивает его или возвращает сохранённый
отчёт; `select_candidate(candidate_id)` выбирает только оценённый кандидат.
Reviewer выбирает финальный кандидат из архива и решает, нужен ли следующий патч.
Изменение сцены не меняет старый отчёт и не превращает его в оценку новой формы.

Артефакты запуска: `result.json`, `history.jsonl`, `task.json`, `config.json`,
`prompts.json`, `provenance.json`, финальная сцена, выбранная геометрия и код;
в `candidates/<id>/` — snapshot, геометрия, состояние, код и фактический отчёт.
CLI дополнительно сохраняет `runner_config.json`. Ошибки оценщика также остаются
в архиве. Артефакты и расходы сохраняются при исчерпании бюджета.

`RunConfig` задаёт лимиты итераций, LLM-вызовов, оценок, общего времени,
времени скрипта и оценщика, числа исправлений, размеров кода/вывода/состояния.
Учитываются неудачные вызовы. Повторный выбор и чтение готового отчёта не
расходуют новую оценку. CLI возвращает код 0 при `completed`, 2 при
`budget_exhausted`, 1 при ошибке. Если бюджет закончился до выбора, результат
может содержать архив без выбранного кандидата.

Геометрия и переменные скрипта принимаются только после полного успеха попытки.
Разрешены документированные инструменты, ограниченный набор builtins и public
math imports. Есть тайм-аут процесса; лимит адресного пространства worker
применяется на Linux. Это ограничения исполнения, а не полноценная OS sandbox.
Оценщик — доверенный внешний callable; он запускается отдельно, с собственным
тайм-аутом, и возвращает JSON. Произвольная логика в переданном LLM-клиенте должна
соблюдать переданный timeout; оба поставляемых транспорта его применяют.

## Пример без LLM

```python
from text2bim_massing import MassingTools, Scene

scene = Scene()
tools = MassingTools(scene, units="mm")
profile = tools.create_polygon([(0, 0), (10000, 0), (10000, 8000), (0, 8000)])
solid = tools.create_extrusion(profile, 0, 6000)
copy = tools.duplicate_obj(solid)[0]
tools.move_obj(copy, xDistance=15000)
massing = tools.export_massing()  # Все координаты и высоты в метрах.
```

Полный пример с отверстием и отдельным компонентом:
`python examples/scene_without_llm.py > /tmp/massing.json`.

`Scene` всегда принимает метры. `MassingTools` принимает `m` или `mm`;
`get_object` и чтение вершин используют единицы инструментов. `read_scene` и
`export_massing` возвращают метры. Углы задаются в градусах. Документация функций
доступна через `tools.documentation()`.

`create_profile(polygons)` принимает плоский список колец по семантике Маслова.
Созданная экструзия сохраняет независимую копию геометрии профиля. Блок
`with scene.transaction(): ...` откатывает всю сцену при ошибке. Он не откатывает
переменные интерпретатора. `scene.snapshot()` хранит неизменяемый JSON;
`to_dict()` и `to_massing()` snapshot возвращают независимые копии.

## Внешние компоненты

`SampleMetricAdapter(metric, report_key="name", layout="building")` и
`SampleProcessorAdapter(processor, report_keys=("name",), layout="extrusions")`
принимают реальные компоненты извне и возвращают JSON-совместимый отчёт.

| layout | Поле `sample[building_key]` |
| --- | --- |
| `extrusions` | `[extrusion, ...]` |
| `building` | `{"id": building_id, "massing": [extrusion, ...]}` |
| `buildings` | `[{"id": building_id, "massing": [extrusion, ...]}]` |

Контекст и геометрия копируются; NaN/Infinity в отчёте отклоняются. Метрики,
цели и направления оптимизации задаются снаружи. `compile_mesh(massing, compiler)`
формирует коллекцию зданий для исходного `MassingMeshCompiler`.

## LLM-клиент

```python
from text2bim_massing.llm import LLMConfig, OpenAIClient

client = OpenAIClient(LLMConfig(model="your-model"))
try:
    text = client.generate_one("Your prompt")
    usage = client.last_response
finally:
    client.close()
```

Ключ читается из `OPENAI_API_KEY`; `.env` автоматически не загружается.
`base_url`, timeout, параметры генерации и stop задаются явно. Retries по умолчанию
отключены. `calls` считает вызовы генерации, `responses` содержит успешные ответы
и фактический usage. В `generate` стоимость оценивается только при явно заданных
ценах входных/выходных токенов и полном usage. Для подписки Codex она остаётся
`null`; лимитируется число вызовов, а usage CLI сохраняется как расход токенов.

Сохранён Chat Completions-интерфейс Text2BIM; настройка SDK сверена с
[официальной документацией OpenAI](https://developers.openai.com/api/reference/python).
Автоматические тесты используют SDK с локальным HTTP transport; живые
Codex-прогоны выполнялись отдельно и перечислены в отчёте проверки.

## Исходные материалы

[Карта переноса](docs/source-map.md), [журнал адаптации](docs/text2bim-adaptation.md)
и [уведомления об исходниках](THIRD_PARTY_NOTICES.md) описывают заимствования и
новый код. [Полный реестр отличий](docs/text2bim-diff.md) охватывает все 44 файла
исходного tree и 156 declarations выбранных Python-файлов. Проверка
`tools/audit_adaptation.py --check` отклоняет новые неописанные файлы и изменения
проверенного состояния; перед `--write` нужно сверить причины в
`docs/adaptation-spec.json`. Это контроль полноты учёта, а не доказательство
эквивалентности методов. Оригиналы с хешами находятся в `upstream/`. Четыре исходных промпта
сохранены без изменений как ресурсы пакета. Адаптации находятся в `prompts.py`
и сохраняются в `prompts.json` каждого запуска.

В текущем каталоге отсутствуют дополнительные материалы, на которые ссылается
план:

- `text2bim-audit/pitfalls-and-validation.md`;
- `text2bim-audit/feasibility-and-priorities.md`;
- `our-method-vs-text2bim-adapted.md`.

Перед использованием этих материалов их нужно добавить с сохранением путей.
