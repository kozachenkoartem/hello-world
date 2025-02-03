import sys
import subprocess

def print_help():
    print("Использование: python script.py <ветка1> <ветка2>")
    print("  где <ветка1> и <ветка2> - имена двух гит веток")
    print("  --help или -h - выводит это сообщение")

def main():
    if len(sys.argv) != 3:
        print("Неверное количество параметров. Используйте --help или -h для справки.")
        return

    if sys.argv[1] in ["--help", "-h"]:
        print_help()
        return
    if sys.argv[2] in ["--help", "-h"]:
        print_help()
        return

    branch1 = sys.argv[1]
    branch2 = sys.argv[2]

    try:
        output = subprocess.check_output(["git", "diff", "--name-only", branch1, branch2])
        files = output.decode("utf-8").splitlines()
        print("Список измененных файлов между ветками {} и {}:".format(branch1, branch2))
        for file in files:
            print(file)
    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении команды git: {}".format(e))

if __name__ == "__main__":
    main()