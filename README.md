
# Book Distribution Management System

A comprehensive Django-based application for managing book inventory and distribution activities, built with a focus on ease of use and efficiency.

This application serves two purposes :-

For distributors(sellers) to keep record for their sales and for admin to manage their own inventory and to transfer book to distribtuor's inventory and to keep track of records of all this incoming and outgoing of books.



## Features

User Management: Role-based access control for administrators and distributors

Inventory Management: Track books across master inventory and distributor inventory

Transaction Processing: Record book distributions with customer information

Donation Tracking: Track and manage donations

Notifications System: Real-time notifications for low stock and new allocations

Receipt Generation: Generate transaction receipts

SMS Integration: Send confirmation messages to customers

Export Functionality: Export data to various formats

## Tech Stack

**Backend:** Django 5.1 \
**Database:** MySQL\
**Task Queue:** Celery with Redis\
**Frontend:** Bootstrap 5, jQuery, Select2\
**Notifications:** Custom notification system\
**SMS:** Twilio integration


## Installation & Setup

    1. Clone the repository
    2. Create a virtual environment
    3. Install dependencies
    4. Configure environment variables :
       Create a .env file in the project root (use .env example as a template) 
    5. Create MySQL database
    6. Apply migrations
    7. Create a superuser
    8. Run the server
    9. Start Celery worker (in a separate terminal)
    10. Start Celery beat (in a separate terminal)
