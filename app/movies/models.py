import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CreatedAtMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        abstract = True


class UpdatedAtMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    name = models.CharField(_('genre name'), max_length=255)
    description = models.TextField(_('genre description'), null=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class Person(UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    full_name = models.CharField(_('person full name'), max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, CreatedAtMixin, UpdatedAtMixin):

    class Filmwork_type(models.TextChoices):
        MOVIE = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('TV Show')

    type = models.TextField(
        _('Filmwork type'),
        choices=Filmwork_type.choices,
        null=True,
    )

    title = models.CharField(_('Filmwork title'), max_length=255)
    description = models.TextField(_('Filmwork description'), null=True)
    creation_date = models.DateTimeField(_('Filmwork creation date'), null=True)
    rating = models.FloatField(
        _('Filmwork rating'),
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    # Параметр upload_to указывает, в какой подпапке будут храниться загружемые файлы.
    # Базовая папка указана в файле настроек как MEDIA_ROOT
    # file_path = models.FileField(_('file'), null=True, upload_to='movies/')

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin, CreatedAtMixin, UpdatedAtMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE, verbose_name=_('Filmwork'))
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, verbose_name=_('Genre'))

    class Meta:
        db_table = 'content"."genre_film_work'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        constraints = [
            models.UniqueConstraint(fields=['film_work_id', 'genre_id'], name='unique genre for filmwork')
        ]


class PersonFilmwork(UUIDMixin, CreatedAtMixin, UpdatedAtMixin):

    class RoleChoices(models.TextChoices):
        ACTOR = 'actor', _('actor')
        DIRECTOR = 'director', _('director')
        WRITER = 'writer', _('writer')

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE, verbose_name=_('Filmwork'))
    person = models.ForeignKey('Person', on_delete=models.CASCADE, verbose_name=_('Person'))
    role = models.TextField(_('PersonFilwork role'), null=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['film_work_id', 'person_id', 'role'],
        #         name='unique filmwork and role for person',
        #     ),
        # ]
