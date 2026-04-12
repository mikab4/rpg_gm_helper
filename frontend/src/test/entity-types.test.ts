import { describe, expect, it } from "vitest";

import { ENTITY_TYPE_OPTIONS } from "../entities/entityTypes";

describe("entity type metadata", () => {
  it("exports compatibility-ready descriptions for every canonical entity type", () => {
    expect(ENTITY_TYPE_OPTIONS).toEqual([
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
    ]);
  });
});
