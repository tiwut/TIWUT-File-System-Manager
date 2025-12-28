import customtkinter as ctk
import zipfile
import os
import io
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TiwutEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TIWUT File System Manager")
        self.geometry("1100x700")
        
        self.required_folders = [
            "data/", "info/", "storage/", "user/", 
            "meta/", "app/", "filesystem/", "temp/"
        ]
        
        self.current_tiwut_path = None
        self.current_selected_file = None

        self.create_layout()

    def create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="TIWUT\nManager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_new = ctk.CTkButton(self.sidebar_frame, text="Create New", command=self.create_new_tiwut)
        self.btn_new.grid(row=1, column=0, padx=20, pady=10)

        self.btn_open = ctk.CTkButton(self.sidebar_frame, text="Open", command=self.open_tiwut)
        self.btn_open.grid(row=2, column=0, padx=20, pady=10)

        self.btn_import = ctk.CTkButton(self.sidebar_frame, text="Import File", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.import_file_to_folder)
        self.btn_import.grid(row=3, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="No file loaded", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=20, pady=20)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.tree_frame = ctk.CTkFrame(self.main_frame, width=300)
        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        self.style_treeview()
        self.tree = ttk.Treeview(self.tree_frame, selectmode="browse", show="tree headings")
        self.tree.heading("#0", text="File System Structure", anchor="w")
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.editor_frame = ctk.CTkFrame(self.main_frame)
        self.editor_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.editor_frame.grid_rowconfigure(1, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        self.editor_label = ctk.CTkLabel(self.editor_frame, text="File Preview / Editor", anchor="w")
        self.editor_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        self.text_editor = ctk.CTkTextbox(self.editor_frame)
        self.text_editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.btn_save_content = ctk.CTkButton(self.editor_frame, text="Save Changes", command=self.save_current_file_content)
        self.btn_save_content.grid(row=2, column=0, sticky="e", padx=10, pady=10)

    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        borderwidth=0,
                        rowheight=25)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")
        style.map("Treeview.Heading", background=[('active', '#333333')])

    def create_new_tiwut(self):
        path = filedialog.asksaveasfilename(defaultextension=".tiwut", filetypes=[("Tiwut File System", "*.tiwut")])
        if not path:
            return

        try:
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for folder in self.required_folders:
                    zfi = zipfile.ZipInfo(folder)
                    zf.writestr(zfi, "")
                
                zf.writestr("meta/created_at.txt", f"Created: {datetime.now()}")

            self.load_tiwut(path)
            messagebox.showinfo("Success", "New .tiwut file system created!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not create file: {e}")

    def open_tiwut(self):
        path = filedialog.askopenfilename(filetypes=[("Tiwut File System", "*.tiwut")])
        if path:
            self.load_tiwut(path)

    def load_tiwut(self, path):
        self.current_tiwut_path = path
        self.status_label.configure(text=f"File: {os.path.basename(path)}")
        self.text_editor.delete("0.0", "end")
        self.current_selected_file = None
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            with zipfile.ZipFile(path, 'r') as zf:
                file_list = sorted(zf.namelist())
                
                self.tree_nodes = {}

                for filepath in file_list:
                    parts = filepath.rstrip('/').split('/')
                    parent_path = ""
                    
                    for i, part in enumerate(parts):
                        current_path = f"{parent_path}{part}"
                        if i < len(parts) - 1 or filepath.endswith('/'):
                            current_path += "/"
                        
                        if current_path not in self.tree_nodes:
                            parent_node = self.tree_nodes.get(parent_path, "")
                            
                            display_text = f"📁 {part}" if current_path.endswith('/') else f"📄 {part}"
                            
                            node_id = self.tree.insert(parent_node, "end", text=display_text, open=False, values=[current_path])
                            self.tree_nodes[current_path] = node_id
                        
                        parent_path = current_path
                        
        except Exception as e:
            messagebox.showerror("Error", f"File damaged or invalid zip: {e}")

    def on_tree_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item_id = selected_items[0]
        file_path = self.tree.item(item_id, "values")[0]

        if file_path.endswith("/"):
            self.current_selected_file = None
            self.editor_label.configure(text=f"Selected folder: {file_path}")
            self.text_editor.delete("0.0", "end")
            self.text_editor.insert("0.0", "[Folders cannot be edited]")
            self.text_editor.configure(state="disabled")
        else:
            self.current_selected_file = file_path
            self.editor_label.configure(text=f"Editing: {file_path}")
            self.read_file_content(file_path)

    def read_file_content(self, file_path):
        self.text_editor.configure(state="normal")
        self.text_editor.delete("0.0", "end")
        
        try:
            with zipfile.ZipFile(self.current_tiwut_path, 'r') as zf:
                with zf.open(file_path) as f:
                    content = f.read()
                    try:
                        text_content = content.decode('utf-8')
                        self.text_editor.insert("0.0", text_content)
                    except UnicodeDecodeError:
                        self.text_editor.insert("0.0", "[Binary file - Preview not available]")
                        self.text_editor.configure(state="disabled")
        except Exception as e:
            self.text_editor.insert("0.0", f"Error reading file: {e}")

    def save_current_file_content(self):
        if not self.current_tiwut_path or not self.current_selected_file:
            return

        if self.text_editor.cget("state") == "disabled":
            messagebox.showwarning("Info", "Binary files or folders cannot be saved here.")
            return

        new_content = self.text_editor.get("0.0", "end-1c")

        try:
            temp_buffer = io.BytesIO()
            
            with zipfile.ZipFile(self.current_tiwut_path, 'r') as zin:
                with zipfile.ZipFile(temp_buffer, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        if item.filename != self.current_selected_file:
                            zout.writestr(item, zin.read(item.filename))
                    
                    zout.writestr(self.current_selected_file, new_content)
            
            with open(self.current_tiwut_path, 'wb') as f:
                f.write(temp_buffer.getvalue())

            messagebox.showinfo("Saved", "File successfully updated in .tiwut system.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

    def import_file_to_folder(self):
        if not self.current_tiwut_path:
            messagebox.showwarning("Warning", "Please open or create a .tiwut file system first.")
            return
        
        selected_items = self.tree.selection()
        target_folder = ""
        if selected_items:
            path = self.tree.item(selected_items[0], "values")[0]
            if path.endswith("/"):
                target_folder = path
            else:
                target_folder = os.path.dirname(path.rstrip('/')) + "/"
                if target_folder == "/": target_folder = ""
        else:
            target_folder = "data/"

        file_to_import = filedialog.askopenfilename()
        if not file_to_import:
            return

        filename = os.path.basename(file_to_import)
        zip_path = target_folder + filename

        try:
            with zipfile.ZipFile(self.current_tiwut_path, 'a', zipfile.ZIP_DEFLATED) as zf:
                zf.write(file_to_import, zip_path)
            
            self.load_tiwut(self.current_tiwut_path)
            messagebox.showinfo("Import", f"File imported to '{target_folder}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")

if __name__ == "__main__":
    app = TiwutEditorApp()
    app.mainloop()