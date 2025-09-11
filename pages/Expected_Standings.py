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
        'Home_Win_pct': 'Home Win%',
        'Draw_pct': 'Draw %', 
        'Away_Win_pct': 'Away Win%',
        'Home_xPTS': 'Home xPTS',
        'Home_xG': 'Home xG', 
        'Home_Goals': 'Home Goals',
        'Away_Goals': 'Away Goals', 
        'Away_xG': 'Away xG',
        'Away_xPTS': 'Away xPTS'
    })
    
    # Convert percentage columns to percentage format
    results['Home Win%'] = results['Home Win%'] * 100
    results['Draw %'] = results['Draw %'] * 100
    results['Away Win%'] = results['Away Win%'] * 100
    
    return standings, results

# Load the dataframes
expected_standings, expected_results = load_data()

st.title("Expected Standings")

# Formatter for GD and xGD (with rounding for xGD)
def plus_formatter(x):
    return f"+{int(x)}" if x > 0 else f"{int(x)}"

def plus_formatter_1decimal(x):
    x_rounded = round(x, 1)
    return f"+{x_rounded:.1f}" if x_rounded > 0 else f"{x_rounded:.1f}"

# Display the standings table (hide index, format GD, xGD, xG, xGA, xPTS)
st.dataframe(
    expected_standings.style.format({
        "GD": plus_formatter,
        "xGD": plus_formatter_1decimal,
        "xG": "{:.1f}".format,
        "xGA": "{:.1f}".format,
        "xPTS": "{:.1f}".format
    }),
    hide_index=True
)

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
        "Home Win%": st.column_config.NumberColumn(
            "Home Win%",
            format="%.1f%%"
        ),
        "Draw %": st.column_config.NumberColumn(
            "Draw %", 
            format="%.1f%%"
        ),
        "Away Win%": st.column_config.NumberColumn(
            "Away Win%",
            format="%.1f%%"
        )
    }
)

