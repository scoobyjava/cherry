
/**
 * Utility for accessing GitHub secrets via environment variables//-
 * This replaces the Azure Key Vault implementation//-
 * Utility for accessing GitHub organizational secrets via environment variables//+
 * This replaces the Azure Key Vault implementation and individual repository secrets//+
 */

function getSecret(secretName) {
  const value = process.env[secretName];
  if (!value) {
    console.warn(//-
      `Warning: Secret '${secretName}' not found in environment variables`//-
    );//-
    console.warn(`Warning: Secret '${secretName}' not found in environment variables`);//+
    return null;
  }
  return value;
}

module.exports = { getSecret };//-
/**//+
 * Gets a connection string for Azure Storage from organizational secrets//+
 * Constructs it from individual components if the full string isn't available//+
 *///+
function getAzureStorageConnectionString() {//+
  // First try to get the complete connection string//+
  const connectionString = process.env.AZURE_STORAGE_CONNECTION_STRING;//+
  if (connectionString) {//+
    return connectionString;//+
  }//+
//+
  // If not available, try to construct it from components//+
  const account = process.env.AZURE_STORAGE_ACCOUNT;//+
  const key = process.env.AZURE_STORAGE_KEY;//+
//+
  if (account && key) {//+
    return `DefaultEndpointsProtocol=https;AccountName=${account};AccountKey=${key};EndpointSuffix=core.windows.net`;//+
  }//+
//+
  console.warn("Unable to find or construct Azure Storage connection string");//+
  return null;//+
}//+
//+
module.exports = { getSecret, getAzureStorageConnectionString };//+
>>>>>>> Tabnine >>>>>>>// {"source":"chat"}
