import { createWriteStream } from 'fs';
import { stat } from 'fs/promises';
import path from 'path';
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
    if (error.code === 'ENOENT') {
      streamError = new Error(`Directory does not exist for output file: ${outputFile}. Please create the directory first.`);
    } else {
      streamError = new Error(`Error writing to file ${outputFile}: ${error.message}`);
    }
  };
  
  try {
    if (outputFile) {
      const resolvedPath = path.resolve(outputFile);
      
      if (resolvedPath.includes('..')) {
        throw new Error(`Invalid output file path: path traversal not allowed (${outputFile})`);
      }
      
      const parentDir = path.dirname(resolvedPath);
      try {
        const parentStat = await stat(parentDir);
        if (!parentStat.isDirectory()) {
          throw new Error(`Parent path is not a directory: ${parentDir}`);
        }
      } catch (error) {
        if (error.code === 'ENOENT') {
          throw new Error(`Directory does not exist for output file: ${parentDir}. Please create the directory first.`);
        }
        throw error;
      }
      
      stream = createWriteStream(resolvedPath);
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