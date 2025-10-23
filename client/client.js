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
  const { displaySize = Settings.displaySize, verbose = Settings.verbose } = options;

  const title = rankingsMetadataToString(metadata, verbose);  
  console.log(`\n${title}`);
  console.log('=' + '='.repeat(title.length) + '\n');

  if (displaySize !== null) {
    players.slice(0, displaySize).forEach(player => {
      console.log(playerToString(player));
    });
    console.log('... (showing', displaySize, 'of', players.length, 'players)');
  } else {
    players.forEach(player => {
      console.log(playerToString(player));
    });
  }
  
  console.log('');
}

function dumpRankingsToTabDelimited(rankings) {
  const { players, metadata } = rankings;

  const title = rankingsMetadataToString(metadata) + " (tab-delimited)";  
  console.log(`\n${title}`);
  console.log('=' + '='.repeat(title.length) + '\n');

  if (Settings.tabDelimitedHeader) {
    console.log(Settings.tabDelimitedHeader); // Header row
  }

  players.forEach(player => {
    console.log(playerToTabDelimitedString(player));
  });
  
  console.log('');
}

export {
  getRankings,
  displayRankings,
  dumpRankingsToTabDelimited
};