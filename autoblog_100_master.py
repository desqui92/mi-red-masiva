import sys
import os
import json
import time
import random
import re
import logging
import yt_dlp
from slugify import slugify
from googleapiclient.discovery import build
from google import genai
from google.genai import types
from github import Auth, Github

# --- CONFIGURACIÓN DE LOGS EN CONSOLA ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("InfoZBot")

# --- 1. CREDENCIALES Y CONFIGURACIÓN ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
YOUTUBE_COOKIES = os.environ.get("YOUTUBE_COOKIES")  # Se agrega esta línea
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_NAME = os.environ.get("REPO_NAME", "desqui92/mi-red-masiva")

MODEL_GEMINI = "gemini-3.6-flash"
REGISTRO_FILE = "procesados.json"

PROPELLER_SCRIPT = """<script>(function(s){s.dataset.zone='11689215',s.src='https://n6wxm.com/vignette.min.js'})([document.documentElement, document.body].filter(Boolean).pop().appendChild(document.createElement('script')))</script>"""

# Verificación de credenciales al iniciar
logger.info("Verificando credenciales de entorno...")
if not YOUTUBE_API_KEY:
    logger.warning("YOUTUBE_API_KEY no detectada. La búsqueda de videos estará desactivada.")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY no detectada. El bot no podrá generar contenido.")
if not GITHUB_TOKEN:
    logger.warning("GITHUB_TOKEN no detectado. No se publicará contenido en GitHub.")

yt_client = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY) if YOUTUBE_API_KEY else None
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

if GITHUB_TOKEN:
    try:
        auth = Auth.Token(GITHUB_TOKEN)
        gh_client = Github(auth=auth)
        repo = gh_client.get_repo(REPO_NAME)
        logger.info(f"Conectado exitosamente al repositorio GitHub: {REPO_NAME}")
    except Exception as e:
        logger.error(f"Error al conectar con GitHub: {e}")
        repo = None
else:
    repo = None

IDIOMAS_MAP = {
    "English": "en", "Español": "es", "Português": "pt", "Français": "fr", "Deutsch": "de", 
    "Italiano": "it", "Nederlands": "nl", "Polski": "pl", "Русский": "ru", "Türkçe": "tr", 
    "日本語": "ja", "한국어": "ko", "Tiếng Việt": "vi", "Bahasa Indonesia": "id", "ไทย": "th", 
    "हिन्दी": "hi", "العربية": "ar", "简体中文": "zh-cn", "繁體中文": "zh-tw", "Svenska": "sv", 
    "Norsk": "no", "Dansk": "da", "Suomi": "fi", "Čeština": "cs", "Română": "ro"
}

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

def cargar_historico() -> list:
    if not repo:
        logger.warning("Sin repositorio configurado. Histórico no cargado.")
        return []
    try:
        logger.info(f"Cargando historial desde {REGISTRO_FILE}...")
        content = repo.get_contents(REGISTRO_FILE)
        data = json.loads(content.decoded_content.decode('utf-8'))
        logger.info(f"Histórico cargado exitosamente. {len(data)} items en registro.")
        return data
    except Exception as e:
        logger.warning(f"No se pudo cargar el histórico ({e}). Iniciando lista vacía.")
        return []

def guardar_historico(historico: list):
    if not repo:
        return
    json_data = json.dumps(historico, indent=2)
    try:
        try:
            content = repo.get_contents(REGISTRO_FILE)
            repo.update_file(content.path, "Update processed log", json_data, content.sha)
            logger.info("Registro de histórico actualizado en GitHub.")
        except Exception:
            repo.create_file(REGISTRO_FILE, "Create processed log", json_data)
            logger.info("Registro de histórico creado por primera vez en GitHub.")
    except Exception as e:
        logger.error(f"Error al guardar el histórico en GitHub: {e}")

def llamar_gemini_con_reintento(prompt: str, mime_type: str = None, retries: int = 4):
    if not ai_client:
        raise ValueError("GEMINI_API_KEY no está configurada.")
    
    config = types.GenerateContentConfig(response_mime_type=mime_type) if mime_type else None
    
    for intento in range(retries):
        try:
            res = ai_client.models.generate_content(
                model=MODEL_GEMINI,
                contents=prompt,
                config=config
            )
            return res.text
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                wait_time = 15 * (intento + 1)
                logger.warning(f"Rate limit en Gemini. Intento {intento + 1}/{retries}. Esperando {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Error en Gemini (Intento {intento + 1}/{retries}): {e}")
                time.sleep(5)
            
            if intento == retries - 1:
                logger.critical(f"Agotados los reintentos con Gemini para la solicitud.")
                raise e

def limpiar_html_cuerpo(html_str: str) -> str:
    if not html_str:
        return ""
    texto = html_str.strip()
    texto = re.sub(r"^```[a-zA-Z]*\n?", "", texto)
    texto = re.sub(r"\n?```$", "", texto)
    return texto.strip()

def generar_busqueda_ia(nicho: str) -> str:
    logger.info(f"Generando término de búsqueda con IA para el nicho: '{nicho}'...")
    prompt = f"Dame 1 término de búsqueda en YouTube muy específico y tendencia sobre: '{nicho}'. Responde SOLO con el término en texto plano."
    res_text = llamar_gemini_con_reintento(prompt)
    lineas = res_text.strip().splitlines() if res_text else []
    primera_linea = lineas[0] if lineas else nicho
    kw = primera_linea.replace('"', '').replace("'", "").strip()
    logger.info(f"Término generado: '{kw}'")
    return kw

def buscar_videos_yt(query: str) -> list:
    if not yt_client:
        logger.warning("Búsqueda de YouTube omitida (sin cliente configurado).")
        return []
    try:
        logger.info(f"Buscando videos en YouTube para la query: '{query}'...")
        req = yt_client.search().list(
            q=query, 
            part="snippet", 
            type="video", 
            order="relevance", 
            maxResults=5
        )
        res = req.execute()
        items = res.get("items", [])
        video_ids = [item["id"]["videoId"] for item in items]
        logger.info(f"Se encontraron {len(video_ids)} videos: {video_ids}")
        return video_ids
    except Exception as e:
        logger.error(f"Error al realizar búsqueda en YouTube: {e}")
        return []

def descargar_audio_youtube(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    
    # --- INICIO MODIFICACIÓN COOKIES ---
    if YOUTUBE_COOKIES:
        if os.path.isfile(YOUTUBE_COOKIES):
            # Si YOUTUBE_COOKIES es la ruta a un archivo (ej: "cookies.txt")
            ydl_opts['cookiefile'] = YOUTUBE_COOKIES
        else:
            # Si YOUTUBE_COOKIES contiene el texto Netscape pegado en el Secret de GitHub
            with open("temp_cookies.txt", "w", encoding="utf-8") as f:
                f.write(YOUTUBE_COOKIES)
            ydl_opts['cookiefile'] = "temp_cookies.txt"
    # --- FIN MODIFICACIÓN COOKIES ---

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def obtener_contexto_video(video_id: str) -> str:
    archivo_audio = None
    uploaded_file = None
    try:
        archivo_audio = descargar_audio_youtube(video_id)
        
        logger.info(f"Subiendo archivo {archivo_audio} a la File API de Gemini...")
        uploaded_file = ai_client.files.upload(file=archivo_audio)
        logger.info(f"Archivo subido. ID asignado por Gemini: {uploaded_file.name}")
        
        # Espera activa del procesamiento en la nube
        for loop_idx in range(15):
            if uploaded_file.state.name == "ACTIVE":
                logger.info("El archivo de audio se procesó correctamente en Gemini.")
                break
            logger.info(f"Esperando procesamiento del audio en Gemini... Estado actual: {uploaded_file.state.name} ({loop_idx+1}/15)")
            time.sleep(2)
            uploaded_file = ai_client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name != "ACTIVE":
            logger.error("El archivo de audio no alcanzó el estado ACTIVE a tiempo.")
            return None

        logger.info("Solicitando transcripción del audio a Gemini...")
        prompt = "Transcribe todo el audio hablado de este video de forma concisa. Devuelve texto plano."
        
        res = ai_client.models.generate_content(
            model=MODEL_GEMINI,
            contents=[uploaded_file, prompt]
        )
        if res and res.text:
            logger.info("Transcripción completada con éxito.")
            return f"Transcripción de Audio:\n{res.text}"
        
        logger.warning("Gemini devolvió respuesta vacía para la transcripción.")
        return None

    except Exception as e:
        logger.error(f"Fallo al procesar audio del video {video_id}: {e}")
        return None
        
    finally:
        if archivo_audio and os.path.exists(archivo_audio):
            try:
                os.remove(archivo_audio)
                logger.info(f"Archivo local eliminado: {archivo_audio}")
            except Exception as e_del:
                logger.warning(f"No se pudo eliminar archivo temporal {archivo_audio}: {e_del}")
        if uploaded_file:
            try:
                ai_client.files.delete(name=uploaded_file.name)
                logger.info(f"Archivo eliminado de la API de Gemini: {uploaded_file.name}")
            except Exception as e_del_api:
                logger.warning(f"No se pudo eliminar archivo en Gemini API: {e_del_api}")

def redactar_post_ia(contexto: str, idioma: str) -> dict:
    prompt = f"""
    Eres un redactor SEO profesional. Genera un artículo completo de blog bien estructurado sobre este tema.
    
    REGLAS OBLIGATORIAS:
    1. La PRIMERA LÍNEA de tu respuesta DEBE ser el título del artículo envuelto en <h1> y </h1>.
    2. A partir de la segunda línea, escribe todo el cuerpo del artículo usando etiquetas HTML limpias (<h2>, <p>, <ul>, <li>, blockquote).
    3. Idioma de salida: {idioma}.
    4. NO incluyas bloques de código markdown (prohibido usar ```html). Devuelve solo el HTML plano.
    
    Fuente / Contexto:
    {contexto[:3500]}
    """
    res_text = llamar_gemini_con_reintento(prompt)
    if not res_text:
        return None
    
    texto_limpio = limpiar_html_cuerpo(res_text)
    lineas = texto_limpio.splitlines()
    titulo = "Artículo InfoZ"
    cuerpo_lineas = []
    
    for line in lineas:
        if "<h1>" in line and "</h1>" in line and titulo == "Artículo InfoZ":
            titulo = line.replace("<h1>", "").replace("</h1>", "").strip()
        else:
            cuerpo_lineas.append(line)
            
    cuerpo = "\n".join(cuerpo_lineas).strip()
    return {"titulo": titulo, "contenido_html": cuerpo}

def publicar_en_github(slug_z: str, slug_post: str, titulo: str, cuerpo: str, idioma: str):
    if not repo:
        logger.error("Error: Conexión con GitHub no inicializada. Imposible publicar.")
        return

    cuerpo_limpio = limpiar_html_cuerpo(cuerpo)
    lang_code = IDIOMAS_MAP.get(idioma, "en")
    
    html = f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    {PROPELLER_SCRIPT}
    <style>
        :root {{
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --border: #334155;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: var(--bg); 
            color: var(--text); 
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.75; 
            padding: 2rem 1rem; 
        }}
        .container {{ 
            max-width: 760px; 
            margin: 0 auto; 
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        nav {{ margin-bottom: 2rem; }}
        nav a {{ color: var(--accent); text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
        nav a:hover {{ text-decoration: underline; }}
        h1 {{ font-size: 2.25rem; color: #f8fafc; margin-bottom: 1.5rem; line-height: 1.25; letter-spacing: -0.02em; }}
        article h2 {{ font-size: 1.5rem; color: var(--accent); margin-top: 2rem; margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }}
        article h3 {{ font-size: 1.2rem; color: #f8fafc; margin-top: 1.5rem; margin-bottom: 0.5rem; }}
        article p {{ margin-bottom: 1.25rem; color: #cbd5e1; font-size: 1.05rem; }}
        article ul, article ol {{ margin-bottom: 1.25rem; padding-left: 1.5rem; color: #cbd5e1; }}
        article li {{ margin-bottom: 0.5rem; }}
        article blockquote {{ border-left: 4px solid var(--accent); padding: 0.75rem 1rem; margin: 1.5rem 0; font-style: italic; color: var(--text-muted); background: rgba(56, 189, 248, 0.05); border-radius: 0 8px 8px 0; }}
        article a {{ color: var(--accent); text-decoration: underline; }}
        footer {{ margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border); text-align: center; color: var(--text-muted); font-size: 0.875rem; }}
        @media (max-width: 640px) {{ body {{ padding: 1rem 0.5rem; }} .container {{ padding: 1.5rem 1rem; border-radius: 8px; }} h1 {{ font-size: 1.75rem; }} }}
    </style>
</head>
<body>
    <div class="container">
        <nav><a href="../index.html">← Volver a la categoría</a></nav>
        <article>
            <h1>{titulo}</h1>
            {cuerpo_limpio}
        </article>
        <footer><p>&copy; InfoZ Network — Todos los derechos reservados.</p></footer>
    </div>
</body>
</html>"""
    
    path = f"{slug_z}/{lang_code}/{slug_post}.html"
    try:
        try:
            existing_file = repo.get_contents(path)
            repo.update_file(path, f"Update post {slug_post}", html, existing_file.sha)
            logger.info(f"✔ Publicado/Actualizado en GitHub: {path}")
        except Exception:
            repo.create_file(path, f"Post for {slug_z} ({idioma}): {slug_post}", html)
            logger.info(f"✔ Publicado nuevo post en GitHub: {path}")
    except Exception as e:
        logger.error(f"❌ Error al subir {path} a GitHub: {e}")

def generar_indices_y_portada(nichos_modificados: list):
    if not repo:
        logger.warning("Sin repositorio. Se omite la generación de índices.")
        return
    logger.info("--- GENERANDO PORTADAS DE CATEGORÍAS E ÍNDICE GENERAL ---")
    
    try:
        try:
            branch = repo.get_branch("main")
        except Exception:
            branch = repo.get_branch("master")
        tree = repo.get_git_tree(branch.commit.sha, recursive=True)
        logger.info(f"Árbol Git obtenido correctamente ({len(tree.tree)} elementos encontrados).")
    except Exception as e:
        logger.error(f"Error obteniendo árbol del repositorio Git: {e}")
        return

    posts_por_nicho = {cat["slug_z"]: [] for cat in CATEGORIAS_100}
    
    for item in tree.tree:
        parts = item.path.split('/')
        if len(parts) == 3 and parts[0] in posts_por_nicho and parts[2].endswith('.html') and parts[2] != 'index.html':
            slug_z = parts[0]
            lang_slug = parts[1]
            file_slug = parts[2]
            
            titulo = file_slug.replace('.html', '').replace('-', ' ').capitalize()
            posts_por_nicho[slug_z].append({
                "path": f"{lang_slug}/{file_slug}",
                "titulo": titulo,
                "idioma": lang_slug.upper()
            })

    for cat in CATEGORIAS_100:
        slug_z = cat["slug_z"]
        if slug_z not in nichos_modificados:
            continue
            
        nicho = cat["nicho"]
        posts = posts_por_nicho.get(slug_z, [])
        logger.info(f"Generando index.html para nicho '{slug_z}' ({len(posts)} posts asociados)...")
        
        items_html = ""
        if posts:
            for p in posts:
                items_html += f"""
                <li style="margin-bottom: 0.8rem; background: #1e293b; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #334155;">
                    <span style="font-size: 0.75rem; background: #38bdf8; color: #0f172a; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-right: 8px;">{p['idioma']}</span>
                    <a href="{p['path']}" style="color: #f8fafc; text-decoration: none; font-weight: 500;">{p['titulo']}</a>
                </li>
                """
        else:
            items_html = "<p style='color:#94a3b8;'>Próximamente habrá contenido en este nicho.</p>"

        cat_index_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nicho} — InfoZ</title>
    {PROPELLER_SCRIPT}
    <style>
        :root {{ --bg: #0f172a; --card-bg: #1e293b; --text: #f8fafc; --accent: #38bdf8; --border: #334155; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: system-ui, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 2rem 1rem; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 2rem; }}
        h1 {{ color: var(--accent); margin-bottom: 0.5rem; font-size: 2rem; }}
        p.desc {{ color: #94a3b8; margin-bottom: 1.5rem; }}
        nav a {{ color: var(--accent); text-decoration: none; font-weight: 600; display: inline-block; margin-bottom: 1.5rem; }}
        ul {{ list-style: none; }}
    </style>
</head>
<body>
    <div class="container">
        <nav><a href="../index.html">← Volver al Inicio</a></nav>
        <h1>{nicho}</h1>
        <p class="desc">Artículos publicados en esta categoría:</p>
        <ul>{items_html}</ul>
    </div>
</body>
</html>"""

        path_cat = f"{slug_z}/index.html"
        try:
            existing = repo.get_contents(path_cat)
            repo.update_file(path_cat, f"Update index for {slug_z}", cat_index_html, existing.sha)
            logger.info(f"✔ Actualizado index de categoría: {path_cat}")
        except Exception:
            repo.create_file(path_cat, f"Create index for {slug_z}", cat_index_html)
            logger.info(f"✔ Creado index de categoría: {path_cat}")

    grid_items = ""
    for cat in CATEGORIAS_100:
        nicho = cat["nicho"]
        slug_z = cat["slug_z"]
        cant = len(posts_por_nicho.get(slug_z, []))
        grid_items += f"""
        <a href="./{slug_z}/index.html" class="card">
            <h2>{nicho}</h2>
            <div class="card-footer">
                <span class="badge">+{slug_z}</span>
                <span class="count">{cant} posts</span>
            </div>
        </a>
        """

    root_index_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfoZ — Tu Red de Conocimiento Global</title>
    {PROPELLER_SCRIPT}
    <style>
        :root {{ --bg: #0f172a; --card-bg: #1e293b; --text: #f8fafc; --accent: #38bdf8; --border: #334155; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: system-ui, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 2rem 1rem; line-height: 1.5; }}
        header {{ text-align: center; max-width: 800px; margin: 0 auto 3rem; }}
        h1 {{ font-size: 2.5rem; color: var(--accent); margin-bottom: 0.5rem; }}
        p {{ color: #94a3b8; font-size: 1.1rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; max-width: 1200px; margin: 0 auto; }}
        .card {{ background: var(--card-bg); border: 1px solid var(--border); padding: 1.25rem; border-radius: 12px; text-decoration: none; color: inherit; transition: transform 0.2s, border-color 0.2s; display: flex; flex-direction: column; justify-content: space-between; }}
        .card:hover {{ transform: translateY(-3px); border-color: var(--accent); }}
        .card h2 {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.75rem; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; }}
        .badge {{ font-size: 0.75rem; color: var(--accent); font-weight: 700; text-transform: uppercase; }}
        .count {{ font-size: 0.75rem; color: #94a3b8; }}
        footer {{ text-align: center; margin-top: 4rem; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <header>
        <h1>InfoZ</h1>
        <p>Explorá guías, tutoriales y análisis en más de 100 nichos especializados.</p>
    </header>
    <main class="grid">{grid_items}</main>
    <footer><p>&copy; InfoZ Network — Todos los derechos reservados.</p></footer>
</body>
</html>"""

    try:
        existing_file = repo.get_contents("index.html")
        repo.update_file("index.html", "Update index page", root_index_html, existing_file.sha)
        logger.info("✔ Portada principal (index.html raíz) actualizada con éxito.")
    except Exception:
        repo.create_file("index.html", "Create index page", root_index_html)
        logger.info("✔ Portada principal (index.html raíz) creada con éxito.")

def ejecutar_bot_masivo():
    logger.info("=== INICIANDO EJECUCIÓN DEL BOT MASIVO ===")
    historico = cargar_historico()
    lote = random.sample(CATEGORIAS_100, 5)
    
    logger.info(f"Lote de 5 nichos seleccionados para esta ronda: {[c['slug_z'] for c in lote]}")
    nichos_procesados = []
    
    for i, item in enumerate(lote, 1):
        nicho = item["nicho"]
        slug_z = item["slug_z"]
        
        logger.info(f"\n==================================================")
        logger.info(f" PROCESANDO NICHO ({i}/5): {slug_z} -> [{nicho}]")
        logger.info(f"==================================================")
        
        try:
            kw = generar_busqueda_ia(nicho)
            video_ids = buscar_videos_yt(kw)
            
            video_id = None
            contexto = None
            
            if video_ids:
                logger.info(f"Analizando {len(video_ids)} candidatos de video...")
                for vid in video_ids:
                    if vid in historico:
                        logger.info(f"Video {vid} ya fue procesado anteriormente. Omitiendo...")
                        continue
                    
                    logger.info(f"Intentando extraer transcripción del video: {vid}")
                    data_vid = obtener_contexto_video(vid)
                    if data_vid:
                        video_id = vid
                        contexto = data_vid
                        logger.info(f"Video {vid} aceptado como fuente principal de contexto.")
                        break
                    else:
                        logger.warning(f"No se obtuvo contexto del video {vid}, probando siguiente...")
            
            if not contexto:
                logger.warning(f"⚠️ Plan B activado: Generando post temático nativo sobre '{kw}' sin soporte de video.")
                contexto = f"Tema principal: {nicho}. Enfoque específico: {kw}. Genera una guía completa y detallada sobre este tema."

            total_idiomas = len(IDIOMAS_MAP)
            logger.info(f"Iniciando generación multilingüe ({total_idiomas} idiomas)...")

            for idx_lang, (lang_name, lang_code) in enumerate(IDIOMAS_MAP.items(), 1):
                logger.info(f"[{idx_lang}/{total_idiomas}] Generando versión en '{lang_name}' ({lang_code})...")
                try:
                    art = redactar_post_ia(contexto, lang_name)
                    
                    if not art or "titulo" not in art or "contenido_html" not in art:
                        logger.error(f"Respuesta inválida de la IA para idioma {lang_name}. Saltando...")
                        continue

                    slug_post = slugify(art["titulo"])
                    if not slug_post:
                        slug_post = f"article-{int(time.time())}"

                    publicar_en_github(slug_z, slug_post, art["titulo"], art["contenido_html"], lang_name)
                    
                    # Pausa anti rate-limit
                    time.sleep(10)
                    
                except Exception as err:
                    logger.error(f"Error procesando idioma {lang_name}: {err}")
                    continue
                
            if video_id:
                historico.append(video_id)
                guardar_historico(historico)

            nichos_procesados.append(slug_z)
            logger.info(f"Nicho {slug_z} finalizado con éxito.")

        except Exception as e_nicho:
            logger.error(f"Ocurrió un problema procesando el nicho {slug_z}: {e_nicho}. Continuando con el siguiente...")
            continue
        
    generar_indices_y_portada(nichos_procesados)
    logger.info("=== EJECUCIÓN FINALIZADA COMPLETAMENTE ===")

if __name__ == "__main__":
    ejecutar_bot_masivo()
