import { createWriteStream } from 'fs';
import { mkdir, rename, unlink } from 'fs/promises';
import { pipeline } from 'stream/promises';
import { PassThrough } from 'stream';
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

async function ensureDirectoryExists(dirPath) {
  try {
    await mkdir(dirPath, { recursive: true });
  } catch (error) {
    if (error.code !== 'EEXIST') {
      throw new Error(`Failed to create directory ${dirPath}: ${error.message}`);
    }
  }
}

async function withWritableFile(filePath, callback, options = {}) {
  const { atomic = true, ...streamOptions } = options;
  const resolvedPath = path.resolve(filePath);
  const parentDir = path.dirname(resolvedPath);
  
  await ensureDirectoryExists(parentDir);

  if (atomic) {
    return await withAtomicFile(resolvedPath, callback, streamOptions);
  } else {
    return await withDirectFile(resolvedPath, callback, streamOptions);
  }
}

async function withAtomicFile(finalPath, callback, streamOptions = {}) {
  const parentDir = path.dirname(finalPath);
  const basename = path.basename(finalPath);
  const tempName = `.tmp-${process.pid}-${Date.now()}-${basename}`;
  const tempPath = path.join(parentDir, tempName);

  try {
    await withDirectFile(tempPath, callback, streamOptions);
    await rename(tempPath, finalPath);
  } catch (error) {
    try {
      await unlink(tempPath);
    } catch (unlinkError) {
      // Ignore unlink errors - temp file may not exist or already removed
    }
    throw error;
  }
}

async function withDirectFile(filePath, callback, streamOptions = {}) {
  const inputStream = new PassThrough();
  const writeStream = createWriteStream(filePath, streamOptions);

  try {
    const pipelinePromise = pipeline(inputStream, writeStream);

    await callback(inputStream);

    inputStream.end();

    await pipelinePromise;
  } catch (error) {
    if (!inputStream.destroyed) {
      inputStream.destroy();
    }
    if (!writeStream.destroyed) {
      writeStream.destroy();
    }
    throw error;
  }
}

async function withOptionalFileStream(options, callback) {
  const outputFile = options.outputFile ?? Settings.outputFile;

  if (outputFile) {
    const resolvedPath = path.resolve(outputFile);
    const { atomic, ...fileOptions } = options;
    
    await withWritableFile(resolvedPath, async (stream) => {
      await callback(stream);
    }, { atomic: atomic ?? true, ...fileOptions });
    console.info(`Output written to: ${outputFile}`);
  } else {
    await callback(process.stdout);
  }
}

export {
  rankingsMetadataToString,
  playerToString,
  playerToTabDelimitedString,
  withWritableFile,
  withOptionalFileStream
};