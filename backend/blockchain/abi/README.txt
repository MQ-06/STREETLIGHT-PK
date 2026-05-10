Place StreetLight.json here for production (e.g. Render).

Generate it locally:
  cd blockchain-layer
  npm install
  npx hardhat compile

Then copy:
  blockchain-layer/artifacts/contracts/streetLight.sol/StreetLight.json
  -> this folder as StreetLight.json

Commit StreetLight.json and push so the backend can load the contract ABI.
