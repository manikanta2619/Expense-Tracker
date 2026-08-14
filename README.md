# Expense Tracker

A comprehensive Django-based web application for tracking personal expenses and managing financial categories. Monitor your spending habits, categorize expenses, and gain insights into your financial patterns.

## Features

- 🔐 **User Authentication**: Secure login and registration system
- 💰 **Expense Management**: Create, edit, and delete expenses with ease
- 📊 **Dashboard**: Visual overview of spending patterns and expense summaries
- 🏷️ **Category Management**: Organize expenses by custom categories
- 🛒 **Shopping Cart**: Manage multiple expenses in a cart before finalizing
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🔒 **Secure**: Production-ready with security headers and CSRF protection
- 📈 **Order History**: Track all your expense entries and history

## Tech Stack

- **Backend**: Django 6.1 (Python Web Framework)
- **Database**: SQLite (with support for PostgreSQL)
- **Frontend**: HTML5, CSS3, Bootstrap
- **Authentication**: Django's built-in authentication system
- **Email**: Configurable email backend

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/manikanta2619/Expense-Tracker.git
cd Expense-Tracker
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```env
# Development Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - defaults to SQLite)
# DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser Account (Optional)

```bash
python manage.py createsuperuser
```

### 7. Load Sample Data (Optional)

```bash
python manage.py runscript seed_demo_data
```

## Running the Application

### Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

### Admin Panel

Access the Django admin panel at: `http://localhost:8000/admin`

## Project Structure

```
Expense-Tracker/
├── expense_tracker/          # Main Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── tracker/                 # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Form definitions
│   ├── urls.py              # App URL patterns
│   ├── admin.py             # Admin configuration
│   ├── migrations/          # Database migrations
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # HTML templates
├── static/                  # Project-wide static files
├── db.sqlite3              # SQLite database (development)
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (local)
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Usage

### User Registration

1. Click on "Register" on the login page
2. Enter your email, username, and password
3. Submit the form to create your account

### Creating an Expense

1. Log in to your account
2. Click "Add Expense" button
3. Fill in the expense details:
   - Amount
   - Category
   - Description
   - Date
4. Click "Save" to record the expense

### Viewing Dashboard

- The dashboard displays your spending summary
- View total expenses by category
- See recent transactions
- Track spending trends

### Managing Categories

1. Go to the "Categories" section
2. Create new categories for your expenses
3. Edit or delete existing categories as needed

## Deployment

### Production Settings

For production deployment, ensure:

1. **Environment Variables**: Create `.env` file with production values:
```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

2. **Database**: Consider using PostgreSQL instead of SQLite:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker
```

3. **Email**: Configure your email service:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Running Migrations

```bash
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic --noinput
```

### Starting the Application

With Gunicorn (recommended for production):
```bash
pip install gunicorn
gunicorn expense_tracker.wsgi:application --bind 0.0.0.0:8000
```

## Testing

Run the Django test suite:

```bash
python manage.py test
```

Run with verbose output:

```bash
python manage.py test --verbosity=2
```

## System Checks

Verify the application configuration:

```bash
python manage.py check
```

## Security Features

✅ CSRF Protection - Enabled by default
✅ SQL Injection Prevention - Django ORM protection
✅ Password Hashing - Bcrypt/PBKDF2 hashing
✅ Session Security - Secure session cookies
✅ XSS Protection - Template auto-escaping
✅ Security Headers - Configurable for production
✅ Environment Variables - Sensitive data protection

## Troubleshooting

### "No module named 'django'"
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

### "ModuleNotFoundError: No module named 'dotenv'"
- Install python-dotenv: `pip install python-dotenv`

### Database Migration Issues
- Delete `db.sqlite3` and migrations
- Run: `python manage.py migrate`

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_URL` and `STATIC_ROOT` in settings

### Port Already in Use
- Use a different port: `python manage.py runserver 8080`
- Or kill the process using port 8000

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, questions, or bug reports, please:
- Open an issue on GitHub
- Contact: [Your Email/Contact Info]

## Changelog

### Version 1.0.0
- Initial release
- User authentication system
- Expense management features
- Dashboard and analytics
- Category management
- Production-ready deployment configuration

## Roadmap

- [ ] Add expense charts and visualizations
- [ ] Implement budget tracking
- [ ] Add recurring expense support
- [ ] Mobile app development
- [ ] API endpoints for third-party integration
- [ ] Multi-language support
- [ ] Export expenses to CSV/PDF

## Author

**Manikanta**
- GitHub: [@manikanta2619](https://github.com/manikanta2619)

---

**Last Updated**: August 14, 2026

**Status**: ✅ Active & Maintained
