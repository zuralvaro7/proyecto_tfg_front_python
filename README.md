# Trabajo de final de grado

# VistoCine

## Requisitos

- Python 3.11 o superior
- MPC-HC
- Conexión a Internet


## Instalación

Para poder utilizar la aplicación, sigue los siguientes pasos:

1. Clona el repositorio en tu equipo.
   * Para hacerlo utiliza el siguiente comando en el lugar que desees
   
   ```
   git clone https://github.com/zuralvaro7/proyecto_tfg_front_python.git
   ```  
2. Abre la carpeta del proyecto con tu IDE preferido, como **PyCharm** o **Visual Studio Code**.
3. Instala las dependencias necesarias del proyecto.
    * Para hacerlo utiliza el siguiente comando
   
   ```
   pip install -r requirements.txt
   ```   
4. Ejecuta el archivo principal de la aplicación:

   * En PyCharm: clic derecho sobre el archivo y selecciona **Run**.
   * En Visual Studio Code: utiliza la opción **Ejecutar** o el terminal integrado.
   * Para la terminal
     ```
     py .\CambioCap.py
     ```

---

## Configuración de MPC-HC

Antes de poder usar la aplicación hay que activar la interfaz web de **MPC-HC**, para hacerlo hay que seguir los siguientes pasos.

### Pasos para la configuración

1. Abre **MPC-HC**.
2. Ve a **Ver → Opciones → Reproductor → Interfaz web**.
3. Activa la opción **Escuchar en el puerto**.
4. Introduce el puerto **13579**.
5. Guarda los cambios y reinicia el reproductor.

> **Importante:** Si la interfaz web no está habilitada, la aplicación de escritorio no podrá comunicarse con MPC-HC y no funcionará correctamente.

---

## Inicio de sesión

Al ejecutar la aplicación aparecerá la pantalla de inicio de sesión.

1. Introduce tu nombre de usuario.
2. Introduce tu contraseña.
3. Pulsa el botón **Iniciar sesión**.

---

## Selección de carpeta y seguimiento

Para comenzar el seguimiento de una serie:

1. Pulsa el botón **Seleccionar carpeta**.
2. Busca y selecciona la carpeta donde se encuentran los episodios de la serie.
3. Reproduce el episodio deseado en MPC-HC.

La aplicación detectará automáticamente el progreso de reproducción y realizará el seguimiento correspondiente.

---

## Cerrar sesión

En la parte superior de la ventana principal encontrarás el botón **Cerrar sesión**, que te permitirá finalizar tu sesión actual.
