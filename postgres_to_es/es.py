"""ES related functions: create index, create doc."""
from __future__ import annotations

from typing import List, Optional

from db_queries import SELECT_UPDATED_FILMWORKS
from pydantic import BaseModel, Field

ES_INDEX_NAME = 'movies'


def es_create_index(client):
    """Create an index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index=ES_INDEX_NAME,
        body={
            'settings': {
                'refresh_interval': '1s',
                'analysis': {
                    'filter': {
                        'english_stop': {
                            'type': 'stop',
                            'stopwords': '_english_',
                        },
                        'english_stemmer': {
                            'type': 'stemmer',
                            'language': 'english',
                        },
                        'english_possessive_stemmer': {
                            'type': 'stemmer',
                            'language': 'possessive_english',
                        },
                        'russian_stop': {
                            'type': 'stop',
                            'stopwords': '_russian_',
                        },
                        'russian_stemmer': {
                            'type': 'stemmer',
                            'language': 'russian',
                        },
                    },
                    'analyzer': {
                        'ru_en': {
                            'tokenizer': 'standard',
                            'filter': [
                                'lowercase',
                                'english_stop',
                                'english_stemmer',
                                'english_possessive_stemmer',
                                'russian_stop',
                                'russian_stemmer',
                            ],
                        },
                    },
                },
            },
            'mappings': {
                'dynamic': 'strict',
                'properties': {
                    'id': {
                        'type': 'keyword',
                    },
                    'imdb_rating': {
                        'type': 'float',
                    },
                    'genre': {
                        'type': 'keyword',
                    },
                    'title': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                        'fields': {
                            'raw': {
                                'type': 'keyword',
                            },
                        },
                    },
                    'description': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                    'director': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                    'actors_names': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                    'writers_names': {
                        'type': 'text',
                        'analyzer': 'ru_en',
                    },
                    'actors': {
                        'type': 'nested',
                        'dynamic': 'strict',
                        'properties': {
                            'id': {
                                'type': 'keyword',
                            },
                            'name': {
                                'type': 'text',
                                'analyzer': 'ru_en',
                            },
                        },
                    },
                    'writers': {
                        'type': 'nested',
                        'dynamic': 'strict',
                        'properties': {
                            'id': {
                                'type': 'keyword',
                            },
                            'name': {
                                'type': 'text',
                                'analyzer': 'ru_en',
                            },
                        },
                    },
                },
            },
        },
        ignore=400,
    )

class Person(BaseModel):
    id: str
    name: str

class EsDoc(BaseModel):
    id: str
    underscore_id: str = Field(alias='_id')
    imdb_rating: Optional[float] = None
    genre: Optional[List[str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    director: Optional[List[str]] = None
    actors_names: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    actors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None


def validate_row_create_es_doc(row):
    """Convert one row from PG to create a doc for ES."""

    def _dict_from_str(string):
        return {
            'id': (string.split(':::'))[0],
            'role': (string.split(':::'))[1],
            'name': (string.split(':::'))[2],
        }

    if row['persons'][0] is not None:
        persons = [_dict_from_str(p) for p in row['persons']]
        directors = [Person(id=p['id'], name=p['name']) for p in persons if p['role'] == 'director']
        actors = [Person(id=p['id'], name=p['name']) for p in persons if p['role'] == 'actor']
        writers = [Person(id=p['id'], name=p['name']) for p in persons if p['role'] == 'writer']
    else:
        directors, actors, writers = [], [], []

    return EsDoc(
        id=row['id'],
        _id=row['id'],
        imdb_rating=row['imdb_rating'],
        genre=row['genre'],
        title=row['title'],
        description=row['description'],
        director=[p.name for p in directors],
        actors_names=[p.name for p in actors],
        writers_names=[p.name for p in writers],
        actors=actors,
        writers=writers,
    ).dict(by_alias=True)


def generate_actions(pg_cursor, last_successful_load):
    """Collect data on updated filmworks and generate ES actions"""

    # Select entities that have changed since LSL.
    # TODO: refactor query to be more efficient
    pg_cursor.execute(SELECT_UPDATED_FILMWORKS.format(last_successful_load))
    for row in pg_cursor:
        yield validate_row_create_es_doc(row)
