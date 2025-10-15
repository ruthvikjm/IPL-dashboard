from django.shortcuts import render
from django.db.models import Count, Sum
from .models import Match, Delivery
import json


def get_matches_per_year():
    matches_per_year = Match.objects.values('season') .annotate(count=Count('id')) .order_by('season')
    return list(matches_per_year)


def get_team_wins_per_year():
    years = [m['season'] for m in get_matches_per_year()]
    teams = Match.objects.values_list('winner', flat=True).distinct()

    team_wins_data = []
    for team in teams:
        wins_per_year = [Match.objects.filter(season=year, winner=team).count() for year in years]
        team_wins_data.append({'team': team, 'wins': wins_per_year})

    return years, team_wins_data


def get_yearly_stats(year):
    """Return extra runs, top economical bowlers, and team stats for a given year."""
    deliveries = Delivery.objects.filter(match__season=year)

    extra_data = list(
        deliveries.values('bowling_team')
                  .annotate(extra=Sum('extra_runs'))
                  .order_by('bowling_team')
    )

    economy_data = []
    bowler_stats = deliveries.values('bowler') \
                             .annotate(runs=Sum('total_runs'), balls=Count('id'))
    for stat in bowler_stats:
        balls = stat['balls'] or 0
        if balls >= 6:
            economy = stat['runs'] / (balls / 6)
            economy_data.append({
                'bowler': stat['bowler'],
                'runs': stat['runs'],
                'balls': balls,
                'economy': economy
            })
    economy_data = sorted(economy_data, key=lambda x: x['economy'])[:10]

    matches = Match.objects.filter(season=year)
    teams_set = set(list(matches.values_list('team1', flat=True)) +
                    list(matches.values_list('team2', flat=True)))

    played_vs_won = []
    for team in teams_set:
        played = matches.filter(team1=team).count() + matches.filter(team2=team).count()
        won = matches.filter(winner=team).count()
        played_vs_won.append({'team': team, 'played': played, 'won': won})

    return extra_data, economy_data, played_vs_won


def landing(request):
    """Render the main landing page with IPL stats."""
    task1_list = get_matches_per_year()
    years, task2_list = get_team_wins_per_year()

    selected_year = request.GET.get('year')
    extra_data, economy_data, played_data = [], [], []

    if selected_year:
        try:
            year = int(selected_year)
            extra_data, economy_data, played_data = get_yearly_stats(year)
        except ValueError:
            selected_year = None

    context = {
        'years': years,
        'selected_year': int(selected_year) if selected_year else None,
        'task1_json': json.dumps(task1_list),
        'task2_json': json.dumps(task2_list),
        'extra_json': json.dumps(extra_data),
        'econ_json': json.dumps(economy_data),
        'played_json': json.dumps(played_data),
    }

    return render(request, 'landing.html', context)
