import urllib.request
import re
import os
import datetime
import tkinter as tk
from tkinter import filedialog

import json
from PIL import Image, ImageTk
import http.client

# hacer que sea un archivo ejecutable
# poner iconos y hacer que sea mas bonito 
# hacer que detecte de forma automática el reproductor
# [Medio Solucionado]cambiar forma de detección del reproductor, para que no vaya lento
#       posible solución, usar tasklist y sacar el proceso de la aplicacion
#   Laguea mucho menos al mover la interfaz

# otra idea es que el usuario ponga una carpeta "padre" donde estén todas las carpetas de las series y 
#       que detecte si esta en la carpeta padre se modifique automáticamente el registro de la carpeta 
#       donde esta la serie
# [Solucionado]cambiar el que de error si no selecciona ninguna carpeta, le da al cancelar 
#           [Solucionado]quitar el espacio en blanco de la interfaz cuando da este error y cuando 
#           [Solucionado]selecciona la carpeta quitar el label de abajo
# [CREO Solucionado] se cambia el nombre antes de que se ejecute el video y despues
#       s
# Quiero que solo detecte el video cuando se esta ejecutando, no cuando se abre y detecta el reproductor
# LLevar un historial de los capítulos vistos, el dia y la ruta mirar en que formato guardo el historial
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
# Ideas
# Para el final pensar si hacer la aplicacion como servicio y tener una interfaz, tambien que pueda enviar 
#       los datos del historial a una pagina y poder acceder desde cualquier navegador o aplicacion movil
#       posible guia para la aplicacion web y una posible forma de creacion de usuarios e inicio de sesion 
#       para poder enviar los registros automaticamente, si no fuese el caso poner boton para "descargar" 
#       los registros y poder volcarlos a la pagina web o aplicacion
# Guardar el progreso de un episodio, si no lo ha terminado.


# Variables globales
estado_anterior = None
ruta = ""
contador = 0
archivo_anterior = ""
esperando_nuevo_archivo = False



def seleccionar_carpeta():
    global ruta, contador
    
    ruta = filedialog.askdirectory(title="Selecciona la carpeta")
    label.config(text=ruta)
    contador = cargar_contador()
    actualizar_label_contador()
    
    # Solo crear carpeta "0" si NO existe ninguna carpeta numérica
    try:
        carpetas_numericas = [nombre for nombre in os.listdir(ruta) 
                              if os.path.isdir(os.path.join(ruta, nombre)) and nombre.isdigit()]
    except Exception as e:
        print(f"No se detecta ninguna ruta: {e}")
        label.config(text="No hay carpeta seleccionada', selecciona una'")
        return

    if not carpetas_numericas:
        ruta_cero = os.path.join(ruta, "0")
        if not os.path.exists(ruta_cero):
            try:
                os.mkdir(ruta_cero)
                print(f"Carpeta {contador} creada en {ruta}")
            except Exception as e:
                print(f"No se pudo crear la carpeta '0': {e}")


def cargar_contador():
    if not ruta:
        return 0
    progreso_file = os.path.join(ruta, "progreso.txt")
    try:
        with open(progreso_file, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def guardar_contador(contador):
    if not ruta:
        print("No hay ruta seleccionada, no se puede guardar progreso.")
        return
    progreso_file = os.path.join(ruta, "progreso.txt")
    
    try:
        with open(progreso_file, "w") as f:
            f.write(str(contador))
        print(f"Progreso guardado: {contador} en {progreso_file}")
    except Exception as e:
        print(f"Error guardando progreso: {e}")


def renombrar_carpeta(contador):
    contador2 = cargar_contador()
    if not ruta:
        print("No hay carpeta seleccionada para renombrar.")
        return
    
    carpeta_anterior = os.path.join(ruta, str(contador2))
    carpeta_nueva = os.path.join(ruta, str(contador))
    
    if os.path.exists(carpeta_anterior):
        if os.path.exists(carpeta_nueva):
            print(f"La carpeta destino {carpeta_nueva} ya existe, no se renombra.")
            return
        try:
            os.rename(carpeta_anterior, carpeta_nueva)
            print(f"Carpeta renombrada de '{contador-1}' a '{contador}'")
        except Exception as e:
            print(f"Error renombrando carpeta: {e}")
    else:
        print("No existe la carpeta '0' para renombrar.")


def actualizar_label_contador():
    label_contador.config(text=f"Episodios vistos: {contador}")


def tiempoAsegundo(campo):
    campos=campo.split(":")
    tiempo=int(campos[0])*3600+int(campos[1])*60+int(campos[2])
    return tiempo

def porcentajeRestante(tiempoActual, tiempoFinal):
    tiempoQueda=tiempoFinal-tiempoActual
    tiempo=(tiempoQueda/tiempoFinal)*100
    return tiempo

def gestionarId():
    if not os.path.exists("./historial/historial.csv"):
        os.mkdir("./historial")
        historial=open("./historial/historial.csv", 'w')
        historial.write("id,Nombre,Capitulo,Dia visto,Hora,Ruta\n")
        historial.close()
    try:
        with open("./historial/historial.csv", mode='r') as h:
            lineas = h.readlines()
            if len(lineas) > 1:
                ultima_linea = lineas[-1]
                ultimo_id = int(ultima_linea.split(",")[0])
                return ultimo_id + 1
            else:
                return 1
    except Exception as e:
        print(f"No se ha podido gestionar el ID: {e}")
        return 1


# Se guarda el historial en un txt
def guardar_historial(datos):
    dia=datetime.date.today()
    dia=dia.isoformat()
    dia=dia.split("-")
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    if not os.path.exists("./historial"):
        os.mkdir("./historial")
        historial=open("./historial/historial.csv", 'w')
        historial.write("Nombre,Capitulo,Dia visto,Hora,Ruta\n")
        historial.close()
    try:
        with open("./historial/historial.csv", mode='a') as h:
            h.write(f"{gestionarId()},{datos[0]},{contador},{dia[2]}/{dia[1]}/{dia[0]},{hora},{datos[4]}\n")
            h.close()
            print(f"Historial guardado: {datos[0]}, Capítulo: {contador}, Día: {dia[2]}/{dia[1]}/{dia[0]}, Hora: {hora} ,Ruta: {datos[4]}")
    except Exception as e:
        print(f"No se ha podido guardar: {e}")
    subir_historial(datos, contador, dia, hora)

def getConfiguracion():
    try:
        if not os.path.exists("./conf/conf.json"):
            return None

        with open("./conf/conf.json", "r") as conf:
            contenido = conf.read().strip()

        if not contenido:
            return None

        return json.loads(contenido)

    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return None

def subir_historial(datos, contador, dia, hora):
    conn = http.client.HTTPConnection("localhost:8080")
    config = getConfiguracion()
    id_usuario = config["id_usuario"]
    diaHoy = f"{dia[2]}/{dia[1]}/{dia[0]}"
    payload = {
        "tfgUsuariosDto": {"id_usuario": id_usuario},
        "tfgHistorialDto": {
            "nombre_capitulo": datos[0],
            "numero_capitulo": contador,
            "dia_visto": diaHoy,
            "hora": hora
        }
    }
    headers = {'content-type': "application/json"}
    conn.request("POST", "/api/v1/tfg/subirhistorial", json.dumps(payload), headers)
    res = conn.getresponse()
    data = res.read()
    print(payload)
    print(data.decode("utf-8"))

# def reproductor_activo():
#     # Comprobar si el reproductor está activo
#     mpchc = os.system("tasklist | findstr mpc-hc64.exe")
#     reproWindows = os.system("tasklist | findstr Microsoft.Media.Player.ex")
#     vlc = os.system("tasklist | findstr vlc.exe")
    




pruebas= False
# pruebas = True
pp = 0
def comprobar_estado():
    global estado_anterior, contador, archivo_anterior, esperando_nuevo_archivo, pp
    datos = None
    
    if pruebas and pp==0:
        pp=1
        print("Modo pruebas activado, no se ejecutará la comprobación real.")


    if not ruta:
        root.after(2000, comprobar_estado)
        return
    # ejecutar tasklist y comprobar si esta o no
    mpchc = os.system("tasklist | findstr mpc-hc64.exe >nul 2>&1")
    # reproWindows = os.system("tasklist | findstr Microsoft.Media.Player.ex >nul 2>&1")
    # vlc = os.system("tasklist | findstr vlc.exe >nul 2>&1")
    
    # print (f"Comprobando estado del reproductor: mpc-hc={mpchc}, reproWindows={reproWindows}, vlc={vlc}")
    
    if (mpchc==0):
        try:
            datos = urllib.request.urlopen(url="http://127.0.0.1:13579/status.html").read()
            datos = datos.decode("latin1", errors="replace")
        except Exception as e:
            print(f"Error al obtener datos del reproductor: {e}")

    if datos != None:
        campos = re.findall('"(.*?)"', datos)
        archivo_actual = campos[0]
        estado_actual = campos[1]
        

        if archivo_actual != archivo_anterior:
            print("Nuevo archivo detectado:", archivo_actual)
            label_estado1.config(text=f"Archivo: {os.path.basename(archivo_actual)}")
            esperando_nuevo_archivo = False

        tiempoActual=tiempoAsegundo(campos[2])
        tiempoFinal=tiempoAsegundo(campos[3])

        # Tengo un error que cambia el estado y no se esta reproduciendo cambia el nombre y modifica el progreso 
        #           y cuando se reproduce algo cambia también al final del video 
        if estado_actual != estado_anterior:
            print("Cambio de estado:", estado_anterior, "->", estado_actual)
            pintarEstado(estado_actual)

        if estado_actual == "Stopped" or estado_actual == "N/A" or estado_actual == "Detenido" and estado_actual != estado_anterior:
            print("Reproductor detenido, esperando nuevo archivo...")
            esperando_nuevo_archivo = True
            
        try:   
            totalPor=porcentajeRestante(tiempoActual,tiempoFinal)
        except Exception as e:
            print(f"Error al calcular porcentaje: {e}")
            totalPor = 0
        # print(f"Tiempo actual: {tiempoActual}, Tiempo final: {tiempoFinal}, Porcentaje: {totalPor:.2f}%")
        if totalPor<=10.00 and not esperando_nuevo_archivo and not pruebas:
            contador += 1
            renombrar_carpeta(contador)
            guardar_contador(contador)
            actualizar_label_contador()
            guardar_historial(campos)
            esperando_nuevo_archivo = True
        
        estado_anterior = estado_actual
        archivo_anterior = archivo_actual
    root.after(2000, comprobar_estado)


# Interfaz
root = tk.Tk(className="Nombre aplicación")

btn_cerrar=None
boton =None
label=None
label_contador=None
label_estado1=None
label_estado=None
nombre= None
password = None

def pantalla_incio():
    global boton, nombre, password, btn_cerrar
    nombre = tk.Text(root, height=5, width=50)
    password = tk.Text(root, height=5, width=50)
    nombre.pack()
    password.pack()


    boton = tk.Button(root, text="Iniciar", command=lambda :(
        conn := http.client.HTTPConnection("localhost:8080"),
        payload := "{\n  \"nombre_usuario\": \"" + nombre.get("1.0", "end-1c") + "\",\n  \"contrasena\": \"" +
                   password.get("1.0", "end-1c") + "\",\n  \"esLogin\": true\n}",
        headers := {'content-type': "application/json"},
        conn.request("POST", "/api/v1/tfg/login", payload, headers),
        res := conn.getresponse(),
        data := json.loads(res.read()),
        anadirUsuario(data),
        pantalla2()
    ))
    boton.pack()

def anadirUsuario(data):
    if not os.path.exists("./conf"):
        os.mkdir("./conf")
        conf = open("./conf/conf.json", 'w')
        conf.write("{\n\"id_usuario\" : " + str(data["id_usuario"]) + ",\n\"nombre\" : \"" + data[
                "nombre_usuario"] + "\"" + ",\n\"contrasena\" : \"" + data["contrasena"] + "\"\n}")
        conf.close()
        print("hecho")
    elif not os.path.exists("./conf/conf.json"):
        conf = open("./conf/conf.json", 'w')
        conf.write("{\n\"id_usuario\" : " + str(data["id_usuario"]) + ",\n\"nombre\" : \"" + data[
            "nombre_usuario"] + "\"" + ",\n\"contrasena\" : \"" + data["contrasena"] + "\"\n}")
        conf.close()
    elif os.path.exists("./conf/conf.json"):
        conf = open("./conf/conf.json", 'r')
        if conf.read() == "":
            conf = open("./conf/conf.json", 'w')
            conf.write("{\n\"id_usuario\" : " + str(data["id_usuario"]) + ",\n\"nombre\" : \"" + data[
                "nombre_usuario"] + "\"" + ",\n\"contrasena\" : \"" + data["contrasena"] + "\"\n}")
            conf.close()
        conf.close()

def pantalla2():
    global boton, label, label_contador, label_estado1, label_estado, nombre, password,btn_cerrar
    if(boton):
        nombre.destroy()
        password.destroy()
        boton.destroy()
    btn_cerrar = tk.Button(root, text="Cerrar", command=cerra_sesion)
    boton = tk.Button(root, text="Seleccionar Carpeta", command=seleccionar_carpeta)
    label = tk.Label(root, text="No hay carpeta seleccionada', selecciona una'")
    label_contador = tk.Label(root, text=f"Episodios vistos: {contador}")
    label_estado1 = tk.Label(root, text="")
    label_estado = tk.Label(root, text="Estado: N/A")


    btn_cerrar.pack()
    label.pack()
    boton.pack()
    label_contador.pack()
    label_estado1.pack()
    label_estado.pack()
    comprobar_estado()

def cerra_sesion():
    global boton, label, label_contador, label_estado1, label_estado, btn_cerrar
    boton.destroy()
    label.destroy()
    label_contador.destroy()
    label_estado1.destroy()
    label_estado.destroy()
    btn_cerrar.destroy()
    conf = open("./conf/conf.json", 'w')
    conf.write("")
    conf.close()
    pantalla_incio()

def pintarEstado(estado):
    estado = str(estado).encode(encoding="latin1",errors="replace").decode("utf-8", errors="replace")

    label_estado.config(text=f"Estado: {estado}")



    # Para la interfaz lo que quiero es que tenga un apartado de ajustes donde se puedan poner las
    # carpetas padres y se decida si quiere o no que se inicie con el ordenador, que en la interfaz
    # aparezca la ruta, el nombre, y el capitulo, tambien el estado en el que puede estar, tambien
    # poner fija la interfaz(no se pueda hacer mas grande o mas pequeña), tambien que se pueda ver
    # el historial de los episodios vistos
    # flutter, java Swing, react native, c# net, javascript,


    # # formato para insertar imágenes jpeg,jpg y png
    # imagen=Image.open(r"C:\Users\alvar\Desktop\7l5f6RaS.jpeg")
    # # Redimensionar imágenes
    # imagenR=imagen.resize((100,100))
    # imagen_tk = ImageTk.PhotoImage(imagenR)
    # etiqueta=tk.Label(root, image=imagen_tk)
    # etiqueta.pack()
    # etiqueta.imagen_tk = imagen_tk


    # # formato para insertar imagen png
    # png = tk.PhotoImage(file=r"C:\Users\alvar\Desktop\Captura de pantalla 2023-05-27 193350.png")
    # # Redimensionar imágenes
    # png = png.subsample(10,10)
    # etipng = tk.Label(root, image=png)
    # etipng.pack()
if getConfiguracion():
    pantalla2()
else:
    pantalla_incio()

root.mainloop()
