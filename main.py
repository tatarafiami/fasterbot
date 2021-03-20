from bot import Bot
from user import User
from checkoutdata import PaymentInfo, PaymentChannel, PaymentChannelOptionInfo


print("Mengambil informasi user...", end='\r')
cookie = open("cookie.txt", 'r')
user = User.login(cookie.read())
cookie.close()
print("Welcome", user.name, ' ' * 10)
print()

print("Masukan url barang yang akan dibeli")
url = input("url: ")
bot = Bot(user)
item = bot.fetch_item_from_url(url)

print("-" * 32)
print("Nama:", item.name)
print("Harga:", item.get_price(item.price))
print("Brand:", item.brand)
print("Lokasi Toko:", item.shop_location)
print("-" * 32)
print()

selected_model = 0
if len(item.models) > 1:
    print("Pilih model")
    print("-" * 32)
    for index, model in enumerate(item.models):
        print(str(index) + '.', model.name)
        print('\t', "Harga:", item.get_price(model.price))
        print('\t', "Stok:", model.stock)
        print('\t', "ID Model:", model.model_id)
        print("-" * 32)
    print()
    selected_model = int(input("Pilihan: "))

print("Pilih metode pembayaran")
payment_channels = dict(enumerate(PaymentChannel))
for index, channel in payment_channels.items():
    print(str(index) + '.', channel.name)
selected_payment_channel = payment_channels[int(input("Pilihan: "))]
print()

selected_option_info = PaymentChannelOptionInfo.NONE
if selected_payment_channel is PaymentChannel.TRANSFER_BANK or \
        selected_payment_channel is PaymentChannel.AKULAKU:
    options_info = dict(enumerate(list(PaymentChannelOptionInfo)[1 if selected_payment_channel is
                        PaymentChannel.TRANSFER_BANK else 7:None if selected_payment_channel is
                        PaymentChannel.AKULAKU else 7]))
    for index, option_info in options_info.items():
        print(str(index) + '.', option_info.name)
    selected_option_info = options_info[int(input("Pilihan: "))]

input("Catatan: Tunggu 1 menit sebelum Flash Sale tiba, lalu tekan Enter")

print("Menunggu Flash Sale tiba...")
while not item.is_flash_sale:
    item = bot.fetch_item_from_url(url)
print("Flash Sale telah tiba")
print("Menambah item ke cart...")
bot.add_to_cart(item, selected_model)
print("Checkout item...")
bot.checkout(PaymentInfo(
    channel=selected_payment_channel,
    option_info=selected_option_info
), item, selected_model)
print("Sukses")
