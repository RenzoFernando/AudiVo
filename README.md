<div align="center">

# AudiVo

<img src="assets/icon.png" alt="Logo de AudiVo" width="175">

<br>

<p>
  <a href="https://github.com/RenzoFernando/AudiVo/releases/latest">
    <img src="https://img.shields.io/github/v/release/RenzoFernando/AudiVo?style=for-the-badge&label=VERSI%C3%93N&color=3b82f6" alt="Versión actual">
  </a>
  <a href="https://github.com/RenzoFernando/AudiVo/releases/latest">
    <img src="https://img.shields.io/badge/VER%20RELEASES-20242b?style=for-the-badge" alt="Ver releases">
  </a>
  <a href="https://renzofernando.github.io/AudiVo/">
    <img src="https://img.shields.io/badge/P%C3%81GINA%20OFICIAL-3b82f6?style=for-the-badge" alt="Abrir página oficial">
  </a>
</p>

<strong>Convierte audio en video o extrae el audio de un video localmente con FFmpeg.</strong>

</div>

---

## Descripción

**AudiVo** es una aplicación de escritorio para Windows orientada a conversiones de audio y video. Desde una misma interfaz permite crear un MP4 a partir de un archivo de audio o extraer la pista de audio de un video reconocido por FFmpeg.

Cada modo conserva sus propias preferencias y ofrece controles específicos para formato, calidad, fondo, perfil de audio, nombre y carpeta de salida.

## Características

- **Dos modos de conversión:** Audio → Video y Video → Audio.
- **Archivos y arrastrar y soltar:** selecciona el archivo desde la interfaz o suéltalo directamente sobre la aplicación.
- **Formatos visuales configurables:** incluye relaciones horizontal, vertical, cuadrada y otras opciones para crear video.
- **Calidad de video:** 480p, 720p y 1080p.
- **Fondos para Audio → Video:** negro, blanco o imagen personalizada conservando su proporción.
- **Extracción de audio flexible:** admite archivos que FFmpeg reconozca como video y que contengan una pista de audio válida.
- **Múltiples formatos de audio:** FLAC, MP3, M4A, WAV, AAC, OGG, OPUS, WMA, AIFF y AMR.
- **Perfiles de audio:** Voz, Estándar y Original.
- **Nombre y carpeta de salida configurables.**
- **Preferencias persistentes:** recuerda las opciones de cada modo.
- **Progreso y cancelación:** muestra avance, contenido procesado y tiempo restante aproximado.
- **Interfaz en español e inglés.**

## Modos de conversión

| Modo | Entrada | Salida |
| --- | --- | --- |
| **Audio → Video** | MP3, M4A, WAV, AAC, FLAC, OGG, OPUS, WMA, AIFF y AMR | MP4 |
| **Video → Audio** | Archivo reconocido por FFmpeg como video y con pista de audio | FLAC, MP3, M4A, WAV, AAC, OGG, OPUS, WMA, AIFF o AMR |

En **Video → Audio**, AudiVo inicia con **FLAC** y el perfil **Voz** (`16 kHz · mono`). También están disponibles **Estándar** (`48 kHz · estéreo`) y **Original**, que conserva la frecuencia y los canales de la fuente cuando el formato de salida lo permite.

## Uso

1. Elige **AUDIO → VIDEO** o **VIDEO → AUDIO**.
2. Selecciona o arrastra el archivo que quieres convertir.
3. Configura las opciones del modo actual, el nombre del archivo de salida y su carpeta.
4. Pulsa **CREAR VIDEO** o **EXTRAER AUDIO**.
5. Abre el archivo generado o su carpeta directamente desde AudiVo.

Para Video → Audio no se utiliza una lista cerrada de extensiones de video: AudiVo valida el archivo mediante FFmpeg y requiere una pista de video y una pista de audio válidas.

## Descarga

AudiVo se distribuye mediante dos artefactos oficiales para Windows:

- **Instalable recomendado:** [`AudiVo-Setup.exe`](https://github.com/RenzoFernando/AudiVo/releases/latest/download/AudiVo-Setup.exe)
- **Portable:** [`AudiVo-Portable.exe`](https://github.com/RenzoFernando/AudiVo/releases/latest/download/AudiVo-Portable.exe)

El instalable integra la aplicación en Windows y es la opción indicada para uso habitual. El portable puede ejecutarse directamente sin realizar una instalación.

Canales oficiales:

- **Página oficial:** https://renzofernando.github.io/AudiVo/
- **Última release:** https://github.com/RenzoFernando/AudiVo/releases/latest
- **Código fuente:** https://github.com/RenzoFernando/AudiVo

## Funcionamiento local

AudiVo procesa el audio y el video directamente en el computador mediante FFmpeg. Las conversiones no dependen de una API remota ni requieren enviar los archivos a un servicio externo.

## Desarrollo

### Requisitos

- Windows.
- Python 3.11 o 3.12.
- Git.
- Conexión a Internet para instalar dependencias.
- Inno Setup 6 para generar el instalador; `buildinstaller.bat` intenta localizarlo y puede instalarlo mediante `winget` si no está disponible.

### Preparar el entorno

```batch
git clone https://github.com/RenzoFernando/AudiVo.git
cd AudiVo
setupAmp.bat
```

### Ejecutar desde código

```batch
.\.venv\Scripts\python.exe main.py
```

### Generar artefactos

```batch
buildportable.bat
buildinstaller.bat
```

Los artefactos finales se generan en `downloads/`.

## Autor y licencia

[Renzo Fernando Mosquera Daza](https://github.com/RenzoFernando)

Este proyecto se distribuye bajo la **Licencia MIT**. Consulta [`LICENSE`](LICENSE).
