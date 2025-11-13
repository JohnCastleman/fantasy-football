import { RankingTypeEnum, PositionEnum } from '../common/index.js';
import { getRankings, dumpRankingsToTabDelimited } from './client.js';
import { withOptionalFileStream } from './utils.js';

// ==========================================
// Dump Functions (tab-delimited data output)
// ==========================================

function createDumpFunction(rankingType, position) {
  return async function(options = {}) {
    await withOptionalFileStream(options, async (stream) => {
      const rankings = await getRankings(rankingType, position);
      dumpRankingsToTabDelimited(rankings, options, stream);
    });
  };
}

export const dumpRosQbRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.QB);
export const dumpRosRbRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.RB);
export const dumpRosWrRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.WR);
export const dumpRosTeRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.TE);
export const dumpRosKRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.K);
export const dumpRosDstRankings = createDumpFunction(RankingTypeEnum.ROS, PositionEnum.DST);

export const dumpWeeklyQbRankings = createDumpFunction(RankingTypeEnum.WEEKLY, PositionEnum.QB);
export const dumpWeeklyRbRankings = createDumpFunction(RankingTypeEnum.WEEKLY, PositionEnum.RB);
export const dumpWeeklyWrRankings = createDumpFunction(RankingTypeEnum.WEEKLY, PositionEnum.WR);
export const dumpWeeklyTeRankings = createDumpFunction(RankingTypeEnum.WEEKLY, PositionEnum.TE);
export const dumpWeeklyKRankings = createDumpFunction(RankingTypeEnum.WEEKLY, PositionEnum.K);
export const dumpWeeklyDstRankings = createDumpFunction(RankingTypeEnum.WEEKLY, PositionEnum.DST);

export const dumpDynastyQbRankings = createDumpFunction(RankingTypeEnum.DYNASTY, PositionEnum.QB);
export const dumpDynastyRbRankings = createDumpFunction(RankingTypeEnum.DYNASTY, PositionEnum.RB);
export const dumpDynastyWrRankings = createDumpFunction(RankingTypeEnum.DYNASTY, PositionEnum.WR);
export const dumpDynastyTeRankings = createDumpFunction(RankingTypeEnum.DYNASTY, PositionEnum.TE);
export const dumpDynastyKRankings = createDumpFunction(RankingTypeEnum.DYNASTY, PositionEnum.K);
export const dumpDynastyDstRankings = createDumpFunction(RankingTypeEnum.DYNASTY, PositionEnum.DST);

export const dumpDraftQbRankings = createDumpFunction(RankingTypeEnum.DRAFT, PositionEnum.QB);
export const dumpDraftRbRankings = createDumpFunction(RankingTypeEnum.DRAFT, PositionEnum.RB);
export const dumpDraftWrRankings = createDumpFunction(RankingTypeEnum.DRAFT, PositionEnum.WR);
export const dumpDraftTeRankings = createDumpFunction(RankingTypeEnum.DRAFT, PositionEnum.TE);
export const dumpDraftKRankings = createDumpFunction(RankingTypeEnum.DRAFT, PositionEnum.K);
export const dumpDraftDstRankings = createDumpFunction(RankingTypeEnum.DRAFT, PositionEnum.DST);
