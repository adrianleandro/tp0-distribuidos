package common

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

const DataSeparator = ","

type CsvBetReader struct {
	file        *os.File
	scanner     *bufio.Scanner
	batchSize   int
	batchOffset int
}

func CreateBetReader(ID string, batchSize int) *CsvBetReader {
	filePath := fmt.Sprintf("/.data/agency-%s.csv", ID)
	file, err := os.Open(filePath)

	if err != nil {
		log.Fatal("Error opening data file: ", err)
		return nil
	}

	return &CsvBetReader{
		file:        file,
		batchSize:   100,
		batchOffset: 0,
		scanner:     bufio.NewScanner(file),
	}
}

func (br *CsvBetReader) Read() ([]Bet, error) {
	var bets []Bet
	var i int

	for i = br.batchOffset; i < br.batchOffset+br.batchSize && br.scanner.Scan(); i++ {
		line := br.scanner.Text()
		data := strings.Split(line, DataSeparator)
		if len(data) != 5 {
			return bets, fmt.Errorf("invalid csv line: %s", line)
		}
		bet := Bet{
			FirstName: data[0],
			Surname:   data[1],
			Document:  data[2],
			Birthdate: data[3],
			Number:    data[4],
		}
		bets = append(bets, bet)
	}
	br.batchOffset = i

	if err := br.scanner.Err(); err != nil {
		return bets, err
	}
	return bets, nil
}

func (br *CsvBetReader) Close() {
	br.file.Close()
}
