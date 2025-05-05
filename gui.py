import serial
import time
import tkinter as tk

# Set up serial connection
arduino = serial.Serial(port='COM12', baudrate=9600, timeout=.1)

# Create the GUI window
root = tk.Tk()
root.title("Clapper Light Switch")
root.geometry("400x500")  # Set a fixed window size

# Create a canvas for the color square
canvas = tk.Canvas(root, width=200, height=200)
canvas.pack(padx=20, pady=20)

# Create a rectangle (square) on the canvas
square = canvas.create_rectangle(10, 10, 190, 190, fill="black")

# Create a label for the serial text output
label = tk.Label(
    root,
    text="Waiting for data...",
    font=("Helvetica", 14),
    width=40,
    height=10,
    wraplength=300,
    justify="left",
    anchor="n"
)
label.pack(padx=20, pady=10)

# Variables to collect multi-line messages
buffer = []
is_recording = False
light_on = False  # Track the current light state

def update_display():
    global buffer, is_recording, light_on
    line = arduino.readline().decode('utf-8', errors='ignore').strip()
    
    if line:
        print(line)  # For debugging

        if "Recording..." in line:
            is_recording = True
            label.config(text="Recording...")
            buffer = []
        elif "Recording done" in line:
            is_recording = False
        elif is_recording:
            # During recording, we don't process
            pass
        else:
            buffer.append(line)

        if "Starting inferencing" in line:
            full_message = "\n".join(buffer)
            label.config(text=full_message)

            # Parse prediction
            clap_score = None
            for buf_line in buffer:
                if "clap" in buf_line:
                    try:
                        clap_score = float(buf_line.split(" with probability")[1].strip())
                    except Exception as e:
                        print(f"Error parsing clap score: {e}")
                        clap_score = None
            # If a clap was detected with high enough confidence
            if clap_score is not None and clap_score > 0.7:
                # Toggle light state
                light_on = not light_on
            if light_on:
                canvas.itemconfig(square, fill="white")
            else:
                canvas.itemconfig(square, fill="black")
            
            # Reset buffer for next block
            buffer = []

    root.after(50, update_display)

# Start updating
update_display()

# Run the GUI event loop
root.mainloop()

