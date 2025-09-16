import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Expected Standings",
    page_icon="📊"
)

# Load standings data based on selection
@st.cache_data
def load_standings_data(table_type):
    if table_type == "Expected Standings":
        df = pd.read_csv("expected_standings.csv")
        return df.sort_values('xRank')
    elif table_type == "Adjusted Expected Standings":
        df = pd.read_csv("expected_adj_standings.csv")
        return df.sort_values('adjxRank')
    else:  # Non-Penalty Expected Standings
        df = pd.read_csv("expected_np_standings.csv")
        return df.sort_values('npxRank')

# Load results data (always needed)
@st.cache_data
def load_results_data():
    results = pd.read_csv("expected_results.csv")
    
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
    
    results['Home Win%'] = results['Home Win%'] * 100
    results['Draw %'] = results['Draw %'] * 100
    results['Away Win%'] = results['Away Win%'] * 100
    
    return results

st.title("Expected Standings")
st.markdown(
    "Use the buttons below to choose between the Expected Eredivisie standings based on expected goals, adjusted expected goals, or non-penalty expected goals. "
    "You can read more about the method for adjusting xG [here](https://open.substack.com/pub/mikvanwell/p/normalising-xg-for-penalties-removing?r=4l6fci&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)."
)

table_choice = st.radio(
    "Select standings type:",
    ["Expected Standings", "Adjusted Expected Standings", "Non-Penalty Expected Standings"],
    horizontal=True
)

selected_standings = load_standings_data(table_choice)

st.write("### View Options")
view_choice = st.toggle("Switch to Graph View", value=False)

# Function to create the interactive graph
def create_standings_graph(df, table_type):
    if table_type == "Expected Standings":
        x_rank_col = "xRank"
        x_pts_col = "xPTS"
        title_suffix = "Expected"
    elif table_type == "Adjusted Expected Standings":
        x_rank_col = "adjxRank"
        x_pts_col = "adjxPTS"
        title_suffix = "Adjusted Expected"
    else:
        x_rank_col = "npxRank"
        x_pts_col = "npxPTS"
        title_suffix = "Non-Penalty Expected"

    df_sorted = df.sort_values('Rank', ascending=True)
    fig = go.Figure()
    circle_radius = 0.6

    for idx, row in df_sorted.iterrows():
        team = row['Team']
        actual_rank = row['Rank']
        actual_pts = row['PTS']
        expected_rank = row[x_rank_col]
        expected_pts = row[x_pts_col]

        if expected_rank < actual_rank:
            arrow_color = 'green'
        elif expected_rank > actual_rank:
            arrow_color = 'red'
        else:
            arrow_color = 'grey'

        y_pos = actual_rank

        fig.add_trace(go.Scatter(
            x=[actual_pts],
            y=[y_pos],
            mode='markers+text',
            marker=dict(size=25, color='lightblue', line=dict(color='blue', width=2)),
            text=[str(actual_rank)],
            textfont=dict(size=12, color='black'),
            name=f"{team} - Actual",
            showlegend=False,
            hovertemplate=f"<b>{team}</b><br>Actual Rank: {actual_rank}<br>Actual Points: {actual_pts}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=[expected_pts],
            y=[y_pos],
            mode='markers+text',
            marker=dict(
                size=25,
                color='lightcoral' if arrow_color == 'red' else 'lightgreen' if arrow_color == 'green' else 'lightgrey',
                line=dict(color=arrow_color, width=2)
            ),
            text=[str(expected_rank)],
            textfont=dict(size=12, color='black'),
            name=f"{team} - Expected",
            showlegend=False,
            hovertemplate=f"<b>{team}</b><br>Expected Rank: {expected_rank}<br>Expected Points: {expected_pts:.1f}<extra></extra>"
        ))

        if abs(actual_pts - expected_pts) >= 1:
            direction = 1 if expected_pts > actual_pts else -1
            arrow_start = actual_pts + (direction * circle_radius)
            arrow_end = expected_pts - (direction * circle_radius)

            fig.add_trace(go.Scatter(
                x=[arrow_start, arrow_end],
                y=[y_pos, y_pos],
                mode='lines+markers',
                line=dict(color=arrow_color, width=3),
                marker=dict(symbol="arrow", size=12, angleref="previous", color=arrow_color),
                showlegend=False,
                hoverinfo='skip'
            ))

    fig.update_layout(
        title=f"{title_suffix} Points vs Actual Points by Team",
        xaxis_title="Points",
        yaxis_title="Teams (by Actual Rank)",
        height=600,
        showlegend=False,
        hovermode='closest',
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(1, len(df_sorted) + 1)),
            ticktext=[f"{row['Rank']}. {row['Team']}" for _, row in df_sorted.iterrows()],
            autorange='reversed'
        ),
        xaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=1),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='lightblue', line=dict(color='blue', width=2)),
        name='Actual Rank & Points',
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='lightgreen', line=dict(color='green', width=2)),
        name='Expected Rank & Points',
        showlegend=True
    ))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

if not view_choice:
    def plus_formatter(x):
        return f"+{int(x)}" if x > 0 else f"{int(x)}"

    def plus_formatter_1decimal(x):
        x_rounded = round(x, 1)
        return f"+{x_rounded:.1f}" if x_rounded > 0 else f"{x_rounded:.1f}"

    def get_format_dict(choice):
        if choice == "Expected Standings":
            return {"xDif": plus_formatter, "GD": plus_formatter, "xGD": plus_formatter_1decimal, "xG": "{:.1f}".format, "xGA": "{:.1f}".format, "xPTS": "{:.1f}".format}
        elif choice == "Adjusted Expected Standings":
            return {"adjxDif": plus_formatter, "GD": plus_formatter, "adjxGD": plus_formatter_1decimal, "adjxG": "{:.1f}".format, "adjxGA": "{:.1f}".format, "adjxPTS": "{:.1f}".format}
        else:
            return {"npxDif": plus_formatter, "GD": plus_formatter, "npxGD": plus_formatter_1decimal, "npxG": "{:.1f}".format, "npxGA": "{:.1f}".format, "npxPTS": "{:.1f}".format}

    format_dict = get_format_dict(table_choice)
    st.dataframe(selected_standings.style.format(format_dict), hide_index=True)
else:
    fig = create_standings_graph(selected_standings, table_choice)
    st.plotly_chart(fig, use_container_width=True)
    st.info("""
    **How to read the graph:**
    - Teams are arranged by their **actual rank** (1st at top, 18th at bottom)
    - **Blue circles** show actual rank and points
    - **Colored circles** show expected rank and points
    - **Arrows** connect actual to expected positions:
        - 🟢 **Green**: Team should be ranked higher (performing below expected)  
        - 🔴 **Red**: Team should be ranked lower (performing above expected)
        - 🔘 **Grey**: Team is performing as expected
    """)

expected_results = load_results_data()
st.subheader("Expected Results")
gameweeks = sorted(expected_results['GW'].unique())
selected_gw = st.selectbox("Select Gameweek:", gameweeks)
filtered_results = expected_results[expected_results['GW'] == selected_gw]
st.dataframe(
    filtered_results,
    hide_index=True,
    column_config={
        "Home Win%": st.column_config.NumberColumn("Home Win%", format="%.1f%%"),
        "Draw %": st.column_config.NumberColumn("Draw %", format="%.1f%%"),
        "Away Win%": st.column_config.NumberColumn("Away Win%", format="%.1f%%")
    }
)
