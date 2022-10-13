import argparse
import sys
from getpass import getpass

from jobcant import plotting
from jobcant.config import Config
from jobcant.jobcan import JobcanClient


def balance() -> None:
    attendance_table = _get_attendance_table()
    print(f"Monthly overtime balance: {plotting.get_overtime_balance(attendance_table)}")
    print(f"Weekly overtime balance: {plotting.get_overtime_balance(plotting.last_week(attendance_table))}")


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


def graph() -> None:
    attendance_table = _get_attendance_table()
    days, history = plotting.get_overtime_history(attendance_table)
    plotting.plot_overtime_balance_history(days, history)


def main() -> None:
    parser = argparse.ArgumentParser(prog="jobcant")
    parser.set_defaults(method=balance)
    subparsers = parser.add_subparsers(required=False)

    balance_parser = subparsers.add_parser("balance", help="Calculate overtime balance")
    balance_parser.set_defaults(method=balance)

    config_parser = subparsers.add_parser("config", help="Init or update config")
    config_parser.set_defaults(method=update_config)

    graph_parser = subparsers.add_parser("graph", help="Display a graph of overtime balance over the month")
    graph_parser.set_defaults(method=graph)

    args = parser.parse_args(sys.argv[1:])
    args.method()


def _get_attendance_table() -> list[list[str]]:
    config = Config.from_env() or Config.load()
    if not config:
        raise RuntimeError(f"No config found")

    jobcan_client = JobcanClient(
            email=config.jobcan_email,
            client_code=config.jobcan_client_code,
            password=config.jobcan_password
    )
    return jobcan_client.get_attendance_table()


if __name__ == "__main__":
    main()
