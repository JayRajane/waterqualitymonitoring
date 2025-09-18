import tkinter as tk
from tkinter import font, ttk
from PIL import Image, ImageTk
import requests
import json
import threading
from apscheduler.schedulers.blocking import BlockingScheduler

# Global variables to store manual and fetched values
manual_values = {"COD": None, "BOD": None, "TSS": None, "pH": None, "Flow": None, "Daily Flow": None}
fetched_values = {"COD": "00.00", "BOD": "00.00", "TSS": "00.00", "pH": "00.00", "Flow": "00.00", "Daily Flow": "00.00"}

def format_value(value):
    """Format the value to add .00 if it's an integer."""
    try:
        float_val = float(value)
        if float_val.is_integer():
            return f"{float_val:.2f}"
        else:
            return str(float_val)
    except ValueError:
        return value

def create_virtual_keyboard(parent, entry):
    """Create a virtual keyboard for numeric entry."""
    keyboard_frame = tk.Frame(parent)
    keys = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['.', '0', '←'],
        ['Clr']
    ]

    def on_key_click(key):
        if key == 'Clr':
            entry.delete(0, tk.END)
        elif key == '←':
            entry.delete(len(entry.get()) - 1, tk.END)
        else:
            entry.insert(tk.END, key)

    for row_idx, row in enumerate(keys):
        for col_idx, key in enumerate(row):
            btn = tk.Button(keyboard_frame, text=key, width=2, height=1,
                            command=lambda key=key: on_key_click(key), font=("Arial", 12))
            btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)
    keyboard_frame.pack(pady=5)

def open_calibration_popup(root, codButton, bodButton, tssButton, phButton, flowButton, dailyFlowButton):
    """Open the calibration popup."""
    popup = tk.Toplevel(root)
    popup.geometry("300x450")
    popup.title("Calibration")

    selected_param = tk.StringVar(value="COD")
    options = ["COD", "BOD", "TSS", "pH", "Flow", "Daily Flow"]

    ttk.Label(popup, text="Select Parameter:", font=("Arial", 12)).pack(pady=5)
    param_menu = ttk.Combobox(popup, values=options, font=("Arial", 12), state="readonly", textvariable=selected_param)
    param_menu.pack(pady=5)

    ttk.Label(popup, text="Enter Value:", font=("Arial", 12)).pack(pady=5)
    value_entry = tk.Entry(popup, font=("Arial", 12))
    value_entry.pack(pady=5)

    create_virtual_keyboard(popup, value_entry)

    def on_submit():
        value = value_entry.get()
        if value:
            param = selected_param.get()
            formatted_value = format_value(value)
            manual_values[param] = formatted_value
            
            if param == "COD":
                codButton.config(text=f'COD\n\n{formatted_value} mg/l')
            elif param == "BOD":
                bodButton.config(text=f'BOD\n\n{formatted_value} mg/l')
            elif param == "TSS":
                tssButton.config(text=f'TSS\n\n{formatted_value} mg/l')
            elif param == "pH":
                phButton.config(text=f'pH\n\n{formatted_value}')
            elif param == "Flow":
                flowButton.config(text=f'Flow\n\n{formatted_value} m³/h')
            elif param == "Daily Flow":
                dailyFlowButton.config(text=f'Daily Flow\n\n{formatted_value} m³/d')
            popup.destroy()

    submit_button = tk.Button(popup, text="Submit", font=("Arial", 14), command=on_submit)
    submit_button.pack(pady=15)

def get_data():
    """Fetch real-time data from the server."""
    url = "https://impulseengineers.com/app/get_cod_bod_tss_spm_data/1/"
    try:
        response = requests.get(url)
        json_data = response.json()
        
        fetched_values["COD"] = format_value(json_data.get("cod", "00.00"))
        fetched_values["BOD"] = format_value(json_data.get("bod", "00.00"))
        fetched_values["TSS"] = format_value(json_data.get("tss", "00.00"))
        fetched_values["pH"] = format_value(json_data.get("ph_value", "00.00"))
        fetched_values["Flow"] = format_value(json_data.get("flow", "00.00"))
        fetched_values["Daily Flow"] = format_value(json_data.get("daily_flow", "00.00"))
        
        print("Data fetched successfully:", fetched_values)
        update_displayed_values()
    except Exception as e:
        print(f"Error fetching data: {e}")

def update_displayed_values():
    """Update displayed values based on manual or fetched values"""
    if manual_values["COD"] is None:
        codButton.config(text=f'COD\n\n{fetched_values["COD"]} mg/l')
    if manual_values["BOD"] is None:
        bodButton.config(text=f'BOD\n\n{fetched_values["BOD"]} mg/l')
    if manual_values["TSS"] is None:
        tssButton.config(text=f'TSS\n\n{fetched_values["TSS"]} mg/l')
    if manual_values["pH"] is None:
        phButton.config(text=f'pH\n\n{fetched_values["pH"]}')
    if manual_values["Flow"] is None:
        flowButton.config(text=f'Flow\n\n{fetched_values["Flow"]} m³/h')
    if manual_values["Daily Flow"] is None:
        dailyFlowButton.config(text=f'Daily Flow\n\n{fetched_values["Daily Flow"]} m³/d')

def update_data(json_data):
    """Upload calibration data to the server."""
    url = "https://www.impulseengineers.com/app/upload_mpcb_local_data/"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(json_data), headers=headers)
        print("Data uploaded:", response.text)
    except Exception as e:
        print(f"Error uploading data: {e}")

def reset_values():
    """Reset the displayed values to the fetched values."""
    global manual_values
    manual_values = {"COD": None, "BOD": None, "TSS": None, "pH": None, "Flow": None, "Daily Flow": None}
    update_displayed_values()

# Modified button class with square edges
class SquareButton(tk.Frame):
    def __init__(self, parent, text, width, height, bg_color="white", fg="black", border_color="blue", border_width=1, font=None, command=None):
        tk.Frame.__init__(self, parent, width=width, height=height, bg=border_color)
        
        self.inner_frame = tk.Frame(self, bg=bg_color, width=width-2*border_width, height=height-2*border_width)
        self.inner_frame.place(x=border_width, y=border_width)
        
        self.label = tk.Label(self.inner_frame, text=text, bg=bg_color, fg=fg, font=font, justify=tk.CENTER)
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.command = command
        
        self.bind("<Button-1>", self._on_click)
        self.inner_frame.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)
        
        self.pack_propagate(False)
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def config(self, **kwargs):
        if "text" in kwargs:
            self.label.config(text=kwargs["text"])
        if "bg" in kwargs:
            self.inner_frame.config(bg=kwargs["bg"])
            self.label.config(bg=kwargs["bg"])
        if "fg" in kwargs:
            self.label.config(fg=kwargs["fg"])
        if "border_color" in kwargs:
            self.config(bg=kwargs["border_color"])

# Global buttons for access from functions
codButton = None
bodButton = None
tssButton = None
phButton = None
flowButton = None
dailyFlowButton = None

def start_data_fetch():
    """Start fetching data in a separate thread"""
    scheduler = BlockingScheduler()
    scheduler.add_job(get_data, 'interval', seconds=5)
    scheduler.start()

def create_etp_monitoring_system():
    global codButton, bodButton, tssButton, phButton, flowButton, dailyFlowButton
    
    root = tk.Tk()
    root.title("ETP MONITORING SYSTEM")
    root.configure(bg="#1E90FF")
    
    # Set full-screen mode
    root.attributes('-fullscreen', True)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    inner_frame_width = int(screen_width * 0.97)
    inner_frame_height = int(screen_height * 0.95)
    
    inner_frame = tk.Frame(root, width=inner_frame_width, height=inner_frame_height, bg="white")
    inner_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    content_frame = tk.Frame(inner_frame, bg="white")
    content_frame.place(x=10, y=1, width=inner_frame_width-20, height=inner_frame_height-20)

    try:
        logo_img = Image.open("/home/impulse/Desktop/image.png")
        logo_img = logo_img.resize((180, 90))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(content_frame, image=logo_photo, bg="white")
        logo_label.image = logo_photo
        logo_label.place(x=10, y=2)
    except Exception as e:
        print(f"Error loading image: {e}")
        placeholder = tk.Label(content_frame, text="LOGO", bg="white", font=("Arial", 14))
        placeholder.place(x=50, y=2)

    title_font = font.Font(family="Times New Roman", size=20, weight="bold")
    title_label = tk.Label(content_frame, text="ETP MONITORING SYSTEM", font=title_font, bg="white")
    title_label.pack(pady=(30, 30))

    button_font = font.Font(family="Times New Roman", size=20, weight="bold")

    first_row_frame = tk.Frame(content_frame, bg="white")
    first_row_frame.pack(pady=(5, 5))

    second_row_frame = tk.Frame(content_frame, bg="white")
    second_row_frame.pack(pady=(5, 5))

    button_width = 250
    button_height = 130
    button_border_color = "#1E90FF"
    button_text_color = "#333333"

    # First row - COD Button
    codButton = SquareButton(
        first_row_frame,
        text="COD\n\n00.00 mg/l",
        width=button_width,
        height=button_height,
        bg_color="white",
        fg=button_text_color,
        border_color=button_border_color,
        border_width=2,
        font=button_font
    )
    codButton.pack(side="left", padx=15, pady=10)

    # First row - BOD Button
    bodButton = SquareButton(
        first_row_frame,
        text="BOD\n\n00.00 mg/l",
        width=button_width,
        height=button_height,
        bg_color="white",
        fg=button_text_color,
        border_color=button_border_color,
        border_width=2,
        font=button_font
    )
    bodButton.pack(side="left", padx=15, pady=10)

    # First row - TSS Button
    tssButton = SquareButton(
        first_row_frame,
        text="TSS\n\n00.00 mg/l",
        width=button_width,
        height=button_height,
        bg_color="white",
        fg=button_text_color,
        border_color=button_border_color,
        border_width=2,
        font=button_font
    )
    tssButton.pack(side="left", padx=15, pady=10)

    # Second row - pH Button
    phButton = SquareButton(
        second_row_frame,
        text="pH\n\n00.00",
        width=button_width,
        height=button_height,
        bg_color="white",
        fg=button_text_color,
        border_color=button_border_color,
        border_width=2,
        font=button_font
    )
    phButton.pack(side="left", padx=15, pady=10)

    # Second row - Flow Button
    flowButton = SquareButton(
        second_row_frame,
        text="Flow\n\n00.00 m³/h",
        width=button_width,
        height=button_height,
        bg_color="white",
        fg=button_text_color,
        border_color=button_border_color,
        border_width=2,
        font=button_font
    )
    flowButton.pack(side="left", padx=15, pady=10)

    # Second row - Daily Flow Button
    dailyFlowButton = SquareButton(
        second_row_frame,
        text="Daily Flow\n\n00.00 m³/d",
        width=button_width,
        height=button_height,
        bg_color="white",
        fg=button_text_color,
        border_color=button_border_color,
        border_width=2,
        font=button_font
    )
    dailyFlowButton.pack(side="left", padx=15, pady=10)

    # Calibration button
    calibration_button = tk.Button(
        content_frame,
        text="CALIBRATION",
        font=("Times New Roman", 14, "bold"),
        bg="blue",
        fg="white",
        width=87,
        height=2,
        bd=0,
        command=lambda: open_calibration_popup(root, codButton, bodButton, tssButton, phButton, flowButton, dailyFlowButton)
    )
    calibration_button.pack(pady=15)

    # Reset button
    reset_button = tk.Button(
        content_frame,
        text="RESET",
        font=("Times New Roman", 14, "bold"),
        bg="red",
        fg="white",
        width=87,
        height=2,
        bd=0,
        command=reset_values
    )
    reset_button.pack(pady=5)

    get_data()

    data_thread = threading.Thread(target=start_data_fetch, daemon=True)
    data_thread.start()

    return root

if __name__ == "__main__":
    app = create_etp_monitoring_system()
    app.mainloop()
