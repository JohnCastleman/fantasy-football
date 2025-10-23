const { RankingTypeEnum, PositionEnum } = require('../../common');

const TestOutputTypeEnum = Object.freeze({
  DISPLAY: "DISPLAY",
  DUMP: "DUMP",
  ALL: "ALL"
});

const TestSettings = {
  testOutputTypes: TestOutputTypeEnum.DUMP, // TestOutputTypeEnum.DISPLAY | TestOutputTypeEnum.DUMP | TestOutputTypeEnum.ALL
  //testRankingTypes: null, // a collection of RankingTypeEnum values; set to null to test all ranking types
  // Example:
  testRankingTypes: [RankingTypeEnum.WEEKLY],
  //testPositions: null, // a collection of PositionEnum values; set to null to test all positions
  // Example:
  testPositions: [PositionEnum.K, PositionEnum.DST]
};

module.exports = {
  TestOutputTypeEnum,
  TestSettings
};
