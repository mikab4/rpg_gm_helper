import { useState, type SyntheticEvent } from "react";

type CampaignFormValues = {
  description: string;
  name: string;
};

type CampaignFormProps = {
  initialValues: CampaignFormValues;
  submitLabel: string;
  submitError: string | null;
  submitting: boolean;
  onSubmit: (values: CampaignFormValues) => Promise<void>;
};

export function CampaignForm({
  initialValues,
  submitLabel,
  submitError,
  submitting,
  onSubmit,
}: CampaignFormProps) {
  const [name, setName] = useState(initialValues.name);
  const [description, setDescription] = useState(initialValues.description);
  const [nameError, setNameError] = useState<string | null>(null);

  async function handleSubmit(event: SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName) {
      setNameError("Campaign name is required.");
      return;
    }

    setNameError(null);

    await onSubmit({
      description,
      name: trimmedName,
    });
  }

  return (
    <form
      className="record-form"
      onSubmit={(event) => {
        void handleSubmit(event);
      }}
    >
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
        <span className="field-label">Description</span>
        <textarea
          rows={5}
          value={description}
          onChange={(event) => {
            setDescription(event.target.value);
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
