import json
from app import app, db
from config import wrapper
from datetime import datetime

# TODO: need to work on try catch HTTP error

# will need to implement a search bar...
def search_games(query, page):
    gamelist = []
    byte_array = wrapper.api_request(
        'games',
        f'fields id,name,url,cover.image_id,first_release_date; \
        where name ~ *"{query}"*;sort rating desc;'
    )
    response = json.loads(byte_array.decode('utf-8'))

    for game in response:
        gamedict = {}
        gamedict['id'] = game['id']
        gamedict['name'] = game['name']

        from app.models import Game
        game_obj = Game(id=gamedict['id'], name=gamedict['name'])
        if db.session.get(Game, gamedict['id']) is None:
            db.session.add(game_obj)
            db.session.commit()

        gamedict['igdb_url'] = game['url']
        if game.get('cover'):
            #t_cover_small or t_thumb?
            gamedict['image_url'] = f"https://images.igdb.com/igdb/image/upload/t_thumb/{game['cover']['image_id']}.jpg"
        else:
            gamedict['image_url'] = "https://images.igdb.com/igdb/image/upload/t_thumb/nocover.jpg"
        if game.get('first_release_date'):
            gamedict['release_year'] = datetime.fromtimestamp(game['first_release_date']).year
        else:
            gamedict['release_year'] = "Unknown Release Date"
        gamelist.append(gamedict)
    
    # for pagination
    return gamelist[(page - 1) * app.config["POSTS_PER_PAGE"]: page * app.config["POSTS_PER_PAGE"]], len(gamelist)

def get_game_name_from_id(id):
    byte_array = wrapper.api_request(
        'games',
        f'fields name; where id = {id};'
    )

    response = json.loads(byte_array.decode('utf-8'))

    game_name = response[0]['name']
    return game_name

#print(get_game_name_from_id(500))
