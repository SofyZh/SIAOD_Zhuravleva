import tkinter as tk
from tkinter import scrolledtext, Entry, Frame, Label
import re
import sys


class VFS:
    def __init__(self, root):
        self.root = root
        self.root.title("VFS")

        self.current_directory = "/home/user"

        self.create_widgets()

        self.input_field.focus_set()
        self.output_area.tag_config('red', foreground='red')
        self.output_area.tag_config('green', foreground='light green')

    def create_widgets(self):
        self.output_area = scrolledtext.ScrolledText(self.root, width=80, height=25, bg='black', fg='white',
                                                     font=('Arial', 10))
        self.output_area.pack(padx=0, pady=0) # отступы окна от края
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, f"{self.current_directory}: # ", 'green')
        self.output_area.config(state=tk.DISABLED) # редактирование текста

        # строка ввода
        input_frame = Frame(self.root)
        input_frame.pack(padx=0, pady=0, fill=tk.X)

        Label(input_frame, text="> ", fg='light green', bg='black', font=('Ariel', 10)).pack(side=tk.LEFT)

        self.input_field = Entry(input_frame, bg='black', fg='white', insertbackground='black', font=('Ariel', 10))
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

    def process_command(self, event):
        command_line = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)

        if not command_line: return

        args = self.parse_arguments(command_line)
        if not args: return

        command = args[0].lower()
        command_args = args[1:]

        self.output_area.config(state=tk.NORMAL) # разрешение редактирования текста
        self.output_area.insert(tk.END, command_line + '\n')

        if command == 'exit': self.root.quit()
        elif command == 'ls': self.cmd_ls(command_args)
        elif command == 'cd': self.cmd_cd(command_args)
        elif command == 'help': self.cmd_help()
        else: self.output_area.insert(tk.END, f"Ошибка: команда '{command}' не найдена.\n", 'red')

        # Добавляем приглашение для следующей команды
        self.output_area.insert(tk.END, f"{self.current_directory}: # ", 'green')
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def cmd_ls(self, args):
        self.output_area.insert(tk.END, f"Команда: ls\n")
        self.output_area.insert(tk.END, f"Аргументы: {args}\n")

    def cmd_cd(self, args):
        if len(args) > 1: self.output_area.insert(tk.END, "Ошибка: слишком много аргументов для команды cd\n")
        elif args:
            self.output_area.insert(tk.END, f"Команда: cd\n")
            self.output_area.insert(tk.END, f"Аргументы: {args}\n")
            # Симулируем изменение каталога
            new_dir = args[0]
            if new_dir == "..": self.current_directory = "/home"
            elif new_dir == "/": self.current_directory = "/"
            else: self.current_directory = f"{self.current_directory}/{new_dir}"

            self.output_area.insert(tk.END, f"Текущий каталог изменен на: {self.current_directory}\n")

        else: self.output_area.insert(tk.END, "Ошибка: не указан аргумент для команды cd\n")

    def cmd_help(self):
        self.output_area.insert(tk.END, "Доступные команды:\n")
        self.output_area.insert(tk.END, "  ls [аргументы]    - список файлов и каталогов\n")
        self.output_area.insert(tk.END, "  cd [каталог]        - сменить текущий каталог\n")
        self.output_area.insert(tk.END, "  exit                    - выход из системы\n")
        self.output_area.insert(tk.END, "  help                   - показать эту справку\n")



def main():
    root = tk.Tk()
    app = VFS(root)
    root.mainloop()


if __name__ == "__main__":
    main()