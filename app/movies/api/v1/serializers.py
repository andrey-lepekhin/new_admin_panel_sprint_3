from movies.models import Filmwork, Genre, GenreFilmwork, PersonFilmwork
from rest_framework import serializers


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class PersonFilmworkSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='person.full_name')

    class Meta:
        model = PersonFilmwork
        fields = [
            'role',
            'full_name'
            ]


class GenreFilmworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = GenreFilmwork
        fields = ['name']


class FilmworkSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    persons_roles = PersonFilmworkSerializer(source='personfilmwork_set', many=True)

    def to_representation(self, instance):
        """
        Make output conform to schema in openapi.yaml.
        """
        representation = super().to_representation(instance)

        # Create and fill actors, directors, writers nodes
        for role in PersonFilmwork.RoleChoices:
            representation['{}s'.format(role)] = []

        for person_role in representation['persons_roles']:
            if person_role['role'] in PersonFilmwork.RoleChoices:
                representation['{}s'.format(person_role['role'])].append(person_role['full_name'])
        del representation['persons_roles']

        # Explode genres
        representation['genres'] = [genre['name'] for genre in representation['genres']]

        return representation

    class Meta:
        model = Filmwork
        # depth = 1
        fields = [
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            'genres',
            'persons_roles',
        ]
