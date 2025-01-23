import streamlit as st
import pandas as pd
import json
from mplsoccer import VerticalPitch

st.title("Euros 2024 Shotmap")

st.subheader("Select the team/player to see the shots taken throughout the tournament")

df = pd.read_csv('euros_2024_shot_map.csv')

# filter for shots only
df = df[df['type'] == 'Shot'].reset_index(drop=True)

# for shot location
# comes as a list - converts the coordinates into lists instead of string
df['location'] = df['location'].apply(json.loads)

# filter df - create select box
team = st.selectbox('Select Team:', df['team'].sort_values().unique(), index=None)
# select player
player = st.selectbox('Select Player:', df[df['team'] == team]['player'].sort_values().unique(), index=None)
# note, the index = None, means there is no 'default' option selected

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
            s = 1000 * x['shot_statsbomb_xg'], # will scall dot based on the xg value (larger for highest goal)
            color = 'orange' if (x['shot_outcome'] == 'Goal') and (x['shot_type'] == 'Penalty') else 
                ('green' if (x['shot_outcome'] == 'Goal') and (x['shot_type'] != 'Penalty') else 'white'), 
            edgecolors = 'black',
            alpha = 1 if x['type'] == 'goal' else .5, # makes the goals easier to see
            zorder = 2 if x['type'] == 'goal' else 1 # just ordering goals on top of all dots
        )

# use the function
# initially will take time to print for first use
# but check the different options
plot_shots(filtered_df, ax, pitch)

# actually draws this to the web app
st.pyplot(fig)