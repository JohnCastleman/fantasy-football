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

function displayRankings(rankings, options = {}) {
  const { players, metadata } = rankings;
  const { displayMaxPlayers = Settings.displayMaxPlayers ?? null, verbose = Settings.verbose ?? false } = options;

  const title = rankingsMetadataToString(metadata, verbose);  
  process.stdout.write(`\n${title}\n`);
  process.stdout.write('=' + '='.repeat(title.length) + '\n\n');

  if (displayMaxPlayers != null && displayMaxPlayers !== 0) {
    players.slice(0, displayMaxPlayers).forEach(player => {
      process.stdout.write(playerToString(player) + '\n');
    });
    console.log('... (showing', displayMaxPlayers, 'of', players.length, 'players)');
  } else {
    players.forEach(player => {
      process.stdout.write(playerToString(player) + '\n');
    });
  }
  
  process.stdout.write('\n');
}

function dumpRankingsToTabDelimited(rankings) {
  const { players, metadata } = rankings;

  const title = rankingsMetadataToString(metadata) + " (tab-delimited)";  
  console.log(`\n${title}`);
  console.log('=' + '='.repeat(title.length) + '\n');

  const header = Settings.tabDelimitedHeader[metadata.rankingType];
  
  if (header) {
    process.stdout.write(header + '\n');
  }

  players.forEach(player => {
    process.stdout.write(playerToTabDelimitedString(player) + '\n');
  });
  
  process.stdout.write('\n');
}

export {
  getRankings,
  displayRankings,
  dumpRankingsToTabDelimited
};