import { RankingTypeEnum, PositionEnum } from '../../common/index.js';

const TestOutputTypeEnum = Object.freeze({
  DISPLAY: "DISPLAY",
  DUMP: "DUMP",
  ALL: "ALL"
});

const TestSettings = {
  testOutputTypes: TestOutputTypeEnum.ALL, // TestOutputTypeEnum.DISPLAY | TestOutputTypeEnum.DUMP | TestOutputTypeEnum.ALL
  rankingType: RankingTypeEnum.DRAFT, // RankingTypeEnum value
  positions: null, // a collection of PositionEnum values; set to null to test all positions
  // Example:  positions: [PositionEnum.K, PositionEnum.DST]
};

export {
  TestOutputTypeEnum,
  TestSettings
};
