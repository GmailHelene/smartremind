# Smart Påminner Pro PWA

En moderne, progressiv web-app for smarte påminnelser med deling og e-post notifikasjoner.

## Funksjoner

- 📱 **PWA** - Installer som app på mobil/desktop
- 👥 **Deling** - Del påminnelser med andre brukere
- 📧 **E-post** - Automatiske e-post notifikasjoner
- 🔄 **Offline** - Fungerer uten internett
- 🔔 **Push notifications** - Få varsler på enheten din
- 🎨 **Responsiv** - Optimalisert for alle enheter

## Lokal utvikling

```bash
# Klon repository
git clone <repo-url>
cd smart_reminder_pwa

# Installer avhengigheter
pip install -r requirements.txt

# Kopier miljøvariabler
cp .env.example .env

# Rediger .env med dine innstillinger
# Spesielt e-post konfigurasjon

# Kjør app
python app.py
```

# Smart Reminder - Windows PC Version

This is a web-based version of SmartReminder that runs on Windows PC using Python and Flask.

## Features

- Create and manage reminders with titles, descriptions, and due dates
- Share reminders with other users via email
- Shared noteboard functionality for collaborative notes
- Different app modes (Default, ADHD-Friendly, Silent, Focus, Dark)
- Responsive design that works on desktops and mobile browsers

## Installation

1. Make sure you have Python 3.7+ installed on your computer
2. Open Command Prompt or PowerShell
3. Navigate to the project folder:
   ```
   cd c:\Users\helen\Desktop\SmartReminder-main
   ```
4. Create a virtual environment:
   ```
   python -m venv venv
   ```
5. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
6. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the App

1. Make sure your virtual environment is activated:
   ```
   venv\Scripts\activate
   ```
2. Start the application:
   ```
   python app.py
   ```
3. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## App Modes

- **Default**: Standard interface with all features enabled
- **ADHD-Friendly**: High contrast, simplified UI, visual cues, and reduced distractions
- **Silent Mode**: Disables sounds and intrusive notifications
- **Focus Mode**: Simplified interface that shows only essential information
- **Dark Mode**: Dark color scheme for low-light environments

## Sharing Features

- Share reminders with others by entering their email addresses
- Create and share notes on the collaborative noteboard
- Recipients don't need to be registered to receive shared items

## Technologies Used

- Backend: Python with Flask
- Database: SQLite (via SQLAlchemy)
- Frontend: HTML, CSS, JavaScript, Bootstrap 5