export type FarmProfile = {
  id: number;
  username: string;
  location: string;
  crop: string;
  farm_size_hectares: number;
  problem?: string;
};

const PROFILE_KEY = "agriguard-active-profile";
let cachedRaw: string | null | undefined;
let cachedProfile: FarmProfile | null = null;

export function getActiveProfile(): FarmProfile | null {
  if (typeof window === "undefined") return null;
  const saved = window.localStorage.getItem(PROFILE_KEY);
  // useSyncExternalStore requires referentially stable snapshots. Only parse
  // when storage has genuinely changed; otherwise return the same object.
  if (saved === cachedRaw) return cachedProfile;
  cachedRaw = saved;
  try {
    cachedProfile = saved ? JSON.parse(saved) as FarmProfile : null;
  } catch {
    cachedProfile = null;
  }
  return cachedProfile;
}

export function saveActiveProfile(profile: FarmProfile) {
  const serialized = JSON.stringify(profile);
  cachedRaw = serialized;
  cachedProfile = profile;
  window.localStorage.setItem(PROFILE_KEY, serialized);
  window.dispatchEvent(new Event("agriguard-profile-changed"));
}

/** Hydration-safe access to the profile stored in the browser. */
export function subscribeToActiveProfile(callback: () => void) {
  window.addEventListener("agriguard-profile-changed", callback);
  return () => window.removeEventListener("agriguard-profile-changed", callback);
}
