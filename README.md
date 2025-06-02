# UniHub - All-in-One University Management System

![UniHub Logo](static/images/logo.png)

[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Hackathon](https://img.shields.io/badge/NEOFETCH-Inventious%204.1-orange.svg)](https://neofetch.tech)

## 🎓 Project Overview

UniHub is a comprehensive university management system developed for the **NEOFETCH Hackathon Inventious 4.1**. This all-in-one platform streamlines campus life by integrating academic management, communication, navigation, dining, transportation, and security features into a single, user-friendly application.

## 🌟 Key Features

### 📚 Academic Management
- **Course Management**: Complete course catalog with department-wise organization
- **Class Scheduling**: Interactive timetables and routine management
- **Assignment Tracking**: Due date management with automatic reminders
- **Grade Management**: Student performance tracking and analytics
- **Faculty Directory**: Comprehensive staff information and contact details

### 💬 Communication Platform
- **Real-time Chat**: Secure messaging between students and faculty
- **AI Chatbot**: Intelligent assistant for quick queries and support
- **Notifications System**: Customizable alerts for assignments, events, and announcements
- **Study Groups**: Collaborative learning spaces

### 🗺️ Campus Navigation
- **Interactive Maps**: Detailed building and room information
- **AR Wayfinding**: Augmented reality markers for easy navigation
- **Location Services**: Find nearby facilities and services
- **Room Booking**: Reserve study spaces and meeting rooms

### 🍽️ Cafeteria Management
- **Digital Menus**: Real-time menu updates with pricing
- **Online Ordering**: Pre-order meals to save time
- **Nutritional Information**: Dietary preferences and allergen alerts
- **Operating Hours**: Live status of dining facilities

### 🚌 Transportation System
- **Route Information**: Complete bus schedule and route details
- **Real-time Tracking**: Live bus locations and arrival times
- **Delay Notifications**: Automatic updates for schedule changes

### 🔒 Security & Safety
- **Incident Reporting**: Easy-to-use safety reporting system
- **Emergency Contacts**: Quick access to campus security
- **Report Tracking**: Monitor report status and responses

### 🎉 Events & Activities
- **Event Calendar**: Campus-wide event listings
- **Club Management**: Student organization information
- **RSVP System**: Event registration and attendance tracking
- **Personal Calendar**: Integrated schedule management

## 🛠️ Technology Stack

### Backend
- **Framework**: Django (Python)
- **Database**: SQLite3
- **Authentication**: Django's built-in auth system
- **Real-time Features**: WebSocket support for chat

### Frontend
- **Templates**: Django Templates with HTML5/CSS3
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Vanilla JS for interactive elements
- **Icons**: Unicode emojis and custom icons

### Additional Features
- **PDF Generation**: Automated routine and report generation
- **Image Handling**: Media file management
- **Responsive Design**: Mobile-first approach
- **Notification System**: Real-time alerts and reminders

## 📁 Project Structure

```
university_app/
├── academics/          # Academic management module
├── accounts/          # User authentication and profiles
├── cafeteria/         # Dining services management
├── chat/              # Real-time messaging system
├── chatbot/           # AI assistant integration
├── config/            # Django project configuration
├── events/            # Event and club management
├── navigation/        # Campus mapping and wayfinding
├── notifications/     # Alert and notification system
├── security/          # Safety and incident reporting
├── transportation/    # Bus and transport services
├── static/            # Static files (CSS, JS, images)
├── templates/         # HTML templates
├── media/             # User-uploaded media files
├── Neonomads/         # Team documentation and screenshots
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── db.sqlite3         # Database file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/university_app.git
   cd university_app
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**
   - Open your browser and navigate to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## 👥 User Roles & Permissions

### Students
- View personal dashboard with class schedules
- Access assignments and grades
- Use messaging and chat features
- Navigate campus using AR markers
- Order food from cafeteria
- Report safety incidents
- Join events and clubs

### Faculty
- Manage classes and assignments
- Grade student submissions
- Create and schedule exams
- Communicate with students
- Access faculty-specific resources

### Staff/Admin
- Manage system-wide settings
- Oversee all modules
- Generate reports and analytics
- Moderate content and users

## 📱 Key Screenshots

![Dashboard Overview](Neonomads/screenshot1.png)
*Student Dashboard - Centralized access to all university services*

![Navigation System](Neonomads/screenshot2.png)
*Campus Navigation - Interactive maps with AR wayfinding*

![Communication Platform](Neonomads/screenshot3.png)
*Real-time Chat - Secure messaging between students and faculty*

## 🎯 Problem Statement & Solution

### Problem
Universities face challenges in managing diverse student services across multiple platforms, leading to:
- Information fragmentation
- Poor communication channels
- Difficult campus navigation
- Inefficient resource management
- Safety concerns

### Solution
UniHub addresses these challenges by providing:
- **Centralized Platform**: All services in one application
- **Real-time Communication**: Instant messaging and notifications
- **Smart Navigation**: AR-powered wayfinding system
- **Efficient Management**: Streamlined academic and administrative processes
- **Enhanced Safety**: Integrated security reporting system

## 🏆 Hackathon Submission

**Event**: NEOFETCH Hackathon Inventious 4.1  
**Team**: Neonomads  
**Category**: All-in-One University Management System  
**Duration**: 48 hours  

### Judging Criteria Met
- ✅ **Innovation**: AR navigation and AI chatbot integration
- ✅ **Technical Implementation**: Full-stack Django application
- ✅ **User Experience**: Intuitive, responsive design
- ✅ **Problem Solving**: Addresses real university challenges
- ✅ **Scalability**: Modular architecture for easy expansion

## 🔮 Future Enhancements

### Short-term Goals
- Mobile application development (React Native/Flutter)
- Integration with existing university systems
- Advanced analytics and reporting
- Multi-language support

### Long-term Vision
- AI-powered academic advisor
- Blockchain-based credential verification
- IoT integration for smart campus features
- Machine learning for personalized recommendations

## 📄 API Documentation

### Authentication Endpoints
```
POST /accounts/login/          # User login
POST /accounts/register/       # User registration
POST /accounts/logout/         # User logout
```

### Academic Endpoints
```
GET  /academics/courses/       # List all courses
GET  /academics/assignments/   # List assignments
POST /academics/submit/        # Submit assignment
```

### Chat Endpoints
```
GET  /chat/rooms/             # List chat rooms
POST /chat/send/              # Send message
GET  /chat/history/           # Message history
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test academics
python manage.py test chat
```

## 🤝 Contributing

We welcome contributions from the community! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 coding standards
- Write comprehensive tests for new features
- Update documentation for any changes
- Use meaningful commit messages

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=your-email-host
EMAIL_PORT=587
```

### Settings
Key configuration files:
- `config/settings.py` - Main Django settings
- `config/urls.py` - URL routing
- `requirements.txt` - Python dependencies

## 📊 Performance & Monitoring

- **Database Optimization**: Efficient queries with select_related
- **Caching**: Redis caching for frequent data
- **Static Files**: Optimized CSS/JS delivery
- **Monitoring**: Built-in Django admin for system monitoring

## 🔒 Security Features

- **CSRF Protection**: Django's built-in CSRF middleware
- **SQL Injection Prevention**: ORM-based database queries
- **XSS Protection**: Template auto-escaping
- **Authentication**: Secure user authentication system

## 📧 Contact & Support

**Team Neonomads**
- **Lead Developer**: MD Jobayer Arafat
- **Project Repository**: [GitHub Repository](https://github.com/mdjobayerarafat/university_app)
- **Demo**: Available upon request

For support and inquiries:
- 📧 Email: support@unihub.edu
- 💬 Issues: [GitHub Issues](https://github.com/mdjobayerarafat/university_app/issues)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NEOFETCH Hackathon** organizers for the opportunity
- **Django Community** for excellent documentation
- **Open Source Contributors** whose libraries made this possible
- **University Partners** for testing and feedback

---

**Built with ❤️ by Team Neonomads for NEOFETCH Hackathon Inventious 4.1**

*Transforming university life, one feature at a time.*

### 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/mdjobayerarafat/university_app)
![GitHub forks](https://img.shields.io/github/forks/mdjobayerarafat/university_app)
![GitHub issues](https://img.shields.io/github/issues/mdjobayerarafat/university_app)
![GitHub last commit](https://img.shields.io/github/last-commit/mdjobayerarafat/university_app)