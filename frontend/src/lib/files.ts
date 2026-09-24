import type { MediaKind } from "./types";

const MB = 1024 * 1024;

export const MAX_FILES_PER_MESSAGE = 3;

export const FILE_RULES: Record<MediaKind, { extensions: string[]; maxSize: number }> = {
  image: { extensions: ["jpg", "jpeg", "png", "webp"], maxSize: 5 * MB },
  audio: { extensions: ["mp3", "wav", "m4a", "ogg", "webm"], maxSize: 10 * MB },
  video: { extensions: ["mp4", "mov", "webm"], maxSize: 15 * MB },
};

export const ACCEPT_ATTRIBUTE = Object.values(FILE_RULES)
  .flatMap((rule) => rule.extensions.map((ext) => `.${ext}`))
  .join(",");

// Same checks as the backend so the user gets a quick error before uploading
export function checkFile(file: { name: string; size: number; type: string }): string | null {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const declaredKind = file.type.split("/")[0] as MediaKind;
  const kinds = (Object.keys(FILE_RULES) as MediaKind[]).filter((kind) =>
    FILE_RULES[kind].extensions.includes(extension),
  );
  const kind = kinds.includes(declaredKind) ? declaredKind : kinds[0];

  if (!kind) return `${file.name}: only images, audio and video files are allowed.`;
  if (file.size === 0) return `${file.name}: file is empty.`;
  if (file.size > FILE_RULES[kind].maxSize) {
    return `${file.name}: ${kind} must be smaller than ${FILE_RULES[kind].maxSize / MB} MB.`;
  }
  return null;
}

export function formatSize(bytes: number): string {
  return bytes < MB ? `${Math.ceil(bytes / 1024)} KB` : `${(bytes / MB).toFixed(1)} MB`;
}
