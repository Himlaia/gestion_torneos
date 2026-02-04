# 🔄 REFACTOR SISTEMA DE PARTIDOS - RESUMEN Y GUÍA

## ✅ Cambios Completados

### 1. Nuevo Modelo: GoalModel (goal_model.py)
- ✅ Tabla `goles` añadida al schema con campos: id, partido_id, participante_id, equipo_id, minuto
- ✅ Métodos CRUD completos:
  - `registrar_gol()`: Registra un gol con autor y minuto
  - `obtener_goles_partido()`: Obtiene todos los goles de un partido
  - `obtener_goles_equipo_partido()`: Goles de un equipo específico
  - `eliminar_gol()`: Elimina un gol
  - `limpiar_goles_partido()`: Limpia todos los goles de un partido
  - `contar_goles_equipo_partido()`: Cuenta goles de un equipo
  - `actualizar_minuto()`: Actualiza el minuto de un gol

### 2. Nuevo Servicio: MatchService (match_service.py)
- ✅ Dataclass `MatchData` para validación robusta de datos de partido
- ✅ Métodos de validación:
  - `esta_programado()`: Verifica si tiene equipos y fecha
  - `puede_editar_resultado()`: Verifica si tiene equipos
  - `puede_guardar_resultado()`: Verifica equipos + árbitro
  - `validate_for_result_save()`: Validación completa pre-guardado
- ✅ Métodos de persistencia:
  - `load_match()`: Carga partido con validación
  - `save_match_data()`: Guarda datos SIN eliminar emparejamientos
  - `save_convocatoria()`: Guarda convocados completos
  - `save_result_with_goals()`: Guarda resultado + goles + stats
  - `randomize_goalscorers()`: Distribuye goles aleatoriamente

### 3. Schema Actualizado (schema.py)
- ✅ Tabla `goles` añadida con relaciones correctas
- ✅ Índices creados: `idx_goles_partido`, `idx_goles_participante`

### 4. Dirty State Tracking (page_matches.py)
- ✅ Flags añadidos: `datos_dirty`, `convocatoria_dirty`, `resultado_dirty`
- ✅ Métodos de control:
  - `mark_datos_dirty()`: Marca cambios en datos
  - `mark_convocatoria_dirty()`: Marca cambios en convocatoria
  - `mark_resultado_dirty()`: Marca cambios en resultado
  - `clear_all_dirty_flags()`: Limpia todos los flags
  - `has_unsaved_changes()`: Verifica si hay cambios sin guardar
  - `update_guardar_button_state()`: Actualiza estado de botón Guardar
  - `puede_guardar_resultado()`: Valida si se puede guardar resultado

### 5. Sistema de Pestañas Liberado (page_matches.py)
- ✅ **CAMBIO CRÍTICO**: Las pestañas Datos/Convocatoria/Resultado NUNCA se bloquean
- ✅ Usuario puede navegar libremente entre pestañas
- ✅ Validación ocurre solo al guardar
- ✅ Botones de guardar se habilitan/deshabilitan según:
  - Dirty state
  - Validaciones de datos mínimos
  - Modo actual (ver/crear/editar/editar_resultado)

### 6. Validaciones Robustas
- ✅ `set_modo()` actualizado:
  - Modo "ver": Todo deshabilitado
  - Modo "crear"/"editar": Tab Datos habilitado
  - Modo "editar_resultado": Tab Resultado habilitado, árbitro editable
- ✅ Validación en `puede_guardar_resultado()`:
  - Equipos asignados
  - Árbitro asignado
  - No empate total (goles + penaltis)

### 7. UI Goles con Autor (page_matches.py)
- ✅ Grupo "Goles con Autor (Opcional)" añadido
- ✅ Tabla con columnas: Minuto, Equipo, Jugador, [Eliminar]
- ✅ Botones:
  - "Añadir Gol": Añade fila manual
  - "Randomizar Goleadores": Distribuye goles automáticamente
  - "Limpiar Goles": Vacía la tabla

### 8. Señales de Cambio Conectadas
- ✅ Cambios en comboFase → `mark_datos_dirty()`
- ✅ Cambios en comboLocal/comboVisitante → `mark_datos_dirty()`
- ✅ Cambios en fecha_hora → `mark_datos_dirty()`
- ✅ Cambios en comboArbitro → `mark_datos_dirty()`
- ✅ Cambios en goles → `mark_resultado_dirty()`
- ✅ Cambios en penaltis → `mark_resultado_dirty()`

## 🚧 Pendiente de Implementación

### 1. Conectar Botones de Goles con Autor (page_matches.py)
```python
# En conectar_senales(), añadir:
self.btn_anadir_gol.clicked.connect(self.on_anadir_gol_manual)
self.btn_randomizar_goles.clicked.connect(self.on_randomizar_goles)
self.btn_limpiar_goles.clicked.connect(self.on_limpiar_goles)

# Implementar métodos:
def on_anadir_gol_manual(self):
    """Añade una fila para registrar un gol manualmente."""
    # Mostrar diálogo para seleccionar:
    # - Equipo (local/visitante)
    # - Jugador (de los convocados de ese equipo)
    # - Minuto (opcional)
    pass

def on_randomizar_goles(self):
    """Distribuye goles aleatoriamente usando MatchService."""
    if not self.partido_actual_id:
        return
    
    goles_local = self.goles_local.value()
    goles_visitante = self.goles_visitante.value()
    
    goles_detalle = MatchService.randomize_goalscorers(
        self.partido_actual_id,
        goles_local,
        goles_visitante
    )
    
    # Rellenar tabla_goles_autor con goles_detalle
    self.cargar_goles_autor(goles_detalle)
    self.mark_resultado_dirty()

def on_limpiar_goles(self):
    """Limpia la tabla de goles."""
    self.tabla_goles_autor.setRowCount(0)
    self.mark_resultado_dirty()

def cargar_goles_autor(self, goles: list[dict]):
    """Carga los goles en la tabla."""
    self.tabla_goles_autor.setRowCount(len(goles))
    for i, gol in enumerate(goles):
        # Columna 0: Minuto
        minuto_item = QTableWidgetItem(str(gol.get('minuto') or '-'))
        self.tabla_goles_autor.setItem(i, 0, minuto_item)
        
        # Columna 1: Equipo
        # Obtener nombre de equipo desde participante_id
        # ...
        
        # Columna 2: Jugador
        # Obtener nombre desde participante_id
        # ...
        
        # Columna 3: Botón Eliminar
        btn_eliminar = QPushButton("X")
        btn_eliminar.clicked.connect(lambda checked, row=i: self.eliminar_gol_fila(row))
        self.tabla_goles_autor.setCellWidget(i, 3, btn_eliminar)
```

### 2. Actualizar ControladorCalendarioPartidos (matches_controller.py)
```python
# Importar nuevo servicio
from app.services.match_service import MatchService, MatchData

# En _on_guardar_partido():
def _on_guardar_partido(self):
    # Obtener datos del formulario
    datos = self.vista.obtener_datos_formulario()
    
    # Usar MatchService.save_match_data() en lugar de MatchModel.actualizar_partido()
    MatchService.save_match_data(
        partido_id=self.partido_actual_id,
        fase=datos['fase'],
        fecha_hora=datos['fecha_hora'],
        equipo_local_id=datos['local_id'],
        equipo_visitante_id=datos['visitante_id'],
        arbitro_id=datos['arbitro_id']
    )
    
    # Limpiar dirty flags
    self.vista.clear_all_dirty_flags()
    
    # NO elimina emparejamientos, solo actualiza datos

# En _on_guardar_resultado():
def _on_guardar_resultado(self):
    # Validar antes de guardar
    match = MatchService.load_match(self.partido_actual_id)
    if not match:
        QMessageBox.critical(self.vista, "Error", "Partido no encontrado")
        return
    
    es_valido, mensaje = MatchService.validate_for_result_save(match)
    if not es_valido:
        QMessageBox.warning(self.vista, "Validación", mensaje)
        return
    
    # Obtener datos del formulario
    datos = self.vista.get_datos_resultado()
    
    # Obtener goles con autor de la tabla
    goles_detalle = self.vista.get_goles_detalle()
    
    # Guardar con servicio
    MatchService.save_result_with_goals(
        partido_id=self.partido_actual_id,
        goles_local=datos['goles_local'],
        goles_visitante=datos['goles_visitante'],
        penaltis_local=datos.get('penaltis_local'),
        penaltis_visitante=datos.get('penaltis_visitante'),
        goles_detalle=goles_detalle,
        stats=datos['stats']
    )
    
    # Limpiar dirty flags
    self.vista.clear_all_dirty_flags()
    
    # Mostrar mensaje de éxito
    QMessageBox.information(
        self.vista,
        "Éxito",
        "Resultado guardado correctamente.\n"
        "El ganador ha sido avanzado a la siguiente ronda."
    )
```

### 3. Proteger Emparejamientos al Editar
```python
# En MatchService.save_match_data() ya está implementado:
# - NO toca ganador_equipo_id
# - NO resetea emparejamientos
# - Solo actualiza: fase, fecha_hora, equipos, árbitro, estado

# Asegurar que en MatchModel.actualizar_partido() no se toque ganador_equipo_id
# a menos que se esté guardando un resultado
```

### 4. Validar Persistencia de Convocatoria
```python
# En page_matches.py, el método _on_checkbox_changed() ya persiste automáticamente
# Verificar que al cambiar de pestaña no se pierden los checkboxes marcados

# En matches_controller.py:
def _on_convocatoria_cambiada(self, datos: dict):
    """Maneja cambios en convocatoria con persistencia inmediata."""
    # Ya implementado, solo verificar que funciona correctamente
    pass
```

### 5. Ajustar Layout Responsive en Participantes
```python
# En page_participants.py, línea ~155:
# Reducir anchos máximos de los filtros para que quepan en una fila
# Ya está parcialmente hecho, verificar que funciona hasta 800px de ancho
```

### 6. Corregir "ombre" → "Nombre"
```python
# Ya está corregido en page_participants.py línea 324:
# setHorizontalHeaderLabels(["Nombre", "Nacimiento", ...])
# Verificar que se ve correctamente
```

## 📋 Checklist de Testing

### Flujo Datos
- [ ] Crear nuevo partido → Asignar equipos → Guardar
- [ ] Editar fecha/hora de partido existente → Guardar
- [ ] Verificar que emparejamientos NO se borran al editar

### Flujo Convocatoria
- [ ] Marcar jugadores en checkboxes
- [ ] Cambiar a otra pestaña
- [ ] Volver a Convocatoria → Checkboxes siguen marcados
- [ ] Desmarcar jugadores → Persiste automáticamente

### Flujo Resultado
- [ ] Entrar a Resultado sin equipos asignados → Botón Guardar deshabilitado con tooltip
- [ ] Asignar equipos en Datos → Volver a Resultado → Botón sigue deshabilitado si falta árbitro
- [ ] Asignar árbitro → Botón se habilita
- [ ] Ingresar goles → Marca dirty state
- [ ] Click "Randomizar Goleadores" → Tabla de goles se llena
- [ ] Guardar resultado → Goles se registran en BD
- [ ] Verificar que ganador se propaga a siguiente ronda
- [ ] Verificar que cuadro de eliminatorias se actualiza

### Flujo Goles con Autor
- [ ] Ingresar 3 goles local, 2 visitante
- [ ] Click "Randomizar" → 5 filas en tabla
- [ ] Cada gol tiene: minuto, equipo, jugador
- [ ] Click "Añadir Gol" → Diálogo para seleccionar jugador
- [ ] Guardar resultado → Goles se guardan en tabla `goles`
- [ ] Recargar partido → Goles se muestran correctamente

### Validaciones
- [ ] Intentar guardar resultado sin equipos → Mensaje claro con pasos
- [ ] Intentar guardar resultado sin árbitro → Mensaje claro
- [ ] Empate en goles y penaltis → Mensaje de error
- [ ] Cambiar datos sin guardar → Botón Guardar habilitado
- [ ] Guardar cambios → Dirty flags se limpian

## 🎯 Beneficios del Refactor

1. **Flujo Intuitivo**: Usuario puede explorar todas las pestañas sin restricciones
2. **Validación Clara**: Mensajes específicos cuando faltan datos
3. **Dirty State**: Botones Guardar solo habilitados cuando hay cambios
4. **Goles con Autor**: Registro detallado de goleadores y minutos
5. **Emparejamientos Protegidos**: Editar partido NO borra el cuadro
6. **Convocatoria Persistente**: Cambios se guardan automáticamente
7. **Separación de Responsabilidades**: MatchService centraliza lógica
8. **Código Limpio**: Validaciones robustas, sin KeyError

## 🚀 Próximos Pasos

1. **Implementar métodos pendientes** en page_matches.py (ver sección "Pendiente")
2. **Actualizar controlador** para usar MatchService
3. **Testing exhaustivo** según checklist
4. **Migración de BD**: Ejecutar app para crear tabla `goles`
5. **Documentar** cambios para el equipo
6. **Refinar UI** de goles con autor (diálogos, validaciones)

## 📌 Notas Importantes

- **NO EJECUTAR** hasta completar implementaciones pendientes
- **HACER BACKUP** de la base de datos antes de probar
- **VERIFICAR** que convocatoria persiste correctamente
- **PROBAR** flujo completo: crear partido → convocar → resultado → verificar cuadro
