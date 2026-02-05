# 📖 Guía de Usuario - Gestión de Torneo de Fútbol

Bienvenido a la aplicación de **Gestión de Torneos de Fútbol**. Esta guía te ayudará a entender cómo usar cada función de la aplicación paso a paso.

---

## 📋 Índice

1. [Inicio Rápido](#-inicio-rápido)
2. [Vista Inicio](#-vista-inicio)
3. [Gestión de Equipos](#-gestión-de-equipos)
4. [Gestión de Participantes](#-gestión-de-participantes)
5. [Calendario y Partidos](#-calendario-y-partidos)
6. [Cuadro de Eliminatorias](#-cuadro-de-eliminatorias)
7. [Modo Claro/Oscuro](#-modo-clarooscuro)
8. [Preguntas Frecuentes](#-preguntas-frecuentes)

---

## 🚀 Inicio Rápido

### ¿Qué puedo hacer con esta aplicación?

Esta aplicación te permite gestionar un torneo de fútbol completo:
- ✅ Registrar equipos con sus escudos
- ✅ Añadir jugadores y árbitros
- ✅ Programar partidos automáticamente
- ✅ Registrar resultados y estadísticas
- ✅ Ver el cuadro de eliminatorias actualizado automáticamente

### Primer uso - Pasos básicos

1. **Crear equipos** (mínimo 16 para un torneo completo)
2. **Añadir jugadores** a cada equipo
3. **Añadir árbitros** para los partidos
4. **Generar el torneo** automáticamente
5. **Programar fechas** de los partidos
6. **Registrar resultados** a medida que se juegan

---

## 🏠 Vista Inicio

La pantalla de inicio te muestra un resumen del estado del torneo.

### ¿Qué veo aquí?

- **Contador de equipos**: Cuántos equipos hay registrados
- **Contador de jugadores**: Cuántos jugadores hay en total
- **Contador de árbitros**: Cuántos árbitros hay disponibles
- **Contador de partidos**: Cuántos partidos hay programados/jugados
- **Gráfico de progreso**: Muestra visualmente el avance del torneo

### Navegación

Usa el menú lateral izquierdo para moverte entre las diferentes secciones:
- 🏠 **Inicio**: Resumen general
- ⚽ **Equipos**: Gestionar equipos
- 👥 **Participantes**: Gestionar jugadores y árbitros
- 📅 **Calendario**: Ver y programar partidos
- 🏆 **Torneo**: Ver el cuadro de eliminatorias

---

## ⚽ Gestión de Equipos

### ¿Qué puedo hacer aquí?

En esta sección puedes crear, editar y eliminar equipos que participarán en el torneo.

### Crear un nuevo equipo

1. Haz clic en el botón **"+ Añadir Equipo"**
2. Se abrirá un formulario donde debes completar:
   - **Nombre del equipo**: Ej: "FC Barcelona"
   - **Curso**: Ej: "2º ESO"
   - **Color**: Haz clic en el cuadro de color para elegir uno
   - **Escudo** (opcional): Haz clic en "Seleccionar escudo..." para elegir una imagen
3. Haz clic en **"Guardar"**

### Editar un equipo existente

1. Haz clic sobre el equipo en la lista
2. Modifica los datos que necesites en el panel derecho
3. Haz clic en **"Guardar"**

### Eliminar un equipo

1. Haz clic sobre el equipo en la lista
2. Haz clic en el botón **"Eliminar"**
3. Confirma la eliminación

> ⚠️ **Importante**: No puedes eliminar un equipo que ya esté en partidos programados. Primero debes eliminar esos partidos.

### Ver jugadores de un equipo

1. Haz clic sobre un equipo en la lista
2. En el panel derecho verás la pestaña **"Jugadores"**
3. Allí puedes ver todos los jugadores del equipo y añadir nuevos

---

## 👥 Gestión de Participantes

### ¿Qué son los participantes?

Los participantes son todas las personas que intervienen en el torneo:
- **Jugadores**: Personas que juegan en los equipos
- **Árbitros**: Personas que arbitran los partidos
- Una misma persona puede ser jugador Y árbitro

### Crear un nuevo participante

1. Haz clic en **"+ Añadir Participante"**
2. Completa el formulario:
   - **Nombre**: Ej: "Juan"
   - **Apellidos**: Ej: "García Pérez"
   - **Fecha de nacimiento**: Usa el calendario
   - **Curso**: Ej: "2º ESO"
   - **¿Es jugador?**: Marca esta casilla si juega
   - **¿Es árbitro?**: Marca esta casilla si arbitra
   - **Posición** (si es jugador): Portero, Defensa, Centrocampista o Delantero
   - **Equipo** (si es jugador): Selecciona a qué equipo pertenece
3. Haz clic en **"Guardar"**

### Estadísticas automáticas

La aplicación actualiza automáticamente las siguientes estadísticas:
- **Goles**: Se suman cuando registras resultados
- **Tarjetas amarillas**: Se cuentan automáticamente
- **Tarjetas rojas**: Se cuentan automáticamente
- **Partidos jugados**: Se actualizan al guardar resultados

### Filtrar participantes

Usa los botones en la parte superior:
- **Todos**: Muestra todos los participantes
- **Solo Jugadores**: Muestra solo los que son jugadores
- **Solo Árbitros**: Muestra solo los que son árbitros

---

## 📅 Calendario y Partidos

Esta es la sección más importante donde programas y gestionas los partidos del torneo.

### Vista general

La pantalla se divide en tres partes:
1. **Calendario** (izquierda): Muestra los días del mes
2. **Lista de partidos** (centro): Lista de partidos del día seleccionado
3. **Detalles del partido** (derecha): Información completa del partido seleccionado

### Generar el torneo automáticamente

Para empezar un torneo desde cero:

1. **Asegúrate de tener 16 equipos registrados**
2. Haz clic en el botón **"Generar Torneo"** (en la parte superior)
3. Confirma que deseas generar los partidos
4. La aplicación creará automáticamente:
   - 8 partidos de **Octavos de Final**
   - Emparejamientos aleatorios
   - Fechas distribuidas en 8 días consecutivos

> 💡 **Automatización**: Los partidos de cuartos, semifinales y final se crearán automáticamente cuando vayas registrando resultados.

### Programar un partido manualmente

Si quieres crear un partido específico:

1. Haz clic en **"+ Nuevo Partido"**
2. En la pestaña **"Datos"** completa:
   - **Eliminatoria**: Octavos, Cuartos, Semifinal o Final
   - **Equipo Local**: Selecciona un equipo
   - **Equipo Visitante**: Selecciona otro equipo
   - **Fecha y hora**: Usa los selectores
   - **Árbitro**: Selecciona quién arbitrará
3. Haz clic en **"Guardar"**

### Cambiar la fecha de un partido

1. Haz clic sobre el partido en la lista
2. En la pestaña **"Datos"**, modifica la fecha u hora
3. Haz clic en **"Guardar"**

### Convocar jugadores para un partido

Antes de poder registrar el resultado, debes convocar a los jugadores:

1. Selecciona el partido
2. Ve a la pestaña **"Convocatorias"**
3. Para cada equipo:
   - **Equipo Local**: Marca las casillas de los jugadores convocados
   - **Equipo Visitante**: Marca las casillas de los jugadores convocados
4. Haz clic en **"Guardar Convocatorias"**

> ⚠️ **Importante**: Debes convocar al menos 1 jugador por equipo para poder registrar el resultado.

### Registrar el resultado de un partido

Una vez jugado el partido:

1. Selecciona el partido en la lista
2. Ve a la pestaña **"Resultado"**
3. Completa los datos:
   - **Goles Local**: Número de goles del equipo local
   - **Goles Visitante**: Número de goles del equipo visitante
   - **Penaltis** (si hubo empate): Marca la casilla y añade los resultados de penaltis
4. Haz clic en **"Detalles de goles..."** para asignar quién marcó cada gol:
   - Haz clic en **"+ Añadir Gol"**
   - Selecciona el equipo, jugador y minuto
   - Repite hasta completar todos los goles
   - O usa **"Randomizar"** para que se asignen automáticamente
5. (Opcional) Ve a la pestaña **"Estadísticas"** para añadir tarjetas:
   - Selecciona un jugador
   - Ajusta amarillas/rojas con los controles + y -
6. Haz clic en **"Guardar Resultado"**

### Automatización al guardar resultado

Cuando guardas un resultado, la aplicación automáticamente:
- ✅ Determina quién es el ganador
- ✅ Avanza al ganador a la siguiente ronda
- ✅ Crea el partido de la siguiente ronda (si ambos hermanos están jugados)
- ✅ Actualiza el cuadro de eliminatorias
- ✅ Actualiza las estadísticas de los jugadores

### Ver partidos de un día específico

1. Haz clic en cualquier día del calendario
2. Los días con partidos aparecen resaltados
3. La lista central mostrará todos los partidos de ese día

### Calendario de días con partidos

1. Haz clic en el botón **"Partidos del día"** (icono de calendario)
2. Se abrirá un diálogo con todos los días que tienen partidos programados
3. Haz doble clic en un día para ver sus partidos
4. O haz clic en "Abrir partido" para ver los detalles directamente

---

## 🏆 Cuadro de Eliminatorias

### ¿Qué veo aquí?

Esta pantalla muestra el cuadro completo del torneo en formato de eliminatorias, similar a los torneos profesionales.

### Estructura del cuadro

El cuadro se divide en columnas:
- **Octavos de Final** (8 partidos)
- **Cuartos de Final** (4 partidos)
- **Semifinales** (2 partidos)
- **Final** (1 partido)

### Colores y marcas

- **Verde con borde**: El equipo ganó ese partido y avanza
- **Dorado**: El equipo es el campeón del torneo
- **Sin color**: El partido aún no se ha jugado o el equipo perdió

### Modo de configuración manual

Si aún no has generado el torneo automáticamente, puedes:

1. Usar el botón **"Randomizar octavos"** para generar emparejamientos aleatorios
2. O seleccionar manualmente cada equipo en los combos
3. Haz clic en **"Guardar emparejamientos"** cuando termines

### Modo de solo lectura

Una vez que hay partidos en la base de datos, el cuadro pasa a modo solo lectura y se actualiza automáticamente cuando registras resultados.

### Reiniciar el torneo

Si quieres empezar de cero:

1. Haz clic en **"Reiniciar emparejamientos"**
2. Confirma que deseas eliminar TODOS los partidos
3. El cuadro volverá a estar vacío y en modo configurable

> ⚠️ **Cuidado**: Esta acción elimina todos los partidos, convocatorias y resultados. No se puede deshacer.

---

## 🌓 Modo Claro/Oscuro

### Cambiar el tema

Puedes cambiar entre modo claro y oscuro según tu preferencia:

1. Ve al menú **"Ver"** en la parte superior
2. Haz clic en **"Cambiar Tema"**
3. O usa el botón de tema (🌙/☀️) si está disponible

La aplicación recordará tu preferencia para la próxima vez que la abras.

---

## ❓ Preguntas Frecuentes

### ¿Cuántos equipos necesito para un torneo?

Para un torneo completo necesitas **16 equipos**. Si tienes menos, puedes crear partidos manualmente en cualquier fase.

### ¿Qué pasa si hay empate en un partido?

Cuando registras un empate (mismo número de goles), debes marcar la casilla de "Penaltis" e indicar el resultado de la tanda de penaltis para determinar al ganador.

### ¿Puedo editar un resultado después de guardarlo?

Sí, selecciona el partido, ve a la pestaña "Resultado" y haz los cambios necesarios. Al guardar, se actualizarán todas las estadísticas y el cuadro de eliminatorias.

### ¿Cómo elimino un partido?

1. Selecciona el partido en la lista
2. Haz clic en el botón "Eliminar"
3. Confirma la eliminación

> ⚠️ **Nota**: Si eliminas un partido de octavos, se eliminarán en cascada todos los partidos de rondas posteriores que dependan de ese resultado.

### ¿Por qué no puedo guardar un resultado?

Asegúrate de que:
- ✅ Los equipos local y visitante estén asignados
- ✅ El árbitro esté asignado
- ✅ Hay jugadores convocados para ambos equipos
- ✅ Los goles detallados coinciden con el marcador

### ¿Los jugadores convocados deben coincidir con los goleadores?

No necesariamente. Puedes convocar a todos los jugadores del equipo, pero solo algunos marcarán goles. Lo importante es que los jugadores que marquen goles estén en la convocatoria.

### ¿Puedo tener menos de 16 equipos?

Sí, pero no podrás usar la función "Generar Torneo" automática. Deberás crear los partidos manualmente usando "+ Nuevo Partido".

### ¿Qué pasa si elimino un equipo que ya jugó partidos?

No podrás eliminarlo. Primero debes eliminar todos los partidos en los que participó ese equipo.

### ¿Cómo veo las estadísticas de un jugador?

1. Ve a la sección **"Participantes"**
2. Haz clic sobre el jugador en la lista
3. En el panel derecho verás todas sus estadísticas:
   - Goles marcados
   - Tarjetas amarillas
   - Tarjetas rojas
   - Partidos jugados

### ¿Puedo exportar los datos?

Actualmente la aplicación no incluye funcionalidad de exportación, pero todos los datos están almacenados en la base de datos SQLite en la carpeta `data/torneo.db`.

### ¿Dónde se guardan los escudos de los equipos?

Los escudos se guardan en la carpeta `data/escudos/` con un nombre único generado automáticamente.

---

## 💡 Consejos y Trucos

### Flujo de trabajo recomendado

1. **Preparación** (antes del torneo):
   - Crea todos los equipos
   - Añade todos los jugadores y asígnalos a sus equipos
   - Añade los árbitros
   
2. **Inicio del torneo**:
   - Genera el torneo automáticamente
   - Revisa las fechas y ajústalas si es necesario
   
3. **Durante el torneo**:
   - Antes de cada partido: convoca a los jugadores
   - Después de cada partido: registra el resultado y los goles
   - El cuadro se actualiza automáticamente

4. **Final**:
   - Consulta las estadísticas generales
   - Exporta los datos si es necesario

### Atajos útiles

- **Doble clic** en un partido del calendario: Abre los detalles
- **Enter** en los formularios: Guarda los cambios
- **Escape** en los diálogos: Cancela sin guardar

### Organización recomendada

- Usa nombres claros y consistentes para los equipos
- Añade el curso en el nombre si tienes varios torneos
- Programa los partidos con fechas realistas
- Convoca a los jugadores con anticipación

---

## 📞 Soporte

Si tienes problemas o dudas:

1. Revisa esta guía completa
2. Consulta los mensajes de error que muestre la aplicación
3. Verifica que todos los datos estén correctamente ingresados
4. Contacta al administrador del sistema

---

## 📄 Información Adicional

**Versión de la aplicación**: 1.0  
**Última actualización**: Febrero 2026  
**Desarrollado con**: Python, PySide6, SQLite  

---

**¡Disfruta gestionando tu torneo de fútbol! ⚽🏆**
