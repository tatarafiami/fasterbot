from dataclasses import dataclass
from typing import Final
import requests


@dataclass
class Address:
    address: str
    city: str
    country: str
    district: str
    formatted_address: str
    full_address: str
    geo_string: str
    id: int
    name: str
    phone: str
    state: str
    town: str
    zipcode: int


@dataclass
class User:
    userid: int
    shopid: int
    name: str
    email: str
    phone: str
    phone_verified: bool
    default_address: Address
    cookie: str
    csrf_token: str
    with open("user_agent.txt", 'r') as __user_agent:
        USER_AGENT: Final[str] = __user_agent.read()

    @staticmethod
    def login(cookie: str):
        resp = requests.get(
            "https://shopee.co.id/api/v1/account_info",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://shopee.co.id/",
                "User-Agent": User.USER_AGENT,
                "Cookie": cookie
            }
        )
        data = resp.json()
        if len(data) == 0:
            raise Exception("failed to login, invalid cookie")
        csrf_token = None
        for cookie1 in cookie.split(';'):
            key_value = cookie1.split('=')
            if key_value[0].strip() == "csrftoken":
                csrf_token = key_value[1]
                break
        return User(
            userid=data["userid"],
            shopid=data["shopid"],
            name=data["username"],
            email=data["email"],
            phone=data["phone"],
            phone_verified=data["phone_verified"],
            default_address=Address(
                address=data["default_address"]["address"],
                city=data["default_address"]["city"],
                country=data["default_address"]["country"],
                district=data["default_address"]["district"],
                formatted_address=data["default_address"]["formattedAddress"],
                full_address=data["default_address"]["full_address"],
                geo_string=data["default_address"]["geoString"],
                id=data["default_address"]["id"],
                name=data["default_address"]["name"],
                phone=data["default_address"]["phone"],
                state=data["default_address"]["state"],
                town=data["default_address"]["town"],
                zipcode=data["default_address"]["zipcode"]
            ),
            cookie=cookie,
            csrf_token=csrf_token
        )
