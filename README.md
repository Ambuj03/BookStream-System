# 📚 Book-Stream-System

**Book-Stream-System** is a robust Django-based application designed to streamline the management of book inventory and distribution for organizations. It facilitates efficient tracking of book stocks, sales, donations, and transfers between administrators and distributors.

This has two purposes : Sellers can keep track of their records after each sell and the admin can oversee this, admin will update his master inventory and then will 
disburse books to seller's inventory via admin panel, also the admin can track all the other information that seller collects (For eg: Customer Details).

## 🚀 Features

- **User Management**: Role-based access control distinguishing administrators and distributors.
- **Inventory Management**: Monitor books across master and distributor inventories.
- **Transaction Processing**: Record book distributions along with customer details.
- **Donation Tracking**: Manage and track book donations effectively.
- **Notifications System**: Receive real-time alerts for low stock levels.
- **Asynchronous Task Handling**: Utilizes Celery with Redis for background task processing.

## 🛠️ Tech Stack

- **Backend**: Python, Django
- **Database**: MySQL
- **Asynchronous Task Queue**: Celery
- **Message Broker**: Redis
- **Frontend**: Django Templates

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- MySQL Server
- Redis Server

### Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Ambuj03/BookStream-System.git
   cd BookStream-System

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt

4. **Environment Configuration**
   : Create a .env file from the example and edit it with your own values:

   ```bash
   cp .env.example .env
   Then edit the file to match your local setup:

5. **Apply Migrations**

   ```bash
   python manage.py migrate

6. **Create a Superuser**

   ```bash
   python manage.py createsuperuser

6. **Run the Development Server**

   ```bash
   python manage.py runserver

## ⚙️ Asynchronous Task Processing with Celery and Redis
The application leverages Celery for handling asynchronous tasks, with Redis serving as the message broker.

### Starting Redis Server
In a new terminal window (with your virtualenv activated), run:
    
    celery -A BM_DJANGO worker --loglevel=info

## 🧪 Running Tests
    python manage.py test

## 📁 Project Structure

    BookStream-System/
    ├── BM_DJANGO/                 # Core Django project directory
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── bm_app/                    # Main application logic
    │   ├── migrations/
    │   ├── templates/
    │   ├── static/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── tasks.py               # Celery tasks
    │   ├── tests.py
    │   └── views.py
    ├── templates/                 # HTML templates
    ├── .env.example               # Example environment variables file
    ├── .gitignore
    ├── manage.py
    └── requirements.txt

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for details.

## 📬 Contact
For any inquiries or feedback, please contact [Ambuj Mishra] at [mishraambuj8269@gmail.com].










   

