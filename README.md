📚 Lab Management System
A system for managing lab resources, books, and student interactions.

🚀 Project Structure
bash
lab-project/
├── admin/                  # Admin scripts
│   ├── admin_dashboard     # Admin control panel
│   ├── admin_student_is    # Student status management
│   └── delivery            # Resource delivery logs
├── backend/                # Core logic
│   ├── init_db             # Database initialization
│   └── issue_book          # Book issuance system
├── student/                # Student interfaces
│   ├── student_dashbook    # Student dashboard
│   └── view_books          # Book catalog
└── frontend/               # User interfaces (HTML/JS)
    ├── add_book            # Add new books
    ├── add_eco_books       # Eco-friendly materials
    └── return_book         # Book return system

    
🛠️ Setup Instructions
Prerequisites
Node.js (for backend)

MySQL/SQLite (for database)

Installation
Clone the repo:

bash
git clone https://github.com/yourusername/lab-project.git
Initialize the database:

bash
cd lab-project/backend
node init_db
Start the server:

bash
node issue_book  # Or your main server file
🎯 Features
Admin: Manage students, books, and deliveries.

Student: View books, check availability.

Automation: Track book issues/returns.

