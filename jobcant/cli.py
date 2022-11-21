import argparse
import sys
from getpass import getpass

from jobcant import plotting
from jobcant.config import Config
from jobcant.jobcan import JobcanClient


def balance(exclude_last_day: bool) -> None:
    attendance_table = _get_attendance_table()
    month = attendance_table[:-1] if exclude_last_day else attendance_table
    print(f"Monthly overtime balance: {plotting.get_overtime_balance(month)}")

    if exclude_last_day:
        return

    last_day = attendance_table[-1]
    print("\nLast day:")
    print(f"  Clock-in: {last_day[2]}")
    print(f"  Working hours: {last_day[4]}")
    print(f"  Break: {last_day[5]}")


def when_to_leave() -> None:
    attendance_table = _get_attendance_table()
    leave_time, includes_break = plotting.get_leave_time(attendance_table)
    current_time = plotting.get_current_time(attendance_table)
    if leave_time <= current_time:
        print("Leave today as early as you like.")
        return

    break_msg = "(includes a 1-hour break)" if includes_break else "(break time not included)"
    print(f"Leave today at {leave_time} to avoid overtime {break_msg}.")


def update_config() -> None:
    jobcan_email = input("jobcan.email: ")
    jobcan_client_code = input("jobcan.clientCode: ")
    jobcan_password = getpass("jobcan.password: ")
    config = Config(
        jobcan_email=jobcan_email,
        jobcan_client_code=jobcan_client_code,
        jobcan_password=jobcan_password
    )
    config.save()


def graph(exclude_last_day: bool) -> None:
    attendance_table = _get_attendance_table()
    if exclude_last_day and len(attendance_table) > 1:
        attendance_table = attendance_table[:-1]
    days, history = plotting.get_overtime_history(attendance_table)
    plotting.plot_overtime_balance_history(days, history)


def main() -> None:
    parser = argparse.ArgumentParser(prog="jobcant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    balance_parser = subparsers.add_parser("balance", help="Calculate overtime balance")
    balance_parser.add_argument(
        "--exclude-last-day",
        action="store_true",
        help="Exclude last/current day from the calculation"
    )

    subparsers.add_parser("when", help="Calculate at which time to leave to avoid overtime this month")

    subparsers.add_parser("config", help="Init or update config")

    graph_parser = subparsers.add_parser("graph", help="Display a graph of overtime balance over the month")
    graph_parser.add_argument(
        "--exclude-last-day",
        action="store_true",
        help="Exclude last/current day from the graph"
    )

    args = parser.parse_args(sys.argv[1:])
    match args.command:
        case "balance":
            balance(exclude_last_day=args.exclude_last_day)
        case "when":
            when_to_leave()
        case "config":
            update_config()
        case "graph":
            graph(exclude_last_day=args.exclude_last_day)


def _get_attendance_table() -> list[list[str]]:
    config = Config.from_env() or Config.load()
    if not config:
        raise RuntimeError(f"No config found")

    jobcan_client = JobcanClient(
            email=config.jobcan_email,
            client_code=config.jobcan_client_code,
            password=config.jobcan_password
    )
    attendance_table = jobcan_client.get_attendance_table()
    # Remove rows without working hours
    attendance_table = [
        row for row in attendance_table
        if row[4]
    ]
    return attendance_table


if __name__ == "__main__":
    main()
