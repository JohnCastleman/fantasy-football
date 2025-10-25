# Player Ownership Integration - Planning Document

## Goal

Integrate league roster data to show which team owns each player in rankings, enabling better waiver wire and trade analysis.

## Proof of Concept - Completed

### API Discovery

Successfully identified two FantasyPros APIs that work together:

1. **Consensus Rankings API** (already in use)
   - Returns player rankings with `player_id` field
   - Example: `player_id: 19275` (Jalen Hurts)

2. **League Roster API** (new discovery)
   - URL: `https://mpbnfl.fantasypros.com/api/getLeagueRostersJSON?key={leagueKey}`
   - Returns all teams in league with their player rosters
   - Player IDs directly match those in consensus rankings

### Cross-Reference Test

Successfully cross-referenced GeekSquadron league roster against Week 7 rankings:

**Project Mayhem Roster Identified (13 players):**

| Player Name          | Position | Team | Opponent  |
|---------------------|----------|------|-----------|
| Jalen Hurts         | QB       | PHI  | vs MIN    |
| Jaxson Dart         | QB       | NYG  | vs DEN    |
| Quinshon Judkins    | RB       | CLE  | vs MIA    |
| Ashton Jeanty       | RB       | LV   | vs KC     |
| Jaylen Warren       | RB       | PIT  | vs CIN    |
| Woody Marks         | RB       | HOU  | vs SEA    |
| CeeDee Lamb         | WR       | DAL  | vs WAS    |
| Drake London        | WR       | ATL  | vs SF     |
| Jaylen Waddle       | WR       | MIA  | vs CLE    |
| Tetairoa McMillan   | WR       | CAR  | vs NYJ    |
| Emeka Egbuka        | WR       | TB   | vs DET    |
| Tyler Warren        | TE       | IND  | vs LAC    |
| New England Patriots| DST      | NE   | vs TEN    |

**Key Finding:** The league roster API's player ID arrays directly correspond to `player_id` in rankings responses. This makes ownership integration straightforward.

## Investigative Steps Taken

1. **API Exploration**
   - Examined `fantasypros-league-roster-geeksquadron.json` sample
   - Identified team structure with player ID arrays
   - Confirmed Project Mayhem team ID: 7

2. **Data Cross-Reference**
   - Fetched Week 7 rankings for all positions (QB, RB, WR, TE, K, DST)
   - Filtered by Project Mayhem's 16 player IDs
   - Successfully matched 13 players (3 may have been dropped/added since sample)

3. **League Configuration Refactoring**
   - Moved single league key/scoring from env vars to structured config
   - Created `fantasyprosLeagues` object in `server/settings.js`
   - Supports multiple leagues with name, key, and scoring type

## Data Structures

### League Roster API Response

```json
{
  "teamId": "7",
  "teamName": "Project Mayhem",
  "teams": [
    {
      "id": "1",
      "name": "Rowland's Rad Team",
      "players": [16413, 19788, 22985, ...]
    },
    {
      "id": "7",
      "name": "Project Mayhem",
      "players": [19275, 23062, 23163, 25391, ...]
    }
  ]
}
```

### Proposed Enhancement to PlayerRankingData

```javascript
class PlayerRankingData {
  constructor(rank, playerName, team, bye, opponent, ownedBy, isMyTeam) {
    this.rank = rank;
    this.playerName = playerName;
    this.team = team;
    this.bye = bye;
    this.opponent = opponent;
    this.ownedBy = ownedBy;      // null if free agent, team name if owned
    this.isMyTeam = isMyTeam;    // boolean: true if owned by user's team
  }
}
```

## Implementation Approach (To Be Discussed)

### Server-Side

1. **Fetch League Roster**
   - Add `fetchLeagueRoster(leagueKey)` function
   - Call this once per ranking request (or cache)
   - Build ownership map: `player_id -> { teamName, isMyTeam }`

2. **Augment Player Data**
   - In `fromFantasyprosApiResponse()`, lookup each player in ownership map
   - Add `ownedBy` and `isMyTeam` fields to PlayerRankingData

3. **Configuration**
   - Add `myTeamId` to league config in settings.js
   - Make ownership lookup optional (skip if no league key)

### Client-Side

1. **Display Enhancement**
   - Show ownership indicator: "(FA)", "(My Team)", "(Opponent Name)"
   - Consider color coding or symbols

2. **Dump Enhancement**
   - Add `owned_by` column to tab-delimited output
   - Enables spreadsheet filtering by ownership

3. **Optional Filtering**
   - Add command-line options to show only free agents or only owned players

## Use Cases

1. **Waiver Wire Analysis**: Quickly identify top-ranked free agents
2. **Trade Targets**: See which teams own players of interest
3. **Roster Strength Comparison**: Compare your roster's rankings vs opponents
4. **Pickup Priority**: Focus on unowned players when browsing

## Configuration Needed

Add to league config structure:

```javascript
fantasyprosLeagues: {
  "GeekSquadron": {
    key: "nfl~686bb718-0adf-4076-bbca-f78f0d5176e1",
    scoringType: ScoringTypeEnum.STD,
    myTeamId: "7"  // Project Mayhem
  }
}
```

## Next Steps

1. Discuss implementation approach and priorities
2. Decide on caching strategy for league roster (per request vs. session)
3. Determine client display format for ownership
4. Consider whether to make this a separate feature flag or always-on when league is configured

## Status

**Planning** - Proof of concept successful, ready for implementation discussion.
