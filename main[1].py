import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'students.db')

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            department TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("850x480")
        # Top Frame - Form
        form_frame = tk.Frame(root, padx=10, pady=10)
        form_frame.pack(fill='x')

        tk.Label(form_frame, text="Reg No").grid(row=0, column=0, sticky='w')
        tk.Label(form_frame, text="Name").grid(row=0, column=2, sticky='w')
        tk.Label(form_frame, text="Age").grid(row=1, column=0, sticky='w')
        tk.Label(form_frame, text="Gender").grid(row=1, column=2, sticky='w')
        tk.Label(form_frame, text="Department").grid(row=2, column=0, sticky='w')
        tk.Label(form_frame, text="Email").grid(row=2, column=2, sticky='w')

        self.reg_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.email_var = tk.StringVar()

        tk.Entry(form_frame, textvariable=self.reg_var, width=20).grid(row=0, column=1, padx=5, pady=4)
        tk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=0, column=3, padx=5, pady=4)
        tk.Entry(form_frame, textvariable=self.age_var, width=20).grid(row=1, column=1, padx=5, pady=4)
        ttk.Combobox(form_frame, textvariable=self.gender_var, values=['Male','Female','Other'], width=18).grid(row=1, column=3, padx=5, pady=4)
        tk.Entry(form_frame, textvariable=self.dept_var, width=20).grid(row=2, column=1, padx=5, pady=4)
        tk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=2, column=3, padx=5, pady=4)

        btn_frame = tk.Frame(root, pady=6)
        btn_frame.pack(fill='x')
        tk.Button(btn_frame, text="Add", width=12, command=self.add_student).pack(side='left', padx=6)
        tk.Button(btn_frame, text="Update", width=12, command=self.update_student).pack(side='left', padx=6)
        tk.Button(btn_frame, text="Delete", width=12, command=self.delete_student).pack(side='left', padx=6)
        tk.Button(btn_frame, text="Clear", width=12, command=self.clear_form).pack(side='left', padx=6)
        tk.Button(btn_frame, text="Export CSV", width=12, command=self.export_csv).pack(side='right', padx=6)

        # Search
        search_frame = tk.Frame(root, padx=10, pady=4)
        search_frame.pack(fill='x')
        tk.Label(search_frame, text="Search by RegNo/Name").pack(side='left')
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side='left', padx=6)
        tk.Button(search_frame, text="Search", command=self.search_student).pack(side='left')
        tk.Button(search_frame, text="Show All", command=self.load_students).pack(side='left', padx=6)

        # Table
        table_frame = tk.Frame(root, padx=10, pady=6)
        table_frame.pack(fill='both', expand=True)
        cols = ('id','reg_no','name','age','gender','department','email')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings')
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, anchor='w', width=110)
        self.tree.column('id', width=40)
        self.tree.pack(fill='both', expand=True, side='left')

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        init_db()
        self.load_students()

    def run_query(self, query, params=()):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        rows = cur.fetchall()
        conn.close()
        return rows

    def add_student(self):
        reg = self.reg_var.get().strip()
        name = self.name_var.get().strip()
        if not reg or not name:
            messagebox.showwarning("Validation", "Reg No and Name are required.")
            return
        try:
            self.run_query('INSERT INTO students (reg_no,name,age,gender,department,email) VALUES (?,?,?,?,?,?)',
                           (reg, name, self.age_var.get() or None, self.gender_var.get() or None, self.dept_var.get() or None, self.email_var.get() or None))
            messagebox.showinfo("Success", "Student added successfully.")
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_students(self):
        records = self.run_query('SELECT id, reg_no, name, age, gender, department, email FROM students ORDER BY id DESC')
        # clear current
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in records:
            self.tree.insert('', 'end', values=row)

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: 
            return
        values = self.tree.item(selected[0])['values']
        # populate form
        self.reg_var.set(values[1])
        self.name_var.set(values[2])
        self.age_var.set(values[3] or '')
        self.gender_var.set(values[4] or '')
        self.dept_var.set(values[5] or '')
        self.email_var.set(values[6] or '')

    def clear_form(self):
        self.reg_var.set('')
        self.name_var.set('')
        self.age_var.set('')
        self.gender_var.set('')
        self.dept_var.set('')
        self.email_var.set('')

    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a record to update.")
            return
        sid = self.tree.item(selected[0])['values'][0]
        try:
            self.run_query('UPDATE students SET reg_no=?, name=?, age=?, gender=?, department=?, email=? WHERE id=?',
                           (self.reg_var.get().strip(), self.name_var.get().strip(), self.age_var.get() or None, self.gender_var.get() or None, self.dept_var.get() or None, self.email_var.get() or None, sid))
            messagebox.showinfo("Success", "Student updated successfully.")
            self.load_students()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a record to delete.")
            return
        sid = self.tree.item(selected[0])['values'][0]
        answer = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if answer:
            self.run_query('DELETE FROM students WHERE id=?', (sid,))
            messagebox.showinfo("Deleted", "Record deleted.")
            self.load_students()
            self.clear_form()

    def search_student(self):
        q = self.search_var.get().strip()
        if not q:
            self.load_students()
            return
        rows = self.run_query("SELECT id, reg_no, name, age, gender, department, email FROM students WHERE reg_no LIKE ? OR name LIKE ? ORDER BY id DESC", ('%'+q+'%', '%'+q+'%'))
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def export_csv(self):
        records = self.run_query('SELECT id, reg_no, name, age, gender, department, email FROM students ORDER BY id DESC')
        if not records:
            messagebox.showinfo("No data", "No records to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files','*.csv')], initialfile='students.csv')
        if not file:
            return
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id','reg_no','name','age','gender','department','email'])
            writer.writerows(records)
        messagebox.showinfo("Exported", f"Exported {len(records)} rows to {file}")

if __name__ == '__main__':
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()