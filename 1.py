import sqlite3
from datetime import datetime


def create_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        BookID TEXT PRIMARY KEY,
        Title TEXT,
        Author TEXT,
        ISBN TEXT,
        Status TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID TEXT PRIMARY KEY,
        Name TEXT,
        Email TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        ReservationID TEXT PRIMARY KEY,
        BookID TEXT,
        UserID TEXT,
        ReservationDate TEXT,
        FOREIGN KEY(BookID) REFERENCES Books(BookID),
        FOREIGN KEY(UserID) REFERENCES Users(UserID)
    );
    ''')

    conn.commit()
    conn.close()


def add_book():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    while True:
        BookID = input("Enter Book ID: ")
        cursor.execute("SELECT * FROM Books WHERE BookID = ?", (BookID,))
        existing_book = cursor.fetchone()
        if existing_book:
            print("This BookID already exists. Please enter a different BookID.")
        else:
            break

    Title = input("Enter Book Title: ")
    Author = input("Enter Author: ")
    ISBN = input("Enter ISBN: ")
    Status = "Available"

    cursor.execute("INSERT INTO Books VALUES (?, ?, ?, ?, ?)", (BookID, Title, Author, ISBN, Status))
    conn.commit()
    conn.close()
    print(f"Book {Title} added successfully.")


def find_book():
    BookID = input("Enter Book ID: ")
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    query = '''
    SELECT Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status, 
           Reservations.ReservationID, Reservations.ReservationDate, 
           Users.UserID, Users.Name, Users.Email
    FROM Books
    LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
    LEFT JOIN Users ON Reservations.UserID = Users.UserID
    WHERE Books.BookID = ?
    '''

    cursor.execute(query, (BookID,))
    result = cursor.fetchone()

    if result:
        print(
            f"Book Details: ID: {result[0]}, Title: {result[1]}, Author: {result[2]}, ISBN: {result[3]}, Status: {result[4]}")

        if result[5]:
            print(f"Reservation Details: Reservation ID: {result[5]}, Reservation Date: {result[6]}")
            print(f"User Details: User ID: {result[7]}, Name: {result[8]}, Email: {result[9]}")
        else:
            print("This book is currently not reserved.")
    else:
        print("Book not found.")

    conn.close()


def find_book_status():
    identifier = input("Enter BookID/Title/UserID/ReservationID: ")
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    query = '''
    SELECT Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status, 
           Reservations.ReservationID, Reservations.ReservationDate, 
           Users.UserID, Users.Name, Users.Email
    FROM Books
    LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
    LEFT JOIN Users ON Reservations.UserID = Users.UserID
    '''

    if identifier.startswith('LB'):
        query += " WHERE Books.BookID = ?"
    elif identifier.startswith('LU'):
        query += " WHERE Users.UserID = ?"
    elif identifier.startswith('LR'):
        query += " WHERE Reservations.ReservationID = ?"
    else:
        query += " WHERE Books.Title = ?"

    cursor.execute(query, (identifier,))
    result = cursor.fetchone()

    def print_details(result):
        if result:
            print(
                f"Book Details: ID: {result[0]}, Title: {result[1]}, Author: {result[2]}, ISBN: {result[3]}, Status: {result[4]}")
            if result[5]:  # If ReservationID exists
                print(f"Reservation Details: Reservation ID: {result[5]}, Reservation Date: {result[6]}")
                print(f"User Details: User ID: {result[7]}, Name: {result[8]}, Email: {result[9]}")
            else:
                print("This book is currently not reserved.")

    if result:
        print_details(result)
    else:
        print("Not found in database.")

    conn.close()


def find_all_books():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    query = '''
    SELECT Books.BookID, Books.Title, Books.Author, Books.ISBN, Books.Status, 
           Reservations.ReservationID, Reservations.ReservationDate, 
           Users.UserID, Users.Name, Users.Email
    FROM Books
    LEFT JOIN Reservations ON Books.BookID = Reservations.BookID
    LEFT JOIN Users ON Reservations.UserID = Users.UserID
    '''

    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        print("All Books:")
        for result in results:
            print(
                f"Book Details: ID: {result[0]}, Title: {result[1]}, Author: {result[2]}, ISBN: {result[3]}, Status: {result[4]}")

            if result[5]:  # If ReservationID exists
                print(f"Reservation Details: Reservation ID: {result[5]}, Reservation Date: {result[6]}")
                print(f"User Details: User ID: {result[7]}, Name: {result[8]}, Email: {result[9]}")
            else:
                print("This book is currently not reserved.")
    else:
        print("No books found.")

    conn.close()


def update_book():
    BookID = input("Enter Book ID to update: ")
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Books WHERE BookID = ?", (BookID,))
    book = cursor.fetchone()

    if book:
        print("What would you like to update?")
        print("1. Book details (Title, Author, ISBN)")
        print("2. Reservation status")

        choice = input("Enter your choice (1 or 2): ")

        if choice == '1':
            new_title = input("Enter new title: ")
            new_author = input("Enter new author: ")
            new_isbn = input("Enter new ISBN: ")
            cursor.execute("UPDATE Books SET Title = ?, Author = ?, ISBN = ? WHERE BookID = ?",
                           (new_title, new_author, new_isbn, BookID))

        elif choice == '2':
            new_status = input("Enter new status (Available, Reserved, Checked Out, In Maintenance): ")
            cursor.execute("UPDATE Books SET Status = ? WHERE BookID = ?", (new_status, BookID))

            if new_status == 'Reserved':
                # Generate a unique ReservationID based on the current timestamp
                reservation_id = 'R' + datetime.now().strftime('%Y%m%d%H%M%S')

                new_user_id = input("Enter UserID who reserved the book: ")
                new_user_name = input("Enter the name of the user who reserved the book: ")
                new_user_email = input("Enter the email of the user who reserved the book: ")

                # Insert or update the user in the Users table
                cursor.execute("INSERT OR IGNORE INTO Users (UserID, Name, Email) VALUES (?, ?, ?)",
                               (new_user_id, new_user_name, new_user_email))

                new_reservation_date = datetime.now().strftime('%Y-%m-%d')
                # Insert the new reservation into the Reservations table
                cursor.execute(
                    "INSERT INTO Reservations (ReservationID, BookID, UserID, ReservationDate) VALUES (?, ?, ?, ?)",
                    (reservation_id, BookID, new_user_id, new_reservation_date))

            else:
                cursor.execute("DELETE FROM Reservations WHERE BookID = ?", (BookID,))

        conn.commit()
        print("Book details updated successfully.")

    else:
        print("Book not found.")

    conn.close()


def delete_book():
    BookID = input("Enter Book ID to delete: ")
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Check if the book exists in the Books table
    cursor.execute("SELECT * FROM Books WHERE BookID = ?", (BookID,))
    book = cursor.fetchone()

    if book:
        # Delete from Reservations table if the book is reserved
        cursor.execute("DELETE FROM Reservations WHERE BookID = ?", (BookID,))

        # Delete from Books table
        cursor.execute("DELETE FROM Books WHERE BookID = ?", (BookID,))

        conn.commit()
        print("Book deleted successfully.")
    else:
        print("Book not found.")

    conn.close()


def main():
    while True:
        print("\nLibrary Management System")
        print("1. Add a new book")
        print("2. Find a book's detail")
        print("3. Find a book's reservation status")
        print("4. Find all the books")
        print("5. Update book details")
        print("6. Delete a book")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_book()
        elif choice == '2':
            find_book()
        elif choice == '3':
            find_book_status()
        elif choice == '4':
            find_all_books()
        elif choice == '5':
            update_book()
        elif choice == '6':
            delete_book()
        elif choice == '7':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")


# Initialize the database
create_database()
# Run the main program
main()
