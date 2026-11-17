# Especificación de Proyecto: Sistema Predictivo de Estrés Térmico (MVP)
## Refrigeración Sectorizada e Inteligente para Ganado Lechero

* **Documento:** `spec.md`
* **Autores:** Iván & Facundo
* **Contexto:** Nestlé Conecta — AgroChallenge 2026 (Eje: Lechería Regenerativa, Eficiencia Hídrica y Bienestar Animal)
* **Versión:** 2.3.0 (Strict 4-Ring Clean Architecture: Domain / Application / Adapters / Infrastructure, Multi-Interface Synced State & No-Leakage ML)
* **Entorno de Desarrollo:** Linux (Konsole / Kate / Python 3.10–3.12 Estable / Qt6)

---

## 1. Visión General y Propuesta de Valor

### 1.1 El Problema Agronómico y Operativo
En los tambos de la cuenca lechera (Argentina / Cono Sur), el estrés térmico durante el período estival provoca caídas de entre el **10% y el 25% en la producción diaria de leche**, además de afecciones reproductivas e inmunológicas en las vacas. 

El estándar tradicional mitiga el calor mediante:
1. **Temporizadores fijos (timers de reloj):** Encienden bombas y ventiladores a horarios prefijados (ej. de 10:00 a 18:00 hs, 8 horas continuas), sin correlación con el ITH real ni con el pronóstico horario.
2. **Refrigeración masiva indiferenciada:** Riega y ventila todas las instalaciones en bloque, derrochando miles de litros de agua y kilovatios en sectores vacíos (ej. corrales de espera cuando el lote de vacas ya pasó a la sala de ordeñe o a pastoreo) o mojando camas de descanso donde el agua dispara el riesgo de mastitis.

### 1.2 La Solución Propuesta (MVP AgroChallenge)
Un sistema de **Refrigeración Sectorizada Predictiva** gobernado por Machine Learning (sin *data leakage*) y reglas bio-climáticas del INTA:
* **Anticipación:** Predice la evolución del Índice de Temperatura y Humedad (ITH/THI) y la carga térmica efectiva animal en ventanas de $+1\text{h}$ y $+2\text{h}$ mediante pronóstico meteorológico e inercia acumulada.
* **Sectorización Inteligente y Sanitaria:** Evalúa el tambo en zonas independientes (*Corral de espera*, *Línea de comederos/alimentación*, *Sombra/descanso*). Solo activa electroválvulas y ventiladores en sectores que registran **ocupación real** y superan el umbral tolerable del lote, bloqueando estrictamente la aspersión de agua en sectores de cama orgánica (*Compost Barn* / descanso) para prevenir mastitis.
* **Micro-ciclos de Enfriamiento Evaporativo:** Sustituye el mojado continuo por ciclos técnicos validados por INTA Rafaela (mojado de lomo con gota gruesa de 40 seg seguido de barrido con ventilación forzada de 4.5 min).
* **Métrica Central de Retorno:** Ahorro medible superior al **35% en agua** (por gestión inteligente de software, superando el **75%** al combinar con boquillas de bajo caudal) y **40% en energía eléctrica**, garantizando la homeostasis animal y protegiendo el pico de lactancia.

### 1.3 Análisis y Justificación de Interfaz: App Nativa de Escritorio (Desktop SCADA)
En la industria lechera moderna, la interfaz elegida define la adopción real del producto. La aplicación se estructura bajo un enfoque **multicanal complementario y sincronizado en tiempo real**:

#### ¿Por qué la App Nativa de Escritorio (PyQt6 / PySide6) es la solución recomendada para el usuario final?
1. **La Realidad Operativa del Tambo:** En la oficina o sala de leche, las computadoras de campo gestionan la ordeñadora mecánica, los tanques de frío y las raciones (ej. software de DeLaval, GEA o Lely). Una aplicación de escritorio nativa se integra de forma natural en esa estación de trabajo, ejecutándose las 24 horas sin depender de navegadores web pesados.
2. **Resiliencia Rural (Funcionamiento Offline y Conectividad Intermitente):** Las zonas rurales lecheras de Argentina sufren caídas frecuentes de enlace 4G o satelital. Una aplicación de escritorio almacena localmente el pronóstico meteorológico cacheado y las reglas heurísticas, garantizando que el ganado nunca quede sin refrigeración ante una desconexión de internet.
3. **Impacto Visual Supremo para el Jurado (Demo AgroChallenge):** Una app de escritorio permite presentar un tablero de control industrial tipo SCADA:
   * **Mapa interactivo del tambo** con los sectores cambiando de color en tiempo real (verde, amarillo, rojo).
   * **Curva gráfica animada** del pronóstico de ITH para las próximas 24 horas y los momentos exactos de micro-nebulización.
   * **Panel de ROI en vivo:** Medidores que computan el ahorro acumulado de litros de agua, energía eléctrica ($/kWh) y leche defendida en proporción a las horas de estrés mitigadas.
4. **Coexistencia Sincronizada con Alertas Móviles (Telegram Bot):** La Desktop App actúa como la **"Estación Base"** en la oficina, mientras que el Bot de Telegram actúa como el **"Control Móvil de Bolsillo"** para cuando el productor recorre los potreros. Ambos consumen **exactamente los mismos casos de uso y comparten el estado de sectores en tiempo real** (corriendo el listener del bot en un hilo worker dentro de la estación base o compartiendo persistencia SQLite), de modo que cualquier comando enviado desde el celular se refleja instantáneamente en la pantalla SCADA.

### 1.4 Estrategia Escalonada de Entregables: Los 3 Niveles de MVP (Roadmap Anti-Bloqueos)
Para garantizar que el equipo siempre disponga de un software 100% operativo y testeable en cada etapa (evitando el síndrome del proyecto que "casi funciona"), el desarrollo se estructura en **tres niveles progresivos de Producto Mínimo Viable (MVP)**:

```text
[ MVP Nivel 1: Core Engine & CLI ]  --->  [ MVP Nivel 2: Bot Telegram & QR ]  --->  [ MVP Nivel 3: Desktop SCADA & ESG ]
  - Dominio 100% puro testeado              - Canal móvil interactivo                - Tablero industrial PyQt6 sincronizado
  - Modelo ML Random Forest sin leakage     - Handlers atómicos y push HTTP          - Curva ITH 24h (matplotlib)
  - Balance de ahorro L y kWh en terminal   - Demo en vivo en celular de jurados     - Reporte PDF formal Nestlé
  (Hito Base Funcional en 48-72h)           (Hito de Respaldo Competitivo)           (Hito de Máximo Impacto Demo Day)
```

1. **MVP Nivel 1: "Core Engine & Consola CLI" (Hito Funcional Base - Fases 1 a 8)**
   * **Alcance Técnico:** Lógica de negocio pura en `src/domain/`, Value Objects con validación NRC y marcadores fisiológicos (Oliveira et al., 2025), Entidades `Sector` y `CoolingOrder`, Pipeline de ML pragmático con Scikit-Learn (`RandomForestClassifier`), conexión a Open-Meteo y Runner de terminal interactivo (`python src/main.py --cli`).
   * **Propósito:** Certificar que el núcleo algorítmico, las predicciones climáticas y el cálculo analítico de litros y kWh ahorrados funcionan a la perfección sin depender de interfaces gráficas ni frameworks de UI.
2. **MVP Nivel 2: "Canal Móvil Ágil / Bot de Telegram con QR" (Hito de Demostración Rápida - Fase 11)**
   * **Alcance Técnico:** Conexión del Core Engine al bot oficial de Telegram mediante `python-telegram-bot` consumiendo los mismos casos de uso, alertas push síncronas vía REST y generación automática del código QR (`qrcode[pil]`) para el pitch. Comandos `/estado`, `/pronostico`, `/sectores`, `/ocupar`, `/prediccion`, `/ahorro` y `/reporte`.
   * **Propósito Estratégico (Red de Seguridad):** Telegram es extraordinariamente rápido de integrar (en pocas horas). Si el desarrollo visual en PyQt6 demandara más tiempo del previsto, **el MVP Nivel 2 ya constituye una solución 100% funcional, interactiva y presentable para ganar el AgroChallenge**: cada miembro del jurado escanea el QR y prueba el sistema en vivo desde su teléfono.
3. **MVP Nivel 3: "Estación Base Completa / Desktop SCADA & Reportes ESG" (Hito Premium - Fases 9, 10 & 12)**
   * **Alcance Técnico:** Tablero SCADA industrial nativo en PyQt6 con grilla de sectores sincronizada con el Bot de Telegram, reactividad de colores, animación de relés de aspersión y ventilación, curva gráfica de ITH a 24 horas (`matplotlib`), sliders de simulación para el jurado y generador del Reporte de Sustentabilidad en PDF.
   * **Propósito:** Demostración de máxima sofisticación técnica en pantalla grande para la estación de control del tambo y el pitch principal.

---

### 1.5 Los 4 Mandamientos del Desarrollo Ágil y Pragmático (Clean & Lean)
Para avanzar a máxima velocidad sin fricciones técnicas, Iván y Facu deben respetar estas directivas durante toda la codificación:

1. **Empezar Estrictamente "De Adentro hacia Afuera" (Inside-Out):**
   * El código arranca en `src/domain/value_objects/` (`thi_score.py`, `weather_conditions.py`, `nocturnal_recovery.py`, etc.) y `src/domain/entities/` (`sector.py`, `cooling_order.py`).
   * **Regla de oro:** No se escribe una sola línea de interfaz gráfica (Qt), Telegram, SQLite ni llamadas de red hasta que la suite unitaria (`pytest tests/test_domain/`) certifique que el cálculo de ITH y los niveles 0, 1 y 2 funcionan sin errores.
2. **Pragmatismo Radical en Machine Learning (Scikit-Learn Tabular sin Data Leakage):**
   * Queda expresamente prohibido sobrediseñar redes neuronales profundas o hacer trampa pasando el target pre-calculado como feature. Como demostraron Becker et al. (2021) y Pacheco et al. (2020), un modelo **Random Forest** o **Gradient Boosting** que integra **temperatura, humedad, viento, radiación solar, hora del día, depresión de bulbo húmedo, inercia térmica de 3h y deuda nocturna** supera ampliamente al ITH estático porque captura la carga térmica efectiva real sobre el animal.
3. **Control Riguroso del Hilo Gráfico en PyQt6 (`QThread` Obligatorio):**
   * Toda llamada a la API meteorológica, inferencia de Scikit-Learn o escucha de comandos de Telegram debe ejecutarse dentro de workers en segundo plano (`weather_sync_worker.py` y `telegram_bot_worker.py` heredando de `QThread`). Jamás se realizan operaciones de red o I/O bloqueante en el hilo de la UI, asegurando que la ventana mantenga **60 fps fluidos** y nunca se congele en Linux.
4. **El Bot de Telegram como Salvaguarda de Entrega:**
   * Si el pulido visual de la app de escritorio consume demasiado tiempo de maquetado QSS, se pivota de inmediato hacia el Bot de Telegram para cerrar el MVP Nivel 2. Esto garantiza que el equipo nunca llegue al día del pitch con las manos vacías.

---

## 2. Fundamentos Bio-Matemáticos y Fisiológicos (Literatura INTA & Oliveira et al., 2025)

### 2.1 Índice de Temperatura y Humedad (ITH / THI)
Se utiliza la formulación estándar del *National Research Council* (NRC / Thom) adaptada a grados Celsius ($T$ en °C, $HR$ en % relativo de 0 a 100):

$$\text{ITH} = (1.8 \times T + 32) - \left[(0.55 - 0.0055 \times HR) \times (1.8 \times T - 26)\right]$$

### 2.2 Umbrales de Estrés Térmico Parametrizables por Lote y Marcadores Fisiológicos
De acuerdo con la revisión científica de **Oliveira et al. (2025, *Animals*, 15, 249)** y los protocolos del **INTA Rafaela**, los umbrales de estrés térmico dependen del nivel metabólico-productivo del lote alojado en cada sector:
* **Rodeo General / Media Producción:** Umbral de Alerta en $\text{ITH} = 72.0$, Umbral de Peligro en $\text{ITH} = 78.0$.
* **Rodeo de Alta Producción ($>35\text{ kg/día}$, ej. sector de sombras/descanso diferenciado):** Mayor calor metabólico endógeno, reduciendo los umbrales a $\text{ITH} = 68.0 - 70.0$ (Alerta) e $\text{ITH} = 76.0$ (Peligro).

| Nivel | Estado / Categoría | Rango ITH (Rodeo Gral / Alta Prod.) | Marcador Fisiológico (Oliveira et al., 2025) | Acción del Sistema Predictivo |
| :---: | :--- | :---: | :--- | :--- |
| **0** | **Confort** | $\text{ITH} < 72.0$ (o $< 68.0 - 70.0$ alta prod.) | Frecuencia respiratoria $<60\text{ resp/min}$. Temp. rectal $\approx 38.5\text{ °C}$. | Equipos apagados. Monitoreo pasivo. |
| **1** | **Alerta Leve** | $72.0 \le \text{ITH} < 78.0$ ($68.0 - 76.0$ alta prod.) | Frecuencia respiratoria $60 - 80\text{ resp/min}$. Jadeo incipiente. | Activar **solo ventilación forzada** (flujo de aire $\sim 2.5\text{ m/s}$). |
| **2** | **Estrés Peligroso / Grave** | $\text{ITH} \ge 78.0$ ($\ge 76.0$ alta prod.) | Frecuencia respiratoria $>80\text{ resp/min}$. Temp. rectal $\approx 40.0\text{ °C}$. | Activar **sistema combinado (aspersión de bajo caudal + ventilación)** en sectores con piso de hormigón; **solo ventilación máxima** en cama orgánica. |

> **Arquitectura de Umbrales en el Dominio:** El Value Object `THI_Score` calcula el valor matemático del ITH y asigna un nivel base (por defecto con umbrales 72.0 / 78.0, o recibiendo umbrales parametrizados). A su vez, cada entidad `Sector` posee sus propios umbrales configurables (`thi_threshold_alert`, `thi_threshold_danger`), los cuales se reducen dinámicamente hasta en $3.0\text{ puntos}$ cuando `NocturnalRecovery` detecta deuda térmica nocturna acumulada.

### 2.3 Dinámica de Enfriamiento, Caudales Optimizados y Reglas por Instalación

#### Optimización de Caudal de Aspersión (Chen et al., 2016 en Oliveira et al., 2025)
* El sobredimensionamiento clásico de bombas utiliza caudales elevados de hasta $4.9\text{ L/min}$ por aspersor, provocando anegamiento y derroche de agua dulce.
* Los ensayos validados por Chen et al. (2016) demuestran que un caudal eficiente de **$1.3\text{ L/min}$ por aspersor** (gota gruesa de 3–5 mm que penetra el pelaje hasta la piel sin formar neblina aislante):
  * Logra **exactamente el mismo descenso de temperatura corporal** ($0.3\text{ °C a }0.7\text{ °C}$).
  * Produce **la misma ganancia en producción de leche** ($+3.3\text{ a }+3.7\text{ kg/vaca/día}$).
  * **Reduce en un $73.5\%$ el consumo de agua** respecto al caudal de $4.9\text{ L/min}$.

#### Reglas de Sectorización por Tipo de Instalación (Higiene y Salud de Ubre)
* En tambos con sistema **Compost Barn** o piquetes de tierra/sombra, la aspersión de agua **no debe aplicarse sobre la cama de descanso**, ya que el exceso de humedad deteriora el compostaje, degrada el score de higiene de ubre y dispara el Recuento de Células Somáticas (RCS / SCC), elevando la incidencia de mastitis ambiental (Oliveira et al., 2025).
* **Regla de Dominio (`allows_water_sprinkling`):** Las órdenes de aspersión con agua (`CoolingOrder.water_mist_seconds > 0`) quedan restringidas estrictamente a sectores con piso de hormigón (`allows_water_sprinkling = True`):
  1. **Corral de Espera Pre-ordeñe (`corral_espera`):** Piso de hormigón ranurado (`allows_water_sprinkling = True`, `sprinkler_count = 10`, `fan_count = 4`).
  2. **Pista de Alimentación / Comederos (`comederos`):** Piso de hormigón (`allows_water_sprinkling = True`, `sprinkler_count = 15`, `fan_count = 6`).
  3. **Zona de Descanso / Sombras (`sombras`):** Cama orgánica / piquete (`allows_water_sprinkling = False`, `sprinkler_count = 0`, `fan_count = 4`). Incluso en Nivel 2 (Peligro), el sistema activa **exclusivamente ventilación forzada**, manteniendo la cama seca.

#### Parámetros Técnicos e Hidráulicos para el Cálculo Exacto de Recursos
* **Aspersión Eficiente por Sector Activo (Nivel 2 y `allows_water_sprinkling == True`):**
  * Caudal unitario optimizado: $q_{\text{opt}} = 1.3\text{ L/min}$ por aspersor (frente a $q_{\text{trad}} = 4.9\text{ L/min}$ tradicional).
  * Duración del pulso de mojado por ciclo: $t_{\text{agua}} = 40\text{ segundos}$ ($0.667\text{ min}$).
  * Duración de barrido de ventilación por ciclo: $t_{\text{vent}} = 270\text{ segundos}$ ($4.5\text{ min}$).
  * Duración total del micro-ciclo: $T_{\text{ciclo}} = 310\text{ segundos}$ ($5.167\text{ min} \approx 11.61\text{ ciclos/hora}$).
  * **Fracción activa de bombeo en Nivel 2 (Duty Cycle Hídrico):** $40\text{ s} / 310\text{ s} = 12.90\%$ del tiempo de la hora ($\approx 7.74\text{ min de agua efectiva por hora de estrés Nivel 2}$).
  * **Consumo de agua por hora en un sector $s$ en Nivel 2:**
    $$V_{\text{pred}}(s, \text{hora}) = N_{\text{aspersores}}(s) \times 1.3\text{ L/min} \times 7.74\text{ min/h}$$
  * Potencia eléctrica de bomba de agua: $P_{\text{bomba}} = 2.2\text{ kW}$ ($3\text{ HP}$), operando solo durante la fracción activa de mojado ($12.90\%$ de la hora en Nivel 2).
* **Ventilación Industrial por Sector Activo (Nivel 1 o Nivel 2):**
  * Potencia unitaria por ventilador: $P_{\text{vent\_unit}} = 0.75\text{ kW}$ (ej. 4 ventiladores = $3.0\text{ kW}$; 6 ventiladores = $4.5\text{ kW}$).
  * En Nivel 1 opera de forma continua durante la hora activa; en Nivel 2 opera durante el barrido evaporativo ($270\text{ s} / 310\text{ s} = 87.10\%$ del ciclo, o continuo para máximo confort).

#### Modelo Tradicional (Baseline de Contraste: 8 Horas Fijas, 10:00 a 18:00 hs)
Para transparentar el impacto ante el jurado de Nestlé, el caso de uso `CalculateSavingsUseCase` reporta dos métricas complementarias:
1. **Ahorro Puro por Gestión Inteligente de Software (Mismo Caudal Instalado $1.3\text{ L/min}$):**
   * Contrasta el timer fijo tradicional de **8 horas continuas** (con ciclos simples de 50% o continuo en todos los sectores con aspersores sin importar ocupación ni pronóstico) contra la activación predictiva sectorizada por micro-ciclos ($12.9\%$ duty cycle solo con presencia animal e $\text{ITH} \ge \text{Umbral}$). Demuestra un ahorro puro de software del **$40\%$ al $65\%$**.
2. **Ahorro Integral del Proyecto (Software + Optimización Hidráulica Chen et al., 2016):**
   * Contrasta contra una instalación tradicional sin optimizar ($4.9\text{ L/min}$ por aspersor durante 8 horas fijas), alcanzando ahorros hídricos totales superiores al **$75\% - 85\%$**.
* **Fórmulas de Ahorro Relativo:**
  $$\% \text{ Ahorro Agua} = \frac{V_{\text{trad}} - V_{\text{pred}}}{V_{\text{trad}}} \times 100 \quad ; \quad \% \text{ Ahorro kWh} = \frac{E_{\text{trad}} - E_{\text{pred}}}{E_{\text{trad}}} \times 100$$

### 2.4 Estrategia de Ingesta Meteorológica: Clima Actual y Pronóstico Horario Futuro
Para que el sistema sea genuinamente **predictivo** (y no un mero termostato reactivo), la ingesta climática cubre dos dimensiones temporales simultáneas:
1. **Tiempo Real ($t_0$):** Conocer el estado actual del tambo para verificar si se requiere enfriamiento inmediato.
2. **Pronóstico Horario ($t+1\text{h}, t+2\text{h}, \dots, t+24\text{h}$):** Anticipar el incremento térmico de la tarde. Si a las 11:30 hs el $\text{ITH} = 69.5$ (Confort para el corral general con umbral $72.0$), pero el pronóstico meteorológico anticipa que a las 13:30 hs el $\text{ITH}$ alcanzará $78.5$ (Peligro), el sistema programa el pre-enfriamiento preventivo antes de que el lote de animales entre al corral o comedero, evitando que el calor corporal comience a acumularse.

#### Proveedor Primario Seleccionado: Open-Meteo API
* **Endpoint unificado:** `https://api.open-meteo.com/v1/forecast`
* **Ventajas técnicas para el MVP:**
  * **Sin API Key:** No expira tokens, no bloquea las pruebas del jurado y facilita el despliegue directo desde consola.
  * **Respuesta combinada:** En una **única petición HTTP GET**, la API entrega el bloque `current` (condiciones actuales) y el bloque `hourly` (pronóstico hora por hora para las próximas 24 a 48 horas).
  * **Variables agronómicas completas (incluyendo radiación solar):** `temperature_2m`, `relative_humidity_2m`, `wind_speed_10m`, `shortwave_radiation`.
* **Ejemplo de consulta para Rafaela (Santa Fe):**
  ```text
  GET https://api.open-meteo.com/v1/forecast?latitude=-31.25&longitude=-61.48
      &current=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation
      &hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation
      &forecast_days=2&timezone=auto
  ```
* **Proveedor Secundario (Fallback):** OpenWeatherMap (`/weather` y `/forecast`), configurable opcionalmente en el archivo `.env`.

### 2.5 Inercia Térmica Nocturna y Deuda Calórica Acumulada
En la fisiología de la vaca lechera de alta producción, la tolerancia al calor diurno depende críticamente de la **recuperación nocturna**:
* **Principio Biológico:** Si durante la noche (21:00 a 06:00 hs) el ITH desciende por debajo de $65.0$ durante al menos $6\text{ horas}$, el animal disipa el calor metabólico acumulado y comienza el día siguiente en equilibrio homeostático.
* **El Problema de las "Noches Tropicales":** Si el ITH nocturno permanece elevado ($\ge 65.0$, y especialmente $> 70.0$), el ganado no logra disipar calor, produciendo **deuda térmica acumulada** (*Thermal Debt*).
* **Ajuste Dinámico de Umbrales en el Modelo:**
  El Value Object `NocturnalRecovery` computa las horas nocturnas frescas ($\text{ITH} < 65.0$). Si $\text{Horas}(\text{ITH} < 65.0) < 6$, se calcula una penalización proporcional ($0.5\text{ puntos}$ por cada hora faltante de descanso fresco, hasta un máximo de $3.0\text{ puntos}$) que reduce dinámicamente los umbrales de cada sector:
  $$\text{Umbral Efectivo}(s) = \text{Umbral Base}(s) - \text{Penalización Nocturna (hasta } 3.0\text{ puntos)}$$
  Esto anticipa la refrigeración en días subsiguientes a noches tropicales, protegiendo al animal antes de que colapse.

### 2.6 Cuantificación de Impacto Nestlé: Huella de Carbono y Dinero Protegido
Para que la propuesta se alinee con los compromisos de sustentabilidad de Nestlé (*Net Zero 2050* y *Lechería Regenerativa*), los ahorros físicos se traducen en métricas ESG y financieras dinámicas:
* **Factor de Emisión de Carbono (CAMMESA):**
  Cada $\text{kWh}$ eléctrico ahorrado en bombas y ventiladores evita la emisión de gases de efecto invernadero según el factor oficial de la matriz energética argentina:
  $$\text{Emisiones Evitadas (kg CO}_2\text{e)} = \text{kWh Ahorrados} \times 0.35\text{ kg CO}_2/\text{kWh}$$
* **Valor Financiero de Leche Protegida Proporcional a las Horas de Estrés (Panel SIGLeA):**
  La literatura del INTA evidencia mermas de entre $2.0\text{ y }4.0\text{ litros/vaca/día}$ durante jornadas completas de estrés calórico no mitigado ($\sim 8\text{ a }10\text{ horas}$ de calor diurno), lo que equivale a una pérdida aproximada de **$0.35\text{ L/vaca}$ por cada hora de estrés severo (Nivel 2)** y **$0.15\text{ L/vaca}$ por cada hora de estrés leve (Nivel 1)** (con un tope biológico de $4.0\text{ L/vaca/día}$).
  Para un lote de $N$ vacas en ordeñe donde el sistema mitiga $H_1$ horas de Alerta y $H_2$ horas de Peligro:
  $$\text{Litros Protegidos Día} = N \times \min\left(4.0,\; 0.15 \times H_1 + 0.35 \times H_2\right)$$
  $$\text{Retorno Económico Protegido (\$)} = \text{Litros Protegidos} \times \text{Precio SIGLeA (\$/Litro)}$$
  Esto permite que el tablero SCADA actualice los litros y pesos defendidos hora por hora de forma rigurosa y demuestre un **período de repago (ROI) inferior a 1 temporada estival**.

### 2.7 Agenda Horaria Automática del Tambo (Rutina de Ordeñe Programada)
Para evitar que el tambero deba encender o apagar manualmente la presencia de vacas en la aplicación durante la faena diaria:
* El Value Object `MilkingSchedule` almacena los turnos fijos de ordeñe (ej. Turno Mañana: 04:30 a 07:00 hs; Turno Tarde: 16:00 a 18:30 hs).
* **Pre-enfriamiento Preventivo:** Si a la hora de ingreso al corral de espera ($16:00\text{ hs}$) la predicción marca $\text{ITH} \ge \text{Umbral Peligro}$, el sistema inicia un pre-mojado de piso y cañerías $15\text{ minutos antes}$ ($15:45\text{ hs}$). Así, el lote de vacas entra a una instalación ya refrigerada, evitando el pico agudo de calor por aglomeración.

---

## 3. Arquitectura de Software y Principios SOLID (Innegociables)

El diseño sigue estrictamente **Clean Architecture en 4 anillos concéntricos (Domain → Application → Interface Adapters → Infrastructure & Drivers)**. La lógica central del tambo no depende de librerías de ML, APIs de clima, PyQt6 ni del framework de Telegram; y los mecanismos de entrega pesados (`PyQt6`, `python-telegram-bot`, CLI, ML, SQLite) viven confinados dentro de `src/infrastructure/`.

```
       +-------------------------------------------------------------------------+
       |                 4. INFRASTRUCTURE & DRIVERS LAYER (src/infrastructure/) |
       |  +--------------------+  +----------------------+  +-----------------+  |
       |  | UI Desktop (PyQt6) |  | UI Telegram / CLI    |  | ML & Artifacts  |  |
       |  | Views/Widgets/Qt   |  | Bot Runner / Console |  | Sklearn/.joblib |  |
       |  +---------+----------+  +----------+-----------+  +--------+--------+  |
       |  | Weather Adapters (OpenMeteo/Mock) | SQLite Cache | Serial IoT / PDF |  |
       +------------+------------------------+-----------------------+-----------+
                    | (invoca controladores / implementa puertos)    |
                    v                                                |
       +-------------------------------------------------------------+-----------+
       |                   3. INTERFACE ADAPTERS LAYER (src/adapters/)           |
       |  ViewModels (Desktop) | Command Handlers & Formatters (Telegram / CLI)  |
       +------------------------------------+------------------------------------+
                                            | (invoca Casos de Uso)
                                            v
       +-------------------------------------------------------------------------+
       |                        2. APPLICATION LAYER (src/application/)          |
       |        Use Cases: PredictSectorStress / CalculateSavings / Status       |
       +------------------------------------+------------------------------------+
                                            | (usa Entidades, VOs y Puertos)
                                            v
       +-------------------------------------------------------------------------+
       |                          1. DOMAIN LAYER (src/domain/)                  |
       |  Entities: Sector, Farm, CoolingOrder, HeatStressAlert                  |
       |  Value Objects: THI_Score, WeatherConditions, ResourceSavings           |
       |  Ports: IWeatherProvider, IModelPredictor, ISectorRepository, ICache    |
       +-------------------------------------------------------------------------+
```

### Aplicación Rigurosa de Principios SOLID

| Principio | Aplicación Radical en el Proyecto |
| :--- | :--- |
| **S (Single Responsibility)** | Cada clase, función o contrato reside en su **propio archivo atómico**. Ningún archivo contiene múltiples responsabilidades o entidades agrupadas. |
| **O (Open/Closed)** | El dominio y los casos de uso están cerrados a modificaciones y abiertos a extensiones mediante puertos (`Protocol`). Agregar una nueva fuente climática o modelo de IA no altera el código existente. |
| **L (Liskov Substitution)** | Cualquier implementación de puerto (ej. `MockWeatherAdapter` frente a `OpenMeteoAdapter`, o `HeuristicPredictor` frente a `SklearnPredictor`) es 100% intercambiable sin alterar el comportamiento esperado por la capa de aplicación. |
| **I (Interface Segregation)** | Interfaces mínimas y atómicas: un puerto por necesidad. `IWeatherProvider` no sabe de persistencia, `IWeatherCache` no sabe de llamadas HTTP, y `INotifier` no sabe de cálculo de estrés. |
| **D (Dependency Inversion)** | La regla dorada: Las flechas de dependencia solo apuntan hacia adentro. Los casos de uso dependen exclusivamente de contratos abstractos (`ports/`), y la inyección se resuelve en el Composition Root (`main.py`). |

### 3.2 Regla de Archivos Atómicos y Modularidad Estricta (Anti-Bloat Policy)
Para garantizar código profesional, mantenible y libre de desorden ("archivos sucios con muchas líneas"):
1. **Un Archivo = Una Sola Responsabilidad / Una Clase Principal:** Se prohíben archivos multipropósito acumuladores (como `entities.py`, `ports.py`, `handlers.py`, `views.py` o `utils.py`). Cada concepto del negocio tiene su propio módulo.
2. **Límite de Longitud:** Ningún archivo de lógica debe superar las **80 a 120 líneas de código**. Si un componente crece, debe descomponerse en submódulos o componentes independientes.
3. **Ergonomía en Kate y Terminal:** Facilita abrir pestañas puntuales en el editor (ej. `sector.py`, `thi_score.py`) para inspección inmediata sin scroll excesivo.
4. **Cero Conflictos de Merge en Git:** Iván y Facu trabajan simultáneamente en módulos independientes sin colisiones de código al fusionar ramas.
5. **Espejo de Pruebas 1 a 1:** A cada archivo de lógica en `src/` le corresponde un archivo de prueba atómico directo en `tests/`.

---

## 4. Estructura Completa del Repositorio (`Tree` Atómico y Granular)

```text
AgroChallenge/ (raíz del repositorio)
├── .env.example                               # Plantilla de variables de entorno (API keys, bot token)
├── .gitignore                                 # Exclusión de venv, cache, bytecode, datos crudos y .joblib
├── pytest.ini                                 # Configuración de rutas de prueba
├── README.md                                  # Guía rápida de instalación y ejecución en terminal
├── requirements.txt                           # Dependencias compatibles con Python 3.10–3.12 (Estable)
├── spec.md                                    # Esta especificación técnica
│
├── src/
│   ├── __init__.py
│   ├── main.py                                # Composition Root: Inyección de dependencias y arranque
│   │
│   ├── domain/                                # ANILLO 1: CAPA DE DOMINIO (Cero dependencias externas)
│   │   ├── __init__.py
│   │   ├── entities/                          # Entidades con ciclo de vida e identidad
│   │   │   ├── __init__.py
│   │   │   ├── sector.py                      # Entidad Sector (capacidad, ocupación, umbrales, piso)
│   │   │   ├── cooling_order.py               # Orden de activación (mojado 40s / ventilación 270s)
│   │   │   ├── heat_stress_alert.py           # Alerta de estrés clasificada por nivel
│   │   │   └── farm.py                        # Entidad Tambo (agrupador de sectores y coordenadas)
│   │   │
│   │   ├── value_objects/                     # Objetos inmutables por valor
│   │   │   ├── __init__.py
│   │   │   ├── thi_score.py                   # Cálculo matemático NRC de ITH y categoría parametrizable
│   │   │   ├── weather_conditions.py          # Mediciones de temp, humedad, viento y radiación solar
│   │   │   ├── resource_savings.py            # Cuantificación de litros de agua y kWh ahorrados
│   │   │   ├── cooling_cycle.py               # Parámetros temporales del ciclo evaporativo (40s/270s)
│   │   │   ├── nocturnal_recovery.py          # Horas frescas nocturnas y deuda térmica acumulada
│   │   │   ├── carbon_footprint.py            # Conversor a kg CO2e evitados (Factor CAMMESA)
│   │   │   ├── economic_impact.py             # Valor financiero de leche protegida (SIGLeA por hora)
│   │   │   └── milking_schedule.py            # Horarios de ordeñe y pre-enfriamiento automático
│   │   │
│   │   ├── fixtures/                          # Datos semilla de dominio inmutables
│   │   │   ├── __init__.py
│   │   │   └── default_farm.py                # Configuración inicial de los 3 sectores del Tambo San José
│   │   │
│   │   ├── ports/                             # Interfaces abstractas (Contratos con typing.Protocol)
│   │   │   ├── __init__.py
│   │   │   ├── weather_provider_port.py       # Contrato IWeatherProvider (actual + pronóstico)
│   │   │   ├── model_predictor_port.py        # Contrato IModelPredictor (inferencia 0, 1, 2 con contexto)
│   │   │   ├── sector_repository_port.py      # Contrato ISectorRepository (persistencia sectores)
│   │   │   ├── weather_cache_port.py          # Contrato IWeatherCache (resiliencia offline)
│   │   │   ├── notifier_port.py               # Contrato INotifier (emisión de alertas push síncronas)
│   │   │   ├── hardware_controller_port.py    # Contrato IHardwareController (Relés/LEDs IoT)
│   │   │   └── report_generator_port.py       # Contrato IReportGenerator (Reportes PDF/ESG)
│   │   │
│   │   └── exceptions/                        # Excepciones de dominio tipadas
│   │       ├── __init__.py
│   │       ├── base_domain_exception.py       # Excepción raíz del dominio
│   │       ├── invalid_weather_exception.py   # Datos meteorológicos fuera de rango físico
│   │       └── sector_not_found_exception.py  # Consulta a sector inexistente
│   │
│   ├── application/                           # ANILLO 2: CAPA DE APLICACIÓN (Casos de uso orquestadores)
│   │   ├── __init__.py
│   │   ├── dtos/                              # Data Transfer Objects atómicos
│   │   │   ├── __init__.py
│   │   │   ├── predict_stress_request_dto.py
│   │   │   ├── predict_stress_response_dto.py
│   │   │   ├── calculate_savings_request_dto.py
│   │   │   ├── calculate_savings_response_dto.py
│   │   │   ├── sustainability_report_dto.py
│   │   │   └── sector_status_dto.py
│   │   │
│   │   └── use_cases/                         # Un archivo por Caso de Uso
│   │       ├── __init__.py
│   │       ├── predict_sector_stress_uc.py    # Evalúa clima t0, t+1h y emite órdenes
│   │       ├── calculate_savings_uc.py        # Compara consumo tradicional vs predictivo
│   │       ├── toggle_sector_occupancy_uc.py  # Actualiza la presencia de vacas en un sector
│   │       ├── get_farm_status_uc.py          # Consolida el estado general del tambo
│   │       └── generate_sustainability_report_uc.py # Genera informe formal auditado Nestlé
│   │
│   ├── adapters/                              # ANILLO 3: ADAPTADORES DE INTERFAZ (Sin dependencia PyQt6/Telegram)
│   │   ├── __init__.py
│   │   ├── desktop/
│   │   │   ├── __init__.py
│   │   │   └── viewmodels/                    # Presenters / ViewModels delgados que traducen DTOs <-> UI
│   │   │       ├── __init__.py
│   │   │       ├── scada_viewmodel.py
│   │   │       ├── forecast_viewmodel.py
│   │   │       └── savings_viewmodel.py
│   │   ├── telegram/
│   │   │   ├── __init__.py
│   │   │   ├── handlers/                      # Controladores atómicos por comando (delegan a Use Cases)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── start_handler.py           # Comando /start y /help
│   │   │   │   ├── state_handler.py           # Comando /estado (clima e ITH actual)
│   │   │   │   ├── forecast_handler.py        # Comando /pronostico (curva proyectada)
│   │   │   │   ├── sectors_handler.py         # Comando /sectores (ocupación y equipos)
│   │   │   │   ├── occupy_handler.py          # Comando /ocupar (simulación de ganado en vivo)
│   │   │   │   ├── predict_handler.py         # Comando /prediccion (órdenes de activación)
│   │   │   │   ├── savings_handler.py         # Comando /ahorro (balance de recursos)
│   │   │   │   └── report_handler.py          # Comando /reporte (envía el PDF de sustentabilidad)
│   │   │   └── formatters/
│   │   │       ├── __init__.py
│   │   │       └── message_formatter.py       # Generador de tablas con texto monoespaciado y emojis
│   │   └── cli/
│   │       ├── __init__.py
│   │       ├── cli_controller.py              # Controlador delgado que orquesta los casos de uso en CLI
│   │       └── cli_formatter.py               # Tabuladores de texto para terminal
│   │
│   └── infrastructure/                        # ANILLO 4: INFRAESTRUCTURA Y DRIVERS (Detalles Técnicos y UI)
│       ├── __init__.py
│       ├── weather_api/                       # Adaptadores de clima externo
│       │   ├── __init__.py
│       │   ├── open_meteo_adapter.py          # Proveedor primario (Open-Meteo REST API)
│       │   ├── open_weather_adapter.py        # Proveedor secundario (OpenWeatherMap API)
│       │   ├── mock_weather_adapter.py        # Generador de escenarios para tests y demo
│       │   └── weather_api_mapper.py          # Mapeador de payload JSON a WeatherConditions
│       │
│       ├── ml/                                # Detalles de Machine Learning (Scikit-Learn encapsulado en src)
│       │   ├── __init__.py
│       │   ├── sklearn_predictor_adapter.py   # Inferencia con modelo .joblib serializado
│       │   ├── heuristic_predictor_adapter.py # Fallback determinístico basado en reglas ITH
│       │   ├── feature_builder.py             # Vectorizador de variables para inferencia (sin leakage)
│       │   ├── train_pipeline.py              # Script de entrenamiento y validación
│       │   └── artifacts/                     # Artefactos ML entrenados encapsulados dentro de ml/
│       │       ├── heat_stress_classifier.joblib
│       │       └── training_report.json
│       │
│       ├── persistence/                       # Persistencia local para resiliencia rural
│       │   ├── __init__.py
│       │   ├── sqlite_weather_cache_adapter.py# Cache local de pronóstico meteorológico
│       │   └── cache_schema.py                # DDL de tablas SQLite (cache climático y estado de sectores)
│       │
│       ├── notifications/                     # Adaptadores de mensajería saliente
│       │   ├── __init__.py
│       │   └── telegram_notifier_adapter.py   # Emisor HTTP REST síncrono thread-safe a Telegram API
│       │
│       ├── hardware/                          # Adaptadores para Maqueta / Relés IoT (Hardware-in-the-loop)
│       │   ├── __init__.py
│       │   ├── serial_relay_adapter.py        # Control físico de relés/LEDs por puerto serie (USB/Arduino)
│       │   └── mock_relay_adapter.py          # Simulador de hardware en memoria
│       │
│       ├── reporting/                         # Generación documental de sustentabilidad
│       │   ├── __init__.py
│       │   └── pdf_sustainability_report_adapter.py # Renderizador PDF con gráficos y métricas
│       │
│       ├── repositories/                      # Repositorios de datos
│       │   ├── __init__.py
│       │   └── in_memory_sector_repo.py       # Repositorio de sectores (compartido en proceso y/o SQLite)
│       │
│       └── ui/                                # Mecanismos de entrega pesados (PyQt6 / Bot Runner / CLI Runner)
│           ├── __init__.py
│           ├── desktop/                       # Driver Nativo de Escritorio (PyQt6 / Qt)
│           │   ├── __init__.py
│           │   ├── app.py                     # Inicialización de QApplication y carga de estilos
│           │   ├── main_window.py             # Ventana principal (Docking, barra superior y tabs)
│           │   ├── styles/
│           │   │   └── dark_agro_theme.qss    # Hoja de estilos Qt limpia y moderna
│           │   ├── workers/                   # Hilos en segundo plano (QThread) para no bloquear la UI
│           │   │   ├── __init__.py
│           │   │   ├── weather_sync_worker.py # Peticiones HTTP e inferencia ML en background
│           │   │   └── telegram_bot_worker.py # Listener del Bot en background sincronizado con la UI
│           │   ├── components/                # Widgets reutilizables independientes
│           │   │   ├── __init__.py
│           │   │   ├── sector_card_widget.py  # Tarjeta interactiva de sector (color, relé, toggle)
│           │   │   ├── kpi_metric_card_widget.py # Tarjeta de métrica de ahorro ($/L/kWh/CO2)
│           │   │   └── thi_gauge_widget.py    # Barra / Cuadrante de nivel de estrés
│           │   └── views/                     # Vistas por pestaña
│           │       ├── __init__.py
│           │       ├── scada_view.py          # Tablero SCADA con grilla de sectores en vivo
│           │       ├── forecast_view.py       # Gráfico interactivo curva ITH 24h
│           │       ├── savings_view.py        # Panel de ROI, sostenibilidad y leche protegida
│           │       ├── simulation_view.py     # Sliders de simulación interactiva para el jurado
│           │       └── report_view.py         # Vista previa y botón de exportación PDF
│           │
│           ├── telegram_bot/                  # Driver Bot de Telegram (python-telegram-bot)
│           │   ├── __init__.py
│           │   ├── bot_service.py             # Orquestador del ciclo de vida del bot
│           │   └── qr_generator.py            # Generador de imagen QR para escaneo del jurado
│           │
│           └── cli/                           # Driver de Consola (Pruebas técnicas ágiles)
│               ├── __init__.py
│               └── console_runner.py          # Runner interactivo para depuración en Konsole
│
├── data/                                      # GESTIÓN DE DATOS Y DATASETS (No ejecutable)
│   ├── raw/                                   # Archivos climáticos crudos descargados
│   ├── processed/                             # Dataset limpio con features térmicas
│   │   └── weather_heat_stress_dataset.csv
│   ├── cache/                                 # Directorio para base de datos SQLite local y bot_qr.png
│   └── scripts/                               # Scripts atómicos de ingeniería de datos
│       ├── fetch_historical_weather.py
│       └── generate_synthetic_dataset.py
│
└── tests/                                     # SUITE DE PRUEBAS AUTOMATIZADAS (ESPEJO ATÓMICO)
    ├── conftest.py                            # Fixtures compartidas de pytest
    ├── test_domain/                           # Tests unitarios del dominio (sin mocks de framework)
    │   ├── test_thi_score.py                  # Verificación matemática de fórmula NRC vs tablas INTA
    │   ├── test_weather_conditions.py         # Validaciones de rangos físicos y radiación
    │   ├── test_sector.py                     # Cambio de ocupación, umbrales y regla anti-mastitis
    │   ├── test_cooling_order.py              # Validación de tiempos de mojado y ventilación
    │   ├── test_nocturnal_recovery.py         # Deuda térmica nocturna y penalización de umbral
    │   ├── test_resource_savings.py           # Cálculo de ahorro de litros de agua y kWh
    │   ├── test_economic_impact.py            # Leche protegida por hora y huella de carbono CAMMESA
    │   └── test_milking_schedule.py           # Ventanas de ordeñe y pre-enfriamiento preventivo
    ├── test_application/                      # Tests unitarios de casos de uso (con mocks de puertos)
    │   ├── test_predict_sector_stress_uc.py
    │   ├── test_calculate_savings_uc.py
    │   └── test_toggle_sector_occupancy_uc.py
    └── test_infrastructure/                   # Tests de integración técnica
        ├── test_open_meteo_adapter.py         # Parsing y respuesta de API meteorológica
        ├── test_sqlite_weather_cache.py       # Escritura, lectura y expiración de cache
        ├── test_sklearn_predictor_adapter.py  # Inferencia con archivo .joblib
        └── test_heuristic_predictor_adapter.py# Verificación de lógica de fallback
```

---

## 5. Especificación Atómica de Dominio, Contratos y Puertos

Cada componente se escribe en su propio archivo atómico dentro de `src/domain/`.

### 5.1 Value Object: `src/domain/value_objects/weather_conditions.py`
```python
from dataclasses import dataclass
from datetime import datetime
from src.domain.exceptions.invalid_weather_exception import InvalidWeatherException

@dataclass(frozen=True)
class WeatherConditions:
    temperature_c: float            # Temperatura ambiente en °C (-15.0 a 55.0)
    relative_humidity: float        # Humedad relativa en % (0.0 a 100.0)
    wind_speed_kmh: float           # Velocidad de viento en km/h (>= 0.0)
    timestamp: datetime             # Momento de la observación o pronóstico
    solar_radiation_wm2: float = 0.0# Radiación solar de onda corta en W/m² (>= 0.0)

    def __post_init__(self) -> None:
        if not (-15.0 <= self.temperature_c <= 55.0):
            raise InvalidWeatherException(f"Temperatura fuera de rango físico: {self.temperature_c} °C")
        if not (0.0 <= self.relative_humidity <= 100.0):
            raise InvalidWeatherException(f"Humedad fuera de rango: {self.relative_humidity}%")
        if self.wind_speed_kmh < 0.0 or self.solar_radiation_wm2 < 0.0:
            raise InvalidWeatherException("El viento y la radiación solar no pueden ser negativos.")
```

### 5.2 Value Object: `src/domain/value_objects/thi_score.py`
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class THI_Score:
    value: float
    stress_level: int           # 0 = Confort, 1 = Alerta, 2 = Peligro

    @classmethod
    def calculate(
        cls,
        temp_c: float,
        rh: float,
        threshold_alert: float = 72.0,
        threshold_danger: float = 78.0,
    ) -> "THI_Score":
        # Fórmula NRC / Thom adaptada a Celsius
        val = (1.8 * temp_c + 32) - ((0.55 - 0.0055 * rh) * (1.8 * temp_c - 26))
        rounded_val = round(val, 2)
        if rounded_val < threshold_alert:
            level = 0
        elif rounded_val < threshold_danger:
            level = 1
        else:
            level = 2
        return cls(value=rounded_val, stress_level=level)
```

### 5.3 Entidad: `src/domain/entities/sector.py`
```python
from dataclasses import dataclass

@dataclass
class Sector:
    sector_id: str                      # Ej: "corral_espera", "comederos", "sombras"
    name: str                           # Nombre descriptivo
    cow_capacity: int                   # Cantidad máxima de animales
    current_occupancy: bool             # True = vacas presentes en el sector
    thi_threshold_alert: float = 72.0   # 72.0 rodeo gral / 68.0-70.0 alta producción
    thi_threshold_danger: float = 78.0  # 78.0 rodeo gral / 76.0 alta producción
    allows_water_sprinkling: bool = True# True en piso de hormigón; False en cama orgánica (anti-mastitis)
    sprinkler_count: int = 10           # Cantidad de picos aspersores de 1.3 L/min en el sector
    fan_count: int = 4                  # Cantidad de ventiladores de 0.75 kW en el sector

    def set_occupancy(self, occupied: bool) -> None:
        self.current_occupancy = occupied

    def evaluate_stress_level(self, thi_val: float, nocturnal_penalty: float = 0.0) -> int:
        alert_limit = self.thi_threshold_alert - nocturnal_penalty
        danger_limit = self.thi_threshold_danger - nocturnal_penalty
        if thi_val < alert_limit:
            return 0
        if thi_val < danger_limit:
            return 1
        return 2

    def requires_cooling(self, thi_val: float, nocturnal_penalty: float = 0.0) -> bool:
        return self.current_occupancy and (self.evaluate_stress_level(thi_val, nocturnal_penalty) > 0)
```

### 5.4 Entidad: `src/domain/entities/cooling_order.py` y Value Objects Complementarios
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class CoolingOrder:
    sector_id: str
    stress_level: int           # 0 = Confort, 1 = Alerta, 2 = Peligro
    water_mist_seconds: int     # 40s si Nivel 2 y sector.allows_water_sprinkling == True; 0s en otro caso
    fan_ventilation_seconds: int# 270s en Nivel 1 o 2; 0s en Nivel 0
    target_time: datetime       # Hora proyectada para el ciclo
    justification: str          # Descripción técnica para el operador (ej. protección mastitis o pre-enfriado)
```

* **Contratos de Value Objects Complementarios (`src/domain/value_objects/`):**
  * `nocturnal_recovery.py` (`NocturnalRecovery`): Recibe las mediciones nocturnas (21:00 a 06:00 hs), cuenta `cool_hours` ($\text{ITH} < 65.0$) y calcula `threshold_penalty: float = min(3.0, max(0.0, (6 - cool_hours) * 0.5))`.
  * `resource_savings.py` (`ResourceSavings`): Almacena `water_saved_liters`, `water_saved_pct`, `energy_saved_kwh`, `energy_saved_pct`, desglosando el ahorro puro de software ($1.3\text{ L/min}$ vs timer fijo de 8 hs) y el ahorro hidráulico combinado ($4.9\text{ L/min}$).
  * `carbon_footprint.py` (`CarbonFootprint`): Calcula `co2_avoided_kg = round(energy_saved_kwh * 0.35, 2)` según factor CAMMESA.
  * `economic_impact.py` (`EconomicImpact`): Calcula `milk_protected_liters = cow_count * min(4.0, 0.15 * hours_level_1 + 0.35 * hours_level_2)` y su valorización monetaria en ARS según precio SIGLeA.
  * `milking_schedule.py` (`MilkingSchedule`): Evalúa si una hora objetivo coincide con la ventana de pre-enfriamiento ($15\text{ min}$ antes del turno de ordeñe de mañana o tarde).

### 5.5 Puertos Abstractos Atómicos (`src/domain/ports/`)

#### `src/domain/ports/weather_provider_port.py`
```python
from typing import Protocol, List
from src.domain.value_objects.weather_conditions import WeatherConditions

class IWeatherProvider(Protocol):
    def get_current_weather(self, lat: float, lon: float) -> WeatherConditions: ...
    def get_hourly_forecast(self, lat: float, lon: float, hours: int = 24) -> List[WeatherConditions]: ...
```

#### `src/domain/ports/model_predictor_port.py`
```python
from typing import Protocol, Sequence
from src.domain.value_objects.weather_conditions import WeatherConditions

class IModelPredictor(Protocol):
    def predict_stress_level(
        self,
        conditions: WeatherConditions,
        recent_history: Sequence[WeatherConditions] = (),
        nocturnal_debt_hours: int = 0,
    ) -> int: ...
```

#### `src/domain/ports/sector_repository_port.py`
```python
from typing import Protocol, List
from src.domain.entities.sector import Sector

class ISectorRepository(Protocol):
    def get_all_sectors(self) -> List[Sector]: ...
    def get_by_id(self, sector_id: str) -> Sector: ...
    def update_occupancy(self, sector_id: str, is_occupied: bool) -> None: ...
```

#### `src/domain/ports/weather_cache_port.py`
```python
from typing import Protocol, List
from src.domain.value_objects.weather_conditions import WeatherConditions

class IWeatherCache(Protocol):
    def save_forecast(self, conditions_list: List[WeatherConditions]) -> None: ...
    def get_cached_forecast(self) -> List[WeatherConditions]: ...
    def is_cache_valid(self, max_age_hours: int = 6) -> bool: ...
```

#### `src/domain/ports/notifier_port.py`
```python
from typing import Protocol
from src.domain.entities.heat_stress_alert import HeatStressAlert

class INotifier(Protocol):
    def send_alert(self, alert: HeatStressAlert) -> bool: ...
```

#### `src/domain/ports/hardware_controller_port.py`
```python
from typing import Protocol

class IHardwareController(Protocol):
    def activate_water_valve(self, sector_id: str, duration_seconds: int) -> bool: ...
    def activate_ventilation_fan(self, sector_id: str, duration_seconds: int) -> bool: ...
    def emergency_shutoff_all(self) -> None: ...
```

#### `src/domain/ports/report_generator_port.py`
```python
from typing import Protocol
from src.domain.value_objects.resource_savings import ResourceSavings

class IReportGenerator(Protocol):
    def generate_sustainability_pdf(self, farm_name: str, savings: ResourceSavings, output_path: str) -> str: ...
```

### 5.6 Especificación de la Interfaz Nativa de Escritorio (PyQt6 Desktop SCADA)

La aplicación de escritorio se diseña para funcionar como la **Estación de Monitoreo Central del Tambo** y centro de demostración interactiva para el jurado de Nestlé Conecta, sincronizada en tiempo real con el Bot de Telegram.

#### Wireframe Lógico de la Ventana Principal (`MainWindow`)
```text
+----------------------------------------------------------------------------------------------------+
|  [AGRO-PREDICT 2026] - Sistema Predictivo de Estrés Térmico | Tambo: San José (Rafaela, SF)       |
|  Estado: ONLINE (Open-Meteo + Bot Sync) | Clima: 31.4°C | HR: 62% | Viento: 14 km/h | ITH: 81.2   |
+----------------------------------------------------------------------------------------------------+
| [TAB 1: SCADA TAMBO]  |  [TAB 2: CURVA ITH 24H]  |  [TAB 3: PANEL ROI & SOSTENIBILIDAD]  |  [TAB 4] |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +---------------------------+  +---------------------------+  +---------------------------+       |
|  | SECTOR 1: CORRAL ESPERA   |  | SECTOR 2: COMEDEROS       |  | SECTOR 3: SOMBRAS/DESCANSO|       |
|  | Piso: Hormigón (10 asp.)  |  | Piso: Hormigón (15 asp.)  |  | Piso: Cama Compost (Seco) |       |
|  | Capacidad: 80 vacas       |  | Capacidad: 120 vacas      |  | Capacidad: 100 vacas      |       |
|  | Ocupación: [ V ] OCUPADO  |  | Ocupación: [   ] VACÍO    |  | Ocupación: [ V ] OCUPADO  |       |
|  | Nivel Estrés: 🔴 PELIGRO  |  | Nivel Estrés: 🔴 PELIGRO  |  | Nivel Estrés: 🔴 PELIGRO  |       |
|  |                           |  |                           |  |                           |       |
|  | [BOMBA ASPERSIÓN: ACTIVA] |  | [BOMBA ASPERSIÓN: OFF]    |  | [ASPERSIÓN: BLOQUEADA]    |       |
|  | Pulso: 40s (Restan: 18s)  |  | *Sector vacío: Ahorro 100%|  | *Protección Anti-Mastitis |       |
|  |                           |  |                           |  |                           |       |
|  | [VENTILADORES: ACTIVOS]   |  | [VENTILADORES: OFF]       |  | [VENTILADORES: ACTIVOS]   |       |
|  | Barrido: 270s (Restan 190s)|  | *Sector vacío: Ahorro 100%|  | Flujo continuo 2.5 m/s    |       |
|  +---------------------------+  +---------------------------+  +---------------------------+       |
|                                                                                                    |
|----------------------------------------------------------------------------------------------------|
|  BARRA DE CONTROL RÁPIDO & OVERRIDE MANUAL:                                                        |
|  [ Sincronizar Clima Ahora ]  |  [ Simular Ola de Calor (Demo) ]  |  [ Detención de Emergencia ]   |
+----------------------------------------------------------------------------------------------------+
```

#### Pestañas (Tabs) Detalladas:
1. **Tab 1: Tablero SCADA en Vivo:**
   * Visualización tipo tarjetas de cada sector con cambio reactivo de colores según el estrés (Verde = Confort, Amarillo = Alerta, Rojo = Peligro).
   * Switches interactivos de ocupación (`True` / `False`) sincronizados bidireccionalmente con el comando `/ocupar` del Bot de Telegram. Si el usuario o un jurado desmarca la ocupación de un sector, el sistema cancela de inmediato las órdenes de mojado/ventilación y refleja el ahorro de recursos generado en tiempo real.
   * Visualización explícita de la **Regla Anti-Mastitis** en el Sector 3 (Sombras/Descanso): indica que el agua está bloqueada por protocolo sanitario sobre cama orgánica, activando únicamente ventilación forzada.
   * Animación/indicadores de electroválvulas y relés de ventilación con cronómetro regresivo de ciclo (40 seg aspersión / 270 seg barrido) gobernado por un `QTimer` no bloqueante (tick de 1s).
2. **Tab 2: Curva Predictiva ITH (24 Horas):**
   * Gráfico integrado con `matplotlib`.
   * Muestra la curva horaria proyectada de ITH.
   * Dibuja líneas horizontales de umbral crítico: Línea amarilla punteada ($\text{ITH}=72.0$, o ajustada por deuda nocturna) y línea roja sólida ($\text{ITH}=78.0$).
   * Puntos de activación: Marca visualmente las horas donde el modelo ML ha programado el pre-enfriamiento preventivo.
3. **Tab 3: Panel de Sustentabilidad y ROI (AgroChallenge & ESG):**
   * Tarjetas de impacto acumulado en tiempo real:
     * **Litros de Agua Ahorrados** (frente al timer tradicional de 8 horas continuas, mostrando tanto el ahorro por software como el ahorro combinado con boquillas de $1.3\text{ L/min}$).
     * **Kilovatios/hora (kWh) Ahorrados**.
     * **Reducción de Huella de Carbono:** $\text{kg CO}_2\text{e}$ evitados (Factor CAMMESA $0.35\text{ kg CO}_2/\text{kWh}$).
     * **Leche Protegida Estimada:** Litros de leche preservados calculados dinámicamente según las horas efectivas de estrés mitigadas.
     * **Retorno Económico en Pesos/Dólares:** Valorización monetaria de la leche defendida según panel SIGLeA.
     * **Botón de Acción Directa:** `[ Exportar Reporte de Sustentabilidad en PDF ]` para auditorías de Nestlé Conecta.
4. **Tab 4: Simulador Interactivo para el Jurado:**
   * Permite mover *sliders* de Temperatura (15°C a 45°C), Humedad (20% a 95%), Viento (0 a 40 km/h) y Radiación Solar (0 a 1000 $\text{W/m}^2$) para ver cómo el modelo ML predice en milisegundos y cómo cambian las órdenes de enfriamiento.
5. **Tab 5: Hardware-in-the-Loop (Relés / LEDs IoT):**
   * Muestra el estado del conector de hardware (`SerialRelayAdapter` o `MockRelayAdapter`).
   * Indicadores de pines físicos conmutados en tiempo real (LED azul = Válvula Agua; LED verde = Ventilador) para la maqueta física de demostración ante el jurado.

---

### 5.7 Resiliencia Rural y Modo Offline (Local Cache & Fail-Safe)
En las cuencas lecheras de Argentina, los cortes de enlace rural (4G o radioenlace) son frecuentes. Para garantizar la seguridad animal y evitar que el software se cuelgue:
1. **Capa de Persistencia (`SqliteWeatherCache`):**
   * Cada vez que se consulta con éxito la API meteorológica, se persiste el pronóstico horario completo en una base de datos local SQLite (`data/cache/weather_cache.sqlite`).
2. **Degradación Elegante (Fallback Mechanism):**
   * Si la llamada a Open-Meteo falla (timeout o red inaccesible):
     * El sistema consulta el último pronóstico cacheado para la hora actual y las próximas horas.
     * Si el cache tiene menos de 6 horas de antigüedad, opera normalmente con los datos proyectados.
     * Si no hay conexión ni cache válido, se activa el **Modo de Contingencia Local Heurístico**, emitiendo una alerta visual en la UI de escritorio y en Telegram para advertir al tambero.
3. **Seguridad Operativa (Watchdog):**
   * El sistema nunca deja electroválvulas de agua encendidas en caso de crash: cada orden de mojado tiene un tiempo límite estricto de seguridad ($60\text{ segundos}$ máximo físico enviado por comando no bloqueante al controlador de hardware).

---

### 5.8 Esquema Formal del Dataset de Entrenamiento y Features ML (Sin Data Leakage)

Para garantizar que el entrenamiento del modelo sea científicamente riguroso y defendible ante un jurado técnico, **queda prohibido incluir `thi_calculated` o `respiratory_rate_est` dentro de la matriz de entrada `X` del modelo** (evitando la circularidad donde un árbol memoriza un umbral estático).

El modelo de Machine Learning (`RandomForestClassifier`) aprende a predecir el nivel de estrés fisiológico real del animal integrando **variables meteorológicas crudas + radiación solar + alivio por viento + inercia térmica de las últimas 3 horas + deuda térmica nocturna** (siguiendo a Becker et al., 2021; Pacheco et al., 2020; Oliveira et al., 2025):

| Columna | Rol en ML | Tipo / Rango | Descripción / Justificación Científica |
| :--- | :---: | :---: | :--- |
| `timestamp` | Metadato (Índice) | `YYYY-MM-DD HH:00:00` | Fecha y hora de la observación horaria (se usa para split temporal Train/Test sin mezclar futuro con pasado) |
| `temperature_c` | **Feature (`X`)** | `float [-10.0, 50.0]` | Temperatura del aire a 2 metros en °C |
| `relative_humidity` | **Feature (`X`)** | `float [0.0, 100.0]` | Humedad relativa porcentual |
| `wind_speed_kmh` | **Feature (`X`)** | `float [0.0, 120.0]` | Velocidad del viento a 10 m en km/h (disipación por convección natural) |
| `solar_radiation_wm2` | **Feature (`X`)** | `float [0.0, 1200.0]` | Radiación solar de onda corta en $\text{W/m}^2$ (carga radiante directa sobre el animal) |
| `hour_of_day` | **Feature (`X`)** | `int [0, 23]` | Hora del día (captura el ciclo metabólico circadiano) |
| `wet_bulb_depression` | **Feature (`X`)** | `float [0.0, 30.0]` | Depresión del bulbo húmedo ($T_{\text{seca}} - T_{\text{húmeda}}$): potencial físico de enfriamiento evaporativo |
| `thi_rolling_avg_3h` | **Feature (`X`)** | `float [40.0, 100.0]` | Media móvil de las 3 horas previas ($t-3, t-2, t-1$): captura la inercia calórica acumulada |
| `nocturnal_debt_hours`| **Feature (`X`)** | `int [0, 6]` | Horas nocturnas previas en las que el animal no logró enfriarse ($\text{ITH} \ge 65.0$) |
| `thi_calculated` | Solo Auditoría | `float [40.0, 100.0]` | ITH NRC clásico (se excluye de `X` en `train_pipeline.py` y se usa como baseline de comparación) |
| `respiratory_rate_est`| Solo Auditoría | `float [30.0, 120.0]` | Frecuencia respiratoria estimada (resp/min) derivada de la carga térmica efectiva |
| `stress_level` | **TARGET (`y`)** | `int {0, 1, 2}` | Nivel de estrés bio-fisiológico ($0=\text{Confort}$, $1=\text{Alerta}$, $2=\text{Peligro}$) |

> **Construcción Biológica del Target (`stress_level`) en el Dataset:** En `generate_synthetic_dataset.py` y `fetch_historical_weather.py`, la etiqueta real `stress_level` se determina a partir del **Índice de Carga Térmica Efectiva (Effective Heat Load / Adjusted THI)** validado en la literatura, que suma al ITH base la penalización por radiación solar alta ($+0.5\text{ a }+2.5\text{ pts}$ cuando $\text{Rad} > 500\text{ W/m}^2$), la inercia acumulada de las últimas 3 horas, la deuda nocturna, y descuenta el alivio convectivo por viento ($-0.3\text{ pts}$ por cada $\text{m/s}$ de brisa). Así, el modelo ML supera significativamente al ITH estático porque anticipa cuándo la combinación de radiación, falta de viento e inercia empujará a la vaca al jadeo severo ($>80\text{ resp/min}$) incluso antes de que el termómetro seco aislado cruce el umbral clásico.

---

### 5.9 Especificación Operativa del Bot de Telegram (Canal Móvil, Push Síncrono y Sincronización con UI)

El Bot de Telegram actúa como el **"Control Móvil de Bolsillo"** del productor agropecuario y canal de demostración interactiva directa para los jurados de Nestlé Conecta.

#### 1. Arquitectura Técnica, Sincronización en Vivo y Creación del Bot
* **Proceso de Creación (1 minuto, 100% gratuito en `@BotFather`):**
  1. Enviar `/newbot` a `@BotFather`, definir nombre visible (*AgroPredict Tambo*) y usuario (`@AgroStressNestleBot`).
  2. Configurar el token en `.env`:
     ```bash
     TELEGRAM_BOT_TOKEN="718293849:AAHkL7Xy9..."
     TELEGRAM_ADMIN_CHAT_ID="" # Opcional: ID de chat predeterminado para alertas push
     ```
* **Sincronización en Tiempo Real entre Bot y Desktop GUI (`telegram_bot_worker.py`):**
  * Cuando se inicia la estación base (`python src/main.py --desktop`) y existe un `TELEGRAM_BOT_TOKEN` configurado, `MainWindow` levanta automáticamente `TelegramBotWorker(QThread)` en segundo plano compartiendo **la misma instancia en memoria de `ISectorRepository` y de los Casos de Uso**.
  * Cada vez que un miembro del jurado ejecuta `/ocupar <sector_id> <true/false>` desde su celular, el worker invoca `ToggleSectorOccupancyUseCase` y emite la señal `sector_state_changed = pyqtSignal()`, provocando que las tarjetas SCADA de la notebook cambien de estado, color y métricas de ahorro en menos de $100\text{ ms}$ frente a los ojos del jurado.
* **Desacoplamiento Síncrono de Alertas Push (`TelegramNotifierAdapter`):**
  *Dado que `python-telegram-bot` v21+ utiliza `asyncio` mientras que los casos de uso del dominio y PyQt6 operan de forma síncrona, el adaptador `src/infrastructure/notifications/telegram_notifier_adapter.py` implementa `INotifier.send_alert()` realizando un `requests.post` HTTP directo al endpoint REST `https://api.telegram.org/bot<TOKEN>/sendMessage` (con `timeout=5`). Esto garantiza envíos *thread-safe* libres de colisiones de *event loops* desde cualquier caso de uso, CLI o `QThread`.
* **Principio de Tolerancia (Fail-Safe):**
  * Si `TELEGRAM_BOT_TOKEN` está vacío o no hay internet, el sistema **no crashea**: deshabilita silenciosamente el listener móvil y permite operar 100% en modo Consola (`--cli`) o App de Escritorio (`--desktop`).

#### 2. Registro de Usuarios y Notificaciones Push Proactivas
* **Captura del `chat_id`:**
  * Cuando el tambero o jurado busca el bot y presiona **"Iniciar"** (`/start`), `start_handler.py` registra el `chat_id` del remitente en la lista de suscriptores activos.
* **Comportamiento Automático:** Si `predict_sector_stress_uc.py` detecta que en la próxima hora ($+1\text{h}$) un sector ocupado por vacas entrará en Nivel 2 (Peligro), dispara automáticamente la alerta al teléfono:
  > *"🚨 **ALERTA PREVENTIVA TAMBO SAN JOSÉ** 🚨*\n*A las 14:00 el Sector 'Corral de Espera' alcanzará ITH 81.2 (Peligro).* \n*Plan de acción: Activación preventiva de micro-aspersión (40s) y ventiladores (270s) para evitar pérdida en curva de lactancia."*

#### 3. Catálogo de Comandos y Respuestas del Bot
| Comando | Propósito | Respuesta Esperada |
| :--- | :--- | :--- |
| `/start` o `/help` | Bienvenida | Muestra menú interactivo con botones inline del tambo y desafío Nestlé. |
| `/estado` | Monitoreo Inmediato | Reporta Temperatura, Humedad, Viento, Radiación e ITH actual con semáforo (🟢/🟡/🔴). |
| `/pronostico` | Proyección Climática | Gráfica de texto con la evolución del ITH para las próximas 24 horas. |
| `/sectores` | Estado de las Zonas | Lista los sectores, si tienen vacas (`Ocupado`/`Vacío`), regla sanitaria y relés activos. |
| `/ocupar <id> <true/false>` | Simulación Dinámica | Simula el ingreso/egreso de vacas a un sector (ej: `/ocupar corral_espera true`) y actualiza el SCADA en vivo. |
| `/prediccion` | Inferencia ML | Corre el modelo a $+1\text{h}$ e informa órdenes de enfriamiento preventivo. |
| `/ahorro` | Métricas de Negocio | Devuelve litros de agua ahorrados, kWh eléctricos, $\text{kg CO}_2\text{e}$ y litros de leche protegidos. |
| `/reporte` | Auditoría ESG | Genera y envía al chat el Reporte de Sustentabilidad en formato PDF. |

#### 4. Estrategia de Demostración para el Pitch (AgroChallenge 2026)
* El módulo `src/infrastructure/ui/telegram_bot/qr_generator.py` genera automáticamente el archivo `data/cache/bot_qr.png` con el enlace `https://t.me/<TuBotUsername>`.
* En la presentación ante el jurado, se proyecta el **Código QR** en pantalla (o desde una pestaña/modal de la app).
* Los evaluadores de Nestlé lo escanean con sus celulares, ejecutan `/ocupar`, `/prediccion` y `/ahorro`, y observan en vivo cómo la aplicación de escritorio en la notebook de Iván y Facu reacciona instantáneamente ante sus comandos.

---

## 6. Plan de Ejecución Dividido en 12 Micro-Fases (Agrupadas en 3 Niveles de MVP)

Para optimizar el flujo de trabajo en consola/Kate entre Iván y Facu, evitar sobrecargas y asegurar que cada componente sea 100% verificable antes de pasar al siguiente, el desarrollo se organiza en **12 micro-fases secuenciales estructuradas en 3 hitos de MVP**:

```text
========================================================================================
BLOQUE 1: MVP NIVEL 1 — CORE ENGINE & CONSOLA CLI (Fases 1 a 8)
========================================================================================
Fase 1: Setup & Entorno Virtual (PyQt6, Sklearn, Pytest, Dotenv)
   │
   ▼
Fase 2: Dominio Puro "Inside-Out" (Value Objects, Entidades y Tests Unitarios Pytest)
   │
   ▼
Fase 3: Extracción Climática (Tiempo Real + Forecast) & Dataset con Oliveira et al. (2025)
   │
   ▼
Fase 4: Pipeline de ML Pragmático (Scikit-Learn Random Forest Tabular)
   │
   ▼
Fase 5: Adaptador de Inferencia ML & Fail-Safe Heurístico
   │
   ▼
Fase 6: Casos de Uso (Application Layer) & Balance de Ahorro L/kWh
   │
   ▼
Fase 7: Adaptadores Climáticos & Persistencia Cache Offline Rural (SQLite)
   │
   ▼
Fase 8: Runner de Consola (CLI) & Simulación de Escenarios
   ════════════════════════════════════════════════════════════════════════════════════
   ⭐ [HITO MVP 1 CONCLUIDO]: Motor algorítmico 100% funcional y testeado en terminal.
   ════════════════════════════════════════════════════════════════════════════════════

========================================================================================
BLOQUE 2: MVP NIVEL 2 — CANAL MÓVIL ÁGIL & DEMO TELEGRAM CON QR (Fase 11)
========================================================================================
Fase 11: Canal Móvil: Bot de Telegram (Handlers Atómicos, Push Alerts y Código QR)
   ════════════════════════════════════════════════════════════════════════════════════
   ⭐ [HITO MVP 2 CONCLUIDO]: Demo interactiva en vivo en los celulares del jurado.
      *Red de seguridad: si el tiempo apremia, este producto ya es presentable al 100%.
   ════════════════════════════════════════════════════════════════════════════════════

========================================================================================
BLOQUE 3: MVP NIVEL 3 — ESTACIÓN BASE SCADA (PyQt6) & REPORTES ESG (Fases 9, 10, 12)
========================================================================================
Fase 9: Desktop Nativo (PyQt6 con QThread Asíncrono): Shell & Tablero SCADA
   │
   ▼
Fase 10: Desktop Nativo: Curva ITH 24h (matplotlib), ROI Financiero & Simulador Jurado
   │
   ▼
Fase 12: Validación End-to-End, Reporte PDF Nestlé Conecta & Pitch Deck Final
   ════════════════════════════════════════════════════════════════════════════════════
   ⭐ [HITO MVP 3 CONCLUIDO]: Solución completa SCADA industrial y reporte PDF.
   ════════════════════════════════════════════════════════════════════════════════════
```

---

### Fase 1: Configuración del Entorno, Estructura y Dependencias Base
* **Objetivo:** Disponer del entorno virtual aislado, el árbol de directorios atómico de 4 anillos (`domain`, `application`, `adapters`, `infrastructure`) y todas las dependencias (compatibles con Python 3.10–3.12 Estable y Qt6) listas en Linux.
* **Tareas Específicas:**
  1. Configurar el entorno virtual `python3 -m venv venv` y activarlo.
  2. Generar el archivo `requirements.txt` con rangos compatibles (incluyendo `PyQt6`, `matplotlib`, `pandas`, `scikit-learn`, `joblib`, `requests`, `python-telegram-bot`, `fpdf2`, `qrcode[pil]`, `pyserial`, `pytest`, `pytest-mock`, `python-dotenv`).
  3. Crear la estructura de carpetas completa de la Sección 4 con sus archivos `__init__.py` (encapsulando `ml/` y `ui/` dentro de `src/infrastructure/`, y los controladores/ViewModels delgados en `src/adapters/`).
  4. Configurar `.env.example`, `.gitignore` y `pytest.ini`.
* **Entregable:** Repositorio estructurado y entorno virtual funcional con dependencias instaladas.
* **Comando de Verificación:** `python -c "import PyQt6, matplotlib, pandas, sklearn, telegram, qrcode; print('ENTORNO LISTO')"`

---

### Fase 2: Capa de Dominio — Entidades, Value Objects y Puertos Atómicos (SOLID)
* **Objetivo:** Modelar la lógica de negocio pura y abstracta en archivos atómicos sin tocar ninguna librería externa, base de datos ni UI.
* **Tareas Específicas:**
  1. Implementar Value Objects atómicos en `src/domain/value_objects/`: `thi_score.py`, `weather_conditions.py`, `resource_savings.py`, `cooling_cycle.py`, `nocturnal_recovery.py`, `carbon_footprint.py`, `economic_impact.py` y `milking_schedule.py`.
  2. Implementar Entidades atómicas en `src/domain/entities/`: `sector.py` (con `allows_water_sprinkling`, `sprinkler_count`, `fan_count` y evaluación de umbrales con penalización nocturna), `cooling_order.py`, `heat_stress_alert.py` y `farm.py`, más los datos semilla en `src/domain/fixtures/default_farm.py`.
  3. Implementar Puertos atómicos en `src/domain/ports/`: `weather_provider_port.py`, `model_predictor_port.py`, `sector_repository_port.py`, `weather_cache_port.py`, `notifier_port.py`, `hardware_controller_port.py` y `report_generator_port.py`.
  4. Crear pruebas unitarias espejo en `tests/test_domain/` (`test_thi_score.py`, `test_weather_conditions.py`, `test_sector.py`, `test_cooling_order.py`, `test_nocturnal_recovery.py`, `test_resource_savings.py`, `test_economic_impact.py`, `test_milking_schedule.py`).
* **Entregable:** Módulo `src/domain/` 100% puro y suite unitaria de dominio aprobada con `pytest`.
* **Comando de Verificación:** `pytest tests/test_domain/`

---

### Fase 3: Adquisición, Curaduría del Dataset y Horizontes Temporales (Sin Data Leakage)
* **Objetivo:** Obtener y limpiar un dataset representativo de la cuenca lechera (Rafaela / Santa Fe: `-31.25, -61.48`) combinando variables meteorológicas, radiación solar, inercia térmica de 3h y deuda nocturna.
* **Tareas Específicas:**
  1. Desarrollar `data/scripts/fetch_historical_weather.py` utilizando la API de archivo de Open-Meteo de los veranos recientes (`temperature_2m`, `relative_humidity_2m`, `wind_speed_10m`, `shortwave_radiation`).
  2. Implementar fallback con `data/scripts/generate_synthetic_dataset.py` para generar datos continuos simulando olas de calor diurnas, radiación solar, viento y noches tropicales.
  3. Calcular las columnas de contexto: `wet_bulb_depression`, `thi_rolling_avg_3h` y `nocturnal_debt_hours`.
  4. Generar la variable target `stress_level` ($0=\text{Confort}$, $1=\text{Alerta}$, $2=\text{Peligro}$) mediante el modelo fisiológico de Carga Térmica Efectiva (Oliveira et al., 2025 / Becker et al., 2021).
  5. Guardar dataset limpio en `data/processed/weather_heat_stress_dataset.csv`.
* **Entregable:** Dataset CSV con al menos 2.000 observaciones horarias limpias y etiquetadas sin *data leakage*.
* **Comando de Verificación:** `python -c "import pandas as pd; df=pd.read_csv('data/processed/weather_heat_stress_dataset.csv'); print(df['stress_level'].value_counts())"`

---

### Fase 4: Pipeline de Machine Learning & Evaluación de Modelos
* **Objetivo:** Entrenar y evaluar un clasificador predictivo de estrés térmico con métricas de alta precisión excluyendo las columnas de auditoría (`thi_calculated`, `respiratory_rate_est`) de la matriz `X`.
* **Tareas Específicas:**
  1. Crear script de entrenamiento `src/infrastructure/ml/train_pipeline.py` y el vectorizador `src/infrastructure/ml/feature_builder.py`.
  2. Separar datos en Train y Test (80/20) respetando estrictamente el orden temporal (sin data leakage).
  3. Entrenar y comparar al menos dos modelos sobre las 8 features limpias:
     * Baseline: Regresión Logística / Decision Tree.
     * Candidato Final: Random Forest o Gradient Boosting (Scikit-Learn).
  4. Evaluar con métricas: *Accuracy*, *Precision*, *Recall* por clase y *Confusion Matrix*, contrastando contra el baseline de ITH estático.
  5. Serializar el mejor modelo en `src/infrastructure/ml/artifacts/heat_stress_classifier.joblib` y guardar reporte en `src/infrastructure/ml/artifacts/training_report.json`.
* **Entregable:** Archivo `.joblib` generado con Accuracy $\ge 85\%$ y Recall en Peligro $\ge 90\%$ + reporte JSON documentado.
* **Comando de Verificación:** `python src/infrastructure/ml/train_pipeline.py`

---

### Fase 5: Adaptador de Machine Learning & Fallback Heurístico
* **Objetivo:** Implementar el puerto `IModelPredictor` desacoplando la inferencia de la infraestructura.
* **Tareas Específicas:**
  1. Crear `src/infrastructure/ml/sklearn_predictor_adapter.py` que implementa `IModelPredictor`, cargando el archivo `.joblib` desde `src/infrastructure/ml/artifacts/` y utilizando `feature_builder.py` para construir el vector de 8 features a partir de `conditions`, `recent_history` y `nocturnal_debt_hours`.
  2. Crear `src/infrastructure/ml/heuristic_predictor_adapter.py` que implementa `IModelPredictor` usando cálculo matemático de ITH + penalización por radiación/deuda nocturna como mecanismo de seguridad (fail-safe).
  3. Probar ambos adaptadores mediante `tests/test_infrastructure/test_sklearn_predictor_adapter.py` y `test_heuristic_predictor_adapter.py`.
* **Entregable:** Inferencia encapsulada y tolerante a fallos lista para ser inyectada en los casos de uso.
* **Comando de Verificación:** `pytest tests/test_infrastructure/test_sklearn_predictor_adapter.py tests/test_infrastructure/test_heuristic_predictor_adapter.py`

---

### Fase 6: Casos de Uso (Application Layer) & Matemática de Ahorro
* **Objetivo:** Implementar la lógica orquestadora del negocio sin dependencias directas de frameworks ni interfaces.
* **Tareas Específicas:**
  1. Implementar `src/application/use_cases/predict_sector_stress_uc.py`:
     * Obtiene el clima actual, el historial reciente y el pronóstico $+1\text{h}/+2\text{h}$, más la deuda nocturna (`NocturnalRecovery`) y agenda de ordeñe (`MilkingSchedule`).
     * Obtiene los sectores del repositorio (`ISectorRepository`).
     * Para cada sector ocupado, evalúa el estrés combinando el predictor ML y los umbrales propios del sector, respetando `allows_water_sprinkling` (0s de agua en cama de compost).
     * Genera la lista de `CoolingOrder` y dispara alertas preventivas por `INotifier` si corresponde.
  2. Implementar `src/application/use_cases/calculate_savings_uc.py`, `toggle_sector_occupancy_uc.py`, `get_farm_status_uc.py` y `generate_sustainability_report_uc.py`:
     * Modela el consumo del sistema tradicional de 8 horas fijas (10:00 a 18:00 hs) vs las órdenes efectivas del sistema predictivo, calculando `ResourceSavings`, `CarbonFootprint` y `EconomicImpact`.
  3. Testear los casos de uso en `tests/test_application/` con Mocks de los puertos.
* **Entregable:** Lógica de orquestación 100% testeada con cobertura de casos borde (sectores desocupados, cama de compost sin agua, días fríos, olas de calor).
* **Comando de Verificación:** `pytest tests/test_application/`

---

### Fase 7: Adaptadores de Clima, Notificaciones, Reportes y Cache Offline SQLite
* **Objetivo:** Conectar el sistema a fuentes meteorológicas reales, notificaciones REST de Telegram, generador PDF y persistencia SQLite ante cortes de internet.
* **Tareas Específicas:**
  1. Desarrollar `src/infrastructure/weather_api/open_meteo_adapter.py` y `weather_api_mapper.py` consumiendo la API abierta (`current` y `hourly` incluyendo `shortwave_radiation`).
  2. Desarrollar `src/infrastructure/persistence/sqlite_weather_cache_adapter.py` y `cache_schema.py` para persistir localmente el pronóstico y soportar operación offline en zonas rurales.
  3. Desarrollar `src/infrastructure/weather_api/mock_weather_adapter.py` con los 3 perfiles de demo (`heatwave`, `nocturnal_debt`, `temperate`).
  4. Implementar `src/infrastructure/repositories/in_memory_sector_repo.py` inicializado con `default_farm.py`, `src/infrastructure/notifications/telegram_notifier_adapter.py` (REST HTTP síncrono) y `src/infrastructure/reporting/pdf_sustainability_report_adapter.py` (`fpdf2`).
* **Entregable:** Adaptadores de infraestructura funcionales con tests de integración en `tests/test_infrastructure/`.
* **Comando de Verificación:** `pytest tests/test_infrastructure/`

---

### Fase 8: Interfaz de Consola (CLI Runner) & Diagnóstico en Terminal
* **Objetivo:** Probar el sistema de punta a punta directamente desde Konsole/Kate con comandos de texto rápidos.
* **Tareas Específicas:**
  1. Desarrollar el controlador y formateador en `src/adapters/cli/` (`cli_controller.py`, `cli_formatter.py`) y el driver en `src/infrastructure/ui/cli/console_runner.py` con menú interactivo y modo `--benchmark`:
     * Consultar estado climático actual y cálculo de ITH en Rafaela.
     * Simular ocupación de sectores (entran/salen vacas del corral de espera).
     * Ejecutar predicción a $+1\text{h}$ y ver activación de electroválvulas y ventiladores (verificando bloqueo de agua en sector `sombras`).
     * Generar reporte comparativo de litros de agua, kWh, $\text{CO}_2\text{e}$ y leche protegida.
  2. Configurar `src/main.py` con soporte para flags de consola (`--cli`, `--desktop`, `--bot`, `--demo-heatwave`, `--benchmark`).
* **Entregable:** CLI funcional para desarrollo ágil y testing en terminal (`MVP Nivel 1` completado).
* **Comando de Verificación:** `python src/main.py --cli --benchmark`

---

### Fase 9: Aplicación Nativa de Escritorio (PyQt6) — Shell Principal, Workers & Tablero SCADA
* **Objetivo:** Construir la base de la aplicación de escritorio nativa dentro de `src/infrastructure/ui/desktop/`, los workers asíncronos (`QThread`) y los ViewModels en `src/adapters/desktop/viewmodels/`.
* **Tareas Específicas:**
  1. Crear `src/infrastructure/ui/desktop/app.py` configurando `QApplication` con la hoja de estilo `styles/dark_agro_theme.qss`.
  2. Implementar `workers/weather_sync_worker.py` y `workers/telegram_bot_worker.py` heredando de `QThread` para sincronización climática y escucha de comandos móviles en tiempo real sin bloquear el hilo gráfico.
  3. Desarrollar `src/infrastructure/ui/desktop/components/sector_card_widget.py`, `kpi_metric_card_widget.py` y `thi_gauge_widget.py`:
     * Tarjeta visual para cada sector con colores dinámicos según nivel de estrés y etiqueta de tipo de piso / protección anti-mastitis.
     * Switch interactivo de ocupación (`True`/`False`) y cronómetro regresivo de ciclo (40s / 270s) gobernado por `QTimer`.
  4. Integrar `src/infrastructure/ui/desktop/views/scada_view.py` conectado al presenter `src/adapters/desktop/viewmodels/scada_viewmodel.py` en `main_window.py`.
* **Entregable:** Aplicación de escritorio nativa abriendo en Linux y respondiendo visualmente al estado del tambo.
* **Comando de Verificación:** `python src/main.py --desktop`

---

### Fase 10: Aplicación Nativa de Escritorio (PyQt6) — Analítica 24h, ROI, Reporte PDF & Simulador Jurado
* **Objetivo:** Completar las pantallas de analítica predictiva, métricas de sostenibilidad ESG, exportación PDF y el simulador interactivo para el jurado.
* **Tareas Específicas:**
  1. Desarrollar `src/infrastructure/ui/desktop/views/forecast_view.py` y `src/adapters/desktop/viewmodels/forecast_viewmodel.py` embebiendo un gráfico de `matplotlib`:
     * Curva de ITH proyectada hora por hora a 24 horas con líneas de umbral ($\text{ITH}=72.0$ y $\text{ITH}=78.0$) y marcadores de pre-enfriamiento preventivo.
  2. Desarrollar `src/infrastructure/ui/desktop/views/savings_view.py`, `src/adapters/desktop/viewmodels/savings_viewmodel.py` y `views/report_view.py`:
     * Tarjetas KPI de Litros de Agua Ahorrados, kWh Eléctricos, Huella de Carbono CAMMESA y Litros de Leche Protegidos (SIGLeA) + botón de exportación PDF.
  3. Desarrollar `src/infrastructure/ui/desktop/views/simulation_view.py`:
     * Sliders de Temperatura, Humedad, Viento y Radiación Solar para que el jurado fuerce olas de calor y observe la respuesta del sistema en vivo.
* **Entregable:** Panel analítico, exportador PDF y simulador interactivo 100% operativos en la Desktop App.
* **Comando de Verificación:** `python src/main.py --desktop --demo-heatwave`

---

### Fase 11: Canal Móvil — Bot de Telegram Interactivo y Generador QR
* **Objetivo:** Proveer el canal de alertas móviles y control remoto sincronizado en vivo con la estación base SCADA.
* **Tareas Específicas:**
  1. Configurar el driver en `src/infrastructure/ui/telegram_bot/bot_service.py` y el generador de código QR en `src/infrastructure/ui/telegram_bot/qr_generator.py`.
  2. Implementar los handlers atómicos en `src/adapters/telegram/handlers/`:
     * `start_handler.py` (`/start` y `/help`), `state_handler.py` (`/estado`), `forecast_handler.py` (`/pronostico`), `sectors_handler.py` (`/sectores`), `occupy_handler.py` (`/ocupar <sector_id> <true/false>`), `predict_handler.py` (`/prediccion`), `savings_handler.py` (`/ahorro`) y `report_handler.py` (`/reporte`).
  3. Crear el formateador visual con tablas monoespaciadas y emojis en `src/adapters/telegram/formatters/message_formatter.py`.
* **Entregable:** Bot de Telegram respondiendo en tiempo real y sincronizando cambios de ocupación con la GUI de escritorio (`MVP Nivel 2` completado).
* **Comando de Verificación:** `python src/main.py --bot`

---

### Fase 12: Validación Integral, Benchmark de Sostenibilidad y Pitch Nestlé
* **Objetivo:** Consolidar el paquete final para el jurado con foco en retorno de inversión, sostenibilidad y arquitectura.
* **Tareas Específicas:**
  1. Correr la suite completa de pruebas unitarias y de integración (`pytest --verbose`).
  2. Ejecutar corrida de simulación completa de 24 horas y generar el documento de impacto y el PDF de sustentabilidad auditado.
  3. Preparar la estructura del Pitch Deck para AgroChallenge 2026:
     * *Gancho:* Pérdida millonaria por estrés calórico en cuencas lecheras argentinas.
     * *Innovación:* Sectorización predictiva sanitaria (anti-mastitis) vs temporizadores estáticos ciegos.
     * *Resultados numéricos:* $>35\%$ ahorro de agua por software ($>75\%$ combinado con caudal eficiente), $>40\%$ ahorro de energía, defensa de la curva de lactancia.
     * *Sustentabilidad Nestlé:* Contribución directa a la huella hídrica y carbono neutro.
* **Entregable:** Proyecto completo, suite de tests en verde y reporte ejecutivo de métricas de impacto para la presentación (`MVP Nivel 3` completado).
* **Comando de Verificación:** `pytest && python src/main.py --cli --benchmark`

---

## 7. Matriz de Distribución de Tareas (Iván & Facu)

| Micro-Fase | Perfil A (Facu) — Infraestructura, APIs & UI Desktop | Perfil B (Iván) — Dominio, Modelado & Matemática de Negocio |
| :--- | :--- | :--- |
| **Fase 1** | Configuración de entorno Linux, git, carpetas de 4 anillos y `requirements.txt` (Python 3.10–3.12 Estable). | Definición de constantes bio-climáticas y fixtures en `default_farm.py`. |
| **Fase 2** | Contratos en `src/domain/ports/*.py` y excepciones en `src/domain/exceptions/*.py`. | Implementación de `src/domain/value_objects/*.py`, `src/domain/entities/*.py` y `tests/test_domain/*.py`. |
| **Fase 3** | Script `fetch_historical_weather.py` (Open-Meteo Archive con radiación solar). | Script `generate_synthetic_dataset.py`, cálculo de inercia 3h, deuda nocturna y etiquetado fisiológico. |
| **Fase 4** | Vectorizador `src/infrastructure/ml/feature_builder.py` y split temporal Train/Test sin leakage. | Script `src/infrastructure/ml/train_pipeline.py` y artefactos en `src/infrastructure/ml/artifacts/`. |
| **Fase 5** | Serialización `.joblib` e implementación de `sklearn_predictor_adapter.py`. | Implementación de `heuristic_predictor_adapter.py` y tests en `tests/test_infrastructure/`. |
| **Fase 6** | Creación de DTOs en `src/application/dtos/*.py`, `toggle_sector_occupancy_uc.py` y `get_farm_status_uc.py`. | Implementación de `predict_sector_stress_uc.py`, `calculate_savings_uc.py` y `generate_sustainability_report_uc.py`. |
| **Fase 7** | `open_meteo_adapter.py`, `sqlite_weather_cache_adapter.py`, `telegram_notifier_adapter.py` y `pdf_sustainability_report_adapter.py`. | `mock_weather_adapter.py`, `in_memory_sector_repo.py` y adaptadores de hardware (`serial_relay_adapter.py` / `mock_relay_adapter.py`). |
| **Fase 8** | Driver `src/infrastructure/ui/cli/console_runner.py` y `src/main.py`. | Controlador/Formateador delgado en `src/adapters/cli/`, escenarios de estrés y modo `--benchmark`. |
| **Fase 9** | `src/infrastructure/ui/desktop/` (`app.py`, `main_window.py`, `dark_agro_theme.qss`, `weather_sync_worker.py`, `sector_card_widget.py`). | `telegram_bot_worker.py`, `scada_view.py`, `src/adapters/desktop/viewmodels/scada_viewmodel.py` y sync Bot $\leftrightarrow$ SCADA. |
| **Fase 10** | `forecast_view.py` (`matplotlib`), `simulation_view.py` (sliders) y `report_view.py`. | `savings_view.py`, `savings_viewmodel.py` y visualización de fórmulas de agua, kWh, $\text{CO}_2\text{e}$ y leche SIGLeA. |
| **Fase 11** | `src/infrastructure/ui/telegram_bot/` (`bot_service.py`, `qr_generator.py`) y handlers en `src/adapters/telegram/handlers/*.py`. | Formateador `src/adapters/telegram/formatters/message_formatter.py`, textos de alertas push y validación QR. |
| **Fase 12** | Pruebas de integración E2E (`pytest`), validación de hilos Qt y empaquetado para la demo. | Generación del reporte PDF Nestlé Conecta y guion/diapositivas del pitch. |

---

## 8. Criterios de Aceptación y Checklist para el Jurado

- [ ] **Clean Architecture Inmaculada (4 Anillos):** `domain/` y `application/` no importan librerías externas; `adapters/` no importa widgets ni drivers pesados; todo detalle técnico (`PyQt6`, `sklearn`, `telegram`, `sqlite3`, `ml/artifacts`) vive encapsulado dentro de `src/infrastructure/`.
- [ ] **Regla de Archivos Atómicos y SRP Extremo:** Ningún archivo de lógica o interfaz supera las 100-120 líneas de código. Se erradican archivos agrupadores; cada entidad, valor objeto, caso de uso, adaptador y componente gráfico reside en su propio archivo atómico.
- [ ] **Desacoplamiento Tecnológico y Sincronización Multi-Interfaz:** Es posible correr el sistema desde terminal (`--cli`), solo bot (`--bot`) o estación completa (`--desktop` con worker de Telegram sincronizado en tiempo real).
- [ ] **Sectorización Efectiva y Regla Anti-Mastitis:** Si un sector está vacío (`current_occupancy = False`), se cancela cualquier enfriamiento; y si el sector tiene cama orgánica (`allows_water_sprinkling = False`), jamás se activa la válvula de agua incluso con $\text{ITH} > 80$.
- [ ] **Resiliencia Rural Offline:** Ante desconexión simulada de internet, el sistema conmuta sin crashear a `SqliteWeatherCacheAdapter` y activa el fail-safe heurístico.
- [ ] **Validación Matemática:** El cálculo de ITH coincide con una precisión de $\pm 0.1$ frente a la tabla oficial del INTA Rafaela / NRC.
- [ ] **Precisión de Inferencia sin Data Leakage:** Modelo de Machine Learning entrenado sin incluir `thi_calculated` en `X`, logrando *Accuracy* $\ge 85\%$ y *Recall* en clase crítica (Estrés Peligroso) $\ge 90\%$.
- [ ] **Demostración de Ahorro Cuantificable:** La interfaz evidencia analíticamente un ahorro de agua $\ge 35\%$ por gestión de software ($>75\%$ combinado con caudal eficiente) y de energía eléctrica $\ge 40\%$ comparado con el modelo tradicional continuo de 8 horas (10:00 a 18:00 hs).
- [ ] **Operación Ligera en Linux (Python 3.10–3.12 Estable):** Ejecutable 100% desde consola Linux (Konsole) y editable limpiamente en Kate sin dependencias rotas ni bloqueos de compilación.

---

## 9. Especificación y Guion del Video Pitch (AgroChallenge 2026)

Para el proceso de selección y evaluación del jurado de Nestlé Conecta, el video constituye la pieza audiovisual central de evaluación.

### 9.1 Parámetros de Producción Audiovisual
* **Duración Estricta:** 3 minutos (180 segundos máximo).
* **Resolución:** Full HD 1080p (1920x1080) a 30/60 fps.
* **Herramientas Recomendadas en Linux:**
  * **Captura de Pantalla (Screencast de la App):** OBS Studio o SimpleScreenRecorder.
  * **Edición de Audio (Limpieza de voz y música suave):** Audacity.
  * **Edición de Video:** Kdenlive o CapCut.

---

## 10. Blindaje Técnico Anti-Bloqueos (Garantía de Cero Fallas en Desarrollo)

Para evitar que el desarrollo se frene por problemas de librerías en versiones de Python modernas (recomendado Python 3.10 / 3.12 LTS estable en Linux), congelamiento de ventanas, falta de datos iniciales o fallas de internet durante la demo, se definen los siguientes 6 pilares de blindaje técnico:

### 10.1 Dependencias Compatibles con Python 3.10–3.12 (Estable) en `requirements.txt`
Se utilizan cotas mínimas (`>=`) compatibles con los *wheels* binarios precompilados oficiales en Linux (evitando fallos de compilación de Cython/Meson de versiones antiguas):
```text
# Núcleo Científico y Modelado (Python 3.10 / 3.12 LTS Estable)
numpy>=2.1.0
pandas>=2.2.3
scikit-learn>=1.5.2
joblib>=1.4.2

# Ingesta Climática y Red
requests>=2.32.3
python-dotenv>=1.0.1

# Interfaz Nativa de Escritorio (Qt6)
PyQt6>=6.7.1
matplotlib>=3.9.2

# Canal Móvil, QR y Reportes PDF
python-telegram-bot>=21.6
fpdf2>=2.8.1
qrcode[pil]>=8.0

# Hardware IoT y Simulación
pyserial>=3.5

# Calidad y Testing
pytest>=8.3.3
pytest-mock>=3.14.0
```

> **Tip para Linux:** En distribuciones basadas en Ubuntu/Debian/Fedora, PyQt6 requiere soporte multimedia y X11/Wayland estándar. Si al correr la GUI falta alguna biblioteca gráfica del sistema, se resuelve con:
> `sudo apt install libgl1-mesa-glx libegl1 libxkbcommon-x11-0 libdbus-1-3` (o `sudo dnf install mesa-libGL libxkbcommon-x11` en Fedora/RHEL).

---

### 10.2 Plantilla Definitiva de Variables de Entorno (`.env.example`)
El archivo `.env.example` en la raíz del proyecto debe incluir todos los parámetros configurables:
```bash
# =======================================================
# CONFIGURACIÓN DEL TAMBO (CASO PILOTO RAFAELA, SANTA FE)
# =======================================================
FARM_NAME="Tambo San José - Nestlé Conecta"
FARM_LATITUDE=-31.25
FARM_LONGITUDE=-61.48
DEFAULT_COW_COUNT=100
MILK_PRICE_ARS_PER_LITER=430.0

# =======================================================
# PROVEEDOR METEOROLÓGICO
# Opciones: open_meteo | mock | open_weather
# =======================================================
WEATHER_PROVIDER="open_meteo"
OPENWEATHER_API_KEY="" # Opcional: solo si se cambia a open_weather

# =======================================================
# CANAL MÓVIL (BOT DE TELEGRAM)
# =======================================================
TELEGRAM_BOT_TOKEN="" # Si se deja vacío, el sistema opera normalmente en modo Desktop o CLI
TELEGRAM_ADMIN_CHAT_ID=""
TELEGRAM_BOT_USERNAME="AgroStressNestleBot"

# =======================================================
# HARDWARE IOT & MAQUETA FÍSICA
# =======================================================
USE_MOCK_HARDWARE=true # true para usar simulador en memoria; false para placa real
SERIAL_PORT="/dev/ttyUSB0"
SERIAL_BAUDRATE=9600
```

---

### 10.3 Prevención de Congelamiento de la UI y Sincronización Móvil (`QThread`)
* **El Peligro Técnico:** Si una llamada HTTP a Open-Meteo tarda $800\text{ ms}$, el modelo ML procesa datos o el bot de Telegram hace long-polling en el hilo principal de la interfaz, la ventana de PyQt6 en Linux se congela y el sistema operativo reporta *"La aplicación no responde"*.
* **La Solución Arquitectónica:** 
  1. `src/infrastructure/ui/desktop/workers/weather_sync_worker.py` (`QThread`): Ejecuta la ingesta meteorológica y las predicciones horarias en segundo plano, emitiendo `weather_synced = pyqtSignal(object)`.
  2. `src/infrastructure/ui/desktop/workers/telegram_bot_worker.py` (`QThread`): Ejecuta el listener de comandos de Telegram en un hilo dedicado compartiendo la misma instancia de casos de uso y repositorio en memoria, emitiendo `sector_state_changed = pyqtSignal()` cada vez que un usuario ejecuta `/ocupar`.
  * La interfaz gráfica (`MainWindow`) se conecta a ambas señales y refresca los widgets a 60 fps sin trabas ni latencias.

---

### 10.4 Perfiles de Demostración Offline para el Jurado (Demo Presets)
¿Qué ocurre si el día del pitch ante Nestlé se corta el WiFi del recinto, o la temperatura exterior en Rafaela es de 18°C y el sistema no activa nada por estar en confort?
Para asegurar una demo impecable ante cualquier circunstancia, el sistema cuenta con **3 escenarios climáticos preconfigurados en `MockWeatherAdapter`**:
1. **Perfil `heatwave` (Ola de Calor Extrema):** $T = 34.5\text{°C}$, $HR = 68\%$, $\text{Rad} = 820\text{ W/m}^2 \rightarrow \text{ITH} = 85.2$ [PELIGRO CRÍTICO]. Dispara aspersión en sectores de hormigón, solo ventilación en cama de compost y alertas inmediatas.
2. **Perfil `nocturnal_debt` (Noche Tropical con Deuda Térmica):** Noche previa con $\text{ITH} = 73.0$ ($0\text{ hs}$ frescas). Demuestra la reducción automática del umbral diurno en $3.0\text{ puntos}$ por inercia térmica acumulada.
3. **Perfil `temperate` (Confort):** $T = 20.0\text{°C}$, $HR = 45\% \rightarrow \text{ITH} = 64.0$. Demuestra que el sistema apaga 100% de los equipos y ahorra recursos.
* Se activan con un botón en la app de escritorio o pasando la bandera de terminal: `python src/main.py --desktop --demo-heatwave`.

---

### 10.5 Datos Semilla Iniciales (`src/domain/fixtures/default_farm.py`)
Para que al clonar el repositorio y correr la app por primera vez la pantalla no aparezca en blanco o con errores de sectores nulos, `src/domain/fixtures/default_farm.py` precarga los 3 sectores de referencia con sus parámetros físicos y sanitarios:
1. **Sector 1 (`corral_espera`):** *Corral de Espera Pre-ordeñe* (Capacidad: 80 vacas, Ocupación: `True`, Umbrales: `72.0/78.0`, Piso hormigón: `allows_water_sprinkling=True`, `sprinkler_count=10`, `fan_count=4`).
2. **Sector 2 (`comederos`):** *Línea de Comederos y Pista de Alimentación* (Capacidad: 120 vacas, Ocupación: `True`, Umbrales: `72.0/78.0`, Piso hormigón: `allows_water_sprinkling=True`, `sprinkler_count=15`, `fan_count=6`).
3. **Sector 3 (`sombras`):** *Galpón Compost Barn / Sombras y Descanso* (Capacidad: 100 vacas, Ocupación: `True`, Umbrales: `70.0/76.0` - lote alta producción, Cama orgánica: `allows_water_sprinkling=False`, `sprinkler_count=0`, `fan_count=4`).

---

### 10.6 Estructura del Composition Root (`src/main.py`)
`main.py` actúa como el único punto donde se resuelve la Inversión de Dependencias, inyectando las mismas instancias de repositorio y casos de uso tanto en la GUI de escritorio como en el worker del Bot de Telegram:
```python
"""
Punto de Entrada Principal (Composition Root)
AgroChallenge 2026 - Nestlé Conecta
"""
import argparse
from dotenv import load_dotenv

def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="AgroChallenge 2026 - Sistema Predictivo de Estrés Térmico")
    parser.add_argument("--desktop", action="store_true", help="Iniciar App Nativa de Escritorio (PyQt6 + Bot Worker)")
    parser.add_argument("--bot", action="store_true", help="Iniciar Bot de Telegram en modo standalone (headless)")
    parser.add_argument("--cli", action="store_true", help="Iniciar Interfaz de Consola Interactiva")
    parser.add_argument("--demo-heatwave", action="store_true", help="Forzar perfil simulado de ola de calor")
    parser.add_argument("--benchmark", action="store_true", help="Ejecutar simulación analítica de ahorro de 24h")

    args = parser.parse_args()

    # 1. Instanciación única (Singleton en proceso) de Repositorios y Adaptadores según flags y .env
    # 2. Instanciación de Casos de Uso compartidos (Predict, Savings, ToggleOccupancy, Status, Report)
    # 3. Inyección en Controladores/ViewModels (`src/adapters/`) y Drivers UI (`src/infrastructure/ui/`)

    if args.bot:
        from src.infrastructure.ui.telegram_bot.bot_service import run_bot
        run_bot(force_heatwave=args.demo_heatwave)
    elif args.cli or args.benchmark:
        from src.infrastructure.ui.cli.console_runner import run_cli
        run_cli(benchmark_mode=args.benchmark, force_heatwave=args.demo_heatwave)
    else:
        # Por defecto inicia la Estación Base de Escritorio (con TelegramBotWorker sincronizado si hay token)
        from src.infrastructure.ui.desktop.app import run_desktop_app
        run_desktop_app(force_heatwave=args.demo_heatwave)

if __name__ == "__main__":
    main()
```

---

## 11. Referencias Científicas y Bibliografía de Soporte

1. **Oliveira, C. P., Sousa, F. C. d., Silva, A. L. d., Schultz, É. B., Valderrama Londoño, R. I., & Souza, P. A. R. d. (2025).** *Heat Stress in Dairy Cows: Impacts, Identification, and Mitigation Strategies—A Review*. Animals, 15(2), 249. https://doi.org/10.3390/ani15020249
2. **Chen, J. M., Schütz, K. E., & Tucker, C. B. (2016).** *Cooling cows in the feeding alley: Different sprinkler flow rates*. Journal of Dairy Science, 99(8), 6470-6481. (Demostración de que 1.3 L/min enfría idénticamente a 4.9 L/min ahorrando 73.5% de agua).
3. **Pacheco, P. R. V., et al. (2020).** *Machine learning models applied to the identification of heat stress in Holstein cows*. Computers and Electronics in Agriculture, 178, 105760. (Precisión del 84% de modelos ML frente al 68% del THI estático).
4. **Becker, C. A., et al. (2021).** *Evaluation of heat stress in dairy cows using machine learning algorithms*. Biosystems Engineering, 208, 105-115. (Superioridad de Random Forest en vacas con sistema de aspersores).
5. **Garner, J. B., et al. (2017).** *Genomic selection for heat tolerance in dairy cattle: Heat stress causes acute milk production drops in climate chambers*. Journal of Dairy Science, 100(8), 6331-6342.
6. **Rejeb, M., et al. (2016).** *Impact of heat stress on milk yield and physiological parameters of dairy cows*. International Journal of Biometeorology, 60(8), 1269-1277.
7. **Taverna, M., et al. (2018).** *Pautas técnicas para el manejo del estrés calórico en rodeos lecheros*. INTA EEA Rafaela, Publicación Miscelánea.
8. **Thom, E. C. (1959).** *The discomfort index*. Weatherwise, 12, 57-60. / NRC (1971). *A Guide to Environmental Research on Animals*.

