require('dotenv').config();

import { ScoringTypeEnum, RankingTypeEnum, PositionEnum } from '../common';

const Settings = {
  season: 2025,
  scoringType: ScoringTypeEnum.STD,
  
  // API Key from environment variable (required)
  fantasyprosApiKey: process.env.FANTASYPROS_API_KEY || null,
  
  // API mappings
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

export default { Settings };