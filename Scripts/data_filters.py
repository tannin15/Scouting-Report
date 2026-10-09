"""Simple Statcast filters for the pitcher scouting report.

Run add_game_context() on the full-season pitch data first. Use the resulting
columns to build the dropdowns, then filter before making report tables/plots.
"""

import pandas as pd


def add_game_context(pitch_data):
    """Identify pitching team, opposing team, and home/road for each pitch."""
    required = ['inning_topbot', 'home_team', 'away_team']
    for column in required:
        if column not in pitch_data.columns:
            raise ValueError(f'Missing Statcast column: {column}')

    data = pitch_data.copy()
    inning_half = data['inning_topbot'].astype('string').str.strip().str.lower()
    home = data['home_team'].astype('string').str.strip().str.upper()
    away = data['away_team'].astype('string').str.strip().str.upper()

    top = inning_half == 'top'
    bottom = inning_half.isin(['bot', 'bottom'])

    # Start with missing values; only fill rows where the inning half is known.
    data['pitcher_team'] = pd.Series(pd.NA, index=data.index, dtype='string')
    data['opponent_team'] = pd.Series(pd.NA, index=data.index, dtype='string')
    data['pitcher_location'] = pd.Series(pd.NA, index=data.index, dtype='string')

    data.loc[top, 'pitcher_team'] = home[top]
    data.loc[top, 'opponent_team'] = away[top]
    data.loc[top, 'pitcher_location'] = 'Home'

    data.loc[bottom, 'pitcher_team'] = away[bottom]
    data.loc[bottom, 'opponent_team'] = home[bottom]
    data.loc[bottom, 'pitcher_location'] = 'Road'

    return data


def pitching_teams(data):
    """Find pitching teams from the entire season (before applying filters)."""
    return sorted(data['pitcher_team'].dropna().unique().tolist())


def opposing_teams(data):
    """Find opponents represented in the selected pitch data."""
    return sorted(data['opponent_team'].dropna().unique().tolist())


def has_multiple_pitching_teams(data):
    return len(pitching_teams(data)) > 1


def filter_pitch_data(data, pitching_team='ALL', opponent='ALL', location='ALL'):
    """Filter already-enriched pitch data without modifying the original."""
    filtered = data.copy()

    if pitching_team and pitching_team.upper() != 'ALL':
        filtered = filtered[filtered['pitcher_team'] == pitching_team.upper()]

    if opponent and opponent.upper() != 'ALL':
        filtered = filtered[filtered['opponent_team'] == opponent.upper()]

    if location and location.upper() != 'ALL':
        location = location.title()
        if location not in ('Home', 'Road'):
            raise ValueError('location must be ALL, Home, or Road')
        filtered = filtered[filtered['pitcher_location'] == location]

    return filtered.copy()


def filter_by_opponent(data, opponent=None):
    """Compatibility helper for the earlier opponent-only implementation."""
    if data is None or opponent is None or opponent.upper() == 'ALL':
        return data
    if 'opponent_team' not in data.columns:
        data = add_game_context(data)
    return filter_pitch_data(data, opponent=opponent)
