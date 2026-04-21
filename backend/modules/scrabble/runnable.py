from newscrab import Scrabble, Turn, Letter, LetterPlace, Coordinate, DirectionValue, ModifierValue, Modifier

def generate_turn(startCoordinate: Coordinate, word: str, direction: DirectionValue) -> Turn:
	# Generate a turn with random letters and direction

	coordinate = startCoordinate
	letters = []
	for letter in word:
		letters.append(LetterPlace(coordinate=coordinate, letter=Letter(letter=letter, isBlank=False)))

		# For next word
		if direction == DirectionValue.DOWN:
			coordinate = Coordinate(x=coordinate.x, y=coordinate.y + 1)
		else:
			coordinate = Coordinate(x=coordinate.x + 1, y=coordinate.y)

	return Turn(letters=letters, direction=direction)



if __name__ == "__main__":
	x = Scrabble()
	turn = generate_turn(Coordinate(x=7, y=7), "HELLO", DirectionValue.RIGHT)
	turn2 = generate_turn(Coordinate(x=7, y=8), "ELP", DirectionValue.DOWN)
	turn3 = generate_turn(Coordinate(x=8, y=9), "INT", DirectionValue.RIGHT)
	
	x.place_word(turn)
	x.print_board()
	x.place_word(turn2)
	x.print_board()
	x.place_word(turn3)
	x.print_board()
	# do stuff