import { Settings } from './settings.js';
import { rankingsMetadataToString, playerToString, playerToTabDelimitedString } from './utils.js';
import { fetchGeeksquadronRankings } from '../server/index.js';

async function getRankings(rankingType, position) {
  try {
    return await fetchGeeksquadronRankings(rankingType, position);
  } catch (error) {
        console.error(`Failed to fetch rankings for ${rankingType}  ${position}.`, error);
        throw error;
  }
}

function displayRankings(rankings, options = {}, outStream = process.stdout) {
  const { players, metadata } = rankings;
  const { 
    displayMaxPlayers = Settings.displayMaxPlayers ?? null, 
    verbose = Settings.verbose ?? false
  } = options;

  const title = rankingsMetadataToString(metadata, verbose);  
  outStream.write(`\n${title}\n`);
  outStream.write('=' + '='.repeat(title.length) + '\n\n');

  if (displayMaxPlayers != null && displayMaxPlayers !== 0) {
    players.slice(0, displayMaxPlayers).forEach(player => {
      outStream.write(playerToString(player) + '\n');
    });
    outStream.write(`... (showing ${displayMaxPlayers} of ${players.length} players)\n`);
  } else {
    players.forEach(player => {
      outStream.write(playerToString(player) + '\n');
    });
  }
  
  outStream.write('\n');
}

function dumpRankingsToTabDelimited(rankings, options = {}, outStream = process.stdout) {
  const { players, metadata } = rankings;

  const title = rankingsMetadataToString(metadata) + " (tab-delimited)";  
  console.log(`\n${title}`);
  console.log('=' + '='.repeat(title.length) + '\n');

  const header = Settings.tabDelimitedHeader[metadata.rankingType];
  
  if (header) {
    outStream.write(header + '\n');
  }

  players.forEach(player => {
    outStream.write(playerToTabDelimitedString(player) + '\n');
  });
  
  outStream.write('\n');
}

export {
  getRankings,
  displayRankings,
  dumpRankingsToTabDelimited
};