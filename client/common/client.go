package common

import (
	"fmt"
	"github.com/op/go-logging"
	"io"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	BatchSize     int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config    ClientConfig
	betReader *CsvBetReader
	sigc      chan os.Signal
	exit      bool
	conn      net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:    config,
		sigc:      make(chan os.Signal, 1),
		betReader: CreateBetReader(config.ID, config.BatchSize),
	}

	signal.Notify(client.sigc, syscall.SIGTERM)
	go func() {
		<-client.sigc
		client.exit = true
		log.Infof(
			"action: close | result: in_progress | client_id: %v ",
			client.config.ID,
		)
		if client.conn != nil {
			client.conn.Close()
		}
	}()

	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (c *Client) write(msg []byte) error {
	totalWritten := 0
	for totalWritten < len(msg) {
		written, err := c.conn.Write(msg[totalWritten:])
		if err != nil {
			return fmt.Errorf("error escribiendo en el socket: %w", err)
		}
		totalWritten += written
	}
	return nil
}

func (c *Client) sendBets() (int, error) {
	id := []byte(c.config.ID)
	idLength := []byte{'b', uint8(len(id))}
	msg := append(idLength, id...)

	bets, err := c.betReader.Read()

	if err != nil {
		return 0, err
	}

	msg = append(msg, uint8(len(bets)))
	for _, bet := range bets {
		encodedBet := bet.Encode()
		msg = append(msg, uint8(len(encodedBet)))
		msg = append(msg, encodedBet...)
	}

	err = c.write(msg)
	if err != nil {
		return 0, err
	}
	return len(bets), nil
}

func (c *Client) readResponse() (string, error) {
	message := make([]byte, 2)
	_, err := io.ReadFull(c.conn, message)
	if err != nil {
		return "", fmt.Errorf("failed to read message: %v", err)
	}
	if message[0] != 'a' {
		return "", fmt.Errorf("invalid response type: %x", message[0])
	}

	switch message[1] {
	case 0:
		return "ok", nil
	case 1:
		return "bad_request", nil
	default:
		return fmt.Sprintf("unknown response"), nil
	}
}

func (c *Client) requestWinners() (int, []string, error) {
	id := []byte(c.config.ID)
	idLength := []byte{'w', uint8(len(id))}
	msg := append(idLength, id...)

	err := c.write(msg)
	if err != nil {
		return 0, nil, err
	}

	message, err := io.ReadAll(c.conn)
	if err != nil {
		return 0, nil, fmt.Errorf("failed to read message: %v", err)
	}

	switch message[0] {
	case 0x77:
		winners, err := decodeWinners(message[1:])
		if err != nil {
			return 0, nil, fmt.Errorf("failed to decode message: %v", err)
		}
		return 1, winners, nil
	default:
		return 0, nil, nil
	}

}

func (c *Client) Close() {
	c.betReader.Close()
}

// Run Send a bet to the server
func (c *Client) Run() {
	readBets := 1
	for readBets > 0 {
		if c.exit {
			c.conn.Close()
			c.betReader.Close()
			return
		}

		err := c.createClientSocket()

		if err != nil {
			log.Errorf("action: connect | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		readBets, err = c.sendBets()

		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			c.conn.Close()
			c.betReader.Close()
		}

		resp, err := c.readResponse()

		if err != nil {
			log.Errorf("action: response | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
		} else {
			log.Infof("action: response | result: success | client_id: %v | response: %v",
				c.config.ID,
				resp,
			)
		}
	}
	c.betReader.Close()

	_, err := c.sendBets()
	if err != nil {
		log.Errorf("action: send_done | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	} else {
		log.Infof("action: send_done | result: success")
	}

	for {
		err := c.createClientSocket()

		if err != nil {
			log.Errorf("action: connect | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		ready, winners, err := c.requestWinners()
		if err != nil {
			log.Errorf("action: consulta_ganadores | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			break
		}
		if ready == 1 {
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(winners))
			c.conn.Close()
			return
		}

		c.conn.Close()
		time.Sleep(c.config.LoopPeriod)
	}
	c.conn.Close()
}
