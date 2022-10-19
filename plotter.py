"""
This script creates several plots wtih the data from scrapper.py

Make sure to change the CSV file name and the year (when applicable).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
from plotly.subplots import make_subplots
import argparse
from datetime import datetime


x = datetime.now()

#argparse object creation
arg=argparse.ArgumentParser(description="plots subreddits data")
arg.add_argument("-r", "--r",
                type = str,
                default = "Python",
                help = " takes in name of the subreddit")
arg.add_argument("-yr", "--yr",
                type = int,
                default = x.year,
                help = " takes in required Year")
args=arg.parse_args()


def plot_calendar(args):
    """
    This function will create a calendar plot, very similar to
    the one seen in GitHub profiles.
    """

    # This plot needs to know the year so it can configure itself.
    year = args.yr

    # We read our CSV file and make the isodate column our index.
    df = pd.read_csv(
        f"./{args.r}-{year}.csv",
        parse_dates=["isodate"],
        index_col="isodate"
    )

    # For this plot We only need the date (not time), we extract it from the datetime index.
    df["date"] = df.index.date

    # We extract the value counts of each date found into a Series.
    totals = df["date"].value_counts().sort_index()

    # In order for the calendar to work we need to create a 'skeleton' with all
    # the days in the specified year.
    # We create this skeleton using a date_range. Then we will add the previously
    # created Series as the 'total' column.
    # We might get NA values for missing days. We will address that in a bit.
    final = pd.DataFrame(index=pd.date_range(
        f"{year}-01-01", f"{year}-12-31", freq="d"), data={"total": totals})

    # For this calendar to work we need a grid of 53 columns and 7 rows.
    # We can't use the week, dayofyear or similar properties from the date index
    # as they use the Gregorian calendar.
    # That being said we create such grid.
    week_numbers = list()

    for week in range(53):
        week_numbers.extend([week for _ in range(7)])

    # We extract the day of the week from the first day of the year, this will be used
    # to slice the previously created list. This is because not all years start on Mondays.
    pad = final.index[0].dayofweek

    # This column will be used for our Y-axis.
    final["dayofweek"] = final.index.dayofweek

    # This column will be used for our x-axis, notice how we slice
    # the week_numbers list. This way it will be the exact size as the DataFrame.
    final["week"] = week_numbers[pad:len(final) + pad]

    # Calendar plots have the problem that it is hard to determine where the months start
    # my attempt to fix this is to add a border to the first day of each month.
    final["border"] = final.index.map(lambda x: 1 if x.day == 1 else 0)

    # Optional: fill NA values (missing days) with 0.
    final["total"].fillna(0, inplace=True)

    # Here we extract some descriptive statistics that will be used in a table.
    stats_min = f"{final['total'].min():,.0f} on {final['total'].idxmin():%F}"
    stats_max = f"{final['total'].max():,.0f} on {final['total'].idxmax():%F}"
    stats_total = final["total"].sum()
    stats_mean = final["total"].sum() / len(final)

    # Hard-coded abbreviations of the months for the x-axis.
    months_labels = ["Jan", "Feb", "Mar", "Apr",
                     "May", "Jun", "Jul", "Aug",
                     "Sep", "Oct", "Nov", "Dec"]

    # These values evenly spread the abbreviations above the plot.
    months_ticks = np.linspace(1.5, 49.5, 12)

    # Hard-coded names of the days of the week for the y-axis.
    days_ticks = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
                  3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    # We will create a figure with 2 rows: A heatmap and a table.
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[250, 150],
        vertical_spacing=0.07,
        specs=[
            [{"type": "scatter"}],
            [{"type": "table"}]
        ]
    )

    # The first heatmap will be used to show the borders only.
    # Notice the xgap # and ygap properties.
    fig.add_trace(
        go.Heatmap(
            x=final["week"],
            y=final["dayofweek"],
            z=final["border"],
            xgap=1,
            ygap=12,
            colorscale=["hsla(0, 100%, 100%, 0.0)",
                        "hsla(0, 100%, 100%, 1.0)"],
            showscale=False,
        ), col=1, row=1
    )

    # We will add a heatmap above the previous one with the real values.
    # Again, notice the xgap and ygap values, with that trick we can have
    # borders.
    fig.add_trace(
        go.Heatmap(
            x=final["week"],
            y=final["dayofweek"],
            z=final["total"],
            xgap=5,
            ygap=16,
            colorscale="speed_r",
            colorbar={
                "y": 0.6,
                "ticks": "outside",
                "outlinewidth": 2,
                "thickness": 20,
                "outlinecolor": "#FFFFFF",
                "tickwidth": 2,
                "tickcolor": "#FFFFFF",
                "ticklen": 10,
                "tickfont_size": 16,
                "separatethousands": True
            }
        ), col=1, row=1
    )

    # Finally we add a simple table with the descriptive statistics.
    fig.add_trace(
        go.Table(
            header=dict(
                values=[
                    "<b>Maximum</b>",
                    "<b>Minimum</b>",
                    "<b>Total</b>",
                    "<b>Average</b>"
                ],
                font_color="#FFFFFF",
                fill_color="#789A07",
                align="center",
                height=32,
                line_width=0.8),
            cells=dict(
                values=[
                    stats_max,
                    stats_min,
                    f"{stats_total:,.0f}",
                    f"{stats_mean:,.0f} daily"
                ],
                fill_color="#041C32",
                height=32,
                line_width=0.8,
                align="center"
            )
        ), col=1, row=2
    )

    fig.update_xaxes(
        title="",
        side="top",
        tickfont_size=20,
        range=[-1, 53],
        ticktext=months_labels,
        tickvals=months_ticks,
        ticks="outside",
        ticklen=5,
        tickwidth=0,
        linecolor="#FFFFFF",
        tickcolor="#1E1E1E",
        showline=True,
        zeroline=False,
        showgrid=False,
        mirror=True,
    )

    fig.update_yaxes(
        range=[6.75, -0.75],
        ticktext=list(days_ticks.values()),
        tickvals=list(days_ticks.keys()),
        ticks="outside",
        tickfont_size=16,
        ticklen=10,
        title_standoff=0,
        tickcolor="#FFFFFF",
        linewidth=1.5,
        showline=True,
        zeroline=False,
        showgrid=False,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=500,
        font_family="Jura",
        font_color="#FFFFFF",
        font_size=20,
        title_text=f"Distribution of submissions in r/{args.r} during {year} by date (UTC)",
        title_x=0.5,
        title_y=0.93,
        margin_t=120,
        margin_l=120,
        margin_r=140,
        margin_b=0,
        title_font_size=30,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.01,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Source: Pushshift API"
            ),
            dict(
                x=0.5,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="□: Start of the month"
            ),
            dict(
                x=1.01,
                y=0.04,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ]
    )

    fig.write_image("./1.png")


def plot_radar(args):
    """
    This function creates a radar chart that shows the distribution
    by hour of the day.
    """

    # We read our CSV file and make the isodate column our index.
    df = pd.read_csv(
        f"./{args.r}-{args.yr}.csv",
        parse_dates=["isodate"],
        index_col="isodate"
    )

    # For this plot We only need the hour, we extract it from the datetime index.
    df["hour"] = df.index.hour

    # We extract the value counts of each hour found into a Series.
    totals = df["hour"].value_counts().sort_index()

    # In order for the radar plot to work we need to create a 'skeleton' with all
    # the hours in the day (0-23).
    # We create this skeleton using a simple range. Then we will add the previously
    # created Series as the 'total' column.
    final = pd.DataFrame(index=np.arange(24), data={"total": totals})

    # To make the radar plot work we need to use categorical data for our
    # angular axis.
    final["label"] = final.index.map(lambda x: "{} hrs.".format(x))

    # This will be used for the legend.
    total = final["total"].sum()

    # IMPORTANT!
    # We need to duplicate the first value and append it to the bottom.
    # This is so the polygon can be closed, otherwise it will show a hole.
    final.loc[24] = final.iloc[0]

    # Fill NA values with 0, othersise you will have holes in the polygon.
    final["total"].fillna(0, inplace=True)

    fig = go.Figure()

    fig.add_traces(
        go.Scatterpolar(
            r=final["total"],
            theta=final["label"],
            name=f"Submissions ({total:,.0f})",
            line_width=4,
            fill="toself",
            line_color="hsl(73, 100%, 70%)",
            fillcolor="hsla(73, 100%, 70%, 0.15)",
        )
    )

    # For polar charts we don't have X or Y axes, we have
    # angular and radial axes which can be customized in a similar way.
    fig.update_polars(
        angularaxis_direction="clockwise",
        angularaxis_nticks=24,
        angularaxis_ticks="outside",
        angularaxis_ticklen=12,
        angularaxis_tickcolor="#FFFFFF",
        angularaxis_tickwidth=0.75,
        angularaxis_gridwidth=0.75,
        angularaxis_linewidth=2,
        radialaxis_gridwidth=0.75,
        radialaxis_separatethousands=True,
        bgcolor="#041C32",
    )

    fig.update_layout(
        showlegend=True,
        legend_orientation="h",
        legend_x=0.5,
        legend_y=-0.075,
        legend_xanchor="center",
        legend_yanchor="top",
        legend_borderwidth=1.5,
        width=1000,
        height=1000,
        font_family="Jura",
        font_color="#FFFFFF",
        font_size=16,
        title_text=f"Distribution of submissions in r/{args.r} during {args.yr} by hour (UTC)",
        title_x=0.5,
        title_y=0.96,
        margin_t=120,
        margin_l=0,
        margin_r=0,
        margin_b=120,
        title_font_size=22,
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.05,
                y=-0.12,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Source: Pushshift API",
            ),
            dict(
                x=0.96,
                y=-0.12,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ])

    fig.write_image(f"./2.png")


def plot_bars(args):
    """
    This function creates a simple vertical bar chart with the distribution by month.
    """

    # We read our CSV file and make the isodate column our index.
    df = pd.read_csv(
        f"./{args.r}-{args.yr}.csv",
        parse_dates=["isodate"],
        index_col="isodate"
    )

    # For this plot We only need the month, we extract it from the datetime index.
    df["month"] = df.index.month

    # We extract the value counts of each month found into a Series.
    totals = df["month"].value_counts().sort_index()

    # It is not strictly neccesary to create the skeleton for this plot
    # but I prefer to plot all the months eveh if we don't have data for them
    # as some people can get confused by the missing months.
    # we will use a simple range and add the 'total' column with the previous Series.
    final = pd.DataFrame(index=np.arange(1, 13), data={"total": totals})

    # Hard-coded abbreviations of the months.
    months_ticks = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
                    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
                    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

    fig = go.Figure()

    # As you will see, the 'total' column is used for several features
    # including the text on top of each bar and thei fill colors.
    fig.add_trace(
        go.Bar(
            x=final.index,
            y=final["total"],
            text=final["total"],
            texttemplate="%{y:,.0f}",
            textfont_size=24,
            marker_line_width=0,
            marker_color=final["total"],
            marker_colorscale="portland_r",
            textposition="outside"
        )
    )

    fig.update_xaxes(
        title="Month",
        ticktext=list(months_ticks.values()),
        tickvals=list(months_ticks.keys()),
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=20,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        mirror=True
    )

    fig.update_yaxes(
        title="Total submissions",
        range=[0, final["total"].max() * 1.1],
        ticks="outside",
        separatethousands=True,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        mirror=True
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=720,
        font_family="Jura",
        font_color="white",
        font_size=18,
        title_text=f"Distribution of submissions in r/{args.r} during {args.yr} by month (UTC)",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_l=100,
        margin_r=40,
        margin_b=90,
        title_font_size=24,
        plot_bgcolor="#041C32",
        paper_bgcolor="#04293A",
        annotations=[
            dict(
                x=0.01,
                y=-0.14,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Source: Pushshift API"
            ),
            dict(
                x=1.01,
                y=-0.14,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ])

    fig.write_image("./3.png")


def plot_donut(args):
    """
    This function creates a donut plot with a gauge effect
    # that shows the distribution by day of the week.
    """

    # We read our CSV file and make the isodate column our index.
    df = pd.read_csv(
        f"./{args.r}-{args.yr}.csv",
        parse_dates=["isodate"],
        index_col="isodate"
    )

    # For this plot We only need the day of the week, we extract it from the datetime index.
    df["weekday"] = df.index.weekday

    # We extract the value counts of each day of the week found into a Series.
    totals = df["weekday"].value_counts().sort_index()

    # Hard-coded names of the days of the week.
    days = {0: "Monday", 1: "Tuesday", 2: "Wednesday",
            3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    # The skeleton doesn't matter for this kind of plot, but we will use it for consistency. :P
    final = pd.DataFrame(index=np.arange(7), data={"total": totals})

    # We map the index to their respective labels.
    final.index = final.index.map(days)

    # We will calculate the percentages of each sector.
    final["perc"] = final["total"] / final["total"].sum() * 100

    # We create our labels for the legend.
    final["label"] = final.apply(
        lambda x: f"{x.name} ({x['total']:,.0f})", axis=1)

    fig = go.Figure()

    # We create a Pie chart and add some fancy customizations so it has
    # a hole and a thick border the same size as the plot background
    # giving the ilusion of segmentation.
    fig.add_trace(
        go.Pie(
            labels=final["label"],
            values=final["total"],
            text=final["perc"],
            texttemplate="%{text:.2f}%",
            hole=0.75,
            textposition="outside",
            marker_line_color="#04293A",
            marker_line_width=15,
        ))

    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_font_size=24,
        legend_x=0.5,
        legend_y=0.5,
        legend_xanchor="center",
        legend_yanchor="middle",
        width=1280,
        height=720,
        font_family="Jura",
        font_color="white",
        font_size=18,
        title_text=f"Distribution of submissions in r/{args.r} during {args.yr} by day of the week (UTC)",
        title_x=0.5,
        title_y=0.95,
        margin_t=100,
        margin_l=40,
        margin_r=40,
        margin_b=50,
        title_font_size=24,
        paper_bgcolor="#04293A",
        colorway=qualitative.Set3,
        annotations=[
            dict(
                x=0.01,
                y=-0.05,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Source: Pushshift API"
            ),
            dict(
                x=1.01,
                y=-0.05,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita"
            )
        ])

    fig.write_image("./4.png")


if __name__ == "__main__":

    plot_calendar(args)
    plot_radar(args)
    plot_bars(args)
    plot_donut(args)
