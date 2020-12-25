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
        'round', 'time', 'method', 'fighter_new_dk_score', 'fighter_old_dk_score', 
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
all_fight_data_df = pd.read_csv(
    "https://github.com/mjester93/ufc-data/blob/main/fight_data.csv?raw=True",
    low_memory=False)

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

with row2_2:
    start_week, stop_week = st.select_slider(
        'Select A Date Range (TBD)',
        options=list(range(1,22)),
        value=(1,21))


# ==========================================================================
# --------------------------- FIGHTER INFO ---------------------------------
# ==========================================================================

st.write('')
row1_space1, row1_1, row1_space2, row1_2, row1_space3, row1_3, row1_space4 = st.beta_columns(
    (.15, 1, .3, 1, .00000001, 3, 0.15))

with row1_1, _lock:
    fighter_filter = all_fighters_df.loc[all_fighters_df["ufcstats_id"] == ufcstats_id]
    fighter_career_stats_filter = all_career_stats_df.loc[all_career_stats_df["ufcstats_id"] == ufcstats_id]
    st.subheader('Fighter Info')

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
    st.text(f"Reach: {fighter_filter['reach'].to_string(index=False).lstrip()}")
    st.text(f"Stance: {fighter_filter['stance'].to_string(index=False).lstrip()}")
    st.text(f"Record: {record}")

with row1_2, _lock:
    fighter_career_stats_filter = all_career_stats_df.loc[all_career_stats_df["ufcstats_id"] == ufcstats_id]

    str_acc = fighter_career_stats_filter['sig_strike_accuracy'].astype(int).to_string(index=False).lstrip()
    str_def = fighter_career_stats_filter['sig_strike_defence'].astype(int).to_string(index=False).lstrip()
    td_acc = fighter_career_stats_filter['takedown_accuracy'].astype(int).to_string(index=False).lstrip()
    td_def = fighter_career_stats_filter['takedown_defence'].astype(int).to_string(index=False).lstrip()

    fighter_fights = all_fight_data_df.loc[all_fight_data_df["ufcstats_id"] == ufcstats_id]
    opp_fights = all_fight_data_df.loc[all_fight_data_df["opp_ufcstats_id"] == ufcstats_id]

    control = fighter_fights[["fighter_total_control"]].astype(int).sum().to_string(index=False).lstrip()
    total_seconds = fighter_fights[["fight_time_seconds"]].astype(int).sum().to_string(index=False).lstrip()
    try:
        ctrl_pct = round(int(control) / int(total_seconds) * 100, 2)
    except ZeroDivisionError:
        ctrl_pct = 0

    control_against = opp_fights[["fighter_total_control"]].astype(int).sum().to_string(index=False).lstrip()
    total_seconds_against = opp_fights[["fight_time_seconds"]].astype(int).sum().to_string(index=False).lstrip()
    try:
        ctrl_agt_pct = round(int(control_against) / int(total_seconds_against) * 100, 2)
    except ZeroDivisionError:
        ctrl_agt_pct = 0

    st.subheader(' ')
    st.text(' ')
    st.text(f"SLpM: {fighter_career_stats_filter['sig_strikes_landed_per_minute'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"Str. Acc: {str_acc}%")
    st.text(f"SApM: {fighter_career_stats_filter['sig_strikes_absorbed_per_minute'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"Str. Def: {str_def}%")
    st.text(f"TD Avg.: {fighter_career_stats_filter['avg_takedowns_per_15_minutes'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"TD Acc.: {td_acc}%")
    st.text(f"TD Def.: {td_def}%")
    st.text(f"Sub. Avg.: {fighter_career_stats_filter['avg_submission_attempts_per_15_minutes'].astype(float).to_string(index=False).lstrip()}")
    st.text(f"Ctrl. Pct.: {ctrl_pct}%")
    st.text(f"Ctrl. Agt. Pct.: {ctrl_agt_pct}%")

with row1_3, _lock:
    st.subheader('Fight Log (2018-present)')
    has_data = len(all_fight_data_df.loc[all_fight_data_df["ufcstats_id"] == ufcstats_id])
    if has_data > 0:
        st.dataframe(fight_logs(ufcstats_id), width=5000,height=700)

    else:
        st.error(
            "Oops! This player did not fight during the selected time period. "\
            "Change the filter and try again.")
        st.stop()

# ==========================================================================
# -------------------------------- KEY -------------------------------------
# ==========================================================================
row5_spacer1, row5_1, row5_spacer2 = st.beta_columns((.1, 3.2, .1))

with row5_1:
    st.markdown('___')
    about = st.beta_expander('Key/Additional Info')
    with about:
        '''
        **SLpM:** Significant strikes landed per minute

        **Str. Acc:** Significant strike accuracy

        **SApM:** Significant strikes absorbed per minute

        **Str. Def:** Significant Strike Defence (the % of opponents strikes that did not land)

        **TD Avg:** Average Takedowns Landed per 15 minutes

        **TD Acc:** Takedown accuracy

        **TD Def.:** Takedown Defense (the % of opponents TD attempts that did not land)

        **Sub. Avg.:** Average Submissions Attempted per 15 minutes

        **Ctrl. Pct.:** Control percentage (total number of seconds controlled / total fight time in seconds)

        **Ctrl. Agt. Pct.:** Control Against Percentage (total number of seconds being controlled / toglt fight time in seconds)
        '''