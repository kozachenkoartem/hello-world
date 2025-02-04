import sys

def read_file(path):
    try:
        with open(path, 'r') as file:
            for_review = file.read()
            return for_review
    except FileNotFoundError:
        print(f"Файл {path} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python script.py <путь_к_файлу>")
        sys.exit(1)

    path = sys.argv[1]
    for_review = read_file(path)
    print(for_review)