import socket
import logging
from signal import signal, SIGTERM

from common.response import Response
from common.utils import Bet, store_bets, encode_winners

from server.common.utils import load_bets, has_won


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
        self._agencies = set()
        self.exit_program = False

    def signal_exit(self, signum, frame):
        self.exit_program = True

        if self._client_socket:
            self._client_socket.close()

        self._server_socket.close()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        signal(SIGTERM, self.signal_exit)
        while not self.exit_program:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError as e:
                if self.exit_program:
                    logging.info(f'action: close | result: success')


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = client_sock.recv(8192)
            if not msg:
                raise OSError('Connection closed')
            match chr(msg[0]):
                case 'b':
                    quantity, bets = self.__read_bets(msg[1:])
                    store_bets(bets)
                    if quantity == len(bets):
                        logging.info(f'action: apuesta_recibida | result: success | cantidad: {quantity}')
                    else:
                        logging.error(f'action: apuesta_recibida | result: error | cantidad: {quantity}')
                    client_sock.send(Response.OK.encode())
                case 'w':
                    agency = self.__read_winner_request(msg[1:])
                    if len(self._agencies) == 0:
                        logging.info(f'action: sorteo | result: success')
                        bets = load_bets()
                        winners = []
                        for bet in bets:
                            if has_won(bet) and bet.is_agency(agency):
                                winners.append(bet.document)
                        client_sock.send(encode_winners(winners))
                    else:
                        logging.info(f'action: sorteo | result: in_progress')
                case _:
                    raise ValueError('Bad message')
        except OSError as e:
            logging.error(f'action: apuesta_recibida | result: fail | error: {e}')
        except (ValueError, IndexError) as e:
            logging.error(f'action: apuesta_recibida | result: fail | error: {e}')
            client_sock.send(Response.BAD_REQUEST.encode())
        finally:
            client_sock.close()

    def __read_bets(self, msg) -> (int, list[Bet]):
        bets = []
        agency_length = msg[0]
        agency = msg[1:1 + agency_length]
        bet_quantity = msg[1 + agency_length]
        if bet_quantity > 0:
            self._agencies.add(agency)
            offset = 2 + agency_length
            for bet in range(bet_quantity):
                bet_length = msg[offset]
                offset += 1
                bet = Bet.decode(agency, msg[offset:offset + bet_length])
                offset += bet_length
                bets.append(bet)
        else:
            self._agencies.discard(agency)
        return bet_quantity, bets

    def __read_winner_request(self, msg) -> str:
        agency_length = msg[0]
        agency = msg[1:1 + agency_length]
        return agency


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        self._client_socket = c
        return c