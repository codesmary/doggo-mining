from oauthlib.oauth2 import BackendApplicationClient as BAC
from requests_oauthlib import OAuth2Session
import requests
import os
import json
import pprint
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Pet
import sqlite3 as lite
import pandas as pd

engine = create_engine('sqlite:///pets.db')
Base.metadata.bind = engine

class OAuthAPI:
    def __init__(self, key, secret, base_url, token_url):
        self.base_url = base_url
        client = BAC(client_id=key)
        self.oauth = OAuth2Session(client=client)
        self.oauth.fetch_token(token_url=base_url + token_url, client_secret=secret, client_id=key)
    
    def close(self):
        self.oauth.close()

    def get(self, url):
        return self.oauth.get(self.base_url + url).text

class PetAPI(OAuthAPI):
    def __init__(self):
        load_dotenv()

        key = os.getenv("PF_API_KEY")
        secret = os.getenv("PF_API_SECRET")
        super().__init__(key, secret, base_url="https://api.petfinder.com", token_url="/v2/oauth2/token")

    def get_paginated_data(self, endpoint, parameters="", pages=1, limit=100):
        total_pages = None
        for p in range(1, pages + 1):
            response = json.loads(
                self.get(f"/v2/{endpoint}?page={p}&limit={limit}&{parameters}")
            )
            if total_pages is None:
                total_pages = response["pagination"]["total_pages"]
            if p > total_pages:
                break
            for datum in response[endpoint]:
                yield datum

    def get_animals(self, pages=1, limit=100):
        animal_generator = self.get_paginated_data("animals", pages=pages, limit=limit)
        animals = []
        for animal in animal_generator:
            if animal['type'] != "Dog":
                continue

            breeds = animal.get('breeds', {})
            colors = animal.get('colors', {})
            environment_factors = animal.get('environment', {})

            new_animal = {
                'mixed_breed': breeds.get('mixed', 'N/A'),
                'primary_color': colors.get('primary', 'N/A'),
                'secondary_color': colors.get('secondary', 'N/A'),
                'tertiary_color': colors.get('tertiary', 'N/A'),
                'age': animal.get('age', 'N/A'),
                'size': animal.get('size', 'N/A'),
                'gender': animal.get('gender', 'N/A'),
                'coat': animal.get('coat', 'N/A'),
                'good_with_children': environment_factors.get('children', 'N/A'),
                'good_with_other_dogs': environment_factors.get('dogs', 'N/A'),
                'good_with_cats': environment_factors.get('cats', 'N/A'),
                'unknown_breed': breeds.get('unknown', 'N/A'),
                'primary_breed': breeds.get('primary', 'N/A'),
                'secondary_breed': breeds.get('secondary', 'N/A'),
                'tertiary_breed': breeds.get('tertiary', 'N/A')
            }
            animals.append(new_animal)
        return animals

def populate_database(pets):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    meta = MetaData(engine)
    for tbl in reversed(meta.sorted_tables):
        engine.execute(tbl.delete())

    for pet in pets:
        session.add(Pet(
            mixed_breed=pet['mixed_breed'],
            primary_color=pet['primary_color'],
            secondary_color=pet['secondary_color'],
            tertiary_color=pet['tertiary_color'],
            age=pet['age'],
            size=pet['size'],
            gender=pet['gender'],
            coat=pet['coat'],
            good_with_children=pet['good_with_children'],
            good_with_other_dogs=pet['good_with_other_dogs'],
            good_with_cats=pet['good_with_cats'],
            unknown_breed=pet['unknown_breed'],
            primary_breed=pet['primary_breed'],
            secondary_breed=pet['secondary_breed'],
            tertiary_breed=pet['tertiary_breed']
        ))

    session.commit()

def get_posts():
    conn = lite.connect('pets.db')
    print(pd.read_sql_query('SELECT * FROM pet', conn))

def main():
    pet_api = PetAPI()
    pets = pet_api.get_animals(pages=100)
    populate_database(pets)
    pet_api.close()

    get_posts()

if __name__ == "__main__":
    main()

