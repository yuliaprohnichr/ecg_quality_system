import os
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from scipy.signal import find_peaks


VISIBLE_SAMPLES = 4000


def prepare_plots_folder():
    folder = "static/plots"
    os.makedirs(folder, exist_ok=True)
    return folder


def create_time_axis(signal, fs):
    visible_length = min(len(signal), VISIBLE_SAMPLES)
    return np.arange(visible_length) / fs


def create_single_plot(signal, title, line_name, color, fs=800):
    visible_signal = signal[:VISIBLE_SAMPLES]
    time_axis = create_time_axis(signal, fs)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_axis,
        y=visible_signal,
        mode="lines",
        name=line_name,
        line=dict(color=color)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Час, с",
        yaxis_title="Амплітуда ЕКГ-сигналу, умовні одиниці",
        template="plotly_white",
        autosize=False,
        width=700,
        height=430
    )

    return pio.to_html(fig, full_html=False)


def create_r_peaks_plot(signal, fs=800):
    visible_signal = signal[:VISIBLE_SAMPLES]
    time_axis = create_time_axis(signal, fs)

    peaks, _ = find_peaks(
        visible_signal,
        distance=int(0.4 * fs),
        prominence=np.std(visible_signal)
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_axis,
        y=visible_signal,
        mode="lines",
        name="Оброблений ЕКГ-сигнал",
        line=dict(color="green")
    ))

    fig.add_trace(go.Scatter(
        x=time_axis[peaks],
        y=visible_signal[peaks],
        mode="markers",
        name="Виявлені R-піки",
        marker=dict(color="orange", size=8)
    ))

    fig.update_layout(
        title="Виявлення R-піків на ЕКГ-сигналі",
        xaxis_title="Час, с",
        yaxis_title="Амплітуда ЕКГ-сигналу, умовні одиниці",
        template="plotly_white",
        autosize=False,
        width=700,
        height=430
    )

    return pio.to_html(fig, full_html=False)


def create_spectrum_plot(signal, title, color, fs=800):
    fft_values = np.fft.fft(signal)

    fft_frequencies = np.fft.fftfreq(
        len(signal),
        d=1 / fs
    )

    positive_freqs = fft_frequencies[:len(signal) // 2]
    positive_magnitude = np.abs(fft_values[:len(signal) // 2])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=positive_freqs,
        y=positive_magnitude,
        mode="lines",
        name="Амплітудний спектр",
        line=dict(color=color)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Частота, Гц",
        yaxis_title="Амплітуда спектра, умовні одиниці",
        template="plotly_white",
        autosize=False,
        width=700,
        height=430
    )

    return pio.to_html(fig, full_html=False)


def create_signal_plots_dict(original_signal, processed_signal, fs=800):
    noise_signal = original_signal - processed_signal

    return {
        "original": create_single_plot(
            original_signal,
            "Початковий ЕКГ-сигнал",
            "Початковий сигнал",
            "blue",
            fs
        ),

        "processed": create_single_plot(
            processed_signal,
            "Оброблений ЕКГ-сигнал після фільтрації",
            "Оброблений сигнал",
            "green",
            fs
        ),

        "noise": create_single_plot(
            noise_signal,
            "Шумовий компонент, видалений під час обробки",
            "Шумовий компонент",
            "red",
            fs
        ),

        "r_peaks": create_r_peaks_plot(
            processed_signal,
            fs
        ),

        "spectrum": create_spectrum_plot(
            original_signal,
            "Спектральний аналіз ЕКГ-сигналу",
            "purple",
            fs
        )
    }


def save_plot_image(fig, filename):
    folder = prepare_plots_folder()
    path = os.path.join(folder, filename)

    fig.write_image(
        path,
        width=1100,
        height=420,
        scale=2
    )

    return path


def create_ecg_fragment_image(processed_signal, fs=800):
    visible_signal = processed_signal[:VISIBLE_SAMPLES]
    time_axis = create_time_axis(processed_signal, fs)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_axis,
        y=visible_signal,
        mode="lines",
        name="Оброблений ЕКГ-сигнал",
        line=dict(color="#00AEEF", width=2)
    ))

    fig.update_layout(
        title="Фрагмент обробленого ЕКГ-сигналу",
        xaxis_title="Час, секунди",
        yaxis_title="Амплітуда ЕКГ-сигналу, умовні одиниці",
        template="plotly_dark",
        paper_bgcolor="#06111F",
        plot_bgcolor="#06111F",
        font=dict(color="white"),
        margin=dict(l=50, r=30, t=60, b=45)
    )

    return save_plot_image(
        fig,
        "ecg_fragment.png"
    )


def create_r_peaks_image(processed_signal, fs=800):
    visible_signal = processed_signal[:VISIBLE_SAMPLES]
    time_axis = create_time_axis(processed_signal, fs)

    peaks, _ = find_peaks(
        visible_signal,
        distance=int(0.4 * fs),
        prominence=np.std(visible_signal)
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time_axis,
        y=visible_signal,
        mode="lines",
        name="Оброблений ЕКГ-сигнал",
        line=dict(color="#00AEEF", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=time_axis[peaks],
        y=visible_signal[peaks],
        mode="markers",
        name="Виявлені R-піки",
        marker=dict(color="#22C55E", size=8)
    ))

    fig.update_layout(
        title="Виявлення R-піків",
        xaxis_title="Час, с",
        yaxis_title="Амплітуда ЕКГ-сигналу, умовні одиниці",
        template="plotly_dark",
        paper_bgcolor="#06111F",
        plot_bgcolor="#06111F",
        font=dict(color="white"),
        margin=dict(l=50, r=30, t=60, b=45)
    )

    return save_plot_image(
        fig,
        "r_peaks.png"
    )


def create_spectrum_image(original_signal, fs=800):
    fft_values = np.fft.fft(original_signal)

    fft_frequencies = np.fft.fftfreq(
        len(original_signal),
        d=1 / fs
    )

    positive_freqs = fft_frequencies[:len(original_signal) // 2]
    positive_magnitude = np.abs(fft_values[:len(original_signal) // 2])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=positive_freqs,
        y=positive_magnitude,
        mode="lines",
        name="Амплітудний спектр",
        line=dict(color="#A855F7", width=2)
    ))

    fig.update_layout(
        title="Спектральний аналіз ЕКГ-сигналу",
        xaxis_title="Частота, Гц",
        yaxis_title="Амплітуда спектра, умовні одиниці",
        template="plotly_dark",
        paper_bgcolor="#06111F",
        plot_bgcolor="#06111F",
        font=dict(color="white"),
        margin=dict(l=50, r=30, t=60, b=45)
    )

    return save_plot_image(
        fig,
        "spectrum.png"
    )


def create_pdf_plot_images(original_signal, processed_signal, fs=800):
    return {
        "ecg_fragment": create_ecg_fragment_image(
            processed_signal,
            fs
        ),

        "r_peaks": create_r_peaks_image(
            processed_signal,
            fs
        ),

        "spectrum": create_spectrum_image(
            original_signal,
            fs
        )
    }