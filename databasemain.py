import tkinter as tk
import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from datetime import datetime
from tkinter import messagebox


# Create the main window
root = tk.Tk()
root.title("Email")  # window title
root.geometry("800x600")  # window dimensions (width x height)

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')


## email function
def send_email_with_attachment(receiver_email, subject, body, attachment_path):



    sender_email = EMAIL  # email
    sender_password = PASSWORD       # password
    smtp_server = "smtp.gmail.com"         # SMTP server
    smtp_port = 587                          # Port for TLS
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "plain"))
    
    # Attach the file if it exists
    if attachment_path and os.path.isfile(attachment_path):
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(attachment_path)}",
            )
            message.attach(part)
    else:
        print(f"Attachment file {attachment_path} not found.")
        return False
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email to {receiver_email}: {e}")
        return False



def connect():

            with psycopg2.connect(
            dbname = 'management',
            user= 'postgres',
            password = 'qapmoc',
            host='localhost',
            port=5432
        ) as conn:
                print("Connection to database established successfully")
                return conn




def submit_invoice_range():
    invoice_from = entry_invoice_from.get()
    invoice_to = entry_invoice_to.get()

    if not invoice_from and invoice_to:
        messagebox.showwarning("Input Error", "Please enter both invoice numbers.")
        return     
    
    try:
        conn = connect()
        cursor = conn.cursor()
                
        fetch_range_query = """
    SELECT invoices.invoice_id, customers.name, invoices.amount, customers.email, invoices.file
    FROM invoices 
    JOIN customers ON invoices.customer_id = customers.id 
    WHERE invoices.invoice_id BETWEEN %s AND %s;
"""
        cursor.execute(fetch_range_query, (invoice_from, invoice_to))
        unsent_invoices = cursor.fetchall()

        for invoice_id, name, amount, email, file_name in unsent_invoices:
            # Prepare the email
            subject = f"Invoice #{invoice_id}"
            body = f"Sehr geehrte Damen und Herren,\n\nAnliegend ihre Rechnung #{invoice_id} über den Betrag von {amount}€.\n\nMit freundlichen Grüßen,\nihre Wegener.inc"
            attachment_path = os.path.join("/home/dci-student/school/python/databaseproject/", file_name)  # Adjust the path where PDFs are stored

            # Attempt to send the email
            email_sent = send_email_with_attachment(email, subject, body, attachment_path)
            
            if email_sent:
                # Update email status in the database
                update_query = "UPDATE invoices SET emailstatus = True WHERE invoice_id = %s;"
                cursor.execute(update_query, (invoice_id,))
                conn.commit()
                
                # Log success
                log_message = f"Invoice: {invoice_id}, Customer: {name}, Amount: {amount}, Status: Sent"
                add_log_entry(log_message, success=True)
            else:
                # Log failure
                log_message = f"Invoice: {invoice_id}, Customer: {name}, Amount: {amount}, Status: Failed"
                add_log_entry(log_message, success=False)

        messagebox.showinfo("Info", "All invoices have been processed.")   
    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

    finally:
        cursor.close()
        conn.close()


def submit_customer_select():
    customer_id = customer_select.get()  # Get the selected customer ID
    
    # Validate input
    if not customer_id:
        messagebox.showwarning("Input Error", "Please enter a customer ID.")
        return
    
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # Parameterized query to prevent SQL injection
        fetch_customer_query = """
            SELECT invoices.invoice_id, customers.name, invoices.amount, customers.email, invoices.file
            FROM invoices 
            JOIN customers ON invoices.customer_id = customers.id 
            WHERE invoices.emailstatus = False
            AND customer_id = %s;
        """
        cursor.execute(fetch_customer_query, (customer_id,))
        unsent_invoices = cursor.fetchall()

        for invoice_id, name, amount, email, file_name in unsent_invoices:
            # Prepare the email
            subject = f"Invoice #{invoice_id}"
            body = f"Sehr geehrte Damen und Herren,\n\nAnliegend ihre Rechnung #{invoice_id} über den Betrag von {amount}€.\n\nMit freundlichen Grüßen,\nihre Wegener.inc"
            attachment_path = os.path.join("/home/dci-student/school/python/databaseproject/", file_name)  # Adjust the path where PDFs are stored

            # Attempt to send the email
            email_sent = send_email_with_attachment(email, subject, body, attachment_path)
            
            if email_sent:
                # Update email status in the database
                update_query = "UPDATE invoices SET emailstatus = True WHERE invoice_id = %s;"
                cursor.execute(update_query, (invoice_id,))
                conn.commit()
                
                # Log success
                log_message = f"Invoice: {invoice_id}, Customer: {name}, Amount: {amount}, Status: Sent"
                add_log_entry(log_message, success=True)
            else:
                # Log failure
                log_message = f"Invoice: {invoice_id}, Customer: {name}, Amount: {amount}, Status: Failed"
                add_log_entry(log_message, success=False)
        
        messagebox.showinfo("Info", f"All unsent invoices for customer ID {customer_id} sent as Email.")

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

def send_all():
    conn = connect()  # Connect to your database
    cursor = conn.cursor()

    # Fetch all unsent invoices with customer email and file path
    fetch_unsent_query = """
        SELECT invoices.invoice_id, customers.name, invoices.amount, customers.email, invoices.file
        FROM invoices 
        JOIN customers ON invoices.customer_id = customers.id 
        WHERE invoices.emailstatus = False;
    """
    cursor.execute(fetch_unsent_query)
    unsent_invoices = cursor.fetchall()

    for invoice_id, name, amount, email, file_name in unsent_invoices:
        # Prepare the email
        subject = f"Invoice #{invoice_id}"
        body = f"Sehr geehrte Damen und Herren,\n\nAnliegend ihre Rechnung #{invoice_id} über den Betrag von {amount}€.\n\nMit freundlichen Grüßen,\nihre Wegener.inc"
        attachment_path = os.path.join("/home/dci-student/school/python/databaseproject/", file_name)  # Adjust the path where PDFs are stored

        # Attempt to send the email
        email_sent = send_email_with_attachment(email, subject, body, attachment_path)
        
        if email_sent:
            # Update email status in the database
            update_query = "UPDATE invoices SET emailstatus = True WHERE invoice_id = %s;"
            cursor.execute(update_query, (invoice_id,))
            conn.commit()
            
            # Log success
            log_message = f"Invoice: {invoice_id}, Customer: {name}, Amount: {amount}, Status: Sent"
            add_log_entry(log_message, success=True)
        else:
            # Log failure
            log_message = f"Invoice: {invoice_id}, Customer: {name}, Amount: {amount}, Status: Failed"
            add_log_entry(log_message, success=False)

    messagebox.showinfo("Info", "All unsent invoices have been processed.")

    cursor.close()
    conn.close()

def add_log_entry(text, success=True):
    """
    Adds a new log entry to the log_text widget.
    - text: The log entry text to display.
    - success: Boolean to indicate if the message is a success (True) or failure (False).
    """
    log_text.config(state="normal")  # Enable the text widget temporarily

    # Set color based on success or failure
    color = "green" if success else "red"
    log_text.insert("end", text + "\n", color)  # Insert the log entry
    log_text.tag_configure("green", foreground="green")  # Configure tag for green
    log_text.tag_configure("red", foreground="red")  # Configure tag for red

    log_text.config(state="disabled")  # Disable the text widget again
    log_text.see("end")  # Scroll to the end to show the latest entry

# saving to a log file on close:

def save_log_to_file():
    try:
        # Get all text from log_text
        log_text.config(state="normal")  # Temporarily enable to access the text
        log_content = log_text.get("1.0", "end-1c")  # Get content without the last newline
        log_text.config(state="disabled")
        
        # Format the filename with the current datetime
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"log_{current_time}.txt"
        
        # Write to file
        with open(file_path, "w") as file:
            file.write(log_content)
        
        print(f"Log saved to {file_path}.")
    except Exception as e:
        print(f"Failed to save log: {e}")

# Handle the app close event without asking
def on_close():
    save_log_to_file()  # Automatically save the log when closing
    root.destroy()       # Close the application

# Bind the window close event
root.protocol("WM_DELETE_WINDOW", on_close)


########################################################

basic_label = tk.Label(root, text=" Send invoices by invoice number:")
basic_label.pack(pady = 10)

frame = tk.Frame(root)
frame.pack(pady=20, padx=10, fill="x")

# Entry for "Invoice Number From"
label_from = tk.Label(frame, text="From:")
label_from.pack(side="left", padx=(0, 5))
entry_invoice_from = tk.Entry(frame, width=10)
entry_invoice_from.pack(side="left")

# Entry for "Invoice Number To"
label_to = tk.Label(frame, text="To:")
label_to.pack(side="left", padx=(15, 5))
entry_invoice_to = tk.Entry(frame, width=10)
entry_invoice_to.pack(side="left")

# "Send" button on the right
button_send = tk.Button(frame, text="Send", command=submit_invoice_range)
button_send.pack(side="right")

###########################################################

basic_label = tk.Label(root, text=" Send all unsent invoices of customer:")
basic_label.pack()

frame2= tk.Frame(root)
frame2.pack(pady=20, padx=10, fill="x")

# Entry for "customer_select"
label_from = tk.Label(frame2, text="Customer ID:")
label_from.pack(side="left", padx=(0, 5))
customer_select = tk.Entry(frame2, width=10)
customer_select.pack(side="left")


# "Send" button on the right
button_send = tk.Button(frame2, text="Send", command=submit_customer_select)
button_send.pack(side="right")


################################################################

basic_label = tk.Label(root, text=" Send all unsent invoices:")
basic_label.pack()

button_send_all = tk.Button(root, text="Send all", command=send_all)
button_send_all.pack(pady=20)

###############################################################

# Create a frame to hold the Text widget and the Scrollbar
framelog = tk.Frame(root)
framelog.pack(fill="both", expand=True, padx=10, pady=(5, 10))

# Define log_text widget
log_text = tk.Text(framelog, height=10, wrap="word", state="disabled", bg="lightblue", font=("Arial", 10))
log_text.pack(side="left", fill="both", expand=True)

# Create a scrollbar and link it to the log_text widget
scrollbar = tk.Scrollbar(framelog, command=log_text.yview)
scrollbar.pack(side="right", fill="y")

# Configure the text widget to use the scrollbar
log_text.config(yscrollcommand=scrollbar.set)

# Run the application
root.mainloop()