#!/usr/bin/env node
// Build one episode of "MBA English with William".
//   node scripts/make-episode.mjs 1        -> voices series/day-01.json, writes index.html
// Steps: Kokoro TTS per sentence (cached) -> join with pauses -> loudness envelope
// for lip sync -> estimated word timings -> fill template.html -> index.html.
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const VOICE = "am_michael"; // American English male
const SPEED = 1.08; // brisk, energetic delivery
const FPS = 30;
const SR = 24000;
const LEAD = 0.8; // silence before the first sentence
const GAP = 0.45; // pause between sentences
const TAIL = 1.4; // hold after the last sentence
const MUSIC_DB = -10; // music bed level before ducking
// Voice polish: cut rumble, lift presence/air, compress, normalise to social-media loudness.
const VOICE_FX =
  "highpass=f=80,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1.2:g=4,equalizer=f=8000:t=q:w=1:g=2," +
  "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=7";

const dayNum = Number(process.argv[2] || 1);
const dd = String(dayNum).padStart(2, "0");
const ep = JSON.parse(readFileSync(join(ROOT, `series/day-${dd}.json`), "utf8"));
if (ep.sentences.length !== 6) console.warn(`warning: day ${dd} has ${ep.sentences.length} sentences (expected 6)`);

const cacheDir = join(ROOT, ".cache/tts");
mkdirSync(cacheDir, { recursive: true });
mkdirSync(join(ROOT, "assets/audio"), { recursive: true });

const env = { ...process.env };
if (!env.HYPERFRAMES_PYTHON && existsSync(`${env.HOME}/.venvs/kokoro/bin/python`)) {
  env.HYPERFRAMES_PYTHON = `${env.HOME}/.venvs/kokoro/bin/python`;
}

function tts(text) {
  const key = createHash("sha1").update(`${VOICE}|${SPEED}|${text}`).digest("hex").slice(0, 16);
  const out = join(cacheDir, `${key}.wav`);
  if (!existsSync(out)) {
    console.log(`  tts: ${text.slice(0, 60)}...`);
    execFileSync("npx", ["hyperframes", "tts", text, "-v", VOICE, "-s", String(SPEED), "-o", out], {
      env,
      stdio: ["ignore", "ignore", "inherit"],
    });
  }
  return out;
}

function pcm(file) {
  const buf = execFileSync("ffmpeg", ["-v", "error", "-i", file, "-f", "s16le", "-ac", "1", "-ar", String(SR), "-"], {
    maxBuffer: 1 << 30,
  });
  return new Int16Array(buf.buffer, buf.byteOffset, buf.length / 2);
}

function rmsFrames(samples) {
  const hop = SR / FPS;
  const n = Math.ceil(samples.length / hop);
  const out = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    let s = 0;
    const a = Math.floor(i * hop);
    const b = Math.min(samples.length, Math.floor((i + 1) * hop));
    for (let j = a; j < b; j++) s += (samples[j] / 32768) ** 2;
    out[i] = Math.sqrt(s / Math.max(1, b - a));
  }
  return out;
}

// Spread a sentence's words across its voiced span, weighted by length + punctuation pauses.
function wordTimes(text, start, end) {
  const words = text.split(/\s+/).filter(Boolean);
  const weights = words.map((w) => w.replace(/[^A-Za-z0-9]/g, "").length + 1.6 + (/[,;:]$/.test(w) ? 2.2 : 0));
  const total = weights.reduce((a, b) => a + b, 0);
  let t = start;
  return words.map((w, i) => {
    const d = ((end - start) * weights[i]) / total;
    const item = { w, s: +t.toFixed(3), e: +(t + d).toFixed(3) };
    t += d;
    return item;
  });
}

console.log(`Day ${dd}: ${ep.topic}`);
const parts = [];
const sentences = [];
let cursor = LEAD;
for (const text of ep.sentences) {
  const samples = pcm(tts(text));
  const env = rmsFrames(samples);
  const thr = 0.012;
  let first = env.findIndex((v) => v > thr);
  let last = env.length - 1 - [...env].reverse().findIndex((v) => v > thr);
  if (first < 0) (first = 0), (last = env.length - 1);
  const dur = samples.length / SR;
  sentences.push({
    text,
    start: +cursor.toFixed(3),
    end: +(cursor + dur).toFixed(3),
    words: wordTimes(text, cursor + first / FPS, cursor + (last + 1) / FPS),
  });
  parts.push({ samples, at: cursor });
  cursor += dur + GAP;
}
const duration = +(cursor - GAP + TAIL).toFixed(2);

// Mix into one PCM track.
const total = new Int16Array(Math.ceil(duration * SR));
for (const p of parts) total.set(p.samples, Math.round(p.at * SR));
const rawPath = join(cacheDir, `day-${dd}.pcm`);
writeFileSync(rawPath, Buffer.from(total.buffer));
const audioRel = `assets/audio/day-${dd}.wav`;
const voicePath = join(cacheDir, `day-${dd}.voice.wav`);
execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "s16le", "-ar", String(SR), "-ac", "1", "-i", rawPath, "-af", VOICE_FX, "-ar", "48000", "-ac", "2", voicePath]);

// Background music: synthesised bed, ducked ~10 dB under the voice (sidechain), mixed into one track.
const bgmPath = join(cacheDir, `day-${dd}.bgm.wav`);
execFileSync(env.HYPERFRAMES_PYTHON || "python3", [join(ROOT, "scripts/make-bgm.py"), bgmPath, String(duration)], { stdio: "ignore" });
execFileSync("ffmpeg", [
  "-v", "error", "-y", "-i", voicePath, "-i", bgmPath, "-filter_complex",
  `[1:a]volume=${MUSIC_DB}dB[m];[0:a]asplit=2[v][sc];` +
    "[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=350:makeup=1[md];" +
    "[v][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9",
  "-ar", "48000", join(ROOT, audioRel),
]);

// Mouth envelope: normalise to the 95th percentile, light smoothing, 2 decimals.
const raw = rmsFrames(total);
const sorted = [...raw].filter((v) => v > 0.01).sort((a, b) => a - b);
const p95 = sorted[Math.floor(sorted.length * 0.95)] || 1;
const mouth = [];
for (let i = 0; i < raw.length; i++) {
  const v = (raw[Math.max(0, i - 1)] * 0.25 + raw[i] * 0.5 + raw[Math.min(raw.length - 1, i + 1)] * 0.25) / p95;
  mouth.push(Math.round(Math.min(1, Math.max(0, (v - 0.08) / 0.92)) * 100) / 100);
}

const data = { day: ep.day, topic: ep.topic, subtitle: ep.subtitle || "", duration, fps: FPS, audio: audioRel, sentences, mouth };
const tpl = readFileSync(join(ROOT, "scripts/template.html"), "utf8");
const html = tpl
  .replaceAll("__DURATION__", String(duration))
  .replaceAll("__AUDIO__", audioRel)
  .replaceAll("__DAY__", dd)
  .replaceAll("__TOPIC__", ep.topic)
  .replaceAll("__SUBTITLE__", ep.subtitle || "")
  .replace("/*__EPISODE_DATA__*/null", JSON.stringify(data));
writeFileSync(join(ROOT, "index.html"), html);
console.log(`  -> index.html (${duration}s), ${audioRel}`);
