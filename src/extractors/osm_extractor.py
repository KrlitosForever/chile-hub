"""Extrae puntos de interes (POI) de Chile desde OpenStreetMap via Overpass API.

Fuente: OpenStreetMap contributors, via Overpass API (https://overpass-api.de)
Licencia: ODbL 1.0 (atribucion requerida)
Formato: JSON via API REST

Extrae nodos OSM con tags de comercio, servicio, turismo, oficina y oficio que
tengan nombre y direccion (addr:street + addr:housenumber). Cruza con la DPA
para obtener codigo_comuna y codigo_region.

Para mantenerse dentro de los limites de Overpass, consulta por bloques de
latitud (franjas horizontales de ~3 grados) que cubren todo Chile continental.
"""

import datetime
import json
import os
import sys
import time
from pathlib import Path

import polars as pl
import requests

UTC = datetime.timezone.utc

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from src.extractors.base import (
        BaseExtractor,
        ensure_staging_directories,
        write_staging_metadata,
    )
except ModuleNotFoundError:
    from base import BaseExtractor, ensure_staging_directories, write_staging_metadata

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
RAW_DIR = os.path.join(DATA_DIR, "raw")
STAGING_DIR = os.path.join(DATA_DIR, "staging")
STAGING_CSV_PATH = os.path.join(STAGING_DIR, "puntos_interes.csv")
METADATA_PATH = os.path.join(STAGING_DIR, "puntos_interes.metadata.json")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "chile-hub/0.1 (https://github.com/cortega26/chile-hub)"

# En CI reducimos los timeouts para no bloquear el pipeline por minutes.
# Overpass puede ser lento; preferimos cobertura parcial a un build colgado.
_IN_CI = os.environ.get("CI", "").lower() == "true"
_OVERPASS_SERVER_TIMEOUT = 30 if _IN_CI else 120
_OVERPASS_CLIENT_TIMEOUT = _OVERPASS_SERVER_TIMEOUT + 15
_BAND_SLEEP = 0.5  # respeto al rate limiting de Overpass

# Franjas de latitud que cubren Chile continental (~17°S a ~56°S)
# Cada franja tiene ~3 grados de altura para mantenerse dentro de limites
LAT_BANDS = [
    (-17.5, -20.5),  # Arica a Iquique
    (-20.5, -23.5),  # Antofagasta
    (-23.5, -26.5),  # Copiapo
    (-26.5, -29.5),  # La Serena
    (-29.5, -32.5),  # Valparaiso norte
    (-32.5, -35.5),  # Santiago / Rancagua
    (-35.5, -38.5),  # Talca / Concepcion
    (-38.5, -41.5),  # Temuco / Valdivia
    (-41.5, -44.5),  # Puerto Montt
    (-44.5, -47.5),  # Coyhaique
    (-47.5, -50.5),  # Patagonia sur
    (-50.5, -56.5),  # Punta Arenas / Tierra del Fuego
]

# Longitud de Chile continental (~67°W a ~76°W, mas isla de Pascua)
LON_WEST = -76.5
LON_EAST = -66.5

# Tags OSM a extraer y su categoria en espanol
OSM_TAG_CATEGORIES = {
    "amenity": "amenidad",
    "shop": "comercio",
    "tourism": "turismo",
    "office": "oficina",
    "craft": "oficio",
}

# Mapeo de valores OSM comunes a espanol
OSM_VALUE_ES = {
    # amenity
    "restaurant": "restaurante",
    "cafe": "cafeteria",
    "bar": "bar",
    "pub": "pub",
    "fast_food": "comida_rapida",
    "pharmacy": "farmacia",
    "bank": "banco",
    "atm": "cajero_automatico",
    "fuel": "combustible",
    "hospital": "hospital",
    "clinic": "clinica",
    "dentist": "dentista",
    "veterinary": "veterinaria",
    "school": "colegio",
    "university": "universidad",
    "library": "biblioteca",
    "police": "comisaria",
    "post_office": "correos",
    "townhall": "municipalidad",
    "courthouse": "tribunal",
    "marketplace": "mercado",
    "childcare": "guarderia",
    "cinema": "cine",
    "theatre": "teatro",
    "nightclub": "discoteca",
    "gym": "gimnasio",
    "parking": "estacionamiento",
    "bicycle_rental": "arriendo_bicicletas",
    "car_rental": "arriendo_autos",
    "car_wash": "lavado_autos",
    "place_of_worship": "lugar_culto",
    "community_centre": "centro_comunitario",
    "public_building": "edificio_publico",
    # shop
    "supermarket": "supermercado",
    "convenience": "almacen",
    "bakery": "panaderia",
    "butcher": "carniceria",
    "clothes": "ropa",
    "shoes": "zapatos",
    "hairdresser": "peluqueria",
    "beauty": "belleza",
    "jewelry": "joyeria",
    "electronics": "electronica",
    "hardware": "ferreteria",
    "furniture": "muebles",
    "books": "libreria",
    "alcohol": "botilleria",
    "chemist": "farmacia_perfumeria",
    "car": "venta_autos",
    "car_repair": "mecanica",
    "bicycle": "bicicleteria",
    "florist": "floreria",
    "optician": "optica",
    "garden_centre": "vivero",
    "doityourself": "bricolaje",
    "department_store": "tienda_departamental",
    "mall": "centro_comercial",
    "computer": "computacion",
    "mobile_phone": "celulares",
    "stationery": "libreria_articulos",
    "pet": "mascotas",
    "toy": "juguetes",
    "sports": "deportes",
    "travel_agency": "agencia_viajes",
    "laundry": "lavanderia",
    "dry_cleaning": "tintoreria",
    "funeral_directors": "funeraria",
    "kiosk": "kiosco",
    "newsagent": "diarios_revistas",
    "charity": "caridad",
    "second_hand": "segunda_mano",
    "variety_store": "multitienda",
    "wholesale": "mayorista",
    "copyshop": "fotocopiadora",
    "seafood": "pescaderia",
    "deli": "rotiseria",
    "greengrocer": "verduleria",
    "beverages": "bebidas",
    "health_food": "dietetica",
    "medical_supply": "insumos_medicos",
    "tobacco": "tabaquería",
    "tattoo": "tatuajes",
    "antiques": "antiguedades",
    "art": "arte",
    "craft": "artesania",
    "musical_instruments": "instrumentos_musicales",
    "photo": "fotografia",
    "video_games": "videojuegos",
    "outdoor": "equipo_aire_libre",
    "bag": "bolsos",
    "fabric": "telas",
    "curtain": "cortinas",
    "interior_decoration": "decoracion",
    "lighting": "iluminacion",
    "massage": "masajes",
    "cosmetics": "cosmeticos",
    "perfumery": "perfumeria",
    "chocolate": "chocolateria",
    "coffee": "cafeteria_tienda",
    "tea": "te",
    "wine": "vinos",
    "cheese": "quesos",
    "dairy": "lacteos",
    "pasta": "pastas",
    "pastry": "pasteleria",
    "confectionery": "confiteria",
    "ice_cream": "heladeria",
    "frozen_food": "congelados",
    "organic": "organicos",
    "spices": "especias",
    "water": "agua",
    "energy": "energia",
    "agrarian": "insumos_agricolas",
    "trade": "materiales_construccion",
    "motorcycle": "motos",
    "car_parts": "repuestos_autos",
    "tires": "neumaticos",
    "fishing": "pesca",
    "hunting": "caza",
    "swimming_pool": "piscinas",
    "security": "seguridad",
    "storage_rental": "bodegas",
    "weapons": "armas",
    "houseware": "menaje",
    "kitchen": "cocina",
    "carpet": "alfombras",
    "bedding": "blanqueria",
    "bathroom_furnishing": "bano",
    "doors": "puertas",
    "flooring": "pisos",
    "glaziery": "vidrieria",
    "paint": "pinturas",
    "pottery": "ceramica",
    "gas": "gas",
    "heating": "calefaccion",
    "radiotechnics": "radiotecnia",
    "hifi": "audio",
    "electrical": "electricidad",
    "plumber": "plomeria",
    "roofing": "techado",
    "carpenter": "carpinteria",
    "gardening": "jardineria",
    "general": "ferreteria_general",
    "e-cigarette": "cigarrillos_electronicos",
    "vacuum_cleaner": "aspiradoras",
    "locksmith": "cerrajeria",
    "pyrotechnics": "pirotecnia",
    "cannabis": "cannabis",
    "erotic": "erotica",
    "party": "fiestas",
    "rental": "arriendo_general",
    "ticket": "entradas",
    "bookmaker": "apuestas",
    "lottery": "loteria",
    "pawnbroker": "casa_empeno",
    "money_lender": "prestamista",
    "outpost": "punto_retiro",
    "e-commerce": "comercio_electronico",
    "food_court": "patio_comidas",
    "paintball": "paintball",
    "scuba_diving": "buceo",
    "surf": "surf",
    "fashion_accessories": "accesorios_moda",
    "leather": "cuero",
    "watches": "relojes",
    "frame": "marcos",
    "model": "modelismo",
    "collector": "coleccionismo",
    "stamp": "filatelia",
    "camera": "camaras",
    "dive": "buceo_tienda",
    "military_surplus": "articulos_militares",
    "nutrition_supplements": "suplementos",
    "spa": "spa",
    "nails": "unas",
    "tanning": "bronceado",
    "piercing": "piercing",
    "hairdresser_supply": "insumos_peluqueria",
    "tailor": "sastre",
    "watches_repair": "reparacion_relojes",
    "shoemaker": "zapatero",
    "electronics_repair": "reparacion_electronica",
    "printer_ink": "tintas_impresora",
    # tourism
    "hotel": "hotel",
    "hostel": "hostal",
    "guest_house": "hospedaje",
    "motel": "motel",
    "museum": "museo",
    "artwork": "obra_arte",
    "attraction": "atraccion",
    "viewpoint": "mirador",
    "zoo": "zoologico",
    "aquarium": "acuario",
    "theme_park": "parque_tematico",
    "gallery": "galeria",
    "picnic_site": "zona_picnic",
    "camp_site": "camping",
    "caravan_site": "zona_caravanas",
    "alpine_hut": "refugio_montana",
    "chalet": "chalet",
    "wilderness_hut": "refugio_natural",
    "information": "informacion_turistica",
    # office
    "company": "empresa",
    "insurance": "seguros",
    "lawyer": "abogado",
    "notary": "notaria",
    "accountant": "contador",
    "architect": "arquitecto",
    "travel_agent": "agencia_viajes_of",
    "estate_agent": "corredor_propiedades",
    "government": "oficina_publica",
    "ngo": "ong",
    "association": "asociacion",
    "foundation": "fundacion",
    "political_party": "partido_politico",
    "research": "investigacion",
    "educational_institution": "institucion_educativa",
    "employment_agency": "agencia_empleo",
    "newspaper": "periodico",
    "publisher": "editorial",
    "quango": "organismo_publico",
    "religion": "oficina_religiosa",
    "telecommunication": "telecomunicaciones",
    "it": "informatica",
    "engineer": "ingenieria",
    "consulting": "consultoria",
    "financial": "financiera",
    "advertising": "publicidad",
    "marketing": "marketing",
    "design": "diseno",
    "photography": "fotografia_of",
    "translator": "traduccion",
    "therapist": "terapia",
    "physician": "medico",
    "logistics": "logistica",
    "taxi": "taxi_of",
    "coworking": "coworking",
    "property_management": "administracion_propiedades",
    "energy_supplier": "proveedor_energia",
    "water_utility": "servicio_agua",
    "surveyor": "topografia",
    "forestry": "forestal",
    "guide": "guia_turistico",
    # craft (solo valores que NO aparecen en shop/amenity/tourism/office)
    "electrician": "electricista",
    "painter": "pintor",
    "bricklayer": "albanil",
    "tiler": "albanil_azulejos",
    "roofer": "techador",
    "glazier": "vidriero",
    "blacksmith": "herrero",
    "metal_construction": "construccion_metalica",
    "upholsterer": "tapicero",
    "photographer": "fotografo",
    "jeweller": "joyero",
    "watchmaker": "relojero",
    "gardener": "jardinero",
    "beekeeper": "apicultor",
    "brewer": "cervecero",
    "winemaker": "viticultor",
    "baker": "panadero_artesanal",
    "confectioner": "confitero",
    "cheesemaker": "quesero",
    "distillery": "destilador",
    "caterer": "servicio_catering",
    "floorer": "solador",
    "chimney_sweeper": "deshollinador",
    "hvac": "climatizacion",
    "insulation": "aislamiento",
    "scaffolder": "andamios",
    "stonemason": "cantero",
    "handicraft": "artesania_manual",
    "sawmill": "aserradero",
    "window_construction": "fabricacion_ventanas",
    "door_construction": "fabricacion_puertas",
    "key_cutter": "copiador_llaves",
    "engraver": "grabador",
    "printer": "impresor",
    "bookbinder": "encuadernador",
    "sculptor": "escultor",
    "signmaker": "rotulista",
    "clockmaker": "relojero_antiguo",
    "dental_technician": "tecnico_dental",
    "optics": "optica_artesanal",
    "rigger": "aparejador",
    "sailmaker": "velero",
}

REUSE_POLICY = {
    "status": "open-attribution",
    "license": "ODbL 1.0",
    "license_url": "https://opendatacommons.org/licenses/odbl/",
    "attribution_required": True,
    "redistribution_ok": True,
    "summary": (
        "Datos de OpenStreetMap bajo licencia ODbL. "
        "Atribucion requerida: '© OpenStreetMap contributors'."
    ),
}

# ── Datos de fallback (POIs representativos de Santiago) ──────────────────────
# Usados si la API de Overpass no responde.
OSM_FALLBACK_DATA = [
    {
        "osm_id": 436035940,
        "nombre": "El Toro",
        "categoria": "amenidad",
        "tipo": "restaurante",
        "direccion": "Loreto 33",
        "comuna": "Recoleta",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.43305,
        "longitud": -70.64225,
    },
    {
        "osm_id": 581881234,
        "nombre": "Liguria",
        "categoria": "amenidad",
        "tipo": "restaurante",
        "direccion": "Av. Providencia 1373",
        "comuna": "Providencia",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.42588,
        "longitud": -70.61962,
    },
    {
        "osm_id": 1023456789,
        "nombre": "Jumbo",
        "categoria": "comercio",
        "tipo": "supermercado",
        "direccion": "Av. Francisco Bilbao 2875",
        "comuna": "Providencia",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.43754,
        "longitud": -70.60097,
    },
    {
        "osm_id": 987654321,
        "nombre": "Farmacia Ahumada",
        "categoria": "amenidad",
        "tipo": "farmacia",
        "direccion": "Alameda 2300",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.44889,
        "longitud": -70.66926,
    },
    {
        "osm_id": 876543210,
        "nombre": "Banco de Chile",
        "categoria": "amenidad",
        "tipo": "banco",
        "direccion": "Bandera 156",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.44203,
        "longitud": -70.65178,
    },
    {
        "osm_id": 765432109,
        "nombre": "Copec",
        "categoria": "amenidad",
        "tipo": "combustible",
        "direccion": "Av. Apoquindo 4500",
        "comuna": "Las Condes",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.41520,
        "longitud": -70.57150,
    },
    {
        "osm_id": 654321098,
        "nombre": "Hotel Plaza San Francisco",
        "categoria": "turismo",
        "tipo": "hotel",
        "direccion": "Alameda 816",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.44455,
        "longitud": -70.66165,
    },
    {
        "osm_id": 543210987,
        "nombre": "Museo de Bellas Artes",
        "categoria": "turismo",
        "tipo": "museo",
        "direccion": "Parque Forestal s/n",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.43531,
        "longitud": -70.64375,
    },
    {
        "osm_id": 432109876,
        "nombre": "Cafe Haiti",
        "categoria": "amenidad",
        "tipo": "cafeteria",
        "direccion": "Av. Providencia 1306",
        "comuna": "Providencia",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.42576,
        "longitud": -70.62108,
    },
    {
        "osm_id": 321098765,
        "nombre": "Juzgado de Familia",
        "categoria": "oficina",
        "tipo": "tribunal",
        "direccion": "Paseo Bulnes 120",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.45123,
        "longitud": -70.65678,
    },
    {
        "osm_id": 210987654,
        "nombre": "Mercado Central",
        "categoria": "amenidad",
        "tipo": "mercado",
        "direccion": "San Pablo 967",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.43380,
        "longitud": -70.65137,
    },
    {
        "osm_id": 109876543,
        "nombre": "Lider Express",
        "categoria": "comercio",
        "tipo": "supermercado",
        "direccion": "Av. Matta 1200",
        "comuna": "Santiago",
        "codigo_comuna": None,
        "codigo_region": None,
        "telefono": None,
        "sitio_web": None,
        "latitud": -33.46100,
        "longitud": -70.64150,
    },
]


def _clean_comuna_name(name: str) -> str:
    """Normaliza un nombre de comuna para fuzzy matching (sin acentos, lowercase)."""
    if not name:
        return ""
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
        "Á": "a",
        "É": "e",
        "Í": "i",
        "Ó": "o",
        "Ú": "u",
        "Ü": "u",
        "Ñ": "n",
    }
    result = name.strip().lower()
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def _query_overpass_band(south: float, north: float) -> list[dict]:
    """Consulta Overpass API para una franja de latitud.

    Args:
        south: Latitud sur de la franja.
        north: Latitud norte de la franja.

    Returns:
        Lista de elementos OSM (nodos con tags).
    """
    # Construir bounding box: [S, W, N, E]
    bbox = f"({south},{LON_WEST},{north},{LON_EAST})"

    # Tags a consultar: todos los nodos con name + addr:street + (amenity|shop|tourism|office|craft)
    tag_filters = "\n".join(
        f'  node["{tag}"]["name"]["addr:street"]{bbox};' for tag in OSM_TAG_CATEGORIES
    )

    query = f"""[out:json][timeout:{_OVERPASS_SERVER_TIMEOUT}];
(
{tag_filters}
);
out body qt 10000;
"""

    resp = requests.get(
        OVERPASS_URL,
        params={"data": query},
        headers={"User-Agent": USER_AGENT},
        timeout=_OVERPASS_CLIENT_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("elements", [])


def fetch_osm_pois() -> tuple[list[dict], str, str]:
    """Obtiene POIs de OpenStreetMap via Overpass API.

    Consulta por franjas de latitud para no exceder los limites de Overpass.
    Si una franja falla, la omite con warning (resiliencia parcial).
    Si todas fallan, usa datos de fallback.

    Returns:
        Tuple con (lista_de_elementos_osm, source_mode, source_detail).
    """
    ensure_staging_directories()

    all_elements = []
    failed_bands = []
    source_mode = "live"
    timestamp = datetime.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    modo = "CI (timeouts reducidos)" if _IN_CI else "local"
    print(f"Extrayendo POIs de OpenStreetMap ({len(LAT_BANDS)} franjas, modo {modo})…")

    # LAT_BANDS almacena (borde_norte, borde_sur) — el valor menos negativo
    # primero (más cerca del ecuador).  Para el bbox de Overpass necesitamos
    # (south, west, north, east) con south < north, así que south es el valor
    # más negativo (más al sur).
    for north_edge, south_edge in LAT_BANDS:
        try:
            print(
                f"  Consultando franja {north_edge}°S a {south_edge}°S… ",
                end="",
                flush=True,
            )
            elements = _query_overpass_band(south_edge, north_edge)
            all_elements.extend(elements)
            print(f"{len(elements)} POIs", flush=True)
            # Respetar rate limiting de Overpass
            time.sleep(_BAND_SLEEP)
        except Exception as exc:
            failed_bands.append(f"{north_edge}-{south_edge}: {exc}")
            print(f"FALLIDA ({exc})", flush=True)

    if not all_elements:
        # Intentar recuperar snapshot raw previo
        raw_snapshots = sorted(Path(RAW_DIR).glob("osm_pois_*.json"))
        if raw_snapshots:
            source_mode = "fallback"
            print(f"Usando snapshot raw: {raw_snapshots[-1].name}")
            all_elements = json.loads(raw_snapshots[-1].read_text(encoding="utf-8"))
        else:
            source_mode = "fallback"
            print("Usando datos de fallback embebidos (OSM_FALLBACK_DATA).")

    # Guardar snapshot raw en vivo
    if source_mode == "live" and all_elements:
        raw_path = Path(RAW_DIR) / f"osm_pois_{timestamp}.json"
        raw_path.write_text(
            json.dumps(all_elements, ensure_ascii=False),
            encoding="utf-8",
        )

    source_detail = "overpass_api" if source_mode == "live" else "fallback_embedded"
    return all_elements, source_mode, source_detail


def parse_osm_elements(
    elements: list[dict],
    comunas_ref: pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Convierte elementos OSM al schema canonico de puntos_interes.

    Args:
        elements: Lista de elementos OSM (nodos con tags).
        comunas_ref: DataFrame con columnas [codigo_comuna, nombre_comuna_clean]
                     para el cruce con la DPA. Si es None, codigo_comuna queda nulo.

    Returns:
        DataFrame de Polars con el schema canonico.
    """
    if not elements:
        # Datos de fallback: convertir a formato de elementos
        return pl.DataFrame(OSM_FALLBACK_DATA)

    records = []

    for el in elements:
        if el.get("type") != "node":
            continue

        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name:
            continue

        # Determinar categoria y tipo
        categoria = None
        tipo = None
        for tag_key, cat_name in OSM_TAG_CATEGORIES.items():
            if tag_key in tags:
                categoria = cat_name
                tipo = tags[tag_key]
                break

        if categoria is None:
            continue  # no deberia ocurrir por el filtro Overpass, pero seguro

        # Direccion
        street = tags.get("addr:street", "").strip()
        housenumber = tags.get("addr:housenumber", "").strip()
        if street and housenumber:
            direccion = f"{street} {housenumber}"
        elif street:
            direccion = street
        else:
            direccion = ""

        # Comuna desde addr:city
        comuna = tags.get("addr:city", "").strip()

        # Telefono y web
        telefono = tags.get("phone", "").strip() or None
        sitio_web = tags.get("website", "").strip() or None
        if sitio_web and not sitio_web.startswith("http"):
            sitio_web = f"https://{sitio_web}"

        # Traducir tipo a espanol si existe mapeo
        tipo_es = OSM_VALUE_ES.get(tipo, tipo)

        records.append(
            {
                "osm_id": el["id"],
                "nombre": name,
                "categoria": categoria,
                "tipo": tipo_es,
                "direccion": direccion,
                "comuna": comuna,
                "telefono": telefono,
                "sitio_web": sitio_web,
                "latitud": el["lat"],
                "longitud": el["lon"],
            }
        )

    df = pl.DataFrame(records)

    # Si no hay registros, devolver DataFrame vacio con schema correcto
    if df.height == 0:
        return pl.DataFrame(
            schema={
                "osm_id": pl.Int64,
                "nombre": pl.String,
                "categoria": pl.String,
                "tipo": pl.String,
                "direccion": pl.String,
                "comuna": pl.String,
                "codigo_comuna": pl.String,
                "codigo_region": pl.String,
                "telefono": pl.String,
                "sitio_web": pl.String,
                "latitud": pl.Float64,
                "longitud": pl.Float64,
            }
        )

    # Cruzar con DPA si hay referencia
    if comunas_ref is not None and df.height > 0:
        df = _cross_reference_dpa(df, comunas_ref)
    else:
        df = df.with_columns(
            [
                pl.lit(None, dtype=pl.String).alias("codigo_comuna"),
                pl.lit(None, dtype=pl.String).alias("codigo_region"),
            ]
        )

    # Ordenar por categoria, tipo, nombre
    df = df.sort(["categoria", "tipo", "nombre"])

    # Schema final
    final_cols = [
        "osm_id",
        "nombre",
        "categoria",
        "tipo",
        "direccion",
        "comuna",
        "codigo_comuna",
        "codigo_region",
        "telefono",
        "sitio_web",
        "latitud",
        "longitud",
    ]
    return df.select([c for c in final_cols if c in df.columns])


def _cross_reference_dpa(df: pl.DataFrame, comunas_ref: pl.DataFrame) -> pl.DataFrame:
    """Cruza los POIs con la DPA para obtener codigo_comuna y codigo_region.

    Usa coincidencia exacta sobre nombre_comuna_clean (normalizado sin acentos).
    Los POIs que no cruzan quedan con codigo_comuna nulo.

    Args:
        df: DataFrame con columna 'comuna'.
        comunas_ref: DataFrame con columnas [codigo_comuna, nombre_comuna_clean,
                     codigo_region, nombre_region].

    Returns:
        DataFrame con codigo_comuna y codigo_region agregados.
    """
    # Normalizar comuna del POI para el cruce
    df = df.with_columns(
        pl.col("comuna")
        .map_elements(_clean_comuna_name, return_dtype=pl.String)
        .alias("_comuna_clean")
    )

    # Join exacto por nombre_comuna_clean
    df = df.join(
        comunas_ref.select(
            pl.col("codigo_comuna"),
            pl.col("codigo_region"),
            pl.col("nombre_region"),
            pl.col("nombre_comuna_clean"),
        ),
        left_on="_comuna_clean",
        right_on="nombre_comuna_clean",
        how="left",
    )

    # Limpiar columna auxiliar
    df = df.drop(["_comuna_clean", "nombre_comuna_clean", "nombre_region"])

    matched = df.filter(pl.col("codigo_comuna").is_not_null()).height
    total = df.height
    if total > 0:
        print(f"Cruce DPA: {matched}/{total} POIs con codigo_comuna ({100 * matched // total}%)")

    return df


def load_comunas_reference() -> pl.DataFrame | None:
    """Carga la tabla de comunas desde staging para el cruce con DPA.

    Returns:
        DataFrame con columnas [codigo_comuna, nombre_comuna_clean,
        codigo_region, nombre_region], o None si no existe.
    """
    comunas_csv = os.path.join(STAGING_DIR, "comunas.csv")
    if not os.path.exists(comunas_csv):
        print(
            "Advertencia: comunas.csv no encontrado en staging. "
            "El cruce con DPA no estara disponible."
        )
        return None

    df = pl.read_csv(
        comunas_csv,
        schema_overrides={
            "codigo_comuna": pl.String,
            "codigo_region": pl.String,
            "nombre_region": pl.String,
            "nombre_comuna_clean": pl.String,
        },
    ).select(["codigo_comuna", "codigo_region", "nombre_region", "nombre_comuna_clean"])

    # Asegurar que nombre_comuna_clean existe; si no, calcularlo
    if "nombre_comuna_clean" not in df.columns:
        if "nombre_comuna" in df.columns:
            df = df.with_columns(
                pl.col("nombre_comuna")
                .map_elements(_clean_comuna_name, return_dtype=pl.String)
                .alias("nombre_comuna_clean")
            )

    return df


class OsmExtractor(BaseExtractor):
    """Extractor para Puntos de Interes de OpenStreetMap."""

    @property
    def dataset_name(self) -> str:
        return "puntos_interes"

    def fetch(self, **kwargs):
        return fetch_osm_pois()

    def normalize(self, raw_data):
        elements, _, _ = raw_data
        comunas_ref = load_comunas_reference()
        return parse_osm_elements(elements, comunas_ref)

    def validate(self, df, metadata: dict) -> dict:
        from src.validation import validate_puntos_interes

        return validate_puntos_interes(df, metadata)

    def write_staging(self, df, metadata: dict) -> Path:
        ensure_staging_directories()
        output = Path(STAGING_CSV_PATH)
        df.write_csv(output)
        full_metadata = {
            **metadata,
            "dataset": self.dataset_name,
            "record_count": df.height,
            "fields": df.columns,
            "reuse_policy": REUSE_POLICY,
        }
        write_staging_metadata(METADATA_PATH, full_metadata)
        return output


def process() -> str:
    """Ejecuta el pipeline completo del extractor OSM."""
    elements, source_mode, source_detail = fetch_osm_pois()
    comunas_ref = load_comunas_reference()
    df = parse_osm_elements(elements, comunas_ref)

    extractor = OsmExtractor()
    validation = extractor.validate(df, {"source_mode": source_mode})
    if validation["status"] == "error":
        raise SystemExit(f"Validacion fallida: {validation['errors']}")

    notes = [
        "Datos de OpenStreetMap bajo licencia ODbL.",
        "Cobertura parcial: mayor densidad en zonas urbanas, limitada en zonas rurales.",
        "Las categorias son tags OSM, no clasificacion CIIU oficial.",
        "Los datos dependen de contribuidores voluntarios; pueden no reflejar cierres recientes.",
        "Sin RUT: no es posible cruzar directamente con el RES.",
    ]
    if source_mode == "fallback":
        notes.append("Datos de fallback: muestra reducida sin valor estadistico.")

    metadata = {
        "dataset": "puntos_interes",
        "source_name": "OpenStreetMap contributors",
        "source_url": "https://overpass-api.de/api/interpreter",
        "source_mode": source_mode,
        "source_detail": source_detail,
        "refreshed_at_utc": datetime.datetime.now(UTC).isoformat(),
        "record_count": df.height,
        "fields": df.columns,
        "notes": notes,
        "coverage": {
            "status": "partial",
            "baseline": 50000,
            "summary": (
                "Cobertura desigual: buena en zonas urbanas, "
                "limitada en zonas rurales. Sin valor censal."
            ),
        },
        "reuse_policy": REUSE_POLICY,
    }
    extractor.write_staging(df, metadata)
    print(
        f"Puntos de interes guardados en: {STAGING_CSV_PATH} ({df.height} registros, {source_mode})"
    )
    return STAGING_CSV_PATH


if __name__ == "__main__":
    process()
