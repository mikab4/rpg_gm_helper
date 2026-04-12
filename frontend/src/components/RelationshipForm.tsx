import { useEffect, useMemo, useState, type SyntheticEvent } from "react";
import { Link } from "react-router-dom";

import type { Entity } from "../types/entities";
import type { RelationshipType } from "../types/relationshipTypes";

export type RelationshipFormValues = {
  sourceEntityId: string;
  targetEntityId: string;
  relationshipType: string;
  lifecycleStatus: string;
  visibilityStatus: string;
  certaintyStatus: string;
  notes: string;
};

type RelationshipFormProps = {
  campaignId: string;
  entities: Entity[];
  initialValues: RelationshipFormValues;
  relationshipTypes: RelationshipType[];
  submitError: string | null;
  submitLabel: string;
  submitting: boolean;
  onSubmit: (values: RelationshipFormValues) => Promise<void>;
};

const LIFECYCLE_OPTIONS = ["current", "former"];
const VISIBILITY_OPTIONS = ["public", "secret"];
const CERTAINTY_OPTIONS = ["confirmed", "rumored", "suspected"];

function formatRelationshipFamilyLabel(relationshipFamily: string): string {
  return relationshipFamily
    .split(/[_-]/)
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function RelationshipForm({
  campaignId,
  entities,
  initialValues,
  relationshipTypes,
  submitError,
  submitLabel,
  submitting,
  onSubmit,
}: RelationshipFormProps) {
  const [sourceEntityId, setSourceEntityId] = useState(initialValues.sourceEntityId);
  const [targetEntityId, setTargetEntityId] = useState(initialValues.targetEntityId);
  const [relationshipType, setRelationshipType] = useState(initialValues.relationshipType);
  const [relationshipGroup, setRelationshipGroup] = useState(
    relationshipTypes.find((typeOption) => typeOption.key === initialValues.relationshipType)?.family ?? "",
  );
  const [lifecycleStatus, setLifecycleStatus] = useState(initialValues.lifecycleStatus);
  const [visibilityStatus, setVisibilityStatus] = useState(initialValues.visibilityStatus);
  const [certaintyStatus, setCertaintyStatus] = useState(initialValues.certaintyStatus);
  const [notes, setNotes] = useState(initialValues.notes);

  const selectedRelationshipType = useMemo(
    () => relationshipTypes.find((typeOption) => typeOption.key === relationshipType),
    [relationshipType, relationshipTypes],
  );

  const sourceEntityType = entities.find((entity) => entity.id === sourceEntityId)?.type;
  const targetEntityType = entities.find((entity) => entity.id === targetEntityId)?.type;

  const compatibleRelationshipTypes = relationshipTypes.filter((typeOption) => {
    if (!sourceEntityType || !targetEntityType) {
      if (sourceEntityType && !typeOption.allowedSourceTypes.includes(sourceEntityType)) {
        return false;
      }

      if (targetEntityType && !typeOption.allowedTargetTypes.includes(targetEntityType)) {
        return false;
      }

      return true;
    }

    return (
      typeOption.allowedSourceTypes.includes(sourceEntityType) && typeOption.allowedTargetTypes.includes(targetEntityType)
    );
  });

  const availableRelationshipGroups = useMemo(
    () => Array.from(new Set(compatibleRelationshipTypes.map((typeOption) => typeOption.family))),
    [compatibleRelationshipTypes],
  );

  const groupedRelationshipTypes = compatibleRelationshipTypes.filter((typeOption) =>
    relationshipGroup ? typeOption.family === relationshipGroup : true,
  );

  const selectedRelationshipGroupIsAvailable =
    relationshipGroup === "" || availableRelationshipGroups.includes(relationshipGroup);

  const sourceEntityOptions = entities.filter((entity) => {
    if (!selectedRelationshipType) {
      return true;
    }

    return selectedRelationshipType.allowedSourceTypes.includes(entity.type);
  });

  const targetEntityOptions = entities.filter((entity) => {
    if (!selectedRelationshipType) {
      return true;
    }

    return selectedRelationshipType.allowedTargetTypes.includes(entity.type);
  });

  useEffect(() => {
    if (!selectedRelationshipGroupIsAvailable) {
      setRelationshipGroup("");
    }
  }, [selectedRelationshipGroupIsAvailable]);

  useEffect(() => {
    if (!relationshipType) {
      return;
    }

    const selectedTypeIsAvailable = compatibleRelationshipTypes.some((typeOption) => typeOption.key === relationshipType);

    if (!selectedTypeIsAvailable) {
      setRelationshipType("");
      return;
    }

    if (selectedRelationshipType && selectedRelationshipType.family !== relationshipGroup) {
      setRelationshipGroup(selectedRelationshipType.family);
    }
  }, [compatibleRelationshipTypes, relationshipGroup, relationshipType, selectedRelationshipType]);

  useEffect(() => {
    if (!sourceEntityId) {
      return;
    }

    const selectedSourceStillAllowed = sourceEntityOptions.some((entity) => entity.id === sourceEntityId);

    if (!selectedSourceStillAllowed) {
      setSourceEntityId("");
    }
  }, [sourceEntityId, sourceEntityOptions]);

  useEffect(() => {
    if (!targetEntityId) {
      return;
    }

    const selectedTargetStillAllowed = targetEntityOptions.some((entity) => entity.id === targetEntityId);

    if (!selectedTargetStillAllowed) {
      setTargetEntityId("");
    }
  }, [targetEntityId, targetEntityOptions]);

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    await onSubmit({
      certaintyStatus,
      lifecycleStatus,
      notes,
      relationshipType,
      sourceEntityId,
      targetEntityId,
      visibilityStatus,
    });
  }

  return (
    <form
      className="record-form relationship-form"
      onSubmit={(event) => {
        void handleSubmit(event);
      }}
    >
      <label className="field">
        <span className="field-label">Source Entity</span>
        <select
          value={sourceEntityId}
          onChange={(event) => {
            setSourceEntityId(event.target.value);
          }}
        >
          <option value="">Select source entity</option>
          {sourceEntityOptions.map((entity) => (
            <option key={entity.id} value={entity.id}>
              {entity.name}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span className="field-label">Relationship Group</span>
        <select
          value={relationshipGroup}
          onChange={(event) => {
            const nextRelationshipGroup = event.target.value;
            setRelationshipGroup(nextRelationshipGroup);

            const selectedTypeStillMatches = compatibleRelationshipTypes.some(
              (typeOption) => typeOption.key === relationshipType && typeOption.family === nextRelationshipGroup,
            );

            if (!selectedTypeStillMatches) {
              setRelationshipType("");
            }
          }}
        >
          <option value="">Select relationship group</option>
          {availableRelationshipGroups.map((groupOption) => (
            <option key={groupOption} value={groupOption}>
              {formatRelationshipFamilyLabel(groupOption)}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span className="field-label">Relationship Type</span>
        <select
          disabled={!relationshipGroup}
          value={relationshipType}
          onChange={(event) => {
            setRelationshipType(event.target.value);
          }}
        >
          <option value="">{relationshipGroup ? "Select relationship type" : "Select relationship group first"}</option>
          {groupedRelationshipTypes.map((typeOption) => (
            <option key={typeOption.key} value={typeOption.key}>
              {typeOption.label}
            </option>
          ))}
        </select>
      </label>
      <label className="field">
        <span className="field-label">Target Entity</span>
        <select
          value={targetEntityId}
          onChange={(event) => {
            setTargetEntityId(event.target.value);
          }}
        >
          <option value="">Select target entity</option>
          {targetEntityOptions.map((entity) => (
            <option key={entity.id} value={entity.id}>
              {entity.name}
            </option>
          ))}
        </select>
      </label>
      <div className="filter-grid">
        <label className="field">
          <span className="field-label">Lifecycle</span>
          <select
            value={lifecycleStatus}
            onChange={(event) => {
              setLifecycleStatus(event.target.value);
            }}
          >
            {LIFECYCLE_OPTIONS.map((statusOption) => (
              <option key={statusOption} value={statusOption}>
                {statusOption}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span className="field-label">Visibility</span>
          <select
            value={visibilityStatus}
            onChange={(event) => {
              setVisibilityStatus(event.target.value);
            }}
          >
            {VISIBILITY_OPTIONS.map((statusOption) => (
              <option key={statusOption} value={statusOption}>
                {statusOption}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span className="field-label">Certainty</span>
          <select
            value={certaintyStatus}
            onChange={(event) => {
              setCertaintyStatus(event.target.value);
            }}
          >
            {CERTAINTY_OPTIONS.map((statusOption) => (
              <option key={statusOption} value={statusOption}>
                {statusOption}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label className="field">
        <span className="field-label">Notes</span>
        <textarea
          rows={5}
          value={notes}
          onChange={(event) => {
            setNotes(event.target.value);
          }}
        />
      </label>
      {selectedRelationshipType?.isCustom ? (
        <p className="section-copy">
          Editing a custom type?{" "}
          <Link className="text-link" to={`/campaigns/${campaignId}/relationships`}>
            Jump to relationship management.
          </Link>
        </p>
      ) : null}
      {submitError ? <p className="field-error">{submitError}</p> : null}
      <button className="primary-button" disabled={submitting} type="submit">
        {submitting ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
