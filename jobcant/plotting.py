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


def get_today_last_clock_in(attendance_table: list[list[str]]) -> Duration:
    return Duration.parse(attendance_table[-1][2])


def get_today_working_hours(attendance_table: list[list[str]]) -> Duration:
    return Duration.parse(attendance_table[-1][4])


def get_today_break_length(attendance_table: list[list[str]]) -> Duration:
    return Duration.parse(attendance_table[-1][5])


def get_current_time(attendance_table: list[list[str]]) -> Duration:
    return (
        get_today_last_clock_in(attendance_table) +
        get_today_break_length(attendance_table) +
        get_today_working_hours(attendance_table)
    )


def get_leave_time(attendance_table: list[list[str]]) -> tuple[Duration, bool]:
    day_base_hours = Duration(8 * 60)
    min_hours_for_mandatory_break = Duration(6 * 60)
    overtime_balance = get_overtime_balance(attendance_table[:-1])
    last_clock_in = get_today_last_clock_in(attendance_table)
    today_break = get_today_break_length(attendance_table)

    leave_time = last_clock_in + day_base_hours - overtime_balance

    # When more than 6 hours must be achieved during the day,
    # add a mandatory 1-hour break time.
    required_today = day_base_hours - overtime_balance
    if (required_today > min_hours_for_mandatory_break) or (today_break > Duration(0)):
        leave_time += Duration(60)
        return leave_time, True

    return leave_time, False


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
