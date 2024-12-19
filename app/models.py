from datetime import datetime, timezone
from time import time
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db, login

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)

class Play(db.Model):
    __tablename__ = 'played_games'

    # Composite primary key
    player_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
    game_id: so.Mapped[int] = so.mapped_column(sa.Integer, sa.ForeignKey('game.id'), primary_key=True)

    # Additional fields
    #hours_played = so.mapped_column(sa.Float, default=0.0)

    # Relationships to User and Game models
    user: so.Mapped['User'] = so.relationship('User', back_populates='played_games')
    game: so.Mapped['Game'] = so.relationship('Game', back_populates='players')

    def __repr__(self):
        return f"<Play(user_id={self.player_id}, game_id={self.game_id}, hours_played={self.hours_played})>"

class Game(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True, unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(256))
    igdb_url: so.Mapped[str] = so.mapped_column(sa.String(256))
    image_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    release_year: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer)

    players: so.WriteOnlyMapped[Play] = so.relationship('Play', back_populates='game', lazy='dynamic')
    
    def __repr__(self):
        return '{}'.format(self.name)
    
    def players_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.players.select().subquery())
        return db.session.scalar(query)

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    played_games: so.WriteOnlyMapped[Play] = so.relationship('Play', back_populates='user', lazy='dynamic')

    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
    
    def start_playing(self, game):
        if not self.is_playing(game):
            play = Play(player_id=self.id, game_id=game.id)
            self.played_games.add(play)

    # needs extra attention ig
    def stop_playing(self, game):
        if self.is_playing(game):
            play = db.session.scalar(sa.select(Play).where(Play.player_id == self.id, Play.game_id == game.id))
            self.played_games.remove(play)
            db.session.delete(play)

    def is_playing(self, game):
        query = sa.select(Play).where(Play.player_id == self.id, Play.game_id == game.id)
        return db.session.scalar(query) is not None
    
    def played_games_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.played_games.select().subquery())
        return db.session.scalar(query)
    
    def played_games_list(self):
        query = self.played_games.select()
        #return db.session.scalars(query)
        return [play.game for play in db.session.scalars(query)]

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Post(db.Model):

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)