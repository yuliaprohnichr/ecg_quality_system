import os
from flask import Flask, render_template, request, send_file

from modules.signal_loader import load_ecg_signal
from modules.preprocessing import preprocess_signal
from modules.quality_metrics import calculate_metrics

from modules.visualization import (
    create_signal_plots_dict,
    create_pdf_plot_images
)

from modules.pdf_report import generate_pdf_report


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

last_metrics = None
last_conclusion = None
last_plot_images = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    global last_metrics, last_conclusion, last_plot_images

    if "file" not in request.files:
        return "Файл не знайдено"

    file = request.files["file"]

    if file.filename == "":
        return "Файл не вибрано"

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(file_path)

    ecg_column = int(
        request.form.get("ecg_column", 3)
    )

    sampling_rate = int(
        request.form.get("sampling_rate", 800)
    )

    original_signal = load_ecg_signal(
        file_path,
        ecg_column=ecg_column
    )

    processed_signal = preprocess_signal(
        original_signal
    )

    metrics, conclusion = calculate_metrics(
        original_signal,
        processed_signal,
        sampling_rate
    )

    plots = create_signal_plots_dict(
        original_signal,
        processed_signal,
        sampling_rate
    )

    plot_images = create_pdf_plot_images(
        original_signal,
        processed_signal,
        sampling_rate
    )

    last_metrics = metrics
    last_conclusion = conclusion
    last_plot_images = plot_images

    return render_template(
        "results.html",
        metrics=metrics,
        conclusion=conclusion,
        plots=plots
    )


@app.route("/download-report")
def download_report():
    if last_metrics is None or last_conclusion is None:
        return "Спочатку виконайте аналіз сигналу"

    filename = generate_pdf_report(
        last_metrics,
        last_conclusion,
        last_plot_images
    )

    return send_file(
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)