import { createWriteStream } from 'fs';
import { ScoringTypeEnum, RankingTypeEnum, PositionEnum } from '../common/index.js';
import { Settings } from './settings.js';

function rankingsMetadataToString(metadata, verbose = false) {
  let typeText = Settings.displayText.rankingType[metadata.rankingType] || metadata.rankingType;
  if (metadata.week && metadata.rankingType === RankingTypeEnum.WEEKLY) {
    typeText = `Week ${metadata.week}`;
  }
  
  const positionText = Settings.displayText.position[metadata.position] || metadata.position;

  const baseText = `${typeText} ${positionText} Rankings`;

  if (!verbose) return baseText;

  const scoringText = Settings.displayText.scoringType[metadata.scoringType] || metadata.scoringType;
  
  const dateStr = metadata.lastUpdated ? 
    ` (as of ${metadata.lastUpdated.toLocaleDateString('en-US')})`  :
    '';

  return `${metadata.season} ${scoringText} ${baseText}${dateStr}`.trim();
}

function playerToString(player) {
  const opponentOrBye = player.opponent ? ` ${player.opponent}` : player.bye ? ` (BYE:${player.bye})` : '';
  return `${player.rank}. ${player.name} ${player.team}${opponentOrBye}`;
}

function playerToTabDelimitedString(player) {
  const opponentOrBye = player.opponent ? `\t${player.opponent}` : player.bye ? `\t${player.bye}` : '';
  return `${player.rank}\t${player.name}\t${player.team}${opponentOrBye}`;
}

async function withOptionalFileStream(options, callback) {
  const outputFile = options.outputFile ?? Settings.outputFile;

  let stream = null;
  try {
    if (outputFile) {
      stream = createWriteStream(outputFile);
      stream.on('error', (error) => {
        if (error.code === 'ENOENT') {
          console.error(`Directory does not exist for output file: ${outputFile}. Please create the directory first.`);
        } else {
          console.error(`Error writing to file ${outputFile}:`, error);
        }
        // Error will propagate through callback promise rejection, caught by try/catch
      });
    }
    await callback(stream || process.stdout);
    
    if (stream && outputFile) {
      await new Promise((resolve, reject) => {
        stream.on('finish', resolve);
        stream.on('error', reject);
        stream.end();
      });
      console.info(`Output written to: ${outputFile}`);
    }
  } catch (error) {
    if (stream && outputFile) {
      stream.end();
    }
    console.error(`Error writing output:`, error);
    throw error;
  }
}

export {
  rankingsMetadataToString,
  playerToString,
  playerToTabDelimitedString,
  withOptionalFileStream
};