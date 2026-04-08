import { useEffect, useRef, useState } from "react";

export function useLocalStorageState(storageKey: string, initialValue = "") {
  const [value, setValue] = useState(initialValue);
  const pendingHydrationKey = useRef<string | null>(null);

  useEffect(() => {
    pendingHydrationKey.current = storageKey;
    setValue(window.localStorage.getItem(storageKey) ?? initialValue);
  }, [initialValue, storageKey]);

  useEffect(() => {
    if (pendingHydrationKey.current === storageKey) {
      pendingHydrationKey.current = null;
      return;
    }

    window.localStorage.setItem(storageKey, value);
  }, [storageKey, value]);

  return [value, setValue] as const;
}
