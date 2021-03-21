from urllib.parse import urlencode
from item import *
from user import User
from json import dumps
from re import search
from time import time
from checkoutdata import *
import requests


class Bot:
    user: User

    def __init__(self, user: User):
        self.user = user

    def fetch_item_from_url(self, url: str) -> Item:
        """
                :param url: the item url
                :return: Item object
                the url will definitely be one of these:
                    - https://shopee.co.id/product/xxxx/xxxx
                    - https://shopee.co.id/Item-Name.xxxx.xxxx
                """
        match = search(r"(?:.*\.(\d+)\.(\d+))|(?:.*/(\d+)/(\d+).*?)", url)
        if match is None:
            raise ValueError("unexpected url")

        return self.fetch_item(int(match.group(2)), int(match.group(1)))

    def fetch_item(self, item_id: int, shop_id: int) -> Item:
        resp = requests.get(
            "https://shopee.co.id/api/v2/item/get?" + urlencode({
                "itemid": item_id,
                "shopid": shop_id
            }),
            headers={
                "Host": "shopee.co.id",
                "Accept": "*/*",
                "User-Agent": self.user.USER_AGENT,
                "Referer": "https://shopee.co.id/",
                "Cookie": self.user.cookie,
                "if-none-match-": "*"
            }
        )
        item_data = resp.json()["item"]
        if item_data is None:
            raise NameError("item not found")
        return Item(
            item_id=item_data["itemid"],
            shop_id=item_data["shopid"],
            models=[Model(
                currency=model["currency"],
                item_id=model["itemid"],
                model_id=model["modelid"],
                promotion_id=model["promotionid"],
                name=model["name"],
                price=model["price"],
                stock=model["stock"]
            ) for model in item_data["models"]],
            name=item_data["name"],
            price=item_data["price"],
            price_before_discount=item_data["price_before_discount"],
            brand=item_data["brand"],
            shop_location=item_data["shop_location"],
            flash_sale=FlashSaleInfo(
                discount=item_data["flash_sale"]["discount"],
                end_time=item_data["flash_sale"]["end_time"],
                flash_catid=item_data["flash_sale"]["flash_catid"],
                flash_sale_stock=item_data["flash_sale"]["flash_sale_stock"],
                hidden_price_display=item_data["flash_sale"]["hidden_price_display"],
                item_id=item_data["flash_sale"]["itemid"],
                model_ids=item_data["flash_sale"]["modelids"],
                name=item_data["flash_sale"]["name"],
                price=item_data["flash_sale"]["price"],
                price_before_discount=item_data["flash_sale"]["price_before_discount"],
                promo_name=item_data["flash_sale"]["promo_name"],
                promotion_id=item_data["flash_sale"]["promotionid"],
                raw_discount=item_data["flash_sale"]["raw_discount"],
                shop_id=item_data["flash_sale"]["shopid"],
                start_time=item_data["flash_sale"]["start_time"],
                stock=item_data["flash_sale"]["stock"]
            ) if item_data["flash_sale"] is not None else None,
            add_on_deal_info=AddOnDealInfo(
                add_on_deal_id=item_data["add_on_deal_info"]["add_on_deal_id"],
                add_on_deal_label=item_data["add_on_deal_info"]["add_on_deal_label"],
                sub_type=item_data["add_on_deal_info"]["sub_type"]
            ) if item_data["add_on_deal_info"] is not None else AddOnDealInfo(),
            price_min=item_data["price_min"],
            price_max=item_data["price_max"],
            stock=item_data["stock"],
            is_flash_sale=item_data["flash_sale"] is not None
        )

    def add_to_cart(self, item: Item, model_index: int):
        if not item.models[model_index].is_available():
            raise Exception("out of stock")
        resp = requests.post(
            url="https://shopee.co.id/api/v2/cart/add_to_cart",
            headers={
                "Accept": "application/json",
                "Referer": "https://shopee.co.id/",
                "Cookie": self.user.cookie,
                "User-Agent": self.user.USER_AGENT,
                "X-Csrftoken": self.user.csrf_token,
                "Content-Type": "application/json"
            },
            data=dumps({
                "checkout": True,
                "client_source": 1,
                "donot_add_quantity": False,
                "itemid": item.item_id,
                "modelid": item.models[model_index].model_id,
                "quantity": 1,
                "shopid": item.shop_id,
                "source": "",
                "update_checkout_only": False
            })
        )
        error = resp.json()['error']
        if error != 0:
            print("modelid:", item.models[0].model_id)
            print(resp.text)
            raise Exception(f"failed to add to cart {error}")

    def fetch_cart_item(self, item: Item) -> CartItem:
        resp = requests.post(
            url="https://shopee.co.id/api/v4/cart/mini",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": self.user.cookie,
                "if-none-match-": "*",
                "Referer": "https://shopee.co.id/",
                "User-Agent": self.user.USER_AGENT,
                "X-Csrftoken": self.user.csrf_token
            }
        )
        data = resp.json()
        if data["error"] != 0:
            print(resp.text)
            raise Exception("failed to fetch cart item")
        for cart_item in data["data"]["recent_cart_item_details"]:
            if cart_item["itemid"] == item.item_id:
                return CartItem(
                    add_on_deal_id=cart_item["add_on_deal_id"],
                    item_group_id=cart_item["item_group_id"],
                    item_id=cart_item["itemid"],
                    model_name=cart_item["model_name"],
                    model_id=cart_item["modelid"],
                    name=cart_item["name"],
                    price=cart_item["price"],
                    shop_id=cart_item["shopid"],
                    stock=cart_item["stock"]
                )

    def __checkout_get(self, payment: PaymentInfo, item: Item, model_index: int) -> CheckoutData:
        item_group_id = self.fetch_cart_item(item).item_group_id
        resp = requests.post(
            url="https://shopee.co.id/api/v2/checkout/get",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": self.user.cookie,
                "User-Agent": self.user.USER_AGENT,
                "Referer": "https://shopee.co.id/",
                "X-Csrftoken": self.user.csrf_token,
                "if-none-match-": "*"
            },
            # TODO: Implement all original data
            data=dumps({
                "cart_type": 0,
                "client_id": 0,
                "device_info": {
                    "buyer_payment_info": {},
                    "device_fingerprint": "",
                    "device_id": "",
                    "tongdun_blackbox": ""
                },
                "dropshipping_info": {
                    "enabled": False,
                    "name": "",
                    "phone_number": ""
                },
                "order_update_info": {},
                "promotion_data": {
                    "auto_apply_shop_voucher": False,
                    "check_shop_voucher_entrances": True,
                    "free_shipping_voucher_info": {
                        "disabled_reason": None,
                        "free_shipping_voucher_code": "",
                        "free_shipping_voucher_id": 0
                    },
                    "platform_voucher": [],
                    "shop_voucher": [],
                    "use_coins": False
                },
                "selected_payment_channel_data": {
                    "channel_id": payment.channel.value,
                    "channel_item_option_info": {"option_info": payment.option_info.value},
                    "version": 2
                },
                "shipping_orders": [{
                    "buyer_address_data": {
                        "address_type": 0,
                        "addressid": self.user.default_address.id,
                        "error_status": "",
                        "tax_address": ""
                    },
                    "buyer_ic_number": "",
                    "logistics": {
                        "recommended_channelids": None
                    },
                    "selected_preferred_delivery_instructions": {},
                    "selected_preferred_delivery_time_option_id": 0,
                    "selected_preferred_delivery_time_slot_id": None,
                    "shipping_id": 1,
                    "shoporder_indexes": [0],
                    "sync": True
                }],
                "shoporders": [{
                    "buyer_address_data": {
                        "address_type": 0,
                        "addressid": self.user.default_address.id,
                        "error_status": "",
                        "tax_address": ""
                    },
                    "items": [{
                        "add_on_deal_id": item.add_on_deal_info.add_on_deal_id,
                        "is_add_on_sub_item": False,
                        "item_group_id": item_group_id,
                        "itemid": item.item_id,
                        "modelid": item.models[model_index].model_id,
                        "quantity": 1
                    }],
                    "logistics": {
                        "recommended_channelids": None
                    },
                    "selected_preferred_delivery_instructions": {},
                    "selected_preferred_delivery_time_option_id": 0,
                    "selected_preferred_delivery_time_slot_id": None,
                    "shipping_id": 1,
                    "shop": {"shopid": item.shop_id}
                }],
                "tax_info": {
                    "tax_id": ""
                },
                "timestamp": time()
            })
        )

        if not resp.ok:
            print(resp.text)
            raise Exception("failed to get checkout info")
        data = resp.json()
        return CheckoutData(
            can_checkout=data["can_checkout"],
            cart_type=data["cart_type"],
            client_id=data["client_id"],
            shipping_orders=data["shipping_orders"],
            disabled_checkout_info=data["disabled_checkout_info"],
            checkout_price_data=data["checkout_price_data"],
            promotion_data=data["promotion_data"],
            dropshipping_info=data["dropshipping_info"],
            selected_payment_channel_data=data["selected_payment_channel_data"],
            shoporders=data["shoporders"],
            order_update_info=data["order_update_info"],
            buyer_txn_fee_info=data["buyer_txn_fee_info"],
            timestamp=data["timestamp"]
        )

    def checkout(self, payment: PaymentInfo, item: Item, model_index: int):
        data = self.__checkout_get(payment, item, model_index)
        resp = requests.post(
            url="https://shopee.co.id/api/v2/checkout/place_order",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": self.user.cookie,
                "Referer": "https://shopee.co.id/",
                "User-Agent": self.user.USER_AGENT,
                "X-Csrftoken": self.user.csrf_token,
                "if-none-match-": "*"
            },
            data=dumps({
                "status": 200,
                "headers": {},
                "cart_type": data.cart_type,
                "shipping_orders": data.shipping_orders,
                "disabled_checkout_info": data.disabled_checkout_info,
                "timestamp": data.timestamp,
                "checkout_price_data": data.checkout_price_data,
                "client_id": data.client_id,
                "promotion_data": data.promotion_data,
                "dropshipping_info": data.dropshipping_info,
                "selected_payment_channel_data": data.selected_payment_channel_data,
                "shoporders": data.shoporders,
                "can_checkout": data.can_checkout,
                "order_update_info": data.order_update_info,
                "buyer_txn_fee_info": data.buyer_txn_fee_info
            })
        )
        if "error" in resp.json():
            print(resp.text)
            raise Exception("failed to checkout")

    def buy(self, item: Item, model_index: int, payment: PaymentInfo):
        self.add_to_cart(item, model_index)
        self.checkout(payment, item, model_index)

    def remove_item_from_cart(self, cart_item: CartItem):
        resp = requests.post(
            url="https://shopee.co.id/api/v4/cart/update",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": self.user.cookie,
                "if-none-match-": "*",
                "Referer": "https://shopee.co.id/cart",
                "User-Agent": self.user.USER_AGENT,
                "X-Csrftoken": self.user.csrf_token
            },
            data=dumps({
                "action_type": 2,
                "updated_shop_order_ids": [
                    {
                        "item_briefs": [
                            {
                                "add_on_deal_id": cart_item.add_on_deal_id,
                                "checkout": False,
                                "item_group_id": cart_item.item_group_id,
                                "itemid": cart_item.item_id,
                                "modelid": cart_item.model_id,
                                "price": cart_item.price,
                                "shopid": cart_item.shop_id
                            }
                        ],
                        "shopid": cart_item.shop_id
                    }
                ]
            })
        )
        if resp.json()["error"] != 0:
            raise Exception("failed to remove item from cart")
