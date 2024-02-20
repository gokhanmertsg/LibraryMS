# Library Management System

The Library Management System is a FastAPI-based project that provides CRUD operations for managing books in a library. It supports JWT authentication, allowing librarians to perform actions such as adding and deleting books.

## Features

- **CRUD Operations:**
  - Librarian can add a new book to the library.
  - Librarian can delete a book from the library.
  - Librarian can read all books from the library.
    
  - Students can borrow books from the library.
  - Students can return books to the library.
  - Students can read their own books from the library.
  - Students can read available books from the library.

- **Book Types:**
  - Two types of books are supported: School Book and Reading Book.
  - School Books contain additional information such as the subject.

- **JWT Authentication:**
  - Librarian actions are protected by JWT authentication.
  - Librarian needs to authenticate with a valid token to perform CRUD operations.

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gokhanmertsg/LibraryMS.git

2. Install dependencies using Poetry:
   ```bash
    cd library-management-system
    poetry install
3. Configuration
   Create a '.env' file in the project root and configure the following variables:
   ```
   SQLALCHEMY_DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256   
4. Running PostgreSQL on Docker
   Firstly, configure connection information from docker.compose.yml. Then,
   ```bash
   apt install docker.io
   docker-compose up --build

6. Running the application
   ```bash
   poetry run uvicorn app.main:app --reload

## Contact
For any questions or feedback, feel free to contact us at gokhan@sensgreen.com
