import csv
import datetime
import logging
import time

""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574


""" A lottery bet registry. """
class Bet:
    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        self.agency = int(agency)
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = datetime.date.fromisoformat(birthdate)
        self.number = int(number)

    @classmethod
    def decode(cls, agency: str, message: bytes) -> (int, 'Bet'):
        def read_field(msg: bytes, index: int) -> tuple[str, int]:
            length = msg[index]
            field = msg[index + 1:index + 1 + length].decode('utf-8')
            return field, index + 1 + length

        idx = 0
        first_name, idx = read_field(message, idx)
        last_name, idx = read_field(message, idx)
        document, idx = read_field(message, idx)
        birth_date, idx = read_field(message, idx)
        number, idx = read_field(message, idx)
        if not first_name or not last_name or not document or not birth_date or not number:
            raise ValueError('Missing fields')

        return idx, Bet(agency, first_name, last_name, document, birth_date, number)

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])

def test_decode():
    message = bytes.fromhex('044A75616E05506572657A093132333435363738390A313939302D30352D3135023432')
    test_bet = Bet('1', 'Juan', 'Perez', '123456789', '1990-05-15', '42')
    decoded_bet = Bet.decode('1', message)
    assert decoded_bet.agency == test_bet.agency
    assert decoded_bet.first_name == test_bet.first_name
    assert decoded_bet.last_name == test_bet.last_name
    assert decoded_bet.document == test_bet.document
    assert decoded_bet.birthdate == test_bet.birthdate
    assert decoded_bet.number == test_bet.number
