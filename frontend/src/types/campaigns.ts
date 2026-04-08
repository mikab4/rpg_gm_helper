export type Campaign = {
  id: string;
  ownerId: string;
  name: string;
  description: string | null;
  createdAt: string;
  updatedAt: string;
};

export type CampaignCreate = {
  ownerId: string;
  name: string;
  description: string | null;
};

export type CampaignUpdate = {
  name?: string;
  description?: string | null;
};
