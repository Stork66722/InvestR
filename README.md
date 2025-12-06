# 📈 InvestR - Stock Trading Simulation Platform

> **Arizona State University Capstone Project**  
> **Final Grade: A**

A full-stack Django web application enabling users to practice stock trading strategies without financial risk. Features real-time portfolio tracking, order confirmation workflows, and administrative market controls.

[![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.1-green?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

## 🌐 Live Demo

**🚀 Live Application:** https://investr-iklw.onrender.com

**Admin Dashboard:** https://investr-iklw.onrender.com/admin

**🟢 System Status:** [stats.uptimerobot.com/UuxJ2DiPIX](https://stats.uptimerobot.com/UuxJ2DiPIX)

*Note: Application stays warm 24/7 via UptimeRobot monitoring - no cold starts!*

---

## 🎓 Academic Project Information

**Team Members:**
- **Jorge Aguilar** 
- **Richard Lahaie** 
- **Summer Olson** 

**Course:** IFT 401 - Information Technology Capstone  
**Institution:** Arizona State University - Ira A. Fulton Schools of Engineering  
**Semester:** Fall 2024  
**Professor:** Michael Walsh  
**Final Grade:** A

**Original Repository:** [jraguil5/IFT401-FinalProject](https://github.com/jraguil5/IFT401-FinalProject)

---

## 🚀 Features

### 👤 Customer Functions
- ✅ **User Authentication** - Secure registration and login system with email validation
- ✅ **Buy Stocks** - Order confirmation modal with cancellation option before execution
- ✅ **Sell Stocks** - Review and confirm sale details with ability to cancel before finalizing
- ✅ **Real-time Portfolio** - Live tracking of holdings, market values, and account equity
- ✅ **Cash Management** - Deposit and withdraw virtual funds with balance validation
- ✅ **Transaction History** - Complete audit trail of all trades and cash movements

### 👨‍💼 Administrator Functions
- ✅ **Stock Management** - Create and manage securities with ticker symbols and company names
- ✅ **Market Hours Configuration** - Set trading schedules (open/close times, weekdays)
- ✅ **Price Generator** - Manual button to trigger price updates with random fluctuations

### ⚙️ System Features
- ✅ **Market Hours Validation** - Prevents trading outside configured hours (24/7 capable for demo)
- ✅ **Real-time Price Updates** - Dynamic stock pricing with daily high/low/opening price tracking
- ✅ **Database Integration** - Full referential integrity across all tables
- ✅ **Complete Order Workflow** - Order → Trade → Transaction pipeline with transactional consistency

---

## 🛠️ Technology Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6)
- Custom responsive design
- AJAX for dynamic updates
- Modal-based order confirmations

### Backend
- **Python 3.12**
- **Django 5.1** - Web framework
- **Django REST Framework** - API endpoints
- **Gunicorn** - WSGI HTTP server

### Database
- **PostgreSQL 16** - Production (Render)
- **MySQL 8.0** - Original deployment (AWS RDS)
- **SQLite** - Local development

### Deployment & DevOps
- **Render** - Free tier hosting (current)
- **AWS Elastic Beanstalk** - Original production deployment
- **AWS RDS** - Managed MySQL database
- **Git/GitHub** - Version control and collaboration
- **WhiteNoise** - Static file serving
- **UptimeRobot** - 24/7 uptime monitoring and status page

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.12 or higher
- pip and virtualenv
- PostgreSQL / MySQL / SQLite (development)
- Git

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/Stork66722/InvestR.git
cd InvestR

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment configuration
cp .env.example .env
# Edit .env with your database settings

# 5. Database setup
python manage.py migrate

# 6. Create superuser (admin account)
python manage.py createsuperuser

# 7. Create sample stock data (optional)
python manage.py shell
>>> from customer.models import Stock
>>> Stock.objects.create(
...     ticker='AAPL',
...     company_name='Apple Inc.',
...     current_price=189.41,
...     opening_price=189.00,
...     day_high=190.50,
...     day_low=188.00,
...     float_shares=1000000
... )
>>> exit()

# 8. Run development server
python manage.py runserver
```

**Access application:** http://localhost:8000

---

## 🎯 Key Achievements & Learning Outcomes

### Technical Implementation
✅ Implemented order confirmation workflow mirroring professional platforms (Robinhood, E*TRADE)  
✅ Built RESTful API endpoints for portfolio tracking and transaction management  
✅ Designed normalized MySQL/PostgreSQL database with full referential integrity  
✅ Deployed production environment on AWS Elastic Beanstalk with RDS  
✅ Migrated to Render with PostgreSQL for cost optimization  
✅ Created admin dashboard with comprehensive market control features  

### Agile Development Process
✅ Two-week sprint cycles with iterative feature development  
✅ Requirements validation at every development milestone  
✅ Post-deployment enhancement (added order confirmation after initial release)  
✅ Effective team collaboration via GitHub (90+ commits across 3 developers)  

### Critical Lessons Learned

**1. Requirements Traceability**
- Initially implemented instant trade execution
- Discovered missed requirement during final review: "User must have option to cancel order before execution"
- Solution: Added confirmation modals to both buy and sell workflows
- **Takeaway:** Always create requirements traceability matrix at project start; validate at every milestone

**2. Cloud Deployment Best Practices**
- Encountered AWS deployment failure due to virtual environment conflicts
- Root cause: Local `venv/` uploaded to AWS, conflicting with Elastic Beanstalk's environment
- Solution: Created `.ebignore` to exclude `venv/`, verified `requirements.txt` completeness
- **Takeaway:** Understand cloud platform expectations; never commit virtual environments to version control

**3. Version Control & Team Collaboration**
- GitHub enabled effective distributed development across 3 team members
- Branching strategy prevented conflicts during parallel feature development
- Code review process caught bugs before production deployment
- **Takeaway:** Proper Git workflow is essential for team projects

---

## 🔮 Future Enhancements

- [ ] Reset password function
- [ ] Integrate live market data via financial APIs (Alpha Vantage, IEX Cloud)
- [ ] Add advanced charting with technical indicators
- [ ] Implement automated price updates on scheduled intervals
- [ ] Create portfolio performance analytics and reporting dashboards
- [ ] Add email notifications for order confirmations and price alerts
- [ ] Build watchlist functionality for tracking favorite stocks
- [ ] Develop mobile-responsive design improvements
- [ ] Add social features for sharing trading strategies
- [ ] Implement machine learning-based price prediction models

---

## 📄 Project Documentation

- **Business Case:** Requirements specification and problem definition
- **Design Document:** System architecture and database schema
- **Build Deck:** Implementation details and final presentation

---

## 🙏 Acknowledgments

- **Professor Michael Walsh** - Course instructor and project advisor
- **Arizona State University** - Ira A. Fulton Schools of Engineering
- **Team Members** - Jorge Aguilar and Summer Olson for outstanding collaboration
- **AWS Academy** - Cloud computing resources and training

---

## 📧 Contact

**Richard Lahaie**
- GitHub: [@Stork66722](https://github.com/Stork66722)
- Repository: [InvestR](https://github.com/Stork66722/InvestR)
- LinkedIn: www.linkedin.com/in/richard-lahaie-332b5959
- Email: stork66722@gmail.com

---

## 📄 License

This project was created as an academic capstone and is available for educational and portfolio purposes.

---

*This repository is a copy maintained independently for portfolio purposes. Original collaborative project completed Fall 2025 with a final grade of A+.*
