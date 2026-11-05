# Отдельные эксперименты Маслова

Тонкий runner вокруг `generate`: режимы `pilot` и `requirements`, исходные оценщики, независимые задачи,
закреплённая версия пакета и output в формате `pred_massing`.
Поддерживается одно требуемое здание на sample. Общий launcher Маслова,
параметризация и NSGA-II не меняются.

## Статус и версии

| Компонент | Версия |
| --- | --- |
| Runtime Text2BIM-Massing | `62162651ce3bdd2d7ed0a9373ef6a392c4642a36` |
| massing-generation | `607ff1fcf80477787409522d93e18e42ac1436cf`, неизменённый `src/` |
| Модель пилота | `gpt-6.1-sol`, reasoning `low`, Codex CLI 0.164.0 через ChatGPT login |
| Конфиг | `pilot.json`: цели, metric factories, модель и бюджеты |

Живой Linux-пилот участка 1028279 завершён: `floor_count=2`, `site_match=1`,
3 LLM-вызова, 1 оценка за 88.86 с. Footprint 560 м² полностью внутри участка;
исходный mesh-компилятор дал замкнутую mesh 3360 м³. Первая попытка была
неудачной; обе описаны в [отчёте standalone-проекта](https://github.com/rokerius/Text2BIM-Massing/blob/main/docs/validation.md).

Runner, оба конфига и README скопированы в локальный
`massing-generation/experiments/methods/text2bim_adapted/`. Commit/PR в целевую
ветку Маслова ещё не зафиксирован. Каноническая версионируемая копия находится
в `integrations/maslov/` этого репозитория.

## Установка

В новом окружении:

```bash
python3.12 -m venv /tmp/text2bim-pilot-env
/tmp/text2bim-pilot-env/bin/pip install \
  'text2bim-massing[llm,maslov,mesh] @ git+https://github.com/rokerius/Text2BIM-Massing.git@62162651ce3bdd2d7ed0a9373ef6a392c4642a36'
```

Нужен установленный Codex CLI с ChatGPT login. Также принимается editable
checkout пакета, если `src/` и `pyproject.toml` совпадают с pin; новые
неотслеживаемые runtime-файлы отклоняются. Совпадения номера `0.1.0`
недостаточно: runner проверяет происхождение установки по Git commit.

Если в существующем окружении pip сохранил другую установку той же версии,
после установки нужных extras переустановить сам пакет:

```bash
python -m pip install --force-reinstall --no-deps \
  'text2bim-massing @ git+https://github.com/rokerius/Text2BIM-Massing.git@62162651ce3bdd2d7ed0a9373ef6a392c4642a36'
```

## Запуск

Из checkout Text2BIM-Massing:

```bash
/tmp/text2bim-pilot-env/bin/python integrations/maslov/run.py \
  --maslov-repo /absolute/path/to/massing-generation \
  --sample /absolute/path/to/massing-generation/experiments/workspace/parametrization/zero_shot/validation/initial_samples/1028279.json \
  --output /tmp/text2bim-site-1028279-01
```

Либо скопировать `run.py`, `pilot.json`, `requirements.json`, `README.md` без правок в отдельную
папку эксперимента и запускать из checkout Маслова:

```bash
/tmp/text2bim-pilot-env/bin/python experiments/methods/text2bim_adapted/run.py \
  --maslov-repo "$PWD" \
  --sample experiments/workspace/parametrization/zero_shot/validation/initial_samples/1028279.json \
  --output /tmp/text2bim-site-1028279-01
```

`--config` переопределяет соседний `pilot.json`, повторяемый `--sample-id`
выбирает rows по ID. Каталог результата должен быть пустым; resume и
параллельное выполнение в этой версии отсутствуют.

## Вход и выход

Вход — один JSON sample или список rows с `id`, `site_contour` и необязательным
`requirements`. ID одиночного файла без поля id берётся из имени файла.
При наличии requirements нужен список ровно с одним зданием и его ID.
Неподдерживаемые rows, дубликаты и неизвестные выбранные IDs отклоняются до LLM.

В модель передаются только `id`, `site_contour`, `requirements`; исходные
`building`, `massing`, `pred_massing` и прочие target-поля исключены.
Конфиг требует включать весь контур и единицы в ответ Enhancer: Programmer
получает только этот ответ, как в Text2BIM.

| Выход | Содержимое |
| --- | --- |
| `submit.json` | Rows с `pred_massing=[{"id": building_id, "massing": [...]}]`; при отсутствии выбранного кандидата — пустой список. |
| `report.json` | Статус, reason, candidate ID, отдельные метрики, расходы и путь к артефактам каждой задачи. |
| `result.json` | Число задач, обработанных, завершённых и имеющих выбор; агрегация метрик отсутствует. |
| `tasks/<index>/` | Полные независимые результаты `generate`, архив и история. |
| `runner_config.json`, `experiment_provenance.json` | Конфиг, package/Maslov commits, SHA dataset и runner, выбранные IDs. |

Выход обновляется после каждого sample, включая частичные результаты.
Код 0 — все задачи completed, 2 — есть незавершённые; конфигурационные ошибки
завершаются исключением до генерации. Выбранный оценённый кандидат может
сохраняться и при неполном статусе — смотреть report.

## Граница пилота

Два этажа и 3 м на этаж — явные диагностические цели конфига. Для настоящих
requirements добавлены `requirements.json` и адаптер полных числовых требований.
[Схема, provenance и prepare-only](https://github.com/rokerius/Text2BIM-Massing/blob/main/integrations/maslov/requirements.md)
описаны отдельно; неизвестные значения не подменяются целями пилота. Несколько зданий
отклоняются, их IDs не теряются молча.

FloorCount/SiteMatch не заменяют полный benchmark с общими девятью метриками.
Общий датасет, серия участков и сравнительный отчёт — оставшаяся работа.
Текущие возможности и план доступны из [README standalone-проекта](https://github.com/rokerius/Text2BIM-Massing).

Текущий pin включает исправление checkpoints. Исторические результаты 1028279
и 1627 в отчёте относятся к предыдущему runtime; новый replay-экспорт описан
в [checkpoints](https://github.com/rokerius/Text2BIM-Massing/blob/main/docs/checkpoints.md).
