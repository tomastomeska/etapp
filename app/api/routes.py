"""
API routes - REST API pro mobilní aplikace a externí systémy
"""

from datetime import datetime
from flask import jsonify, request
from flask_login import current_user, login_required
from app import db
from app.api import bp
from app.models import User, News, Comment, Poll, Message

@bp.route('/status')
def status():
    """Status API."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@bp.route('/user/profile')
@login_required
def user_profile():
    """Profil aktuálního uživatele."""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'full_name': current_user.get_full_name(),
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'phone': current_user.phone,
        'department': current_user.department,
        'position': current_user.position,
        'role': current_user.role.name if current_user.role else None,
        'last_seen': current_user.last_seen.isoformat() if current_user.last_seen else None,
        'created_at': current_user.created_at.isoformat()
    })

@bp.route('/users/online')
@login_required
def users_online():
    """Seznam online uživatelů (posledních 15 minut)."""
    if not current_user.is_administrator():
        return jsonify({'error': 'Nemáte oprávnění'}), 403
    
    from datetime import timedelta
    online_threshold = datetime.utcnow() - timedelta(minutes=15)
    
    online_users = User.query.filter(
        User.last_seen > online_threshold,
        User.is_active == True
    ).all()
    
    return jsonify({
        'count': len(online_users),
        'users': [{
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'last_seen': user.last_seen.isoformat()
        } for user in online_users]
    })

@bp.route('/news')
@login_required
def news_list():
    """Seznam novinek."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    
    news = News.query.filter_by(published=True).order_by(
        News.featured.desc(), News.created_at.desc()
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'news': [{
            'id': item.id,
            'title': item.title,
            'summary': item.summary,
            'content': item.content,
            'featured': item.featured,
            'likes_count': item.get_likes_count(),
            'is_liked': item.is_liked_by(current_user),
            'comments_count': item.comments.filter_by(approved=True).count(),
            'author': {
                'id': item.author.id,
                'name': item.author.get_full_name()
            },
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        } for item in news.items],
        'pagination': {
            'page': news.page,
            'pages': news.pages,
            'per_page': news.per_page,
            'total': news.total,
            'has_next': news.has_next,
            'has_prev': news.has_prev
        }
    })

@bp.route('/news/<int:id>')
@login_required
def news_detail(id):
    """Detail novinky."""
    news = News.query.get_or_404(id)
    
    if not news.published and not current_user.is_administrator():
        return jsonify({'error': 'Novinka není publikovaná'}), 404
    
    # Komentáře
    comments = Comment.query.filter_by(news_id=id, approved=True).order_by(
        Comment.created_at.asc()
    ).all()
    
    return jsonify({
        'id': news.id,
        'title': news.title,
        'summary': news.summary,
        'content': news.content,
        'featured': news.featured,
        'likes_count': news.get_likes_count(),
        'is_liked': news.is_liked_by(current_user),
        'allow_comments': news.allow_comments,
        'author': {
            'id': news.author.id,
            'name': news.author.get_full_name()
        },
        'comments': [{
            'id': comment.id,
            'content': comment.content,
            'author': {
                'id': comment.author.id,
                'name': comment.author.get_full_name()
            },
            'created_at': comment.created_at.isoformat()
        } for comment in comments],
        'created_at': news.created_at.isoformat(),
        'updated_at': news.updated_at.isoformat()
    })

@bp.route('/news/<int:id>/like', methods=['POST'])
@login_required
def toggle_news_like(id):
    """Toggle lajku novinky."""
    news = News.query.get_or_404(id)
    
    from app.models import NewsLike
    existing_like = NewsLike.query.filter_by(
        user_id=current_user.id,
        news_id=id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = NewsLike(user=current_user, news=news)
        db.session.add(like)
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'liked': liked,
        'likes_count': news.get_likes_count()
    })

@bp.route('/news/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """Přidání komentáře k novince."""
    news = News.query.get_or_404(id)
    
    if not news.allow_comments:
        return jsonify({'error': 'Komentáře nejsou povolené'}), 400
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Komentář nemůže být prázdný'}), 400
    
    if len(content) > 1000:
        return jsonify({'error': 'Komentář je příliš dlouhý'}), 400
    
    comment = Comment(
        content=content,
        author=current_user,
        news=news
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'author': {
            'id': comment.author.id,
            'name': comment.author.get_full_name()
        },
        'created_at': comment.created_at.isoformat()
    }), 201

@bp.route('/polls')
@login_required
def polls_list():
    """Seznam aktivních anket."""
    polls = Poll.query.filter_by(active=True).filter(
        Poll.end_date.is_(None) | (Poll.end_date > datetime.utcnow())
    ).order_by(Poll.created_at.desc()).all()
    
    return jsonify({
        'polls': [{
            'id': poll.id,
            'question': poll.question,
            'description': poll.description,
            'multiple_choice': poll.multiple_choice,
            'anonymous': poll.anonymous,
            'total_votes': poll.get_total_votes(),
            'has_voted': poll.has_voted(current_user),
            'options': [{
                'id': option.id,
                'text': option.text,
                'votes_count': option.get_votes_count(),
                'percentage': option.get_percentage()
            } for option in poll.options.order_by('order')],
            'created_at': poll.created_at.isoformat(),
            'end_date': poll.end_date.isoformat() if poll.end_date else None
        } for poll in polls]
    })

@bp.route('/polls/<int:poll_id>/vote', methods=['POST'])
@login_required
def vote_poll(poll_id):
    """Hlasování v anketě."""
    poll = Poll.query.get_or_404(poll_id)
    
    if not poll.is_active():
        return jsonify({'error': 'Anketa už není aktivní'}), 400
    
    data = request.get_json()
    option_id = data.get('option_id')
    
    from app.models import PollOption, PollVote
    option = PollOption.query.get_or_404(option_id)
    
    if option.poll_id != poll_id:
        return jsonify({'error': 'Neplatná možnost'}), 400
    
    if poll.has_voted(current_user) and not poll.multiple_choice:
        return jsonify({'error': 'V této anketě můžete hlasovat pouze jednou'}), 400
    
    vote = PollVote(poll=poll, option=option, voter=current_user)
    db.session.add(vote)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'total_votes': poll.get_total_votes(),
        'option_votes': option.get_votes_count()
    })

@bp.route('/messages')
@login_required
def messages_list():
    """Seznam zpráv uživatele."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    message_type = request.args.get('type', 'received')  # received, sent
    
    if message_type == 'sent':
        query = Message.query.filter_by(sender_id=current_user.id)
    else:
        query = Message.query.filter_by(recipient_id=current_user.id)
    
    messages = query.order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'messages': [{
            'id': msg.id,
            'subject': msg.subject,
            'body': msg.body[:100] + '...' if len(msg.body) > 100 else msg.body,
            'priority': msg.priority,
            'is_read': msg.is_read(),
            'is_broadcast': msg.is_broadcast,
            'sender': {
                'id': msg.sender.id,
                'name': msg.sender.get_full_name()
            } if message_type == 'received' else None,
            'recipient': {
                'id': msg.recipient.id,
                'name': msg.recipient.get_full_name()
            } if message_type == 'sent' else None,
            'created_at': msg.created_at.isoformat(),
            'read_at': msg.read_at.isoformat() if msg.read_at else None
        } for msg in messages.items],
        'pagination': {
            'page': messages.page,
            'pages': messages.pages,
            'per_page': messages.per_page,
            'total': messages.total,
            'has_next': messages.has_next,
            'has_prev': messages.has_prev
        },
        'unread_count': Message.query.filter_by(
            recipient_id=current_user.id,
            read_at=None
        ).count() if message_type == 'received' else 0
    })

@bp.route('/messages/<int:id>')
@login_required
def message_detail(id):
    """Detail zprávy."""
    message = Message.query.get_or_404(id)
    
    # Kontrola oprávnění
    if (message.recipient_id != current_user.id and 
        message.sender_id != current_user.id and
        not current_user.is_administrator()):
        return jsonify({'error': 'Nemáte oprávnění'}), 403
    
    # Označení jako přečtené
    if message.recipient_id == current_user.id and not message.is_read():
        message.mark_as_read()
    
    return jsonify({
        'id': message.id,
        'subject': message.subject,
        'body': message.body,
        'priority': message.priority,
        'is_read': message.is_read(),
        'is_broadcast': message.is_broadcast,
        'sender': {
            'id': message.sender.id,
            'name': message.sender.get_full_name()
        },
        'recipient': {
            'id': message.recipient.id,
            'name': message.recipient.get_full_name()
        } if message.recipient else None,
        'created_at': message.created_at.isoformat(),
        'read_at': message.read_at.isoformat() if message.read_at else None
    })