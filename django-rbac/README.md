# Django RBAC User Management

A Django-based REST API for user management with Role-Based Access Control (RBAC).
Includes user registration, authentication, password management, soft deletion, and detailed auditing features.  

---

## Features

- Custom user model with extensible roles (`ADMIN`, `USER`, `MANAGER`).
- Secure JWT authentication (`djangorestframework-simplejwt`) with token rotation and blacklisting.
- Full user lifecycle management (register, update, soft-delete).
- **Dynamic RBAC**: Create and manage roles and permissions via the API.
- Change password endpoint
- Password reset via email OTP.
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

All endpoints are prefixed with `/api/`. The table below shows the full path for each endpoint.

| Method   | Endpoint                     | Description                                                 |
|----------|------------------------------|-------------------------------------------------------------|
**Auth**
| POST     | `/login/`                    | Obtain JWT access and refresh tokens.                       |
| POST     | `/token/refresh/`            | Get a new access token using a refresh token.               |
| POST     | `/logout/`                   | Invalidates the refresh token and logs the logout action.   |
**Users**
| POST     | `/users/register/`           | Register a new user.                                        |
| GET      | `/users/`                    | List users (filter by `is_active`).                         |
| GET      | `/users/me/`                 | Get current authenticated user's details.                   |
| POST     | `/users/change-password/`    | Change own password.                                        |
| POST     | `/users/request-otp/`        | Request a One-Time Password (OTP) for password reset.       |
| POST     | `/users/reset-password/`     | Reset password using a valid OTP.                           |
| GET      | `/users/<pk>/`               | Retrieve a specific user's details.                         |
| PUT/PATCH| `/users/<pk>/`               | Update a specific user's info.                              |
| DELETE   | `/users/<pk>/`               | Deactivate (soft delete) a user.                            |
**Audit**
| GET      | `/users/history/`            | Get the complete history of all user data changes.          |
| GET      | `/users/history/<pk>`        | Get data change history for a specific user.                |
| GET      | `/users/audit-log/`          | Get the log of all user actions (login, etc.).              |

**RBAC Management**
| GET      | `/permissions/`              | List all available permissions.                             |
| GET      | `/permissions/<pk>/`         | Retrieve a specific permission.                             |
| PUT/PATCH| `/permissions/<pk>/`         | Update a permission's details (label, description).         |
| GET      | `/roles/`                    | List all available roles.                                   |
| POST     | `/roles/`                    | Create a new role with a set of permissions.                |
| GET      | `/roles/<pk>/`               | Retrieve a specific role and its permissions.               |
| PUT/PATCH| `/roles/<pk>/`               | Update a role's details and permissions.                    |
| DELETE   | `/roles/<pk>/`               | Delete a role.                                              |
| POST     | `/roles/assign/<user_id>/`   | Assign a role to a user.                                    |
| POST     | `/roles/remove/<user_id>/`   | Remove a role from a user.                                  |
**RBAC History**
| GET      | `/permissions/history/`      | Get the complete history for all permissions.               |
| GET      | `/permissions/history/<pk>/` | Get the history for a specific permission.                  |
| GET      | `/roles/history/`            | Get the complete history for all roles.                     |
| GET      | `/roles/history/<pk>/`       | Get the history for a specific role.                        |

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