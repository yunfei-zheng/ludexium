import json
from app import app, db
from app.models import Game
from config import wrapper
from datetime import datetime

def search_games(query, page):
    gamelist = []
    byte_array = wrapper.api_request(
        'games',
        f'fields id,name,url,cover.image_id,first_release_date; \
        search "{query}";limit 500;'
    )
    response = json.loads(byte_array.decode('utf-8'))

    for gamejson in response:
        
        game = Game(id=gamejson['id'], name=gamejson['name'], igdb_url=gamejson['url'])
        if db.session.get(Game, gamejson['id']) is None:
            db.session.add(game)
            db.session.commit()

        if gamejson.get('cover'):
            #sizes: t_cover_small or t_thumb?
            game.image_url = f"https://images.igdb.com/igdb/image/upload/t_thumb/{gamejson['cover']['image_id']}.jpg"
        if gamejson.get('first_release_date'):
            game.release_year = datetime.fromtimestamp(gamejson['first_release_date']).year
        gamelist.append(game)
    
    # for pagination
    return gamelist[(page - 1) * app.config["POSTS_PER_PAGE"]: page * app.config["POSTS_PER_PAGE"]], len(gamelist)
