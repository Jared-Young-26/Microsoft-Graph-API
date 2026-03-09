const assert = require("node:assert/strict");

const persistenceSecurity = require("./persistence_security.js");

const profileConfig = persistenceSecurity.sanitizeProfileConfig({
  tenant_id: "tenant",
  client_id: "client",
  client_secret: "super-secret",
  graph_user_id: "user@example.com",
});

assert.deepEqual(profileConfig, {
  tenant_id: "tenant",
  client_id: "client",
  graph_user_id: "user@example.com",
});

const profiles = persistenceSecurity.sanitizeProfiles([
  {
    name: "Profile A",
    config: {
      tenant_id: "tenant",
      client_secret: "secret",
      spo_admin_url: "https://contoso-admin.sharepoint.com",
    },
  },
]);

assert.deepEqual(profiles, [
  {
    name: "Profile A",
    config: {
      tenant_id: "tenant",
      spo_admin_url: "https://contoso-admin.sharepoint.com",
    },
  },
]);

const paramsStore = persistenceSecurity.sanitizeActionPackParamsStore({
  packA: {
    stepParams: {
      "exchange.send_mail": {
        mailbox: "user@example.com",
        client_secret: "remove-me",
        nested: {
          api_key: "remove-me-too",
          subject: "hello",
        },
      },
    },
    includeSteps: {
      "exchange.send_mail": true,
    },
    dryRun: false,
  },
});

assert.deepEqual(paramsStore, {
  packA: {
    stepParams: {
      "exchange.send_mail": {
        mailbox: "user@example.com",
        nested: {
          subject: "hello",
        },
      },
    },
    includeSteps: {
      "exchange.send_mail": true,
    },
    dryRun: false,
  },
});

const history = persistenceSecurity.sanitizeActionPackHistory([
  {
    packId: "packA",
    stepParams: {
      "exchange.send_mail": {
        mailbox: "user@example.com",
        access_token: "drop",
        message: "hello",
      },
    },
    includeSteps: {
      "exchange.send_mail": true,
    },
    dryRun: true,
  },
]);

assert.deepEqual(history, [
  {
    packId: "packA",
    stepParams: {
      "exchange.send_mail": {
        mailbox: "user@example.com",
        message: "hello",
      },
    },
    includeSteps: {
      "exchange.send_mail": true,
    },
    dryRun: true,
  },
]);

assert.equal(persistenceSecurity.isSecretLikeKey("client_secret"), true);
assert.equal(persistenceSecurity.isSecretLikeKey("apiToken"), true);
assert.equal(persistenceSecurity.isSecretLikeKey("displayName"), false);

console.log("persistence security tests passed");
