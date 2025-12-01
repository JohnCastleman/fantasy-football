import { dumpWeeklyDstRankings } from '../../client/dump.js';

// Redirect console.log to stderr so only TSV goes to stdout
const originalLog = console.log;
console.log = (...args) => {
  process.stderr.write(args.map(String).join(' ') + '\n');
};

await dumpWeeklyDstRankings();

