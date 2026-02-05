# Estado del Proyecto - Gestión de Torneo de Fútbol

**Fecha de última actualización:** 5 de febrero de 2026  
**Versión:** 1.0.0

---

## 📊 Resumen Ejecutivo

| Categoría | Estado | Porcentaje Completado |
|-----------|--------|----------------------|
| **Funcionalidades Básicas** | 🟡 CASI COMPLETO | 95% (6.5/7) |
| **Requisitos Técnicos** | 🟡 EN PROGRESO | 85% |
| **Entregables** | 🔴 PENDIENTE | 40% |
| **TOTAL PROYECTO** | 🟡 EN PROGRESO | **73%** |

---

## 📋 Checklist Detallado de Requisitos

### 1️⃣ FUNCIONALIDADES BÁSICAS (95% 🟡)

#### 1.1 Gestión de Equipos
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Crear equipos (nombre, curso, color, emblema) | ✅ HECHO | Implementado con subida de imágenes |
| ✅ Listar equipos registrados | ✅ HECHO | Con tabla filtrable |
| ⚠️ Ver jugadores al pulsar sobre equipo | 🔴 FALTA | **Solo muestra en panel derecho, no lista jugadores** |
| ✅ Editar equipos existentes | ✅ HECHO | Diálogo de edición |
| ✅ Eliminar equipos | ✅ HECHO | Con validaciones |

#### 1.2 Gestión de Participantes
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Registrar participante (nombre, fecha nac., curso) | ✅ HECHO | Formulario completo |
| ✅ Rol: jugador y/o árbitro | ✅ HECHO | Checkboxes independientes |
| ✅ Posición (delantero, defensa, etc.) | ✅ HECHO | ComboBox con posiciones |
| ✅ Tarjetas amarillas y rojas | ✅ HECHO | Campos numéricos |
| ✅ Goles | ✅ HECHO | Campo numérico |
| ✅ Asignar jugador a equipo | ✅ HECHO | Sistema de convocatorias |
| ✅ Asignar árbitro a partido | ✅ HECHO | ComboBox en diálogo partido |
| ✅ Listar, editar y eliminar participantes | ✅ HECHO | CRUD completo |
| ✅ Clasificar por tarjetas o goles | ✅ HECHO | Filtros en tabla |

#### 1.3 Gestión del Calendario
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Programar partidos | ✅ HECHO | Diálogo completo |
| ✅ Equipos participantes | ✅ HECHO | ComboBox local/visitante |
| ✅ Fecha y hora | ✅ HECHO | DateTimeEdit |
| ✅ Árbitro asignado | ✅ HECHO | ComboBox de árbitros |
| ✅ Eliminatoria (octavos mínimo) | ✅ HECHO | Octavos, cuartos, semi, final |
| ✅ Listar partidos por fechas y eliminatoria | ✅ HECHO | Tabla con filtros |
| ✅ Editar partidos | ✅ HECHO | Diálogo de edición |
| ✅ Eliminar partidos | ✅ HECHO | Con confirmación |

#### 1.4 Actualización de Resultados
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Registrar goles de cada equipo | ✅ HECHO | SpinBox en diálogo |
| ✅ Actualizar clasificación automáticamente | ✅ HECHO | Ganador determinado auto |
| ✅ Registrar goles de jugadores | ✅ HECHO | Diálogo detalle de goles |
| ✅ Registrar tarjetas a jugadores | ✅ HECHO | En stats del partido |
| ✅ Listar partidos jugados con resultado | ✅ HECHO | Filtro por estado |

#### 1.5 Clasificación/Gestión de Eliminatorias
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Generar rondas automáticamente | ✅ HECHO | Avance de ganadores |
| ✅ Cuartos, semifinales, final según resultados | ✅ HECHO | Lógica de propagación |
| ✅ Mostrar cuadro de emparejamiento | ✅ HECHO | Widget visual de bracket |

#### 1.6 Créditos
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Pantalla de créditos | ✅ HECHO | Autor, versión, fecha |

#### 1.7 Ayuda
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Ventana con ayuda mínima | ✅ HECHO | Instrucciones básicas |

---

### 2️⃣ REQUISITOS TÉCNICOS (85% 🟡)

#### 2.1 Interfaz Gráfica
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Usar Qt Designer para diseñar ventanas | ✅ HECHO | Archivos .ui de referencia |
| ✅ Cargar diseños con PySide6 | ✅ HECHO | Implementado en Python |

#### 2.2 Base de Datos
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Implementar SQLite | ✅ HECHO | `torneo.db` |
| ✅ Tablas creadas | ✅ HECHO | 6 tablas principales |
| ✅ Relaciones entre tablas | ✅ HECHO | Claves foráneas |
| ✅ Base de datos documentada | ✅ HECHO | `schema.py` con estructura |

#### 2.3 Código Limpio
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Separar control y gestión de DB | ✅ HECHO | Arquitectura MVC |
| ✅ Independizar vistas de control/datos | ✅ HECHO | Separación clara |
| ✅ Documentar código | ✅ HECHO | Docstrings en clases/métodos |
| ✅ Buenas prácticas de programación | ✅ HECHO | PEP 8, type hints |

#### 2.4 Estilo Visual y Empaquetado
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Personalizar con QSS | ✅ HECHO | Temas light y dark |
| ⚠️ Añadir iconos en botones | 🟡 PARCIAL | Pocos iconos, ampliar |
| ✅ Añadir imágenes en ventanas | ✅ HECHO | Fondo de césped |
| ✅ Tooltips | ✅ HECHO | En elementos clave |
| ❌ PyInstaller para Windows | ❌ PENDIENTE | **CRÍTICO** |
| ❌ Paquete .deb para GNU/Linux | ❌ PENDIENTE | Opcional |
| ❌ Módulo DB como librería instalable | ❌ PENDIENTE | No incluir en proyecto |

---

### 3️⃣ ENTREGABLES (40% 🔴)

#### 3.1 Código Fuente
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ✅ Views con archivos .ui y .py | ✅ HECHO | Carpeta `views/` |
| ✅ Controllers con lógica | ✅ HECHO | Carpeta `controllers/` |
| ✅ Models (DB, clases de tablas) | ✅ HECHO | Carpeta `models/` |
| ✅ Resources (img, iconos, qss) | ✅ HECHO | Carpeta `resources/` |
| ✅ Organización en carpetas | ✅ HECHO | Estructura MVC completa |

#### 3.2 Manual de Usuario
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ⚠️ Manual en formato PDF | 🔴 PENDIENTE | Existe en Markdown |
| ✅ Info sobre base de datos | ✅ HECHO | En `GUIA_USUARIO.md` |
| ✅ Info sobre librerías propias | ✅ HECHO | En documentación |
| ❌ Convertir a PDF | ❌ PENDIENTE | **IMPORTANTE** |

#### 3.3 Informe Técnico
| Requisito | Estado | Notas |
|-----------|--------|-------|
| ❌ Informe técnico en PDF | ❌ PENDIENTE | **IMPORTANTE** |
| ❌ Explicar estructura del proyecto | ❌ PENDIENTE | Arquitectura MVC |
| ❌ Decisiones tomadas en desarrollo | ❌ PENDIENTE | Justificar elecciones |

---

### 4️⃣ OPCIONAL (Valoración a la alza)

| Funcionalidad | Estado | Notas |
|---------------|--------|-------|
| ❌ Exportación a CSV | ❌ NO HECHO | Clasificación/resultados |
| ✅ Notificaciones/alertas | ✅ HECHO | Validaciones y confirmaciones |

---

---

## 1. Funcionalidades Básicas (95% 🟡)

⚠️ **FALTA:** Mostrar lista de jugadores al seleccionar un equipo en la tabla.

Ver sección de Checklist Detallado arriba para desglose completo de cada funcionalidad.

### 1.5. Clasificación/Gestión de Eliminatorias ✅
- [x] **Generar rondas automáticamente** según resultados
- [x] **Mostrar cuadro de eliminatorias** visual
- [x] **Emparejamientos automáticos** correctos:
  - Octavos 1 vs 3 → Cuartos 1
  - Octavos 5 vs 7 → Cuartos 2
  - Octavos 2 vs 4 → Cuartos 3
  - Octavos 6 vs 8 → Cuartos 4
- [x] **Avance automático** de ganadores a siguiente ronda
- [x] **Visualización de ganadores parciales** (aunque el partido hermano no se haya jugado)
- [x] **Bracket visual interactivo** con 8 columnas (izquierda y derecha)

**Archivos principales:**
- `app/views/page_bracket.py`
- `app/controllers/bracket_controller.py`
- `app/services/tournament_service.py`

---

### 1.6. Créditos ✅
- [x] **Pantalla de créditos** con:
  - Autor
  - Versión
  - Fecha de actualización
  - Información del proyecto

**Archivo:** `app/views/page_credits.py`

---

### 1.7. Ayuda ✅
- [x] **Ventana de ayuda** con instrucciones mínimas
- [x] **Tooltips** en elementos clave de la UI

**Archivo:** `app/views/page_help.py`

---

## 2. Requisitos Técnicos (85% 🟡)

### 2.1. Interfaz Gráfica ✅
- [x] **Qt Designer** - Archivos .ui de referencia creados
- [x] **PySide6** para interfaces (implementación en código Python)
- [x] **Diseño responsive** adaptado a diferentes tamaños
- [x] **Navegación** por pestañas/páginas
- [x] **Diálogos modales** para operaciones CRUD

**Archivos .ui incluidos:** `app/views/ui/`
- `main_window.ui`, `page_teams.ui`, `page_participants.ui`, `page_matches.ui`
- `dialog_equipo.ui`, `dialog_participante.ui`, `dialog_partido.ui`

**Nota:** Los archivos .ui son de referencia. La aplicación usa código Python directo para mejor control y mantenimiento.

---

### 2.2. Base de Datos ✅
- [x] **SQLite** implementado
- [x] **Tablas creadas:**
  - `equipos` (id, nombre, curso, color_camiseta, logo_path)
  - `participantes` (id, nombre, apellidos, fecha_nacimiento, curso, es_jugador, es_arbitro, posicion, goles, tarjetas_amarillas, tarjetas_rojas)
  - `convocatorias` (id, partido_id, equipo_id, participante_id, es_titular)
  - `partidos` (id, eliminatoria, slot, fecha_hora, equipo_local_id, equipo_visitante_id, arbitro_id, goles_local, goles_visitante, penaltis_local, penaltis_visitante, ganador_equipo_id, estado)
  - `goles` (id, partido_id, equipo_id, participante_id, minuto, tipo)
  - `stats_partido` (id, partido_id, participante_id, equipo_id, tarjetas_amarillas, tarjetas_rojas)
- [x] **Relaciones** entre tablas con claves foráneas
- [x] **Restricciones** de integridad referencial
- [x] **Esquema documentado** en `app/models/schema.py`

**Archivos principales:**
- `app/models/db.py` - Gestor de conexiones
- `app/models/schema.py` - Definición del esquema
- `data/torneo.db` - Base de datos SQLite

---

### 2.3. Código Limpio ✅
- [x] **Arquitectura MVC:**
  - `models/` - Lógica de datos
  - `views/` - Interfaces de usuario
  - `controllers/` - Lógica de control
- [x] **Separación de responsabilidades**
- [x] **Docstrings** en funciones y clases
- [x] **Type hints** en parámetros
- [x] **Nomenclatura** descriptiva
- [x] **Modularización** adecuada

---

### 2.4. Estilo Visual y Empaquetado 🟡
- [x] **QSS (Hojas de estilo Qt):**
  - Tema claro (`light.qss`)
  - Tema oscuro (`dark.qss`)
  - Cambio dinámico de tema
- [x] **Iconos** en botones (⚠️ LIMITADO: pocos iconos, usar más)
- [x] **Imágenes** en ventanas (fondo de césped)
- [x] **Tooltips** básicos
- [ ] **PyInstaller** para empaquetado Windows ❌ PENDIENTE
- [ ] **Paquete .deb** para GNU/Linux ❌ PENDIENTE
- [ ] **Librería local instalable** para DB ❌ PENDIENTE

**Estado:** Estilos completos, falta empaquetado

---

## 3. Entregables (40% 🔴)

### 3.1. Código Fuente ✅
- [x] **Organización en carpetas:**
  ```
  torneo_futbol/
  ├── app/
  │   ├── views/         # Vistas en Python
  │   │   ├── ui/        # ✅ Archivos .ui de Qt Designer (referencia)
  │   │   ├── dialogs/   # Diálogos en Python
  │   │   └── widgets/   # Widgets personalizados
  │   ├── controllers/   # Controladores
  │   ├── models/        # Modelos y acceso a DB
  │   ├── services/      # Lógica de negocio
  │   ├── utils/         # Utilidades
  │   └── resources/     # Recursos
  │       ├── img/       # Imágenes
  │       ├── fonts/     # Fuentes
  │       └── styles/    # QSS
  ├── data/              # Base de datos
  ├── scripts/           # Scripts auxiliares
  └── main.py            # Punto de entrada
  ```

---

### 3.2. Manual de Usuario 🔴
- [ ] **Manual en PDF** ❌ PENDIENTE
- [x] **Guía básica** en `GUIA_USUARIO.md` ✅ (formato Markdown, falta PDF)

**Contenido requerido:**
- Instalación
- Uso de funcionalidades
- Información sobre base de datos
- Librerías propias a instalar

---

### 3.3. Informe Técnico 🔴
- [ ] **Informe en PDF** ❌ PENDIENTE

**Contenido requerido:**
- Estructura del proyecto
- Decisiones técnicas tomadas
- Arquitectura MVC
- Esquema de base de datos
- Tecnologías utilizadas
- Patrones de diseño implementados

---

---

## 5. Criterios de Evaluación - Autoevaluación

| Criterio | Peso | Estado | Nota Estimada | Observaciones |
|----------|------|--------|---------------|---------------|
| **Diseño interfaz gráfica** | 30% | ✅ COMPLETO | 28/30 | Interfaz responsive con temas. Faltan más iconos |
| **Funcionalidades** | 20% | 🟡 CASI COMPLETO | 19/20 | Falta listar jugadores al seleccionar equipo |
| **Base de datos** | 10% | ✅ COMPLETO | 10/10 | SQLite con relaciones correctas |
| **Calidad del código** | 10% | ✅ COMPLETO | 9/10 | MVC, docstrings, limpio |
| **Estilo visual** | 15% | 🟡 PARCIAL | 12/15 | QSS completo. Faltan más iconos |
| **Documentación** | 5% | 🔴 INCOMPLETO | 2/5 | Falta PDF manual e informe |
| **Empaquetado** | 10% | 🔴 NO HECHO | 0/10 | ❌ **CRÍTICO - CERO SIN ESTO** |
| **TOTAL** | 100% | 🟡 EN PROGRESO | **80/100** | **Notable bajo** |

---

## 6. TAREAS PENDIENTES - LO QUE TE FALTA

### 🔴 CRÍTICO - OBLIGATORIO (Sin esto = calificación 0)

| # | Tarea | Peso | Tiempo Estimado | Prioridad |
|---|-------|------|-----------------|-----------|| 0 | **Listar jugadores al seleccionar equipo** | 1% | 2-3 horas | 🔴 MÁXIMA |
| - | Crear tabla/lista en panel derecho | - | 1 hora | - |
| - | Conectar señal de selección de equipo | - | 30 min | - |
| - | Mostrar jugadores del equipo (convocatorias) | - | 1 hora | - |
| - | Probar funcionalidad completa | - | 30 min | - || 1 | **Empaquetar con PyInstaller (.exe Windows)** | 10% | 6-8 horas | 🔴 MÁXIMA |
| - | Configurar PyInstaller con recursos | - | 2 horas | - |
| - | Incluir imágenes, QSS, fuentes en bundle | - | 2 horas | - |
| - | Probar en máquina limpia (sin Python) | - | 2 horas | - |
| - | Corregir errores de empaquetado | - | 2 horas | - |

**⚠️ NOTA IMPORTANTE:** El enunciado dice que sin ejecutable funcional (.exe) la calificación es **0 automáticamente**.

---

### 🟠 IMPORTANTE - NECESARIO (Afecta significativamente la nota)

| # | Tarea | Peso | Tiempo Estimado | Prioridad |
|---|-------|------|-----------------|-----------|
| 2 | **Manual de Usuario en PDF** | 2.5% | 4-5 horas | 🟠 ALTA |
| - | Convertir GUIA_USUARIO.md a PDF | - | 1 hora | - |
| - | Añadir capturas de pantalla | - | 2 horas | - |
| - | Incluir info de instalación y librerías | - | 1 hora | - |
| - | Revisar formato y presentación | - | 1 hora | - |
| 3 | **Informe Técnico en PDF** | 2.5% | 5-6 horas | 🟠 ALTA |
| - | Documentar arquitectura MVC | - | 1.5 horas | - |
| - | Explicar decisiones técnicas | - | 1.5 horas | - |
| - | Crear diagramas de base de datos | - | 1 hora | - |
| - | Crear diagramas de clases | - | 1 hora | - |
| - | Revisar y formatear | - | 1 hora | - |

---

### 🟡 DESEABLE - MEJORARÍA LA NOTA (Pero no crítico)

| # | Tarea | Impacto | Tiempo Estimado | Prioridad |
|---|-------|---------|-----------------|-----------|
| 4 | **Añadir más iconos** | +2-3 puntos | 2-3 horas | 🟡 MEDIA |
| - | Iconos en botones de acciones | Estilo visual | 1 hora | - |
| - | Iconos en pestañas de navegación | Estilo visual | 1 hora | - |
| - | Iconos en menús y diálogos | Estilo visual | 1 hora | - |
| 5 | **Librería DB instalable** | Requisito | 3-4 horas | 🟡 MEDIA |
| - | Crear módulo `torneo_db_utils` | - | 2 horas | - |
| - | Configurar setup.py | - | 1 hora | - |
| - | Documentar instalación | - | 1 hora | - |
| 6 | **Exportar a CSV** (OPCIONAL) | +Bonus | 2 horas | 🟢 BAJA |
| - | Implementar exportación clasificación | - | 1 hora | - |
| - | Implementar exportación resultados | - | 1 hora | - |
| 7 | **Paquete .deb Linux** (OPCIONAL) | Extra | 4-5 horas | 🟢 BAJA |

---

## 7. Plan de Acción Recomendado

### 📅 Semana 1 (5-11 febrero) - CRÍTICO
**Objetivo:** Implementar lista de jugadores y completar el empaquetado

| Día | Actividad | Horas | Resultado Esperado |
|-----|-----------|-------|-------------------|
| **Mié 5** | **Implementar lista jugadores al seleccionar equipo** | 2-3h | ✅ Funcionalidad completa |
| **Jue 6** | Configurar PyInstaller | 3h | Primer .exe generado |
| **Vie 7** | Incluir recursos en bundle | 3h | Recursos accesibles |
| **Sáb 8** | Probar ejecutable en PC limpia | 3h | Ejecutable funcional |
| **Dom 9** | Corregir errores de empaquetado | 3h | Ejecutable estable |
| **Lun 10** | Pruebas finales del .exe | 2h | ✅ Empaquetado completo |

### 📅 Semana 2 (12-18 febrero) - DOCUMENTACIÓN
**Objetivo:** Completar manual e informe técnico

| Día | Actividad | Horas | Resultado Esperado |
|-----|-----------|-------|-------------------|
| **Lun 12** | Crear Manual PDF (parte 1) | 3h | Estructura y contenido |
| **Mar 13** | Crear Manual PDF (parte 2) | 3h | Capturas y formato |
| **Mié 14** | Crear Informe Técnico (parte 1) | 3h | Arquitectura y decisiones |
| **Jue 15** | Crear Informe Técnico (parte 2) | 3h | Diagramas |
| **Vie 16** | Revisar documentación | 2h | ✅ PDFs completos |

### 📅 Semana 3 (19-25 febrero) - PULIR
**Objetivo:** Mejorar detalles y preparar entrega

| Día | Actividad | Horas | Resultado Esperado |
|-----|-----------|-------|-------------------|
| **Lun 19** | Añadir más iconos | 3h | UI más visual |
| **Mar 20** | Crear librería instalable | 3h | Módulo DB externo |
| **Mié 21** | Pruebas integrales | 3h | Detectar bugs |
| **Jue 22** | Corregir bugs encontrados | 3h | Aplicación estable |
| **Vie 23** | Preparar entrega final | 2h | ✅ Todo listo |

---

## 8. Resumen Visual del Estado

### ✅ LO QUE TIENES (Completado al 100%)

```
[████████████████████] Funcionalidades básicas
[████████████████████] Interfaz gráfica
[████████████████████] Base de datos
[████████████████████] Código MVC limpio
[████████████████████] Estilos QSS
[████████████████████] Sistema de navegación
```

### 🔴 LO QUE TE FALTA (Crítico)

```
[████████████████░░░░] Lista jugadores (80%) ← **PRIORIDAD 0**
[░░░░░░░░░░░░░░░░░░░░] Empaquetado .exe     ← **PRIORIDAD 1**
[████████░░░░░░░░░░░░] Manual PDF (40%)     ← **PRIORIDAD 2**
[░░░░░░░░░░░░░░░░░░░░] Informe técnico PDF  ← **PRIORIDAD 3**
[████████████░░░░░░░░] Iconos (60%)         ← **PRIORIDAD 4**
[░░░░░░░░░░░░░░░░░░░░] Librería instalable  ← **PRIORIDAD 5**
```

---

## 9. Estimación Final

### Tiempo Total Necesario para Completar
- **FUNCIONALIDAD (Lista jugadores):** 2-3 horas
- **CRÍTICO (Empaquetado):** 8 horas
- **IMPORTANTE (Documentación):** 10 horas  
- **DESEABLE (Mejoras):** 5-8 horas
- **TOTAL:** **25-29 horas de trabajo**

### Nota Estimada por Escenario

| Escenario | Tareas Completadas | Nota Estimada |
|-----------|-------------------|---------------|
| **Actual** | Sin empaquetado | **0** (sin .exe) |
| **Mínimo viable** | Solo empaquetado | **~60/100** |
| **Con documentación** | Empaquetado + PDFs | **~85/100** |
| **Completo** | Todo + mejoras | **~95/100** |

---

## 10. Bugs Conocidos y Estado

### ✅ Corregidos Recientemente (4-5 feb 2026)
1. ~~Columna "Jugador" muy ancha~~ → **SOLUCIONADO**
2. ~~Botón ↑ SpinBox no funcionaba~~ → **SOLUCIONADO**
3. ~~Ganadores octavos no aparecían~~ → **SOLUCIONADO**
4. ~~Emparejamiento incorrecto bracket~~ → **SOLUCIONADO**
5. ~~Espacio excesivo título-botones home~~ → **SOLUCIONADO**

### 🟢 Estado Actual
- ✅ Aplicación estable
- ✅ Sin bugs críticos
- ⚠️ Funcionalidades operativas al 95% (falta listar jugadores de equipo)

### 🔴 Pendientes Funcionales
1. **Listar jugadores al seleccionar equipo** en gestión de equipos

---

## 11. Recursos y Tecnologías

### Stack Tecnológico
- **Python 3.13.7**
- **PySide6** (Qt for Python)
- **SQLite** 
- **PyInstaller** (pendiente configurar)

### Herramientas
- VS Code
- Git/GitHub
- Qt Designer (referencia)

---

## ⚠️ RECORDATORIO CRÍTICO

**El enunciado especifica claramente:**

> "El proyecto deberá entregarse en formato ejecutable (.exe) completamente funcional, de modo que el usuario final pueda ejecutar la aplicación directamente mediante doble clic, sin necesidad de realizar ninguna configuración previa ni posterior. **La calificación será de 0 para cualquier proyecto que no funcione de esta manera.**"

### Conclusión
El proyecto está **funcionalmente casi completo al 95%** (falta listar jugadores al seleccionar equipo), pero **técnicamente incompleto** porque falta:
0. ⚠️ **FUNCIONALIDAD BÁSICA:** Listar jugadores al seleccionar equipo (-1% de funcionalidades)
1. 🔴 **CRÍTICO:** Empaquetado .exe (SIN ESTO = 0)
2. ⚠️ **IMPORTANTE:** Documentación PDF (Afecta -5% de nota)
3. 🟡 **DESEABLE:** Mejoras visuales y extras

**Tiempo estimado para completar lo mínimo:** 20-23 horas
**Tiempo estimado para nota alta (>90):** 28-32 horas

---

**Última actualización:** 5 de febrero de 2026  
**Próxima revisión:** 12 de febrero de 2026
