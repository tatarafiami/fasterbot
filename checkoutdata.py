from dataclasses import dataclass
from enum import Enum


class PaymentChannel(Enum):
    ALFAMART = 8003200
    INDOMART_ISAKU = 8003001
    AKULAKU = 8000700
    TRANSFER_BANK = 8005200
    COD_BAYAR_DI_TEMPAT = 89000


class PaymentChannelOptionInfo(Enum):
    NONE = ""
    # Transfer Bank
    TRANSFER_BANK_BCA_AUTO = "89052001"
    TRANSFER_BANK_MANDIRI_AUTO = "89052002"
    TRANSFER_BANK_BNI_AUTO = "89052003"
    TRANSFER_BANK_BRI_AUTO = "89052004"
    TRANSFER_BANK_SYARIAH_AUTO = "89052005"
    TRANSFER_BANK_PERMATA_AUTO = "89052006"

    # Akulaku
    AKULAKU_CICILAN_1X = "8000700-25"
    AKULAKU_CICILAN_2X = "8000700-26"
    # untested
    AKULAKU_CICILAN_3X = "8000700-27"
    AKULAKU_CICILAN_6X = "8000700-28"
    AKULAKU_CICILAN_9X = "8000700-29"
    AKULAKU_CICILAN_12X = "8000700-30"


@dataclass
class PaymentInfo:
    channel: PaymentChannel
    option_info: PaymentChannelOptionInfo = PaymentChannelOptionInfo.NONE


@dataclass
class CheckoutData:
    can_checkout: bool
    cart_type: int
    client_id: int
    shipping_orders: list
    disabled_checkout_info: dict
    checkout_price_data: dict
    promotion_data: dict
    dropshipping_info: dict
    selected_payment_channel_data: dict
    shoporders: list
    order_update_info: dict
    buyer_txn_fee_info: dict
    timestamp: int
