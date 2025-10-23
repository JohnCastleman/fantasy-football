const { RankingTypeEnum, PositionEnum } = require('../common');
const { getRankings, dumpRankingsToTabDelimited } = require('./client');

// ==========================================
// Dump Functions (tab-delimited data output)
// ==========================================
async function dumpRosQbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpRosRbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpRosWrRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpRosTeRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpRosKRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpRosDstRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpWeeklyQbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpWeeklyRbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpWeeklyWrRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpWeeklyTeRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpWeeklyKRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpWeeklyDstRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDynastyQbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDynastyRbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDynastyWrRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDynastyTeRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDynastyKRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDynastyDstRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDraftQbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDraftRbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDraftWrRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDraftTeRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDraftKRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

async function dumpDraftDstRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  dumpRankingsToTabDelimited(rankings);
}

module.exports = {
  dumpRosQbRankings, dumpRosRbRankings, dumpRosWrRankings, dumpRosTeRankings, dumpRosKRankings, dumpRosDstRankings,
  dumpWeeklyQbRankings, dumpWeeklyRbRankings, dumpWeeklyWrRankings, dumpWeeklyTeRankings, dumpWeeklyKRankings, dumpWeeklyDstRankings,
  dumpDynastyQbRankings, dumpDynastyRbRankings, dumpDynastyWrRankings, dumpDynastyTeRankings, dumpDynastyKRankings, dumpDynastyDstRankings,
  dumpDraftQbRankings, dumpDraftRbRankings, dumpDraftWrRankings, dumpDraftTeRankings, dumpDraftKRankings, dumpDraftDstRankings
};