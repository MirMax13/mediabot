"""Centralized mappings for media category and subtype handling."""

MAIN_MEDIA_OPTIONS = ['Фільми', 'Серіали', 'Аніме', 'Мультфільми', 'Усе']

SUBMEDIA_OPTIONS_BY_MEDIA = {
    'аніме': ['Аніме фільми', 'Аніме серіали', 'Усе аніме'],
    'мультфільми': ['Мультфільми', 'Мультсеріали', 'Усе мультики'],
}

MEDIA_SELECTION_TO_MOVIE_TYPE = {
    'фільми': 'film',
    'серіали': 'series',
    'усе': 'media',
}

SUBMEDIA_SELECTION_TO_MOVIE_TYPE = {
    'аніме_фільми': 'anime_movie',
    'аніме_серіали': 'anime_series',
    'усе_аніме': 'anime',
    'мультфільми': 'animated_movie',
    'мультсеріали': 'animated_series',
    'усе_мультики': 'animated',
    'усе': 'media',
}

LIST_MESSAGE_TO_MEDIA_TYPE = {
    'ігри': 'game',
    'книги': 'book',
}

DIRECT_FILM_TYPES = {
    'film',
    'anime_series',
    'anime_movie',
    'series',
    'animated_series',
    'animated_movie',
}

GROUPED_FILM_TYPES = {
    'anime': ['anime_series', 'anime_movie'],
    'animated': ['animated_series', 'animated_movie'],
}

SERIES_TYPES = {'series', 'anime_series', 'animated_series'}