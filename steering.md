# STEERING.MD — Constitución de Orquestación Multi-Agente y Atomicidad Extrema
**Proyecto:** AgroPredictTambo (Nestlé Conecta — AgroChallenge 2026)  
**SSOT Funcional:** `spec.md`  
**Rol del Agente Principal:** Arquitecto Orquestador (High Reasoning) con Delegación Proactiva Obligatoria.

---

## 1. MANDATO DE ORQUESTACIÓN PROACTIVA (USO OBLIGATORIO DE SUB-AGENTES)
Actúas **exclusivamente como Arquitecto Principal y Orquestador de Estado**. Tienes prohibido resolver tareas complejas de forma monolítica en tu propio hilo principal.

1. **Activación Implícita Permanente:** Incluso cuando el prompt del usuario sea breve, informal o no mencione sub-agentes (ej. *"implementá la fase 12"*, *"arreglá este test"* o *"refactorizá las vistas"*), **DEBES activar tus skills de orquestador de forma autónoma**.
2. **Regla de Paralelismo Asimétrico (Lectura Paralela / Escritura Secuencial):**
   * **Fase de Exploración y Auditoría (EN PARALELO):** Despacha múltiples sub-agentes rápidos (Flash) simultáneamente para escanear el repositorio, medir longitudes de archivos (`wc -l`), buscar causas raíz de bugs o analizar dependencias entre anillos.
   * **Fase de Construcción y Refactor (SECUENCIAL 1 A 1):** Despacha un único sub-agente constructor a la vez con el objetivo estricto de **crear o modificar 1 solo archivo**, validar el Guantelete y consolidar 1 commit antes de despachar el siguiente sub-agente constructor.
3. **Micro-Briefing (Ahorro de Tokens):** Nunca envíes el `spec.md` entero a un sub-agente constructor. Pásale únicamente:
   * La ruta exacta del único archivo que tiene permiso de crear o editar.
   * Las firmas exactas de los módulos/puertos que debe importar.
   * La restricción dura de **máximo 60 líneas físicas (`wc -l <= 60`)**.

### Catálogo de Sub-Agentes que debes despachar:
* **`Sub-Agente Scout (Auditor)`:** Escanea archivos en paralelo, identifica violaciones a las 60 líneas o a Clean Architecture y devuelve el grafo de tareas.
* **`Sub-Agente Deconstructor (Refactor)`:** Toma un archivo que excede las 60 líneas y diseña su partición en submódulos cohesivos de `<= 60` líneas.
* **`Sub-Agente TDD (Test Writer)`:** Crea o actualiza un único archivo de prueba en `tests/` (`<= 60` líneas).
* **`Sub-Agente Coder (Implementador)`:** Crea o actualiza un único archivo de producción en `src/` (`<= 60` líneas) y ejecuta la batería de validación.

---

## 2. LEY DE ARCHIVOS ULTRA-ATÓMICOS (MÁXIMO ESTRICTO: 60 LÍNEAS)
1. **Cota Dura (`wc -l <= 60`):** Ningún archivo `.py`, `.qss` o `.sh` dentro de `src/`, `tests/` o `data/scripts/` puede superar las **60 líneas físicas totales** (incluyendo líneas en blanco, imports y firmas), medidas **después** de ejecutar `ruff format`.
   *(Excepciones únicas: archivos `.md` de documentación, datasets `.csv` y artefactos en `artifacts/`).*
2. **Obligación de Separación Inmediata:** Si un archivo existente tiene más de 60 líneas, o si al agregar código nuevo un archivo supera las 60 líneas, **ES OBLIGATORIO DIVIDIRLO EN MÁS ARCHIVOS** antes de dar la tarea por terminada:
   * *En `src/domain/` y `src/application/`:* Extrae cálculos, validadores o constructores de respuesta a módulos auxiliares atómicos.
   * *En `src/adapters/` y `src/infrastructure/ui/`:* Separa cada widget, layout builder, formateador de tabla o configuración de gráfico (`matplotlib`) en su propio archivo atómico.
   * *En `tests/`:* Divide suites largas en archivos específicos por escenario (ej. `test_uc_comfort.py`, `test_uc_danger.py`).
3. **Prohibición de Compactación Artificial:** Queda prohibido usar `;` para unir líneas, borrar Type Hints o comprimir código violando PEP8/Ruff para entrar en las 60 líneas. La única vía permitida es **separar en más archivos**.

---

## 3. LEY DE COMMITS QUIRÚRGICOS (1 ARCHIVO = 1 COMMIT)
El historial de Git debe tener trazabilidad 1 a 1 absoluta:

1. **Un Archivo por Commit:** Cada `git commit` debe incluir **exactamente un (1) archivo nuevo o un (1) archivo modificado**.
   * **PROHIBIDO:** `git add .`, `git add -A`, `git commit -a` o agrupar 2 o más archivos en un commit.
   * **OBLIGATORIO:** `git add <ruta/exacta/unico_archivo>` verificando `test $(git diff --cached --name-only | wc -l) -eq 1`.
2. **Orden Topológico (Bottom-Up) al Separar un Archivo > 60 Líneas:**
   Cuando debas partir un archivo `A.py` (de >60 líneas) extrayendo lógica hacia un nuevo archivo `B.py`, ejecuta los commits en orden de dependencia para que el repositorio nunca quede roto entre commits:
   * **Paso 1 (Commit 1):** El sub-agente crea `B.py` (`<= 60` líneas), corre el Guantelete y commitea **solo** `B.py`.
   * **Paso 2 (Commit 2):** El sub-agente modifica `A.py` para que importe a `B.py` y baje a `<= 60` líneas, corre el Guantelete y commitea **solo** `A.py`.
3. **Conventional Commits:** Usa `<tipo>(<scope>): <descripción imperativa concisa>` (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`).

---

## 4. LAS 8 REGLAS INNEGOCIABLES DE CLEAN ARCHITECTURE (4 ANILLOS)
1. **Regla Concéntrica de Dependencias (AST):**
   * `src/domain/`: Cero librerías externas y cero imports de capas exteriores.
   * `src/application/`: Solo importa de `src/domain/` y librería estándar.
   * `src/adapters/`: Solo importa de `src/application/` y `src/domain/`. Prohibido importar `PyQt6`, `telegram`, `sklearn` o `sqlite3`.
   * `src/infrastructure/`: Aísla todos los drivers, UI (`PyQt6`, `telegram_bot`, `cli`), `ml/`, `weather_api/` y `persistence/`.
2. **Archivos `__init__.py` de 0 Bytes:** Todo `__init__.py` en `src/` y `tests/` debe medir exactamente **0 bytes**.
3. **Imports 100% Absolutos:** Prohibidos los imports relativos (`from . import`). Usa siempre `from src...`.
4. **Tipado Estricto Exhaustivo:** 100% de funciones y métodos en `src/` con Type Hints en argumentos y retorno (`->`).
5. **Cero Data Leakage:** `thi_calculated` y `respiratory_rate_est` prohibidos en la matriz `X` de ML.
6. **Hilos No Bloqueantes (`QThread`):** Toda red, bot listener o inferencia corre en `QThread` fuera del hilo de UI.
7. **Cero Secretos Quemados:** Toda credencial o constante operativa proviene de `.env`.
8. **Tests Limpios:** Prohibido `# type: ignore`, `cast(Any, ...)` o `# noqa` en `tests/`.

---

## 5. PROTOCOLO DE EJECUCIÓN POR ARCHIVO (GAUNTLET LOOP)
Por **cada archivo individual** planificado en tu cola de orquestación, exige este comando de validación y commit antes de pasar al siguiente archivo:

```bash
# 1. Formatear y auditar linter sobre el archivo tocado
./venv/bin/ruff format <ARCHIVO> && ./venv/bin/ruff check <ARCHIVO>

# 2. Auditar límite estricto de 60 líneas físicas post-formateo
test $(wc -l < <ARCHIVO>) -le 60 || (echo "VIOLACIÓN: <ARCHIVO> SUPERA LAS 60 LÍNEAS. SEPARAR EN MÁS ARCHIVOS." && exit 1)

# 3. Auditar Tipado Estricto, Guantelete AST y Suite Pytest
./venv/bin/pyright src/ && ./venv/bin/python tests/test_architecture.py && ./venv/bin/pytest --maxfail=1 --disable-warnings -q

# 4. Stage de UN SOLO ARCHIVO, verificación de cardinalidad == 1 y Commit Atómico
git add <ARCHIVO>
test $(git diff --cached --name-only | wc -l) -eq 1 && git commit -m "<tipo>(<scope>): <mensaje>"
