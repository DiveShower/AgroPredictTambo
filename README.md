# Sistema Predictivo de Estrés Térmico (MVP) — AgroChallenge 2026

Software de **Refrigeración Sectorizada e Inteligente para Ganado Lechero** desarrollado bajo **Clean Architecture (4 anillos: Domain, Application, Interface Adapters, Infrastructure)** para el desafío **Nestlé Conecta — AgroChallenge 2026**.

## Instalación y Entorno (Linux / Python 3.10–3.12 Estable)

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Copiar `.env.example` a `.env` y ajustar las variables si se desea usar Telegram o hardware serie:

```bash
cp .env.example .env
```

## Ejecución de Tests

```bash
pytest -v
# Solo capa de dominio (sin dependencias externas)
pytest tests/test_domain/ -v
```

## Modos de Arranque

```bash
# Interfaz de consola interactiva (CLI)
python src/main.py --cli

# Simulación analítica de ahorro 24h en consola
python src/main.py --cli --benchmark

# Aplicación Nativa de Escritorio (PyQt6 SCADA)
python src/main.py --desktop

# Estación Desktop con perfil offline de ola de calor para demo
python src/main.py --desktop --demo-heatwave

# Bot de Telegram en modo standalone (headless)
python src/main.py --bot
```
