# AgroPredictTambo — Sistema Predictivo de Estrés Térmico (MVP)

Software de **Predicción Bioclimática y Sectorización Anti-Mastitis para Ganado Lechero** desarrollado bajo **Clean Architecture en 4 Anillos** para el desafío **Nestlé Conecta — AgroChallenge 2026** (establecimiento piloto: *Tambo San José*, Rafaela, Santa Fe).

- **Guion del Jurado (Pitch 180s):** [PITCH_NESTLE_2026.md](PITCH_NESTLE_2026.md)
- **Reglas de Ingeniería y Arquitectura:** [steering.md](steering.md)

---

## Arquitectura Limpia en 4 Anillos y Reglas de Calidad

El código fuente sigue la regla concéntrica de dependencias de **Clean Architecture** y las restricciones auditadas en [steering.md](steering.md):

| Anillo | Ruta | Responsabilidad y Frontera de Dependencias |
| :--- | :--- | :--- |
| **1. Domain** | `src/domain/` | Entidades, value objects y lógica pura de ITH, deuda nocturna y sectorización anti-mastitis. Cero librerías externas y cero imports de capas exteriores. |
| **2. Application** | `src/application/` | Casos de uso y puertos (`use_cases/`, `ports/`). Solo importa de `src/domain/` y la librería estándar. |
| **3. Interface Adapters** | `src/adapters/` | Controladores CLI, ViewModels desktop, handlers de Telegram y presenters. Solo importa de `src/application/` y `src/domain/` (prohibido importar `PyQt6`, `telegram`, `sklearn` o `sqlite3`). |
| **4. Infrastructure** | `src/infrastructure/` | Drivers concretos: UI (`cli`, `desktop`, `telegram_bot`), `ml/`, `weather_api/`, `persistence/` (SQLite), hardware/simulador y generador PDF. |

### Reglas Estructurales Auditadas ([steering.md](steering.md))
- **Cota ultra-atómica (`wc -l <= 60`):** Todo archivo `.py`, `.qss` o `.sh` en `src/`, `tests/` y `data/scripts/` tiene como máximo **60 líneas físicas** post-formateo (archivos `.md` exentos).
- **Paquetes puros (`__init__.py` de 0 bytes):** Todos los `__init__.py` en `src/` y `tests/` miden exactamente `0` bytes.
- **Tipado estricto y cero data leakage:** `Pyright` estricto sobre `src/`, imports 100% absolutos (`from src...`), y exclusión de `thi_calculated` y `respiratory_rate_est` de la matriz de entrenamiento ML.

---

## Instalación Rápida en Linux (`./venv`) y Configuración `.env`

```bash
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Variables principales en `.env` (a partir de `.env.example`):
- **Tambo:** `FARM_NAME`, `FARM_LATITUDE`, `FARM_LONGITUDE`, `DEFAULT_COW_COUNT`, `MILK_PRICE_ARS_PER_LITER`.
- **Clima:** `WEATHER_PROVIDER` (`open_meteo`, `mock` u `open_weather`) y `OPENWEATHER_API_KEY` (opcional).
- **Telegram:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_CHAT_ID`, `TELEGRAM_BOT_USERNAME` (si el token está vacío, el sistema opera normalmente en modo fail-safe).
- **Hardware IoT:** `USE_MOCK_HARDWARE`, `SERIAL_PORT`, `SERIAL_BAUDRATE`.

---

## Ejecución de los 3 Niveles de MVP

Todos los niveles comparten el mismo núcleo de dominio y casos de uso desde `src/main.py`:

### Nivel 1 — CLI & Benchmark 24h
```bash
# Interfaz de consola interactiva (CLI)
./venv/bin/python src/main.py --cli

# Simulación analítica y balance ESG 24h en consola
./venv/bin/python src/main.py --cli --benchmark
```

### Nivel 2 — Canal Móvil Telegram + QR
```bash
# Bot de Telegram headless + generación de QR en data/cache/bot_qr.png
./venv/bin/python src/main.py --bot
```
- Genera el código QR de acceso en `data/cache/bot_qr.png`.
- **Arranque fail-safe sin token:** si `TELEGRAM_BOT_TOKEN` no está configurado en `.env`, registra el estado de forma segura sin abortar el sistema.

### Nivel 3 — Estación Desktop PyQt6 + Sync SCADA
```bash
# Estación nativa de escritorio PyQt6 (SCADA)
./venv/bin/python src/main.py --desktop

# Estación Desktop con perfil offline de ola de calor para demostración
./venv/bin/python src/main.py --desktop --demo-heatwave
```

---

## Reporte PDF ESG y Métricas Auditadas (Benchmark 24h)

La estación Desktop y el Bot permiten exportar el reporte auditado de sustentabilidad en PDF (`data/cache/reporte_sustentabilidad_nestle.pdf` / `data/cache/sustainability_report_nestle.pdf`).

Resultados verificados de [PITCH_NESTLE_2026.md](PITCH_NESTLE_2026.md) para el escenario piloto (`100` vacas, operación predictiva de `3.5h` frente a esquema tradicional continuo de `8h`):

| Indicador ESG / Productivo | Base Tradicional (8h) | Modelo Predictivo (3.5h) | Impacto Verificado |
| :--- | :---: | :---: | :--- |
| **Ahorro hídrico por software (`1.3 L/min`)** | `2012.90 L` | `880.65 L` | `1132.26 L` ahorrados (**`56.25%`**) |
| **Ahorro hidráulico combinado (vs `4.9 L/min`)** | `7587.10 L` | `880.65 L` | **`88.39%`** de ahorro hídrico total |
| **Ahorro eléctrico** | `86.27 kWh` | `37.74 kWh` | **`48.53 kWh`** ahorrados (**`56.25%`**) |
| **Huella de carbono evitada (CAMMESA)** | — | — | **`16.99 kg CO2e/día`** evitados (`0.35 kg CO2e/kWh`) |
| **Leche protegida (SIGLeA)** | — | — | **`80.00 L/día`** = **`$34400.00 ARS/día`** (`$430.00 ARS/L`) |

---

## Testing, Guantelete AST y Markers Oficiales

Markers declarados en [pytest.ini](pytest.ini):
- `unit`: pruebas unitarias puras
- `architecture`: verificación AST de Clean Architecture y cota de 60 líneas
- `integration`: pruebas de adaptadores, ML y componentes
- `e2e`: pruebas integrales end-to-end del sistema

Comandos de verificación oficial:

```bash
# Suite completa en modo headless (PyQt6 offscreen)
QT_QPA_PLATFORM=offscreen ./venv/bin/pytest --verbose

# Solo pruebas integrales End-to-End
QT_QPA_PLATFORM=offscreen ./venv/bin/pytest -m e2e

# Guantelete AST de Clean Architecture, 0-byte __init__.py y cota <= 60 líneas
./venv/bin/python tests/test_architecture.py

# Verificación de tipado estricto en src/
./venv/bin/pyright src/
```
