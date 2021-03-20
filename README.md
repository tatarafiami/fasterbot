# Requirement
- Python 3.7.x

Download python di https://www.python.org/downloads/
# Setup
Install modul `requests` dengan perintah berikut
```sh
pip install requests
```
jika sudah, buka chrome dan buka https://shopee.co.id/ lalu login.
tekan F12 lalu masuk tab network.

![tab network](images/tab_network.png)

refresh webpage dan cari item yang seperti berikut: `/`

![forward slash](images/forward_slash.png)

klik item dan klik kanan pada header "cookie" didalam "Request headers"

![copy header](images/copy_header.png)

lalu pilih `copy value`.

edit cookie.txt lalu paste dan save!

selesai/sudah siap login

jalankan scriptnya dengan perintah berikut
```
python main.py
```
