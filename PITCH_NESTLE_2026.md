# Pitch Nestlé Conecta — AgroChallenge 2026 (Guion 3 Minutos / 180s)

**Proyecto:** AgroPredictTambo — Predicción Bioclimática y Sectorización Anti-Mastitis para Tambos Inteligentes  
**Establecimiento de Referencia:** Tambo San José — Rafaela, Santa Fe (`lat: -31.25`, `lon: -61.48`, `100` vacas en Benchmark)  
**Duración Total:** `03:00` (`180` segundos estrictos)

---

## 0. Parámetros Audiovisuales de Producción (Sección 9 de `spec.md`)

- **Duración máxima estricta:** `3:00 min` (`180` segundos).
- **Resolución y tasa de cuadros:** Full HD `1080p` (`1920x1080`) a `30` o `60 fps`.
- **Herramientas recomendadas en Linux:**
  - **Captura de pantalla (Screencast CLI / Desktop SCADA / Bot):** `OBS Studio` o `SimpleScreenRecorder`.
  - **Edición y limpieza de audio (locución + música de fondo suave):** `Audacity`.
  - **Edición y montaje final de video:** `Kdenlive` o `CapCut`.

---

## Tabla de Tiempos del Pitch (180s)

| Acto | Ventana | Duración | Foco Visual en Pantalla | Mensaje Clave al Jurado |
| :--- | :---: | :---: | :--- | :--- |
| **Acto 1** | `0:00 – 0:35` | `35s` | Mapa de Rafaela + curva ITH / ola de calor | Dolor productivo por estrés calórico e inercia nocturna |
| **Acto 2** | `0:35 – 1:25` | `50s` | Diagrama RF sin leakage + 3 sectores SCADA | Innovación sanitaria (Anti-Mastitis) y resiliencia offline |
| **Acto 3** | `1:25 – 2:15` | `50s` | Salida auditada `--cli --benchmark` + tabla ESG | Ahorros reales: `56.25%` / `88.39%` agua, `48.53 kWh`, `$34.400 ARS/día` |
| **Acto 4** | `2:15 – 3:00` | `45s` | Demo en vivo: CLI, Bot + QR, Desktop SCADA + PDF | 3 niveles de MVP sincronizados (`< 100 ms`) y PDF auditado |

---

## Acto 1 — Gancho y Problema (`0:00 – 0:35`, 35s)

- **Visual en pantalla:** Toma inicial del escenario de ola de calor en la cuenca lechera de **Rafaela (Santa Fe)** y panel de condiciones críticas (`34.5 °C`, `68% HR`, `ITH 87.75`).
- **Locución:**
  > "En la cuenca lechera de Rafaela, Santa Fe, una sola ola de calor reduce drásticamente la producción de leche y compromete el bienestar animal. El problema no termina cuando baja el sol: si el ganado no logra disipar calor durante la noche, acumula **inercia térmica y deuda nocturna** —como en nuestro escenario de referencia con **ITH actual de 87.75** y **6 horas de deuda nocturna** acumuladas al amanecer (`3.0 pts` de penalización)—, haciendo que los tambos enciendan aspersores con temporizadores fijos de 8 horas continuas (`10:00 a 18:00 hs`), desperdiciando miles de litros de agua, energía eléctrica y mojando camas orgánicas donde nace la mastitis."

---

## Acto 2 — Innovación Sanitaria y Algorítmica (`0:35 – 1:25`, 50s)

- **Visual en pantalla:** Esquema de los 4 anillos de Clean Architecture, vector de 8 features sin `thi_calculated`, y tarjetas de los 3 sectores (`corral_espera`, `comederos`, `sombras`).
- **Locución:**
  > "**AgroPredictTambo** reemplaza los temporizadores ciegos por control predictivo basado en ciencia y sanidad animal:
  > 1. **Modelo Random Forest sin *data leakage*:** Nuestro clasificador (`heat_stress_classifier.joblib`) predice el nivel de estrés con 8 variables físicas y temporales —incluyendo depresión de bulbo húmedo, media móvil ITH de 3 horas y deuda térmica nocturna (Oliveira et al., 2025)— con **0% de uso de `thi_calculated`** en la matriz de entrenamiento. En validación temporal alcanzó **95.83% de accuracy** y **100% de recall en clase crítica (Estrés Peligroso)**.
  > 2. **Sectorización Predictiva y Regla Anti-Mastitis estricta:** En pisos de hormigón (`corral_espera` y `comederos`), activa micro-ciclos evaporativos de **40s de aspersión (1.3 L/min) + 270s de ventilación**. En cambio, en el **Galpón Compost Barn (`sombras`, `allows_water_sprinkling=False`)**, aplica **0% de agua y 270s de solo ventilación** incluso en Nivel 2, protegiendo la cama orgánica contra mastitis. Si un sector está desocupado (`current_occupancy=False`), se apaga automáticamente.
  > 3. **Resiliencia Rural Offline:** Sin conectividad en el campo, conmuta automáticamente a caché local (`SqliteWeatherCacheAdapter`) y respaldo heurístico (`HeuristicPredictorAdapter`) sin interrumpir la operación."

---

## Acto 3 — Resultados Auditados de Benchmark 24h (`1:25 – 2:15`, 50s)

- **Visual en pantalla:** Terminal ejecutando `./venv/bin/python src/main.py --cli --benchmark` y tabla comparativa frente al esquema tradicional continuo de 8 horas (`baseline: 8.0h` vs `predictivo: 3.5h`, `100` vacas, `25` aspersores, `14` ventiladores).
- **Locución:**
  > "Contrastando el esquema tradicional continuo de 8 horas frente a nuestra operación predictiva de 3.5 horas activas, estos son los resultados auditados del benchmark:"

| Indicador ESG / Productivo | Base Tradicional (8h) | Modelo Predictivo (3.5h) | Impacto Auditado | Meta `spec.md` |
| :--- | :---: | :---: | :---: | :---: |
| **Agua por software (1.3 L/min)** | `2012.90 L` | `880.65 L` | **`1132.26 L` ahorrados (`56.25%`)** | `>= 35%` |
| **Ahorro hidráulico combinado (vs 4.9 L/min, Chen et al. 2016)** | `7587.10 L` | `880.65 L` | **`88.39%` de ahorro hídrico total** | `>= 75%` |
| **Energía eléctrica** | `86.27 kWh` | `37.74 kWh` | **`48.53 kWh` ahorrados (`56.25%`)** | `>= 40%` |
| **Huella de carbono evitada (CAMMESA `0.35 kg CO2e/kWh`)** | — | — | **`16.99 kg CO2e/día` evitados** | Neutro CO2 |
| **Leche protegida (SIGLeA, `$430.00 ARS/L`)** | — | — | **`80.00 L/día` = `$34400.00 ARS/día`** | Defensa lactancia |

- **Cierre de locución del Acto 3:**
  > "Esto representa un ahorro del **56.25% de agua por software** —y **88.39% combinado** frente a boquillas tradicionales de 4.9 L/min—, **56.25% de ahorro eléctrico**, **16.99 kg de CO2e evitados por día** según factor CAMMESA, y **80 litros diarios de leche protegidos** equivalentes a **$34.400 ARS/día** en un tambo tipo de 100 vacas."

---

## Acto 4 — Demo en Vivo Multi-Interfaz (`2:15 – 3:00`, 45s)

- **Visual en pantalla:** Ejecución en vivo de los 3 niveles de MVP sobre un mismo núcleo de dominio desacoplado (`Clean Architecture` en 4 anillos).

1. **MVP Nivel 1 — CLI & Benchmark Auditado (`10s`):**
   ```bash
   ./venv/bin/python src/main.py --cli --benchmark
   ```
   - Muestra el estado operativo de los 3 sectores, la predicción (`Actual: 34.5C | HR 68% | ITH 87.75`, `Proyectado: 25.5C | HR 78% | ITH 75.49 | Deuda Nocturna: 6h`) y el balance ESG completo.

2. **MVP Nivel 2 — Bot de Telegram & Acceso por QR (`15s`):**
   ```bash
   ./venv/bin/python src/main.py --bot
   ```
   - Mostrar el código QR generado en `data/cache/bot_qr.png` y ejecutar desde el celular `/estado`, `/ahorro` y `/ocupar sombras false`.

3. **MVP Nivel 3 — Estación Desktop SCADA + Sync en Tiempo Real + PDF (`20s`):**
   ```bash
   ./venv/bin/python src/main.py --desktop --demo-heatwave
   ```
   - Demostrar la sincronización en `< 100 ms` al enviar `/ocupar corral_espera false` desde Telegram y ver el apagado instantáneo en la tarjeta SCADA.
   - Exportar el reporte PDF auditado para Nestlé Conecta (`data/cache/reporte_sustentabilidad_nestle.pdf`).

- **Frase de cierre (`2:50 – 3:00`):**
  > "**AgroPredictTambo**: menos agua, menos energía, cero mastitis por exceso de humedad y más leche protegida para una lechería sustentable junto a Nestlé Conecta."
