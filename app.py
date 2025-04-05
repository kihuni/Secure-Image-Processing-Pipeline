import pulumi_esc_sdk as esc
import os
import json
import logging
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from pcloud import PyCloud
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Ensure the upload and results directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs("results", exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def process_image(image_path):
    try:
        # Fetch secrets and configs from Pulumi ESC
        client = esc.EscClient(esc.Configuration(access_token=os.getenv("PULUMI_ACCESS_TOKEN")))
        env, values, _ = client.open_and_read_environment("kihuni", "Secure-Multi-Cloud-Backup-Orchestrator ", "dev-environment")

        # pCloud credentials
        pcloud_username = values["pcloud:username"]
        pcloud_password = values["pcloud:password"]
        pcloud_folder_path = values["pcloud:folderPath"]

        # Clarifai API key
        clarifai_api_key = values["clarifai:apiKey"]

        # Process the image with Clarifai
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)
        metadata = (("authorization", f"Key {clarifai_api_key}"),)

        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        request = service_pb2.PostModelOutputsRequest(
            model_id="aaa03c23b3724a16a56b629203edc62c",  # General model for label detection
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(base64=image_data)
                    )
                )
            ],
        )
        response = stub.PostModelOutputs(request, metadata=metadata)
        if response.status.code != status_code_pb2.SUCCESS:
            raise RuntimeError(f"Clarifai API error: {response.status.description}")

        labels = [concept.name for concept in response.outputs[0].data.concepts]
        logging.info(f"Detected labels: {labels}")

        # Save results locally
        results = {"image": image_path, "labels": labels}
        output_path = os.path.join("results", "analysis_results.json")
        with open(output_path, "w") as f:
            json.dump(results, f)

        # Upload to pCloud
        pcloud = PyCloud(pcloud_username, pcloud_password)
        pcloud.uploadfile(files=[output_path], path=pcloud_folder_path)

        logging.info(f"Uploaded analysis results to pCloud in folder: {pcloud_folder_path}")
        return labels, output_path

    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        raise
    except RuntimeError as e:
        logging.error(f"API error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", error="No file part")
        file = request.files["file"]
        if file.filename == "":
            return render_template("index.html", error="No file selected")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(image_path)

            try:
                labels, output_path = process_image(image_path)
                return render_template("result.html", labels=labels, output_path=output_path, image_filename=filename)
            except Exception as e:
                return render_template("index.html", error=str(e))
        else:
            return render_template("index.html", error="Invalid file type")
    return render_template("index.html", error=None)

@app.route("/results/<filename>")
def serve_results(filename):
    return send_from_directory("results", filename)

@app.route("/uploads/<filename>")
def serve_uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)