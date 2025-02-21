from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# Ruta para manejar la descarga
@app.route("/descargar", methods=["POST"])
def descargar():
    data = request.get_json()
    url = data.get("url")  # Obtener la URL del JSON
    calidad = data.get("calidad")  # Obtener la calidad seleccionada

    if not url:
        return jsonify({"error": "Por favor, ingresa una URL válida."}), 400

    try:
        # Crear la carpeta "downloads" si no existe
        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        # Opciones de descarga
        opciones = {
            'format': calidad,  # Usar la calidad seleccionada
            'outtmpl': os.path.join("downloads", "%(title)s.%(ext)s"),  # Nombre del archivo con el título del video
            'merge_output_format': 'mp4',  # Asegurar formato MP4
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)  # Obtener información del video sin descargar
            titulo = info.get("title", "video")  # Obtener el título del video
            ruta_archivo = ydl.prepare_filename(info)  # Generar la ruta del archivo con el título
            ydl.download([url])  # Descargar el video

        # Enviar el archivo al usuario
        response = send_file(ruta_archivo, as_attachment=True)

        # Eliminar el archivo después de enviarlo
        @response.call_on_close
        def eliminar_archivo():
            try:
                os.remove(ruta_archivo)
            except Exception as e:
                print(f"Error al eliminar el archivo: {e}")

        return response

    except Exception as e:
        return jsonify({"error": f"Error al descargar el video: {e}"}), 500

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)