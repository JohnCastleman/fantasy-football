#!/usr/bin/env node
// Remove single-letter tiers (e.g., "S", "A"-"R", "T"-"Z") from stdin and write cleaned output to stdout
//
// e.g.
//   @"
//   A
//   1. Player One
//   B
//   2. Player Two
//   "@ | node ./bin/remove-tiers.js
// output:
//   1. Player One
//   2. Player Two
//
// e.g.
//   type ./input.txt | node ./bin/remove-tiers.js > ./output.txt

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
	const out = input
		.split(/\r?\n/)
		.filter(line => !/^\s*([A-Z])\1?\s*$/.test(line))
		.join('\n');
	process.stdout.write(out);
});
