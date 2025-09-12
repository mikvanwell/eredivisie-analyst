import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Expected Standings",
    page_icon="📊"
)

# Load standings data based on selection
@st.cache_data
def load_standings_data(table_type):
    if table_type == "Expected Standings":
        df = pd.read_csv("expected_standings.csv")
    elif table_type == "Adjusted Expected Standings":
        df = pd.read_csv("expected_adj_standings.csv")
    else:  # Non-Penalty Standings
        df = pd.read_csv("expected_np_standings.csv")
    
    # Sort by Rank
    return df.sort_values('Rank')

# Load results data (always needed)
@st.cache_data
def load_results_data():
    results = pd.read_csv("expected_results.csv")
    
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
    
    return results

st.title("Expected Standings")
st.markdown(
    "Use the buttons below to choose between the Expected Eredivisie standings based on expected goals, adjusted expected goals, or non-penalty expected goals. "
    "You can read more about the method for adjusting xG [here](https://open.substack.com/pub/mikvanwell/p/normalising-xg-for-penalties-removing?r=4l6fci&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)."
)

# Radio button selection for table type
table_choice = st.radio(
    "Select Standings Type:",
    ["Expected Standings", "Adjusted Expected Standings", "Non-Penalty Expected Standings"],
    horizontal=True
)

# Load only the selected standings data
selected_standings = load_standings_data(table_choice)

# Formatter for GD and xGD (with rounding for xGD)
def plus_formatter(x):
    return f"+{int(x)}" if x > 0 else f"{int(x)}"

def plus_formatter_1decimal(x):
    x_rounded = round(x, 1)
    return f"+{x_rounded:.1f}" if x_rounded > 0 else f"{x_rounded:.1f}"

# Create format dictionary based on table type
def get_format_dict(choice):
    if choice == "Expected Standings":
        return {
            "GD": plus_formatter,
            "xGD": plus_formatter_1decimal,
            "xG": "{:.1f}".format,
            "xGA": "{:.1f}".format,
            "xPTS": "{:.1f}".format
        }
    elif choice == "Adjusted Expected Standings":
        return {
            "GD": plus_formatter,
            "adjxGD": plus_formatter_1decimal,
            "adjxG": "{:.1f}".format,
            "adjxGA": "{:.1f}".format,
            "adjxPTS": "{:.1f}".format
        }
    else:  # Non-Penalty Expected Standings
        return {
            "GD": plus_formatter,
            "npxGD": plus_formatter_1decimal,
            "npxG": "{:.1f}".format,
            "npxGA": "{:.1f}".format,
            "npxPTS": "{:.1f}".format
        }

# Get the appropriate format dictionary
format_dict = get_format_dict(table_choice)

# Display the selected standings table
st.dataframe(
    selected_standings.style.format(format_dict),
    hide_index=True
)

# Load results data
expected_results = load_results_data()

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