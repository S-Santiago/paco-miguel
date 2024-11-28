#
# Creador de PDF con las gráficas de las notas de los alumnos
# Santiago Fernández Sánchez
# 28/11/2024
#

# IMPORTANTE: Para el funcionamiento del programa es necesario tener una carpeta en el mismo directorio que el script llamada "temp"

# Modulos necesarios → "requests", "Pillow", "fpdf"

import base64
import os
from bs4 import BeautifulSoup
import requests
from io import BytesIO
from PIL import Image
from fpdf import FPDF

def sessionGET(url, session_token):
    session = requests.Session()
    session.cookies.set('PHPSESSID', session_token)
    
    response = session.get(url, data={})

    return response

def get_phpsessid(*, username: str, password: str):
    session = requests.Session()

    response = session.post("https://myagora.novaschool.es/myagora/index.php", data={
        "centro": 1, # Novaschool Añoreta → 1
        "user": username,
        "passwd": password,
        "Login": "Iniciar sesión",
        "submit": 1,
        "pasoLogueo": "submitted",
        "validarLogin": "Ir",
        "request_uri": ""
    })

    if not response.status_code == 200:
        raise Exception("Se ha producido un error en la solicitud")

    if not "error" in response.url:
        return session.cookies.get('PHPSESSID')
    
phpsessid = get_phpsessid(username="", password="") # <--- Completar con usuario y contraseña

def get_graficaAlumno_base64(id_ce: int, id_alumno: int, id_curso: int, session_token: str):
    try:
        response = sessionGET(f"https://myagora.novaschool.es/myagora/gestor_academico/?changeCurso={str(id_ce)}&url_destino=https%3A%2F%2Fmyagora.novaschool.es%2Fmyagora%2Fgestor_academico%2Fmod_notas%3Faccion%3Dresumen_notas%26id_alumno%3D{str(id_alumno)}%26id_curso%3D{str(id_curso)}", session_token)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return soup.select("#capa_notas_por_competencias > div:nth-child(1) > img")[0].attrs['src']
        else:
            return f"Error al enviar la solicitud: {response.status_code}, {response.reason}"
    except Exception as e:
        return e
    except:
        return "Se ha producido un error"

alumnos_id = [] # <----- Introducir aquí las IDs de los alumnos

alumnos_graficas = [
    get_graficaAlumno_base64(
        id_ce=20,
        id_alumno=id_alumno,
        id_curso=198,
        session_token=phpsessid,
    )
    for id_alumno in alumnos_id
]

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

for idx, img_base64 in enumerate(alumnos_graficas):
    image_data = base64.b64decode(img_base64.split('base64,')[1])
    image_file = BytesIO(image_data)

    with Image.open(image_file) as img:
        img_path = f"temp/{idx}.png"
        img.save(img_path)

    pdf = FPDF()
    pdf.add_page()
    pdf.image(img_path, x=10, y=10, w=100)

for idx in range(len(alumnos_graficas)):
    img_path = f"temp/{idx}.png"
    if os.path.exists(img_path):
        os.remove(img_path)

pdf.output("graficas_alumnos.pdf")
