import os
import json
import time
import random
from slugify import slugify
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types
from github import Github

# --- 1. CREDENCIALES Y CONFIGURACIÓN ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("REPO_NAME", "tu-usuario/tu-repositorio-blog")

# Script de tu red de anuncios (PropellerAds / PopAds / Adsterra)
PROPELLER_SCRIPT = """<script>(function(d,z,s){s.src='https://'+d+'/401/'+z;try{(document.body||document.documentElement).appendChild(s)}catch(e){}}('groleegni.net',1234567,document.createElement('script')))</script>"""

# Clientes API
yt_client = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
gh_client = Github(GITHUB_TOKEN)
repo = gh_client.get_repo(REPO_NAME)

REGISTRO_FILE = "procesados.json"

# --- 2. LOS 25 IDIOMAS MÁS LUCRATIVOS ---
IDIOMAS_MAXIMOS = [
    "English", "Español", "Português", "Français", "Deutsch", 
    "Italiano", "Nederlands", "Polski", "Русский", "Türkçe", 
    "日本語", "한국어", "Tiếng Việt", "Bahasa Indonesia", "ไทย", 
    "हिन्दी", "العربية", "简体中文", "繁體中文", "Svenska", 
    "Norsk", "Dansk", "Suomi", "Čeština", "Română"
]

# --- 3. LAS 100 CATEGORÍAS (SLUGS CON 'Z' AL FINAL) ---
CATEGORIAS_100 = [
    {"nicho": "Programación en Python", "slug_z": "pythonz"},
    {"nicho": "Inteligencia Artificial y Bots", "slug_z": "iaz"},
    {"nicho": "Criptomonedas y Bitcoin", "slug_z": "criptoz"},
    {"nicho": "Finanzas Personales e Inversiones", "slug_z": "finanzasz"},
    {"nicho": "Desarrollo Web Frontend", "slug_z": "webz"},
    {"nicho": "Ciberseguridad y Hacking Ético", "slug_z": "securityz"},
    {"nicho": "Marketing Digital y SEO", "slug_z": "seoz"},
    {"nicho": "E-commerce y Dropshipping", "slug_z": "ecommercez"},
    {"nicho": "Gimnasio y Calistenia", "slug_z": "fitnessz"},
    {"nicho": "Nutrición y Dieta Keto", "slug_z": "nutricionz"},
    {"nicho": "Yoga y Meditación", "slug_z": "yogaz"},
    {"nicho": "Recetas de Cocina Fácil", "slug_z": "cocinaz"},
    {"nicho": "Repostería y Panadería", "slug_z": "reposteriaz"},
    {"nicho": "Café de Especialidad y Barismo", "slug_z": "cafez"},
    {"nicho": "Coctelería y Bebidas", "slug_z": "coctelesz"},
    {"nicho": "Fotografía Digital y Edición", "slug_z": "fotoz"},
    {"nicho": "Edición de Video y Premiere", "slug_z": "videoz"},
    {"nicho": "Diseño Gráfico y Canva", "slug_z": "disenoz"},
    {"nicho": "Modelado e Impresión 3D", "slug_z": "3dz"},
    {"nicho": "Música y Producción Musical", "slug_z": "musicaz"},
    {"nicho": "Guitarra e Instrumentos", "slug_z": "guitarraz"},
    {"nicho": "Videojuegos y Gaming PC", "slug_z": "gamingz"},
    {"nicho": "Desarrollo de Videojuegos", "slug_z": "gamedevz"},
    {"nicho": "Anime y Manga", "slug_z": "animez"},
    {"nicho": "Cine y Series Review", "slug_z": "cinez"},
    {"nicho": "Jardinería y Huerto Urbano", "slug_z": "jardinz"},
    {"nicho": "Bricolaje y Carpintería", "slug_z": "bricolajez"},
    {"nicho": "Mecánica Automotriz", "slug_z": "autosz"},
    {"nicho": "Motos y Reparación", "slug_z": "motosz"},
    {"nicho": "Movilidad Eléctrica y E-bikes", "slug_z": "ebikesz"},
    {"nicho": "Viajes Económicos y Mochileros", "slug_z": "viajesz"},
    {"nicho": "Nómadas Digitales y Trabajo Remoto", "slug_z": "nomadaz"},
    {"nicho": "Idiomas e Inglés Rápido", "slug_z": "idiomasz"},
    {"nicho": "Cuidado de Perros y Mascotas", "slug_z": "perrosz"},
    {"nicho": "Cuidado Felino", "slug_z": "gatosz"},
    {"nicho": "Acuarios y Peces de Agua Dulce", "slug_z": "acuariosz"},
    {"nicho": "Moda Masculina y Estilo", "slug_z": "modaz"},
    {"nicho": "Cuidado de la Piel y Skincare", "slug_z": "skincarez"},
    {"nicho": "Maquillaje y Belleza", "slug_z": "beautyz"},
    {"nicho": "Productividad y Método Notion", "slug_z": "productividadz"},
    {"nicho": "Desarrollo Personal y Estoicismo", "slug_z": "mentez"},
    {"nicho": "Psicología Práctica", "slug_z": "psicologiaz"},
    {"nicho": "Libros y Resúmenes Literarios", "slug_z": "librosz"},
    {"nicho": "Historia Universal", "slug_z": "historiaz"},
    {"nicho": "Ciencia y Astronomía", "slug_z": "astronomiaz"},
    {"nicho": "Física y Divulgación", "slug_z": "fisicaz"},
    {"nicho": "Biología y Naturaleza", "slug_z": "biologiaz"},
    {"nicho": "Ecología y Energías Renovables", "slug_z": "solarz"},
    {"nicho": "Supervivencia y Camping", "slug_z": "outdoorz"},
    {"nicho": "Pesca Deportiva", "slug_z": "pescaz"},
    {"nicho": "Ciclismo y Montaña", "slug_z": "mtbz"},
    {"nicho": "Running y Maratonismo", "slug_z": "runningz"},
    {"nicho": "Fútbol y Análisis Táctico", "slug_z": "futbolz"},
    {"nicho": "Baloncesto y NBA", "slug_z": "basketz"},
    {"nicho": "Artes Marciales y UFC", "slug_z": "ufcz"},
    {"nicho": "Ajedrez y Estrategia", "slug_z": "ajedrezz"},
    {"nicho": "Juegos de Mesa y Rol", "slug_z": "boardgamesz"},
    {"nicho": "Coleccionismo y Antigüedades", "slug_z": "collectionz"},
    {"nicho": "Bienes Raíces e Inmuebles", "slug_z": "realestatez"},
    {"nicho": "Negocios Locales y Pymes", "slug_z": "negociosz"},
    {"nicho": "Liderazgo y Gestión de Equipos", "slug_z": "liderazgoz"},
    {"nicho": "Ventas y Negociación", "slug_z": "ventasz"},
    {"nicho": "Recursos Humanos y Empleo", "slug_z": "empleoz"},
    {"nicho": "Contabilidad y Tributación", "slug_z": "taxz"},
    {"nicho": "Derecho y Asesoría Legal", "slug_z": "legalz"},
    {"nicho": "Arquitectura e Interiorismo", "slug_z": "casaz"},
    {"nicho": "Casas Inteligentes y Domótica", "slug_z": "domoticaz"},
    {"nicho": "Electricidad y Electrónica", "slug_z": "electroz"},
    {"nicho": "Robótica y Arduino", "slug_z": "arduinofz"},
    {"nicho": "Impresión en Resina y Minis", "slug_z": "minisz"},
    {"nicho": "Tejido y Crochet", "slug_z": "crochetz"},
    {"nicho": "Costura y Confección", "slug_z": "costuraz"},
    {"nicho": "Jabones y Cosmética Natural", "slug_z": "jabonesz"},
    {"nicho": "Velas Artesanales", "slug_z": "velasz"},
    {"nicho": "Cerveza Artesanal", "slug_z": "cervezaz"},
    {"nicho": "Vinos y Enología", "slug_z": "vinoz"},
    {"nicho": "Quesos y Charcutería", "slug_z": "gourmetz"},
    {"nicho": "Barbacoa y Parrilla", "slug_z": "asadoz"},
    {"nicho": "Postres Veganos", "slug_z": "veganz"},
    {"nicho": "Huerto en Balcón", "slug_z": "urbangardenz"},
    {"nicho": "Medicina Preventiva y Salud", "slug_z": "saludz"},
    {"nicho": "Salud Mental y Ansiedad", "slug_z": "bienestarz"},
    {"nicho": "Cuidado de Bebés y Maternidad", "slug_z": "bebesz"},
    {"nicho": "Crianza Respetuosa", "slug_z": "padresz"},
    {"nicho": "Tercera Edad y Vigor", "slug_z": "seniorsz"},
    {"nicho": "Organización del Hogar", "slug_z": "homez"},
    {"nicho": "Minimalismo y Orden", "slug_z": "ordenz"},
    {"nicho": "Magia e Ilusionismo", "slug_z": "magiaz"},
    {"nicho": "Estructura de Datos y Algoritmos", "slug_z": "algoritmosz"},
    {"nicho": "Linux y SysAdmin", "slug_z": "linuxz"},
    {"nicho": "Cloud Computing (AWS/GCP)", "slug_z": "cloudz"},
    {"nicho": "Bases de Datos y SQL", "slug_z": "sqlz"},
    {"nicho": "Excel y Análisis de Datos", "slug_z": "excelz"},
    {"nicho": "Power BI y Visualización", "slug_z": "powerbiz"},
    {"nicho": "Teletrabajo y Herramientas", "slug_z": "remotoz"},
    {"nicho": "Podcast y Podcasting", "slug_z": "podcastz"},
    {"nicho": "Streaming y Twitch Setup", "slug_z": "streamz"},
    {"nicho": "Smartphones y Gadgets", "slug_z": "gadgetsz"},
    {"nicho": "Audio de Alta Fidelidad (Hi-Fi)", "slug_z": "audioz"},
    {"nicho": "Drones y Fotografía Aérea", "slug_z": "dronesz"}
]

# --- 4. FUNCIONES DEL SISTEMA ---
def cargar_historico() -> list:
    try:
        content = repo.get_contents(REGISTRO_FILE)
        return json.loads(content.decoded_content.decode('utf-8'))
    except Exception:
        return []

def guardar_historico(historico: list):
    json_data = json.dumps(historico, indent=2)
    try:
        content = repo.get_contents(REGISTRO_FILE)
        repo.update_file(content.path, "Update processed log", json_data, content.sha)
    except Exception:
        repo.create_file(REGISTRO_FILE, "Create processed log", json_data)

def generar_busqueda_ia(nicho: str) -> str:
    prompt = f"Dame 1 término de búsqueda en YouTube muy específico y tendencia sobre: '{nicho}'. Responde SOLO con el término en texto plano."
    res = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return res.text.strip().replace('"', '')

def buscar_video_yt(query: str) -> str:
    req = yt_client.search().list(q=query, part="snippet", type="video", order="relevance", maxResults=3)
    res = req.execute()
    items = res.get("items", [])
    return items[0]["id"]["videoId"] if items else None

def obtener_transcripcion(video_id: str):
    try:
        t = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en'])
        return " ".join([x['text'] for x in t])
    except Exception:
        return None

def redactar_post_ia(transcripcion: str, idioma: str) -> dict:
    prompt = f"""
    Eres un redactor SEO profesional. Genera un artículo de blog estructurado a partir de esta transcripción.
    Responde ÚNICAMENTE un JSON estricto con:
    {{
        "titulo": "Título SEO atractivo",
        "contenido_html": "Cuerpo con <h2>, <h3>, <p>, <ul>, <li>"
    }}
    Idioma de salida: {idioma}
    Transcripción: {transcripcion[:4000]}
    """
    res = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(res.text)

def publicar_en_github(slug_z: str, slug_post: str, titulo: str, cuerpo: str, idioma: str):
    html = f"""<!DOCTYPE html>
<html lang="{idioma[:2].lower()}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    {PROPELLER_SCRIPT}
</head>
<body>
    <article>
        <h1>{titulo}</h1>
        {cuerpo}
    </article>
</body>
</html>"""
    
    path = f"{slug_z}/{slugify(idioma)}/{slug_post}.html"
    try:
        repo.create_file(path, f"Post for {slug_z} ({idioma}): {slug_post}", html)
        print(f"  ✅ Publicado: {path}")
    except Exception as e:
        print(f"  ❌ Error al subir {path}: {e}")

# --- 5. BUCLE PRINCIPAL ---
def ejecutar_bot_masivo():
    historico = cargar_historico()
    
    # Toma un lote aleatorio de 5 categorías por ejecución para balancear consumo
    lote = random.sample(CATEGORIAS_100, 5)
    
    for item in lote:
        nicho = item["nicho"]
        slug_z = item["slug_z"]
        
        print(f"\n🚀 Procesando sitio: {slug_z} ({nicho})")
        
        kw = generar_busqueda_ia(nicho)
        video_id = buscar_video_yt(kw)
        
        if not video_id or video_id in historico:
            print(f"⚠️ Video omitido (duplicado o inexistente)")
            continue
            
        transcripcion = obtener_transcripcion(video_id)
        if not transcripcion:
            print(f"⚠️ Video sin transcripción disponible")
            continue
            
        # Generar las 25 versiones de idioma
        for lang in IDIOMAS_MAXIMOS:
            try:
                art = redactar_post_ia(transcripcion, lang)
                slug_post = slugify(art["titulo"])
                publicar_en_github(slug_z, slug_post, art["titulo"], art["contenido_html"], lang)
                time.sleep(1.2)  # Pausa táctica anti-rate-limit
            except Exception as err:
                print(f"  ⚠️ Falló idioma {lang}: {err}")
                continue
            
        historico.append(video_id)
        guardar_historico(historico)

if __name__ == "__main__":
    ejecutar_bot_masivo()
