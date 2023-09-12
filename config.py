# ======================================================================================#
# =================| Общие настройки модулей |==========================================#
# ======================================================================================#

RETRY = 3  # кол-во попыток при ошибках/фейлах
THREAD = 5  # кол-во потоков

# если газ за транзу с этой сети будет выше в $, тогда скрипт будет спать 30с и пробовать снова
CHECK_GASS = True

MAX_GAS_CHARGE = {
    'ethereum': 5,
    'zksync': 3,
    'arbitrum': 1,
}

CHECK_GWEI = True  # перед работай чекает GWEI, если выше ожидаем GWEI

GWEI = 25


# =================================================================================================#
# =================|   Creating a route   |========================================================#
# =================================================================================================#

#######

# BitGet - Вывод с биржи

# OKX - Вывод с биржи

# ZK_bridge - off бридж с эфира в зк

Deposit = 'OKX'  # OKX, BitGet, ZK_bridge( bridge + OKX), None - не нужен вывод

#########

# Merkly  - Бридж через мост Merkly из Zksync

# Wrapped_ETH - Обёртывание Эфира

# DEX - свапы и залив ликвидности на разных площадках

# Domains_Name - минт домена на https://app.zkns.domains/ (цена домена +- 5$)

# Deploy_Contract - деплоим контракт

# Lending_Protocol - работа по протоколу https://app.reactorfusion.xyz/

# NFT - mint NFT Tevaera https://tevaera.com/ (2 штуки)

# DMAIL - спам сообщений (дешёвый набив тх) https://mail.dmail.ai/

Route = ["DEX", 'NFT', 'Deploy_Contract', 'Wrapped_ETH', 'Merkly', "DMAIL", "Lending_Protocol"]

#########

# Withdraw - Вывод ETH (ethereum, zksync)

# Orbiter - Вывод через Orbiter zksync -> arbitrum -> OKX

# Across - Вывод через Across zksync -> arbitrum -> OKX


Withdraw = True

Orbiter = False

Across = True


# ======================================================================================#
# =================| BitGet    |========================================================#
# ======================================================================================#


api_BitGet = ''

secret_BitGet = ''

pass_BitGet = ''

BitGet_AMOUNT = [0.001, 0.0015]  # обьём вывода ETH

BitGet_CHAIN = 'zksync'  # ethereum, zksync

# ======================================================================================#
# =================| OKX    |========================================================#
# ======================================================================================#

OKX_api_key = ''

OKX_secret_key = ''

OKX_password = ''

OKX_CHAIN = ['zksync']  # ethereum, zksync

OKX_AMOUNT = [0.5349, 0.5349]  # обьём вывода ETH


# ======================================================================================#
# =================| Wrapped_ETH  |========================================================#
# ======================================================================================#

WRAP_VALUE = [0.49, 0.5]  # объмы обёртывания

WRAP_AMOUNT = 5  # колличество заходов


# ======================================================================================#
# =================| DEX  |========================================================#
# ======================================================================================#

# "Izumi", "Mute", "Odos", "Openocean", "Syncswap", "Zkswap", "Spacefi"

WORK_DEX = ["Izumi", "Mute", "Openocean", "Syncswap", "Zkswap", 'Spacefi', "Odos"]  # список площадок с какими работаем

DEX_TOKEN = ['ETH', 'USDC']  # токены которые бьудут в работе 'ETH', 'USDC', 'BUSD'

DEX_VALUE = [2, 5]  # обёмы свапов в $

DEX_AMOUNT = [8, 10]  # колличество свапов

DEX_SLEEP = [10, 15]


# ======================================================================================#
# =================| ZK Bridge  |========================================================#
# ======================================================================================#

VALUE_BRIDGE = [0.001, 0.003]  # объём бриджа в ETH


# ======================================================================================#
# =================| Merkly  |========================================================#
# ======================================================================================#


TX_MERKLY = [1, 1]  # колличество транзакции

VALUE_MERKLY = [0.03, 0.03]  # объём бриджа

SLEEP_MERKLY = [20, 30]  # зедержка между бриджами


# ======================================================================================#
# =================| Withdraw  |========================================================#
# ======================================================================================#

# Если выводим через орбитер то оставляет остаток BALANCE_WALLET

CHAIN_WITHDRAW = ['zksync']  # 'ethereum', 'zksync'

BALANCE_WALLET = [9, 10]  # остаток на балансе (если не нужно ничего осталять, оставить пустой список)



# ======================================================================================#
# =================| NFT |========================================================#
# ======================================================================================#

NFT_AMOUNT = [2, 2]  # сколько минтим, максимум 2


# ======================================================================================#
# =================| Lending Protocol  |========================================================#
# ======================================================================================#

LENDING_VOLUME = [0.5, 0.52]  # бъём прогона в ETH

LENDING_AMOUNT = 4  # Колличество проходов


# ======================================================================================#
# =================| DMAIL  |========================================================#
# ======================================================================================#

DMAIL_AMOUNT = [2, 4]


# ======================================================================================#
# =================| Auto  |========================================================#
# ======================================================================================#


Range_Operation = 1  # промежуток работы прогрева кошельков (число - колличество дней)

Tx_Operation = [2, 3]  # колличество Tx за 1 проход

