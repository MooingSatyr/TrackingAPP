import pandas as pd
import os


def load_logs(path: str) -> pd.DataFrame:
    """
    Загружает один .log/.csv файл или все файлы из папки.
    Возвращает объединённый DataFrame.
    """
    dfs = []

    # Если путь — это файл
    if os.path.isfile(path):
        try:
            df = pd.read_csv(path)
            dfs.append(df)
            print(f"✅ Загружен файл: {os.path.basename(path)}")
        except Exception as e:
            print(f"⚠️ Ошибка при чтении файла {path}: {e}")

    # Если путь — это папка
    elif os.path.isdir(path):
        for name in os.listdir(path):
            file_path = os.path.join(path, name)

            # Пропускаем не-файлы и не .log/.csv
            if not os.path.isfile(file_path) or not name.lower().endswith((".log")):
                continue

            try:
                df_part = pd.read_csv(file_path)
                dfs.append(df_part)
                print(f"✅ Загружен файл: {name}")
            except Exception as e:
                print(f"⚠️ Ошибка при чтении файла {name}: {e}")
    else:
        raise FileNotFoundError("Указанный путь не найден.")

    if not dfs:
        raise ValueError("Не удалось загрузить ни одного файла.")

    df = pd.concat(dfs, ignore_index=True)
    print("📊 Загружено строк:", len(df))
    return df


# # Пример использования:
# # path = "D:/Projects/csv_to_df_parser/logs"  # Папка
# path = "D:/Projects/csv_to_df_parser/logs/20250918_105347.log"  # Один файл

# df = load_logs(path)

# print(df.describe())
