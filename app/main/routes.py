"""
Hlavní routes aplikace - dashboard, novinky, zprávy
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.main.forms import NewsForm, CommentForm, PollForm, MessageForm
from app.models import User, News, Comment, NewsLike, Poll, PollOption, PollVote, Message, Application

@bp.route('/')
@bp.route('/index')
def index():
    """Hlavní stránka aplikace."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Log návštěvy hlavní stránky
    current_user.log_activity('page_view', 'Návštěva hlavní stránky', request.remote_addr)
    
    # Nejnovější novinky
    page = request.args.get('page', 1, type=int)
    news = News.query.filter_by(published=True).order_by(
        News.featured.desc(), News.created_at.desc()
    ).paginate(
        page=page, per_page=5, error_out=False
    )
    
    # Dostupné aplikace pro uživatele
    applications = Application.query.filter_by(active=True).order_by(
        Application.order.asc(), Application.name.asc()
    ).all()
    
    # Filtrování aplikací podle oprávnění
    accessible_apps = [app for app in applications if app.can_access(current_user)]
    
    # Nepřečtené zprávy
    unread_messages_count = Message.query.filter_by(
        recipient_id=current_user.id,
        read_at=None
    ).count()
    
    # Aktivní ankety
    active_polls = Poll.query.filter_by(active=True).filter(
        Poll.end_date.is_(None) | (Poll.end_date > datetime.utcnow())
    ).order_by(Poll.created_at.desc()).limit(3).all()
    
    return render_template('main/index.html', 
                         title='Dashboard',
                         news=news,
                         applications=accessible_apps,
                         unread_messages_count=unread_messages_count,
                         active_polls=active_polls)

@bp.route('/news/<int:id>')
def news_detail(id):
    """Detail novinky."""
    news = News.query.get_or_404(id)
    
    if not news.published and not current_user.is_administrator():
        flash('Tato novinka není publikovaná', 'warning')
        return redirect(url_for('main.index'))
    
    # Log zobrazení novinky
    if current_user.is_authenticated:
        current_user.log_activity('news_view', f'Zobrazení novinky: {news.title}',
                                request.remote_addr)
    
    # Komentáře
    comments = Comment.query.filter_by(news_id=id, approved=True).order_by(
        Comment.created_at.asc()
    ).all()
    
    # Formulář pro nový komentář
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=form.content.data,
            author=current_user,
            news=news
        )
        db.session.add(comment)
        db.session.commit()
        
        # Log přidání komentáře
        current_user.log_activity('comment_added', 
                                f'Komentář k novince: {news.title}',
                                request.remote_addr)
        
        flash('Váš komentář byl přidán', 'success')
        return redirect(url_for('main.news_detail', id=id))
    
    return render_template('main/news_detail.html', 
                         title=news.title,
                         news=news,
                         comments=comments,
                         form=form)

@bp.route('/like_news/<int:id>', methods=['POST'])
@login_required
def like_news(id):
    """Toggle lajku novinky."""
    news = News.query.get_or_404(id)
    
    existing_like = NewsLike.query.filter_by(
        user_id=current_user.id,
        news_id=id
    ).first()
    
    if existing_like:
        # Odebrání lajku
        db.session.delete(existing_like)
        liked = False
        action = 'unlike'
    else:
        # Přidání lajku
        like = NewsLike(user=current_user, news=news)
        db.session.add(like)
        liked = True
        action = 'like'
    
    db.session.commit()
    
    # Log akce
    current_user.log_activity(f'news_{action}', 
                            f'{"Líbí se" if liked else "Už se nelíbí"}: {news.title}',
                            request.remote_addr)
    
    return jsonify({
        'liked': liked,
        'likes_count': news.get_likes_count()
    })

@bp.route('/poll/<int:id>')
def poll_detail(id):
    """Detail ankety."""
    poll = Poll.query.get_or_404(id)
    
    # Kontrola, zda je anketa aktivní
    if not poll.is_active() and not current_user.is_administrator():
        flash('Tato anketa už není aktivní', 'warning')
        return redirect(url_for('main.index'))
    
    # Log zobrazení ankety
    current_user.log_activity('poll_view', f'Zobrazení ankety: {poll.question}',
                            request.remote_addr)
    
    # Možnosti s počty hlasů
    options_with_votes = []
    for option in poll.options.order_by(PollOption.order.asc()):
        options_with_votes.append({
            'option': option,
            'votes_count': option.get_votes_count(),
            'percentage': option.get_percentage()
        })
    
    user_vote = None
    if current_user.is_authenticated:
        user_vote = PollVote.query.filter_by(
            poll_id=id,
            user_id=current_user.id
        ).first()
    
    return render_template('main/poll_detail.html',
                         title=poll.question,
                         poll=poll,
                         options_with_votes=options_with_votes,
                         user_vote=user_vote)

@bp.route('/vote/<int:poll_id>/<int:option_id>', methods=['POST'])
@login_required
def vote_poll(poll_id, option_id):
    """Hlasování v anketě."""
    poll = Poll.query.get_or_404(poll_id)
    option = PollOption.query.get_or_404(option_id)
    
    if option.poll_id != poll_id:
        return jsonify({'error': 'Neplatná možnost'}), 400
    
    if not poll.is_active():
        return jsonify({'error': 'Anketa už není aktivní'}), 400
    
    if poll.has_voted(current_user):
        if not poll.multiple_choice:
            return jsonify({'error': 'V této anketě můžete hlasovat pouze jednou'}), 400
    
    # Vytvoření hlasu
    vote = PollVote(poll=poll, option=option, voter=current_user)
    db.session.add(vote)
    db.session.commit()
    
    # Log hlasování
    current_user.log_activity('poll_vote', 
                            f'Hlas v anketě: {poll.question} -> {option.text}',
                            request.remote_addr)
    
    return jsonify({
        'success': True,
        'total_votes': poll.get_total_votes()
    })

@bp.route('/messages')
@login_required
def messages():
    """Seznam zpráv uživatele."""
    page = request.args.get('page', 1, type=int)
    
    # Příchozí zprávy
    received = Message.query.filter_by(recipient_id=current_user.id).order_by(
        Message.created_at.desc()
    ).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Odeslané zprávy
    sent_page = request.args.get('sent_page', 1, type=int)
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(
        Message.created_at.desc()
    ).paginate(
        page=sent_page, per_page=10, error_out=False
    )
    
    # Log zobrazení zpráv
    current_user.log_activity('messages_view', 'Zobrazení seznamu zpráv',
                            request.remote_addr)
    
    return render_template('main/messages.html',
                         title='Zprávy',
                         received_messages=received,
                         sent_messages=sent)

@bp.route('/message/<int:id>')
@login_required
def message_detail(id):
    """Detail zprávy."""
    message = Message.query.get_or_404(id)
    
    # Kontrola oprávnění
    if (message.recipient_id != current_user.id and 
        message.sender_id != current_user.id and
        not current_user.is_administrator()):
        flash('Nemáte oprávnění k zobrazení této zprávy', 'danger')
        return redirect(url_for('main.messages'))
    
    # Označení jako přečtené
    if message.recipient_id == current_user.id and not message.is_read():
        message.mark_as_read()
    
    # Log zobrazení zprávy
    current_user.log_activity('message_view', f'Zobrazení zprávy: {message.subject}',
                            request.remote_addr)
    
    return render_template('main/message_detail.html',
                         title=message.subject,
                         message=message)

@bp.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    """Odeslání nové zprávy."""
    form = MessageForm()
    
    # Naplnění seznamu uživatelů
    users = User.query.filter(User.id != current_user.id).order_by(
        User.first_name.asc(), User.last_name.asc()
    ).all()
    form.recipient.choices = [(0, 'Vyberte příjemce')] + [
        (user.id, f'{user.get_full_name()} ({user.username})')
        for user in users
    ]
    
    if form.validate_on_submit():
        recipient = User.query.get(form.recipient.data)
        if not recipient:
            flash('Neplatný příjemce', 'danger')
            return redirect(url_for('main.send_message'))
        
        message = Message(
            subject=form.subject.data,
            body=form.body.data,
            priority=form.priority.data,
            sender=current_user,
            recipient=recipient
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Log odeslání zprávy
        current_user.log_activity('message_sent', 
                                f'Zpráva odeslána uživateli: {recipient.username}',
                                request.remote_addr)
        
        flash(f'Zpráva byla odeslána uživateli {recipient.get_full_name()}', 'success')
        return redirect(url_for('main.messages'))
    
    return render_template('main/send_message.html',
                         title='Nová zpráva',
                         form=form)

@bp.route('/applications')
@login_required
def applications():
    """Seznam dostupných aplikací."""
    # Všechny aktivní aplikace
    all_applications = Application.query.filter_by(active=True).order_by(
        Application.order.asc(), Application.name.asc()
    ).all()
    
    # Filtrování podle oprávnění
    accessible_apps = [app for app in all_applications if app.can_access(current_user)]
    
    # Log zobrazení aplikací
    current_user.log_activity('applications_view', 'Zobrazení seznamu aplikací',
                            request.remote_addr)
    
    return render_template('main/applications.html',
                         title='Aplikace',
                         applications=accessible_apps)

@bp.route('/application/<int:id>')
@login_required
def application_redirect(id):
    """Přesměrování na aplikaci."""
    app = Application.query.get_or_404(id)
    
    if not app.can_access(current_user):
        flash('Nemáte přístup k této aplikaci', 'danger')
        return redirect(url_for('main.applications'))
    
    # Log přístupu do aplikace
    current_user.log_activity('application_access', 
                            f'Přístup do aplikace: {app.name}',
                            request.remote_addr)
    
    if app.url:
        return redirect(app.url)
    else:
        flash('Aplikace není dostupná', 'warning')
        return redirect(url_for('main.applications'))