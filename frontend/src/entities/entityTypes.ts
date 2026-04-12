export const ENTITY_TYPE_OPTIONS = [
  { label: "Person", value: "person" },
  { label: "Location", value: "location" },
  { label: "Organization", value: "organization" },
  { label: "Item", value: "item" },
  { label: "Event", value: "event" },
  { label: "Deity", value: "deity" },
  { label: "Other", value: "other" },
] as const;

export type EntityTypeValue = (typeof ENTITY_TYPE_OPTIONS)[number]["value"];

const LEGACY_ENTITY_TYPE_LABELS = new Map<string, string>([
  ["npc", "NPC"],
  ["artifact", "Artifact"],
  ["faction", "Faction"],
  ["lore", "Lore"],
]);

const ENTITY_TYPE_LABELS = new Map<string, string>(ENTITY_TYPE_OPTIONS.map((option) => [option.value, option.label]));

export function formatEntityTypeLabel(entityType: string): string {
  return ENTITY_TYPE_LABELS.get(entityType) ?? LEGACY_ENTITY_TYPE_LABELS.get(entityType) ?? entityType;
}
