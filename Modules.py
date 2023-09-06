from Info.Checker import get_info


def wallet() -> list:
    with open('wallet.txt', 'r') as file:
        wallets = file.read().splitlines()
        wallets = [wal.split(';') for wal in wallets]
        return wallets


def main():
    print(''' 
                        1) Chek address
    ''')
    modul = int(input('Какой модуль крутим: '))

    modules = {1: get_info
               }
    func = modules[modul]
    func()


if __name__ == '__main__':
    main()
