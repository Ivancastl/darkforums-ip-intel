# 🗺️ DarkForums IP Intelligence Map

Herramienta OSINT para visualizar y mapear IPs en un mapa interactivo oscuro. Geolocalización offline con GeoLite2 + enriquecimiento con ipinfo.io al hacer clic.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Leaflet](https://img.shields.io/badge/Leaflet.js-1.9-green?logo=leaflet)

---

## ✨ Funciones

- 🌍 Mapa oscuro interactivo con clustering de marcadores
- 🔍 Búsqueda de username con autocompletado en tiempo real
- 📌 Filtro de mapa por actor — clic en sugerencia → solo sus IPs
- 🏢 Detalle enriquecido al clic: ciudad, ISP, timezone, hostname
- 🚫 Deduplicación automática de IPs por actor
- 🗺️ Mini mapa de ubicación exacta en el panel lateral
- 🌐 Filtro por país

---

## 📋 Requisitos

- Python 
- Cuenta gratuita en https://ipinfo.io — 50,000 consultas/mes gratis
  
---

## 🚀 Instalación

### 1. Clonar

```bash
git clone https://github.com/Ivancastl/darkforums-ip-intel.git
cd darkforums-ip-intel
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Token gratuito de ipinfo.io

1. Regístrate en https://ipinfo.io/signup
2. Copia tu token desde https://ipinfo.io/account/token
3. El plan gratuito incluye **50,000 consultas/mes**

El token enriquece el detalle al hacer clic en un pin (ciudad exacta, ISP, timezone). Sin token el mapa sigue funcionando con GeoLite2.

### 5. Correr

```bash
python flask_app.py
```

Pedirá el token de forma segura (oculto en consola). Presiona Enter para omitir.

```
🔑 Token ipinfo.io (oculto, Enter para omitir):
==================================================
  IP Intelligence Map
  DB     : C:\...\ips.db
  GeoIP  : C:\...\GeoLite2-Country.mmdb
  ipinfo : ✓ configurado
  URL    : http://127.0.0.1:5000
==================================================
```

Abre: **http://127.0.0.1:5000**

---



## 🔒 Privacidad

`ips.db` y `GeoLite2-Country.mmdb` están en `.gitignore`. Nunca compartas tu base de datos ni tu token públicamente.

---

## 📄 Licencia

MIT
