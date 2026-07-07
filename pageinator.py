import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from pdf_utils import PDFHelper


class PageInatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Page-Inator")
        self.root.geometry("520x520")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Create tabs
        self.split_tab = tk.Frame(self.notebook)
        self.merge_tab = tk.Frame(self.notebook)

        self.notebook.add(self.split_tab, text="Split")
        self.notebook.add(self.merge_tab, text="Merge")

        # Build tab contents
        self.build_split_tab()
        self.build_merge_tab()

        # Footer
        version = self.get_local_version()
        
        self.footer = tk.Label(
            self.root,
            text=f"Page-Inator v{version} | Created by Robert Melberg",
            font=("Arial", 8),
            fg="gray"
        )
        self.footer.pack(side="bottom", anchor="e", padx=5, pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def build_merge_tab(self):
        label = tk.Label(
            self.merge_tab,
            text="Merge PDFs",
            font=("Arial", 14)
        )
        label.pack(pady=10)
    
        self.file_listbox = tk.Listbox(self.merge_tab, width=60, height=12)
        self.file_listbox.pack(pady=5)
    
        button_frame = tk.Frame(self.merge_tab)
        button_frame.pack(pady=5)
    
        tk.Button(button_frame, text="Add Files", command=self.add_files).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Remove", command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Move Up", command=self.move_up).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Move Down", command=self.move_down).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_all).grid(row=0, column=4, padx=5)
    
        tk.Button(
            self.merge_tab,
            text="Merge PDFs",
            width=25,
            command=self.merge_pdfs
        ).pack(pady=10)

    def build_split_tab(self):
        label = tk.Label(
            self.split_tab,
            text="Split PDF",
            font=("Arial", 14)
        )
        label.pack(pady=20)
    
        self.split_button = tk.Button(
            self.split_tab,
            text="Select PDF to Split",
            width=30,
            command=self.split_pdf
        )
        self.split_button.pack(pady=10)

    # ======================
    # Unified Split Function
    # ======================
    def split_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
    
        if not file_path:
            return
    
        choice = self.ask_split_method()
    
        if not choice:
            return
    
        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
    
            # ✅ Split into pages
            if choice == "pages":
                output_dir = os.path.join(os.path.dirname(file_path), f"{base_name}_pages")
    
                files = PDFHelper.split_pdf_into_pages(file_path, output_dir)
    
                messagebox.showinfo(
                    "Success",
                    f"Split into {len(files)} pages\nSaved in:\n{output_dir}"
                )
    
            # ✅ Split at page
            elif choice == "split":
                split_page = simpledialog.askinteger(
                    "Split Page",
                    "Enter page number:",
                    minvalue=1
                )
    
                if not split_page:
                    return
    
                output_dir = os.path.join(os.path.dirname(file_path), f"{base_name}_split")
    
                PDFHelper.split_pdf_at_page(file_path, output_dir, split_page)
    
                messagebox.showinfo(
                    "Success",
                    "PDF split successfully!"
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ======================
    # Merge Functions
    # ======================
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDFs",
            filetypes=[("PDF files", "*.pdf")]
        )

        for f in files:
            if f not in self.file_listbox.get(0, tk.END):
                self.file_listbox.insert(tk.END, f)

    def remove_selected(self):
        selected = list(self.file_listbox.curselection())
        selected.reverse()

        for i in selected:
            self.file_listbox.delete(i)

    def move_up(self):
        selected = self.file_listbox.curselection()

        for i in selected:
            if i == 0:
                continue

            text = self.file_listbox.get(i)
            self.file_listbox.delete(i)
            self.file_listbox.insert(i - 1, text)
            self.file_listbox.selection_set(i - 1)

    def move_down(self):
        selected = self.file_listbox.curselection()

        for i in reversed(selected):
            if i == self.file_listbox.size() - 1:
                continue

            text = self.file_listbox.get(i)
            self.file_listbox.delete(i)
            self.file_listbox.insert(i + 1, text)
            self.file_listbox.selection_set(i + 1)

    def clear_all(self):
        self.file_listbox.delete(0, tk.END)

    def merge_pdfs(self):
        files = self.file_listbox.get(0, tk.END)

        if not files:
            messagebox.showwarning("No Files", "Please add files.")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output_file:
            return

        try:
            PDFHelper.merge_pdfs(files, output_file)

            messagebox.showinfo("Success", "Merge complete!")

            self.file_listbox.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ask_split_method(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Split Method")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.grab_set()  # Make modal
    
        choice_var = tk.StringVar(value="pages")
    
        label = tk.Label(dialog, text="Choose how to split the PDF:")
        label.pack(pady=10)
    
        rb1 = tk.Radiobutton(dialog, text="Split into individual pages", variable=choice_var, value="pages")
        rb1.pack(anchor="w", padx=20)
    
        rb2 = tk.Radiobutton(dialog, text="Split at a page number", variable=choice_var, value="split")
        rb2.pack(anchor="w", padx=20)
    
        result = {"choice": None}
    
        def on_ok():
            result["choice"] = choice_var.get()
            dialog.destroy()
    
        def on_cancel():
            dialog.destroy()
    
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
    
        ok_button = tk.Button(button_frame, text="OK", width=10, command=on_ok)
        ok_button.grid(row=0, column=0, padx=5)
    
        cancel_button = tk.Button(button_frame, text="Cancel", width=10, command=on_cancel)
        cancel_button.grid(row=0, column=1, padx=5)
    
        dialog.wait_window()

        return result["choice"]
    # ======================
    # Exit
    # ======================
    def on_exit(self):
        try:
            self.root.quit()
            self.root.destroy()
        finally:
            sys.exit()

    def get_local_version(self):
        version_file = os.path.join(os.getcwd(), "version.txt")
    
        try:
            with open(version_file, "r") as f:
                for line in f:
                    if line.startswith("pageinator"):
                        return line.strip().split("=")[1]
        except:
            return "unknown"
    
        return "unknown"

if __name__ == "__main__":
    root = tk.Tk()
    app = PageInatorApp(root)
    root.mainloop()
