from dataclasses import dataclass
from typing import List


@dataclass
class Model:
    currency: str
    item_id: int
    model_id: int
    promotion_id: int
    name: str
    price: int
    stock: int

    def is_available(self):
        return self.stock != 0


@dataclass
class FlashSaleInfo:
    discount: str
    end_time: int
    flash_catid: int
    flash_sale_stock: int
    hidden_price_display: str
    item_id: int
    model_ids: list
    name: str
    price: int
    price_before_discount: int
    promo_name: str
    promotion_id: int
    raw_discount: int
    shop_id: int
    start_time: int
    stock: int


@dataclass
class AddOnDealInfo:
    add_on_deal_id: int = 0
    add_on_deal_label: str = ""
    sub_type: int = 0


@dataclass
class TierVariationInfo:
    name: str
    options: list
    properties: list


@dataclass
class Item:
    item_id: int
    shop_id: int
    models: List[Model]
    name: str
    price: int
    price_before_discount: int
    brand: str
    shop_location: str

    # prepared for the future (if needed)
    flash_sale: FlashSaleInfo
    add_on_deal_info: AddOnDealInfo
    price_min: int
    price_max: int
    stock: int
    is_flash_sale: bool

    @staticmethod
    def get_price(price) -> int:
        return price // 99999


@dataclass
class CartItem:
    add_on_deal_id: int
    item_group_id: str
    item_id: int
    model_name: str
    model_id: int
    name: str
    price: int
    shop_id: int
    stock: int
