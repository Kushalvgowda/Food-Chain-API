# 🍽️ Food Chain API

A robust and RESTful Django API for managing a food ordering system, including menu items, categories, carts, orders, and role-based access for managers, delivery crew, and customers.

## 🚀 Features

- **Authentication & Authorization**  
  Token-based auth with permissions for Admins, Managers, Delivery Crew, and Customers.

- **User Role Management**  
  Add/remove users to/from Manager and Delivery Crew groups via secure endpoints.

- **Menu Management**  
  CRUD operations for menu items with support for filtering, ordering, and pagination.

- **Category Management**  
  Admins can add categories. Public can view them.

- **Item of the Day**  
  Set and retrieve the featured menu item.

- **Cart Management**  
  Customers can add, view, and delete cart items, or clear the entire cart.

- **Order System**  
  - Customers can place orders.
  - Managers can assign delivery crew.
  - Delivery crew can mark orders as delivered.
  - Role-based order retrieval.

- **Throtling & Rate limiting**
  - Custom throtling rate for both anonymous and authenticated users

- **Djoser implementation**
  - User creation, bearer-token and many more using `Djoser`

- **Swagger/OpenAPI Documentation**  
  Fully documented using `drf-yasg`.
  

## 📁 Endpoints Overview

| Resource               | Methods                          | Roles Allowed                    |
|------------------------|----------------------------------|----------------------------------|
| `api/menu-items/`            | `GET`, `POST`                    | Admin, Manager, Customer(GET), Delivery-crew(GET)                            |
| `api/menu-item/<int:pk>`       | `GET`, `PATCH`, `DELETE`                         | Admin, Manager, Customer(GET), Delivery-crew(GET)                            |
| `api/groups/manager/users`      | `GET`, `POST`                    | Admin                  |
| `api/groups/manager/users/<int:pk>` | `GET`, `PATCH`, `DELETE`                         | Admin                   |
| `api/groups/delivery-crew/users`         | `GET`, `POST`                            | Admin, Manager                          |
| `api/groups/delivery-crew/users/<int:pk>`         | `GET`, `POST`, `DELETE`, `PATCH`                           | Admin, Manager                   |
| `api/cart/menu-items'`    | `GET`, `POST`  | Customer                  |
| `api/cart/menu-items/<int:pk>`         | `GET`, `DELETE`                            | Customer                          |
| `api/orders/`         | `GET`, `POST`                           | Customer, Manager                            |
| `api/orders/<int:order_id>`               | `GET`, `DELETE`          | Customer, Manager(GET)                  |
| `api/category/`          | `GET` , `POST`                        | Authenticated users                 |
| `api/itemofday/`             | `GET`, `POST`, `PATCH`, `DELETE`                    | Admin, Manager, Customer(GET)            |
| `api/api-token-auth//`  | `GET`           | Authenticated users                |
| `api/token/`      | `GET`                            | Authenticated users                            |
| `api/token/refresh/`      | `GET`                           | Authenticated users                |
| `api/token/blacklist/` | 'GET` |  Authenticated users |



## 🔒 Permissions

| Role         | Description                                             |
|--------------|---------------------------------------------------------|
| **Admin**    | Full access to all resources except for customer access.|
| **Manager**  | Can manage menu, delivery crew, orders.                 |
| **Delivery** | Can view assigned orders and mark delivered.            |
| **Customer** | Can manage own cart and place/view orders.              |

## 🛠️ Tech Stack

- **Backend**: `Django`, `Django REST Framework`
- **Auth**: Token-based (DRF), `JWT`
- **Docs**: `drf-yasg` (Swagger/OpenAPI)
- **Filtering**: `django-filter`
- **Pagination**: DRF PageNumberPagination
- **Database**: `PostgreSQL`
- **Container**: `Docker`


## 📄 API Documentation

Once running, visit:

```
http://localhost:8000/
```
or
```
http://localhost:8000/redoc/
```

## 🧪 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/your-username/little-lemon-api.git
cd Restaurants

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

## 🧾 License

This project is licensed under the [MIT License](LICENSE).