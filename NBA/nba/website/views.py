from django.http import HttpResponse  
from django.views.generic import CreateView  
from django.shortcuts import render
from django import forms
import json
import traceback
from io import StringIO
import sqlite3
import sys
import csv
import os
from operator import and_
from functools import reduce
from website.searches import query, get_select, get_from, get_join, get_on, get_where, \
get_ratios, get_header, clean_header

CALL_ACCURACY = [
    ('', '----'),
    ('CC', 'CC'),
    ('CNC', 'CNC'),
    ('IC', 'IC'),
    ('INC', 'INC'),
]

class SearchForm(forms.Form):
    '''
    Creates the form using the SQL database to grab the unique choices for 
    the choice fields.
    '''

    context = {}
    empty_choice = [('', '---------')]
    DATA_DIR = os.path.dirname(__file__)
    DATABASE_FILENAME = os.path.join(DATA_DIR, 'NBARefs.db')
    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()

    #Queries to grab the options in the drag down list
    ref_query = "SELECT DISTINCT referee_name, referee_name FROM referees JOIN calls \
        on referees.game_code = calls.game_code;"
    committing_player_query = "SELECT DISTINCT committing_player, committing_player \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    disadvantaged_player_query = "SELECT DISTINCT disadvantaged_player, disadvantaged_player \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    call_type_query = "SELECT DISTINCT call_type, call_type \
        FROM referees JOIN calls on referees.game_code = calls.game_code;" 
    home_team_query = "SELECT DISTINCT home_team, home_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    away_team_query = "SELECT DISTINCT away_team, away_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    offending_team_query = "SELECT DISTINCT offending_team, offending_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"
    defending_team_query = "SELECT DISTINCT defending_team, defending_team \
        FROM referees JOIN calls on referees.game_code = calls.game_code;"

    #Executes the SQL queries and saves the output, as well as removing some bug cases
    c.execute(ref_query)
    REFS = c.fetchall()
    c.execute(committing_player_query)
    COMMITTING_PLAYER = c.fetchall()
    COMMITTING_PLAYER.remove(('', ''))
    COMMITTING_PLAYER.remove((',', ','))
    c.execute(disadvantaged_player_query)
    DISADVANTAGED_PLAYER = c.fetchall()
    DISADVANTAGED_PLAYER.remove(('', ''))
    DISADVANTAGED_PLAYER.remove((',', ','))
    c.execute(call_type_query)
    CALL_TYPE = c.fetchall()
    c.execute(home_team_query)
    HOME_TEAM = c.fetchall()
    c.execute(away_team_query)
    AWAY_TEAM = c.fetchall()
    c.execute(offending_team_query)
    OFFENDING_TEAM = c.fetchall()
    OFFENDING_TEAM.remove(('', ''))
    c.execute(defending_team_query)
    DEFENDING_TEAM = c.fetchall()

    #Adds the option of an empty choice
    REFS =  empty_choice + REFS
    COMMITTING_PLAYER = empty_choice + COMMITTING_PLAYER
    CALL_TYPE = empty_choice + CALL_TYPE
    DISADVANTAGED_PLAYER = empty_choice + DISADVANTAGED_PLAYER
    HOME_TEAM = empty_choice + HOME_TEAM
    AWAY_TEAM = empty_choice + AWAY_TEAM
    OFFENDING_TEAM = empty_choice + OFFENDING_TEAM
    DEFENDING_TEAM = empty_choice + DEFENDING_TEAM

    #Creates the fields for the search function
    refs1 = forms.ChoiceField(label= 'Referee 1', choices=REFS, required=False)
    refs2 = forms.ChoiceField(label= 'Referee 2', choices=REFS, required=False)
    refs3 = forms.ChoiceField(label= 'Referee 3', choices=REFS, required=False)
    committing_player = forms.ChoiceField(label= 'Committing Player', \
        choices=COMMITTING_PLAYER, required=False)   
    disadvantaged_player = forms.ChoiceField(label= 'Disadvantaged Player', \
        choices=DISADVANTAGED_PLAYER, required=False) 
    call_type = forms.ChoiceField(label= 'Call Type', \
        choices=CALL_TYPE, required=False) 
    call_accuracy = forms.ChoiceField(label= 'Call Accuracy', \
        choices=CALL_ACCURACY, required=False) 
    home_team = forms.ChoiceField(label= 'Home Team', choices=HOME_TEAM, required=False)
    away_team = forms.ChoiceField(label= 'Away Team', choices=AWAY_TEAM, required=False)
    offending_team = forms.ChoiceField(label= 'Offending Team', choices=OFFENDING_TEAM, required=False)
    defending_team = forms.ChoiceField(label= 'Defending Team', choices=DEFENDING_TEAM, required=False)
    comment = forms.BooleanField(required=False, label="Check this for comments")

def home(request):
    '''
    This handles the homepage of the website and directs the user
    to either the search or statistics page.
    '''
    return render(request, 'website/home.html')

def search(request):
    '''
    This function creates a dictionary from the inputs (GET) and then returns a list
    of the incorrect call/non-call ratios and a list of the specified calls based
    off the input criteria. The template is under website/search.html
    '''

    column_dictionary = {'game_name': 'Game Name', 'game_code': 'Game Code', \
    'home_team': 'Home Team', 'away_team': 'Away Team', 'time': 'Time', 'period': \
    'Period', 'call_type': 'Call Type', 'committing_player': 'Committing Player',\
    'offending_team': 'Offending Team', 'disadvantaged_player': 'Disadvantaged Player', \
    'defending_team': 'Defending Team', 'call_accuracy': 'Call Accuracy', \
    'referee_name': 'Referee Name'}
    
    context = {}
    res = None
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            args = {}

            if form.cleaned_data['comment']:
                args['comment'] = form.cleaned_data['comment']
            if form.cleaned_data['refs1']:
                args['refs1'] = form.cleaned_data['refs1']
            if form.cleaned_data['refs1']:
                args['refs2'] = form.cleaned_data['refs2']
            if form.cleaned_data['refs1']:
                args['refs3'] = form.cleaned_data['refs3']
            if form.cleaned_data['committing_player']:
                args['committing_player'] = form.cleaned_data['committing_player']
            if form.cleaned_data['disadvantaged_player']:
                args['disadvantaged_player'] = form.cleaned_data['disadvantaged_player']
            if form.cleaned_data['call_type']:
                args['call_type'] = form.cleaned_data['call_type']
            if form.cleaned_data['call_accuracy']:
                args['call_accuracy'] = form.cleaned_data['call_accuracy']
            if form.cleaned_data['home_team']:
                args['home_team'] = form.cleaned_data['home_team']
            if form.cleaned_data['away_team']:
                args['away_team'] = form.cleaned_data['away_team']
            if form.cleaned_data['offending_team']:
                args['offending_team'] = form.cleaned_data['offending_team']
            if form.cleaned_data['defending_team']:
                args['defending_team'] = form.cleaned_data['defending_team']
            try:
                DATA_DIR = os.path.dirname(__file__)
                DATABASE_FILENAME = os.path.join(DATA_DIR, 'NBARefs.db')
                res = query(DATABASE_FILENAME, args)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in find_courses:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
            
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
        cols = None
    else:
        call_ratio = res[0]
        columns, result = res[1]

        call_ratio.append(len(result))

        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        for i, column in enumerate(columns):
            columns[i] = column_dictionary[column]

        ratio_col = ['Incorrect Call Percentage', 'Incorrect Non-Call Percentage', \
        'Total Incorrect Percentage', 'Total Calls']

        context['ratios'] = call_ratio
        context['ratio_col'] = ratio_col
        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = columns

    context['form'] = form
    return render(request, 'website/search.html', context)

def stats(request):
    '''
    This function creates the stats homepage that allows the user to navigate to
    a specific statistical portion of the website.
    '''

    return render(request, 'website/stats.html')

def refstats(request):
    '''
    This handles the page that creates a table for all the refs and their
    respective statistics.
    '''
    context = {}
    DATA_DIR = os.path.dirname(__file__)
    DATABASE_FILENAME = os.path.join(DATA_DIR, 'NBARefs.db')
    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()
    
    stat1_query = "SELECT referee_name, count(case call_accuracy when 'IC' then 1 else \
    null end) AS icc, count(case call_accuracy when 'INC' then 1 else null end) as incc, \
    count(case call_accuracy when 'IC' then 1 else null end) + count(case call_accuracy \
    when 'INC' then 1 else null end) as totali, count(comment) as total, ((count(case call_accuracy \
    when 'IC' then 1 else null end) + count(case call_accuracy when 'INC' then 1 else null \
    end)) * 1.00) / count(comment) AS percentage FROM referees JOIN calls ON \
    referees.game_code = calls.game_code GROUP BY referee_name ORDER BY total DESC;"

    c.execute(stat1_query)
    stat1 = c.fetchall()
    context['stat1'] = stat1

    return render(request, 'website/refstats.html', context)

def playerstats(request):
    '''
    This handles the page that creates 4 tables of players, each dealing with particular 
    statistics of receiving and committing a call/non-call. 
    '''

    context = {}
    DATA_DIR = os.path.dirname(__file__)
    DATABASE_FILENAME = os.path.join(DATA_DIR, 'NBARefs.db')
    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()

    stat2_query = "SELECT disadvantaged_player, count(comment) FROM referees JOIN calls \
    ON referees.game_code = calls.game_code WHERE call_accuracy = 'IC' GROUP BY \
    disadvantaged_player ORDER BY count(comment) DESC limit 15;"

    stat3_query = "SELECT disadvantaged_player, count(calls.game_code) FROM referees \
    JOIN calls ON referees.game_code = calls.game_code WHERE call_accuracy = 'CC' AND \
    call_type = 'Foul: Personal'GROUP BY disadvantaged_player ORDER BY count(comment) \
    DESC limit 15;"

    stat4_query = "SELECT committing_player, count(comment) FROM referees JOIN calls ON \
    referees.game_code = calls.game_code WHERE call_accuracy = 'INC' GROUP BY \
    disadvantaged_player ORDER BY count(comment) DESC limit 15;"

    stat5_query = "SELECT committing_player, count(comment) FROM referees JOIN calls ON \
    referees.game_code = calls.game_code WHERE call_accuracy = 'CC' GROUP BY \
    disadvantaged_player ORDER BY count(comment) DESC limit 20;"

    c.execute(stat2_query)
    stat2 = c.fetchall()
    del stat2[0]
    context['stat2'] = stat2   

    c.execute(stat3_query)
    stat3 = c.fetchall()
    context['stat3'] = stat3     

    c.execute(stat4_query)
    stat4 = c.fetchall()
    del stat4[0]
    context['stat4'] = stat4 

    c.execute(stat5_query)
    stat5 = c.fetchall()
    del stat5[0]
    context['stat5'] = stat5

    return render(request, 'website/playerstats.html', context)

def statspdf(request):
    '''
    This handles the page the holds the pdf of the analysis done on the data.
    '''

    DATA_DIR = os.path.dirname(__file__)
    DATABASE_FILENAME = os.path.join(DATA_DIR, 'NBARefereeing.pdf')

    with open(DATABASE_FILENAME, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
    
    return response
    