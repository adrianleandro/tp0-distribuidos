package common

import "fmt"

func decodeWinners(msg []byte) ([]string, error) {
	if len(msg) == 0 {
		return nil, fmt.Errorf("empty data")
	}

	totalWinners := int(msg[0])
	strings := make([]string, 0, totalWinners)
	pos := 1

	for i := 0; i < totalWinners; i++ {
		if pos >= len(msg) {
			return nil, fmt.Errorf("missing length byte")
		}

		strLen := int(msg[pos])
		pos++

		if pos+strLen > len(msg) {
			return nil, fmt.Errorf("string data invalid")
		}

		strBytes := msg[pos : pos+strLen]
		strings = append(strings, string(strBytes))
		pos += strLen
	}

	return strings, nil
}
