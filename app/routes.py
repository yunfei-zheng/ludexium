from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from requests import HTTPError
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, \
    PostForm, ResetPasswordRequestForm, ResetPasswordForm, SearchForm
from app.models import User, Post, Game
from app.email import send_password_reset_email
from app.games import search_games

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form, posts=posts.items, 
                           next_url=next_url, prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        g.search_form = SearchForm()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are no longer following {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('explore'))

    page = request.args.get('page', 1, type=int)
    search_query = g.search_form.q.data
    try:
        games, total = search_games(search_query, page)
    except HTTPError:
        return render_template('500.html')

    # bad lol
    global current_url
    current_url = url_for('search', q=g.search_form.q.data, page=page)
    
    next_url = url_for('search', q=g.search_form.q.data, page=page + 1) \
        if total > page * app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    form = EmptyForm()
    return render_template('search.html', title='Search', games=games, next_url=next_url, prev_url=prev_url, form=form)

# @app.route('/play/<game_id>', methods=['POST'])
# @login_required
# def play(game_id):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         game = db.session.scalar(
#             sa.select(Game).where(Game.id == game_id))
#         if game is None:
#             flash(f'Game {game.name} not found.')
#             return redirect(url_for('index'))
#         if current_user.is_playing(game):
#             flash('You are already playing this game!')
#             return redirect(current_url)
#         current_user.start_playing(game)
#         db.session.commit()
#         flash(f'You have added {game.name} to your Played List!')
#         return redirect(current_url)
#     else:
#         return redirect(url_for('index'))
@app.route('/play/<game_id>', methods=['POST'])
@login_required
def play(game_id):
    # Fetch the game from the database
    game = db.session.scalar(
        sa.select(Game).where(Game.id == game_id)
    )
    if game is None:
        flash('Game not found.')
        return jsonify(success=False, message="Game not found"), 404

    # Check if the user is already playing the game
    if current_user.is_playing(game):
        flash('You are already playing this game!')
        return jsonify(success=False, message="Game is already not being played"), 400

    # Add the game to the user's played list
    #flash(f'You have added {game.name} to your Played List!', 'success')
    current_user.start_playing(game)
    db.session.commit()
    return jsonify(success=True, message=f'You have added {game.name} to your Played List!')

# @app.route('/unplay/<game_id>', methods=['POST'])
# @login_required
# def unplay(game_id):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         game = db.session.scalar(
#             sa.select(Game).where(Game.id == game_id))
#         if game is None:
#             flash(f'Game {game.name} not found.')
#             return redirect(url_for('index'))
#         if not current_user.is_playing(game):
#             flash('You are already not playing this game!')
#             return redirect(current_url)
#         current_user.stop_playing(game)
#         db.session.commit()
#         flash(f'You have removed {game.name} from your Played List!')
#         return redirect(current_url)
#     else:
#         return redirect(url_for('index'))
@app.route('/unplay/<game_id>', methods=['POST'])
@login_required
def unplay(game_id):
    game = db.session.scalar(
        sa.select(Game).where(Game.id == game_id)
    )
    if game is None:
        return jsonify(success=False, message="Game not found"), 404

    if not current_user.is_playing(game):
        return jsonify(success=False, message="Game is already not being played"), 400

    #flash(f'You have removed {game.name} to your Played List!', 'success')
    current_user.stop_playing(game)
    db.session.commit()
    return jsonify(success=True, message=f'You have removed {game.name} to your Played List!')

@app.route('/my_games/<username>')
@login_required
def my_games(username):
    form = EmptyForm()
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('my_games.html', user=user)