import { useMemo, useState, type Dispatch, type SetStateAction, type SyntheticEvent } from "react";

import { ENTITY_TYPE_OPTIONS, formatEntityTypeLabel, type EntityTypeValue } from "../entities/entityTypes";
import {
  RELATIONSHIP_FAMILY_OPTIONS,
  formatRelationshipFamilyLabel,
  type RelationshipFamilyValue,
} from "../relationships/domain";
import type { RelationshipType, RelationshipTypeCreate, RelationshipTypeUpdate } from "../types/relationshipTypes";

type RelationshipTypeManagerProps = {
  relationshipTypes: RelationshipType[];
  submitError: string | null;
  submitting: boolean;
  onCreate: (relationshipTypeCreate: RelationshipTypeCreate) => Promise<boolean>;
  onDelete: (relationshipTypeKey: string) => Promise<void>;
  onUpdate: (relationshipTypeKey: string, relationshipTypeUpdate: RelationshipTypeUpdate) => Promise<boolean>;
};

export function RelationshipTypeManager({
  relationshipTypes,
  submitError,
  submitting,
  onCreate,
  onDelete,
  onUpdate,
}: RelationshipTypeManagerProps) {
  const [label, setLabel] = useState("");
  const [family, setFamily] = useState<RelationshipFamilyValue>("social");
  const [reverseLabel, setReverseLabel] = useState("");
  const [isSymmetric, setIsSymmetric] = useState(false);
  const [allowedSourceTypes, setAllowedSourceTypes] = useState<EntityTypeValue[]>(["person"]);
  const [allowedTargetTypes, setAllowedTargetTypes] = useState<EntityTypeValue[]>(["person"]);
  const [selectedAllowedSourceType, setSelectedAllowedSourceType] = useState<EntityTypeValue>("person");
  const [selectedAllowedTargetType, setSelectedAllowedTargetType] = useState<EntityTypeValue>("person");
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editingLabel, setEditingLabel] = useState("");

  const sortedRelationshipTypes = useMemo(
    () =>
      [...relationshipTypes].sort((leftRelationshipType, rightRelationshipType) => {
        if (leftRelationshipType.isCustom !== rightRelationshipType.isCustom) {
          return leftRelationshipType.isCustom ? -1 : 1;
        }

        if (leftRelationshipType.isCustom && rightRelationshipType.isCustom) {
          return (rightRelationshipType.createdAt ?? "").localeCompare(leftRelationshipType.createdAt ?? "");
        }

        return leftRelationshipType.label.localeCompare(rightRelationshipType.label);
      }),
    [relationshipTypes],
  );

  async function handleCreate(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const createSucceeded = await onCreate({
      allowedSourceTypes,
      allowedTargetTypes,
      family,
      isSymmetric,
      label: label.trim(),
      reverseLabel: isSymmetric ? null : reverseLabel.trim() || null,
    });

    if (!createSucceeded) {
      return;
    }

    setLabel("");
    setReverseLabel("");
    setAllowedSourceTypes(["person"]);
    setAllowedTargetTypes(["person"]);
    setSelectedAllowedSourceType("person");
    setSelectedAllowedTargetType("person");
    setFamily("social");
    setIsSymmetric(false);
  }

  async function handleUpdate(relationshipTypeKey: string) {
    const updateSucceeded = await onUpdate(relationshipTypeKey, { label: editingLabel.trim() });

    if (!updateSucceeded) {
      return;
    }

    setEditingKey(null);
    setEditingLabel("");
  }

  function addAllowedType(nextType: EntityTypeValue, setAllowedTypes: Dispatch<SetStateAction<EntityTypeValue[]>>) {
    setAllowedTypes((currentAllowedTypes) =>
      currentAllowedTypes.includes(nextType) ? currentAllowedTypes : [...currentAllowedTypes, nextType],
    );
  }

  function removeAllowedType(removedType: EntityTypeValue, setAllowedTypes: Dispatch<SetStateAction<EntityTypeValue[]>>) {
    setAllowedTypes((currentAllowedTypes) => currentAllowedTypes.filter((allowedType) => allowedType !== removedType));
  }

  return (
    <div className="relationship-type-manager">
      <form
        className="record-form relationship-type-form"
        onSubmit={(event) => {
          void handleCreate(event);
        }}
      >
        <label className="field">
          <span className="field-label">Custom Type Label</span>
          <input
            placeholder="bodyguard of"
            value={label}
            onChange={(event) => {
              setLabel(event.target.value);
            }}
          />
        </label>
        <label className="field">
          <span className="field-label">Family</span>
          <select
            value={family}
            onChange={(event) => {
              setFamily(event.target.value as RelationshipFamilyValue);
            }}
          >
            {RELATIONSHIP_FAMILY_OPTIONS.map((familyOption) => (
              <option key={familyOption.value} value={familyOption.value}>
                {familyOption.label}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span className="field-label">Allowed Source Types</span>
          <div className="relationship-type-picker">
            <select
              aria-label="Allowed Source Type"
              value={selectedAllowedSourceType}
              onChange={(event) => {
                setSelectedAllowedSourceType(event.target.value as EntityTypeValue);
              }}
            >
              {ENTITY_TYPE_OPTIONS.map((entityTypeOption) => (
                <option key={entityTypeOption.value} value={entityTypeOption.value}>
                  {entityTypeOption.label}
                </option>
              ))}
            </select>
            <button
              className="secondary-button"
              type="button"
              onClick={() => {
                addAllowedType(selectedAllowedSourceType, setAllowedSourceTypes);
              }}
            >
              Add source type
            </button>
          </div>
          <div className="relationship-type-chip-list">
            {allowedSourceTypes.map((allowedSourceType) => (
              <span key={allowedSourceType} className="relationship-type-chip">
                {formatEntityTypeLabel(allowedSourceType)}
                <button
                  aria-label={`Remove ${formatEntityTypeLabel(allowedSourceType)} from source types`}
                  className="text-button"
                  type="button"
                  onClick={() => {
                    removeAllowedType(allowedSourceType, setAllowedSourceTypes);
                  }}
                >
                  Remove
                </button>
              </span>
            ))}
          </div>
        </label>
        <label className="field">
          <span className="field-label">Allowed Target Types</span>
          <div className="relationship-type-picker">
            <select
              aria-label="Allowed Target Type"
              value={selectedAllowedTargetType}
              onChange={(event) => {
                setSelectedAllowedTargetType(event.target.value as EntityTypeValue);
              }}
            >
              {ENTITY_TYPE_OPTIONS.map((entityTypeOption) => (
                <option key={entityTypeOption.value} value={entityTypeOption.value}>
                  {entityTypeOption.label}
                </option>
              ))}
            </select>
            <button
              className="secondary-button"
              type="button"
              onClick={() => {
                addAllowedType(selectedAllowedTargetType, setAllowedTargetTypes);
              }}
            >
              Add target type
            </button>
          </div>
          <div className="relationship-type-chip-list">
            {allowedTargetTypes.map((allowedTargetType) => (
              <span key={allowedTargetType} className="relationship-type-chip">
                {formatEntityTypeLabel(allowedTargetType)}
                <button
                  aria-label={`Remove ${formatEntityTypeLabel(allowedTargetType)} from target types`}
                  className="text-button"
                  type="button"
                  onClick={() => {
                    removeAllowedType(allowedTargetType, setAllowedTargetTypes);
                  }}
                >
                  Remove
                </button>
              </span>
            ))}
          </div>
        </label>
        <label className="field checkbox-field">
          <input
            className="relationship-type-checkbox"
            checked={isSymmetric}
            type="checkbox"
            onChange={(event) => {
              setIsSymmetric(event.target.checked);
            }}
          />
          <span className="field-label">Symmetric type</span>
        </label>
        {isSymmetric ? null : (
          <label className="field">
            <span className="field-label">Reverse Label</span>
            <input
              placeholder="guarded by"
              value={reverseLabel}
              onChange={(event) => {
                setReverseLabel(event.target.value);
              }}
            />
          </label>
        )}
        {submitError ? <p className="field-error">{submitError}</p> : null}
        <button className="secondary-button" disabled={submitting} type="submit">
          {submitting ? "Saving..." : "Add Custom Type"}
        </button>
      </form>

      <h4 className="relationship-type-list-heading">Existing Relationship Types</h4>
      <div className="relationship-type-list">
        {sortedRelationshipTypes.map((relationshipType) => (
          <article key={relationshipType.key} className="relationship-type-card">
            <div className="relationship-type-copy">
              <strong>{relationshipType.label}</strong>
              <span>
                {formatRelationshipFamilyLabel(relationshipType.family)} ·{" "}
                {relationshipType.isCustom ? "Custom" : "Built In"}
              </span>
              <span>
                {relationshipType.allowedSourceTypes.join(", ")} {"->"} {relationshipType.allowedTargetTypes.join(", ")}
              </span>
            </div>
            {relationshipType.isCustom ? (
              <div className="relationship-type-actions">
                {editingKey === relationshipType.key ? (
                  <>
                    <input
                      value={editingLabel}
                      onChange={(event) => {
                        setEditingLabel(event.target.value);
                      }}
                    />
                    <button
                      className="text-button"
                      type="button"
                      onClick={() => {
                        void handleUpdate(relationshipType.key);
                      }}
                    >
                      Save
                    </button>
                  </>
                ) : (
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => {
                      setEditingKey(relationshipType.key);
                      setEditingLabel(relationshipType.label);
                    }}
                  >
                    Rename
                  </button>
                )}
                <button
                  className="text-button"
                  type="button"
                  onClick={() => {
                    void onDelete(relationshipType.key);
                  }}
                >
                  Delete
                </button>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  );
}
