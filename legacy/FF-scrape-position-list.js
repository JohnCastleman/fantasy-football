// tested, working
const listElementK = document.querySelector('ol.position-section__list.position-section__list--k');

let dataK = "";

if (listElementK) {
  const kickerElements = listElementK.querySelectorAll('li.player-list-item');
  dataK = "rank\tname\tteam\n"; // Tab-delimited header
  kickerElements.forEach((kicker) => {
    const rankElement = kicker.querySelector('.player-list-item__rank');
    const nameElement = kicker.querySelector('a.player-list-item__player-name');
    const teamElement = kicker.querySelector('span.player-list-item__team');

    const rawRank = rankElement ? rankElement.textContent.trim() : '';
    const rank = rawRank.replace('.', ''); // Remove the period
    const name = nameElement ? nameElement.getAttribute('fp-player-name') : '';
    const team = teamElement ? teamElement.textContent.trim() : '';

    dataK += `${rank}\t"${name}"\t"${team}"\n`; // Tab-delimited data
  });
} else {
  dataK = "List element with class position-section__list position-section__list--K not found.";
}

/* K sample output:
rank	name	team
1	"C. Dicker"	"LAC"
2	"M. Prater"	"BUF"
3	"B. Aubrey"	"DAL"
4	"T. Loop"	"BAL"
5	"B. McManus"	"GB"
6	"J. Bates"	"DET"
7	"S. Shrader"	"IND"
8	"K. Fairbairn"	"HOU"
9	"C. Boswell"	"PIT"
10	"J. Karty"	"LAR"
11	"J. Elliott"	"PHI"
12	"H. Butker"	"KC"
13	"W. Lutz"	"DEN"
14	"E. Pineiro"	"SF"
15	"C. Little"	"JAC"
16	"D. Carlson"	"LV"
17	"W. Reichard"	"MIN"
18	"J. Myers"	"SEA"
19	"M. Gay"	"WAS"
20	"C. Santos"	"CHI"
21	"C. McLaughlin"	"TB"
22	"C. Ryland"	"ARI"
23	"A. Borregales"	"NE"
24	"P. Romo"	"ATL"
25	"R. Patterson"	"MIA"
26	"N. Folk"	"NYJ"
27	"J. Slye"	"TEN"
28	"E. McPherson"	"CIN"
29	"R. Fitzgerald"	"CAR"
30	"G. Gano"	"NYG"
31	"B. Grupe"	"NO"
32	"A. Szmyt"	"CLE"
33	"Y. Koo"	"NYG"
 */

// tested, working
const listElementDST = document.querySelector('ol.position-section__list.position-section__list--dst');

let dataDST = "";

if (listElementDST) {
  const dstElements = listElementDST.querySelectorAll('li.player-list-item');
  dataDST = "rank\tname\n"; // Tab-delimited header
  dstElements.forEach((dst) => {
    const rankElement = dst.querySelector('.player-list-item__rank');
    const nameElement = dst.querySelector('.player-list-item__team, .player-list-item__player-name');

    const rawRank = rankElement ? rankElement.textContent.trim() : '';
    const rank = rawRank.replace('.', ''); // Remove the period
    const name = nameElement ? nameElement.getAttribute('fp-player-name') : '';

    dataDST += `${rank}\t"${name}"\n`; // Tab-delimited data
  });
} else {
  dataDST = "List element with class position-section__list--dst not found.";
}

/* DST sample output:
rank	team
1	"Denver Broncos"
2	"Houston Texans"
3	"Buffalo Bills"
4	"Detroit Lions"
5	"Los Angeles Chargers"
6	"Green Bay Packers"
7	"Minnesota Vikings"
8	"Philadelphia Eagles"
9	"New England Patriots"
10	"Pittsburgh Steelers"
11	"Seattle Seahawks"
12	"San Francisco 49ers"
13	"Arizona Cardinals"
14	"Tennessee Titans"
15	"New York Jets"
16	"Chicago Bears"
17	"Washington Commanders"
18	"Los Angeles Rams"
19	"Miami Dolphins"
20	"Baltimore Ravens"
21	"Atlanta Falcons"
22	"Carolina Panthers"
23	"Jacksonville Jaguars"
24	"Cleveland Browns"
25	"New York Giants"
26	"Las Vegas Raiders"
27	"Indianapolis Colts"
28	"Tampa Bay Buccaneers"
29	"Kansas City Chiefs"
30	"Cincinnati Bengals"
31	"Dallas Cowboys"
32	"New Orleans Saints"
 */