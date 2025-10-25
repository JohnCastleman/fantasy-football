const ScoringTypeEnum = Object.freeze({
  STD: "STD",
  PPR: "PPR",
  HALF: "HALF"
});

const RankingTypeEnum = Object.freeze({
  ROS: "ROS",
  WEEKLY: "WEEKLY",
  DYNASTY: "DYNASTY",
  DRAFT: "DRAFT"
});

const PositionEnum = Object.freeze({
  QB: "QB",
  RB: "RB",
  WR: "WR",
  TE: "TE",
  K: "K",
  DST: "DST"
});

class PlayerRankingData {
  constructor(rank, name, team, bye, opponent = null) {
    this.rank = rank;
    this.name = name;
    this.team = team;
    this.bye = bye;
    this.opponent = opponent;
  }
}

class RankingsResult {
  constructor(players, {
    season,
    scoringType,
    rankingType,
    week = null,
    position,
    lastUpdated = null
  }) {
    this.players = players;
    this.metadata = {
      season,
      scoringType,
      rankingType,
      week,
      position,
      lastUpdated
    };
  }
}

export {
  ScoringTypeEnum,
  RankingTypeEnum,
  PositionEnum,
  PlayerRankingData,
  RankingsResult
};