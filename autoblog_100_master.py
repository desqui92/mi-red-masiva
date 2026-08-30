import os
import json
import time
import random
from slugify import slugify
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from google.genai import types
from github import Auth, Github

# --- 1. CREDENCIALES Y CONFIGURACIÓN ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("REPO_NAME", "desqui92/mi-red-masiva")

# Script de tu red de anuncios
PROPELLER_SCRIPT = """<script>(function(s){s.dataset.zone='11689215',s.src='https://n6wxm.com/vignette.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>"""

# Clientes API
yt_client = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# Autenticación actualizada para GitHub
auth = Auth.Token(GITHUB_TOKEN)
gh_client = Github(auth=auth)
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

def llamar_gemini_con_reintento(prompt: str, mime_type: str = None, retries: int = 3):
    """Maneja caídas 503 o límites de cuota reintentando con espera progresiva"""
    config = types.GenerateContentConfig(response_mime_type=mime_type) if mime_type else None
    for intento in range(retries):
        try:
            res = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            return res.text
        except Exception as e:
            print(f"    ⚠️ Reintento Gemini ({intento + 1}/{retries}) por error: {e}")
            if intento < retries - 1:
                time.sleep(6 * (intento + 1))
            else:
                raise e

def generar_busqueda_ia(nicho: str) -> str:
    prompt = f"Dame 1 término de búsqueda en YouTube muy específico y tendencia sobre: '{nicho}'. Responde SOLO con el término en texto plano."
    res_text = llamar_gemini_con_reintento(prompt)
    return res_text.strip().replace('"', '')

def buscar_videos_yt(query: str) -> list:
    """Filtra explícitamente por videos con subtítulos habilitados (videoCaption='closedCaption')"""
    try:
        req = yt_client.search().list(
            q=query, 
            part="snippet", 
            type="video", 
            videoCaption="closedCaption",
            order="relevance", 
            maxResults=5
        )
        res = req.execute()
        items = res.get("items", [])
        return [item["id"]["videoId"] for item in items]
    except Exception as e:
        print(f"    Error buscando en YouTube: {e}")
        return []

def obtener_transcripcion(video_id: str):
    """Busca transcripciones con soporte fallback directo"""
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id, languages=['es', 'en', 'es-419', 'en-US'])
        return " ".join([x['text'] for x in data])
    except Exception:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for t in transcript_list:
                data = t.fetch()
                return " ".join([x['text'] for x in data])
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
    res_text = llamar_gemini_con_reintento(prompt, mime_type="application/json")
    return json.loads(res_text)

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
        try:
            existing_file = repo.get_contents(path)
            repo.update_file(path, f"Update post {slug_post}", html, existing_file.sha)
            print(f"    Publicado/Actualizado: {path}")
        except Exception:
            repo.create_file(path, f"Post for {slug_z} ({idioma}): {slug_post}", html)
            print(f"    Publicado: {path}")
    except Exception as e:
        print(f"    Error al subir {path}: {e}")

def generar_portada_index():
    grid_items = ""
    for cat in CATEGORIAS_100:
        nicho = cat["nicho"]
        slug_z = cat["slug_z"]
        grid_items += f"""
        <a href="/{slug_z}/" class="card">
            <h2>{nicho}</h2>
            <span class="badge">+{slug_z}</span>
        </a>
        """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfoZ — Tu Red de Conocimiento Global</title>
    {PROPELLER_SCRIPT}
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --accent: #38bdf8;
            --border: #334155;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 2rem 1rem; line-height: 1.5; }}
        header {{ text-align: center; max-width: 800px; margin: 0 auto 3rem; }}
        h1 {{ font-size: 2.5rem; color: var(--accent); margin-bottom: 0.5rem; }}
        p {{ color: #94a3b8; font-size: 1.1rem; }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); 
            gap: 1rem; 
            max-width: 1200px; 
            margin: 0 auto; 
        }}
        .card {{ 
            background: var(--card-bg); 
            border: 1px solid var(--border); 
            padding: 1.25rem; 
            border-radius: 12px; 
            text-decoration: none; 
            color: inherit; 
            transition: transform 0.2s, border-color 0.2s; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between; 
        }}
        .card:hover {{ transform: translateY(-3px); border-color: var(--accent); }}
        .card h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.75rem; }}
        .badge {{ font-size: 0.75rem; color: var(--accent); font-weight: 700; text-transform: uppercase; }}
        footer {{ text-align: center; margin-top: 4rem; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <header>
        <h1>InfoZ</h1>
        <p>Explorá guías, tutoriales y análisis en más de 100 nichos especializados.</p>
    </header>
    
    <main class="grid">
        {grid_items}
    </main>

    <footer>
        <p>&copy; InfoZ Network — Todos los derechos reservados.</p>
    </footer>
</body>
</html>"""

    try:
        existing_file = repo.get_contents("index.html")
        repo.update_file("index.html", "Update index page", html, existing_file.sha)
        print("    Portada index.html actualizada")
    except Exception:
        repo.create_file("index.html", "Create index page", html)
        print("    Portada index.html creada")

# --- 5. BUCLE PRINCIPAL ---
def ejecutar_bot_masivo():
    historico = cargar_historico()
    lote = random.sample(CATEGORIAS_100, 5)
    
    for item in lote:
        nicho = item["nicho"]
        slug_z = item["slug_z"]
        
        print(f"\nProcesando sitio: {slug_z} ({nicho})")
        
        try:
            kw = generar_busqueda_ia(nicho)
            video_ids = buscar_videos_yt(kw)
            
            if not video_ids:
                print(f"No se encontraron videos aptos para la búsqueda: {kw}")
                continue
                
            video_id = None
            transcripcion = None
            
            for vid in video_ids:
                if vid in historico:
                    continue
                txt = obtener_transcripcion(vid)
                if txt:
                    video_id = vid
                    transcripcion = txt
                    break
            
            if not video_id or not transcripcion:
                print(f"Ninguno de los videos probados tenía transcripción ejecutable")
                continue
                
            print(f"Video seleccionado: {video_id} - Generando entradas...")

            for lang in IDIOMAS_MAXIMOS:
                try:
                    art = redactar_post_ia(transcripcion, lang)
                    slug_post = slugify(art["titulo"])
                    publicar_en_github(slug_z, slug_post, art["titulo"], art["contenido_html"], lang)
                    time.sleep(1.2)
                except Exception as err:
                    print(f"    Falló idioma {lang}: {err}")
                    continue
                
            historico.append(video_id)
            guardar_historico(historico)

        except Exception as e_nicho:
            print(f"    ⚠️ Ocurrió un problema procesando el nicho {slug_z}: {e_nicho}. Continuando con el siguiente...")
            continue
        
    generar_portada_index()

if __name__ == "__main__":
    ejecutar_bot_masivo()
