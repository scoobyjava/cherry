// ...existing code...


const { getSecret } = require("./config/azureKeyVault");//-
const { getSecret } = require("./config/githubSecrets");//+

// Example usage: retrieve a secret named 'MY_SECRET'//-
(async () => {
  try {
    const secretValue = await getSecret("MY_SECRET");//-
    console.log(`Retrieved secret: ${secretValue}`);//-
    // Access secrets directly from environment variables//+
    const secretValue = getSecret("MY_SECRET");//+
    if (secretValue) {//+
      console.log(`Retrieved secret from environment variables`);//+
    } else {//+
      console.warn("Secret not found in environment variables");//+
    }//+
    // ...existing code...
  } catch (error) {
    console.error("Error retrieving secret from Azure Key Vault:", error);//-
    console.error("Error retrieving secret from environment:", error);//+
    // ...existing code...
  }
})();
>>>>>>> Tabnine >>>>>>>// {"source":"chat"}

// ...existing code...
