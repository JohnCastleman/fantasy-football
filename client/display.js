import { RankingTypeEnum, PositionEnum } from '../common/index.js';
import { getRankings, displayRankings } from './client.js';
import { withOptionalFileStream } from './utils.js';

// ==========================================
// Display Functions (human-readable Output)
// ==========================================

function createDisplayFunction(rankingType, position) {
  return async function() {
    await withOptionalFileStream({}, async (stream) => {
      const rankings = await getRankings(rankingType, position);
      displayRankings(rankings, {}, stream);
    });
  };
}

export const displayRosQbRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.QB);
export const displayRosRbRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.RB);
export const displayRosWrRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.WR);
export const displayRosTeRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.TE);
export const displayRosKRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.K);
export const displayRosDstRankings = createDisplayFunction(RankingTypeEnum.ROS, PositionEnum.DST);

export const displayWeeklyQbRankings = createDisplayFunction(RankingTypeEnum.WEEKLY, PositionEnum.QB);
export const displayWeeklyRbRankings = createDisplayFunction(RankingTypeEnum.WEEKLY, PositionEnum.RB);
export const displayWeeklyWrRankings = createDisplayFunction(RankingTypeEnum.WEEKLY, PositionEnum.WR);
export const displayWeeklyTeRankings = createDisplayFunction(RankingTypeEnum.WEEKLY, PositionEnum.TE);
export const displayWeeklyKRankings = createDisplayFunction(RankingTypeEnum.WEEKLY, PositionEnum.K);
export const displayWeeklyDstRankings = createDisplayFunction(RankingTypeEnum.WEEKLY, PositionEnum.DST);

export const displayDynastyQbRankings = createDisplayFunction(RankingTypeEnum.DYNASTY, PositionEnum.QB);
export const displayDynastyRbRankings = createDisplayFunction(RankingTypeEnum.DYNASTY, PositionEnum.RB);
export const displayDynastyWrRankings = createDisplayFunction(RankingTypeEnum.DYNASTY, PositionEnum.WR);
export const displayDynastyTeRankings = createDisplayFunction(RankingTypeEnum.DYNASTY, PositionEnum.TE);
export const displayDynastyKRankings = createDisplayFunction(RankingTypeEnum.DYNASTY, PositionEnum.K);
export const displayDynastyDstRankings = createDisplayFunction(RankingTypeEnum.DYNASTY, PositionEnum.DST);

export const displayDraftQbRankings = createDisplayFunction(RankingTypeEnum.DRAFT, PositionEnum.QB);
export const displayDraftRbRankings = createDisplayFunction(RankingTypeEnum.DRAFT, PositionEnum.RB);
export const displayDraftWrRankings = createDisplayFunction(RankingTypeEnum.DRAFT, PositionEnum.WR);
export const displayDraftTeRankings = createDisplayFunction(RankingTypeEnum.DRAFT, PositionEnum.TE);
export const displayDraftKRankings = createDisplayFunction(RankingTypeEnum.DRAFT, PositionEnum.K);
export const displayDraftDstRankings = createDisplayFunction(RankingTypeEnum.DRAFT, PositionEnum.DST);
