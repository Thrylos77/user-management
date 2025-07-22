# Django RBAC User Management

A Django-based REST API for user management with Role-Based Access Control (RBAC).  
Includes user registration, authentication, password management, soft deletion, and role management.

---

## Features

- Custom user model with roles (Admin, User, Manager)
- JWT authentication (with `djangorestframework-simplejwt`)
- User registration and detail endpoints
- Change password endpoint
- Soft delete (deactivation) instead of hard delete for users
- List/filter users by active status
- List available roles via API
- Admin-only endpoints for sensitive operations
- OpenAPI/Swagger documentation (with `drf-spectacular`)

---

## Quick Start

### 1. **Clone the repository**

```bash
git clone <your-repo-url>
cd django-rbac
```

### 2. **Install dependencies**

```bash
pip install -r requirements.txt
# or, if you use poetry:
poetry install
```

### 3. **Set up environment variables**

Create a `.env` file at the project root (see `.env.example` if available):

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_FIRSTNAME=Admin
DJANGO_SUPERUSER_LASTNAME=User
```

### 4. **Apply migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. **Run the development server**

```bash
python manage.py runserver
```

---

## API Endpoints

### 1.
/api/users/<users urls>

| Method | Endpoint          | Description                        | Auth required | Admin only |
|--------|-------------------|------------------------------------|---------------|------------|
| POST   | `register/`       | Register a new user                | Yes           | Yes        |
| GET    | `me/`             | Get current user details           | Yes           | No         |
| GET    | `list/`           | List users (filter by is_active)   | Yes           | Yes        |
| GET    | `roles/`          | List available roles               | Yes           | Yes        |
| PATCH  | `<id_user>/`      | Update user info                   | Yes           | Yes        |
| DELETE | `<id_user>/`      | Deactivate (soft delete) user      | Yes           | Yes        |
| POST   | `change-password/`| Change own password                | Yes           | No         |

- **Filter users**: `/users/list/?is_active=true` or `/users/list/?is_active=false`

---

## Authentication

- Uses JWT tokens (`Authorization: Bearer <token>`)
- Obtain a token via your authentication endpoint (not shown here, but typically `/api/token/`)

---

## Soft Delete

- Deleting a user sets `is_active=False` instead of removing the record.
- Inactive users cannot log in.

---

## Documentation

- Interactive API docs available at `/api/schema/swagger-ui/` (or similar, depending on your config).

---

## License


---

## Credits

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/)