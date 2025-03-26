package common

import (
	"fmt"
	"github.com/op/go-logging"
	"net"
	"os"
	"os/signal"
	"syscall"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	bet    Bet
	sigc   chan os.Signal
	exit   bool
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, bet Bet) *Client {
	client := &Client{
		config: config,
		sigc:   make(chan os.Signal, 1),
		bet:    bet,
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

func (c *Client) placeBet() error {
	msg := c.bet.Encode()
	written, err := c.conn.Write(msg)
	if err != nil {
		return err
	}
	if written != len(msg) {
		return fmt.Errorf("partial write")
	}
	return nil
}

// Run Send a bet to the server
func (c *Client) Run() {
	if c.exit {
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

	err = c.placeBet()

	if err != nil {
		log.Errorf("action: send_bet | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	c.conn.Close()

	log.Infof("action: send_bet | result: success | client_id: %v",
		c.config.ID,
	)
}
