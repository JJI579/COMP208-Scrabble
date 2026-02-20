import type { UserReturn } from "./types"

type Tile = {
	letter: string,
	points: number
}
type PlacedTile = Tile & {
	coordinate: [number, number],
}

type GameUser = UserReturn & {
	placed: []
	points: number
}


export type { Tile, PlacedTile, GameUser };