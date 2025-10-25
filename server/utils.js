import { parse } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { PlayerRankingData, RankingsResult } from '../common/index.js';
import { Settings } from './settings.js';

function toFantasyProsApiParams(season, scoringType, rankingType, position, leagueKey = null) {
  const params = {
    season: season,
    scoringType: Settings.fantasyprosApiMapping.scoringType[scoringType],
    rankingType: Settings.fantasyprosApiMapping.rankingType[rankingType],
    position: Settings.fantasyprosApiMapping.position[position]
  };
  if (leagueKey) {
    params.leagueKey = leagueKey;
  }

  return params;
}

function toFantasyprosUrl(apiParams) {
  let url = `https://api.fantasypros.com/v2/json/nfl/${apiParams.season}/consensus-rankings?` +
            `scoring=${apiParams.scoringType}&` +
            `type=${apiParams.rankingType}&` +
            `position=${apiParams.position}`;

  if (apiParams.leagueKey) {
    url += `&league_key=${apiParams.leagueKey}`;
  }

  return url;
}

function toFantasyprosHttpHeaders(apiKey) {
  return {
    'accept': 'application/json',
    'x-api-key': apiKey
  };
}

function fromFantasyprosApiResponse(data) {
  const players = data.players && Array.isArray(data.players) ? data.players.map(p => {
    // Normalize opponent format: "vs." => "vs", "at" => "@"
    let opponent = p.player_opponent || null;
    if (opponent) {
      opponent = opponent.replace(/^vs\.\s*/i, 'vs ').replace(/^at\s+/i, '@ ');
    }
    
    // If no opponent but player is on bye this week (for WEEKLY rankings), set opponent to "BYE"
    if (!opponent && data.ranking_type_name === 'weekly' && p.player_bye_week && p.player_bye_week === data.week) {
      opponent = 'BYE';
    }
    
    return new PlayerRankingData(
      p.rank_ecr,
      p.player_name,
      p.player_team_id,
      p.player_bye_week,
      opponent
    );
  }) : null;

  // Map API values back to our enums
  const scoringType = Object.keys(Settings.fantasyprosApiMapping.scoringType).find(key => 
    Settings.fantasyprosApiMapping.scoringType[key] === data.scoring
  ) || null;

  const resultType = Object.keys(Settings.fantasyprosApiMapping.rankingType).find(key => 
    Settings.fantasyprosApiMapping.rankingType[key] === data.ranking_type_name
  ) || null;

  const resultPosition = Object.keys(Settings.fantasyprosApiMapping.position).find(key => 
    Settings.fantasyprosApiMapping.position[key] === data.position_id
  ) || null;

  const lastUpdated =  data.last_updated ? parse(data.last_updated, 'MM/dd', new Date(), { locale: enUS }) : new Date(new Date().setUTCHours(0, 0, 0, 0));      // If lastUpdated not provided, use current date at UTC midnight

  return new RankingsResult(
    players,
    {
      season: data.year,
      scoringType: scoringType,
      rankingType: resultType,
      week: data.week || null,
      position: resultPosition,
      lastUpdated: lastUpdated
    }
  );
}

export {
  toFantasyProsApiParams,
  toFantasyprosUrl,
  toFantasyprosHttpHeaders,
  fromFantasyprosApiResponse
};