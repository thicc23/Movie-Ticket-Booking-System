import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class Movie:
    def __init__(self, name, theaters, seats):
        self.name = name
        self.theaters = theaters
        self.seats = seats

class User:
    def __init__(self, username, password):
        self.id = None
        self.username = username
        self.password = password
        self.tickets = []

    def save_to_database(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="movies"
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (self.username, self.password))
        self.id = cursor.lastrowid
        connection.commit()
        connection.close()

    @staticmethod
    def load_from_database(username):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="movies"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user_data = cursor.fetchone()
        connection.close()

        if user_data:
            user = User(user_data[1], user_data[2])
            user.id = user_data[0]
            return user

    def book_ticket(self, ticket_details):
        self.tickets.append(ticket_details)
        self.save_ticket_to_database(ticket_details)

    def save_ticket_to_database(self, ticket_details):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="movies"
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_tickets (user_id, ticket_details) VALUES (%s, %s)", (self.id, ticket_details))
        connection.commit()
        connection.close()

    def load_tickets_from_database(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="movies"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT ticket_details FROM user_tickets WHERE user_id=%s", (self.id,))
        self.tickets = [row[0] for row in cursor.fetchall()]
        connection.close()

    def delete_ticket_from_database(self, ticket_details):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="movies"
        )
        cursor = connection.cursor()
        cursor.execute("DELETE FROM user_tickets WHERE user_id=%s AND ticket_details=%s", (self.id, ticket_details))
        connection.commit()
        connection.close()

    def cancel_ticket(self, ticket_details):
        self.tickets.remove(ticket_details)
        self.delete_ticket_from_database(ticket_details)

class MovieTicketBookingSystem:
    def __init__(self):
        self.movies = [
            Movie("Barbie", ["Theater A", "Theater B"], ["A1", "A2", "A3", "B1"]),
            Movie("Batman Rises", ["Theater B", "Theater C"], ["B1", "B2", "B3"])
        ]
        self.users = []
        self.movie_list_model = None
        self.movie_list = None
        self.theater_combo_box = None
        self.seat_combo_box = None
        self.username_field = None
        self.password_field = None
        self.my_tickets_list_model = None
        self.my_tickets_list = None
        self.current_user = None

        self.create_and_show_gui()

    def create_and_show_gui(self):
        login_frame = tk.Tk()
        login_frame.title("Login or Create Account")
        

        login_button = tk.Button(login_frame, text="Login", command=self.show_login_window,)
        login_button.config(font=("Arial",30))
        create_account_button = tk.Button(login_frame, text="Create Account", command=self.show_create_account_window)
        create_account_button.config(font=("Arial",30))

        login_button.pack()
        create_account_button.pack()

        login_frame.geometry("600x400")
        login_frame.mainloop()

    def show_login_window(self):
        login_window = tk.Tk()
        login_window.title("Login")

        username_label = tk.Label(login_window, text="Username:")
        username_label.config(font=("Arial",30))
        self.username_field = tk.Entry(login_window)
        password_label = tk.Label(login_window, text="Password:")
        password_label.config(font=("Arial",30))
        self.password_field = tk.Entry(login_window, show="*")

        login_button = tk.Button(login_window, text="Login", command=self.login)
        login_button.config(font=("Arial",30))

        username_label.grid(row=0, column=0)
        self.username_field.grid(row=0, column=1)
        password_label.grid(row=1, column=0)
        self.password_field.grid(row=1, column=1)
        login_button.grid(row=2, column=0, columnspan=2)

        login_window.geometry("600x400")
        login_window.mainloop()

    def login(self):
        entered_username = self.username_field.get()
        entered_password = self.password_field.get()
        self.current_user = self.authenticate_user(entered_username, entered_password)

        if self.current_user:
            self.current_user.load_tickets_from_database()
            self.update_my_tickets_list_model()
            messagebox.showinfo("Success", "Login successful!")
            self.show_booking_window()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def show_create_account_window(self):
        create_account_window = tk.Tk()
        create_account_window.title("Create Account")

        new_username_label = tk.Label(create_account_window, text="New Username:")
        new_username_label.config(font=("Arial",30))
        new_username_field = tk.Entry(create_account_window)
        new_username_field.config(font=("Arial",30))
        new_password_label = tk.Label(create_account_window, text="New Password:")
        new_password_label.config(font=("Arial",30))
        new_password_field = tk.Entry(create_account_window, show="*")
        new_password_field.config(font=("Arial",30))

        create_account_button = tk.Button(create_account_window, text="Create Account", command=lambda: self.create_account(new_username_field.get(), new_password_field.get()))

        new_username_label.grid(row=0, column=0)
        new_username_field.grid(row=0, column=1)
        new_password_label.grid(row=1, column=0)
        new_password_field.grid(row=1, column=1)
        create_account_button.grid(row=2, column=0, columnspan=2)

        create_account_window.geometry("600x400")
        create_account_window.mainloop()

    def create_account(self, new_username, new_password):
        if not new_username or not new_password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
        elif self.user_exists(new_username):
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
        else:
            new_user = User(new_username, new_password)
            new_user.save_to_database()
            self.users.append(new_user)
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login_window()

    def show_booking_window(self):
        booking_frame = tk.Tk()
        booking_frame.title("Movie Ticket Booking System")

        movie_label = tk.Label(booking_frame, text="Select a movie:")
        movie_label.grid(row=0, column=0)

        self.movie_list_model = tk.StringVar()
        self.movie_list = tk.Listbox(booking_frame, listvariable=self.movie_list_model)
        for movie in self.movies:
            self.movie_list.insert(tk.END, movie.name)
        self.movie_list.grid(row=0, column=1)

        theater_label = tk.Label(booking_frame, text="Select a theater:")
        theater_label.grid(row=1, column=0)

        self.theater_combo_box = ttk.Combobox(booking_frame)
        self.theater_combo_box.grid(row=1, column=1)

        seat_label = tk.Label(booking_frame, text="Select a seat:")
        seat_label.grid(row=2, column=0)

        self.seat_combo_box = ttk.Combobox(booking_frame)
        self.seat_combo_box.grid(row=2, column=1)

        book_button = tk.Button(booking_frame, text="Book Ticket", command=self.book_ticket)
        book_button.grid(row=3, column=0, columnspan=2)

        self.my_tickets_list_model = tk.StringVar()
        self.my_tickets_list = tk.Listbox(booking_frame, listvariable=self.my_tickets_list_model)
        self.my_tickets_list.grid(row=4, column=0, columnspan=2)

        print(self.current_user.tickets)
        self.update_my_tickets_list_model()

        self.movie_list.bind("<<ListboxSelect>>", self.load_theaters_and_seats)

        username_label = tk.Label(booking_frame, text="Logged in as: " + (self.current_user.username if self.current_user else "Guest"))
        username_label.grid(row=5, column=0, columnspan=2)

        cancel_button = tk.Button(booking_frame, text="Cancel Ticket", command=self.cancel_ticket)
        cancel_button.grid(row=6, column=0, columnspan=2)

        booking_frame.geometry("600x400")
        booking_frame.mainloop()

    def book_ticket(self):
        if self.current_user:
            selected_movie = self.movie_list.get(tk.ACTIVE)
            selected_theater = self.theater_combo_box.get()
            selected_seat = self.seat_combo_box.get()
            selected_ticket_details = f"{selected_movie} at {selected_theater}, Seat: {selected_seat}"

            if selected_ticket_details not in self.current_user.tickets:
                self.current_user.book_ticket(selected_ticket_details)
                self.update_my_tickets_list_model()
                messagebox.showinfo("Success", f"Ticket booked for {selected_movie} at {selected_theater}, Seat: {selected_seat}")
            else:
                messagebox.showerror("Error", "This ticket has already been booked.")
        else:
            messagebox.showerror("Error", "Please log in to book a ticket.")

    def load_theaters_and_seats(self, event):
        selected_movie = self.movie_list.get(tk.ACTIVE)
        movie = self.find_movie_by_name(selected_movie)
        if movie:
            self.theater_combo_box["values"] = movie.theaters
            self.seat_combo_box["values"] = movie.seats

    def cancel_ticket(self):
        selected_ticket = self.my_tickets_list.get(tk.ACTIVE)
        if selected_ticket:
            self.current_user.cancel_ticket(selected_ticket)
            self.update_my_tickets_list_model()
            messagebox.showinfo("Success", f"Ticket canceled: {selected_ticket}")
        else:
            messagebox.showerror("Error", "Please select a ticket to cancel.")

    def update_my_tickets_list_model(self):
        if self.my_tickets_list_model:
            if self.current_user:
                self.my_tickets_list_model.set("\n".join(self.current_user.tickets))
            else:
                self.my_tickets_list_model.set("")

    def user_exists(self, username):
        return any(user.username == username for user in self.users)

    def authenticate_user(self, username, password):
        user = User.load_from_database(username)
        if user and user.password == password:
            return user

    def find_movie_by_name(self, name):
        return next((movie for movie in self.movies if movie.name == name), None)

    def main(self):
        self.create_database()
        self.create_and_show_gui()


    def create_database(self):
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS movies")
        cursor.execute("USE movies")

        # Create users table
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), password VARCHAR(255))")

        # Create user_tickets table
        cursor.execute("CREATE TABLE IF NOT EXISTS user_tickets (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, ticket_details TEXT, FOREIGN KEY(user_id) REFERENCES users(id))")

        connection.commit()
        connection.close()

if __name__ == "__main__":
    booking_system = MovieTicketBookingSystem()
    booking_system.main()
