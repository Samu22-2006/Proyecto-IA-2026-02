# Crédito · Sistema experto e inferencia difusa

Aplicación Streamlit en español para explorar un proyecto académico de evaluación crediticia. Reúne el sistema experto inicial, las mejoras del Sprint 3 y una extensión de lógica difusa explicable.

## Ejecutar

Requiere Python 3.12 (versión validada).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

No necesita API keys, servicios externos ni base de datos. Usa expedientes ficticios. Las solicitudes permanecen en la sesión de Streamlit y sólo se exportan cuando el usuario descarga el JSON.

## Validar

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Las pruebas cubren amortización, umbrales del motor, partición y cobertura difusa, continuidad, controles explícitos, optimización y navegación con Streamlit AppTest. Los archivos originales se incluyen íntegros en `documentos/`.

## Publicar en Streamlit Community Cloud

GitHub almacena el código; para ejecutar una app Streamlit hace falta un servicio de alojamiento.

1. En https://share.streamlit.io/ inicia sesión con la cuenta de GitHub autorizada.
2. Selecciona **Create app** y el repositorio `Samu22-2006/Proyecto-IA-2026-02`.
3. Selecciona la rama `main` y el archivo de entrada `app.py`.
4. En opciones avanzadas selecciona Python 3.12. No se requieren secretos.
5. Despliega y comprueba «Evaluar solicitud» con los valores predeterminados.

El despliegue web requiere autorización de la cuenta de Streamlit; subir el código a GitHub por sí solo no crea una URL pública de la aplicación.

## Organización y trazabilidad

- `app.py`: proyecto, evaluador común, conocimiento, explicación difusa, documentos y apoyo de IA.
- `motor_original.py`: funciones extraídas del notebook `Sprint 3.ipynb`, sin entrada interactiva ni gráficos de Matplotlib. Conserva reglas y fitness originales.
- `credito.py`: validación y nuevo modelo difuso Sugeno de orden cero.
- `documentos/`: los dos HTML y los dos notebooks aportados, sin modificación.
- `tests/`: pruebas del dominio y de la interfaz.

Los adjuntos sólo identifican explícitamente el Sprint 3. La organización «Sprint 1: conocimiento; Sprint 2: inferencia; Sprint 3: optimización» se infiere del recorrido del sistema experto inicial. No se afirma que existan entregas independientes de los dos primeros sprints. Debe contrastarse con la documentación original del curso.

## Decisión difusa y rigidez

Sugeno de orden cero facilita exponer cada regla y obtener un índice continuo mediante un promedio ponderado, sin discretizar una salida como en Mamdani. No requiere un conjunto de entrenamiento inexistente en las entregas.

Se usan particiones lineales con hombros y tres centros: score (500, 650, 800), deuda (30, 50, 70 %) y cuota/ingreso (15, 30, 45 %). Las 27 combinaciones cubren todo el dominio. AND es el producto de pertenencias. Cualquier condición desfavorable tiene consecuente 15; las tres favorables, 85; las restantes, 50. El índice final es Σ(w·z)/Σ(w). Menos de 35 recomienda rechazo, de 35 a menos de 70 revisión, y desde 70 aprobación orientativa.

Estos parámetros y controles son una propuesta académica nueva, no se encuentran en los adjuntos ni están calibrados con datos reales. La salida categórica conserva umbrales; lo que se suaviza es el índice y la participación de las reglas. Dos reportes negativos mantienen rechazo; un reporte, edad fuera de 18–65 o empleo inferior a un año impiden aprobación automática. El índice no es una probabilidad de incumplimiento.

Se conserva el motor rígido para comparar. Sus criterios por edad y el uso de N/A como condición aprobable se muestran de manera explícita. La cuota excluye seguros, comisiones y otros cargos. El endeudamiento declarado y la carga de la nueva cuota se evalúan por separado, según los adjuntos.

## Estrategia evolutiva

Sólo se ejecuta si el motor original con intereses devuelve REVISIÓN. Usa μ=6, λ=12, 50 generaciones y semilla configurable. Busca montos entre el 70 y 100 % del original y plazos en meses entre el solicitado y 240. La selección conserva padres y descendientes, de modo que el mejor fitness no decrece.

Fitness = 0.50 × capacidad + 0.25 × cercanía de monto + 0.25 × cercanía de plazo − penalización por no aprobación. Las utilidades del cliente y del prestamista se muestran por separado: no son los objetivos directos del fitness, pese a la descripción general del prototipo HTML. No se garantiza óptimo global ni encontrar aprobación. Si el score, los reportes o la deuda bloquean, cambiar monto y plazo no lo resuelve.

## Apoyo de IA

El autor confirmó el uso de **ChatGPT** en los sprints originales, sin detallar tareas concretas. En esta integración se utilizó **ChatGPT / Codex** para analizar entregas, implementar y documentar la interfaz, proponer el modelo difuso y preparar pruebas. No se atribuyen otras herramientas sin confirmación.

Proyecto educativo: necesita revisión por expertos, calibración y evaluación de sesgos antes de considerar cualquier uso financiero real.

## GitHub Pages · Python en el navegador

La versión de Pages usa **Stlite 0.85.1 / Pyodide**: ejecuta Streamlit y los mismos módulos Python en el navegador, sin servidor Python. `scripts/build_pages.py` empaqueta las fuentes y los cuatro documentos en `docs/app-bundle.json`. No contiene secretos. Los originales siguen disponibles para descargar dentro de la app.

El workflow `.github/workflows/pages.yml` genera el paquete y lo publica mediante GitHub Actions con cada cambio en `main`. En **Settings → Pages → Build and deployment → Source** debe estar seleccionado **GitHub Actions**. Esa activación necesita permisos de administración del repositorio. La URL prevista, una vez publicado correctamente, es `https://samu22-2006.github.io/Proyecto-IA-2026-02/`.

También se puede publicar sin Actions seleccionando **Deploy from a branch → main → /docs**, dado que el bundle está incluido en el repositorio. En ese modo hay que ejecutar `python scripts/build_pages.py` después de modificar la aplicación y subir el resultado.

La primera carga descarga el runtime Python/WebAssembly y puede tardar. Se requiere un navegador moderno con JavaScript y acceso a los CDN usados por Stlite. Esta variante depende del Streamlit incluido con Stlite, mientras que la ejecución tradicional usa la versión de `requirements.txt`.
