from bot          import Bot
from user         import User
from checkoutdata import PaymentInfo, PaymentChannel, PaymentChannelOptionInfo
from datetime     import datetime
from colorama     import Fore, Style, init
from time         import sleep
from datetime     import datetime
import os


init()
INFO = Fore.LIGHTBLUE_EX + "[*]" + Fore.BLUE
INPUT = Fore.LIGHTGREEN_EX + "[?]" + Fore.GREEN
PROMPT = Fore.LIGHTRED_EX + "[!]" + Fore.RED
if os.name.lower() == "nt":
    os.system("cls")
else:
    os.system("clear")
print(INFO, "Mengambil informasi user...", end='\r')
cookie = open("cookie.txt", 'r')
user = User.login(cookie.read())
cookie.close()
print(INFO, "Welcome", Fore.GREEN, user.name, ' ' * 10)
print()

print(INFO, "Masukan url barang yang akan dibeli")
bot = Bot(user)
item = bot.fetch_item_from_url(input(INPUT + " url: " + Fore.RESET))

print(Fore.RESET, "-" * 32)
print(Fore.LIGHTBLUE_EX, "Nama:", Fore.GREEN, item.name)
print(Fore.LIGHTBLUE_EX, "Harga:", Fore.GREEN, item.get_price(item.price))
print(Fore.LIGHTBLUE_EX, "Brand:", Fore.GREEN, item.brand)
print(Fore.LIGHTBLUE_EX, "Lokasi Toko:", Fore.GREEN, item.shop_location)
print(Fore.RESET, "-" * 32)
print()

selected_model = 0
if len(item.models) > 1:
    print(INFO, "Pilih model")
    print(Fore.RESET, "-" * 32)
    for index, model in enumerate(item.models):
        print(Fore.GREEN + '[' + str(index) + ']' + Fore.BLUE, model.name)
        print('\t', Fore.LIGHTBLUE_EX, "Harga:", Fore.GREEN, item.get_price(model.price))
        print('\t', Fore.LIGHTBLUE_EX, "Stok:", Fore.GREEN, model.stock)
        print('\t', Fore.LIGHTBLUE_EX, "ID Model:", Fore.GREEN, model.model_id)
        print(Fore.RESET, "-" * 32)
    print()
    selected_model = int(input(INPUT + " Pilihan: "))
    print()

print(INFO, "Pilih metode pembayaran")
payment_channels = dict(enumerate(PaymentChannel))
for index, channel in payment_channels.items():
    print(Fore.GREEN + '[' + str(index) + ']' + Fore.BLUE, channel.name)
print()
selected_payment_channel = payment_channels[int(input(INPUT + " Pilihan: "))]
print()

selected_option_info = PaymentChannelOptionInfo.NONE
if selected_payment_channel is PaymentChannel.TRANSFER_BANK or \
        selected_payment_channel is PaymentChannel.AKULAKU:
    options_info = dict(enumerate(list(PaymentChannelOptionInfo)[1 if selected_payment_channel is
                        PaymentChannel.TRANSFER_BANK else 7:None if selected_payment_channel is
                        PaymentChannel.AKULAKU else 7]))
    for index, option_info in options_info.items():
        print(str(index) + '.', option_info.name)
    selected_option_info = options_info[int(input(INPUT + " Pilihan: "))]

if not item.is_flash_sale:
    if item.upcoming_flash_sale is not None:
        flash_sale_start = datetime.fromtimestamp(item.upcoming_flash_sale.start_time)
        print(INFO, "Waktu Flash Sale: ", flash_sale_start.strftime("%H:%M:%S"))
        print(INFO, "Menunggu Flash Sale...", end='\r')
        sleep((datetime.fromtimestamp(item.upcoming_flash_sale.start_time) - datetime.now()).total_seconds())
    else:
        print(PROMPT, "Flash Sale telah Lewat!")
        exit(1)
print(INFO, "Flash Sale telah tiba")
start = datetime.now()
print(INFO, "Menambah item ke cart...")
cart_item = bot.add_to_cart(item, selected_model)
print(INFO, "Checkout item...")
bot.checkout(PaymentInfo(
    channel=selected_payment_channel,
    option_info=selected_option_info
), cart_item)
final = datetime.now() - start
print(INFO, "Item berhasil dibeli dalam waktu", Fore.YELLOW, final.seconds, "detik", final.microseconds // 1000,
      "milis")
print(Fore.GREEN + "[*]", "Sukses")
