import { RankingTypeEnum, PositionEnum } from '../common/index.js';
import { getRankings, displayRankings } from './client.js';
import { withOptionalFileStream } from './utils.js';

// ==========================================
// Display Functions (human-readable Output)
// ==========================================
async function displayRosQbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayRosRbRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayRosWrRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayRosTeRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayRosKRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayRosDstRankings() {
  const rankingType = RankingTypeEnum.ROS;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayWeeklyQbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayWeeklyRbRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayWeeklyWrRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayWeeklyTeRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayWeeklyKRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayWeeklyDstRankings() {
  const rankingType = RankingTypeEnum.WEEKLY;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDynastyQbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDynastyRbRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDynastyWrRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDynastyTeRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDynastyKRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDynastyDstRankings() {
  const rankingType = RankingTypeEnum.DYNASTY;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDraftQbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.QB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDraftRbRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.RB;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDraftWrRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.WR;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDraftTeRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.TE;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDraftKRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.K;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

async function displayDraftDstRankings() {
  const rankingType = RankingTypeEnum.DRAFT;
  const position = PositionEnum.DST;

  await withOptionalFileStream({}, async (stream) => {
    const rankings = await getRankings(rankingType, position);
    displayRankings(rankings, {}, stream);
  });
}

export {
  displayRosQbRankings, displayRosRbRankings, displayRosWrRankings, displayRosTeRankings, displayRosKRankings, displayRosDstRankings,
  displayWeeklyQbRankings, displayWeeklyRbRankings, displayWeeklyWrRankings, displayWeeklyTeRankings, displayWeeklyKRankings, displayWeeklyDstRankings,
  displayDynastyQbRankings, displayDynastyRbRankings, displayDynastyWrRankings, displayDynastyTeRankings, displayDynastyKRankings, displayDynastyDstRankings,
  displayDraftQbRankings, displayDraftRbRankings, displayDraftWrRankings, displayDraftTeRankings, displayDraftKRankings, displayDraftDstRankings
};
