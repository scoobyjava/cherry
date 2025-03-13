// ...existing code...

const { getSecret } = require("./config/azureKeyVault");

// Example usage: retrieve a secret named 'MY_SECRET'
(async () => {
  try {
    const secretValue = await getSecret("MY_SECRET");
    console.log(`Retrieved secret: ${secretValue}`);
    // ...existing code...
  } catch (error) {
    console.error("Error retrieving secret from Azure Key Vault:", error);
    // ...existing code...
  }
})();

// ...existing code...
