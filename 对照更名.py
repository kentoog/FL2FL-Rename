import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, EXTENDED
from tkinterdnd2 import DND_FILES, TkinterDnD

class RenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("对照目标修改文件名240724拖拽时鼠标选中位置必须相同！")

        # 左边文件列表框
        self.left_listbox = Listbox(root, selectmode=EXTENDED, width=50, height=20)
        self.left_listbox.grid(row=1, column=0, padx=(10, 5), pady=10)

        # 右边文件列表框
        self.right_listbox = Listbox(root, selectmode=EXTENDED, width=50, height=20)
        self.right_listbox.grid(row=1, column=2, padx=(5, 10), pady=10)
        

        # 中间滚动条
        self.middle_scrollbar = Scrollbar(root, orient=tk.VERTICAL, command=self.sync_scroll, width=30)  # 默认宽度是15，这里增加一倍
        self.middle_scrollbar.grid(row=1, column=1, sticky=tk.N+tk.S, padx=5)

        self.left_listbox.config(yscrollcommand=self.middle_scrollbar.set)
        self.right_listbox.config(yscrollcommand=self.middle_scrollbar.set)

        # 数量标签
        self.count_label = tk.Label(root, text="左: 0 | 右: 0", fg="red")
        self.count_label.grid(row=2, column=1)


        # 左边打开文件按钮
        self.open_left_button = tk.Button(root, text="打开需要更名的文件列表", command=self.load_left_files)
        self.open_left_button.grid(row=0, column=0, padx=10, pady=10)
        
        # 红色文字提示 框
        self.red_label = tk.Label(root, text="拖入文件时鼠标选中位置必须相同！\n如：两侧都选中第一个文件拖入。\n 拖动中间滚动条确认全部符合预期后执行! \n （提前备份数据！）", fg="red")
        self.red_label.grid(row=0, column=1, padx=10, pady=10)
        # 右边打开文件按钮
        self.open_right_button = tk.Button(root, text="打开对照目标的文件列表", command=self.load_right_files)
        self.open_right_button.grid(row=0, column=2, padx=10, pady=10)

        # 删除按钮
        self.delete_button = tk.Button(root, text="删除", command=self.delete_selected)
        self.delete_button.grid(row=3, column=0, pady=10)

        # 清空列表按钮
        self.clear_button = tk.Button(root, text="清空列表", command=self.clear_lists)
        self.clear_button.grid(row=3, column=2, pady=10)

        # 添加拖拽功能
        self.left_listbox.drop_target_register(DND_FILES)  # type: ignore
        self.left_listbox.dnd_bind('<<Drop>>', self.load_left_files_from_dnd)  # type: ignore

        self.right_listbox.drop_target_register(DND_FILES)  # type: ignore
        self.right_listbox.dnd_bind('<<Drop>>', self.load_right_files_from_dnd)  # type: ignore

        # 一键更名按钮
        self.rename_button = tk.Button(root, text="一键更名", command=self.rename_files)
        self.rename_button.grid(row=4, column=0, columnspan=3, pady=10)

        self.left_file_paths = []

    def sync_scroll(self, *args):
        self.left_listbox.yview(*args)
        self.right_listbox.yview(*args)

    def update_counts(self):
        left_count = self.left_listbox.size()
        right_count = self.right_listbox.size()
        self.count_label.config(text=f"左: {left_count} | 右: {right_count}", fg="green" if left_count == right_count else "red")

    def load_left_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.left_listbox.delete(0, tk.END)
            self.left_file_paths = file_paths
            for file_path in file_paths:
                self.left_listbox.insert(tk.END, os.path.basename(file_path))
            self.update_counts()

    def load_right_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.right_listbox.delete(0, tk.END)
            for file_path in file_paths:
                self.right_listbox.insert(tk.END, os.path.basename(file_path))
            self.update_counts()

    def load_left_files_from_dnd(self, event):
        file_paths = self.root.tk.splitlist(event.data)
        self.left_listbox.delete(0, tk.END)
        self.left_file_paths = []
        for file_path in file_paths:
            if os.path.isfile(file_path):
                self.left_listbox.insert(tk.END, os.path.basename(file_path))
                self.left_file_paths.append(file_path)
        self.update_counts()

    def load_right_files_from_dnd(self, event):
        file_paths = self.root.tk.splitlist(event.data)
        self.right_listbox.delete(0, tk.END)
        for file_path in file_paths:
            if os.path.isfile(file_path):
                self.right_listbox.insert(tk.END, os.path.basename(file_path))
        self.update_counts()

    def delete_selected(self):
        selected_left_indices = list(self.left_listbox.curselection())
        selected_right_indices = list(self.right_listbox.curselection())

        for i in reversed(selected_left_indices):
            self.left_listbox.delete(i)
            del self.left_file_paths[i]  # type: ignore

        for i in reversed(selected_right_indices):
            self.right_listbox.delete(i)
        
        self.update_counts()

    def clear_lists(self):
        self.left_listbox.delete(0, tk.END)
        self.right_listbox.delete(0, tk.END)
        self.left_file_paths = []
        self.update_counts()

    def rename_files(self):
        left_files = self.left_listbox.get(0, tk.END)
        right_files = self.right_listbox.get(0, tk.END)

        if len(left_files) != len(right_files):
            messagebox.showerror("错误", "两边的文件数量不一致！")
            return

        for left_file, right_file in zip(self.left_file_paths, right_files):
            # 分离文件名和扩展名
            file_name, file_extension = os.path.splitext(left_file)
            # 分离右边文件的文件名和扩展名，并仅保留文件名
            right_file_name, _ = os.path.splitext(right_file)

            directory = os.path.dirname(left_file)

            new_name = os.path.join(directory, right_file_name + file_extension)
            os.rename(left_file, new_name)

        messagebox.showinfo("成功", "文件重命名完成！")
        self.left_listbox.delete(0, tk.END)
        self.update_counts()

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # 使用 TkinterDnD.Tk() 初始化
    app = RenameApp(root)
    root.mainloop()
