import streamlit as st
import pandas as pd
import json
from mplsoccer import VerticalPitch

st.title("UEFA Euros Shotmap")

st.subheader("Select the team, and then the player to see shots and goals since Euros 2020")

df = pd.read_csv('euros_shot_data.csv')

# filter for shots only
df = df[df['type'] == 'Shot'].reset_index(drop=True)

# for shot location
# comes as a list - converts the coordinates into lists instead of string
df['location'] = df['location'].apply(json.loads)


############## select team and players
# filter df - create select box
team = st.selectbox('Select Team:', df['team'].sort_values().unique(), index=None)
# select player
player = st.selectbox('Select Player:', df[df['team'] == team]['player'].sort_values().unique(), index=None)
# note, the index = None, means there is no 'default' option selected

# work with time of game
# game_times = ['1st Half', '2nd Half', 'Extra Time 1st Half', 'Extra Time 2nd Half', 'Penalty Kicks']
# half = st.multiselect('Select Half', options = game_times, default = game_times)
# select when the goals are scored


# side panel
with st.sidebar:
    year = st.segmented_control(
            label = 'Select Tournament Year:', 
            options = [2020, 2024],
            selection_mode = "multi",
            default = [2024])

# filter data based on the year input
df = df[df['edition'].isin(year)]


st.divider()
##############################################################################


# function for filtering data
def filter_data(df, team, player):
    if team:
        df = df[df['team'] == team]
    if player:
        df = df[df['player'] == player]

    return df

filtered_df = filter_data(df, team, player)
# ensures only players belonging to that nation can be selected
# i.e. cannot select Harry Kane if France is selected


#### plot the pitch and shots ####
pitch = VerticalPitch(pitch_type = 'statsbomb', half=True)
fig, ax = pitch.draw(figsize = (10,10))


# plot shots function
def plot_shots(df, ax, pitch):
    for x in df.to_dict(orient='records'): # how to iterate over the shots
        pitch.scatter( # scatter of points
            x = float(x['location'][0]), # transformed to list so we can grab the first element
            y = float(x['location'][1]), # transformed to list so we can grab the second element
            ax = ax,
            s = 1000 * x['shot_statsbomb_xg'], # will scale dot based on the xg value (larger for highest goal)
            color = 'orange' if (x['shot_outcome'] == 'Goal') and (x['shot_type'] == 'Penalty') else 
                ('#1f6915' if (x['shot_outcome'] == 'Goal') and (x['shot_type'] != 'Penalty') else 'white'), 
            edgecolors = 'black',
            linewidth = 2,
            alpha = 1 if x['type'] == 'goal' else .5, # makes the goals easier to see
            zorder = 2 if x['type'] == 'goal' else 1 # just ordering goals on top of all dots
        )

# use the function
# initially will take time to print for first use
# but check the different options
plot_shots(filtered_df, ax, pitch)


# actually draws this to the web app
st.pyplot(fig)




st.divider()
#######################################################

# show table of summary scorers for country
st.subheader("Top Goal Scorers:")

# create function to filter the dataset again but no need for player 
def filter_scorers(df, team):
    df = df[df['shot_outcome'] == 'Goal'] # filter for goals only

    # if a team is selected
    if team:
        df = df[df['team'] == team] # filter for team
        
        # group by the players and count goals
        df = df.groupby(['player'])['shot_outcome'].count().reset_index()
        df.rename(columns={'shot_outcome':'Goals'}, inplace=True)
        df_sorted = df.sort_values(by='Goals', ascending=False).set_index('player')

    # if no team is selected - output all
    else:
        df = df.groupby(['player', 'team'])['shot_outcome'].count().reset_index()
        df.rename(columns={'shot_outcome':'Goals', 'player':'Player', 'team':'Nation'}, inplace=True)
        df_sorted = df.sort_values(by='Goals', ascending=False).style.hide_index()
    

    return df_sorted
        
goal_table = filter_scorers(df, team)
# output the table 
st.table(goal_table)

