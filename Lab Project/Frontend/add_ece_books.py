import requests

API_URL = "http://127.0.0.1:5000/add_book"

books = [
    # ECE
    {"book_name": "Electronic Devices and Circuit Theory", "author_name": "Robert L. Boylestad, Louis Nashelsky"},
    {"book_name": "Principles of Communication Systems", "author_name": "Herbert Taub, Donald Schilling"},
    {"book_name": "Microelectronic Circuits", "author_name": "Sedra & Smith"},
    {"book_name": "Modern Digital and Analog Communication Systems", "author_name": "B.P. Lathi"},
    {"book_name": "Digital Signal Processing", "author_name": "John G. Proakis, Dimitris G. Manolakis"},
    # Mechanical
    {"book_name": "Engineering Thermodynamics", "author_name": "P.K. Nag"},
    {"book_name": "Strength of Materials", "author_name": "R.K. Bansal"},
    {"book_name": "Theory of Machines", "author_name": "S.S. Rattan"},
    {"book_name": "Fluid Mechanics", "author_name": "Yunus A. Cengel, John M. Cimbala"},
    {"book_name": "Heat and Mass Transfer", "author_name": "J.P. Holman"},
    # Civil
    {"book_name": "Surveying Vol. 1", "author_name": "B.C. Punmia"},
    {"book_name": "Building Materials", "author_name": "S.K. Duggal"},
    {"book_name": "Structural Analysis", "author_name": "R.C. Hibbeler"},
    {"book_name": "Soil Mechanics and Foundations", "author_name": "B.C. Punmia"},
    {"book_name": "Concrete Technology", "author_name": "M.S. Shetty"},
    # Computer Science
    {"book_name": "Introduction to Algorithms", "author_name": "Cormen, Leiserson, Rivest, Stein"},
    {"book_name": "Operating System Concepts", "author_name": "Silberschatz, Galvin, Gagne"},
    {"book_name": "Database System Concepts", "author_name": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan"},
    {"book_name": "Computer Networks", "author_name": "Andrew S. Tanenbaum"},
    {"book_name": "Artificial Intelligence: A Modern Approach", "author_name": "Stuart Russell, Peter Norvig"},
    # Electrical
    {"book_name": "Electrical Machinery", "author_name": "P.S. Bimbhra"},
    {"book_name": "Power System Engineering", "author_name": "I.J. Nagrath, D.P. Kothari"},
    {"book_name": "Control Systems Engineering", "author_name": "Norman S. Nise"},
    {"book_name": "Electrical Technology", "author_name": "B.L. Theraja"},
    {"book_name": "Network Analysis", "author_name": "Van Valkenburg"}
]

for book in books:
    payload = {
        "role": "admin",
        "book_name": book["book_name"],
        "author_name": book["author_name"]
    }
    response = requests.post(API_URL, json=payload)
    print(f"Adding '{book['book_name']}' by {book['author_name']}: {response.json()}")
