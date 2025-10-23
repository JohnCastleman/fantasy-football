import { RankingTypeEnum, PositionEnum } from '../../common/index.js';
import { TestOutputTypeEnum, TestSettings } from './settings.js';
import {
  // Display functions
  displayRosQbRankings, displayRosRbRankings, displayRosWrRankings, displayRosTeRankings, displayRosKRankings, displayRosDstRankings,
  displayWeeklyQbRankings, displayWeeklyRbRankings, displayWeeklyWrRankings, displayWeeklyTeRankings, displayWeeklyKRankings, displayWeeklyDstRankings,
  displayDynastyQbRankings, displayDynastyRbRankings, displayDynastyWrRankings, displayDynastyTeRankings, displayDynastyKRankings, displayDynastyDstRankings,
  displayDraftQbRankings, displayDraftRbRankings, displayDraftWrRankings, displayDraftTeRankings, displayDraftKRankings, displayDraftDstRankings,
  // Dump functions
  dumpRosQbRankings, dumpRosRbRankings, dumpRosWrRankings, dumpRosTeRankings, dumpRosKRankings, dumpRosDstRankings,
  dumpWeeklyQbRankings, dumpWeeklyRbRankings, dumpWeeklyWrRankings, dumpWeeklyTeRankings, dumpWeeklyKRankings, dumpWeeklyDstRankings,
  dumpDynastyQbRankings, dumpDynastyRbRankings, dumpDynastyWrRankings, dumpDynastyTeRankings, dumpDynastyKRankings, dumpDynastyDstRankings,
  dumpDraftQbRankings, dumpDraftRbRankings, dumpDraftWrRankings, dumpDraftTeRankings, dumpDraftKRankings, dumpDraftDstRankings
} from '../index.js';

function runConfigurableTests() {
  const { testRankingTypes, testOutputTypes, testPositions } = TestSettings;
  
  // Determine which ranking types to test
  const rankingTypesToTest = testRankingTypes === null
    ? [RankingTypeEnum.ROS, RankingTypeEnum.WEEKLY, RankingTypeEnum.DYNASTY, RankingTypeEnum.DRAFT]
    : testRankingTypes;
  
  // Determine which positions to test  
  const positionsToTest = testPositions === null
    ? [PositionEnum.QB, PositionEnum.RB, PositionEnum.WR, PositionEnum.TE, PositionEnum.K, PositionEnum.DST]
    : testPositions;
  
  // Determine which output types to test
  const shouldTestDisplay = testOutputTypes === TestOutputTypeEnum.ALL || testOutputTypes === TestOutputTypeEnum.DISPLAY;
  const shouldTestDump = testOutputTypes === TestOutputTypeEnum.ALL || testOutputTypes === TestOutputTypeEnum.DUMP;
  
  // Function mappings
  const displayFunctions = {
    [RankingTypeEnum.ROS]: {
      [PositionEnum.QB]: displayRosQbRankings,
      [PositionEnum.RB]: displayRosRbRankings,
      [PositionEnum.WR]: displayRosWrRankings,
      [PositionEnum.TE]: displayRosTeRankings,
      [PositionEnum.K]: displayRosKRankings,
      [PositionEnum.DST]: displayRosDstRankings
    },
    [RankingTypeEnum.WEEKLY]: {
      [PositionEnum.QB]: displayWeeklyQbRankings,
      [PositionEnum.RB]: displayWeeklyRbRankings,
      [PositionEnum.WR]: displayWeeklyWrRankings,
      [PositionEnum.TE]: displayWeeklyTeRankings,
      [PositionEnum.K]: displayWeeklyKRankings,
      [PositionEnum.DST]: displayWeeklyDstRankings
    },
    [RankingTypeEnum.DYNASTY]: {
      [PositionEnum.QB]: displayDynastyQbRankings,
      [PositionEnum.RB]: displayDynastyRbRankings,
      [PositionEnum.WR]: displayDynastyWrRankings,
      [PositionEnum.TE]: displayDynastyTeRankings,
      [PositionEnum.K]: displayDynastyKRankings,
      [PositionEnum.DST]: displayDynastyDstRankings
    },
    [RankingTypeEnum.DRAFT]: {
      [PositionEnum.QB]: displayDraftQbRankings,
      [PositionEnum.RB]: displayDraftRbRankings,
      [PositionEnum.WR]: displayDraftWrRankings,
      [PositionEnum.TE]: displayDraftTeRankings,
      [PositionEnum.K]: displayDraftKRankings,
      [PositionEnum.DST]: displayDraftDstRankings
    }
  };
  
  const dumpFunctions = {
    [RankingTypeEnum.ROS]: {
      [PositionEnum.QB]: dumpRosQbRankings,
      [PositionEnum.RB]: dumpRosRbRankings,
      [PositionEnum.WR]: dumpRosWrRankings,
      [PositionEnum.TE]: dumpRosTeRankings,
      [PositionEnum.K]: dumpRosKRankings,
      [PositionEnum.DST]: dumpRosDstRankings
    },
    [RankingTypeEnum.WEEKLY]: {
      [PositionEnum.QB]: dumpWeeklyQbRankings,
      [PositionEnum.RB]: dumpWeeklyRbRankings,
      [PositionEnum.WR]: dumpWeeklyWrRankings,
      [PositionEnum.TE]: dumpWeeklyTeRankings,
      [PositionEnum.K]: dumpWeeklyKRankings,
      [PositionEnum.DST]: dumpWeeklyDstRankings
    },
    [RankingTypeEnum.DYNASTY]: {
      [PositionEnum.QB]: dumpDynastyQbRankings,
      [PositionEnum.RB]: dumpDynastyRbRankings,
      [PositionEnum.WR]: dumpDynastyWrRankings,
      [PositionEnum.TE]: dumpDynastyTeRankings,
      [PositionEnum.K]: dumpDynastyKRankings,
      [PositionEnum.DST]: dumpDynastyDstRankings
    },
    [RankingTypeEnum.DRAFT]: {
      [PositionEnum.QB]: dumpDraftQbRankings,
      [PositionEnum.RB]: dumpDraftRbRankings,
      [PositionEnum.WR]: dumpDraftWrRankings,
      [PositionEnum.TE]: dumpDraftTeRankings,
      [PositionEnum.K]: dumpDraftKRankings,
      [PositionEnum.DST]: dumpDraftDstRankings
    }
  };
  
  // Run display tests
  if (shouldTestDisplay) {
    for (const rankingType of rankingTypesToTest) {
      for (const position of positionsToTest) {
        if (displayFunctions[rankingType] && displayFunctions[rankingType][position]) {
          displayFunctions[rankingType][position]();
        }
      }
    }
  }
  
  // Run dump tests  
  if (shouldTestDump) {
    for (const rankingType of rankingTypesToTest) {
      for (const position of positionsToTest) {
        if (dumpFunctions[rankingType] && dumpFunctions[rankingType][position]) {
          dumpFunctions[rankingType][position]();
        }
      }
    }
  }
}

export {
  runConfigurableTests
};