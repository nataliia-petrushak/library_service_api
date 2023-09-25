# Readify API
The Readify API is a comprehensive application 
programming interface (API) designed to 
support various functionalities within a 
library management system. It consists of 
multiple services, each serving a 
distinct purpose. Here's an 
overview of the Readify API and its key components:

### Books Service:
The Books Service is responsible 
for managing books within the library, 
including book creation, retrieval, updating, 
and deletion. Only admin can add or update books. Authorized and unauthorized users can see all book list

### Users Service:
* Registration: Users can create accounts by providing a username, email, and password.
* Authentication: Users can log in using their credentials, and the API provides a token for authentication in subsequent requests.
* User Profile: Users can view and update their profile information, including names, profile pictures, and bio.

### Borrowings Service:
The Borrowings Service manages the borrowing of books by users and tracks relevant details.

* Add New Borrowing: Users can create new borrowing records when borrowing books, which automatically updates the inventory count.
* Get Borrowings by User ID and Status: Retrieve a list of borrowings based on a user's ID  (for admin only) and whether the borrowing is still active.
* Get Specific Borrowing: Retrieve detailed information about a specific borrowing transaction.
* Return Book: This API endpoint updates the return date of a borrowed book. If borrowing was expired - a new payment session with status "FINE" will be created.

### Notifications Service (Telegram):
The Notifications Service is responsible for sending notifications related to library activities using Telegram. 
* Inform library administrators about newly created borrowing transactions 
* Send notifications when borrowings are overdue and books have not been returned on time.
* Notify administrators when successful payments are made.
* This service operates in parallel clusters or processes, utilizing packages like Django Q or Django Celery for efficient task handling.

### Payments Service (Stripe):
The Payments Service handles payment processing for book borrowings via the Stripe payment gateway.

* Perform Payments for Book Borrowings: Users can make payments for borrowing books through this service.
* Check Successful Stripe Payment: Verify the success of a Stripe payment.
* Return Payment Paused Message: Provide information to users when a payment is temporarily paused.

### Installing using GitHub
Install PostgresSQL and create db

```shell
git clone https://github.com/nataliia-petrushak/library_service_api.git
cd library_service_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set POSTGRES_HOST=<your db hostname>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=secretpassword
=<your db password>
set SECRET_KEY=<your secret key>
```
### Run with docker
Docker should be installed

```shell
docker-compose build
docker-compose up
```

### Getting access
- create user via /api/user/register
- get access token via /api/user/token/

### Getting started
- Download [ModHeader](https://chrome.google.com/webstore/detail/modheader-modify-http-hea/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en)
- Add name and token
- Now you are authorised and can use the API