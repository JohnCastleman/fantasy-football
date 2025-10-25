// Load environment variables from .env file
import 'dotenv/config';
import { ScoringTypeEnum, RankingTypeEnum, PositionEnum } from '../common/index.js';

const Settings = {
  season: 2025,
  scoringType: ScoringTypeEnum.STD,
  fantasyprosApiKey: process.env.FANTASYPROS_API_KEY || null, // API Key from environment variable (required)
  
  fantasyprosLeagues: {
    "GeekSquadron": {
      key: "nfl~686bb718-0adf-4076-bbca-f78f0d5176e1",
      scoringType: ScoringTypeEnum.STD
    }
  },
  
  fantasyprosApiMapping: {
    scoringType: {
      [ScoringTypeEnum.STD]: "STD",
      [ScoringTypeEnum.PPR]: "PPR",
      [ScoringTypeEnum.HALF]: "HALF"
    },
    rankingType: {
      [RankingTypeEnum.ROS]: "ros",
      [RankingTypeEnum.WEEKLY]: "weekly",
      [RankingTypeEnum.DYNASTY]: "dynasty",
      [RankingTypeEnum.DRAFT]: "draft"
    },
    position: {
      [PositionEnum.QB]: "QB",
      [PositionEnum.RB]: "RB",
      [PositionEnum.WR]: "WR",
      [PositionEnum.TE]: "TE",
      [PositionEnum.K]: "K",
      [PositionEnum.DST]: "DST"
    }
  }
};

export { Settings };