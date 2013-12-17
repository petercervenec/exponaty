# coding = utf-8

from pkg.general import Exhibit, Level

"""
Settings of exhibit levels.
exhibit: list of items of type Exhibit, each of them containing appropriate
level info (see Exhibit)
"""

EXHIBITS = [
    Exhibit(name='elektrostroj', id=82, levels=[
        Level(name='10s', params={'game_time': 10}),
        Level(name='30s', params={'game_time': 30}),
        Level(name='60s', params={'game_time': 60}),
    ]),
    Exhibit(name='reakcia_pyramida', id=89, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='reakcia_bubon', id=90, levels=[
        Level(name='10s', params={'game_time': 10}),
        Level(name='30s', params={'game_time': 30}),
        Level(name='60s', params={'game_time': 60}),
    ]),
    Exhibit(name='sluch_klavir', id=91, levels=[
        Level(name='span1', params={'span': 1}),
        Level(name='span2', params={'span': 2}),
        Level(name='span3', params={'span': 3}),
    ]),
    Exhibit(name='postreh_32', id=98, levels=[
        Level(name='10s', params={'game_time': 10}),
        Level(name='30s', params={'game_time': 30}),
        Level(name='60s', params={'game_time': 60}),
    ]),
    Exhibit(name='presnost_pohyb_ruky', id=99, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='frekvencia_stlacania', id=100, levels=[
        Level(name='10s', params={'game_time': 10}),
        Level(name='20s', params={'game_time': 20}),
        Level(name='30s', params={'game_time': 30}),
    ]),
    Exhibit(name='rozpatie_ruk_a_vyska_vyskoku', id=101, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='reakcia_standard', id=102, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='citlivost_sluchu', id=104, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='sila_hlasu', id=105, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='zvukove_pexeso', id=107, levels=[
        Level(name='default', params={}),
    ]),
    Exhibit(name='test', id='Test', levels=[
        Level(name='default', params={}),
        Level(name='82', params={}),
        Level(name='89', params={}),
        Level(name='90', params={}),
        Level(name='91', params={}),
        Level(name='98', params={}),
        Level(name='99', params={}),
        Level(name='100', params={}),
        Level(name='101', params={}),
        Level(name='102', params={}),
        Level(name='104', params={}),
        Level(name='105', params={}),
        Level(name='107', params={}),
    ]),
]
