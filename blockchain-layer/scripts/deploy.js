//blockchain-layer/scripts/deploy.js
const hre = require("hardhat");

async function main() {

  console.log("🚀 Deploying StreetLight Contract...");

  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying with account:", deployer.address);

  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance));

  // Contract factory
  const StreetLight = await hre.ethers.getContractFactory("StreetLight");

  // Deploy
  const streetlight = await StreetLight.deploy();

  // Wait for deployment
  await streetlight.waitForDeployment();

  const contractAddress = await streetlight.getAddress();

  console.log("✅ StreetLight deployed successfully!");
  console.log("📍 Contract Address:", contractAddress);

}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });