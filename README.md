# 🐄 AgroPredictTambo — Sistema Predictivo de Estrés Térmico y Refrigeración Sectorizada

[![AgroChallenge 2026](https://img.shields.io/badge/Nestl%C3%A9_Conecta-AgroChallenge_2026-0085ca?style=for-the-badge)](https://github.com/DiveShower/AgroPredictTambo)
[![Clean Architecture](https://img.shields.io/badge/Clean_Architecture-4_Anillos-2ecc71?style=for-the-badge)](steering.md)
[![Atomic Limit](https://img.shields.io/badge/Atomic_Code-%E2%89%A4_60_L%C3%ADneas-f1c40f?style=for-the-badge)](tests/test_architecture.py)
[![Tests](https://img.shields.io/badge/Pytest-133_Passed-brightgreen?style=for-the-badge)](tests/)
[![Python](https://img.shields.io/badge/Python-3.10_%7C_3.12_%7C_3.14-3776ab?style=for-the-badge)](requirements.txt)

Software industrial de **Predicción Bioclimática por Machine Learning, Control Sanitario Anti-Mastitis y Eficiencia Hídrica/Energética ESG** para rodeos lecheros, desarrollado bajo **Clean Architecture en 4 Anillos** para el desafío **Nestlé Conecta — AgroChallenge 2026**.

* 📄 **Especificación Técnica Maestra (SSOT):** [spec.md](spec.md)
* 🎤 **Guion del Pitch para el Jurado (180s):** [PITCH_NESTLE_2026.md](PITCH_NESTLE_2026.md)
* 🧭 **Reglas de Ingeniería y Gobernanza AST:** [steering.md](steering.md)
* 🔬 **Spikes de Arquitectura e Investigación Aplicada:** [docs/spikes/](docs/spikes/)

---

## 📌 1. Problemática Abordada

### 1.1 Impacto Fisiológico y Productivo del Estrés Calórico en Ganado Lechero
Las vacas lecheras de alta producción generan una elevada carga de calor metabólico endógeno producto de la fermentación ruminal y la síntesis láctea. Según la evidencia científica reciente (*Oliveira et al., 2025*), los rodeos modernos comienzan a experimentar estrés térmico a partir de un **Índice de Temperatura y Humedad ($\text{ITH}$) de $68.0\text{ a }72.0$**, muy por debajo de los umbrales históricos:
* **Taquipnea e Hipertermia:** Cuando la combinación de temperatura, humedad relativa y radiación solar impide disipar calor hacia el ambiente, la frecuencia respiratoria supera los $60\text{–}80\text{ movimientos/minuto}$ y la temperatura rectal se eleva por encima de $39.2\text{°C}$.
* **Derrumbe de la Curva de Lactancia:** El animal reduce drásticamente su consumo de materia seca para limitar la termogénesis digestiva, provocando pérdidas directas de **$3.0\text{ a }5.0\text{ litros de leche por vaca por día}$**, además de depresión inmunológica y caída severa en la tasa de preñez.
* **Inercia Calórica y Noches Tropicales:** El estrés térmico no es un fenómeno instantáneo; es acumulativo. Si durante la noche previa ($21:00\text{ a }06:00\text{ hs}$) el rodeo no dispone de al menos $6\text{ horas}$ con $\text{ITH} < 65.0$, los animales inician el día siguiente con **deuda térmica acumulada**, entrando en colapso calórico a temperaturas diurnas mucho menores.

### 1.2 Deficiencias del Paradigma Tradicional de Enfriamiento en Tambos
En la mayoría de las explotaciones lecheras, la mitigación térmica se gestiona mediante **temporizadores estáticos de 8 horas continuas ($10:00\text{ a }18:00\text{ hs}$)** o termostatos básicos que accionan bombas y ventiladores a ciegas con boquillas de alto caudal ($4.9\text{ L/min}$). Este esquema presenta tres fallas críticas:
1. **Derroche Hídrico y Energético Masivo:** Los equipos funcionan aunque el sector esté vacío (vacas en pastoreo u ordeñe), aunque sople viento suficiente o en ventanas donde el estrés real es bajo, desperdiciando miles de litros de agua subterránea y kilowatts-hora eléctricos cada jornada.
2. **Riesgo Sanitario Crítico de Mastitis Ambiental:** En galpones de descanso con cama orgánica (*Compost Barn* o tierra), la aspersión de agua humedece el sustrato, destruye el compostaje aeróbico y genera barro, multiplicando patógenos ambientales (*E. coli*, *Streptococcus uberis*) que disparan cuadros graves de **mastitis clínica y subclínica** y penalizaciones en calidad de leche.
3. **Actuación Reactiva y Tardía:** Los termostatos convencionales recién disparan cuando el ambiente ya superó el umbral crítico, sin anticipar la radiación solar entrante ni la aglomeración previa al ingreso a la fosa de ordeñe.

---

## ⚙️ 2. Implementación Desarrollada

**AgroPredictTambo** reemplaza el temporizador ciego por un **motor predictivo bioclimático y sanitario** que orquesta el enfriamiento de forma anticipada, sectorizada y auditable:

### 2.1 Pipeline de Machine Learning sin Data Leakage e Inferencia en Dos Capas
* **Vector de 8 Features Bioclimáticas:** El módulo [feature_builder.py](src/infrastructure/ml/feature_builder.py) construye en tiempo real un vector libre de fuga de datos compuesto por:
  1. `temperature_c` (Temperatura de bulbo seco en $\text{°C}$).
  2. `relative_humidity` (Humedad relativa en $\%$).
  3. `wind_speed_kmh` (Velocidad del viento a $10\text{ m}$ para modelar alivio convectivo).
  4. `solar_radiation_wm2` (Radiación solar de onda corta en $\text{W/m}^2$, crítica para carga radiante directa).
  5. `hour_of_day` (Ciclo circadiano y metabólico).
  6. `wet_bulb_depression` (Depresión de bulbo húmedo calculada mediante la ecuación trigonométrica de Stull, que mide la capacidad física real del aire para evaporar agua sobre el pelaje).
  7. `thi_rolling_avg_3h` (Promedio móvil de ITH de las últimas $3\text{ horas}$ para capturar la inercia térmica).
  8. `nocturnal_debt_hours` (Horas nocturnas frescas faltantes respecto al mínimo fisiológico de $6\text{ h}$).
  *(Las columnas `thi_calculated` y `respiratory_rate_est` se excluyen estrictamente de la matriz `X` para garantizar cero data leakage).*
* **Clasificador Random Forest + Fail-Safe Heurístico:** [SklearnPredictorAdapter](src/infrastructure/ml/sklearn_predictor_adapter.py) clasifica el nivel de estrés ($0=\text{Confort}$, $1=\text{Alerta Leve}$, $2=\text{Peligro}$) a horizonte $+1\text{h} / +2\text{h}$ con **$95.83\%$ de Accuracy** y **$100\%$ de Recall en Peligro**, acelerado por una caché LRU en memoria ([inference_lru_cache.py](src/infrastructure/ml/inference_lru_cache.py)). Si el artefacto `.joblib` no está disponible, conmuta automáticamente y sin interrupción a [HeuristicPredictorAdapter](src/infrastructure/ml/heuristic_predictor_adapter.py).

### 2.2 Ajuste Dinámico por Deuda Nocturna y Pre-enfriamiento de Ordeñe
* **Penalización por Noche Tropical ([nocturnal_recovery.py](src/domain/value_objects/nocturnal_recovery.py)):** Por cada hora nocturna que no logra bajar de $\text{ITH} = 65.0$, el sistema reduce automáticamente los umbrales diurnos de alerta y peligro en **$0.5\text{ puntos de ITH}$** (hasta un máximo de **$-3.0\text{ puntos}$**), activando la mitigación más temprano cuando las vacas no descansaron térmicamente.
* **Pre-enfriamiento Preventivo en Corral de Espera ([milking_schedule.py](src/domain/value_objects/milking_schedule.py)):** Evalúa la cercanía a los turnos de ordeñe (`04:30–07:00` y `16:00–18:30`). Si el pronóstico proyecta peligro térmico dentro de los **$15\text{ minutos}$ previos** al inicio del ordeñe, dispara el pre-enfriamiento anticipado en el corral de espera antes del pico de hacinamiento animal.

### 2.3 Sectorización Diferenciada, Micro-Ciclos Evaporativos y Bloqueo Anti-Mastitis
El caso de uso [PredictSectorStressUseCase](src/application/use_cases/predict_sector_stress_uc.py) y el evaluador [sector_order_helper.py](src/application/use_cases/sector_order_helper.py) cruzan la predicción climática con las reglas físicas y sanitarias de cada sector ([Sector](src/domain/entities/sector.py)):
1. **Verificación de Presencia Animal (`current_occupancy`):** Si un sector se encuentra desocupado (`False`), el sistema emite una orden inactiva (`0s` agua / `0s` ventilación), ahorrando el $100\%$ de agua y electricidad en esa zona.
2. **Pisos de Hormigón (`corral_espera`, `comederos` — `allows_water_sprinkling = True`):**
   * **Nivel 1 (Alerta):** Activa únicamente ventilación forzada ($270\text{s}$) para favorecer la pérdida de calor por convección sin gastar agua.
   * **Nivel 2 (Peligro):** Ejecuta el micro-ciclo evaporativo combinado ([cooling_cycle.py](src/domain/value_objects/cooling_cycle.py)) basado en *Chen et al. (2016)* e INTA Rafaela: **$40\text{ segundos}$ de aspersión de gota gruesa con boquilla calibrada de bajo caudal ($1.3\text{ L/min}$)** para penetrar el pelaje hasta la epidermis sin escurrimiento al piso, seguidos de **$270\text{ segundos}$ de ventilación forzada ($2.5\text{–}3.0\text{ m/s}$)** para evaporar esa lámina de agua extrayendo calor latente del cuerpo de la vaca (*duty cycle* hídrico de solo **$12.90\%$**).
3. **Cama Orgánica / Compost Barn (`sombras` — `allows_water_sprinkling = False`):**
   * Impone en el núcleo del dominio la **Regla Sanitaria Anti-Mastitis**: jamás abre la electroválvula de agua (`water_mist_seconds = 0`) sin importar cuán extremo sea el ITH, manteniendo únicamente la ventilación forzada ($270\text{s}$) para conservar la cama seca y libre de proliferación bacteriana.

### 2.4 Resiliencia Rural Offline, Seguridad de Hardware y Sincronización Multi-Interfaz
* **Operación Offline SQLite ([sqlite_weather_cache_adapter.py](src/infrastructure/persistence/sqlite_weather_cache_adapter.py)):** Cada consulta exitosa a Open-Meteo se persiste en una base local SQLite con `auto_vacuum = INCREMENTAL` y validación de antigüedad (`TTL = 6 horas`). Ante un corte de conectividad rural, el sistema opera sin degradación sobre la caché local.
* **Watchdog Físico de 60 Segundos ([serial_relay_adapter.py](src/infrastructure/hardware/serial_relay_adapter.py) / [mock_relay_adapter.py](src/infrastructure/hardware/mock_relay_adapter.py)):** Toda orden hacia electroválvulas pasa por un limitador de seguridad que impide aperturas continuas mayores a $60\text{ segundos}$ e incluye corte total inmediato (`emergency_shutoff_all()`).
* **Arquitectura Reactiva Multi-Canal (SCADA PyQt6 + Bot de Telegram + CLI):** Los hilos en segundo plano (`WeatherSyncWorker`, `TelegramBotWorker` y `PdfExportWorker` sobre `QThread` / `QThreadPool`) garantizan que la interfaz de escritorio mantenga **60 fps constantes** mientras se sincroniza en menos de $100\text{ ms}$ con los comandos enviados desde los celulares a través del Bot de Telegram.
* **Auditoría ESG y Económica ([calculate_savings_uc.py](src/application/use_cases/calculate_savings_uc.py)):** Cuantifica en tiempo real y exporta a PDF Unicode ([pdf_sustainability_report_adapter.py](src/infrastructure/reporting/pdf_sustainability_report_adapter.py)) los litros de agua ahorrados, kilowatts-hora eléctricos, kilogramos de $\text{CO}_2\text{e}$ evitados en el SADI (**Factor CAMMESA $0.35\text{ kg CO}_2\text{e/kWh}$**) y los litros de leche y pesos argentinos defendidos (**Precio de referencia SIGLeA**).

---

## 🛠️ 3. Stack Tecnológico

| Capa / Dominio | Tecnologías y Librerías | Propósito en el Proyecto |
| :--- | :--- | :--- |
| **Lenguaje & Tipado** | `Python 3.10–3.14`, `typing`, `Pyright` | Núcleo tipado con `Protocol` (PEP 544) y `dataclass(frozen=True)`. |
| **Machine Learning & Datos** | `scikit-learn`, `pandas`, `numpy`, `joblib` | Pipeline `RandomForestClassifier`, vectorización sin *leakage* y caché LRU. |
| **Ingesta Climática & Red** | `requests`, `urllib3` (Retry/Backoff), `Open-Meteo API` | Consulta meteorológica actual y pronóstico horario con radiación solar. |
| **Persistencia Offline** | `sqlite3` (`auto_vacuum = INCREMENTAL`) | Caché climática local con validación de TTL (`6 horas`) para operación sin red. |
| **Estación SCADA Desktop** | `PyQt6`, `matplotlib` (`FigureCanvasQTAgg`), `QSS` | Interfaz industrial oscura de 5 pestañas a 60 fps con `QThread` y `QTimer` maestro. |
| **Canal Móvil & QR** | `python-telegram-bot`, `qrcode[pil]`, REST HTTP | Bot interactivo bidireccional sincronizado con el SCADA y alertas push síncronas. |
| **Reportes ESG & Auditoría** | `fpdf2`, `DejaVuSans.ttf` (Unicode UTF-8) | Generación asíncrona de reportes PDF con logotipo Nestlé Conecta, CAMMESA y SIGLeA. |
| **Hardware IoT** | `pyserial` (`SerialRelayAdapter`, `MockRelayAdapter`) | Actuación sobre electroválvulas y ventiladores por USB/Arduino con Watchdog de 60s. |
| **Calidad & Testing** | `pytest`, `pytest-mock`, `ast`, `ruff` | Suite de **133 tests** (unitarios, integración, E2E y guantelete arquitectónico AST). |

---

## 🏛️ 4. Arquitectura Limpia en 4 Anillos (Clean Architecture)

El sistema implementa una separación concéntrica estricta en **4 Anillos** auditada automáticamente en cada corrida de tests por [tests/test_architecture.py](tests/test_architecture.py):

```mermaid
flowchart TD
    subgraph R4["Anillo 4: Infrastructure & Drivers (src/infrastructure/)"]
        UI_DESK["Desktop SCADA (PyQt6 + Matplotlib + QThread)"]
        UI_BOT["Telegram Bot Service + QR Generator"]
        UI_CLI["CLI Console Runner + Readline Completer"]
        AD_ML["SklearnPredictorAdapter (.joblib) + HeuristicPredictorAdapter"]
        AD_W["OpenMeteoAdapter + MockWeatherAdapter + SqliteWeatherCacheAdapter"]
        AD_IO["TelegramNotifierAdapter + PdfSustainabilityReportAdapter + RelayAdapters"]
    end

    subgraph R3["Anillo 3: Interface Adapters (src/adapters/)"]
        VM["Desktop ViewModels (ScadaViewModel, ForecastViewModel, SavingsViewModel)"]
        TG_H["Telegram Handlers (/estado, /ocupar, /prediccion, /ahorro, /reporte)"]
        CLI_C["CliController + CliFormatter + BenchmarkExporter"]
    end

    subgraph R2["Anillo 2: Application Layer (src/application/)"]
        UC["Use Cases (PredictSectorStress, CalculateSavings, ToggleOccupancy, FarmStatus, Report)"]
        DTO["Immutable DTOs (Requests, Responses, SectorStatus, SustainabilityReport)"]
    end

    subgraph R1["Anillo 1: Pure Domain Layer (src/domain/)"]
        ENT["Entities (Farm, Sector, CoolingOrder, HeatStressAlert)"]
        VO["Value Objects (THI_Score, WeatherConditions, CoolingCycle, NocturnalRecovery, ResourceSavings, CarbonFootprint, EconomicImpact, MilkingSchedule)"]
        PORTS["Abstract Ports / Protocols (IWeatherProvider, IModelPredictor, ISectorRepository, IWeatherCache, INotifier, IHardwareController, IReportGenerator)"]
    end

    R4 --> R3
    R3 --> R2
    R2 --> R1
    R4 --> R1
```

### 📏 Reglas Estructurales Inquebrantables ([steering.md](steering.md))
1. **Regla Ultra-Atómica ($\le 60$ líneas):** Ningún archivo `.py` o `.qss` en `src/`, `tests/` o `data/scripts/` supera las **60 líneas físicas**. Cada concepto reside en su propio módulo atómico.
2. **Inversión de Dependencias Pura:**
   * `src/domain/` no importa **ninguna** librería externa ni módulos de otros anillos.
   * `src/application/` solo importa de `src/domain/` y la biblioteca estándar de Python.
   * `src/adapters/` solo importa de `src/application/` y `src/domain/` (cero referencias a `PyQt6`, `telegram`, `sklearn`, `matplotlib` o `sqlite3`).
3. **Paquetes Limpios:** Todos los archivos `__init__.py` bajo `src/` y `tests/` miden exactamente **0 bytes**.

---

## 📂 5. Árbol de Archivos del Proyecto

```text
AgroPredictTambo/
├── README.md                                  # Documentación general y guía de operación
├── spec.md                                    # Especificación Técnica Maestra (v2.3.0)
├── steering.md                                # Reglas de gobernanza arquitectónica y cota de 60 líneas
├── PITCH_NESTLE_2026.md                       # Guion audiovisual de 3 minutos y métricas para el jurado
├── requirements.txt                           # Dependencias del proyecto compatibles con Linux
├── pytest.ini                                 # Configuración de Pytest y markers oficiales
├── pyrightconfig.json                         # Configuración de chequeo estático de tipos
├── .env.example                               # Plantilla de variables de entorno
│
├── src/                                       # CÓDIGO FUENTE (CLEAN ARCHITECTURE - 4 ANILLOS)
│   ├── main.py                                # Composition Root único (--desktop, --bot, --cli, --benchmark)
│   │
│   ├── domain/                                # 🟢 ANILLO 1: DOMINIO PURO (Cero dependencias externas)
│   │   ├── entities/
│   │   │   ├── farm.py                        # Entidad raíz del establecimiento lechero
│   │   │   ├── sector.py                      # Sector físico, umbrales y regla anti-mastitis
│   │   │   ├── cooling_order.py               # Orden de activación (agua y ventilación en segundos)
│   │   │   └── heat_stress_alert.py           # Alerta preventiva de estrés calórico
│   │   ├── value_objects/
│   │   │   ├── weather_conditions.py          # Variables meteorológicas y depresión de bulbo húmedo (Stull)
│   │   │   ├── thi_score.py                   # Cálculo NRC/Thom de ITH e inercia móvil de 3h
│   │   │   ├── cooling_cycle.py               # Micro-ciclo evaporativo (1.3 L/min, 40s agua / 270s vent.)
│   │   │   ├── nocturnal_recovery.py          # Deuda térmica nocturna y penalización de umbral (-3.0 pts)
│   │   │   ├── milking_schedule.py            # Agenda de ordeñe y ventana de pre-enfriamiento (15 min)
│   │   │   ├── resource_savings.py            # Matemática de ahorro hídrico (software + boquilla) y kWh
│   │   │   ├── carbon_footprint.py            # Huella de carbono evitada (Factor CAMMESA 0.35 kg CO2e/kWh)
│   │   │   └── economic_impact.py             # Leche defendida y retorno en ARS (Panel SIGLeA)
│   │   ├── ports/
│   │   │   ├── weather_provider_port.py       # Protocolo IWeatherProvider
│   │   │   ├── weather_cache_port.py          # Protocolo IWeatherCache
│   │   │   ├── model_predictor_port.py        # Protocolo IModelPredictor
│   │   │   ├── sector_repository_port.py      # Protocolo ISectorRepository
│   │   │   ├── notifier_port.py               # Protocolo INotifier
│   │   │   ├── hardware_controller_port.py    # Protocolo IHardwareController
│   │   │   └── report_generator_port.py       # Protocolo IReportGenerator
│   │   ├── exceptions/
│   │   │   ├── base_domain_exception.py       # Excepción base del dominio
│   │   │   ├── invalid_weather_exception.py   # Excepción por rango físico inválido
│   │   │   └── sector_not_found_exception.py  # Excepción por sector inexistente
│   │   └── fixtures/
│   │       └── default_farm.py                # Configuración inicial de los 3 sectores del tambo
│   │
│   ├── application/                           # 🔵 ANILLO 2: CAPA DE APLICACIÓN (Casos de Uso y DTOs)
│   │   ├── dtos/
│   │   │   ├── predict_stress_request_dto.py
│   │   │   ├── predict_stress_response_dto.py
│   │   │   ├── calculate_savings_request_dto.py
│   │   │   ├── calculate_savings_response_dto.py
│   │   │   ├── sector_status_dto.py
│   │   │   ├── stress_actuation_context.py
│   │   │   └── sustainability_report_dto.py
│   │   └── use_cases/
│   │       ├── predict_sector_stress_uc.py    # Orquestador principal de predicción y órdenes
│   │       ├── stress_pipeline_runner.py      # Ejecutor del pipeline bioclimático por sector
│   │       ├── sector_order_helper.py         # Evaluador de ciclo, anti-mastitis y alertas
│   │       ├── weather_fetcher_helper.py      # Resolución de clima con failover a caché SQLite
│   │       ├── nocturnal_recovery_helper.py   # Cómputo de horas frescas nocturnas
│   │       ├── calculate_savings_uc.py        # Cálculo comparativo 8h fijo vs predictivo
│   │       ├── toggle_sector_occupancy_uc.py  # Conmutación atómica de presencia animal
│   │       ├── get_farm_status_uc.py          # Estado consolidado del tambo en tiempo real
│   │       └── generate_sustainability_report_uc.py # Orquestador del informe ESG PDF
│   │
│   ├── adapters/                              # 🟡 ANILLO 3: ADAPTADORES DE INTERFAZ (Presenters / Handlers)
│   │   ├── desktop/viewmodels/
│   │   │   ├── scada_viewmodel.py             # ViewModel del tablero SCADA y emergencia
│   │   │   ├── forecast_viewmodel.py          # ViewModel de curva ITH 24h y simulador jurado
│   │   │   └── savings_viewmodel.py           # ViewModel de KPIs financieros/ESG y exportación PDF
│   │   ├── telegram/
│   │   │   ├── handlers/                      # Handlers atómicos (/start, /estado, /pronostico, /sectores,
│   │   │   │   └── ...                        # /ocupar, /prediccion, /ahorro, /reporte)
│   │   │   └── formatters/
│   │   │       ├── message_formatter.py       # Tablas monoespaciadas y alertas para móvil
│   │   │       └── sector_and_savings_formatter.py
│   │   └── cli/
│   │       ├── cli_controller.py              # Controlador de comandos en terminal
│   │       ├── cli_formatter.py               # Formateador tabular ASCII
│   │       └── benchmark_exporter.py          # Exportador JSON de telemetría 24h (--export-json)
│   │
│   └── infrastructure/                        # 🔴 ANILLO 4: INFRAESTRUCTURA Y DRIVERS TÉCNICOS
│       ├── ioc_container.py                   # Contenedor IoC de dependencias compartidas
│       ├── ioc_weather_resolver.py            # Selector dinámico de proveedor climático
│       ├── use_case_factory.py                # Fábrica de ensamblaje del núcleo
│       ├── weather_api/
│       │   ├── open_meteo_adapter.py          # Cliente REST Open-Meteo (actual + 24h)
│       │   ├── http_retry_client.py           # Sesión HTTP con Retry exponencial
│       │   ├── mock_weather_adapter.py        # Perfiles determinísticos (heatwave, nocturnal_debt, temperate)
│       │   └── weather_api_mapper.py          # Mapeador JSON -> WeatherConditions
│       ├── ml/
│       │   ├── sklearn_predictor_adapter.py   # Inferencia Random Forest (.joblib comprimido zlib)
│       │   ├── heuristic_predictor_adapter.py # Fail-safe bioclimático determinístico
│       │   ├── inference_lru_cache.py         # Caché LRU en memoria por firma bioclimática
│       │   ├── feature_builder.py             # Constructor de las 8 features sin data leakage
│       │   ├── model_evaluator.py             # Evaluador contra baseline DecisionTree e ITH estático
│       │   ├── train_pipeline.py              # Pipeline de entrenamiento temporal 80/20
│       │   └── artifacts/                     # Modelo entrenado (.joblib) y training_report.json
│       ├── persistence/
│       │   ├── sqlite_weather_cache_adapter.py# Caché offline SQLite con TTL y auto-vacuum
│       │   └── cache_schema.py                # DDL y consultas SQL parametrizadas
│       ├── repositories/
│       │   └── in_memory_sector_repo.py       # Repositorio de sectores thread-safe (RLock)
│       ├── notifications/
│       │   └── telegram_notifier_adapter.py   # Emisor HTTP POST síncrono de alertas push
│       ├── hardware/
│       │   ├── serial_relay_adapter.py        # Driver serie USB/Arduino con Watchdog de 60s
│       │   └── mock_relay_adapter.py          # Simulador de relés en memoria con Watchdog de 60s
│       ├── reporting/
│       │   ├── pdf_sustainability_report_adapter.py # Renderizador PDF ESG con fpdf2
│       │   ├── pdf_asset_loader.py            # Cargador de fuente Unicode DejaVuSans y logo Nestlé
│       │   ├── pdf_water_section.py           # Sección de balance hídrico del PDF
│       │   ├── pdf_energy_section.py          # Sección energética y huella CAMMESA del PDF
│       │   └── assets/                        # Fuente DejaVuSans.ttf y nestle_conecta_logo.png
│       └── ui/
│           ├── desktop/                       # Estación Base Nativa PyQt6
│           │   ├── app.py                     # Inicializador QApplication y carga de tema QSS
│           │   ├── main_window.py             # Ventana principal con sincronización QThread
│           │   ├── tab_builder.py             # Constructor de las 5 pestañas operativas
│           │   ├── styles/dark_agro_theme.qss # Tema industrial oscuro con propiedades dinámicas
│           │   ├── workers/                   # WeatherSyncWorker, TelegramBotWorker, PdfExportWorker
│           │   ├── components/                # SectorCardWidget, ThiGaugeWidget, ForecastChartWidget, etc.
│           │   └── views/                     # ScadaView, ForecastView, SavingsView, SimulationView, ReportView
│           ├── telegram_bot/
│           │   ├── bot_service.py             # Servicio python-telegram-bot con modo fail-safe
│           │   ├── bot_command_router.py      # Enrutador de comandos móviles
│           │   └── qr_generator.py            # Generador automático de data/cache/bot_qr.png
│           └── cli/
│               ├── console_runner.py          # Menú interactivo de consola y runner benchmark
│               └── readline_completer.py      # Autocompletado con Tab de sectores en terminal
│
├── data/                                      # DATOS, CACHÉ LOCAL Y SCRIPTS DE INGENIERÍA DE DATOS
│   ├── scripts/                               # Scripts atómicos de extracción Open-Meteo y dataset sintético
│   ├── processed/weather_heat_stress_dataset.csv # Dataset horario etiquetado (2520 observaciones)
│   └── cache/                                 # SQLite cache, código QR (bot_qr.png) y reportes PDF
│
├── docs/spikes/                               # DOCUMENTACIÓN DE SPIKES ARQUITECTÓNICOS (#16 a #21)
│   ├── spike_16_serial_watchdog.md            # Protocolo serie y circuito Watchdog físico de 60s
│   ├── spike_17_microclimate_sensors.md       # Fusión híbrida de sensores in-situ y Open-Meteo
│   ├── spike_18_siglea_cammesa_automation.md  # Automatización de parámetros SIGLeA y CAMMESA
│   ├── spike_19_automatic_occupancy_detection.md # Detección automática de ocupación en corrales
│   ├── spike_20_linux_packaging_systemd.md    # Empaquetado autónomo Linux y servicio systemd
│   └── spike_21_telegram_bot_security.md      # Seguridad RBAC y whitelist del Bot de Telegram
│
└── tests/                                     # SUITE AUTOMATIZADA DE PRUEBAS (133 TESTS)
    ├── test_architecture.py                   # Guantelete AST (4 anillos, 0-byte __init__, <= 60 líneas)
    ├── test_domain/                           # Tests unitarios puros de fórmulas, entidades y reglas
    ├── test_application/                      # Tests de casos de uso con mocks de puertos
    ├── test_adapters/                         # Tests de ViewModels, CliController y Handlers de Telegram
    ├── test_infrastructure/                   # Tests de integración (ML, SQLite, Open-Meteo, PDF, QR, Qt)
    └── test_e2e/                              # Tests End-to-End de flujos completos del sistema
```

---

## 🔧 6. Instalación y Configuración

### 1. Clonar el repositorio y crear el entorno virtual en Linux
```bash
git clone https://github.com/DiveShower/AgroPredictTambo.git
cd AgroPredictTambo
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configurar variables de entorno (`.env`)
```bash
cp .env.example .env
```
Parámetros principales en `.env`:
* `FARM_NAME` — Nombre del establecimiento lechero.
* `FARM_LATITUDE` / `FARM_LONGITUDE` — Coordenadas geográficas de la cuenca lechera.
* `DEFAULT_COW_COUNT=100` / `MILK_PRICE_ARS_PER_LITER=430.0` — Tamaño del rodeo y precio por litro de referencia SIGLeA.
* `WEATHER_PROVIDER="open_meteo"` (`open_meteo` | `mock`).
* `TELEGRAM_BOT_TOKEN=""` y `TELEGRAM_ADMIN_CHAT_ID=""` *(Opcional: si se deja vacío, la app de escritorio y la CLI operan normalmente en modo fail-safe)*.

---

## 🚀 7. Guía de Uso — Los 3 Niveles de MVP

El punto de entrada único [src/main.py](src/main.py) permite levantar cualquiera de las interfaces compartiendo exactamente el mismo motor de dominio y casos de uso:

### 🖥️ MVP Nivel 3: Estación Base SCADA Nativa (PyQt6)
```bash
# Iniciar Estación SCADA con perfil de demostración de Ola de Calor
python src/main.py --desktop --demo-heatwave

# Iniciar Estación SCADA conectada al clima en tiempo real (Open-Meteo)
python src/main.py --desktop
```
**Pestañas disponibles en la estación SCADA:**
1. **TAB 1 — SCADA TAMBO:** Cuadrante general de ITH, tarjetas reactivas de los 3 sectores (`corral_espera`, `comederos`, `sombras`), switches de ocupación animal en vivo, bloqueo sanitario anti-mastitis en Compost Barn, cronómetro regresivo `40s / 270s` y barra inferior con botones **"Sincronizar Clima Ahora"**, **"Simular Ola de Calor"** y **"Detención de Emergencia"**.
2. **TAB 2 — CURVA ITH 24H:** Gráfico `matplotlib` con blitting incremental, líneas de umbral ajustadas por deuda térmica nocturna y marcadores de pre-enfriamiento ML.
3. **TAB 3 — ROI & ESG:** Tarjetas KPI de agua ahorrada (software y combinada), energía eléctrica ($\text{kWh}$), huella de carbono CAMMESA ($\text{kg CO}_2\text{e}$) y leche defendida SIGLeA ($\text{ARS}$).
4. **TAB 4 — SIMULADOR JURADO:** 4 sliders interactivos con *debounce* (Temperatura $15\text{–}45\text{°C}$, Humedad $20\text{–}95\%$, Viento $0\text{–}40\text{ km/h}$, Radiación Solar $0\text{–}1000\text{ W/m}^2$) que recalculan en vivo la respuesta en pisos de hormigón vs cama de compost.
5. **TAB 5 — REPORTE PDF:** Previsualización ejecutiva y exportación asíncrona (`QThreadPool`) del reporte PDF auditado con apertura automática en el visor del sistema.

---

### 📱 MVP Nivel 2: Bot de Telegram Interactivo y Código QR
```bash
# Iniciar el Bot de Telegram en modo standalone y generar data/cache/bot_qr.png
python src/main.py --bot --demo-heatwave
```
Comandos disponibles desde el celular:
* `/start` o `/help` — Menú interactivo de comandos.
* `/estado` — Condiciones meteorológicas actuales e ITH.
* `/pronostico` — Proyección horaria de ITH a 24 horas.
* `/sectores` — Estado de ocupación, piso y equipamiento de los 3 sectores.
* `/ocupar <sector_id> <true/false>` — Simula el ingreso/egreso de vacas en vivo (ej. `/ocupar corral_espera false`) y actualiza instantáneamente la pantalla SCADA de escritorio.
* `/prediccion` — Ejecuta la inferencia ML a $+1\text{h}$ y detalla las órdenes de enfriamiento por sector.
* `/ahorro` — Balance auditado de litros de agua, $\text{kWh}$, $\text{CO}_2\text{e}$ y leche protegida.
* `/reporte` — Genera y envía el PDF de sustentabilidad directamente al chat de Telegram.

---

### ⌨️ MVP Nivel 1: Consola Interactiva (CLI) y Modo Benchmark 24h
```bash
# Ejecutar simulación analítica completa de 24 horas en terminal
python src/main.py --cli --benchmark

# Exportar telemetría del benchmark 24h a un archivo JSON auditable
python src/main.py --cli --benchmark --export-json data/cache/benchmark_24h.json

# Abrir menú interactivo de diagnóstico en consola (con autocompletado Tab)
python src/main.py --cli --demo-heatwave
```

---

## 📊 8. Impacto Auditado de Sustentabilidad ESG y Retorno Productivo

Resultados verificados en el benchmark de 24 horas (**100 vacas en ordeñe**, operación predictiva focalizada de $3.5\text{ h}$ frente al régimen tradicional continuo de $8.0\text{ h}$):

| Indicador Auditado | Régimen Tradicional (8h Fijas) | Sistema Predictivo AgroPredictTambo | Impacto Neto Verificado |
| :--- | :---: | :---: | :--- |
| **Consumo de Agua (Software, pico `1.3 L/min`)** | $2\,012.90\text{ L/día}$ | $880.65\text{ L/día}$ | **$1\,132.26\text{ L/día}$ ahorrados ($56.25\%$)** |
| **Consumo Hidráulico Tradicional (pico `4.9 L/min`)** | $7\,587.10\text{ L/día}$ | $880.65\text{ L/día}$ | **$6\,706.45\text{ L/día}$ ahorrados ($88.39\%$)** |
| **Consumo de Energía Eléctrica (Bomba + Vent.)** | $86.27\text{ kWh/día}$ | $37.74\text{ kWh/día}$ | **$48.53\text{ kWh/día}$ ahorrados ($56.25\%$)** |
| **Huella de Carbono Evitada (Factor CAMMESA)** | — | Factor $0.35\text{ kg CO}_2\text{e/kWh}$ | **$16.99\text{ kg CO}_2\text{e/día}$ evitados** |
| **Producción Láctea Defendida (Panel SIGLeA)** | Pérdida por estrés | Mitigación anticipada ML | **$80.00\text{ L/día}$ protegidos ($34\,400\text{ ARS/día}$)** |

---

## 🧪 9. Suite de Pruebas Automatizadas y Auditoría de Calidad

El repositorio cuenta con **133 pruebas automatizadas** divididas en `unit`, `architecture`, `integration` y `e2e`:

```bash
# Ejecutar las 133 pruebas (modo headless offscreen para PyQt6)
QT_QPA_PLATFORM=offscreen .venv/bin/pytest -v

# Ejecutar únicamente el guantelete AST de Clean Architecture y límite de 60 líneas
.venv/bin/python tests/test_architecture.py

# Ejecutar únicamente las pruebas integrales End-to-End (E2E)
QT_QPA_PLATFORM=offscreen .venv/bin/pytest -m e2e -v

# Re-entrenar y auditar el modelo Random Forest sin data leakage
.venv/bin/python src/infrastructure/ml/train_pipeline.py
```

---

## 📚 10. Respaldo Científico y Bibliografía

1. **Oliveira, C. P., et al. (2025).** *Heat Stress in Dairy Cows: Impacts, Identification, and Mitigation Strategies—A Review*. Animals, 15(2), 249. https://doi.org/10.3390/ani15020249
2. **Chen, J. M., Schütz, K. E., & Tucker, C. B. (2016).** *Cooling cows in the feeding alley: Different sprinkler flow rates*. Journal of Dairy Science, 99(8), 6470–6481. *(Demostración experimental de que $1.3\text{ L/min}$ logra igual abatimiento térmico que $4.9\text{ L/min}$ reduciendo un $73.5\%$ el uso de agua).*
3. **Becker, C. A., et al. (2021).** *Evaluation of heat stress in dairy cows using machine learning algorithms*. Biosystems Engineering, 208, 105–115.
4. **Pacheco, P. R. V., et al. (2020).** *Machine learning models applied to the identification of heat stress in Holstein cows*. Computers and Electronics in Agriculture, 178, 105760.
5. **Taverna, M., et al. (2018).** *Pautas técnicas para el manejo del estrés calórico en rodeos lecheros*. INTA EEA Rafaela.

---

## 👥 Autores — Equipo AgroChallenge 2026 (Nestlé Conecta)

* **Iván Pereyra** ([@jpereyra89](https://github.com/jpereyra89))
* **Facundo León** ([@DiveShower](https://github.com/DiveShower))
