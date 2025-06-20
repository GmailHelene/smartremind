from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    DateField, TimeField, SelectField
)
from wtforms.validators import DataRequired, Email, Length
import json
import os
import uuid
import logging
import sqlite3
import random
import string
from flask_mail import Message, Mail
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
import psutil  # For memory usage tracking
import re  # For email validation

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create Flask app
app = Flask(__name__)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Set up configurations
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-smartreminder'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    NOTIFICATION_ADVANCE_MINUTES = int(os.environ.get('NOTIFICATION_ADVANCE_MINUTES', 30))

# Apply configuration
app.config.from_object(Config)

# Initialize extensions
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vennligst logg inn for å få tilgang til denne siden.'
login_manager.login_message_category = 'info'

# Ensure secret key is set directly
if not app.secret_key:
    app.secret_key = app.config['SECRET_KEY']


# Update the get_db_connection function with better error handling
def get_db_connection():
    """Get a SQLite database connection with proper error handling"""
    try:
        conn = sqlite3.connect('smartreminder.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def return_db_connection(conn):
    try:
        if conn:
            conn.close()
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

# Data manager for fallback to JSON
class DataManager:
    def load_data(self, data_type):
        try:
            with open(f'data/{data_type}.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            if data_type == 'users':
                return {}
            return []
            
    def save_data(self, data_type, data):
        try:
            os.makedirs('data', exist_ok=True)
            with open(f'data/{data_type}.json', 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False

dm = DataManager()

# Initialize database
def init_db():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            # Create users table if it doesn't exist
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            cur.close()
            logger.info("Database tables initialized!")
            return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False
    finally:
        if conn:
            return_db_connection(conn)

# Initialize database on startup
init_db()

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# WTForms
class LoginForm(FlaskForm):
    username = StringField('Brukernavn/E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired()])
    submit = SubmitField('Logg inn')

class RegisterForm(FlaskForm):
    username = StringField('Brukernavn/E-post', validators=[DataRequired(), Email()])
    password = PasswordField('Passord', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrer deg')

class ReminderForm(FlaskForm):
    title = StringField('Tittel', validators=[DataRequired()])
    description = TextAreaField('Beskrivelse')
    date = DateField('Dato', validators=[DataRequired()], default=datetime.now().date())
    time = TimeField('Tid', validators=[DataRequired()], default=datetime.now().time())
    priority = SelectField('Prioritet', choices=[('Lav', 'Lav'), ('Medium', 'Medium'), ('Høy', 'Høy')])
    category = SelectField('Kategori', choices=[
        ('Jobb', 'Jobb'), ('Privat', 'Privat'), ('Helse', 'Helse'), 
        ('Familie', 'Familie'), ('Annet', 'Annet')
    ])
    share_with = StringField('Del med (e-post, bruk komma for flere)')
    submit = SubmitField('Opprett påminnelse')

class NoteForm(FlaskForm):
    title = StringField('Tittel', validators=[DataRequired()])
    content = TextAreaField('Notat', validators=[DataRequired()])
    share_with = StringField('Del med (e-post)')
    submit = SubmitField('Lagre notat')

class SettingsForm(FlaskForm):
    app_mode = SelectField('Appmodus', choices=[
        ('DEFAULT', 'Standard'), 
        ('ADHD_FRIENDLY', 'ADHD-Vennlig'), 
        ('SILENT', 'Stillemodus'), 
        ('FOCUS', 'Fokusmodus'), 
        ('DARK', 'Mørk modus')
    ])
    submit = SubmitField('Lagre innstillinger')

# User Class
class User(UserMixin):
    def __init__(self, user_id, username, email, password_hash=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._app_mode = "DEFAULT"
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get(user_id):
        # Try database first
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT id, username, email, password_hash, app_mode FROM users WHERE id = ?', (user_id,))
                user = cur.fetchone()
                cur.close()
                
                if user:
                    u = User(user[0], user[1], user[2], user[3])
                    u._app_mode = user[4] if user[4] else "DEFAULT"
                    return u
            except Exception as e:
                logger.error(f"Database error in User.get: {e}")
            finally:
                return_db_connection(conn)
        
        # Fallback to JSON
        users = dm.load_data('users')
        if user_id in users:
            user_data = users[user_id]
            u = User(user_id, user_data['username'], user_data['email'], user_data.get('password_hash'))
            u._app_mode = user_data.get('app_mode', "DEFAULT")
            return u
        return None
    
    @staticmethod
    def get_by_email(email):
        # Try database first
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute('SELECT id, username, email, password_hash, app_mode FROM users WHERE email = ?', (email,))
                user = cur.fetchone()
                cur.close()
                
                if user:
                    u = User(user[0], user[1], user[2], user[3])
                    u._app_mode = user[4] if user[4] else "DEFAULT"
                    return u
            except Exception as e:
                logger.error(f"Database error in User.get_by_email: {e}")
            finally:
                return_db_connection(conn)
        
        # Fallback to JSON
        users = dm.load_data('users')
        for user_id, user_data in users.items():
            if user_data.get('email') == email:
                u = User(
                    user_id, 
                    user_data.get('username', email), 
                    email, 
                    user_data.get('password_hash')
                )
                u._app_mode = user_data.get('app_mode', "DEFAULT")
                return u
        return None

    def save(self):
        """Save user to database and JSON"""
        # Save to database if available
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    'INSERT INTO users (id, username, email, password_hash, app_mode) VALUES (?, ?, ?, ?, ?) ON CONFLICT (email) DO NOTHING',
                    (self.id, self.username, self.email, self.password_hash, self._app_mode)
                )
                conn.commit()
                cur.close()
                logger.info(f"User {self.email} saved to database")
                return True
            except Exception as e:
                logger.error(f"Database error saving user: {e}")
            finally: 
                return_db_connection(conn)
        
        # Always save to JSON as backup
        users = dm.load_data('users')
        users[self.id] = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'app_mode': self._app_mode,
            'created': datetime.now().isoformat()
        }
        dm.save_data('users', users)
        logger.info(f"User {self.email} saved to JSON")
        return True

    @property
    def app_mode(self):
        return self._app_mode
    
    @app_mode.setter
    def app_mode(self, mode):
        # Prøv database først
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute('UPDATE users SET app_mode = ? WHERE id = ?', (mode, self.id))
                conn.commit()
                cur.close()
                self._app_mode = mode
                return
            except Exception as e:
                logger.error(f"Database error setting app_mode: {e}")
            finally:
                return_db_connection(conn)
        
        # Fallback til JSON
        try:
            users = dm.load_data('users')
            if self.id in users:
                users[self.id]['app_mode'] = mode
                dm.save_data('users', users)
            self._app_mode = mode
        except Exception as e:
            logger.error(f"JSON error setting app_mode: {e}")

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Email functions
def send_email(to, subject, template=None, html_content=None, **kwargs):
    """Send email with template or direct HTML"""
    try:
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            logger.warning(f"Email not sent: Missing MAIL_USERNAME or MAIL_PASSWORD")
            return False
        
        # Email validation
        if not to or (isinstance(to, str) and '@' not in to) or (isinstance(to, list) and not all('@' in recipient for recipient in to)):
            logger.warning(f"Invalid email address: {to}")
            return False
            
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            sender=app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME']
        )
        
        if template:
            msg.html = render_template(template, **kwargs)
        elif html_content:
            msg.html = html_content
        else:
            logger.error("Email missing both template and HTML content")
            return False
              # Send the email
        mail.send(msg)
        logger.info(f"Email sent to {to}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {to}: {e}")
        return False

def check_reminders_for_notifications():
    """Check reminders and send notifications with memory logging"""
    with app.app_context():
        try:
            # Log memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            logger.info(f"Memory usage before reminder check: {memory_mb:.2f} MB")
            
            now = datetime.now()
            notification_time = now + timedelta(minutes=app.config['NOTIFICATION_ADVANCE_MINUTES'])
            
            reminders = dm.load_data('reminders')
            shared_reminders = dm.load_data('shared_reminders')
            notifications = dm.load_data('notifications')
            
            sent_notifications = {n['reminder_id'] for n in notifications}
            all_reminders = []
            
            # Process reminders
            for reminder in reminders:
                if not reminder['completed'] and reminder['id'] not in sent_notifications:
                    try:
                        reminder_dt = datetime.fromisoformat(reminder['datetime'].replace(' ', 'T'))
                        if now <= reminder_dt <= notification_time:
                            if reminder['user_id'] and '@' in reminder['user_id']:
                                all_reminders.append((reminder, reminder['user_id']))
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Invalid reminder datetime: {e}")
            
            # Process shared reminders
            for reminder in shared_reminders:
                if not reminder['completed'] and reminder['id'] not in sent_notifications:
                    try:
                        reminder_dt = datetime.fromisoformat(reminder['datetime'].replace(' ', 'T'))
                        if now <= reminder_dt <= notification_time:
                            if reminder['shared_with'] and '@' in reminder['shared_with']:
                                all_reminders.append((reminder, reminder['shared_with']))
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Invalid shared reminder datetime: {e}")
            
            # Send notifications (limit to 5 per run to prevent memory issues)
            sent_count = 0
            for reminder, recipient_email in all_reminders[:5]:
                subject = f"🔔 Påminnelse: {reminder['title']}"
                html_content = f"""
                <h2>Påminnelse: {reminder['title']}</h2>
                <p>Dette er en påminnelse om at du har en oppgave som snart forfaller.</p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <h3>{reminder['title']}</h3>
                    <p><strong>Beskrivelse:</strong> {reminder.get('description', 'Ingen beskrivelse')}</p>
                    <p><strong>Tid:</strong> {reminder['datetime']}</p>
                    <p><strong>Prioritet:</strong> {reminder['priority']}</p>
                </div>
                """
                
                success = send_email(
                    to=recipient_email,
                    subject=subject,
                    html_content=html_content
                )
                
                if success:
                    notifications.append({
                        'reminder_id': reminder['id'],
                        'recipient': recipient_email,
                        'sent_at': now.isoformat(),
                        'type': 'reminder_notification'
                    })
                    sent_count += 1
            
            # Save updated notifications
            if sent_count > 0:
                dm.save_data('notifications', notifications)
                logger.info(f"Sent {sent_count} reminder notifications")
            
            # Log memory usage after
            memory_mb_after = process.memory_info().rss / 1024 / 1024
            logger.info(f"Memory usage after reminder check: {memory_mb_after:.2f} MB")
            
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")

# Initialize scheduler with reduced frequency
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=check_reminders_for_notifications,
    trigger="interval",
    minutes=15,  # Reduced from 5 to 15 minutes
    id='check_reminders_for_notifications'
)
scheduler.start()

# Helper functions
# Fix the empty exception blocks in get_user_profile
def get_user_profile(user_id):
    """Get user profile or create default"""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database when getting user profile")
        return {
            'id': None,
            'user_id': user_id,
            'profile_type': 'standard',
            'preferences': {},
            'accessibility_settings': {}
        }
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, profile_type, preferences, accessibility_settings
            FROM user_profiles WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            profile = {
                'id': row[0],
                'user_id': row[1],
                'profile_type': row[2],
                'preferences': json.loads(row[3]) if row[3] else {},
                'accessibility_settings': json.loads(row[4]) if row[4] else {}
            }
        else:
            # Create default profile if not found
            cursor.execute("""
                INSERT INTO user_profiles (user_id, profile_type, preferences, accessibility_settings)
                VALUES (?, ?, ?, ?)
            """, (user_id, 'standard', json.dumps({}), json.dumps({})))
            conn.commit()
            profile = {
                'id': cursor.lastrowid,
                'user_id': user_id,
                'profile_type': 'standard',
                'preferences': {},
                'accessibility_settings': {}
            }
        return profile
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return {
            'id': None,
            'user_id': user_id,
            'profile_type': 'standard',
            'preferences': {},
            'accessibility_settings': {}
        }
    finally:
        if 'cursor' in locals():
            cursor.close()
        return_db_connection(conn)

def get_user_reminders(user_id):
    """Get user's reminders"""
    # Try database first
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, due_date, category, priority, completed
                FROM reminders WHERE user_id = ?
                ORDER BY due_date ASC
            """, (user_id,))
            
            reminders = cursor.fetchall()
            cursor.close()
            return [{'id': r[0], 'title': r[1], 'description': r[2], 
                    'datetime': r[3], 'category': r[4], 'priority': r[5], 
                    'completed': r[6]} for r in reminders]
        except Exception as e:
            logger.error(f"Error getting user reminders: {e}")
        finally:
            return_db_connection(conn)
    
    # Fallback to JSON
    reminders = dm.load_data('reminders')
    user_email = User.get(user_id).email if User.get(user_id) else None
    return [r for r in reminders if r.get('user_id') == user_email]

def get_shared_reminders(user_id):
    """Get reminders shared with user"""
    shared_reminders = dm.load_data('shared_reminders')
    user_email = User.get(user_id).email if User.get(user_id) else None
    return [r for r in shared_reminders if r.get('shared_with') == user_email]

def calculate_user_stats(user_id):
    """Calculate user statistics"""
    conn = get_db_connection()
    if not conn:
        return {
            'total': 0, 'completed': 0, 'shared_count': 0, 'completion_rate': 0,
            'completed_today': 0, 'sessions_today': 0, 'total_time_today': 0, 'streak_days': 0
        }
    
    try:
        cursor = conn.cursor()
        
        # Total reminders
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()[0]
        
        # Completed reminders
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE user_id = ? AND completed = TRUE", (user_id,))
        completed = cursor.fetchone()[0]
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        cursor.close()
        return {
            'total': total,
            'completed': completed,
            'shared_count': 0,
            'completion_rate': completion_rate,
            'completed_today': 0,
            'sessions_today': 0,
            'total_time_today': 0,
            'streak_days': 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return {
            'total': 0, 'completed': 0, 'shared_count': 0, 'completion_rate': 0,
            'completed_today': 0, 'sessions_today': 0, 'total_time_today': 0, 'streak_days': 0
        }
    finally:
        return_db_connection(conn)

def get_user_notes(user_id, limit=None):
    """Get user's notes"""
    notes = dm.load_data('shared_notes')
    user_email = User.get(user_id).email if User.get(user_id) else None
    user_notes = [n for n in notes if n.get('user_id') == user_email]
    return user_notes[:limit] if limit else user_notes

def get_shared_notes(user_id, limit=None):
    """Get notes shared with user"""
    notes = dm.load_data('shared_notes')
    user_email = User.get(user_id).email if User.get(user_id) else None
    shared_notes = [n for n in notes if user_email in n.get('shared_with', [])]
    return shared_notes[:limit] if limit else shared_notes

def get_focus_stats(user_id):
    """Get focus session statistics"""
    return {'sessions_today': 0, 'total_time_today': 0}

def get_available_users(user_id):
    """Get available users for sharing"""
    users = dm.load_data('users')
    current_user_email = User.get(user_id).email if User.get(user_id) else None
    
    # Don't include the current user in the list
    available_users = []
    for user_id, user_data in users.items():
        if user_data.get('email') != current_user_email:
            available_users.append({
                'id': user_id,
                'email': user_data.get('email'),
                'username': user_data.get('username', user_data.get('email').split('@')[0])
            })
    
    return available_users

try:
    # Import APScheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    import psutil  # For memory usage tracking

    # Initialize scheduler with reduced frequency
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=check_reminders_for_notifications,
        trigger="interval",
        minutes=15,  # Reduced from 5 to 15 minutes
        id='check_reminders_for_notifications'
    )
    scheduler.start()
except ImportError as e:
    logger.warning(f"Scheduler dependencies not installed: {e}")
    scheduler = None


def get_dashboard_config(profile):
    """Get dashboard configuration based on profile"""
    profile_type = profile.get('profile_type', 'standard')
    
    # Default configuration
    config = {
        'show_stats': True,
        'show_calendar': True,
        'show_reminders': True,
        'show_notes': True,
        'show_focus': True,
        'layout': 'standard'
    }
    
    # Customize based on profile type
    if profile_type == 'adhd':
        config.update({
            'show_stats': False,  # Simplify UI
            'layout': 'focused',
            'reduced_animations': True,
            'high_contrast': True
        })
    elif profile_type == 'minimal':
        config.update({
            'show_stats': False,
            'show_calendar': False,
            'show_notes': False,
            'show_focus': False,
            'layout': 'minimal'
        })
    
    # Apply any custom preferences from profile
    preferences = profile.get('preferences', {})
    if preferences:
        config.update(preferences)
    
    return config

def award_points(user_id, action, value=1):
    """Award points for various actions"""
    points_map = {
        'focus_session_completed': value * 2,
        'reminder_completed': 5,
        'daily_streak': 20,
        'weekly_goal': 50
    }
    
    points = points_map.get(action, 0)
    
    conn = get_db_connection()
    if not conn:
        return points
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_statistics (user_id, date, points)
            VALUES (?, CURRENT_DATE, ?)
            ON CONFLICT (user_id, date) 
            DO UPDATE SET points = COALESCE(user_statistics.points, 0) + ?
        """, (user_id, points, points))
        
        conn.commit()
        cursor.close()
    except Exception as e:
        logger.error(f"Error awarding points: {e}")
    finally:
        return_db_connection(conn)    
    return points

# Routes for static files
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('icons/favicon.ico')

@app.route('/sw.js')
def service_worker():
    return app.send_static_file('js/sw.js')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/offline')
def offline():
    """Offline page"""
    return render_template('offline.html')

# Routes
@app.route('/')
def index():
    # Create a simple form for CSRF protection
    form = FlaskForm()
    return render_template('index.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    try:
        if form.validate_on_submit():
            user = User.get_by_email(form.username.data)
            
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                # Validate the next parameter to prevent open redirect vulnerabilities
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                flash('Velkommen tilbake!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Ugyldig e-post eller passord', 'danger')
    except Exception as e:
        logger.error(f"Login error: {e}")
        flash('En feil oppstod. Vennligst prøv igjen.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            logger.info("Starting user registration process")
            
            # Valider e-post
            email = form.username.data.lower().strip()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                logger.warning(f"Invalid email format: {email}")
                flash('Vennligst oppgi en gyldig e-postadresse.', 'error')
                return render_template('register.html', form=form)
            
            # Sjekk om bruker eksisterer
            existing_user = User.get_by_email(email)
            if existing_user:
                logger.warning(f"Registration attempted with existing email: {email}")
                flash('Denne e-postadressen er allerede registrert. Vennligst logg inn eller bruk glemt passord.', 'error')
                return render_template('register.html', form=form)
            
            # Valider passord
            password = form.password.data
            if len(password) < 8:
                logger.warning("Password too short during registration")
                flash('Passordet må være minst 8 tegn langt.', 'error')
                return render_template('register.html', form=form)
            
            # Opprett bruker
            user_id = str(uuid.uuid4())
            password_hash = generate_password_hash(password)
            username = email.split('@')[0]  # Bruk delen før @ som brukernavn
            logger.info(f"Creating new user with email: {email}")
            
            # Opprett bruker i database
            user = User(user_id, username, email, password_hash)
            
            # Sett standardverdier
            user._app_mode = 'DEFAULT'  # Bruk protected attribute direkte her
            
            if not user.save():
                logger.error("Failed to save user to database")
                flash('Beklager, kunne ikke opprette brukeren. Prøv igjen senere.', 'error')
                return render_template('register.html', form=form)            # Initialiser brukerprofil
            try:
                logger.info(f"Initializing user profile for {email}")
                init_user_profile(user_id)
            except Exception as e:
                logger.error(f"Kunne ikke opprette brukerprofil for {email}: {e}")
                # Fortsett selv om profil-initialisering feiler
                flash('Merk: Noen innstillinger måtte settes til standard. Du kan endre disse senere.', 'info')

            # Send velkomst-e-post
            logger.info(f"Attempting to send welcome email to {email}")
            welcome_sent = False
            try:
                welcome_sent = send_email(
                    to=email,
                    subject="Velkommen til Smart Påminner Pro!",
                    template='emails/welcome.html',
                    user={'username': username}
                )
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")
                # Fortsett selv om e-post feiler

            # Logg inn brukeren automatisk
            login_user(user)
            flash('Registrering vellykket! Velkommen til SmartReminder!', 'success')
            if not welcome_sent:
                flash('Merk: Kunne ikke sende velkomst-e-post. Sjekk spam-mappen eller kontakt support.', 'warning')
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            logger.error(f"Registreringsfeil: {e}")
            flash('Beklager, en feil oppstod under registrering. Vennligst prøv igjen.', 'error')
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)

def init_user_profile(user_id):
    """Initialiser brukerprofil med standardinnstillinger"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_profiles (user_id, profile_type, preferences)
                VALUES (?, 'standard', '{"notifications": true, "daily_goal": 5}')
            """, (user_id,))
            conn.commit()
            cur.close()
        except Exception as e:
            logger.error(f"Database error initializing user profile: {e}")
            raise
        finally:
            return_db_connection(conn)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du er nå logget ut.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user profile
    profile = get_user_profile(current_user.id)
    
    # Get reminders
    my_reminders = get_user_reminders(current_user.id)
    shared_reminders = get_shared_reminders(current_user.id)
    
    # Get notes
    my_notes = get_user_notes(current_user.id, limit=3)
    shared_notes = get_shared_notes(current_user.id, limit=3)
    
    # Calculate statistics
    stats = calculate_user_stats(current_user.id)
    
    # Create form
    form = ReminderForm()
    
    return render_template('dashboard.html', 
                         form=form, 
                         my_reminders=my_reminders,
                         shared_reminders=shared_reminders,
                         stats=stats,
                         current_time=datetime.now(),
                         profile=profile,
                         my_notes=my_notes,
                         shared_notes=shared_notes,
                         app_mode=current_user.app_mode)

@app.route('/add_reminder', methods=['POST'])
@login_required
def add_reminder():
    form = ReminderForm()
    
    if form.validate_on_submit():
        # Process share_with field to get a list of email addresses
        share_with = []
        if form.share_with.data:
            share_with = [email.strip() for email in form.share_with.data.split(',') if '@' in email]
        
        reminder_id = str(uuid.uuid4())
        new_reminder = {
            'id': reminder_id,
            'user_id': current_user.email,
            'title': form.title.data,
            'description': form.description.data,
            'datetime': f"{form.date.data} {form.time.data}",
            'priority': form.priority.data,
            'category': form.category.data,
            'completed': False,
            'created': datetime.now().isoformat(),
            'shared_with': share_with
        }
        
        reminders = dm.load_data('reminders')
        reminders.append(new_reminder)
        dm.save_data('reminders', reminders)
        
        if share_with:
            shared_reminders = dm.load_data('shared_reminders')
            
            for recipient in share_with:
                shared_reminder = {
                    'id': str(uuid.uuid4()),
                    'original_id': reminder_id,
                    'shared_by': current_user.email,
                    'shared_with': recipient,
                    'title': form.title.data,
                    'description': form.description.data,
                    'datetime': f"{form.date.data} {form.time.data}",
                    'priority': form.priority.data,
                    'category': form.category.data,
                    'completed': False,
                    'created': datetime.now().isoformat(),
                    'is_shared': True
                }
                shared_reminders.append(shared_reminder)
                
                # Send email notification to the recipient regardless of whether they're a registered user
                try:
                    msg = Message(
                        f"Delt påminnelse: {form.title.data}",
                        recipients=[recipient]
                    )
                    msg.html = render_template(
                        'emails/shared_reminder.html',
                        reminder=shared_reminder,
                        sender=current_user.email
                    )
                    mail.send(msg)
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
            
            dm.save_data('shared_reminders', shared_reminders)
            flash(f'Påminnelse "{form.title.data}" opprettet og delt med {len(share_with)} personer!', 'success')
        else:
            flash(f'Påminnelse "{form.title.data}" opprettet!', 'success')
    else:
        flash('Feil i skjema. Sjekk alle felt.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/complete_reminder/<reminder_id>')
@login_required
def complete_reminder(reminder_id):
    # Check my reminders
    reminders = dm.load_data('reminders')
    for reminder in reminders:
        if reminder['id'] == reminder_id and reminder['user_id'] == current_user.email:
            reminder['completed'] = True
            reminder['completed_at'] = datetime.now().isoformat()
            dm.save_data('reminders', reminders)
            flash('Påminnelse fullført!', 'success')
            return redirect(url_for('dashboard'))
    
    # Check shared reminders
    shared_reminders = dm.load_data('shared_reminders')
    for reminder in shared_reminders:
        if reminder['id'] == reminder_id and reminder['shared_with'] == current_user.email:
            reminder['completed'] = True
            reminder['completed_at'] = datetime.now().isoformat()
            dm.save_data('shared_reminders', shared_reminders)
            flash('Delt påminnelse fullført!', 'success')
            return redirect(url_for('dashboard'))
    
    flash('Påminnelse ikke funnet!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_reminder/<reminder_id>')
@login_required
def delete_reminder(reminder_id):
    reminders = dm.load_data('reminders')
    original_count = len(reminders)
    
    reminders = [r for r in reminders if not (r['id'] == reminder_id and r['user_id'] == current_user.email)]
    
    if len(reminders) < original_count:
        dm.save_data('reminders', reminders)
        flash('Påminnelse slettet!', 'success')
    else:
        flash('Påminnelse ikke funnet eller tilhører ikke deg!', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/notes')
@login_required
def notes():
    notes = dm.load_data('shared_notes')
    my_notes = [n for n in notes if n.get('user_id') == current_user.email]
    shared_with_me = [n for n in notes if current_user.email in n.get('shared_with', [])]
    
    form = NoteForm()
    
    return render_template('notes.html', 
                          form=form,
                          my_notes=my_notes,
                          shared_notes=shared_with_me)

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    form = NoteForm()
    
    if form.validate_on_submit():
        share_with = []
        if form.share_with.data:
            share_with = [email.strip() for email in form.share_with.data.split(',')]
        
        note_id = str(uuid.uuid4())
        new_note = {
            'id': note_id,
            'user_id': current_user.email,
            'title': form.title.data,
            'content': form.content.data,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'shared_with': share_with
        }
        
        notes = dm.load_data('shared_notes')
        notes.append(new_note)
        dm.save_data('shared_notes', notes)
        
        flash('Notat opprettet!', 'success')
    
    return redirect(url_for('notes'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    
    if form.validate_on_submit():
        app_mode = form.app_mode.data
        current_user.app_mode = app_mode
        # In a real application, save this to the database
        flash('Innstillinger oppdatert!', 'success')
        return redirect(url_for('settings'))
    
    # Pre-fill the form with the current user's settings
    form.app_mode.data = current_user.app_mode
    
    return render_template('settings.html', form=form)

@app.route('/profile-setup')
@login_required
def profile_setup():
    """Show profile selection for new users"""
    return render_template('profile_setup.html')

@app.route('/profile-setup', methods=['POST'])
@login_required
def profile_setup_post():
    """Handle profile selection"""
    profile_type = request.form.get('profile_type')
    accessibility_needs = request.form.getlist('accessibility')
    
    flash(f'Profil konfigurert som {profile_type}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/focus-mode')
@login_required
def focus_mode():
    """Focus mode for ADHD/students"""
    profile = get_user_profile(current_user.id)
    return render_template('focus_mode.html', profile=profile)

@app.route('/start-focus-session', methods=['POST'])
@login_required
def start_focus_session():
    """Start a focus session"""
    session_type = request.form.get('session_type', 'pomodoro')
    duration = int(request.form.get('duration', 25))
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO focus_sessions (user_id, session_type, duration_minutes, started_at)
            VALUES (?, ?, ?, ?) RETURNING id
        """, (current_user.id, session_type, duration, datetime.now()))
        
        session_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        return jsonify({'session_id': session_id, 'duration': duration})
    except Exception as e:
        logger.error(f"Error starting focus session: {e}")
        return jsonify({'error': 'Failed to start session'}), 500
    finally:
        return_db_connection(conn)
        
@app.route('/focus')
@login_required
def focus_session():
    return render_template('focus_session.html')  # Fixed template name
    
@app.route('/focus-session/stop/<int:session_id>', methods=['POST'])
@login_required
def stop_focus_session(session_id):
    notes = request.form.get('notes', '')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE focus_sessions 
            SET notes = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (notes, session_id, current_user.id))
        
        conn.commit()
        cursor.close()
        
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.error(f"Error stopping focus session: {e}")
        return jsonify({'error': 'Failed to stop session'}), 500
    finally:
        return_db_connection(conn)

@app.route('/focus-session/complete/<int:session_id>', methods=['POST'])
@login_required
def complete_focus_session(session_id):
    notes = request.form.get('notes', '')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Mark session as completed
        cursor.execute("""
            UPDATE focus_sessions 
            SET completed = TRUE, notes = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (notes, session_id, current_user.id))
        
        # Get session duration
        cursor.execute("""
            SELECT duration_minutes FROM focus_sessions 
            WHERE id = ? AND user_id = ?
        """, (session_id, current_user.id))
        
        duration = cursor.fetchone()[0]
        
        # Award points
        points_earned = award_points(current_user.id, 'focus_session_completed', duration)
        
        conn.commit()
        cursor.close()
        
        return jsonify({'status': 'completed', 'points_earned': points_earned})
    except Exception as e:
        logger.error(f"Error completing focus session: {e}")
        return jsonify({'error': 'Failed to complete session'}), 500
    finally:
        return_db_connection(conn)

@app.route('/gentle-mode')
@login_required
def gentle_mode():
    """Gentle reminder mode"""
    profile = get_user_profile(current_user.id)
    
    # Get only important, non-stressful reminders
    my_reminders = get_user_reminders(current_user.id)
    gentle_reminders = [r for r in my_reminders if not r['completed']][:3]
    
    return render_template('gentle_mode.html', 
                         profile=profile,
                         reminders=gentle_reminders)

@app.route('/test-email')
def test_email():
    if current_user.is_authenticated:
        recipient = current_user.email
    else:
        recipient = request.args.get('email')
        
    if not recipient:
        return "Mangler e-postadresse", 400
        
    success = send_email(
        to=recipient,        subject="Test fra Smart Påminner Pro",
        html_content=f"<h2>Test e-post</h2><p>Hei {current_user.username if current_user.is_authenticated else 'Test'}!</p><p>Dette er en test e-post fra Smart Påminner Pro.</p>"
    )
    
    return f"E-post {'sendt' if success else 'FEILET'} til {recipient}"

@app.route('/admin/setup-db')
def setup_database():
    """Setup database endpoint"""
    success = init_db()
    return jsonify({
        'status': 'success' if success else 'failed',
        'message': 'Database initialized' if success else 'Database initialization failed'
    })

@app.route('/shared-notes')
@login_required
def shared_notes():
    # Get shared notes from JSON since DB is not available
    notes = dm.load_data('shared_notes')
    user_notes = [n for n in notes if n.get('user_id') == current_user.email]
    shared_with_me = [n for n in notes if current_user.email in n.get('shared_with', [])]
    all_notes = user_notes + shared_with_me
    
    return render_template('shared_notes.html', notes=all_notes)

@app.route('/shared-notes/create', methods=['GET', 'POST'])
def create_shared_note():
    form = FlaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        title = request.form.get('title')
        content = request.form.get('content', '')
        if not title:
            flash('Tittel er påkrevd', 'danger')
            return redirect(url_for('create_shared_note'))
        
        # Generate random access code
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        note_id = str(uuid.uuid4())
        new_note = {
            'id': note_id,
            'title': title,
            'content': content,
            'user_id': current_user.email,
            'access_code': access_code,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'members': [
                {
                    'email': current_user.email,
                    'role': 'owner',
                    'joined_at': datetime.now().isoformat()
                }
            ],
            'messages': []
        }
        notes = dm.load_data('shared_notes')
        notes.append(new_note)
        dm.save_data('shared_notes', notes)
        flash('Notat opprettet! Del tilgangskoden med andre.', 'success')
        return redirect(url_for('view_shared_note', note_id=note_id))
    
    return render_template('create_shared_note.html', form=form)

@app.route('/shared-notes/view/<note_id>')
@login_required
def view_shared_note(note_id):
    notes = dm.load_data('shared_notes')
    note = next((n for n in notes if n.get('id') == note_id), None)
    
    if not note:
        flash('Notat ikke funnet', 'danger')
        return redirect(url_for('shared_notes'))
    
    # Check if user has access
    user_email = current_user.email
    is_member = any(m.get('email') == user_email for m in note.get('members', []))
    is_owner = note.get('user_id') == user_email
    
    if not (is_member or is_owner):
        flash('Du har ikke tilgang til dette notatet', 'danger')
        return redirect(url_for('shared_notes'))
    
    return render_template('view_shared_note.html', note=note)

@app.route('/shared-notes/join', methods=['GET', 'POST'])
@login_required
def join_shared_note():
    form = FlaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        access_code = request.form.get('access_code')
        
        if not access_code:
            flash('Tilgangskode er påkrevd', 'danger')
            return redirect(url_for('join_shared_note'))
        
        notes = dm.load_data('shared_notes')
        note = next((n for n in notes if n.get('access_code') == access_code), None)
        
        if not note:
            flash('Ugyldig tilgangskode', 'danger')
            return redirect(url_for('join_shared_note'))
        
        # Check if user is already a member
        user_email = current_user.email
        is_member = any(m.get('email') == user_email for m in note.get('members', []))
        
        if is_member:
            flash('Du er allerede medlem av dette notatet', 'info')
            return redirect(url_for('view_shared_note', note_id=note.get('id')))
        
        # Add user as member
        note['members'].append({
            'email': user_email,
            'role': 'member',
            'joined_at': datetime.now().isoformat()
        })
          # Update shared notes
        for i, n in enumerate(notes):
            if n.get('id') == note.get('id'):
                notes[i] = note
                break
        
        dm.save_data('shared_notes', notes)
        
        flash('Du er nå medlem av notatet!', 'success')
        return redirect(url_for('view_shared_note', note_id=note.get('id')))
    
    return render_template('join_shared_note.html', form=form)

@app.route('/shared-notes/update/<note_id>', methods=['POST'])
@login_required
def update_shared_note(note_id):
    content = request.form.get('content')
    
    notes = dm.load_data('shared_notes')
    note = next((n for n in notes if n.get('id') == note_id), None)
    
    if not note:
        flash('Notat ikke funnet', 'danger')
        return redirect(url_for('shared_notes'))
    
    # Check if user has access
    user_email = current_user.email
    is_member = any(m.get('email') == user_email for m in note.get('members', []))
    is_owner = note.get('user_id') == user_email
    
    if not (is_member or is_owner):
        flash('Du har ikke tilgang til å redigere dette notatet', 'danger')
        return redirect(url_for('shared_notes'))
    
    # Update note
    note['content'] = content
    note['updated_at'] = datetime.now().isoformat()
    
    # Update notes list
    for i, n in enumerate(notes):
        if n.get('id') == note_id:
            notes[i] = note
            break
    
    dm.save_data('shared_notes', notes)
    
    flash('Notat oppdatert!', 'success')
    return redirect(url_for('view_shared_note', note_id=note_id))

@app.route('/shared-notes/message/<note_id>', methods=['POST'])
@login_required
def add_message_to_note(note_id):
    message_content = request.form.get('message')
    
    if not message_content:
        flash('Meldingsinnhold er påkrevd', 'danger')
        return redirect(url_for('view_shared_note', note_id=note_id))
    
    notes = dm.load_data('shared_notes')
    note = next((n for n in notes if n.get('id') == note_id), None)
    
    if not note:
        flash('Notat ikke funnet', 'danger')
        return redirect(url_for('shared_notes'))
    
    # Check if user has access
    user_email = current_user.email
    is_member = any(m.get('email') == user_email for m in note.get('members', []))
    is_owner = note.get('user_id') == user_email
    
    if not (is_member or is_owner):
        flash('Du har ikke tilgang til dette notatet', 'danger')
        return redirect(url_for('shared_notes'))
    
    # Add message
    if 'messages' not in note:
        note['messages'] = []
    
    note['messages'].append({
        'sender': user_email,
        'content': message_content,
        'timestamp': datetime.now().isoformat()
    })
    
    # Update notes list
    for i, n in enumerate(notes):
        if n.get('id') == note_id:
            notes[i] = note
            break
    
    dm.save_data('shared_notes', notes)
    
    return redirect(url_for('view_shared_note', note_id=note_id))



@app.route('/api/mode', methods=['POST'])
@login_required
def change_mode():
    data = request.json
    mode = data.get('mode', 'DEFAULT')
    
    current_user.app_mode = mode    # In a real app, you would save this to the database
    
    return jsonify({'message': f'Mode changed to {mode}', 'mode': mode}), 200

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.route('/set_mode', methods=['POST'])
@login_required
def set_mode():
    """Set the application mode for the current user"""
    mode = request.form.get('app_mode', 'DEFAULT')
    if mode not in ['DEFAULT', 'ADHD_FRIENDLY', 'SILENT', 'FOCUS', 'DARK']:
        flash('Ugyldig modus valgt', 'error')
        return redirect(url_for('settings'))
    
    try:
        current_user.app_mode = mode
        flash('Modus endret til: ' + mode, 'success')
    except Exception as e:
        logger.error(f"Error setting mode: {e}")
        flash('Kunne ikke endre modus', 'error')
    
    return redirect(request.referrer or url_for('dashboard'))

# Oppdater User-klassen
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
