import { RankingTypeEnum, PositionEnum } from '../common/index.js';
import { getRankings, dumpRankingsToTabDelimited } from './client.js';
import { withOptionalFileStream } from './utils.js';

// ==========================================
// Dump Functions (tab-delimited data output)
// ==========================================
async function dumpRosQbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpRosRbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpRosWrRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpRosTeRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpRosKRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpRosDstRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpWeeklyQbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpWeeklyRbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpWeeklyWrRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpWeeklyTeRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpWeeklyKRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpWeeklyDstRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDynastyQbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDynastyRbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDynastyWrRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDynastyTeRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDynastyKRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDynastyDstRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDraftQbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDraftRbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDraftWrRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDraftTeRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDraftKRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

async function dumpDraftDstRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    dumpRankingsToTabDelimited(rankings, {}, stream);
  });
}

export {
  dumpRosQbRankings, dumpRosRbRankings, dumpRosWrRankings, dumpRosTeRankings, dumpRosKRankings, dumpRosDstRankings,
  dumpWeeklyQbRankings, dumpWeeklyRbRankings, dumpWeeklyWrRankings, dumpWeeklyTeRankings, dumpWeeklyKRankings, dumpWeeklyDstRankings,
  dumpDynastyQbRankings, dumpDynastyRbRankings, dumpDynastyWrRankings, dumpDynastyTeRankings, dumpDynastyKRankings, dumpDynastyDstRankings,
  dumpDraftQbRankings, dumpDraftRbRankings, dumpDraftWrRankings, dumpDraftTeRankings, dumpDraftKRankings, dumpDraftDstRankings
};