import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, Label, messagebox
import re, sys, os, subprocess, time, argparse


class VFS:
    def __init__(self, root, path_vfs=None, start_script=None):
        self.root = root
        self.root.title(path_vfs)

        if not path_vfs:
            self.path_vfs = os.getcwd()
            raise Exception(f"Не указан путь vfs")
        else: self.path_vfs = path_vfs
        self.start_script = start_script
        self.current_directory = "/home/user"
        self.script_mode = False
        self.script_commands = []

        #отладочный вывод параметров
        print(f"Параметры запуска:")
        print(f"  Путь к VFS: {self.path_vfs}")
        print(f"  Стартовый скрипт: {self.start_script}")
        print(f"  Текущая директория: {os.getcwd()}")

        self.create_widgets()

        self.input_field.focus_set()
        self.output_area.tag_config('red', foreground='red')
        self.output_area.tag_config('green', foreground='light green')
        self.output_area.tag_config('blue', foreground='light blue')

        if self.start_script: self.execute_script()

    def create_widgets(self):
        self.output_area = scrolledtext.ScrolledText(self.root, width=80, height=25, bg='black', fg='white',
                                                     font=('Arial', 10))
        self.output_area.pack(padx=0, pady=0) # отступы окна от края
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"VFS путь: {self.path_vfs}\n", 'blue')
        if self.start_script:
            self.output_area.insert(tk.END, f"Стартовый скрипт: {self.start_script}\n", 'blue')
        else: self.output_area.insert(tk.END, f"{self.current_directory}: # ", 'green')
        self.output_area.config(state=tk.DISABLED) # редактирование текста

        # строка ввода
        input_frame = Frame(self.root)
        input_frame.pack(padx=0, pady=0, fill=tk.X)

        Label(input_frame, text="> ", fg='light green', bg='black', font=('Ariel', 10)).pack(side=tk.LEFT)

        self.input_field = Entry(input_frame, bg='black', fg='white', insertbackground='white', font=('Ariel', 10))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_field.bind('<Return>', self.process_command) # привязывание Enter к функции p_c

    def parse_arguments(self, command_line):
        pattern = r'\"([^\"\\]*(?:\\.[^\"\\]*)*)\"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\'|(\S+)'
        # ^ строка нужна для разбора поступающих аргументов: тех, что в
        # двойных кавычках: \"([^\"\\]*(?:\\.[^\"\\]*)*)\"
        # ординарных: \'([^\'\\]*(?:\\.[^\'\\]*)*)\'
        # без кавычек: (\S+)
        matches = re.findall(pattern, command_line)

        args = []
        for match in matches:
            arg = next((group for group in match if group), '')
            arg = arg.replace('\\"', '"').replace("\\'", "'")
            # ^ удаление экранирования (\ перед символом)
            args.append(arg)

        return args

    def execute_script(self):
        try:
            if not os.path.exists(self.start_script): raise FileNotFoundError(f"Скрипт {self.start_script} не найден")
            with open(self.start_script, 'r', encoding='utf-8') as f:
                self.script_commands = [i.strip() for i in f if i.strip() and not i.strip().startswith('#')]
            self.script_mode = True
            self.next_script()

        except Exception as e:
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, f"Ошибка загрузки скрипта: {str(e)}\n", 'red')
            self.output_area.insert(tk.END, f"\n{self.current_directory}: # ", 'green')
            self.output_area.config(state=tk.DISABLED)
            messagebox.showerror("Ошибка", f"Не удалось загрузить скрипт: {str(e)}")

    def next_script(self):
        if not self.script_commands:
            self.script_mode = False
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, "Скрипт завершен\n", 'blue')
            self.output_area.insert(tk.END, f"\n{self.current_directory}: # ", 'green')
            self.output_area.config(state=tk.DISABLED)
            return

        command_line = self.script_commands.pop(0)
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"\n{self.current_directory}: # ", 'green')
        self.output_area.insert(tk.END, f"{command_line}\n", 'blue')
        self.output_area.config(state=tk.DISABLED)
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, command_line) #вставляем комманды из скрипта

        self.process_command(None, from_script=True)

        #time in ms before the next command
        if self.script_commands and self.script_mode: self.root.after(1000, self.next_script)


    def process_command(self, event, from_script=False):
        command_line = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)

        if not command_line: return
        args = self.parse_arguments(command_line)
        if not args: return

        command = args[0].lower()
        command_args = args[1:]

        self.output_area.config(state=tk.NORMAL) # разрешение редактирования текста
        if not from_script: self.output_area.insert(tk.END, command_line + '\n')

        try:
            if command == 'exit': self.root.quit()
            elif command == 'ls': self.cmd_ls(command_args)
            elif command == 'cd': self.cmd_cd(command_args)
            elif command == 'help': self.cmd_help()
            elif command == 'pwd': self.cmd_pwd()
            else:
                raise Exception(f"Неизвестная команда: {command}")

        except Exception as e:
            self.output_area.insert(tk.END, f"Ошибка выполнения: {str(e)}\n", 'red')
            if self.script_mode:
                self.script_mode = False
                messagebox.showerror("Ошибка скрипта", f"Скрипт остановлен: {str(e)}")

        if not self.script_mode:
            self.output_area.insert(tk.END, f"\n{self.current_directory}: # ", 'green')
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def cmd_ls(self, args):
        self.output_area.insert(tk.END, f"Команда: ls\n")
        self.output_area.insert(tk.END, f"Аргументы: {args}\n")

    def cmd_cd(self, args):
        if len(args) > 1: raise Exception("Слишком много аргументов для команды cd")
        elif args:
            new_dir = args[0]
            if new_dir == "..": self.current_directory = "/home"
            elif new_dir == "/": self.current_directory = "/"
            elif new_dir == "~": self.current_directory = "/home/user"
            else: self.current_directory = f"{self.current_directory}/{new_dir}"

            self.output_area.insert(tk.END, f"Текущий каталог изменен на: {self.current_directory}\n")

        else: self.current_directory = "/home"

    def cmd_pwd(self):
        self.output_area.insert(tk.END, f"{self.current_directory}\n")

    def cmd_help(self):
        self.output_area.insert(tk.END, "Доступные команды:\n")
        self.output_area.insert(tk.END, "  ls [аргументы]    - список файлов и каталогов\n")
        self.output_area.insert(tk.END, "  cd [каталог]        - сменить текущий каталог\n")
        self.output_area.insert(tk.END, "  pwd                    - показать текущий каталог\n")
        self.output_area.insert(tk.END, "  exit                    - выход из системы\n")
        self.output_area.insert(tk.END, "  help                   - показать эту справку\n")


def parse_arguments():
    parser = argparse.ArgumentParser(description='VFS Emulator')
    parser.add_argument('--vfs-path', '-v', help='Путь к физическому расположению VFS')
    parser.add_argument('--script', '-s', help='Путь к стартовому скрипту')

    return parser.parse_args()

#-------------------------------------------------

# def create_test_scripts():
#     scripts_dir = "test_scripts"
#     os.makedirs(scripts_dir, exist_ok=True)
#
#     # скрипт 1: базовые команды
#     script1 = os.path.join(scripts_dir, "test_basic.vfs")
#     with open(script1, 'w', encoding='utf-8') as f:
#         f.write("""
# # Базовый тестовый скрипт
# pwd
# ls -l
# cd /home
# pwd
# ls
# """)
#
#     # скрипт 2: тест скрипта с ошибкой
#     script2 = os.path.join(scripts_dir, "test_error.vfs")
#     with open(script2, 'w', encoding='utf-8') as f:
#         f.write("""
# # Скрипт с ошибкой
# pwd
# unknown_command  # Эта команда вызовет ошибку
# pwd "Эта строка не будет выполнена"
# """)
#
#     # скрипт 3: тест кавычек
#     script3 = os.path.join(scripts_dir, "test_quotes.vfs")
#     with open(script3, 'w', encoding='utf-8') as f:
#         f.write("""
# # Тест аргументов в кавычках
# ls -l "file with spaces.txt"
# cd "My Documents"
# pwd
# """)

#-----------------------------------------------


def main():
    args = parse_arguments()
    #create_test_scripts()
    root = tk.Tk()
    VFS(root, path_vfs=args.vfs_path, start_script=args.script)
    root.mainloop()



if __name__ == "__main__":
    main()