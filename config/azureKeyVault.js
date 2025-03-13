const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");

// Use the Key Vault name from the environment or default to 'cherryai-kv'
const keyVaultName = process.env.KEY_VAULT_NAME || "cherryai-kv";
const vaultUrl = `https://${keyVaultName}.vault.azure.net`;

const credential = new DefaultAzureCredential();
const client = new SecretClient(vaultUrl, credential);

async function getSecret(secretName) {
  try {
    const secret = await client.getSecret(secretName);
    return secret.value;
  } catch (error) {
    console.error(`Error retrieving secret ${secretName}:`, error);
    throw error;
  }
}

module.exports = { getSecret };
