import assert from "node:assert/strict";
import { test } from "node:test";

import { checkFile, formatSize } from "./files.ts";

const MB = 1024 * 1024;

test("accepts a normal image", () => {
  assert.equal(checkFile({ name: "light.png", size: 2 * MB, type: "image/png" }), null);
});

test("rejects unknown file types", () => {
  assert.match(checkFile({ name: "virus.exe", size: 100, type: "application/octet-stream" }) ?? "", /only images/);
});

test("rejects files that are too big", () => {
  assert.match(checkFile({ name: "clip.mp4", size: 30 * MB, type: "video/mp4" }) ?? "", /smaller than 15 MB/);
});

test("uses the declared type for webm audio", () => {
  assert.equal(checkFile({ name: "engine.webm", size: 8 * MB, type: "audio/webm" }), null);
});

test("rejects empty files", () => {
  assert.match(checkFile({ name: "empty.jpg", size: 0, type: "image/jpeg" }) ?? "", /empty/);
});

test("formats sizes", () => {
  assert.equal(formatSize(2048), "2 KB");
  assert.equal(formatSize(3 * MB), "3.0 MB");
});
