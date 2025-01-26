from setuptools import setup, find_packages

setup(
    name="AI_Medical_FAQ_chatbot_NLP_2",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Core Dependencies
        "Flask==2.3.2",
        "flask-jwt-extended==4.4.4",
        "Flask-Cors==3.0.10",
        "Flask-Session==0.4.0",
        "Flask-Talisman==1.0.0",
        "Flask-Login==0.6.3",
        "python-dotenv==1.0.0",
        "bcrypt==4.0.1",
        "tensorflow==2.16.2",
        "nltk==3.9.0",
        "scikit-learn==1.3.1",
        "numpy==1.26.4",
        "pandas==2.1.1",
        "matplotlib==3.8.0",
        "mysql-connector-python==8.1.0",
        "cryptography==42.0.5",
        "pycryptodome==3.21.0",
        "setuptools==69.1.1",
        "wheel==0.42.0",
        "json5==0.9.6",
        "gunicorn==20.1.0",

        # Testing Frameworks
        "pytest==7.4.0",
        "pytest-cov==4.1.0",

        # End-to-End and Usability Testing
        "selenium==4.12.0",

        # Load Testing
        "locust==2.15.1",

        # Security Testing
        "python-owasp-zap-v2.4==0.0.14",
    ],
    python_requires=">=3.8",  # Specify the minimum Python version required
    include_package_data=True,  # Include non-Python files (e.g., templates, static files)
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "start-chatbot=loginRegister.app:main",  # Example entry point
        ],
    },
)