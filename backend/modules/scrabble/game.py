from .scrabble import Scrabble, arr
from modules.schema import UserFetch, GameOptions, GamePlayer, GAME_TYPE, BotPlayer
import copy
import datetime

class Game:

    def __init__(self, gameID: str, options: GameOptions, leaderID: int) -> None:
        self.id = gameID
        self.leader = leaderID
        self.options = options.model_dump(mode="json")
        self.bot_difficulty = options.bot_difficulty if options.bot_difficulty else "hard"
        self.game = Scrabble(copy.deepcopy(arr), bot_difficulty=self.bot_difficulty)
        self.type: GAME_TYPE = options.game_type
        self.players: list[GamePlayer | BotPlayer] = []
        self.hasStarted = False
        self.groups = []
        if self.type == "GROUP":
            if options.group_size:
                self.groups: list[list[int]] = [[] for _ in range(options.group_size)] # makes array of groups
            else:
                raise Exception("Group size not specified")
        elif self.type == "BOT":
            self.bot = True
        self.dictionary_allowed = options.dictionary
        if type(options.time_limit) == int:
            self.time_limit: int = options.time_limit
        else:
            raise Exception("Time limit has been set wrong")
        # index of the group leaders in self.groupPlayers
        self.groupTurn = 0
        # group leader's userID
        self.groupPlayers = []
        self.finishesAt = 0
        self.partners = {}
        self.skip_counts: dict[int, int] = {}
    
    def mm_give_points(self, points: int):
        """ 
        Gives the current player points.

        Args:
            points (int): The number of points to give.

            Returns:
            int: The number of points given.
        """ 
        
        gameTurn = self.mm_get_current_turn()
        print(f"Trying to give {gameTurn} points {points}")
        try:
            # it gave them points!
            [x for x in self.players if x.userID == gameTurn][0].points += points
        except Exception as er:
            print("did not give points?")
            print(er)
        return points

    def mm_get_current_turn(self):		
        """
        Returns the current turn of the game.

        If the game type is GROUP, return the userID of the current group leader.
        Otherwise, return the result of calling self.game.fetch_turn().
        """
        if self.type == "GROUP":
            userID = self.groupPlayers[self.groupTurn]
            return userID
        else:
            return self.game.fetch_turn()
    
    def mm_next_turn(self):
        # THIS IS A MIDDLE-MAN to separate between groups and normal
        """
        Advances the game state to the next player's turn.

        If the game type is GROUP, cycles through the group leaders.
        Otherwise, calls the next_turn() method of the game object.

        Returns the userID of the player whose turn it now is.
        """
        if self.type == "GROUP":
            
            if (self.groupTurn + 1) == len(self.groupPlayers):
                self.groupTurn = 0
            else:
                self.groupTurn += 1
            return self.mm_get_current_turn()
        else:
            return self.game.next_turn()
        
    async def bot_turn(self):
        resp = await self.game.bot_turn()
        if type(resp) == bool:
            self.register_skip(-2)
            if resp and not self.game.finished:
                self.game.next_turn()
                # bot has skipped
            return False
        self.mm_give_points(resp)
        return resp
    
    def get_group_leader_id(self, userID: int):
        for group in self.groups:
            if userID in group:
                return group[0]
        # This shouldnt return false

    def _get_skip_owner(self, userID: int) -> int:
        if self.type == "GROUP":
            leaderID = self.get_group_leader_id(userID)
            if leaderID is not None:
                return leaderID
        return userID

    def reset_skip_counts(self):
        if self.type == "GROUP":
            tracked_players = self.groupPlayers.copy()
        else:
            tracked_players = [int(player.userID) for player in self.players]
        self.skip_counts = {int(player_id): 0 for player_id in tracked_players}

    def active_competitor_count(self) -> int:
        if self.type == "GROUP":
            return len([group for group in self.groups if len(group) > 0])
        return len(self.players)

    def _rack_owners(self) -> list[int]:
        if self.type == "GROUP":
            return [int(group[0]) for group in self.groups if len(group) > 0]
        return [int(player.userID) for player in self.players]

    def check_end_conditions(self) -> bool:
        if self.hasStarted and self.active_competitor_count() <= 1:
            self.game.finished = True
            return True

        if len(self.game.letterArray) == 0:
            for player_id in self._rack_owners():
                if len(self.game.playerLetters.get(str(player_id), [])) == 0:
                    self.game.finished = True
                    return True

        return self.game.finished

    def register_skip(self, userID: int) -> bool:
        skip_owner = int(self._get_skip_owner(userID))
        if skip_owner not in self.skip_counts:
            self.skip_counts[skip_owner] = 0
        self.skip_counts[skip_owner] += 1
        if len(self.skip_counts) > 0 and all(count >= 2 for count in self.skip_counts.values()):
            self.game.finished = True
        return self.check_end_conditions()

    async def game_turn(self, letters):
        """
        Places a word on the game board based on the given letters and direction.

        Parameters:
            letters (list[tuple[int, int], str]): A list of coordinates and letters.

        Returns:
            bool | int | Literal[False]: The points gotten by the player for placing the word.
        """

        firstCoordinate = None
        direction = "RIGHT"
        playerLetters = copy.deepcopy(self.game.fetch_player_letters(self.mm_get_current_turn()))
        
        blanksIdentified = []
        for [x,y], letter, blankReplacement in letters:
            # identify direction
            if firstCoordinate == None:
                firstCoordinate = [x,y]
            else:
                if x-firstCoordinate[0] != 0:
                    direction = "RIGHT"
                    letters.sort(key=lambda x: x[0][0])
                else:
                    direction = "DOWN"
                    letters.sort(key=lambda x: x[0][1])
            # identify if player has all available letters.
            if letter in playerLetters:
                playerLetters.remove(letter)
            else:
                # identify if blank is there, and use that.
                blank = " "
                if blank in playerLetters:
                    playerLetters.remove(blank)
                    blanksIdentified.append((x,y))
                else:
                    # Invalid placement, deep copied the player's letters to not affect their actual deck unless it works.
                    print("Invalid placement, deep copied the player's letters to not affect their actual deck unless it works")
                    return False
        print("Player has all letters required for this turn.")
        # this should not have a side effect of moving to the next turn.
        result = await self.game.place_word(letters, direction)
        if type(result) == bool:
            print("here")
            return False
        
        # Update letters and return result.
        # get_current_turn should be the same, otherwise place_word changes the current turn.
        self.game.set_player_letters(self.mm_get_current_turn(), playerLetters)
        
        self.mm_give_points(result)
        self.check_end_conditions()
        
        print(f"result: {result}")
        
        
        return result


    def _toGamePlayer(self, player: UserFetch) -> GamePlayer:
        return GamePlayer.model_validate(player)

    def export_data(self):

        grid = self.game.export_grid()
        data =  {
            "grid": grid,
            "leader": self.leader,
            "game_type": self.type,
            "players": [x.model_dump(mode="json") for x in self.players],	
            "has_started": self.hasStarted,
            "turn": self.game.fetch_turn(),
            "options": self.options,
            "finishes": self.finishesAt
        }
        if self.type == "GROUP":
            data['groups'] = self.groups
            data['partners'] = self.partners
        
        return data
    
    def add_player(self, player: UserFetch):
        """
            Add a player to the game.
            
            Checks if the game has already started or if the player is already in the game.
            If the game is a normal game, it checks if the game is full (4 players).
            If the game is a group game, it checks if all groups are full (each group has 2 players).
            If the game is a bot game, it checks if there is already a player in the game.
            
            Raises an exception if any of the above conditions are met.
            
            Parameters:
            player (UserFetch): The player to add to the game.
            
            Returns:
            None
        """
        if self.hasStarted:
            raise Exception("Game has already started")
        player = self._toGamePlayer(player)

        # Compare by userID, not full model equality, so reconnects/rejoins never duplicate a user.
        if any(existing_player.userID == player.userID for existing_player in self.players):
            raise Exception("Player already in game")

        # Handle checking
        if self.type == "NORMAL":
            if len(self.players) == 4:
                raise Exception("Max amount of players in game")
            self.players.append(player)
        elif self.type == "GROUP":
            maxPlayers = len(self.groups) * 2
            if len(self.players) == maxPlayers:
                raise Exception("Max amount of players in game")
            self.players.append(player)
            hasGroup = False
            for i, group in enumerate(self.groups):
                if player.userID in group:
                    raise Exception("Player already in game")
                if len(group) == 0:
                    self.groups[i].append(player.userID)
                    hasGroup = True
                    break
            if not hasGroup:
                print("All groups are full...")
                # Should remove player?
                raise Exception("All groups are full")
        else:  # bot
            if len(self.players) == 0:
                self.players.append(player)
            else:
                raise Exception("Only one player when Bot Game")
    
    def add_bot(self):
        if len(self.players) == 0:
            raise Exception("No players in game to add bot into the game")
        else:
            self.players.append(BotPlayer())

    def remove_player(self, player: UserFetch | int):
        """
            Remove a player from the game.
            
            Args:
                player (UserFetch | int): The player to remove. Can be either a UserFetch object or the player's userID as an integer.
            
            Returns:
                bool: True if the player was removed successfully, False otherwise.
            
            Raises:
                ValueError: If the player is not in the player list.
        """
        player_id = player.userID if isinstance(player, UserFetch) else player
        removed_player = None

        for i, existing_player in enumerate(self.players):
            if existing_player.userID == player_id:
                removed_player = self.players.pop(i)
                break

        if removed_player is None:
            raise Exception("Player not in player list")

        promoted_leader = None
        removed_skip_count = self.skip_counts.pop(int(player_id), 0)

        if removed_player.userID == self.leader and len(self.players) > 0:
            self.leader = self.players[0].userID

        if self.type == "GROUP":
            for i, group in enumerate(self.groups):
                if player_id in group:
                    removed_was_leader = len(group) > 0 and group[0] == player_id
                    self.groups[i].remove(player_id)
                    if removed_was_leader and len(self.groups[i]) > 0:
                        promoted_leader = self.groups[i][0]
                    break

        if self.hasStarted:
            if str(player_id) in self.game.playerLetters:
                if promoted_leader is not None:
                    self.game.playerLetters[str(promoted_leader)] = self.game.playerLetters.pop(str(player_id))
                else:
                    del self.game.playerLetters[str(player_id)]

            if int(player_id) in self.game.players:
                removed_index = self.game.players.index(int(player_id))
                if promoted_leader is not None:
                    self.game.players[removed_index] = int(promoted_leader)
                else:
                    self.game.players.pop(removed_index)
                    if removed_index < self.game.gameTurn:
                        self.game.gameTurn -= 1
                    if len(self.game.players) == 0:
                        self.game.gameTurn = 0
                    elif self.game.gameTurn >= len(self.game.players):
                        self.game.gameTurn = 0

        if self.type == "GROUP":
            if promoted_leader is not None:
                promoted_player = next((x for x in self.players if x.userID == promoted_leader), None)
                if promoted_player is not None:
                    promoted_player.points = max(promoted_player.points, removed_player.points)
                self.skip_counts[int(promoted_leader)] = max(self.skip_counts.get(int(promoted_leader), 0), removed_skip_count)

            self.groupPlayers = [group[0] for group in self.groups if len(group) > 0]
            if len(self.groupPlayers) == 0:
                self.groupTurn = 0
            elif self.groupTurn >= len(self.groupPlayers):
                self.groupTurn = 0

            self.partners = {}
            for group in self.groups:
                if len(group) == 2:
                    self.partners[group[0]] = group[1]
                    self.partners[group[1]] = group[0]

        self.check_end_conditions()
        return True
    
    def in_group(self, player: UserFetch, groupIndex: int):
        return player.userID in self.groups[groupIndex]

    def join_group(self, player: UserFetch, groupIndex: int):
        """
        Join a player to a group

        Removes the player from any other group they are in - so can be used as a move group

        Args:
            player (UserFetch): The player to join the group
            groupIndex (int): The index of the group to join
        Returns:
            bool: Whether the player was successfully joined
        """
        if self.hasStarted:
            raise Exception("Game has already started")
        alreadyinGroup = self.in_group(player, groupIndex)
        if alreadyinGroup:
            return alreadyinGroup
        
        # check if adding the player into the group becomes too many.
        if len(self.groups[groupIndex]) + 1 > 2:
            raise Exception("Group is full")
        for i, group in enumerate(self.groups):
            if player.userID in group:
                if i != groupIndex: 
                    self.groups[i].remove(player.userID)
                else: 
                    alreadyinGroup = True

        if groupIndex > len(self.groups)-1 or groupIndex < 0:
            raise Exception("Group does not exist")
        if not alreadyinGroup:
            self.groups[groupIndex].append(player.userID)
        return True
    
    def leave_group(self, player: UserFetch):
        """
            Remove a player from a group

            Args:
                player (UserFetch): The player to remove from the group

            Returns:
                bool: Whether the player was successfully removed

            Raises:
                Exception: If the game has already started
                Exception: If the player is not in a group
        """
        if self.hasStarted:
            raise Exception("Game has already started")
        hasGroup = False
        for i, group in enumerate(self.groups):
            if player.userID in group:
                hasGroup = True
                self.groups[i].remove(player.userID)
        if not hasGroup:
            raise Exception("Player is not in a group")
        return True

    def start_game(self):
        """
            Start the game

            Initializes the game state and hands out the current turn
            to the players.

            Returns:
                int: The current turn
        """
        if self.hasStarted:
            return self.mm_get_current_turn()

        if self.type == "BOT":
            self.add_bot()
        elif self.type == "GROUP":
            
            for i, group in enumerate(self.groups):
                if len(group) == 2:
                    # if the group is a group with a partner
                    self.partners[group[0]] = group[1]
                    self.partners[group[1]] = group[0]
        self.hasStarted = True
        self.finishesAt = datetime.datetime.now().timestamp() + int(self.time_limit)
        if self.type == "GROUP":
            # only want to start the game with the leaders
            players = []
            for group in self.groups:
                if len(group) >= 1:
                    groupLeaderID = group[0]
                    players.append([x for x in self.players if x.userID == groupLeaderID][0])
            currentTurn = self.game.init_game(players)
            # Because it is a group it has a different turn system handled in this file.
            self.groupPlayers = [x[0] for x in self.groups if len(x) > 0]
            self.groupTurn = 0
        else:
            currentTurn = self.game.init_game(self.players)
        self.reset_skip_counts()
        self.check_end_conditions()
        currentTurn = self.mm_get_current_turn()
        return currentTurn
    
    def get_partner(self, userID: int) -> int | bool:
        if self.type != "GROUP":
            return False
        if userID in self.partners:
            return self.partners[userID]
        return False
    
    
    
    def finish_game(self) -> dict:
        # get all data from the board, input into database, continue
        
        # TO RETURN
        """
        GRID
        PLAYER SCORE
        PLAYER WORDS

        OTHER PLAYERS SCORES + YOUR OWN FOR LEADERBOARD

        """

        grid = self.game.export_grid()

        if self.type == "GROUP":
            grouped_players = []
            for group in self.groups:
                if len(group) == 0:
                    continue

                members = [player.dump_json() for player in self.players if player.userID in group]
                if len(members) == 0:
                    continue

                grouped_players.append({
                    "userID": group[0],
                    "userName": " & ".join(member["userName"] for member in members),
                    "placed": [],
                    "points": sum(member["points"] for member in members),
                    "members": members,
                })

            grouped_players.sort(key=lambda x: x['points'], reverse=True)
            winner = grouped_players[0] if len(grouped_players) > 0 else {
                "userID": -1,
                "userName": "",
                "placed": [],
                "points": 0,
                "members": [],
            }

            return {
                "grid": grid,
                "players": grouped_players,
                "winner": winner,
                "groups": self.groups,
                "partners": self.partners,
            }

        players = [x.dump_json() for x in self.players]
        players.sort(key=lambda x: x['points'], reverse=True)
        winner = players[0] if len(players) > 0 else {
            "userID": -1,
            "userName": "",
            "placed": [],
            "points": 0,
        }

        return {
            "grid": grid,
            "players": players,
            "winner": winner,
        }