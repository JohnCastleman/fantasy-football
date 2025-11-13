import { createWriteStream } from 'fs';
import { stat, rename, unlink } from 'fs/promises';
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

async function withTempFile(finalPath, callback) {
  const resolvedPath = path.resolve(finalPath);
  const parentDir = path.dirname(resolvedPath);
  const basename = path.basename(resolvedPath);
  const tempName = `.tmp-${process.pid}-${Date.now()}-${basename}`;
  const tempPath = path.join(parentDir, tempName);

  let stream = null;
  let streamError = null;
  let streamEnded = false;

  const handleStreamError = (error) => {
    if (error.code === 'ENOENT') {
      streamError = new Error(`Directory does not exist for output file: ${parentDir}. Please create the directory first.`);
    } else {
      streamError = new Error(`Error writing to temp file ${tempPath}: ${error.message}`);
    }
  };

  try {
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

    stream = createWriteStream(tempPath);
    stream.once('error', handleStreamError);

    await callback(stream);

    if (streamError) {
      throw streamError;
    }

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

    await rename(tempPath, resolvedPath);
  } catch (error) {
    if (tempPath) {
      try {
        await unlink(tempPath);
      } catch (unlinkError) {
        // Ignore unlink errors - temp file may not exist or already removed
      }
    }
    throw error;
  } finally {
    if (stream && !streamEnded) {
      if (streamError || stream.destroyed) {
        stream.destroy();
      } else {
        stream.end();
      }
    }
  }
}

async function withOptionalFileStream(options, callback) {
  const outputFile = options.outputFile ?? Settings.outputFile;

  if (outputFile) {
    const resolvedPath = path.resolve(outputFile);
    
    if (resolvedPath.includes('..')) {
      throw new Error(`Invalid output file path: path traversal not allowed (${outputFile})`);
    }
    
    await withTempFile(resolvedPath, async (stream) => {
      await callback(stream);
    });
    console.info(`Output written to: ${outputFile}`);
  } else {
    await callback(process.stdout);
  }
}

export {
  rankingsMetadataToString,
  playerToString,
  playerToTabDelimitedString,
  withTempFile,
  withOptionalFileStream
};