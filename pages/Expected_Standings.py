import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Expected Standings",
    page_icon="📊"
)

# Load the data
@st.cache_data
def load_data():
    standings = pd.read_csv("expected_standings.csv")
    results = pd.read_csv("expected_results.csv")
    
    # Sort standings by Rank
    standings = standings.sort_values('Rank')
    
    # Fix column names (remove the period and add %)
    results = results.rename(columns={
        'HomeWin.': 'HomeWin%',
        'Draw.': 'Draw%', 
        'AwayWin.': 'AwayWin%'
    })
    
    # Convert percentage columns to percentage format
    results['HomeWin%'] = results['HomeWin%'] * 100
    results['Draw%'] = results['Draw%'] * 100
    results['AwayWin%'] = results['AwayWin%'] * 100
    
    return standings, results

# Load the dataframes
expected_standings, expected_results = load_data()

st.title("Expected Standings")

# Display the standings table (hide index)
st.dataframe(expected_standings, hide_index=True)

# Display results with gameweek filter
st.subheader("Expected Results")

# Create gameweek selector
gameweeks = sorted(expected_results['GW'].unique())
selected_gw = st.selectbox("Select Gameweek:", gameweeks)

# Filter and display results
filtered_results = expected_results[expected_results['GW'] == selected_gw]
st.dataframe(
    filtered_results, 
    hide_index=True,
    column_config={
        "HomeWin%": st.column_config.NumberColumn(
            "HomeWin%",
            format="%.1f%%"
        ),
        "Draw%": st.column_config.NumberColumn(
            "Draw%", 
            format="%.1f%%"
        ),
        "AwayWin%": st.column_config.NumberColumn(
            "AwayWin%",
            format="%.1f%%"
        )
    }
)

