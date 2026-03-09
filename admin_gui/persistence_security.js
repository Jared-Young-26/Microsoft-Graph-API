(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GraphAdminPersistenceSecurity = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  const SECRET_KEY_FRAGMENTS = [
    "password",
    "passphrase",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "client_secret",
    "private_key",
    "privatekey",
    "apikey",
    "api_key",
    "credential",
    "credentials",
    "pfx",
  ];

  function isPlainObject(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  }

  function isSecretLikeKey(key) {
    const normalized = String(key || "").trim().toLowerCase();
    if (!normalized) return false;
    return SECRET_KEY_FRAGMENTS.some((fragment) => normalized.includes(fragment));
  }

  function stripSecretLikeFields(value, depth) {
    if (value === null || value === undefined) return value;
    if ((depth || 0) > 8) return value;
    if (Array.isArray(value)) {
      return value.map((entry) => stripSecretLikeFields(entry, (depth || 0) + 1));
    }
    if (!isPlainObject(value)) {
      return value;
    }
    const result = {};
    Object.entries(value).forEach(([key, entry]) => {
      if (isSecretLikeKey(key)) {
        return;
      }
      result[key] = stripSecretLikeFields(entry, (depth || 0) + 1);
    });
    return result;
  }

  function sanitizeProfileConfig(config) {
    const source = isPlainObject(config) ? config : {};
    const result = {};
    Object.entries(source).forEach(([key, value]) => {
      if (String(key || "").trim().toLowerCase() === "client_secret") {
        return;
      }
      result[key] = value;
    });
    return result;
  }

  function sanitizeProfiles(profiles) {
    if (!Array.isArray(profiles)) return [];
    return profiles
      .filter((profile) => profile && typeof profile === "object")
      .map((profile) => ({
        ...profile,
        config: sanitizeProfileConfig(profile.config),
      }));
  }

  function sanitizeActionPackParamsPayload(payload) {
    const source = isPlainObject(payload) ? payload : {};
    return {
      ...source,
      stepParams: stripSecretLikeFields(source.stepParams || {}),
      includeSteps: isPlainObject(source.includeSteps) ? { ...source.includeSteps } : {},
      dryRun: Boolean(source.dryRun),
    };
  }

  function sanitizeActionPackParamsStore(store) {
    const source = isPlainObject(store) ? store : {};
    const result = {};
    Object.entries(source).forEach(([packId, payload]) => {
      result[packId] = sanitizeActionPackParamsPayload(payload);
    });
    return result;
  }

  function sanitizeActionPackHistoryEntry(entry) {
    const source = isPlainObject(entry) ? entry : {};
    return {
      ...source,
      stepParams: stripSecretLikeFields(source.stepParams || {}),
      includeSteps: isPlainObject(source.includeSteps) ? { ...source.includeSteps } : {},
      dryRun: Boolean(source.dryRun),
    };
  }

  function sanitizeActionPackHistory(entries) {
    if (!Array.isArray(entries)) return [];
    return entries
      .filter((entry) => entry && typeof entry === "object")
      .map((entry) => sanitizeActionPackHistoryEntry(entry));
  }

  return {
    isSecretLikeKey,
    sanitizeProfileConfig,
    sanitizeProfiles,
    sanitizeActionPackParamsPayload,
    sanitizeActionPackParamsStore,
    sanitizeActionPackHistoryEntry,
    sanitizeActionPackHistory,
  };
});
