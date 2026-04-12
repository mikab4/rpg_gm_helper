export const ENTITY_TYPE_OPTIONS = [
  {
    description: "People, characters, and named individuals",
    label: "Person",
    value: "person",
  },
  {
    description: "Places, regions, and physical settings",
    label: "Location",
    value: "location",
  },
  {
    description: "Groups, factions, and institutions",
    label: "Organization",
    value: "organization",
  },
  {
    description: "Objects, artifacts, and tangible things",
    label: "Item",
    value: "item",
  },
  {
    description: "Battles, rituals, and significant happenings",
    label: "Event",
    value: "event",
  },
  {
    description: "Gods, spirits, and divine powers",
    label: "Deity",
    value: "deity",
  },
  {
    description: "Anything that does not fit the main categories cleanly",
    label: "Other",
    value: "other",
  },
] as const;

export type EntityTypeValue = (typeof ENTITY_TYPE_OPTIONS)[number]["value"];
export type EntityTypeOption = (typeof ENTITY_TYPE_OPTIONS)[number];

const ENTITY_TYPE_VALUES = new Set<EntityTypeValue>(ENTITY_TYPE_OPTIONS.map((option) => option.value));

const LEGACY_ENTITY_TYPE_LABELS = new Map<string, string>([
  ["npc", "NPC"],
  ["artifact", "Artifact"],
  ["faction", "Faction"],
  ["lore", "Lore"],
]);

const ENTITY_TYPE_LABELS = new Map<string, string>(ENTITY_TYPE_OPTIONS.map((option) => [option.value, option.label]));

export function isEntityTypeValue(entityType: string): entityType is EntityTypeValue {
  return ENTITY_TYPE_VALUES.has(entityType as EntityTypeValue);
}

export function formatEntityTypeLabel(entityType: string): string {
  return ENTITY_TYPE_LABELS.get(entityType) ?? LEGACY_ENTITY_TYPE_LABELS.get(entityType) ?? entityType;
}
