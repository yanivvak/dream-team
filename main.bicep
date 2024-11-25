
// Define the name of the Azure OpenAI resource name 
param azureOpenaiResourceName string = 'dream' 

// Define the name of the Azure OpenAI model name  
param azureOpenaiDeploymentName string = 'gpt-4o' 



//Define the OpenAI resource
resource openai 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: azureOpenaiResourceName
  location: location
 
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  properties: {
   
  }

}
// Define the OpenAI deployment
resource openaideployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  name: azureOpenaiDeploymentName
  sku: {
    name: 'Standard'
    capacity: 1
  }
  parent: openai
  properties: {
    model: {
      name: 'gpt-4o'
      format: 'OpenAI'
      version: '2024-05-13'
      
    }
    raiPolicyName: 'Microsoft.Default'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
 
  }
}

// value: openaideployment.name 