package common

import (
	"bytes"
	"encoding/binary"
)

type Bet struct {
	FirstName string
	Surname   string
	Document  string
	Birthdate string
	Number    string
}

func (bet *Bet) Encode() []byte {
	var buffer bytes.Buffer

	binary.Write(&buffer, binary.BigEndian, uint8(len(bet.FirstName)))
	binary.Write(&buffer, binary.BigEndian, []byte(bet.FirstName))

	binary.Write(&buffer, binary.BigEndian, uint8(len(bet.Surname)))
	binary.Write(&buffer, binary.BigEndian, []byte(bet.Surname))

	binary.Write(&buffer, binary.BigEndian, uint8(len(bet.Document)))
	binary.Write(&buffer, binary.BigEndian, bet.Document)

	binary.Write(&buffer, binary.BigEndian, uint8(len(bet.Birthdate)))
	binary.Write(&buffer, binary.BigEndian, []byte(bet.Birthdate))

	binary.Write(&buffer, binary.BigEndian, uint8(len(bet.Number)))
	binary.Write(&buffer, binary.BigEndian, bet.Number)

	return buffer.Bytes()
}
