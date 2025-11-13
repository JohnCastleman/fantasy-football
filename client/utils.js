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
  let streamError = null;
  let streamEnded = false;
  
  const handleStreamError = (error) => {
    streamError = error;
    if (error.code === 'ENOENT') {
      console.error(`Directory does not exist for output file: ${outputFile}. Please create the directory first.`);
    } else {
      console.error(`Error writing to file ${outputFile}:`, error);
    }
  };
  
  try {
    if (outputFile) {
      stream = createWriteStream(outputFile);
      stream.once('error', handleStreamError);
    }
    await callback(stream || process.stdout);
    
    if (streamError) {
      throw streamError;
    }
    
    if (stream && outputFile) {
      await new Promise((resolve, reject) => {
        if (streamError) {
          reject(streamError);
          return;
        }
        
        stream.once('finish', () => {
          streamEnded = true;
          resolve();
        });
        stream.once('error', (error) => {
          handleStreamError(error);
          reject(error);
        });
        stream.end();
      });
      console.info(`Output written to: ${outputFile}`);
    }
  } catch (error) {
    if (error !== streamError) {
      console.error(`Error writing output:`, error);
    }
    throw error;
  } finally {
    if (stream && outputFile && !streamEnded) {
      if (streamError || stream.destroyed) {
        stream.destroy();
      } else {
        stream.end();
      }
    }
  }
}

export {
  rankingsMetadataToString,
  playerToString,
  playerToTabDelimitedString,
  withOptionalFileStream
};