"""
Databázové modely pro European Transport CZ aplikaci
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

# Asociační tabulka pro many-to-many vztah mezi uživateli a oprávněními
user_permissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """Model uživatele systému."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    avatar_filename = db.Column(db.String(255))
    
    # Stav účtu
    is_active = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime)
    
    # Časové značky
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_ip = db.Column(db.String(45))  # IPv6 support
    
    # Vztahy
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))
    
    # Příspěvky a komentáře
    news_posts = db.relationship('News', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    # Aktivity uživatele
    activities = db.relationship('UserActivity', backref='user', lazy='dynamic')
    
    # Zprávy
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', 
                                   backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id',
                                       backref='recipient', lazy='dynamic')
    
    def set_password(self, password):
        """Nastavení hashovaného hesla."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Ověření hesla."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Vrátí celé jméno uživatele."""
        return f"{self.first_name} {self.last_name}"
    
    def can(self, permission_name):
        """Kontrola oprávnění uživatele."""
        if self.role:
            return self.role.has_permission(permission_name)
        return False
    
    def is_administrator(self):
        """Kontrola, zda je uživatel administrátor."""
        return self.can('admin')
    
    def ping(self):
        """Aktualizace času poslední aktivity."""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    def log_activity(self, activity_type, description, ip_address=None):
        """Zalogování aktivity uživatele."""
        activity = UserActivity(
            user=self,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Role(db.Model):
    """Model role uživatele."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    default = db.Column(db.Boolean, default=False, index=True)
    
    # Vztahy
    permissions = db.relationship('Permission', secondary='role_permissions',
                                backref=db.backref('roles', lazy='dynamic'))
    
    def add_permission(self, permission_name):
        """Přidání oprávnění k roli."""
        permission = Permission.query.filter_by(name=permission_name).first()
        if permission and permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission_name):
        """Odebrání oprávnění z role."""
        permission = Permission.query.filter_by(name=permission_name).first()
        if permission and permission in self.permissions:
            self.permissions.remove(permission)
    
    def has_permission(self, permission_name):
        """Kontrola, zda role má dané oprávnění."""
        return any(perm.name == permission_name for perm in self.permissions)
    
    @staticmethod
    def insert_roles():
        """Vytvoření základních rolí."""
        roles = {
            'Uživatel': ['read_news', 'comment', 'edit_profile'],
            'Moderátor': ['read_news', 'comment', 'edit_profile', 'moderate_comments'],
            'Administrátor': ['admin', 'read_news', 'comment', 'edit_profile', 
                            'create_news', 'edit_news', 'delete_news', 
                            'moderate_comments', 'manage_users', 'view_analytics']
        }
        
        # Vytvoření oprávnění
        permissions = ['admin', 'read_news', 'comment', 'edit_profile', 
                      'create_news', 'edit_news', 'delete_news', 
                      'moderate_comments', 'manage_users', 'view_analytics']
        
        for perm_name in permissions:
            permission = Permission.query.filter_by(name=perm_name).first()
            if not permission:
                permission = Permission(name=perm_name)
                db.session.add(permission)
        
        # Vytvoření rolí
        default_role = 'Uživatel'
        for role_name, role_permissions in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, default=(role_name == default_role))
                db.session.add(role)
            
            role.permissions = []
            for perm_name in role_permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission:
                    role.permissions.append(permission)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<Role {self.name}>'

# Asociační tabulka pro role a oprávnění
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Permission(db.Model):
    """Model oprávnění."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class News(db.Model):
    """Model novinek a aktualit."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    image_filename = db.Column(db.String(255))
    
    # Stav příspěvku
    published = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)
    
    # Časové značky
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Vztahy
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='news', lazy='dynamic', 
                              cascade='all, delete-orphan')
    likes = db.relationship('NewsLike', backref='news', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    def get_likes_count(self):
        """Počet lajků příspěvku."""
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Kontrola, zda uživatel dal lajk."""
        if not user.is_authenticated:
            return False
        return self.likes.filter_by(user_id=user.id).first() is not None
    
    def __repr__(self):
        return f'<News {self.title}>'

class Comment(db.Model):
    """Model komentářů k novinkám."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Moderace
    approved = db.Column(db.Boolean, default=True)
    
    # Vztahy
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class NewsLike(db.Model):
    """Model lajků novinek."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Vztahy
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'news_id', name='unique_user_news_like'),)

class Poll(db.Model):
    """Model anket."""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Nastavení ankety
    multiple_choice = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    
    # Časové značky
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    
    # Vztahy
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='polls')
    options = db.relationship('PollOption', backref='poll', lazy='dynamic',
                             cascade='all, delete-orphan')
    votes = db.relationship('PollVote', backref='poll', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    def get_total_votes(self):
        """Celkový počet hlasů."""
        return self.votes.count()
    
    def is_active(self):
        """Kontrola, zda je anketa aktivní."""
        if not self.active:
            return False
        if self.end_date and datetime.utcnow() > self.end_date:
            return False
        return True
    
    def has_voted(self, user):
        """Kontrola, zda uživatel již hlasoval."""
        if not user.is_authenticated:
            return False
        return self.votes.filter_by(user_id=user.id).first() is not None
    
    def __repr__(self):
        return f'<Poll {self.question}>'

class PollOption(db.Model):
    """Model možností ankety."""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, default=0)
    
    # Vztahy
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    votes = db.relationship('PollVote', backref='option', lazy='dynamic')
    
    def get_votes_count(self):
        """Počet hlasů pro tuto možnost."""
        return self.votes.count()
    
    def get_percentage(self):
        """Procentuální zastoupení této možnosti."""
        total = self.poll.get_total_votes()
        if total == 0:
            return 0
        return round((self.get_votes_count() / total) * 100, 1)
    
    def __repr__(self):
        return f'<PollOption {self.text}>'

class PollVote(db.Model):
    """Model hlasů v anketách."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Vztahy
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('poll_option.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # NULL pro anonymní hlasování
    voter = db.relationship('User', backref='poll_votes')

class UserActivity(db.Model):
    """Model pro sledování aktivit uživatelů."""
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)  # login, logout, view_page, etc.
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Vztahy
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<UserActivity {self.user.username}: {self.activity_type}>'

class Message(db.Model):
    """Model pro zprávy mezi uživateli."""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime)
    
    # Typ zprávy
    is_broadcast = db.Column(db.Boolean, default=False)  # Zpráva pro všechny
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    
    # Vztahy
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # NULL pro broadcast
    
    def is_read(self):
        """Kontrola, zda byla zpráva přečtena."""
        return self.read_at is not None
    
    def mark_as_read(self):
        """Označení zprávy jako přečtené."""
        if not self.is_read():
            self.read_at = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
    
    def __repr__(self):
        return f'<Message {self.subject}>'

class Application(db.Model):
    """Model pro externí aplikace."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    color = db.Column(db.String(7), default='#007bff')  # Hex color
    
    # Nastavení aplikace
    active = db.Column(db.Boolean, default=True)
    requires_role = db.Column(db.String(64))  # Vyžadovaná role
    order = db.Column(db.Integer, default=0)
    
    # Časové značky
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def can_access(self, user):
        """Kontrola přístupu uživatele k aplikaci."""
        if not self.active:
            return False
        if not self.requires_role:
            return True
        return user.role and user.role.name == self.requires_role
    
    def __repr__(self):
        return f'<Application {self.name}>'