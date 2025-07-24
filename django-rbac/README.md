# Django RBAC User Management

A Django-based REST API for user management with Role-Based Access Control (RBAC).
Includes user registration, authentication, password management, soft deletion, and detailed auditing features.  

---

## Features

- Custom user model with extensible roles (`ADMIN`, `USER`, `MANAGER`).
- Secure JWT authentication (`djangorestframework-simplejwt`) with token rotation and blacklisting.
- Full user lifecycle management (register, update, soft-delete).
- Change password endpoint
- Soft delete (deactivation) instead of hard delete for users
- List/filter users by active status
- **Detailed Auditing**:
    - **Data History**: Tracks every change to user data (powered by `django-simple-history`).
    - **Action Log**: Records key security events like login, logout, and password changes.
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
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=adminpassword
SUPERUSER_FIRSTNAME=Admin
SUPERUSER_LASTNAME=User
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
All endpoints are prefixed with `/api/`.
Users and audit endpoints are prefixed with `/users/`

| Method    | Endpoint             | Description                                                 | Permissions Required |
|-----------|----------------------|-------------------------------------------------------------|----------------------|
| **Auth**  |                      |                                                             |                      |
| POST      | `connexion/token`    | Obtain JWT access and refresh tokens.                       | Public               |
| POST      | `token/refresh/`     | Get a new access token using a refresh token.               | Public               |
| POST      | `logout/`            | Invalidates the refresh token and logs the logout action.   | Authenticated        |
| **Users** |                      |                                                             |                      |
| GET       | `me/`                | Get current authenticated user's details.                   | Authenticated        |
| POST      | `change-password/`   | Change own password.                                        | Authenticated        |
| POST      | `register/`          | Register a new user.                                        | Admin only           |
| GET       | `list/`              | List users (filter by `is_active`).                         | Admin only           |
| GET       | `roles/`             | List available roles.                                       | Admin only           |
| GET       | `<pk>/`              | Retrieve a specific user's details.                         | Admin only           |
| PUT/PATCH | `<pk>/`              | Update a specific user's info.                              | Admin only           |
| DELETE    | `<pk>/`              | Deactivate (soft delete) a user.                            | Admin only           |
| **Audit** |                      |                                                             |                      |
| GET       | `history/`           | Get the complete history of all user data changes.          | Admin only           |
| GET       | `<pk>/history/`      | Get data change history for a specific user.                | Admin only           |
| GET       | `audit-log/`         | Get the log of all user actions (login, etc.).              | Admin only           |

---

## Authentication

- Uses JWT tokens (`Authorization: Bearer <token>`).
- **Access Token Lifetime**: 15 minutes.
- **Refresh Token Lifetime**: 1 day.
- **Security**: Refresh tokens are rotated and blacklisted after use to prevent replay attacks.

---


---

## Permissions Model (RBAC)

The project is built with Role-Based Access Control in mind. The current permission model is simple and effective:

- **Authenticated User (any role)**: Can view their own profile (`/me`) and change their own password.
- **Admin User (`is_staff=True`)**: Has access to all other endpoints, including user management, full history, and audit logs.

The `role` field (`ADMIN`, `MANAGER`, `USER`) is included in the user model and API responses, making it easy to build more granular frontend logic or extend backend permissions in the future (e.g., allowing a `MANAGER` to view users in their team).

---

## Auditing and History

The system maintains two separate logs for complete traceability:
1.  **Data History (`/api/users/history/`)**: Powered by `django-simple-history`, this log provides a detailed snapshot of a user's data every time it is changed. It answers the question: "What did this user object look like at a specific point in time?".
2.  **Action Log (`/api/users/audit-log/`)**: A custom log that records high-level security events. It answers the question: "What actions did a user perform?".

---

## Soft Delete

- Deleting a user sets `is_active=False` instead of removing the record.
- Inactive users cannot log in.

---

## Maintenance

---

### Flushing Expired Tokens

The JWT blacklist can grow over time. A management command is provided to clean it up. It is recommended to run this command periodically (e.g., daily via a cron job).

```bash
python manage.py flush_expired_tokens
```

---

## License

---

## Credits

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/)
- [django-simple-history](https://django-simple-history.readthedocs.io/)