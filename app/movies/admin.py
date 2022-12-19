from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Genre, Filmwork, GenreFilmwork, Person, PersonFilmwork
from django.forms import Textarea
from django.db import models


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ['full_name']


class RatingRangeListFilter(admin.SimpleListFilter):
    # Чтобы не было перечисления всех возможных значений рейтинга,
    # этот класс создаёт фильтр, который помогает раскладывать значения рейтинга
    # по "корзинам": "от 0 до 10", "от 10 до 20" и т.п.
    title = _('Rating range')
    parameter_name = 'rating_range'

    RATING_RANGES = list(zip(
        [x for x in range(0, 91, 10)],
        [x for x in range(10, 101, 10)]
    ))

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        url_and_translation = []
        for rating_start, rating_end in self.RATING_RANGES:
            url_and_translation.append(
                (
                    '{s}-{e}'.format(s=rating_start, e=rating_end),
                    _('between {s} and {e}').format(s=rating_start, e=rating_end),
                ),
            )
        return url_and_translation

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value
        # to decide how to filter the queryset.

        for rating_start, rating_end in self.RATING_RANGES:
            if self.value() == '{s}-{e}'.format(s=rating_start, e=rating_end):
                return queryset.filter(
                    rating__gte=rating_start,
                    rating__lte=rating_end,
                )


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    autocomplete_fields = ['genre']


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ['person']
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmworkInline,
    )
    # Отображение полей в списке
    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
    )

    # Фильтрация в списке
    list_filter = (
        'type',
        'genrefilmwork__genre__name',
        'creation_date',
        RatingRangeListFilter,
    )

    # Поиск по полям
    search_fields = ('title', 'description', 'id')
