import { useMemo, useState, type SyntheticEvent } from "react";

import { ENTITY_TYPE_OPTIONS, formatEntityTypeLabel } from "../entities/entityTypes";
import type { Campaign } from "../types/campaigns";

export type EntityFormValues = {
  campaignId: string;
  name: string;
  summary: string;
  type: string;
};

type EntityFormProps = {
  campaignOptions: Campaign[];
  fixedCampaignId?: string;
  initialValues: EntityFormValues;
  submitError: string | null;
  submitLabel: string;
  submitting: boolean;
  onSubmit: (values: EntityFormValues) => Promise<void>;
};

export function EntityForm({
  campaignOptions,
  fixedCampaignId,
  initialValues,
  submitError,
  submitLabel,
  submitting,
  onSubmit,
}: EntityFormProps) {
  const [campaignId, setCampaignId] = useState(initialValues.campaignId);
  const [type, setType] = useState(initialValues.type);
  const [name, setName] = useState(initialValues.name);
  const [summary, setSummary] = useState(initialValues.summary);
  const [campaignError, setCampaignError] = useState<string | null>(null);
  const [typeError, setTypeError] = useState<string | null>(null);
  const [nameError, setNameError] = useState<string | null>(null);

  const selectedCampaignId = useMemo(() => fixedCampaignId ?? campaignId, [campaignId, fixedCampaignId]);
  const hasLegacyTypeSelection = useMemo(
    () => Boolean(type) && !ENTITY_TYPE_OPTIONS.some((entityTypeOption) => entityTypeOption.value === type),
    [type],
  );

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedType = type.trim();
    const trimmedName = name.trim();
    let hasError = false;

    if (!selectedCampaignId) {
      setCampaignError("Campaign is required.");
      hasError = true;
    } else {
      setCampaignError(null);
    }

    if (!trimmedType) {
      setTypeError("Entity type is required.");
      hasError = true;
    } else {
      setTypeError(null);
    }

    if (!trimmedName) {
      setNameError("Entity name is required.");
      hasError = true;
    } else {
      setNameError(null);
    }

    if (hasError) {
      return;
    }

    await onSubmit({
      campaignId: selectedCampaignId,
      name: trimmedName,
      summary,
      type: trimmedType,
    });
  }

  return (
    <form
      className="record-form"
      onSubmit={(event) => {
        void handleSubmit(event);
      }}
    >
      {fixedCampaignId ? null : (
        <label className="field">
          <span className="field-label">Campaign</span>
          <select
            value={campaignId}
            onChange={(event) => {
              setCampaignId(event.target.value);
            }}
          >
            <option value="">Select a campaign</option>
            {campaignOptions.map((campaign) => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>
          {campaignError ? <span className="field-error">{campaignError}</span> : null}
        </label>
      )}
      <label className="field">
        <span className="field-label">Type</span>
        <select
          value={type}
          onChange={(event) => {
            setType(event.target.value);
          }}
        >
          <option value="">Select an entity type</option>
          {hasLegacyTypeSelection ? <option value={type}>{formatEntityTypeLabel(type)} (legacy)</option> : null}
          {ENTITY_TYPE_OPTIONS.map((entityTypeOption) => (
            <option key={entityTypeOption.value} value={entityTypeOption.value}>
              {entityTypeOption.label}
            </option>
          ))}
        </select>
        {typeError ? <span className="field-error">{typeError}</span> : null}
      </label>
      <label className="field">
        <span className="field-label">Name</span>
        <input
          value={name}
          onChange={(event) => {
            setName(event.target.value);
          }}
        />
        {nameError ? <span className="field-error">{nameError}</span> : null}
      </label>
      <label className="field">
        <span className="field-label">Summary</span>
        <textarea
          rows={6}
          value={summary}
          onChange={(event) => {
            setSummary(event.target.value);
          }}
        />
      </label>
      {submitError ? <p className="field-error">{submitError}</p> : null}
      <button className="primary-button" disabled={submitting} type="submit">
        {submitting ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
