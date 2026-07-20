export type FarmProfile = {
  id: number;
  username: string;
  location: string;
  crop: string;
  farm_size_hectares: number;
  problem?: string;
};

const PROFILE_KEY = "agriguard-active-profile";

export function getActiveProfile(): FarmProfile | null {
  if (typeof window === "undefined") return null;
  const saved = window.localStorage.getItem(PROFILE_KEY);
  return saved ? JSON.parse(saved) as FarmProfile : null;
}

export function saveActiveProfile(profile: FarmProfile) {
  window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}
