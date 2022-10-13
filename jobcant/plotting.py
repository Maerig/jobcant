import plotly.graph_objects as go

from jobcant.duration import Duration


def get_overtime_history(attendance_table: list[list[str]]) -> tuple[list[str], list[Duration]]:
    days = []
    overtime_history = []
    for row in attendance_table:
        if not row[4]:
            continue

        days.append(row[0])
        working_hours = Duration.parse(row[4])
        overtime_history.append(working_hours - Duration(8 * 60))

    return days, overtime_history


def get_overtime_balance(attendance_table: list[list[str]]) -> Duration:
    _, history = get_overtime_history(attendance_table)
    return sum(history, Duration())


def last_week(attendance_table: list[list[str]]) -> list[list[str]]:
    last_week_rows: list[list[str]] = []
    for row in reversed(attendance_table):
        # Iterate until last worked day
        if not (last_week_rows or row[4]):
            continue
        last_week_rows = [row] + last_week_rows
        if row[0].endswith("(Mon)"):
            break

    return last_week_rows


def plot_overtime_balance_history(days: list[str], overtime_history: list[Duration]) -> None:
    cumulative_overtime_history = []
    for overtime in overtime_history:
        last_cumulative_overtime = (
            cumulative_overtime_history[-1] if cumulative_overtime_history
            else Duration()
        )
        cumulative_overtime_history.append(last_cumulative_overtime + overtime)

    fig = go.Figure(
            data=go.Scatter(
                x=days,
                y=[duration.minutes for duration in cumulative_overtime_history],
                mode="lines+markers"
            )
    )
    fig.update_layout(
        yaxis_title="Overtime balance (minutes)"
    )
    fig.show()
