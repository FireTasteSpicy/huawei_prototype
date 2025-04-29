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

5. Build the static files:
```bash
python manage.py collectstatic
```

6. Create a environment file:
```bash
touch .env
```
With the following content:
```bash
# .env
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

8. Access the application at http://127.0.0.1:8000/



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
black .
```
- Use flake8 for linting suggestions.
```bash
flake8 .
```

# Docker Setup
## Prerequisites
- Docker installed on your system
- Docker Compose installed on your system
## Running with Docker
1. Build and run the Docker containers:
- Development
```bash
cd docker/development
docker-compose up --build
```
- Production
```bash
cd docker/production
docker-compose up --build
```
2. Access the application at http://localhost


## Docker Management
- To stop the containers:
```bash
docker-compose down
```

- To view logs:
```bash
docker-compose logs
```
- To run a command inside the web container:
```bash
docker-compose exec web bash

# To exit the container shell
# exit
```

- To test the application:
```bash
# Test development environment
bash docker/scripts/test_clean_install.sh development

# Test production environment
bash docker/scripts/test_clean_install.sh production
```

# Terraform
## Prerequisites
- Install Terraform on your system. You can do this by following the instructions on the [Terraform website](https://developer.hashicorp.com/terraform/install) or by using the following commands:
``` bash
# For Ubuntu/Debian-based systems
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify the installation
terraform version
```

## Setup
1. Initialize Terraform:
```bash
cd terraform
terraform init
```
Validate the configuration:
```bash
terraform validate
```
2. Plan the deployment:
```bash
terraform plan
```
3. Apply the configuration:
```bash
terraform apply
```

## Destroy the infrastructure
To destroy the infrastructure created by Terraform, run:
```bash
terraform destroy
```