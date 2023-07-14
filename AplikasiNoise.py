import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import numpy as np
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk

def remove_salt_and_pepper_noise(image):
    median = cv2.medianBlur(image, 3)
    return median

def login_user():
    
    username = username_entry.get()
    password = password_entry.get()
    db_connection = mysql.connector.connect(
        host="localhost",
        user="username",
        password="",
        database="noise_removal"
    )
    cursor = db_connection.cursor()
       # Check if the user exists in the database
    select_query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(select_query, (username,))
    user = cursor.fetchone()
    if user:
        global current_user
        current_user = username
        
        stored_password = user[2]  # Assuming password is stored in the second column
        if password == stored_password:
            messagebox.showinfo("Login Successful", "Login successful.")
            root.destroy()  # Destroy the login window
            # Create the main application window
            app_window = tk.Tk()
            app_window.title("Image Processing")
            app_window.geometry("800x600")

            # Frame for original image
            original_frame = tk.Frame(app_window, width=400)
            original_frame.pack(side=tk.LEFT, padx=10, pady=10)

            # Label for original image
            original_label = tk.Label(original_frame, text="Original Image", font=("Arial", 12))
            original_label.pack()

            # Canvas for original image
            global canvas_original
            canvas_original = tk.Label(original_frame)
            canvas_original.pack()

            # Frame for processed image
            processed_frame = tk.Frame(app_window)
            processed_frame.pack(side=tk.LEFT, padx=10, pady=10)

            # Label for processed image
            processed_label = tk.Label(processed_frame, text="Processed Image", font=("Arial", 12))
            processed_label.pack()

            # Canvas for processed image
            global canvas_processed
            canvas_processed = tk.Label(processed_frame)
            canvas_processed.pack()

            # Process Image button
            process_button = tk.Button(app_window, text="Process Image", command=process_image)
            process_button.pack(side=tk.BOTTOM, pady=40)


            app_window.configure(bg="#98CA32")
            app_window.mainloop()
        else:
            messagebox.showerror("Login Failed", "Incorrect password.")
    else:
            messagebox.showerror("Login Failed", "User does not exist.")


    # Close the database connection
    cursor.close()
    db_connection.close()

def register_user():
    username = username_entry.get()
    password = password_entry.get()
    db_connection = mysql.connector.connect(
        host="localhost",
        user="username",
        password="",
        database="noise_removal"
    )
    cursor = db_connection.cursor()
    # Check if the username already exists
    select_query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(select_query, (current_user,))
    user = cursor.fetchone()
    if user:
        messagebox.showerror("Registration Failed", "Username already exists.")
    else:
        # Insert the new user into the database
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, password))
        db_connection.commit()
        messagebox.showinfo("Registration Successful", "Registration successful. Please log in.")

    # Close the database connection
    cursor.close()
    db_connection.close() 


def process_image():
    
    file_path = filedialog.askopenfilename(filetypes=[("JPEG", "*.jpg")])
    if file_path:
        original_image = cv2.imread(file_path)
        processed_image = remove_salt_and_pepper_noise(original_image)

        # Convert original image to PIL format
        original_image_pil = Image.fromarray(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))

        # Resize original image to fit in the canvas
        desired_width = 400  # Tentukan lebar yang diinginkan
        aspect_ratio = desired_width / original_image_pil.width
        desired_height = int(original_image_pil.height * aspect_ratio)
        original_image_resized = original_image_pil.resize((desired_width, desired_height), Image.LANCZOS)

        # Convert original image to Tkinter format
        original_image_tk = ImageTk.PhotoImage(original_image_resized)

        # Update the canvas with the original image
        canvas_original.configure(image=original_image_tk)
        canvas_original.image = original_image_tk

        # Convert processed image to PIL format
        processed_image_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))

        # Resize processed image to fit in the canvas
        desired_width = 400  # Tentukan lebar yang diinginkan
        aspect_ratio = desired_width / processed_image_pil.width
        desired_height = int(processed_image_pil.height * aspect_ratio)
        processed_image_resized = processed_image_pil.resize((desired_width, desired_height), Image.LANCZOS)

        # Convert processed image to Tkinter format
        processed_image_tk = ImageTk.PhotoImage(processed_image_resized)

        # Update the canvas with the processed image
        canvas_processed.configure(image=processed_image_tk)
        canvas_processed.image = processed_image_tk

        # Insert image data into the database
        db_connection = mysql.connector.connect(
            host="localhost",
            user="username",
            password="",
            database="noise_removal"
        )
        cursor = db_connection.cursor()

        # Get the ID of the logged-in user
        select_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(select_query, (current_user,))
        user_id = cursor.fetchone()

        if user_id:
            user_id = user_id[1]
            # Insert original image data with user_id
            insert_query = "INSERT INTO images (image_type, image_data, created_at, user_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, ("Original", cv2.imencode('.jpg', original_image)[1].tobytes(), datetime.now(), user_id))

            # Insert processed image data with user_id
            insert_query = "INSERT INTO images (image_type, image_data, created_at, user_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, ("Processed", cv2.imencode('.jpg', processed_image)[1].tobytes(), datetime.now(), user_id))

            db_connection.commit()
            cursor.close()
            db_connection.close()
        else:
            messagebox.showerror("Error", "User ID not found.")

    else:
        messagebox.showerror("Error", "No image selected.")


def create_app_window():
    global canvas_processed
    global canvas_original
    app_window = tk.Tk()
    app_window.title("Salt and Pepper Noise Removal")
    app_window.geometry("800x800")

    # Canvas for original image
    canvas_original = tk.Canvas(app_window, width=600, height=400)  # Ubah ukuran sesuai kebutuhan
    canvas_original.pack(side=tk.TOP, padx=10, pady=10)

    # Canvas for processed image
    canvas_processed = tk.Canvas(app_window, width=600, height=400)  # Ubah ukuran sesuai kebutuhan
    canvas_processed.pack(side=tk.TOP, padx=10, pady=10)

    # Process Image button
    process_button = tk.Button(app_window, text="Process Image", command=process_image)
    process_button.pack(side=tk.TOP, pady=20)


    return canvas_processed
    app_window.mainloop()

root = tk.Tk()
root.title("Login")
root.geometry("800x400")

# Background color
root.configure(bg="#DBE5FF")

# Title label
title_label = tk.Label(root, text="Login", font=("Arial", 16), bg="#DBE5FF")
title_label.pack(pady=20)

# Username label and entry
username_label = tk.Label(root, text="Username:", bg="#678FFE")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

# Password label and entry
password_label = tk.Label(root, text="Password:", bg="#678FFE")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

# Login button
login_button = tk.Button(root, text="Login", command=login_user)
login_button.pack(pady=10)

root.mainloop()
