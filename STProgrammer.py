import tkinter as tk
from tkinter import filedialog
import time
import os
import subprocess
import RPi.GPIO as GPIO

relay_pins = [17, 27, 22, 23] #24V, GND, NC, NC

# Configurazione GPIO
GPIO.setmode(GPIO.BCM)
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # Imposta i relè su OFF all'avvio HIGH perchè la scheda relè funziona in logica negativa


def toggle_relay(relay_index):
    current_state = GPIO.input(relay_pins[relay_index])
    GPIO.output(relay_pins[relay_index], not current_state)

#def select_file():
#    file_path = filedialog.askopenfilename(filetypes=[(" ", "*.*")])
#    if file_path:
#        file_display.delete("1.0", tk.END)
#        file_display.insert(tk.END, file_path)
        
def check_stlink():
    stlink_command = "st-flash reset"
    result = subprocess.run(stlink_command, shell=True, capture_output=True, text=True)
    time.sleep(0.5)
    stlink_command = "st-info --probe"
    result = subprocess.run(stlink_command, shell=True, capture_output=True, text=True)
    info_lines = result.stdout.strip().split("\n")

    try:
        if info_lines[2]:
            stlink_info_label.config(text="Programmatore ST-Link collegato!", fg="green")
            #return
    
    except IndexError:
        stlink_info_label.config(text="Programmatore non collegato!", fg="red")
        
    if len(info_lines) >= 6:
        version_label.config(text=f"{info_lines[1]}")
        serial_label.config(text=f"{info_lines[2]}")
        #chipid_label.config(text=f"{info_lines[5]}")
        devtype_label.config(text=f"{info_lines[6]}")

def connect_device():
    GPIO.output(27, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(17, GPIO.LOW)
    check_stlink()
    GPIO.output(17, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(27, GPIO.HIGH)

def program_device():
    output_text.delete("1.0", tk.END)  # Pulizia della box output_text
    output_text.update()
    
    file_path = "/home/ernesto/Project/FW/SafePay/CR3/LEDController/led_ctr_4.1f_ldr_4.1a.bin"
    if file_path:
        GPIO.output(27, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(17, GPIO.LOW)
        time.sleep(1)
        
        stlink_command = f"st-flash write {file_path} 0x08000000"
        process = subprocess.Popen(stlink_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
            output_text.update()

        if "64/64" in line.strip():
            output_text.insert(tk.END, "\nProgrammazione terminata!\n")
            output_text.see(tk.END)
            output_text.update()

        process.wait()
        
        GPIO.output(17, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(27, GPIO.HIGH)

def verifica():
    GPIO.output(27, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(17, GPIO.LOW)
    time.sleep(2)
    GPIO.output(17, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(27, GPIO.HIGH)

def exit_program():
    GPIO.cleanup()
    root.destroy()

# Creazione della GUI
root = tk.Tk()
root.attributes("-fullscreen", True)
root.title("ST-Link ernatta")

frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

frame_right = tk.Frame(root)
frame_right.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

stlink_info_label = tk.Label(frame_left, text="Verifica ST-Link...", fg="blue")
stlink_info_label.pack()

version_label = tk.Label(frame_left, text="Versione: --")
version_label.pack()
serial_label = tk.Label(frame_left, text="Seriale: --")
serial_label.pack()
#chipid_label = tk.Label(frame_left, text="Chip ID: --")
#chipid_label.pack()
devtype_label = tk.Label(frame_left, text="Dev-Type: --")
devtype_label.pack()

# Pulsante di connessione ST-Link
#connect_button = tk.Button(frame_left, text="Connetti", command=connect_device, height=2, width=15, fg="white", bg="green")
#connect_button.pack(pady=5)

#select_button = tk.Button(frame_left, text="Select File", command=select_file)
#select_button.pack()

# Box FILE con scrollbar
#file_frame = tk.Frame(frame_left)
#file_frame.pack(fill=tk.X, expand=True)
#file_display_scroll = tk.Scrollbar(file_frame, orient=tk.HORIZONTAL)
#file_display = tk.Text(file_frame, wrap=tk.NONE, height=1, width=30, xscrollcommand=file_display_scroll.set)
#file_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
#file_display_scroll.pack(side=tk.BOTTOM, fill=tk.X)
#file_display_scroll.config(command=file_display.xview)

program_button = tk.Button(frame_left, text="Program device", command=program_device, height=15, width=55, fg="white", bg="green")
program_button.pack(pady=3)

# Pulsante verifica
#verify_btn = tk.Button(frame_left, text=f"Verifica ", command=verifica, height=4, width=35, fg="orange", bg="blue")
#verify_btn.pack(pady=10)
    

exit_button = tk.Button(frame_left, text="Exit Program", command=exit_program, height=3, width=35, fg="white", bg="red")
exit_button.pack(pady=25)

#box output
output_frame = tk.Frame(frame_right)
output_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(output_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=20, width=20)
output_text.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=output_text.yview)

root.after(3000, connect_device)

root.mainloop()
