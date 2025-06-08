import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
import html
import os

# --- Constants ---
CHANGELOG_FILE = 'changelog.json'
OPERATIONS = ["Created", "Edited", "Deleted"]
WINDOW_TITLE = "Changelog Generator & Editor"
WINDOW_GEOMETRY = "700x650"  # Increased size for the listbox


# --- Core Logic ---

def load_changelog():
    """Loads and sorts changelog entries (newest first)."""
    if not os.path.exists(CHANGELOG_FILE):
        return []
    try:
        with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
            entries = json.load(f)
            # Sort by timestamp in descending order for display
            entries.sort(key=lambda x: x['timestamp'], reverse=True)
            return entries
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_changelog(entries):
    """Saves the list of entries to the JSON file."""
    with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)


def add_entry(operation, text):
    """Adds a new entry to the changelog."""
    if not text.strip():
        messagebox.showwarning("Input Error", "Changelog text cannot be empty.")
        return False

    entries = load_changelog()
    new_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "operation": operation,
        "text": text
    }
    entries.append(new_entry)
    save_changelog(entries)
    return True


def edit_entry(timestamp, new_operation, new_text):
    """Finds an entry by its timestamp and updates it."""
    if not new_text.strip():
        messagebox.showwarning("Input Error", "Changelog text cannot be empty.")
        return False

    entries = load_changelog()
    entry_found = False
    for entry in entries:
        if entry['timestamp'] == timestamp:
            entry['operation'] = new_operation
            entry['text'] = new_text
            entry_found = True
            break

    if entry_found:
        save_changelog(entries)
        return True
    else:
        messagebox.showerror("Error", "Could not find the entry to edit. It may have been deleted.")
        return False


def delete_entry(timestamp):
    """Removes an entry from the changelog by its timestamp."""
    entries = load_changelog()
    # Create a new list excluding the entry to be deleted
    entries_to_keep = [entry for entry in entries if entry['timestamp'] != timestamp]

    if len(entries) == len(entries_to_keep):
        messagebox.showerror("Error", "Could not find the entry to delete.")
        return False

    save_changelog(entries_to_keep)
    return True


# --- HTML Generation (Unchanged) ---
def generate_html_file():
    """Generates a styled HTML file from the changelog data."""
    entries = load_changelog()  # Already sorted newest first
    if not entries:
        messagebox.showinfo("No Data", "Changelog is empty. Add some entries first.")
        return

    html_content = ""
    for entry in entries:
        op_class = entry['operation'].lower()
        safe_text = html.escape(entry['text'])
        timestamp = datetime.datetime.fromisoformat(entry['timestamp'])
        formatted_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        html_content += f"""
        <div class="entry">
            <span class="tag {op_class}">{entry['operation']}</span>
            <span class="text">{safe_text}</span>
            <span class="date">{formatted_date}</span>
        </div>
        """

    filepath = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
        title="Save Changelog As..."
    )

    if not filepath:
        return

    html_template = f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Changelog</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6;background-color:#f4f7f9;color:#333;margin:0;padding:2em;}}.container{{max-width:800px;margin:0 auto;background-color:#ffffff;padding:2em;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.08);}}h1{{color:#1a253c;border-bottom:2px solid #eef2f5;padding-bottom:0.5em;margin-top:0;}}.entry{{padding:1em 0;border-bottom:1px solid #eef2f5;display:flex;align-items:flex-start;flex-wrap:wrap;}}.entry:last-child{{border-bottom:none;}}.tag{{font-weight:600;padding:0.2em 0.6em;border-radius:12px;color:#fff;font-size:0.85em;margin-right:1em;flex-shrink:0;}}.tag.created{{background-color:#28a745;}}.tag.edited{{background-color:#007bff;}}.tag.deleted{{background-color:#dc3545;}}.text{{flex-grow:1;word-break:break-word;}}.date{{font-size:0.8em;color:#888;margin-left:1.5em;flex-shrink:0;align-self:center;}}@media (max-width:600px){{.entry{{flex-direction:column;align-items:flex-start;}}.date{{margin-left:0;margin-top:0.5em;}}}}
</style></head><body><div class="container"><h1>Project Changelog</h1>{html_content}</div></body></html>"""

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_template)
        messagebox.showinfo("Success", f"Changelog successfully generated at:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save HTML file: {e}")


# --- GUI Setup ---

class ChangelogApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_GEOMETRY)
        self.minsize(600, 500)

        # State tracking
        self.entries = []
        self.selected_entry_timestamp = None

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(5, weight=1)  # Allow listbox to expand
        main_frame.columnconfigure(0, weight=1)

        # --- Input Widgets ---
        input_frame = ttk.LabelFrame(main_frame, text="Add or Edit Entry", padding="10")
        input_frame.grid(column=0, row=0, sticky="ew", padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Operation:").grid(column=0, row=0, sticky=tk.W)
        self.operation_var = tk.StringVar(value=OPERATIONS[0])
        op_menu = ttk.OptionMenu(input_frame, self.operation_var, OPERATIONS[0], *OPERATIONS)
        op_menu.grid(column=1, row=0, sticky=tk.EW, pady=2)

        ttk.Label(input_frame, text="Text:").grid(column=0, row=1, sticky=tk.NW)
        self.text_input = tk.Text(input_frame, height=5, wrap=tk.WORD, undo=True)
        self.text_input.grid(column=1, row=1, sticky="nsew", pady=2)
        self.text_input.focus()

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(column=0, row=2, sticky=tk.E, padx=5, pady=(5, 10))

        self.save_button = ttk.Button(button_frame, text="Add Entry", command=self.save_entry_callback)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_entry_callback,
                                        state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(button_frame, text="New / Clear", command=self.clear_selection,
                                       state=tk.DISABLED)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(column=0, row=3, sticky="ew", pady=5)

        # --- Changelog List ---
        list_frame = ttk.LabelFrame(main_frame, text="Changelog History", padding="10")
        list_frame.grid(column=0, row=5, sticky="nsew", padx=5, pady=5)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.changelog_list = tk.Listbox(list_frame, height=15)
        self.changelog_list.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.changelog_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.changelog_list.config(yscrollcommand=scrollbar.set)
        self.changelog_list.bind('<<ListboxSelect>>', self.on_entry_select)

        # --- Generate HTML Button (bottom) ---
        generate_button = ttk.Button(main_frame, text="Generate HTML Report", command=generate_html_file)
        generate_button.grid(column=0, row=6, sticky="ew", padx=5, pady=10)

        self.refresh_changelog_list()

    def refresh_changelog_list(self):
        """Clears and re-populates the listbox with current entries."""
        self.entries = load_changelog()
        self.changelog_list.delete(0, tk.END)

        for entry in self.entries:
            # Truncate long text for display in the listbox
            text_preview = (entry['text'][:70] + '...') if len(entry['text']) > 70 else entry['text']
            text_preview = text_preview.replace('\n', ' ')
            display_str = f"[{entry['operation']}] {text_preview}"
            self.changelog_list.insert(tk.END, display_str)

    def on_entry_select(self, event):
        """Handler for when a user clicks an item in the listbox."""
        selection_indices = self.changelog_list.curselection()
        if not selection_indices:
            return

        selected_index = selection_indices[0]
        selected_entry = self.entries[selected_index]
        self.selected_entry_timestamp = selected_entry['timestamp']

        # Populate form with selected entry's data
        self.operation_var.set(selected_entry['operation'])
        self.text_input.delete('1.0', tk.END)
        self.text_input.insert('1.0', selected_entry['text'])

        # Update UI state for "edit mode"
        self.save_button.config(text="Save Changes")
        self.delete_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def clear_selection(self):
        """Resets the form to its initial state for adding a new entry."""
        self.selected_entry_timestamp = None
        self.changelog_list.selection_clear(0, tk.END)

        self.operation_var.set(OPERATIONS[0])
        self.text_input.delete('1.0', tk.END)

        self.save_button.config(text="Add Entry")
        self.delete_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.text_input.focus()

    def save_entry_callback(self):
        """Handles both adding a new entry and saving an edited one."""
        operation = self.operation_var.get()
        text = self.text_input.get("1.0", tk.END).strip()

        if self.selected_entry_timestamp:  # Editing an existing entry
            success = edit_entry(self.selected_entry_timestamp, operation, text)
            if success:
                messagebox.showinfo("Success", "Entry updated successfully!")
        else:  # Adding a new entry
            success = add_entry(operation, text)
            if success:
                messagebox.showinfo("Success", "New entry added successfully!")

        if success:
            self.refresh_changelog_list()
            self.clear_selection()

    def delete_entry_callback(self):
        """Handles deleting the selected entry."""
        if not self.selected_entry_timestamp:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to permanently delete this entry?"
        )

        if confirm:
            success = delete_entry(self.selected_entry_timestamp)
            if success:
                messagebox.showinfo("Success", "Entry deleted successfully.")
                self.refresh_changelog_list()
                self.clear_selection()


if __name__ == "__main__":
    app = ChangelogApp()
    app.mainloop()