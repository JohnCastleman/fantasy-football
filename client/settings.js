import { ScoringTypeEnum, RankingTypeEnum, PositionEnum } from '../common/index.js';

const Settings = {
  verbose: false, // Whether to show detailed ranking metadata (and, later, expanded player stats)
  displaySize: 3, // Default number of players to show in display rankings; set to null to show all
  tabDelimitedHeader: 'rank\tname\tteam', // Set this to null to suppress header row in tab-delimited output
  
  // Display text mappings
  displayText: {
    scoringType: {
      [ScoringTypeEnum.STD]: "Standard",
      [ScoringTypeEnum.PPR]: "Points-Per-Reception",
      [ScoringTypeEnum.HALF]: "Half-Point-Per-Reception"
    },
    rankingType: {
      [RankingTypeEnum.ROS]: "Rest-of-Season",
      [RankingTypeEnum.WEEKLY]: "Weekly",
      [RankingTypeEnum.DYNASTY]: "Dynasty",
      [RankingTypeEnum.DRAFT]: "Draft"
    },
    position: {
      [PositionEnum.QB]: "Quarterback",
      [PositionEnum.RB]: "Running Back",
      [PositionEnum.WR]: "Wide Receiver",
      [PositionEnum.TE]: "Tight End",
      [PositionEnum.K]: "Kicker",
      [PositionEnum.DST]: "Defense/Special Teams"
    }
  }
};

export { Settings };