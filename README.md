<div align="center">

# AudiVo

<img src="assets/icon.png" alt="Logo de AudiVo" width="175">

<br>

<p>
  <a href="https://github.com/RenzoFernando/AudiVo/releases/latest">
    <img src="https://img.shields.io/github/v/release/RenzoFernando/AudiVo?style=for-the-badge&label=VERSIÓN&color=3b82f6" alt="Última versión publicada">
  </a>
  <a href="https://github.com/RenzoFernando/AudiVo/releases/latest">
    <img src="https://img.shields.io/badge/VER%20RELEASES-20242b?style=for-the-badge" alt="Ver releases">
  </a>
  <a href="https://renzofernando.github.io/AudiVo/">
    <img src="https://img.shields.io/badge/PÁGINA%20OFICIAL-3b82f6?style=for-the-badge" alt="Abrir página oficial">
  </a>
</p>

<strong>Convierte audio en video o extrae el audio de un video directamente en tu computador.</strong>

<br><br>

AudiVo convierte archivos localmente mediante FFmpeg y permite alternar entre audio → video y video → audio desde la misma interfaz.

</div>

---

## Descripción

**AudiVo** es una aplicación de escritorio enfocada en convertir audio y video de forma sencilla y local.

Puedes seleccionar o arrastrar un archivo, cambiar el sentido de la conversión y conservar preferencias independientes para cada flujo. En audio → video puedes elegir formato visual, calidad y fondo; en video → audio puedes elegir el formato de salida y el perfil de audio.

## Funciones principales

- **Dos modos de conversión:** alterna entre audio → video y video → audio desde el selector de la interfaz.
- **Archivos y arrastrar y soltar:** carga el archivo desde la interfaz o mediante drag and drop.
- **Formatos de video:** horizontal, vertical, cuadrado y otras relaciones de aspecto.
- **Calidad configurable:** 480p, 720p y 1080p para la creación de video.
- **Fondos:** negro, blanco o imagen personalizada conservando su proporción.
- **Extracción de audio:** acepta videos reconocidos por FFmpeg que contengan una pista de audio, sin depender de una extensión concreta.
- **Varios formatos de audio:** FLAC, MP3, M4A, WAV, AAC, OGG, OPUS, WMA, AIFF y AMR.
- **Perfiles de audio:** Voz, Estándar y Original permiten elegir entre 16 kHz mono, 48 kHz estéreo o conservar frecuencia y canales de la fuente.
- **Guardar como:** permite definir el nombre del archivo generado y elegir la carpeta de salida desde el botón de tres puntos.
- **Preferencias persistentes:** recuerda el modo, formato de audio, perfil, opciones de video y carpeta de salida de cada modo.
- **Progreso y cancelación:** consulta porcentaje, contenido procesado y tiempo restante aproximado.
- **Interfaz en español e inglés.**
- **Conversión local con FFmpeg.**

## Modos de conversión

| Modo | Entrada | Salida |
| --- | --- | --- |
| **Audio → Video** | MP3, M4A, WAV, AAC, FLAC, OGG, OPUS, WMA, AIFF y AMR | MP4 |
| **Video → Audio** | Cualquier archivo que FFmpeg reconozca como video y que incluya una pista de audio | FLAC, MP3, M4A, WAV, AAC, OGG, OPUS, WMA, AIFF o AMR |

En **Video → Audio**, AudiVo inicia con **FLAC** y el perfil **Voz** (`16 kHz · mono`). También puedes usar **Estándar** (`48 kHz · estéreo`) u **Original** para conservar la frecuencia y los canales de la fuente cuando el formato de salida lo permite.

## Uso

1. Elige **AUDIO → VIDEO** o **VIDEO → AUDIO** desde el selector de la zona de entrada.
2. Selecciona o arrastra el archivo que quieres convertir.
3. Configura las opciones del modo actual, el nombre de salida y su carpeta.
4. Pulsa **CREAR VIDEO** o **EXTRAER AUDIO**.
5. Abre el archivo generado o su carpeta directamente desde AudiVo.

Formatos de audio compatibles:

`MP3` · `M4A` · `WAV` · `AAC` · `FLAC` · `OGG` · `OPUS` · `WMA` · `AIFF` · `AMR`

Para video → audio no se limita la selección a una lista cerrada de extensiones: AudiVo comprueba el archivo con FFmpeg y requiere una pista de video y una pista de audio válidas.

## Descarga

AudiVo se publica mediante dos artefactos oficiales con nombres estables:

- **Instalable recomendado:** [`AudiVo-Setup.exe`](https://github.com/RenzoFernando/AudiVo/releases/latest/download/AudiVo-Setup.exe)
- **Portable:** [`AudiVo-Portable.exe`](https://github.com/RenzoFernando/AudiVo/releases/latest/download/AudiVo-Portable.exe)

Canales oficiales:

- **Página oficial:** https://renzofernando.github.io/AudiVo/
- **Última release:** https://github.com/RenzoFernando/AudiVo/releases/latest
- **Repositorio:** https://github.com/RenzoFernando/AudiVo
- **Creador:** https://github.com/RenzoFernando

La versión de los ejecutables se obtiene desde `app/app_meta.py`, y la página oficial consulta la última GitHub Release para mostrar la versión publicada y enlazar sus artefactos.

## Privacidad y funcionamiento local

AudiVo procesa el audio y el video directamente en el computador mediante FFmpeg. La conversión no depende de una API por minuto ni requiere enviar los archivos a un servicio externo.

## Licencia

AudiVo se distribuye bajo la **MIT License**.

Copyright © 2026 · Renzo Fernando Mosquera Daza