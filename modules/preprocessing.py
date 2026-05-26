import numpy as np
from scipy.signal import butter, filtfilt


def bandpass_filter(signal, fs=800, lowcut=0.5, highcut=40):
    nyquist = 0.5 * fs

    low = lowcut / nyquist
    high = highcut / nyquist

    b, a = butter(3, [low, high], btype='band')
    filtered_signal = filtfilt(b, a, signal)

    return filtered_signal


def remove_baseline(signal):
    baseline = np.mean(signal)
    return signal - baseline


def preprocess_signal(signal):
    filtered = bandpass_filter(signal, fs=800)
    centered = remove_baseline(filtered)

    return centered