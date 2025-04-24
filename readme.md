# Installation
## Prerequisites
- Python 3.10+
- pip (Python package installer)

## Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd huawei_prototype
```

2. Create and activate a virtual environment:
``` bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run database migrations:
```bash
cd huawei_prototype
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/


# Development
## Testing
Run tests using:
```bash
python manage.py test
```

## Code Style
- Follow PEP 8 guidelines for Python code.
- Use black for code formatting.
```bash
pip install black
black .
```

- Use flake8 for linting.