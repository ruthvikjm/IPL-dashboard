import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipl_api.settings')
django.setup()

from matches.models import Match, Delivery

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHES_CSV = os.path.join(BASE_DIR, "data", "matches.csv")
DELIVERIES_CSV = os.path.join(BASE_DIR, "data", "deliveries.csv")

def load_matches(csv_file=MATCHES_CSV):
    df = pd.read_csv(csv_file)
    match_objs = [
        Match(
            id=row['id'],
            season=row['season'],
            city=row.get('city'),
            date=pd.to_datetime(row['date']).date() if pd.notnull(row['date']) else None,
            team1=row['team1'],
            team2=row['team2'],
            toss_winner=row.get('toss_winner'),
            toss_decision=row.get('toss_decision'),
            result=row.get('result'),
            winner=row.get('winner'),
            win_by_runs=row.get('win_by_runs', 0),
            win_by_wickets=row.get('win_by_wickets', 0),
            player_of_match=row.get('player_of_match'),
            venue=row.get('venue'),
            umpire1=row.get('umpire1'),
            umpire2=row.get('umpire2'),
            umpire3=row.get('umpire3')
        )
        for row in df.to_dict('records')
    ]
    Match.objects.bulk_create(match_objs, ignore_conflicts=True)
    print(f"{Match.objects.count()} matches loaded.")

def load_deliveries(csv_file=DELIVERIES_CSV):
    df = pd.read_csv(csv_file)
    match_map = {m.id: m for m in Match.objects.all()}
    delivery_objs = []
    for row in df.to_dict('records'):
        match = match_map.get(row['match_id'])
        if not match:
            continue
        delivery_objs.append(Delivery(
            match=match,
            inning=row.get('inning'),
            batting_team=row.get('batting_team'),
            bowling_team=row.get('bowling_team'),
            over=row.get('over'),
            ball=row.get('ball'),
            batsman=row.get('batsman'),
            non_striker=row.get('non_striker'),
            bowler=row.get('bowler'),
            is_super_over=row.get('is_super_over', 0),
            wide_runs=row.get('wide_runs', 0),
            bye_runs=row.get('bye_runs', 0),
            legbye_runs=row.get('legbye_runs', 0),
            noball_runs=row.get('noball_runs', 0),
            penalty_runs=row.get('penalty_runs', 0),
            batsman_runs=row.get('batsman_runs', 0),
            extra_runs=row.get('extra_runs', 0),
            total_runs=row.get('total_runs', 0),
            player_dismissed=row.get('player_dismissed'),
            dismissal_kind=row.get('dismissal_kind'),
            fielder=row.get('fielder')
        ))
    Delivery.objects.bulk_create(delivery_objs, ignore_conflicts=True)
    print(f"{Delivery.objects.count()} deliveries loaded.")

if __name__ == "__main__":
    load_matches()
    load_deliveries()
