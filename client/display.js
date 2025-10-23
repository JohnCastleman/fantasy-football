import { RankingTypeEnum, PositionEnum } from '../common/index.js';
import { getRankings, displayRankings } from './client.js';

// ==========================================
// Display Functions (human-readable Output)
// ==========================================
async function displayRosQbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayRosRbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayRosWrRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayRosTeRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayRosKRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayRosDstRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayWeeklyQbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayWeeklyRbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayWeeklyWrRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayWeeklyTeRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayWeeklyKRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayWeeklyDstRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDynastyQbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDynastyRbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDynastyWrRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDynastyTeRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDynastyKRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDynastyDstRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDraftQbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.QB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDraftRbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.RB;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDraftWrRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.WR;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDraftTeRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.TE;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDraftKRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.K;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

async function displayDraftDstRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.DST;

  const rankings = await getRankings(rankingType, position);
  displayRankings(rankings);
}

export {
  displayRosQbRankings, displayRosRbRankings, displayRosWrRankings, displayRosTeRankings, displayRosKRankings, displayRosDstRankings,
  displayWeeklyQbRankings, displayWeeklyRbRankings, displayWeeklyWrRankings, displayWeeklyTeRankings, displayWeeklyKRankings, displayWeeklyDstRankings,
  displayDynastyQbRankings, displayDynastyRbRankings, displayDynastyWrRankings, displayDynastyTeRankings, displayDynastyKRankings, displayDynastyDstRankings,
  displayDraftQbRankings, displayDraftRbRankings, displayDraftWrRankings, displayDraftTeRankings, displayDraftKRankings, displayDraftDstRankings
};
