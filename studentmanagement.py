import tkinter as tk
from tkinter import messagebox, ttk
from psycopg2 import sql

class DatabaseApp:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.cur = self.conn.cursor()
        self.create_table()  # Create the table if it doesn't exist
        self.root.title("Student Management")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        self.create_widgets()
        self.reload_list()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER NOT NULL,
            gender VARCHAR(10) NOT NULL,
            major VARCHAR(100) NOT NULL
        );
        """
        self.cur.execute(create_table_query)
        self.conn.commit()

    def create_widgets(self):
        # Tạo style cho các nút
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10, "bold"), background="#FFC0CB", foreground="black", padding=6)
        style.map("TButton", background=[('active', '#45a049')], relief=[('pressed', 'sunken')])

        # Frame đầu tiên để nhập thông tin (2 dòng)
        frame_top = tk.Frame(self.root, bg='#f0f0f0')
        frame_top.pack(pady=10, padx=10, fill='x')

        tk.Label(frame_top, text="Name:", bg='#f0f0f0', font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_name = tk.Entry(frame_top, font=("Helvetica", 10))
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_top, text="Age:", bg='#f0f0f0', font=("Helvetica", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_age = tk.Entry(frame_top, font=("Helvetica", 10))
        self.entry_age.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_top, text="Gender:", bg='#f0f0f0', font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_gender = tk.Entry(frame_top, font=("Helvetica", 10))
        self.entry_gender.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_top, text="Major:", bg='#f0f0f0', font=("Helvetica", 10)).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_major = tk.Entry(frame_top, font=("Helvetica", 10))
        self.entry_major.grid(row=1, column=3, padx=5, pady=5)

        # Frame giữa để chứa các nút chức năng
        frame_buttons = tk.Frame(self.root, bg='#f0f0f0')
        frame_buttons.pack(pady=10)

        btn_add = ttk.Button(frame_buttons, text="Add Student", command=self.add_student)
        btn_add.grid(row=0, column=0, padx=5, pady=5)

        btn_delete = ttk.Button(frame_buttons, text="Delete Student", command=self.delete_student)
        btn_delete.grid(row=0, column=1, padx=5, pady=5)

        btn_update = ttk.Button(frame_buttons, text="Update Student", command=self.update_student)
        btn_update.grid(row=0, column=2, padx=5, pady=5)

        btn_reload = ttk.Button(frame_buttons, text="Reload List", command=self.reload_list)
        btn_reload.grid(row=0, column=3, padx=5, pady=5)

        # Frame dưới để chứa danh sách sinh viên
        frame_bottom = tk.Frame(self.root)
        frame_bottom.pack(pady=10, padx=10, fill='both', expand=True)

        self.tree = ttk.Treeview(frame_bottom, columns=("ID", "Name", "Age", "Gender", "Major"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Age", text="Age")
        self.tree.heading("Gender", text="Gender")
        self.tree.heading("Major", text="Major")

        self.tree.column("ID", anchor="center", width=50)
        self.tree.column("Name", anchor="center", width=150)
        self.tree.column("Age", anchor="center", width=50)
        self.tree.column("Gender", anchor="center", width=100)
        self.tree.column("Major", anchor="center", width=150)

        self.tree.pack(padx=10, pady=5, fill='both', expand=True)

        # Add a scrollbar for the Treeview
        self.scrollbar = ttk.Scrollbar(frame_bottom, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_student(self):
        name = self.entry_name.get()
        try:
            age = int(self.entry_age.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Age must be a number.")
            return
        gender = self.entry_gender.get()
        major = self.entry_major.get()
        if name and age and gender and major:
            self.cur.execute("INSERT INTO students (name, age, gender, major) VALUES (%s, %s, %s, %s)", (name, age, gender, major))
            self.conn.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            self.reload_list()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    def update_student(self):
        selected = self.tree.selection()
        if selected:
            student_id = self.tree.item(selected[0])['values'][0]
            name = self.entry_name.get()
            try:
                age = int(self.entry_age.get())
            except ValueError:
                messagebox.showwarning("Input Error", "Age must be a number.")
                return
            gender = self.entry_gender.get()
            major = self.entry_major.get()
            if name and age and gender and major:
                self.cur.execute("UPDATE students SET name=%s, age=%s, gender=%s, major=%s WHERE id=%s", (name, age, gender, major, student_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Student updated successfully!")
                self.reload_list()
            else:
                messagebox.showwarning("Input Error", "Please fill in all fields.")
        else:
            messagebox.showwarning("Selection Error", "Please select a student to update.")

    def delete_student(self):
        selected = self.tree.selection()
        if selected:
            student_id = self.tree.item(selected[0])['values'][0]
            self.cur.execute("DELETE FROM students WHERE id=%s", (student_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Student deleted successfully!")
            self.reload_list()
        else:
            messagebox.showwarning("Selection Error", "Please select a student to delete.")

    def reload_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cur.execute("SELECT * FROM students")
        for row in self.cur.fetchall():
            self.tree.insert("", tk.END, values=row)

    def on_closing(self):
        self.cur.close()
        self.conn.close()
        self.root.destroy()
