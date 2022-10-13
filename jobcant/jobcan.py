import os

import requests
from bs4 import BeautifulSoup


class JobcanClient:
    def __init__(self, email: str, client_code: str | None, password: str):
        self._email: str = email
        self._client_code: str | None = client_code
        self._password: str = password

    def get_attendance_table(self) -> list[list[str]]:
        response = requests.get("https://id.jobcan.jp/users/sign_in")
        soup = BeautifulSoup(response.text, "html.parser")
        token = soup.find("input", attrs={
            "name": "authenticity_token"
        })["value"]
        cookies = response.cookies.get_dict()

        params = {
            "authenticity_token": token,
            "user[email]": self._email,
            "user[password]": self._password
        }
        if self._client_code:
            params["user[client_code]"] = self._client_code

        response = requests.post(
                "https://id.jobcan.jp/users/sign_in",
                params=params,
                cookies=cookies,
                allow_redirects=False
        )
        cookies2 = response.cookies.get_dict()
        if "logged_in_users" not in cookies2:
            raise ValueError("Invalid login")

        response = requests.get("https://ssl.jobcan.jp/jbcoauth/login", allow_redirects=False)
        client_id_location = response.headers["Location"]

        response = requests.get(client_id_location, cookies=cookies2, allow_redirects=False)
        code_location = response.headers["Location"]

        response = requests.get(code_location, allow_redirects=False)
        sid = response.cookies.get_dict()

        response = requests.get("https://ssl.jobcan.jp/employee/attendance", cookies=sid)
        soup = BeautifulSoup(response.text, "html.parser")
        table_body = soup.select("#search-result>.table-responsive tbody")[0]
        return [
            [
                column.text
                for column in row.find_all("td")
            ]
            for row in table_body.find_all("tr")
        ]
