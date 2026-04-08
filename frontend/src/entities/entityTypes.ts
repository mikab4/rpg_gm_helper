export const ENTITY_TYPE_OPTIONS = [
  { label: "NPC", value: "npc" },
  { label: "Location", value: "location" },
  { label: "Artifact", value: "artifact" },
  { label: "Faction", value: "faction" },
  { label: "Event", value: "event" },
  { label: "Lore", value: "lore" },
] as const;

export type EntityTypeValue = (typeof ENTITY_TYPE_OPTIONS)[number]["value"];

const ENTITY_TYPE_LABELS = new Map<string, string>(
  ENTITY_TYPE_OPTIONS.map((option) => [option.value, option.label]),
);

export function formatEntityTypeLabel(entityType: string): string {
  return ENTITY_TYPE_LABELS.get(entityType) ?? entityType;
}
