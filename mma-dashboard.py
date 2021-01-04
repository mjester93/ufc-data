import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

#bismo imports
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.figure import Figure
import seaborn as sns
import statsmodels
from statsmodels.nonparametric.smoothers_lowess import lowess


# ==========================================================================
# -------------------------- CUSTOM FUNCTIONS ------------------------------
# ==========================================================================

def fight_logs(ufcstats_id):
    '''
    This function returns a fight log for a particular fighter
    '''
    
    fight_log = all_fight_data_df.loc[all_fight_data_df["ufcstats_id"] == ufcstats_id]    
    fight_log = fight_log[[
        'event_name', 'event_date', 'weight_class', 'opp_name', 'fighter_odds', 'fighter_winner',
        'round', 'time', 'fight_time_seconds', 'method', 'fighter_new_dk_score', 'fighter_old_dk_score', 
        'fighter_total_knockdowns', 'fighter_total_sig_strikes_landed', 
        'fighter_total_strikes_landed', 'fighter_total_takedowns', 
        'fighter_total_submission_attempts', 'fighter_total_reversals', 'fighter_total_control'
    ]]

    fight_log = fight_log.rename(
        columns={
            'event_name': 'Event',
            'event_date': 'Date',
            'weight_class': 'Weight',
            'opp_name': 'Opponent',
            'fighter_odds': 'Odds',
            'fighter_winner': 'Winner?',
            'round': 'Round',
            'time': 'Time',
            'fight_time_seconds': 'Secs.',
            'method': 'Method',
            'fighter_new_dk_score': 'DK Pts (New)',
            'fighter_old_dk_score': 'DK Pts (Old)',
            'fighter_total_knockdowns': 'KO',
            'fighter_total_sig_strikes_landed': 'Sig. Strikes',
            'fighter_total_strikes_landed': 'Strikes',
            'fighter_total_takedowns': 'TD',
            'fighter_total_submission_attempts': 'Sub Att.',
            'fighter_total_reversals': 'Rev',
            'fighter_total_control': 'Ctrl'   
        }
    )

    return fight_log


def sig_strikes_chart(ufcstats_id, weight_class):
    '''
    This function returns sig strikes chart
    '''

    all_fighter_career_stats = all_career_stats_df.loc[(all_career_stats_df["weight_class"].str.contains(weight_class))]

    sig_strikes = all_fighter_career_stats[[
        'ufcstats_id', 'sig_strikes_landed_per_minute', 'sig_strikes_absorbed_per_minute', 'fight_time_seconds_for'
    ]]

    # removing where fighters have 0 and 0
    sig_strikes = sig_strikes.loc[
        (sig_strikes["sig_strikes_landed_per_minute"] > 0) & 
        (sig_strikes["sig_strikes_absorbed_per_minute"] > 0)
    ].reset_index()

    sig_strikes['color'] = '#BFBFBF'
    sig_strikes.loc[(sig_strikes.ufcstats_id == ufcstats_id), 'color'] = "#990000"
    sig_strikes = sig_strikes.sort_values(by='color', ascending=False)

    ss_fig = Figure()
    ax = ss_fig.subplots()

    sns.scatterplot(
        x = sig_strikes["sig_strikes_landed_per_minute"], 
        y = sig_strikes["sig_strikes_absorbed_per_minute"],
        data = sig_strikes,
        hue = sig_strikes["color"],
        palette = dict({'#BFBFBF': '#BFBFBF', '#990000': '#990000'}),
        s = (sig_strikes["fight_time_seconds_for"] / 15), 
        legend=False,
        ax = ax)

    ax.set_xlabel('Sig. Strikes Landed Per Minute', fontsize=12)
    ax.set_ylabel('Sig. Strikes Absorbed Per Minute', fontsize=12)

    ax.grid(zorder=0,alpha=.2)
    ax.set_axisbelow(True)

    ax.axhline(
        y = sig_strikes["sig_strikes_landed_per_minute"].median(),
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    ax.axvline(
        x = sig_strikes["sig_strikes_absorbed_per_minute"].median(),
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    st.pyplot(ss_fig)


def strikes_chart(ufcstats_id, weight_class):
    '''
    This function returns strikes chart
    '''

    all_fighter_career_stats = all_career_stats_df.loc[(all_career_stats_df["weight_class"].str.contains(weight_class))]

    weight_class_fights = all_fight_data_df.loc[(all_fight_data_df["weight_class"].str.contains(weight_class))]

    average_strikes_landed = round(
        weight_class_fights["fighter_total_strikes_landed"].sum() / weight_class_fights['fight_time_seconds'].sum() * 60, 2)

    strikes = all_fighter_career_stats[[
        'ufcstats_id', 'strikes_landed_per_minute', 'strikes_absorbed_per_minute', 'fight_time_seconds_for'
    ]]

    strikes['color'] = '#BFBFBF'
    strikes.loc[(strikes.ufcstats_id == ufcstats_id), 'color'] = "#990000"
    strikes = strikes.sort_values(by='color', ascending=False)

    s_fig = Figure()
    ax = s_fig.subplots()

    sns.scatterplot(
        x = strikes["strikes_landed_per_minute"], 
        y = strikes["strikes_absorbed_per_minute"],
        data = strikes,
        hue = strikes["color"],
        palette = dict({'#BFBFBF': '#BFBFBF', '#990000': '#990000'}),
        s = (strikes["fight_time_seconds_for"] / 15), 
        legend=False,
        ax = ax)

    ax.set_xlabel('Strikes Landed Per Minute', fontsize=12)
    ax.set_ylabel('Strikes Absorbed Per Minute', fontsize=12)

    ax.grid(zorder=0,alpha=.2)
    ax.set_axisbelow(True)

    ax.axhline(
        y = average_strikes_landed,
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    ax.axvline(
        x = average_strikes_landed,
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    st.pyplot(s_fig)


def control_pct_chart(ufcstats_id, weight_class):
    '''
    This function returns control percentage chart
    '''

    all_fighter_career_stats = all_career_stats_df.loc[(all_career_stats_df["weight_class"].str.contains(weight_class))]
    controls = all_fighter_career_stats[[
        'ufcstats_id', 'control_percentage', 'control_against_percentage', 'fight_time_seconds_for'
    ]]

    controls['color'] = '#BFBFBF'
    controls.loc[(controls.ufcstats_id == ufcstats_id), 'color'] = "#990000"
    controls = controls.sort_values(by='color', ascending=False)

    ctr_fig = Figure()
    ax = ctr_fig.subplots()

    sns.scatterplot(
        x = controls["control_percentage"], 
        y = controls["control_against_percentage"],
        data = controls,
        hue = controls["color"],
        palette = dict({'#BFBFBF': '#BFBFBF', '#990000': '#990000'}),
        s = (controls["fight_time_seconds_for"] / 15), 
        legend=False,
        ax = ax)

    ax.set_xlabel('Control Percentage', fontsize=12)
    ax.set_ylabel('Control Against Percentage', fontsize=12)

    ax.grid(zorder=0,alpha=.2)
    ax.set_axisbelow(True)

    ax.axhline(
        y = controls["control_percentage"].median(),
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    ax.axvline(
        x = controls["control_against_percentage"].median(),
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    st.pyplot(ctr_fig)


def td_chart(ufcstats_id, weight_class):
    all_fighter_career_stats = all_career_stats_df.loc[(all_career_stats_df["weight_class"].str.contains(weight_class))]

    takedowns = all_fighter_career_stats[[
        'ufcstats_id', 'takedown_accuracy', 'takedown_defence', 'fight_time_seconds_for'
    ]]

    # removing where fighters have 0 and 0
    takedowns = takedowns.loc[
        (takedowns["takedown_accuracy"] > 0) & 
        (takedowns["takedown_defence"] > 0)
    ].reset_index()

    takedowns['color'] = '#BFBFBF'
    takedowns.loc[(takedowns.ufcstats_id == ufcstats_id), 'color'] = "#990000"
    takedowns = takedowns.sort_values(by='color', ascending=False)

    td_fig = Figure()
    ax = td_fig.subplots()

    sns.scatterplot(
        x = takedowns["takedown_accuracy"], 
        y = takedowns["takedown_defence"],
        data = takedowns,
        hue = takedowns["color"],
        palette = dict({'#BFBFBF': '#BFBFBF', '#990000': '#990000'}),
        s = (takedowns["fight_time_seconds_for"] / 15),
        legend=False,
        ax = ax)

    ax.set_xlabel('Takedown Accuracy (%)', fontsize=12)
    ax.set_ylabel('Takedown Defence (%)', fontsize=12)

    ax.grid(zorder=0,alpha=.2)
    ax.set_axisbelow(True)

    ax.axhline(
        y = takedowns["takedown_defence"].mean(),
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    ax.axvline(
        x = takedowns["takedown_accuracy"].mean(),
        linestyle = '--',
        color = 'black',
        alpha = 0.2)

    st.pyplot(td_fig)


def avg_win_dk_chart(ufcstats_id, weight_class):
    all_fighter_career_stats = all_career_stats_df.loc[(all_career_stats_df["weight_class"].str.contains(weight_class))]

    avg_new_dk_pts = all_fighter_career_stats[[
        'ufcstats_id', 'avg_win_new_dk_score', 'fight_time_seconds_for'
    ]]

    # removing where fighters have nan
    avg_new_dk_pts = avg_new_dk_pts.loc[
        (avg_new_dk_pts["avg_win_new_dk_score"] > 0)
    ].reset_index()

    avg_new_dk_pts['color'] = '#BFBFBF'
    avg_new_dk_pts.loc[(avg_new_dk_pts.ufcstats_id == ufcstats_id), 'color'] = "#990000"
    avg_new_dk_pts = avg_new_dk_pts.sort_values(by='color', ascending=False)

    avg_new_dk_pts_fig = Figure()
    ax = avg_new_dk_pts_fig.subplots()

    sns.scatterplot(
        x = avg_new_dk_pts["avg_win_new_dk_score"], 
        y = avg_new_dk_pts["avg_win_new_dk_score"],
        data = avg_new_dk_pts,
        hue = avg_new_dk_pts["color"],
        palette = dict({'#BFBFBF': '#BFBFBF', '#990000': '#990000'}),
        s = (avg_new_dk_pts["fight_time_seconds_for"] / 15),
        legend=False,
        ax = ax)

    ax.set_xlabel('Average Winning DK Points (New)', fontsize=12)

    st.pyplot(avg_new_dk_pts_fig)


# ==========================================================================
# -------------------------------- SETUP -----------------------------------
# ==========================================================================
_lock = RendererAgg.lock
plt.style.use('default')

st.set_page_config(
    page_title='MMA Fighter Dashboard',
    page_icon='https://pbs.twimg.com/profile_images/837118636003311617/LC2WUyQM_400x400.jpg',
    layout="wide")

# ==========================================================================
# ----------------------------- GATHER DATA --------------------------------
# ==========================================================================

# GETTING ALL FIGHTERS
all_fighters_df = pd.read_csv(
    "https://github.com/mjester93/ufc-data/blob/main/fighters.csv?raw=True",
    low_memory=False)

# GETTING CAREER STATS
all_career_stats_df = pd.read_csv(
    "https://github.com/mjester93/ufc-data/blob/main/fighter_career_stats.csv?raw=True",
    low_memory=False)

# GETTING INDIVIDUAL FIGHT DATA
all_fight_data = pd.read_csv(
    "https://github.com/mjester93/ufc-data/blob/main/fight_data.csv?raw=True",
    low_memory=False, 
    thousands=',')
all_fight_data['event_date'] = pd.to_datetime(all_fight_data['event_date'])

all_fight_data_df = all_fight_data.sort_values(by=['event_date'], ascending=False)

# getting average winning new dk score for each fighter and adding it to all_career_stats_df
all_new_winning_dk_scores_df = all_fight_data_df.loc[all_fight_data_df["fighter_winner"] == True].groupby(
    'ufcstats_id'
).mean().reset_index()[['ufcstats_id', 'fighter_new_dk_score']].rename(columns={
    'fighter_new_dk_score': 'avg_win_new_dk_score'
})

all_career_stats_df = all_career_stats_df.merge(
    all_new_winning_dk_scores_df,
    how="left",
    left_on="ufcstats_id",
    right_on="ufcstats_id")

# getting most-recent weight_class and adding it to all_fighters_df
most_recent_fighters_with_weights = all_fight_data_df.drop_duplicates(
    subset=["ufcstats_id"])[['ufcstats_id', 'weight_class']]

all_fighters_df = all_fighters_df.merge(
    most_recent_fighters_with_weights, 
    how="left",
    left_on="ufcstats_id",
    right_on="ufcstats_id"
)

# getting most-recent weight_class and adding it to all_career_stats_df
all_career_stats_df = all_career_stats_df.merge(
    most_recent_fighters_with_weights, 
    left_on="ufcstats_id",
    right_on="ufcstats_id"
)

# getting strikes and adding it to all_career_stats_df
strikes_for_df = all_fight_data.groupby(
    'ufcstats_id'
).agg({
    'fighter_total_strikes_landed': 'sum',
    'fighter_total_strikes_attempted': 'sum',
    'fight_time_seconds': 'sum'
}).reset_index()

strikes_against_df = all_fight_data.groupby(
    'opp_ufcstats_id'
).agg({
    'fighter_total_strikes_landed': 'sum',
    'fight_time_seconds': 'sum'
}).reset_index()

strikes_for_df['strikes_landed_per_minute'] = round(
    strikes_for_df['fighter_total_strikes_landed'] / strikes_for_df['fight_time_seconds'] * 60, 2)

strikes_for_df['strike_accuracy'] = \
    strikes_for_df['fighter_total_strikes_landed'] / strikes_for_df['fighter_total_strikes_attempted'] * 100

strikes_against_df['strikes_absorbed_per_minute'] = round(
    strikes_against_df['fighter_total_strikes_landed'] / strikes_against_df['fight_time_seconds'] * 60, 2)

final_strikes_df = strikes_for_df.merge(
    strikes_against_df,
    left_on="ufcstats_id",
    right_on="opp_ufcstats_id",
    suffixes=('_for', '_against'))[[
        'ufcstats_id', 'strikes_landed_per_minute', 'strikes_absorbed_per_minute', 'strike_accuracy'
    ]]

all_career_stats_df = all_career_stats_df.merge(
    final_strikes_df, 
    left_on="ufcstats_id",
    right_on="ufcstats_id"
)

# getting control percentage / control against percentage
control_for_df = all_fight_data.groupby(
    'ufcstats_id'
).agg({
    'fighter_total_control': 'sum',
    'fight_time_seconds': 'sum'
}).reset_index()

control_against_df = all_fight_data.groupby(
    'opp_ufcstats_id'
).agg({
    'fighter_total_control': 'sum',
    'fight_time_seconds': 'sum'
}).reset_index()

control_for_df['control_percentage'] = round(
    control_for_df['fighter_total_control'] / control_for_df['fight_time_seconds'] * 100, 2)

control_against_df['control_against_percentage'] = round(
    control_against_df['fighter_total_control'] / control_against_df['fight_time_seconds'] * 100, 2)

final_control_df = control_for_df.merge(
    control_against_df,
    left_on="ufcstats_id",
    right_on="opp_ufcstats_id",
    suffixes=('_for', '_against'))[[
        'ufcstats_id', 'fighter_total_control_for', 'fight_time_seconds_for', 
        'fighter_total_control_against', 'control_percentage', 'control_against_percentage'
    ]]

all_career_stats_df = all_career_stats_df.merge(
    final_control_df, 
    left_on="ufcstats_id",
    right_on="ufcstats_id"
)

# Getting takedowns absorbed

# GETTING EXTERNAL IDS
external_ids_df = pd.read_csv(
    "https://github.com/mjester93/ufc-data/blob/main/external_ids.csv?raw=True",
    low_memory=False,
    dtype={'espn_id': str, 'sherdog_id': str})[['ufcstats_id', 'espn_id', 'sherdog_id']]

# Merging with all_fighters_df
all_fighters_df = all_fighters_df.merge(
    external_ids_df,
    how='left',
    left_on='ufcstats_id',
    right_on='ufcstats_id'
)


# ==========================================================================
# ---------------------------- ROW 1 (TITLE) -------------------------------
# ==========================================================================
row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
    (.1, 2, 1.5, 1, .1))

row1_1.title('MMA Fighter Dashboard')

with row1_2:
    st.write('')
    row1_2.subheader(
    'A web application courtesy of [Occupy Fantasy](https://www.occupyfantasy.com)')


# ==========================================================================
# -------------------------------- ROW 2 -----------------------------------
# ==========================================================================

row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns(
    (.1, 1.6, .1, 1.6, .1))

with row2_1:
    records = all_fighters_df.to_dict("records")

    selected_data = st.selectbox(
        "Select a Fighter",
        options=records,
        format_func=lambda record: f"{record['full_name']}")

    ufcstats_id = selected_data.get("ufcstats_id")
    fighter_name = selected_data.get("full_name")
    weight_class = selected_data.get("weight_class")
    if type(weight_class) is not float:
        weight_class = weight_class.replace("UFC","").replace("Title", "").strip() 

    espn_id = selected_data.get("espn_id")
    sherdog_id = selected_data.get("sherdog_id")

# ==========================================================================
# --------------------------- FIGHTER INFO ---------------------------------
# ==========================================================================

st.write('')
row1_space1, row1_1, row1_space2, row1_2, row1_space3, row1_3, row1_space4, row1_4, row1_space5 = st.beta_columns(
    (0.15, 1, .01, 1, .01, 1, 0.01, 1, 0.15))

with row1_1, _lock:
    st.subheader('Fighter Info')
    BASE_ESPN_URL = "https://a.espncdn.com/combiner/i?img=/i/headshots/mma/players/full/"

    fighter_filter = all_fighters_df.loc[all_fighters_df["ufcstats_id"] == ufcstats_id]

    if len(str(espn_id)) < 5:
        st.image("https://upload.wikimedia.org/wikipedia/commons/c/cd/Portrait_Placeholder_Square.png")
    else: 
        st.image(f"{BASE_ESPN_URL}{espn_id}.png", width=300)

    tapology_search_name = fighter_name.lower().replace(" ","+")
    tapology_url = f"https://www.tapology.com/search?term={tapology_search_name}&commit=Submit&model%5Bfighters%5D=fightersSearch"
    
    st.write(f'[ESPN](https://www.espn.com/mma/fighter/_/id/{espn_id}) / \
        [Sherdog](https://www.sherdog.com/fighter/{sherdog_id}) / \
        [UFCStats](http://www.ufcstats.com/fighter-details/{ufcstats_id}) / \
        [Tapology]({tapology_url})')


with row1_2, _lock:
    st.subheader(' ')
    st.write(' ')

    fighter_filter = all_fighters_df.loc[all_fighters_df["ufcstats_id"] == ufcstats_id]
    fighter_career_stats_filter = all_career_stats_df.loc[all_career_stats_df["ufcstats_id"] == ufcstats_id]
    fighter_fights = all_fight_data_df.loc[all_fight_data_df["ufcstats_id"] == ufcstats_id]

    wins = fighter_filter['wins'].astype(int).to_string(index=False).lstrip()
    losses = fighter_filter['losses'].astype(int).to_string(index=False).lstrip()
    draws = fighter_filter['draws'].to_string(index=False).lstrip()

    nickname = fighter_filter['nickname'].to_string(index=False).lstrip()
    nickname = "" if nickname is None else nickname

    record = f"{wins}-{losses}-{draws}"

    st.text(f"Name: {fighter_filter['full_name'].to_string(index=False).lstrip()}")
    st.text(f"Nickname: {nickname}")
    st.text(f"Date of Birth: {fighter_career_stats_filter['date_of_birth'].to_string(index=False).lstrip()}")
    st.text(f"Height: {fighter_filter['height'].to_string(index=False).lstrip()}")
    st.text(f"Weight: {fighter_filter['weight'].astype(int).to_string(index=False).lstrip()}")
    st.text(f"Weight Class: {weight_class}")
    st.text(f"Reach: {fighter_filter['reach'].to_string(index=False).lstrip()}")
    st.text(f"Stance: {fighter_filter['stance'].to_string(index=False).lstrip()}")
    st.text(f"Record: {record}")

with row1_3, _lock:
    st.subheader('Fighter Stats')

    fighter_career_stats_filter = all_career_stats_df.loc[all_career_stats_df["ufcstats_id"] == ufcstats_id]

    sig_str_acc = fighter_career_stats_filter['sig_strike_accuracy'].astype(int).to_string(index=False).lstrip()
    str_acc = fighter_career_stats_filter['strike_accuracy'].astype(int).to_string(index=False).lstrip()
    sig_str_def = fighter_career_stats_filter['sig_strike_defence'].astype(int).to_string(index=False).lstrip()
    fight_seconds = fighter_career_stats_filter['fight_time_seconds_for'].astype(float).to_string(index=False).lstrip()
    fight_time_mins = float(fight_seconds) / 60 if fight_seconds != "Series([], )" else 0

    st.text(f"SSLpM: {fighter_career_stats_filter['sig_strikes_landed_per_minute'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"SSApM: {fighter_career_stats_filter['sig_strikes_absorbed_per_minute'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"Sig. Str. Acc: {sig_str_acc}%")
    st.text(f"Sig. Str. Def: {sig_str_def}%")
    st.text(f"*SLpM: {fighter_career_stats_filter['strikes_landed_per_minute'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"*SApM: {fighter_career_stats_filter['strikes_absorbed_per_minute'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"*Str. Acc: {str_acc}%")
    st.text(f"*Fight Time (mins): {fight_time_mins}")

with row1_4, _lock:
    st.subheader(' ')
    st.write(' ')

    fighter_career_stats_filter = all_career_stats_df.loc[all_career_stats_df["ufcstats_id"] == ufcstats_id]

    td_acc = fighter_career_stats_filter['takedown_accuracy'].astype(int).to_string(index=False).lstrip()
    td_def = fighter_career_stats_filter['takedown_defence'].astype(int).to_string(index=False).lstrip()
    ctrl_pct = fighter_career_stats_filter["control_percentage"].astype(float).to_string(index=False).lstrip()
    ctrl_agt_pct = fighter_career_stats_filter["control_against_percentage"].astype(float).to_string(index=False).lstrip()
    avg_win_new_dk_score = fighter_career_stats_filter["avg_win_new_dk_score"].astype(float).to_string(index=False).lstrip()

    st.text(f"TD Avg.: {fighter_career_stats_filter['avg_takedowns_per_15_minutes'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"TD Acc.: {td_acc}%")
    st.text(f"TD Def.: {td_def}%")
    st.text(f"Sub. Avg.: {fighter_career_stats_filter['avg_submission_attempts_per_15_minutes'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"*Ctrl. Pct.: {ctrl_pct}%")
    st.text(f"*Ctrl. Agt. Pct.: {ctrl_agt_pct}%")
    st.text(f"*Avg. Win. DK Pts.: {avg_win_new_dk_score}")

# ==========================================================================
# ---------------------------- FIGHTER LOGS --------------------------------
# ==========================================================================

st.write('')
row2_space1, row2_1, row2_space2 = st.beta_columns(
    (.1, 3, 0.1))


with row2_1, _lock:
    st.subheader('Fight Log (2018-present)')
    has_data = len(all_fight_data_df.loc[all_fight_data_df["ufcstats_id"] == ufcstats_id])
    if has_data > 0:
        st.dataframe(fight_logs(ufcstats_id), width=5000,height=1000)

    else:
        st.error(
            "Oops! This player did not fight during the selected time period. "\
            "Change the filter and try again.")
        st.stop()

# ==========================================================================
# --------------------------- FIGHTER CHARTS -------------------------------
# ==========================================================================

st.write('')
row3_space1, row3_1, row3_space2, row3_2, row3_space3, row3_3, row3_space4 = st.beta_columns(
    (.15, 1.5, .00000001, 1.5, .00000001, 1.5, 0.15))

with row3_1, _lock:
    st.subheader('Sig. Strikes by Class')
    sig_strikes_chart(ufcstats_id, weight_class)

with row3_2, _lock:
    st.subheader('Total Strikes by Class (2018-present)')
    strikes_chart(ufcstats_id, weight_class)

with row3_3, _lock:
    st.subheader('Control Percentage by Class (2018-present)')
    control_pct_chart(ufcstats_id, weight_class)


# ==========================================================================
# --------------------------- FIGHTER CHARTS -------------------------------
# ==========================================================================

st.write('')
row4_space1, row4_1, row4_space2, row4_2, row4_space3, row4_3, row4_space4 = st.beta_columns(
    (.15, 1.5, .00000001, 1.5, .00000001, 1.5, 0.15))

with row4_1, _lock:
    st.subheader('Takedowns by Class')
    td_chart(ufcstats_id, weight_class)


with row4_3, _lock:
    st.subheader('Avg. Win. DK Pts by Class (2018-present)')
    avg_win_dk_chart(ufcstats_id, weight_class)


# ==========================================================================
# -------------------------------- KEY -------------------------------------
# ==========================================================================
row6_spacer1, row6_1, row6_spacer2 = st.beta_columns((.1, 3.2, .1))

with row6_1:
    st.markdown('___')
    about = st.beta_expander('Key/Additional Info')
    with about:
        '''
        Data and fight statistics are courtesy of UFCStats.com. Headshots are courtesy of ESPN and is used under fair use. \
        Stats marked with an asterik (*) use fight log data, which is as of 2018 so far. 
        
        A fighter's odds come from various sources. From 2010 to COVID-19, it is take from \
        this [Kaggle Database](https://www.kaggle.com/mdabbert/ufc-fights-2010-2020-with-betting-odds/notebooks), \
        which uses [BestFightOdds.com](https://www.bestfightodds.com). After COVID to the end of 2020, \
        [BestFightOdds.com](https://www.bestfightodds.com) is used. Starting in 2021, the DonBest Consensus \
        moneyline is used.

        **SSLpM:** Significant strikes landed per minute

        **SSApM:** Significant strikes absorbed per minute

        **Sig Str. Acc:** Significant strike accuracy

        **SLpM:** Total Strikes landed per minute

        **SApM:** Total Strikes absorbed per minute

        **Str. Acc.:** Total Strike Accuracy

        **Sig. Str. Def:** Significant Strike Defence (the % of opponents strikes that did not land)

        **TD Avg:** Average Takedowns Landed per 15 minutes

        **TD Acc:** Takedown accuracy

        **TD Def.:** Takedown Defense (the % of opponents TD attempts that did not land)

        **Sub. Avg.:** Average Submissions Attempted per 15 minutes

        **Ctrl. Pct.:** Control percentage (total number of seconds controlled / total fight time in seconds)

        **Ctrl. Agt. Pct.:** Control Against Percentage (total number of seconds being controlled / toglt fight time in seconds)

        **Avg. Win. DK Pts.** Average DraftKings Points (new scoring) in winning fights
        '''