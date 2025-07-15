# Enjoy Kids 📱👦👧

**Enjoy Kids** is a Django-based SMS service platform developed for telecom clients, specifically tailored for child users. It enables children to stay connected with loved ones while maintaining parental control and simplicity.

## 📌 Project Purpose

This platform allows child users to:

- Send an SMS to the special number `555` with up to **5 phone numbers** they wish to connect with.
- Once registered, they are granted **unlimited calling** to those 5 selected numbers.
- Purchase **data packages** using specific keywords sent via SMS, deducted from their prepaid balance.

## ⚙️ Tech Stack

- **Backend**: Python 3, Django
- **APIs**: Django REST Framework (DRF)
- **Database**: SQLite (can be upgraded to MySQL/PostgreSQL)
- **Communication**: SMS gateway integration (via telecom infrastructure)

## 🚀 Installation

```bash
git clone https://github.com/batbyr-hub/enjoy_kids.git
cd enjoy_kids
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
