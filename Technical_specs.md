# Technical Specs

In order to understand the implementation aspects, we would recommend you to consider the pre-reads in the following areas:

- [ ]  authentication in ethereum
- [ ]  simple staking games, voting games
- [ ]  ERC20 token and gensis
- [ ]  Ethereum APIs & testnet deployments


Starterem Dapp can be abstracted under following core components and their interactons as shown in the architecture diagram below:

- App Server (serving web3 app)
- Auth Server
- GraphQL Server
- Smart Contracts


![startereum dapp architecture](https://user-images.githubusercontent.com/1164613/40483920-6e7c464a-5f77-11e8-919b-4c0377c5760d.png)

# Components

## Authentication

We don't need a pure blockchain based authentication. It is slow and it costs gas. We want to register the user with their public ethereum address and authenticate by proof of ownership of respective registered address.

*assumption: we need the users to have metamask browser extension installed.*

Our User model consist of following attributes:

- email
- username
- publicAddress
- nonce
- password

`publicAddress` should be automatically fetched from web3.eth.coinbase which will get the current Metamask account's public address

`nonce` is a random string generated at the time of sign up and each subsequent verification. It's purpose is for validating the signatures as proof of ownership of the publicAddress

`username` will be used to identify the user in the app and leaderboard

`email` will be used to send notifications and system messages

`password` is an added security layer. 

Please look at the workflow below:

![authentication flow](https://user-images.githubusercontent.com/1164613/40483919-6e518cb6-5f77-11e8-8434-27846f9a3fea.png)


helpful reads: 

[One-click Login with Blockchain: A MetaMask Tutorial](https://www.toptal.com/ethereum/one-click-login-flows-a-metamask-tutorial)

## Smart Contract

Startereum is an ERC20 token used for staking in the project matches. The game is described in the TWR Concept in the root directory.

### Overview

1. A `wave` is a tournament style format for creating the ranked list of projects and consists of `matches`. The number of matches depends on the new projects participating in the wave. Generally for a one-to-one comparison, for N projects in a wave there will be N*(N-1)/2 number of matches.
2. A `match` is a staking game between two project on a single dimension. A match starts with default parameters such as `minStake`, `maxStake`, `threshold`, `endTime` but can be changed if desired. 
3. In order to create a new match, owner must provide `waveID`, hashes of the two competing projects as `tags`, and time when the game will expire and reward the winning players.
4. The game contract implements call scheduling with Ethereum Alarm Clock service to execute the set of functions on reaching the `endTime` of the game. More information on that can be found here: [http://blog.ethereum-alarm-clock.com/blog/2016/1/16/the-alarm-service-is-now-available-on-the-testnet](http://blog.ethereum-alarm-clock.com/blog/2016/1/16/the-alarm-service-is-now-available-on-the-testnet)
5. Players should be able to subscribe to the wave of matches and they can only play the matches that are part of the subscribed wave.
6. Players can play the match by calling the `stake` with  `value` and staking preference `tag` on the smart contract.
7. Players can `unstake` anytime before the `endTime` of the match.
8. If the staking value is below the `minStake` or above the `maxStake` of the respective match, then the staking request is rejected and the value is returned (adjusting the gas price)
9. If the staking preference `tag` is not set, then the staking request is rejected and the value is returned.
10. Staking preference is done by setting `tag` to one of the endorsed hashes of the match. 

### Reward Calculations

1. The contract implements the following functions to trigger rewards: `find_winner`, `calc_rewards`, `distribute_rewards`.
2. `find_winner` figures out which of the endorsed hashes won the majority of tokens
3. This is how we define the reward formula:
  1. lets suppose a playerA sent `n` tokens to the later concluded winning side 
  2. lets suppose win:lose is W:L in token volume
  3. lets suppose `n` token staked by playerA is `p%` of the total winning token, i.e `n/W*100`
  4. then playerA is supposed to win `p%` of `L`, i.e `p/100*L`
  5. the reward (`R`) for each winning participant will be `n(i) * L / W`, where `i` represents each unique participant
  6. the total tokens (stake + reward, `T`) to be sent back to a winning participant will be `n(i) + n(i) * L / W`
4. `calc_rewards` works in the following way:
  1. iterates through all the addresses that staked to the contract.
  2. In each iteration,
    1. it checks if the stake is in favour of winning token determined earlier using `find_winner` or not
    2. if it is not a winning address, then it skips to the next iteration
    3. else, it calculates the reward: R using the above formulation
    4. It then calls `distribute_reward` with the following value of `T`: 

        `n(i) + n(i) * L / W`

5. `distribute_rewards` sends the desired tokens back to the originating staking addresses with the above calculations

**further considerations:**

- *The user experience of sending the votes to ethereum blockchain can be improved by optimistic voting confirmation and then batching the requests of all the games played in a session together at the end of the game session.*
- *The house fee needs to be factored before rewarding the winners*
- *The ethereum gas fee needs to be factored in rewarding the winners*

### Smart Contract Functions

Below are the high level functions that are part of the Startereum smart contract. I have also proposed some design patterns inspired by [Numerai]([https://github.com/numerai/contract](https://github.com/numerai/contract)), [StakeBank]([https://github.com/HarbourProject/stakebank](https://github.com/HarbourProject/stakebank)) and [EIP 900: Simple Staking Interface]([https://github.com/ethereum/EIPs/issues/900](https://github.com/ethereum/EIPs/issues/900)).

**player functions**

`transfer(address _to, uint256 _value)`

- `_to` the address where to send the tokens
- `_value` the amount to send

`stake(uint256 _value, bytes32 _tag, uint256 _waveID, uint256 _matchID)`

- `_value` the amount to stake
- `_tag` the preference hash of the project to stake on
- `_waveID` the ID that represent the wave
- `_matchID` the ID that represent the match being staked into

`unstake(uint256 _value, uint256 _waveID, uint256 _matchID)`

- `_value` the amount from the previously staked value to unstake
- `_waveID` the ID that represent the wave
- `_matchID` the ID that represent the match being staked into

**Owner functions**

`createWave(uint256 _waveID, uint256[] _tags)`

- `_waveID` the ID to create the wave
- `_tags` the array of all the participating projects in this wave

`createMatch(uint256 _waveID, uint256 _matchID, uint256 _endTime, uint256 _tagA, uint256 _tagB, uint256 _minStake, uint256 _maxStake, uint256 _threshold)`

- `_waveID` the ID that represent the wave
- `_matchID` the ID to create the match
- `_endtime` the future block time when the game will expire and reward will be triggered
- `_tagA, _tagB` the hashes of the two projects that constitute this game
- `_minStake` the minimum staking value required to play the game. (default is set to 3 STR)
- `_maxStake` the maximum staking value required to play the game. (default is set to 100 STR)
- `_threshold` the minimum value of total staked value to finalise the game. (default is set to 1000 STR)

`stopMatch(uint256 _waveID, uint256 _matchID)`

- `_waveID` the ID that represent the wave
- `_matchID` the ID that represent the match

`resumeMatch(uint256 _waveID, uint256 _matchID)`

- `_waveID` the ID that represent the wave
- `_matchID` the ID that represent the match

`disableStoppingMatch(uint256 _waveID, uint256 _matchID)`

- `_waveID` the ID that represent the wave
- `_matchID` the ID that represent the match

**Inspection functions**

- Returns the data about wave: Number of matches, List of matches, List of project tags

`getWave(uint256 _waveID)`


- Returns the data about match: participating project tags, ending time of the match, status of the match

`getMatch(uint256 _waveID, uint256 _matchID)`

- Returns the status of the match: 0 ended, 1 live

`getMatchStatus(uint256 _waveID, uint256 _matchID)`

- Returns the result of the match: tokens staked for both project tags (tokensForTagA, tokensForTagB), Winner tag value

`getMatchResults(uint256 _waveID, uint256 _matchID)`

- Returns the staked value corresponding to an address in a match: stakedValue

`getStakeFor(uint256 _waveID, uint256 _matchID, address _staker, bytes32 _tag)`

- Returns the reward value corresponding to an address in a match: rewardValue

`getRewardFor(uint256 _waveID, uint256 _matchID, address _staker, bytes32 _tag)`

**Events**

The following events are emitted from the contracts. The events is a good way to generate the data layer for the game interfaces. By storing the events in our centralised data store, we can improve the user experience of the app by offering them live statuses of the matches and their results.

- Staked(stakerAddress, tag, totalAmountStaked, waveID, matchID)
- WaveCreated(waveID)
- MatchCreated(waveID, matchID, endTime, minStake, maxStake, threshold)
- MatchStopped(waveID, matchID)
- MatchResumed(waveID, matchID)
- MatchEnded(waveID, matchID)

**Design pattern**

Contracts
- StartereumBackend.sol
- StartereumDelegate.sol
- StartereumShared.sol

`StartereumShared` implement data structures that will be used in the other smart contracts mainly `StartereumBackend` and `StartereumDelegate`

`StartereumShared` extends an [OpenZepplin interface]([https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/ownership/Shareable.sol](https://github.com/OpenZeppelin/zeppelin-solidity/blob/master/contracts/ownership/Shareable.sol)) called `Shareable, StoppableShareable` that implements owner control features such stopping and resuming the contract functions.

`StartereumBackend` implements basic ERC20 functionalities such as transfer, minting, withdraw etc, and also creates interfaces for staking match operations via `StartereumDelegate` contract methods. The delegate contract can be upgraded but the backend contract is immutable.

## GraphQL Server

Since, we are writing directly on contracts, we will use the contract events to populate data models. It is recommended to use graphQL as the data serving layer as the project will be evolving fast to update existing models or add new models.

We have following data models and querying requirements:

**User model**

- Account of balances
  - how many/what games a user has played
  - what is the current balance of the user wallet
  - how many/what games a user has won
  - how many/what games a user has lost
- User management
  - what is my publicAddress
  - what is my latest nonce (protected method)
  - what is my email
  - what is my password
  - update functions

**Game Model**

- Game status
  - Is the game live?
  - Is the game finished?
  - When is the game ending?
  - What is the result of the game?
  - What are the endorsed projects of the game?
  - What is the game type?
- Game collection and session
  - create a new game
  - list of active games
  - list of inactive games
  - create a new session of games for a user A
  - commit a session on chain