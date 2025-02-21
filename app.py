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

        # Opciones para listar formatos disponibles
        ydl_opts_listar = {}
        with yt_dlp.YoutubeDL(ydl_opts_listar) as ydl:
            info = ydl.extract_info(url, download=False)  # Obtener información del video sin descargar
            formatos_disponibles = info.get("formats", [])  # Obtener los formatos disponibles

        # Verificar si la calidad seleccionada está disponible
        formato_seleccionado = None
        for formato in formatos_disponibles:
            if calidad == "best" and formato.get("format_note") == "best":
                formato_seleccionado = formato["format_id"]
                break
            elif calidad == "worst" and formato.get("format_note") == "worst":
                formato_seleccionado = formato["format_id"]
                break
            elif calidad == f"best[height<={formato.get('height', 0)}]":
                formato_seleccionado = formato["format_id"]
                break

        if not formato_seleccionado:
            return jsonify({"error": f"La calidad seleccionada no está disponible para este video."}), 400

        # Opciones de descarga
        opciones = {
            'format': formato_seleccionado,  # Usar el formato seleccionado
            'outtmpl': os.path.join("downloads", "%(title)s.%(ext)s"),  # Nombre del archivo con el título del video
            'merge_output_format': 'mp4',  # Asegurar formato MP4
        }

        with yt_dlp.YoutubeDL(opciones) as ydl:
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
    app.run(debug=True)