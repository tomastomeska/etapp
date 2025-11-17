"""
Administrační routes - správa uživatelů, novinek, aplikací
"""

from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.admin import bp
from app.auth.forms import RegistrationForm
from app.main.forms import NewsForm, PollForm, BroadcastMessageForm
from app.models import User, Role, News, Comment, Poll, PollOption, Message, Application, UserActivity

def admin_required(f):
    """Dekorátor pro kontrolu administrátorských oprávnění."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_administrator():
            flash('Nemáte oprávnění k přístupu do administrace', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Administrační dashboard."""
    # Statistiky
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_news = News.query.count()
    total_comments = Comment.query.count()
    
    # Uživatelé online (posledních 15 minut)
    online_threshold = datetime.utcnow() - timedelta(minutes=15)
    online_users = User.query.filter(User.last_seen > online_threshold).count()
    
    # Nejnovější aktivity
    recent_activities = UserActivity.query.order_by(
        UserActivity.timestamp.desc()
    ).limit(10).all()
    
    # Nejnovější uživatelé
    new_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Log přístupu do administrace
    current_user.log_activity('admin_access', 'Přístup do administrace',
                            request.remote_addr)
    
    return render_template('admin/index.html',
                         title='Administrace',
                         total_users=total_users,
                         active_users=active_users,
                         online_users=online_users,
                         total_news=total_news,
                         total_comments=total_comments,
                         recent_activities=recent_activities,
                         new_users=new_users)

@bp.route('/users')
@login_required
@admin_required
def users():
    """Seznam všech uživatelů."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    # Vyhledávání
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.email.contains(search) |
            User.first_name.contains(search) |
            User.last_name.contains(search)
        )
    
    # Filtrování podle role
    if role_filter:
        role = Role.query.filter_by(name=role_filter).first()
        if role:
            query = query.filter_by(role=role)
    
    users = query.order_by(User.last_seen.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Seznam rolí pro filtr
    roles = Role.query.all()
    
    return render_template('admin/users.html',
                         title='Správa uživatelů',
                         users=users,
                         roles=roles,
                         search=search,
                         role_filter=role_filter)

@bp.route('/user/<int:id>')
@login_required
@admin_required
def user_detail(id):
    """Detail uživatele."""
    user = User.query.get_or_404(id)
    
    # Poslední aktivity uživatele
    activities = UserActivity.query.filter_by(user_id=id).order_by(
        UserActivity.timestamp.desc()
    ).limit(20).all()
    
    return render_template('admin/user_detail.html',
                         title=f'Detail uživatele: {user.get_full_name()}',
                         user=user,
                         activities=activities)

@bp.route('/user/<int:id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(id):
    """Aktivace/deaktivace uživatele."""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Nemůžete deaktivovat sami sebe'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    # Log akce
    action = 'aktivován' if user.is_active else 'deaktivován'
    current_user.log_activity('user_status_changed', 
                            f'Uživatel {user.username} {action}',
                            request.remote_addr)
    
    return jsonify({
        'success': True,
        'is_active': user.is_active,
        'message': f'Uživatel {user.get_full_name()} byl {action}'
    })

@bp.route('/user/<int:id>/change_role', methods=['POST'])
@login_required
@admin_required
def change_user_role(id):
    """Změna role uživatele."""
    user = User.query.get_or_404(id)
    new_role_id = request.json.get('role_id')
    
    if user.id == current_user.id:
        return jsonify({'error': 'Nemůžete změnit svou vlastní roli'}), 400
    
    new_role = Role.query.get(new_role_id)
    if not new_role:
        return jsonify({'error': 'Neplatná role'}), 400
    
    old_role_name = user.role.name if user.role else 'Žádná'
    user.role = new_role
    db.session.commit()
    
    # Log změny role
    current_user.log_activity('user_role_changed', 
                            f'Role uživatele {user.username}: {old_role_name} → {new_role.name}',
                            request.remote_addr)
    
    return jsonify({
        'success': True,
        'new_role': new_role.name,
        'message': f'Role uživatele {user.get_full_name()} byla změněna na {new_role.name}'
    })

@bp.route('/news')
@login_required
@admin_required
def news():
    """Správa novinek."""
    page = request.args.get('page', 1, type=int)
    
    news_items = News.query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('admin/news.html',
                         title='Správa novinek',
                         news_items=news_items)

@bp.route('/news/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_news():
    """Vytvoření nové novinky."""
    form = NewsForm()
    
    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            summary=form.summary.data,
            content=form.content.data,
            featured=form.featured.data,
            allow_comments=form.allow_comments.data,
            published=form.published.data,
            author=current_user
        )
        
        if form.published.data:
            news.published_at = datetime.utcnow()
        
        # TODO: Zpracování obrázku
        
        db.session.add(news)
        db.session.commit()
        
        # Log vytvoření novinky
        current_user.log_activity('news_created', f'Vytvořena novinka: {news.title}',
                                request.remote_addr)
        
        flash('Novinka byla úspěšně vytvořena', 'success')
        return redirect(url_for('admin.news'))
    
    return render_template('admin/create_news.html',
                         title='Nová novinka',
                         form=form)

@bp.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_news(id):
    """Úprava novinky."""
    news = News.query.get_or_404(id)
    form = NewsForm()
    
    if form.validate_on_submit():
        news.title = form.title.data
        news.summary = form.summary.data
        news.content = form.content.data
        news.featured = form.featured.data
        news.allow_comments = form.allow_comments.data
        was_published = news.published
        news.published = form.published.data
        news.updated_at = datetime.utcnow()
        
        # Pokud se novinka publikuje poprvé
        if form.published.data and not was_published:
            news.published_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log úpravy novinky
        current_user.log_activity('news_edited', f'Upravena novinka: {news.title}',
                                request.remote_addr)
        
        flash('Novinka byla úspěšně upravena', 'success')
        return redirect(url_for('admin.news'))
    
    elif request.method == 'GET':
        # Předvyplnění formuláře
        form.title.data = news.title
        form.summary.data = news.summary
        form.content.data = news.content
        form.featured.data = news.featured
        form.allow_comments.data = news.allow_comments
        form.published.data = news.published
    
    return render_template('admin/edit_news.html',
                         title='Upravit novinku',
                         form=form,
                         news=news)

@bp.route('/news/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_news(id):
    """Smazání novinky."""
    news = News.query.get_or_404(id)
    title = news.title
    
    db.session.delete(news)
    db.session.commit()
    
    # Log smazání novinky
    current_user.log_activity('news_deleted', f'Smazána novinka: {title}',
                            request.remote_addr)
    
    return jsonify({
        'success': True,
        'message': f'Novinka "{title}" byla smazána'
    })

@bp.route('/polls')
@login_required
@admin_required
def polls():
    """Správa anket."""
    page = request.args.get('page', 1, type=int)
    
    polls = Poll.query.order_by(Poll.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('admin/polls.html',
                         title='Správa anket',
                         polls=polls)

@bp.route('/poll/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_poll():
    """Vytvoření nové ankety."""
    form = PollForm()
    
    if form.validate_on_submit():
        poll = Poll(
            question=form.question.data,
            description=form.description.data,
            multiple_choice=form.multiple_choice.data,
            anonymous=form.anonymous.data,
            author=current_user
        )
        
        db.session.add(poll)
        db.session.flush()  # Pro získání ID
        
        # Přidání možností
        options = [
            form.option1.data, form.option2.data, form.option3.data,
            form.option4.data, form.option5.data
        ]
        
        for i, option_text in enumerate(options):
            if option_text and option_text.strip():
                option = PollOption(
                    text=option_text.strip(),
                    order=i,
                    poll=poll
                )
                db.session.add(option)
        
        db.session.commit()
        
        # Log vytvoření ankety
        current_user.log_activity('poll_created', f'Vytvořena anketa: {poll.question}',
                                request.remote_addr)
        
        flash('Anketa byla úspěšně vytvořena', 'success')
        return redirect(url_for('admin.polls'))
    
    return render_template('admin/create_poll.html',
                         title='Nová anketa',
                         form=form)

@bp.route('/broadcast', methods=['GET', 'POST'])
@login_required
@admin_required
def broadcast_message():
    """Odeslání hromadné zprávy."""
    form = BroadcastMessageForm()
    
    if form.validate_on_submit():
        # Získání všech aktivních uživatelů kromě administrátora
        users = User.query.filter(
            User.is_active == True,
            User.id != current_user.id
        ).all()
        
        message_count = 0
        for user in users:
            message = Message(
                subject=form.subject.data,
                body=form.body.data,
                priority=form.priority.data,
                is_broadcast=True,
                sender=current_user,
                recipient=user
            )
            db.session.add(message)
            message_count += 1
        
        db.session.commit()
        
        # Log hromadné zprávy
        current_user.log_activity('broadcast_sent', 
                                f'Hromadná zpráva odeslána {message_count} uživatelům',
                                request.remote_addr)
        
        flash(f'Hromadná zpráva byla odeslána {message_count} uživatelům', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/broadcast.html',
                         title='Hromadná zpráva',
                         form=form)

@bp.route('/applications')
@login_required
@admin_required
def applications():
    """Správa aplikací."""
    applications = Application.query.order_by(
        Application.order.asc(), Application.name.asc()
    ).all()
    
    return render_template('admin/applications.html',
                         title='Správa aplikací',
                         applications=applications)

@bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytické přehledy."""
    # Statistiky za posledních 30 dní
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Přihlášení za posledních 30 dní
    login_stats = db.session.query(
        UserActivity.timestamp.cast(db.Date).label('date'),
        db.func.count(UserActivity.id).label('count')
    ).filter(
        UserActivity.activity_type == 'login',
        UserActivity.timestamp >= thirty_days_ago
    ).group_by(
        UserActivity.timestamp.cast(db.Date)
    ).all()
    
    # Top uživatelé podle aktivity
    top_users = db.session.query(
        User.username,
        User.first_name,
        User.last_name,
        db.func.count(UserActivity.id).label('activity_count')
    ).join(UserActivity).filter(
        UserActivity.timestamp >= thirty_days_ago
    ).group_by(User.id).order_by(
        db.func.count(UserActivity.id).desc()
    ).limit(10).all()
    
    return render_template('admin/analytics.html',
                         title='Analytiky',
                         login_stats=login_stats,
                         top_users=top_users)