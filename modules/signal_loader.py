import os
import pandas as pd


def load_ecg_signal(file_path, ecg_column=3):

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in [".csv", ".txt"]:

        data = pd.read_csv(
            file_path,
            header=None,
            sep=None,
            engine="python"
        )

    elif file_extension in [".xlsx", ".xls"]:

        data = pd.read_excel(
            file_path,
            header=None
        )

    else:
        raise ValueError(
            "Непідтримуваний формат файлу"
        )

    if data.empty:
        raise ValueError(
            "Файл не містить даних"
        )

    if ecg_column >= data.shape[1]:
        raise ValueError(
            "У файлі немає такої колонки"
        )

    signal = pd.to_numeric(
        data.iloc[:, ecg_column],
        errors="coerce"
    )

    signal = signal.dropna().values.astype(float)

    if len(signal) == 0:
        raise ValueError(
            "Колонка ЕКГ порожня або містить нечислові дані"
        )

    return signal