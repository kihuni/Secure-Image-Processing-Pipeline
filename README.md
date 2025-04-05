# Secure Image Processing Pipeline


A secure image processing pipeline that detects labels in images using Clarifai, stores the results in pCloud, and manages sensitive configurations with Pulumi ESC. The project includes a user-friendly Flask web UI for uploading images and viewing results, deployed on PythonAnywhere for online access.
This project was built for the Pulumi Deploy and Document Challenge: Shhh, It's a Secret! hackathon, focusing on secure configuration management using Pulumi ESC.


## Table of Contents
- [Features](#features)

- [Project Structure](#project-structure)

- [Prerequisites](#prerequisites)

- [Setup](#setup)
    - Local Setup (#local-setup)

    - Pulumi ESC Configuration (#pulumi-esc-configuration)

- [Usage](#usage)
    - Running Locally (#running-locally)

    - Deploying on PythonAnywhere (#deploying-on-pythonanywhere)

- [Security Best Practices](#security-best-practices)

- [Troubleshooting](#troubleshooting)


### Features
- Image Processing: Uses Clarifai to detect labels in uploaded images (e.g., dog, pet, animal).

- Secure Storage: Stores results in pCloud with end-to-end encryption.

- Configuration Management: Manages API keys and credentials securely using Pulumi ESC.

- Web UI: A Flask-based interface for uploading images, viewing detected labels, and downloading results.

- Deployment: Hosted on PythonAnywhere for online access at https://yourusername.pythonanywhere.com.

Project Structure

```
Secure-Image-Processing-Pipeline/
├── app.py              # Flask app with UI and processing logic
├── requirements.txt    # Project dependencies
├── templates/          # HTML templates for the UI
│   ├── index.html      # Upload form
│   └── result.html     # Results page
├── uploads/            # Directory for uploaded images (created at runtime)
├── results/            # Directory for analysis_results.json (created at runtime)
└── .gitignore          # Excludes unnecessary files (venv/, uploads/, etc.)
```
### Prerequisites

- Python 3.10+: Ensure Python is installed on your system.

- Pulumi Account: Sign up at pulumi.com to use Pulumi ESC.

- Clarifai Account: Sign up at clarifai.com to get an API key (1,000 free operations/month).

- pCloud Account: Sign up at pcloud.com for free storage (10 GB, no card required).

- PythonAnywhere Account (for deployment): Sign up at [pythonanywhere.com](https://www.pythonanywhere.com/) for free hosting.

### Setup
**Local Setup**
Clone the Repository:
```
git clone https://github.com/your-username/secure-image-processing-pipeline.git
cd Secure-Image-Processing-Pipeline
```

Create a Virtual Environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
Install Dependencies:

```
pip install -r requirements.txt
```
This installs `flask, pulumi-esc-sdk, clarifai-grpc, and pcloud`.

Create Required Directories:
```
mkdir uploads results
```
### Pulumi ESC Configuration

Pulumi ESC is used to manage sensitive data securely. Set up your environment as follows:

Step 1: Install the Pulumi CLI (if not already installed):

Follow the instructions at [pulumi.com/docs/install/](http://pulumi.com/docs/install/).

Step 2: Generate a Pulumi Access Token:
- Log in to the Pulumi Console, go to your user settings, and create a new access token.

- Set the token as an environment variable:

```
export PULUMI_ACCESS_TOKEN="your-pulumi-access-token"
```

Step 3: Create a Pulumi ESC Environment:

```
esc env init my-org/my-project/image-processing-env
esc env set --secret my-org/my-project/image-processing-env clarifai:apiKey "your-clarifai-api-key"
esc env set --secret my-org/my-project/image-processing-env pcloud:username "your-pcloud-email"
esc env set --secret my-org/my-project/image-processing-env pcloud:password "your-pcloud-password"
esc env set my-org/my-project/image-processing-env pcloud:folderPath "/hackathon-results"

```
Step 4: Verify the Environment:

```
esc env get my-org/my-project/image-processing-env
```
### Usage

**Running Locally**

Start the Flask App:
```
python app.py
```
The app will run at http://localhost:5000.

Access the UI:
- Open http://localhost:5000 in your browser.

- Upload an image (PNG, JPG, JPEG, or GIF).

- View the detected labels, the uploaded image, and a link to the results file (analysis_results.json).

- The results are also uploaded to pCloud in the /hackathon-results folder.

### Deploying on PythonAnywhere

To make the app accessible online, deploy it to PythonAnywhere:

Sign Up for PythonAnywhere:
- Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com/).

Upload the Project:

- In the “Files” tab, create a directory: /home/yourusername/Secure-Image-Processing-Pipeline.

- Upload app.py, requirements.txt, and the templates/ directory.

- Create the uploads and results directories:

```
mkdir /home/yourusername/Secure-Image-Processing-Pipeline/uploads
mkdir /home/yourusername/Secure-Image-Processing-Pipeline/results
```

Set Up a Virtual Environment:

Open a Bash console and create a virtual environment:

```
mkvirtualenv --python=/usr/bin/python3.10 my-venv
cd /home/yourusername/Secure-Image-Processing-Pipeline
pip install -r requirements.txt
```

Configure the Web App:

- In the “Web” tab, add a new web app with manual configuration (Python 3.10).

- Set the source code path: /home/yourusername/Secure-Image-Processing-Pipeline.

- Set the virtualenv path: /home/yourusername/.virtualenvs/my-venv.

- Edit the WSGI file (/var/www/yourusername_pythonanywhere_com_wsgi.py):

```
import sys

path = '/home/yourusername/Secure-Image-Processing-Pipeline'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

Set the PULUMI_ACCESS_TOKEN environment variable in the “Environment Variables” section:
- Name: PULUMI_ACCESS_TOKEN

- Value: your-pulumi-access-token

Reload and Test:
- Click the “Reload” button in the “Web” tab.

- Visit https://yourusername.pythonanywhere.com to use the app online.

### Security Best Practices
- Use Pulumi ESC for Secrets: All sensitive data (Clarifai API key, pCloud credentials) is stored in Pulumi ESC, which encrypts secrets at rest and provides audit logs for transparency.

- Avoid Hardcoding Credentials: Never store API keys or passwords in the source code or environment variables directly.

- Leverage pCloud’s Encryption: pCloud provides end-to-end encryption for stored files, ensuring the security of your results.

- Restrict File Uploads: The app only allows image files (PNG, JPG, JPEG, GIF) to prevent malicious uploads.

- Monitor Access: Use Pulumi ESC’s audit logs to track who accesses your secrets and when.

### Troubleshooting
- Pulumi ESC 404 Error (Not Found: Environment 'my-org/my-project/image-processing-env' not found):
Verify the environment path with esc env ls.

- Ensure your PULUMI_ACCESS_TOKEN is set correctly and has access to the environment.

- Recreate the environment if needed (see Pulumi ESC Configuration (#pulumi-esc-configuration)).

ModuleNotFoundError:
- Ensure all dependencies are installed in your virtual environment (pip install -r requirements.txt).

Clarifai API Errors:
- Check your API key and usage limits (1,000 operations/month on the free tier).

pCloud Upload Issues:
- Verify your pCloud credentials and ensure the /hackathon-results folder exists in your pCloud account.

404 Error for Results File:
- Ensure the results directory exists and contains analysis_results.json.

- Check the Flask route (/results/<filename>) in app.py.

