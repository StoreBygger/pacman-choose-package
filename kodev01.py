import subprocess
import webbrowser

import sys
import tty
import termios


def check_ctrl_c(key):

    if key == "\x03":
        exit(0)


def read_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        check_ctrl_c(ch)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class package:

    def __init__(self, name, version, info, path, extra):
        self.name = name
        self.version = version
        self.info = info
        self.path = path
        self.extra = extra

    def __str__(self):
        n = self.name
        v = self.version
        i = self.info
        p = self.path
        e = self.extra

        output = f"name\t: {n}\n"
        output += f"version\t: {v}\n"
        output += f"info\t: {i}\n"
        output += f"path\t: {p}\n"
        output += f"extra\t: {e}\n"
        return output


def package_split(pkg) -> tuple:
    pkg_path_version_list = pkg.split(sep=" ", maxsplit=-1)
    pkg_path_name_list = pkg_path_version_list[0].split(sep="/", maxsplit=-1)

    name = pkg_path_name_list[-1]
    path = pkg_path_version_list[0]
    version = pkg_path_version_list[1]
    extra = ""

    if len(pkg_path_version_list) == 3:
        extra = pkg_path_version_list[2]

    return name, version, path, extra


def get_package_list(cmd=["sudo", "pacman", "-Qs"]) -> list:
    print("Using command {cmd} to get package details")
    cmd_result = subprocess.run(cmd, capture_output=True)

    if cmd_result.stderr == b"":
        pass
    else:
        print("The process failed with error msg: ")
        print(cmd_result.stderr)
        exit(1)

    result_string = cmd_result.stdout.decode("utf-8")
    return result_string.split(sep="\n", maxsplit=-1)


# print(lst)
def package_make(path_version, info) -> package:
    name, version, path, extra = package_split(path_version)
    info = info[4:]
    return package(name, version, info, path, extra)


def package_make_class_list(cmd_result_list) -> list:

    package_list = []
    for i in range(0, len(cmd_result_list) - 1, 2):
        path_version = cmd_result_list[i]
        info = cmd_result_list[i + 1]

        pkg = package_make(path_version, info)
        package_list.append(pkg)

    return package_list


def package_ask(package) -> str:
    while 1:
        print(f"\n---\nDo you want to add package:\n{package} \n(y/n/q/s/h): ")
        cmd = read_key()
        if cmd == "q":
            print("Exiting")
            return "q"
        elif cmd == "n":
            return "n"
        elif cmd == "y":
            return "y"
        elif cmd == "s":
            webbrowser.open(url=f"www.google.com/search?q={package.name}")
        elif cmd == "h":
            print("q: quit\nn: no\ny: yes\ns: search (google)\nh: help")
        else:
            print(f"Wrong input [{cmd}], try again")
    return "f"


def pkg_print_list(pkg_list):
    for pkg in pkg_list:
        print(pkg)


def pkg_lst_ask(pkg_lst) -> list:

    print(f"{len(pkg_lst)} packages to query")

    approved_pkg_lst = []
    denied_pkg_lst = []
    failed_pkg_lst = []

    i = 0

    for pkg in pkg_lst:
        action = package_ask(pkg)

        if action == "q":
            break
        elif action == "y":
            approved_pkg_lst.append(pkg)
        elif action == "n":
            denied_pkg_lst.append(pkg)
        else:
            failed_pkg_lst.append(pkg)
        i += 1

    print(f"{i} packages queried")
    print(f"{len(approved_pkg_lst)} got approved")
    print(f"{len(denied_pkg_lst)} got denied")
    print(f"{len(failed_pkg_lst)} failed")

    print("Do you want to see approved package list? (y/n)")
    cmd = read_key().lower()
    if cmd == "y":
        pkg_print_list(approved_pkg_lst)

    print("Do you want to see denied package list? (y/n)")
    cmd = read_key().lower()
    if cmd == "y":
        pkg_print_list(denied_pkg_lst)

    print("Do you want to see failed package list? (y/n)")
    cmd = read_key().lower()
    if cmd == "y":
        pkg_print_list(failed_pkg_lst)

    return approved_pkg_lst


def pkg_lst_write(pkg_list, file):
    f = open(file, "a")
    for pkg in pkg_list:
        f.write(pkg.name + "\n")


def pkg_ask_and_write_to_file(cmd=[], file="requirements.txt"):
    cmd_result = []

    if cmd == []:
        cmd_result += get_package_list()
    else:
        cmd_result += get_package_list(cmd)

    pkg_list = package_make_class_list(cmd_result)

    approved_packages = pkg_lst_ask(pkg_list)

    print(f"File in question:\n{file}\n")

    print(f"Write {len(approved_packages)} packages to file? (y/n)")
    action = read_key().lower()

    if action == "y":
        pkg_lst_write(approved_packages, file)

    print(f"Approved packages written to\n {file}")


def main():
    print("Write CMD to use ('n' for default cmd)")
    cmd = input("\t<>")

    cmd_lst = []

    if cmd.lower() != "n":
        print(f"Using '{cmd}' as command")
        cmd_lst = cmd.split(sep=" ", maxsplit=-1)
    else:
        print("Using default command")

    print("\nWrite path to file to use ('n' for default path)")
    cmd = input("\t<>")
    path = "requirements.txt"

    if cmd.lower() != "n":
        print(f"Using'{cmd}' as path")
        path = cmd
    else:
        print("Using default path")

    pkg_ask_and_write_to_file(cmd_lst, path)


if __name__ == "__main__":
    main()
