import os, re, random, getpass
from flask import Flask, render_template, jsonify, request

try:
    import geoip2.database
    import requests as req_lib
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False
    print("⚠️  Instala: pip install geoip2 requests")

# ── Token ipinfo — se pide al arrancar si no está en entorno ─────────────────
_token = os.environ.get('IPINFO_TOKEN', '').strip()
if not _token:
    try:
        _token = getpass.getpass('🔑 Token ipinfo.io (oculto, Enter para omitir): ').strip()
    except Exception:
        _token = input('🔑 Token ipinfo.io (Enter para omitir): ').strip()

IPINFO_TOKEN = _token or None

# ── Rutas — ajusta si tus archivos están en otra carpeta ────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, 'ips.db')
MMDB_PATH = os.path.join(BASE_DIR, 'GeoLite2-Country.mmdb')

app = Flask(__name__)

# ── GeoIP singleton ──────────────────────────────────────────────────────────
_geo_reader = None
def get_geo_reader():
    global _geo_reader
    if not GEOIP_AVAILABLE: return None
    if _geo_reader is None and os.path.exists(MMDB_PATH):
        _geo_reader = geoip2.database.Reader(MMDB_PATH)
    return _geo_reader

COUNTRY_COORDS = {
    "AF":(33.93,67.71),"AL":(41.15,20.17),"DZ":(28.03,1.66),"AO":(-11.20,17.87),
    "AR":(-38.42,-63.62),"AM":(40.07,45.04),"AU":(-25.27,133.77),"AT":(47.52,14.55),
    "AZ":(40.14,47.58),"BD":(23.68,90.35),"BE":(50.50,4.47),"BJ":(9.31,2.32),
    "BR":(-14.23,-51.93),"BG":(42.73,25.49),"BF":(12.36,-1.56),"BI":(-3.37,29.92),
    "CM":(3.85,11.50),"CA":(56.13,-106.35),"CF":(6.61,20.94),"TD":(15.45,18.73),
    "CL":(-35.67,-71.54),"CN":(35.86,104.20),"CO":(4.57,-74.30),"CD":(-4.03,21.76),
    "CR":(9.75,-83.75),"CI":(7.54,-5.55),"HR":(45.10,15.20),"CU":(21.52,-77.78),
    "CY":(35.13,33.43),"CZ":(49.82,15.47),"DK":(56.26,9.50),"DO":(18.74,-70.16),
    "EC":(-1.83,-78.18),"EG":(26.82,30.80),"SV":(13.79,-88.90),"EE":(58.60,25.01),
    "ET":(9.14,40.49),"FI":(61.92,25.75),"FR":(46.23,2.21),"GA":(-0.80,11.61),
    "GM":(13.44,-15.31),"GE":(42.31,43.36),"DE":(51.17,10.45),"GH":(7.95,-1.02),
    "GR":(39.07,21.82),"GT":(15.78,-90.23),"GN":(9.95,-11.24),"HT":(18.97,-72.29),
    "HN":(15.20,-86.24),"HU":(47.16,19.50),"IS":(64.96,-19.02),"IN":(20.59,78.96),
    "ID":(-0.79,113.92),"IR":(32.43,53.69),"IQ":(33.22,43.68),"IE":(53.41,-8.24),
    "IL":(31.05,34.85),"IT":(41.87,12.57),"JM":(18.11,-77.30),"JP":(36.20,138.25),
    "JO":(30.59,36.24),"KZ":(48.02,66.92),"KE":(-0.02,37.91),"KP":(40.34,127.51),
    "KR":(35.91,127.77),"KW":(29.31,47.48),"KG":(41.20,74.77),"LA":(19.86,102.50),
    "LV":(56.88,24.60),"LB":(33.85,35.86),"LY":(26.34,17.23),"LT":(55.17,23.88),
    "LU":(49.82,6.13),"MG":(-18.77,46.87),"MW":(-13.25,34.30),"MY":(4.21,101.97),
    "ML":(17.57,-3.99),"MR":(21.01,-10.94),"MX":(23.63,-102.55),"MD":(47.41,28.37),
    "MN":(46.86,103.85),"ME":(42.71,19.37),"MA":(31.79,-7.09),"MZ":(-18.67,35.53),
    "MM":(16.87,96.41),"NA":(-22.96,18.49),"NP":(28.39,84.12),"NL":(52.13,5.29),
    "NZ":(-40.90,174.89),"NI":(12.87,-85.21),"NE":(17.61,8.08),"NG":(9.08,8.68),
    "NO":(60.47,8.47),"OM":(21.51,55.92),"PK":(30.38,69.35),"PA":(8.54,-80.78),
    "PY":(-23.44,-58.44),"PE":(-9.19,-75.02),"PH":(12.88,121.77),"PL":(51.92,19.15),
    "PT":(39.40,-8.22),"QA":(25.35,51.18),"RO":(45.94,24.97),"RU":(61.52,105.32),
    "SA":(23.89,45.08),"SN":(14.50,-14.45),"RS":(44.02,21.01),"SL":(8.46,-11.78),
    "SO":(5.15,46.20),"ZA":(-30.56,22.94),"SS":(4.86,31.57),"ES":(40.46,-3.75),
    "LK":(7.87,80.77),"SD":(12.86,30.22),"SE":(60.13,18.64),"CH":(46.82,8.23),
    "SY":(34.80,38.99),"TW":(23.70,120.96),"TJ":(38.86,71.28),"TZ":(-6.37,34.89),
    "TH":(15.87,100.99),"TG":(8.62,0.82),"TN":(33.89,9.54),"TR":(38.96,35.24),
    "TM":(38.97,59.56),"UG":(1.37,32.29),"UA":(48.38,31.17),"AE":(23.42,53.85),
    "GB":(55.38,-3.44),"US":(37.09,-95.71),"UY":(-32.52,-55.77),"UZ":(41.38,64.59),
    "VE":(6.42,-66.59),"VN":(14.06,108.28),"YE":(15.55,48.52),"ZM":(-13.13,27.85),
    "ZW":(-19.02,29.15),
}

# ── DB ───────────────────────────────────────────────────────────────────────
import sqlite3

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Helpers geo ──────────────────────────────────────────────────────────────
def geolocate_rows(rows):
    """
    Recibe lista de (ip, username).
    Devuelve dict agrupado por país.
    DEDUPLICADO: máximo una entrada por (ip, username).
    """
    reader = get_geo_reader()
    if not reader:
        return {}, 0

    seen    = set()   # evita duplicar el mismo (ip, username)
    points  = {}
    skipped = 0

    for ip, username in rows:
        key = (ip, username)
        if key in seen:
            continue
        seen.add(key)

        try:
            resp = reader.country(ip)
            iso  = resp.country.iso_code
            name = resp.country.name or iso
            if iso not in COUNTRY_COORDS:
                skipped += 1
                continue
            lat, lon = COUNTRY_COORDS[iso]
            jlat = round(lat + random.uniform(-2.5, 2.5), 4)
            jlon = round(lon + random.uniform(-2.5, 2.5), 4)
            if iso not in points:
                points[iso] = {"iso": iso, "country": name,
                               "lat": lat, "lon": lon, "entries": []}
            points[iso]["entries"].append(
                {"ip": ip, "username": username, "lat": jlat, "lon": jlon}
            )
        except Exception:
            skipped += 1

    return points, skipped

# ── Rutas ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("map.html")

# ── Stats ────────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    try:
        conn  = get_db()
        total = conn.execute("SELECT COUNT(*) FROM data").fetchone()[0]
        uniq  = conn.execute("SELECT COUNT(DISTINCT ip) FROM data").fetchone()[0]
        conn.close()
        return jsonify({"total": total, "unique_ips": uniq})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── IPs generales (con dedup por ip+username) ────────────────────────────────
@app.route("/api/ips")
def api_ips():
    c_filter = request.args.get("country", "").upper()
    q_filter = request.args.get("q", "").strip().lower()
    limit    = min(int(request.args.get("limit", 5000)), 50000)

    try:
        conn = get_db()
        if q_filter:
            # DISTINCT ip,username desde la subquery para evitar dupes
            rows = conn.execute("""
                SELECT ip, username FROM (
                    SELECT DISTINCT ip, username FROM data
                    WHERE LOWER(username) LIKE ?
                ) LIMIT ?
            """, (f"%{q_filter}%", limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT ip, username FROM (
                    SELECT DISTINCT ip, username FROM data
                ) LIMIT ?
            """, (limit,)).fetchall()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    points, skipped = geolocate_rows(rows)

    if c_filter:
        points = {k: v for k, v in points.items() if k == c_filter}

    return jsonify({"points": list(points.values()),
                    "skipped": skipped, "total": len(rows)})

# ── Búsqueda de usernames ────────────────────────────────────────────────────
@app.route("/api/search-users")
def search_users():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 1:
        return jsonify([])
    try:
        conn = get_db()
        rows = conn.execute("""
            SELECT username,
                   COUNT(DISTINCT ip)  AS ip_count,
                   COUNT(*)            AS total_records
            FROM data
            WHERE LOWER(username) LIKE ?
            GROUP BY username
            ORDER BY ip_count DESC
            LIMIT 30
        """, (f"%{q}%",)).fetchall()
        conn.close()
        return jsonify([{
            "username": r["username"],
            "ip_count": r["ip_count"],
            "total":    r["total_records"]
        } for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── IPs de un usuario específico (dedup: una entrada por ip única del actor) ─
@app.route("/api/user-ips/<path:username>")
def user_ips(username):
    try:
        conn = get_db()
        # DISTINCT ip: si el actor tiene la misma IP 500 veces → 1 pin
        rows = conn.execute(
            "SELECT DISTINCT ip, username FROM data WHERE username = ?",
            (username,)
        ).fetchall()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    points, _ = geolocate_rows(rows)
    return jsonify({"username": username, "points": list(points.values())})

# ── Detalle IP con ipinfo ────────────────────────────────────────────────────
@app.route("/api/ip-detail/<path:ip>")
def ip_detail(ip):
    if not re.match(r'^[\d\.a-fA-F:]+$', ip):
        return jsonify({"error": "IP inválida"}), 400
    try:
        data = {}
        if IPINFO_TOKEN and req_lib:
            r    = req_lib.get(f"https://ipinfo.io/{ip}",
                               params={"token": IPINFO_TOKEN}, timeout=5)
            data = r.json()
        else:
            data = {"ip": ip, "error": "Sin token ipinfo configurado"}

        # Usuarios de esa IP en la DB (sin duplicar username)
        conn  = get_db()
        users = conn.execute(
            "SELECT DISTINCT username, hostname FROM data WHERE ip = ?", (ip,)
        ).fetchall()
        conn.close()
        data["db_users"] = [
            {"username": u["username"], "hostname": u["hostname"]} for u in users
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Países presentes ─────────────────────────────────────────────────────────
@app.route("/api/countries")
def api_countries():
    try:
        conn = get_db()
        # DISTINCT ip para no inflar conteos por duplicados
        rows = conn.execute(
            "SELECT DISTINCT ip FROM data LIMIT 30000"
        ).fetchall()
        conn.close()
    except Exception as e:
        return jsonify([])

    reader  = get_geo_reader()
    if not reader:
        return jsonify([])

    counter = {}
    for (ip,) in rows:
        try:
            resp = reader.country(ip)
            iso  = resp.country.iso_code
            name = resp.country.name or iso
            entry = counter.get(iso, {"iso": iso, "name": name, "count": 0})
            entry["count"] += 1
            counter[iso] = entry
        except Exception:
            pass

    return jsonify(sorted(counter.values(), key=lambda x: -x["count"]))

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"  IP Intelligence Map")
    print(f"  DB     : {DB_PATH}")
    print(f"  GeoIP  : {MMDB_PATH}")
    print(f"  ipinfo : {'✓ configurado' if IPINFO_TOKEN else '✗ sin token (detalle desactivado)'}")
    print(f"  URL    : http://127.0.0.1:5000")
    print(f"{'='*50}\n")
    app.run(debug=False, host='127.0.0.1', port=5000)
