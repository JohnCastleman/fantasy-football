// Load environment variables from .env file
import 'dotenv/config';
import { ScoringTypeEnum, RankingTypeEnum, PositionEnum } from '../common/index.js';

const Settings = {
  season: 2025,
  scoringType: ScoringTypeEnum.STD,
  fantasyprosApiKey: process.env.FANTASYPROS_API_KEY || null, // API Key from environment variable (required)
  fantasyprosLeagueKey: process.env.FANTASYPROS_LEAGUE_KEY || null, // League Key from environment variable (required for Yahoo public leagues)
  fantasyprosLeagueScoringType: process.env.FANTASYPROS_LEAGUE_SCORING_TYPE || null, // League Scoring Type from environment variable, corresponding to league key
  
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