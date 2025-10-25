import { ScoringTypeEnum } from '../common/index.js';
import { Settings } from './settings.js';
import { toFantasyProsApiParams, toFantasyprosUrl, toFantasyprosHttpHeaders, fromFantasyprosApiResponse } from './utils.js';

async function fetchRankings(apiParams, apiHeaders) {
  if (!apiParams.scoringType) {
    const error = new Error(`Invalid API scoring type parameter: ${apiParams.scoringType}`);
    console.error(error.message);
    throw error;
  }

  if (!apiParams.rankingType) {
    const error = new Error(`Invalid API ranking type parameter: ${apiParams.rankingType}`);
    console.error(error.message);
    throw error;
  }

  if (!apiParams.position) {
    const error = new Error(`Invalid API position parameter: ${apiParams.position}`);
    console.error(error.message);
    throw error;
  }

  const url = toFantasyprosUrl(apiParams);

  console.log('Fetching rankings using API param strings...', apiParams);

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: apiHeaders
    });

    if (!response.ok) {
      const error = new Error(`HTTP error! status: ${response.status}`);
      console.error(error.message);
      throw error;
    }

    const data = await response.json();

    const results = fromFantasyprosApiResponse(data);

    if (!results.players || !Array.isArray(results.players)) {
      const error = new Error('Invalid response: missing players array');
      console.error(error.message);
      throw error;
    }

    console.log(`Returning rankings mapped from API response (${results.metadata.lastUpdated.toLocaleDateString('en-US')})...`, {
      season: results.metadata.season,
      scoringType: results.metadata.scoringType,
      rankingType: results.metadata.rankingType,
      position: results.metadata.position,
      playerCount: results.players.length
    });

    return results;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

async function fetchGeeksquadronRankings(rankingType, position) {
  const season = Settings.season;
  const apiKey = Settings.fantasyprosApiKey; // impl detail: server is using FantasyPros to source rankings
  const league = Settings.fantasyprosLeagues["GeekSquadron"];
  const leagueKey = league.key;
  const scoringType = league.scoringType;

  const apiParams = toFantasyProsApiParams(season, scoringType, rankingType, position, leagueKey);
  const apiHeaders = toFantasyprosHttpHeaders(apiKey);

  return fetchRankings(apiParams, apiHeaders);
}

async function fetchDefaultRankings(rankingType, position) {
  const season = Settings.season;
  const scoringType = Settings.scoringType;
  const apiKey = Settings.fantasyprosApiKey;

  const apiParams = toFantasyProsApiParams(season, scoringType, rankingType, position);
  const apiHeaders = toFantasyprosHttpHeaders(apiKey);

  return fetchRankings(apiParams, apiHeaders);
}

export {
  fetchDefaultRankings,
  fetchGeeksquadronRankings
};