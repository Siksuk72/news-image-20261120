// news-image-20261120: the entrypoint the grader runs (Node 22,
// standard library only).
//
// The front page is already painted and stored in this repository as
// entry.png (see draw.py for how it is drawn, and hero.png for the
// Shenzhen skyline illustration it uses). All this program does is
// hand those bytes to the grader at /output/entry.png.
//
// Local trial run, without the grader:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const source = join(repoRoot, "entry.png");
const targetDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

if (!existsSync(source)) {
  throw new Error(`entry.png missing next to main.ts: ${source}`);
}
mkdirSync(targetDir, { recursive: true });
copyFileSync(source, join(targetDir, "entry.png"));
