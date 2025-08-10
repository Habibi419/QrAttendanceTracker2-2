# QR Code Attendance System

## Overview

This is a Flask-based web application that provides a QR code attendance tracking system. The system allows administrators to generate QR codes for attendance sessions, and students can scan these codes to mark their attendance. The application features session management, attendance tracking, and a simple admin authentication system.

## System Architecture

The application follows a traditional Flask MVC architecture with the following key components:

- **Flask Web Framework**: Core web application framework
- **SQLAlchemy ORM**: Database abstraction layer for data management
- **Flask-WTF**: Form handling and validation
- **QR Code Generation**: Using the `qrcode` library for generating QR codes
- **Session-based Authentication**: Simple password-based admin authentication
- **Bootstrap Frontend**: Responsive UI with dark theme

## Key Components

### Backend Architecture
- **Flask Application (`app.py`)**: Main application entry point with route definitions
- **Database Models (`models.py`)**: SQLAlchemy models for Admin, Session, and Attendance entities
- **Forms (`forms.py`)**: WTForms for user input validation and form handling
- **Main Entry Point (`main.py`)**: Application runner for development

### Frontend Architecture
- **Jinja2 Templates**: Server-side rendered HTML templates
- **Bootstrap 5**: CSS framework with dark theme
- **Font Awesome**: Icon library for UI elements
- **Custom CSS/JS**: Additional styling and client-side functionality

### Database Schema
- **Admin**: User authentication table with username and password hash
- **Session**: Attendance sessions with name, token, expiration, and status
- **Attendance**: Individual attendance records linked to sessions

## Data Flow

1. **Admin Login**: Administrators authenticate using a simple password-based system
2. **Session Creation**: Admins create attendance sessions with configurable duration
3. **QR Code Generation**: System generates unique QR codes containing session tokens
4. **Student Attendance**: Students scan QR codes and fill out attendance forms
5. **Data Storage**: Attendance records are stored with session association and timestamps
6. **Reporting**: Admins can view all attendance records across sessions

## External Dependencies

### Python Packages
- `Flask`: Web framework
- `Flask-SQLAlchemy`: Database ORM
- `Flask-WTF`: Form handling
- `Flask-Login`: User session management (imported but not actively used)
- `qrcode`: QR code generation
- `werkzeug`: WSGI utilities and security helpers

### Frontend Dependencies
- Bootstrap 5 (CDN): UI framework
- Font Awesome 6 (CDN): Icons
- Custom CSS/JS: Application-specific styling and functionality

### Database
- **Development**: SQLite (default)
- **Production**: Configurable via `DATABASE_URL` environment variable
- **Note**: The application uses SQLAlchemy and could easily be configured to use PostgreSQL or other databases

## Deployment Strategy

The application is designed for deployment on platforms like Replit, with the following considerations:

### Configuration
- Environment variables for sensitive data (`SESSION_SECRET`, `ADMIN_PASSWORD`, `DATABASE_URL`)
- ProxyFix middleware for handling reverse proxy headers
- Database connection pooling for reliability

### Security Features
- Password hashing using Werkzeug security utilities
- Session-based authentication
- CSRF protection via Flask-WTF
- Input validation and sanitization

### Scalability Considerations
- Database connection pooling
- Session expiration to prevent unlimited active sessions
- IP address logging for attendance tracking

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- July 07, 2025. Initial setup