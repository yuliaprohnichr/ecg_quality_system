import numpy as np
from scipy.signal import find_peaks


def calculate_snr(original_signal, processed_signal):
    noise = original_signal - processed_signal
    signal_power = np.mean(processed_signal ** 2)
    noise_power = np.mean(noise ** 2)

    if noise_power == 0:
        return 100

    return round(10 * np.log10(signal_power / noise_power), 2)


def calculate_rms(signal):
    return np.sqrt(np.mean(signal ** 2))


def detect_r_peaks(signal, fs):
    min_distance = int(0.4 * fs)

    peaks, _ = find_peaks(
        signal,
        distance=min_distance,
        prominence=np.std(signal)
    )

    return peaks


def calculate_heart_rate(peaks, fs):
    if len(peaks) < 2:
        return "Недостатньо даних"

    rr_intervals = np.diff(peaks) / fs
    mean_rr = np.mean(rr_intervals)

    if mean_rr == 0:
        return "Недостатньо даних"

    return round(float(60 / mean_rr), 2)


def calculate_rhythm_statistics(peaks, fs):
    if len(peaks) < 2:
        return {
            "Середній RR-інтервал": "Недостатньо даних",
            "Мінімальний RR-інтервал": "Недостатньо даних",
            "Максимальний RR-інтервал": "Недостатньо даних",
            "Мінімальна ЧСС": "Недостатньо даних",
            "Максимальна ЧСС": "Недостатньо даних",
        }

    rr_intervals = np.diff(peaks) / fs

    mean_rr = round(float(np.mean(rr_intervals)), 3)
    min_rr = round(float(np.min(rr_intervals)), 3)
    max_rr = round(float(np.max(rr_intervals)), 3)

    min_hr = round(float(60 / max_rr), 2)
    max_hr = round(float(60 / min_rr), 2)

    return {
        "Середній RR-інтервал": f"{mean_rr} с",
        "Мінімальний RR-інтервал": f"{min_rr} с",
        "Максимальний RR-інтервал": f"{max_rr} с",
        "Мінімальна ЧСС": f"{min_hr} уд/хв",
        "Максимальна ЧСС": f"{max_hr} уд/хв",
    }


def evaluate_quality(snr, noise_level):
    if snr >= 15 and noise_level < 0.3:
        return "Якісний сигнал"
    elif snr >= 8:
        return "Сигнал середньої якості"
    else:
        return "Зашумлений сигнал"


def generate_conclusion(quality, snr, noise_level):
    if quality == "Якісний сигнал":
        return (
            f"Сигнал має достатній рівень якості. Значення SNR становить {snr} дБ, "
            f"а рівень шуму є невисоким ({noise_level}). Форма основних компонентів ЕКГ "
            f"після обробки збережена, тому сигнал придатний для подальшого аналізу."
        )

    elif quality == "Сигнал середньої якості":
        return (
            f"Сигнал має середній рівень якості. Значення SNR становить {snr} дБ, "
            f"що вказує на наявність помірного шуму. Після фільтрації основна форма "
            f"ЕКГ-сигналу збережена, однак для точнішого аналізу бажано використовувати "
            f"додаткову попередню обробку."
        )

    else:
        return (
            f"Сигнал має низьку якість. Значення SNR становить {snr} дБ, "
            f"а рівень шуму є підвищеним ({noise_level}). Такий сигнал може містити "
            f"значні спотворення, тому його використання для подальшого аналізу потребує "
            f"обережності або повторної реєстрації."
        )


def calculate_metrics(original_signal, processed_signal, fs=800):
    noise = original_signal - processed_signal

    snr = calculate_snr(original_signal, processed_signal)
    noise_level = round(float(np.std(noise)), 4)
    rms_value = round(float(calculate_rms(original_signal)), 4)
    peak_to_peak = round(float(np.max(original_signal) - np.min(original_signal)), 4)

    r_peaks = detect_r_peaks(processed_signal, fs)
    heart_rate = calculate_heart_rate(r_peaks, fs)
    rhythm_stats = calculate_rhythm_statistics(r_peaks, fs)

    quality = evaluate_quality(snr, noise_level)

    metrics = {
        "Кількість відліків": len(original_signal),
        "Частота дискретизації": f"{fs} Гц",
        "Кількість знайдених R-піків": len(r_peaks),
        "Орієнтовна ЧСС": f"{heart_rate} уд/хв",
        "Середній RR-інтервал": rhythm_stats["Середній RR-інтервал"],
        "Мінімальний RR-інтервал": rhythm_stats["Мінімальний RR-інтервал"],
        "Максимальний RR-інтервал": rhythm_stats["Максимальний RR-інтервал"],
        "Мінімальна ЧСС": rhythm_stats["Мінімальна ЧСС"],
        "Максимальна ЧСС": rhythm_stats["Максимальна ЧСС"],
        "Мінімальна амплітуда": round(float(np.min(original_signal)), 4),
        "Максимальна амплітуда": round(float(np.max(original_signal)), 4),
        "Пікова амплітуда": peak_to_peak,
        "Середнє значення": round(float(np.mean(original_signal)), 4),
        "Дисперсія": round(float(np.var(original_signal)), 4),
        "Стандартне відхилення": round(float(np.std(original_signal)), 4),
        "RMS": rms_value,
        "Енергія сигналу": round(float(np.sum(original_signal ** 2)), 4),
        "Рівень шуму": noise_level,
        "SNR": f"{snr} дБ",
        "Оцінка якості": quality,
    }

    conclusion = generate_conclusion(quality, snr, noise_level)

    return metrics, conclusion