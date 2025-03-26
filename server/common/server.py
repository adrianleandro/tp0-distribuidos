import socket
import logging
from signal import signal, SIGTERM

from common.response import Response
from common.utils import Bet, store_bets


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
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
            quantity, bets = self.__read_bets(client_sock)
            store_bets(bets)
            if quantity == len(bets):
                logging.info(f'action: apuesta_almacenada | result: success | cantidad: {quantity}')
            else:
                logging.error(f'action: apuesta_almacenada | result: error | cantidad: {quantity}')
            client_sock.send(Response.OK.encode())
        except OSError as e:
            logging.error(f'action: apuesta_almacenada | result: fail | error: {e}')
        except (ValueError, IndexError) as e:
            logging.error(f'action: apuesta_almacenada | result: fail | error: {e}')
            client_sock.send(Response.BAD_REQUEST.encode())
        finally:
            client_sock.close()

    def __read_bets(self, client_sock) -> (int, list[Bet]):
        msg = client_sock.recv(8192)
        bets = []
        if not msg:
            raise OSError('Connection closed')
        if chr(msg[0]) != 'b':
            raise ValueError('Bad message')
        agency_length = msg[1]
        agency = msg[2:2 + agency_length]
        bet_quantity = msg[2 + agency_length]
        offset = 2 + agency_length + 1
        for bet in range(bet_quantity):
            bet_length = msg[offset]
            offset += 1
            bet = Bet.decode(agency, msg[offset:offset+bet_length])
            offset += bet_length
            bets.append(bet)
        return bet_quantity, bets

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