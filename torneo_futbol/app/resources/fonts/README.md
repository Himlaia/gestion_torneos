# Fuentes personalizadas

## Poppins

Fuente: [Google Fonts - Poppins](https://fonts.google.com/specimen/Poppins)

Licencia: Open Font License (OFL)

### Archivos incluidos:
- `Poppins-Medium.ttf` (Weight 500)
- `Poppins-SemiBold.ttf` (Weight 600)

### Uso en la aplicación:
La fuente Poppins se aplica a:
- Título principal de cada pantalla (`QLabel#homeTitleLabel` y `QLabel#titleLabel`)
- Fallback para títulos de tarjetas si Montserrat no está disponible

---

## Montserrat

Fuente: [Google Fonts - Montserrat](https://fonts.google.com/specimen/Montserrat)

Licencia: Open Font License (OFL)

### Archivos necesarios:
- `Montserrat-Medium.ttf` (Weight 500) - **Descargar manualmente**
- `Montserrat-SemiBold.ttf` (Weight 600) - **Descargar manualmente**

### Cómo instalar Montserrat:
1. Visita https://fonts.google.com/specimen/Montserrat
2. Descarga los archivos TTF para Medium (500) y SemiBold (600)
3. Coloca los archivos en esta carpeta
4. Reinicia la aplicación

### Uso en la aplicación:
La fuente Montserrat se aplica a:
- Títulos de las tarjetas del menú principal (`QLabel#homeCardTitle`)
- Si no está disponible, se usa Poppins como fallback

---

**Nota:** Todo el texto secundario y descripciones mantienen la fuente por defecto (Segoe UI).
