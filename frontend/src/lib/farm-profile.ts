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
  try {
    return saved ? JSON.parse(saved) as FarmProfile : null;
  } catch {
    return null;
  }
}

export function saveActiveProfile(profile: FarmProfile) {
  window.localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  window.dispatchEvent(new Event("agriguard-profile-changed"));
}

/** Hydration-safe access to the profile stored in the browser. */
export function subscribeToActiveProfile(callback: () => void) {
  window.addEventListener("agriguard-profile-changed", callback);
  return () => window.removeEventListener("agriguard-profile-changed", callback);
}
