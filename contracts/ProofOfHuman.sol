// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @notice Soulbound (non-transferable) badge minted once a face is matched
/// to a real, findable social/web post. Use case: "Proof-of-Human" — dating
/// apps, DAOs, freelance platforms mint this to a user's wallet after a
/// verified match, then re-check it on-chain instead of trusting a
/// screenshot. Can't be sold, gifted, or moved to a fake/bot wallet.
contract ProofOfHuman {
    struct Badge {
        bytes32 faceHash;
        bytes32 postHash;
        string  sourceUrl;
        uint256 timestamp;
    }

    string public constant name = "Proof of Human";
    string public constant symbol = "POH";

    uint256 public nextTokenId;
    mapping(uint256 => address) public ownerOf;
    mapping(address => uint256) public balanceOf;
    mapping(uint256 => Badge) public badges;
    mapping(address => bool) public hasBadge; // one badge per wallet

    event Minted(uint256 indexed tokenId, address indexed to, bytes32 faceHash, bytes32 postHash, string sourceUrl);

    function mint(address to, bytes32 faceHash, bytes32 postHash, string calldata sourceUrl) external returns (uint256) {
        require(!hasBadge[to], "wallet already verified");

        uint256 tokenId = nextTokenId++;
        ownerOf[tokenId] = to;
        balanceOf[to] += 1;
        hasBadge[to] = true;
        badges[tokenId] = Badge(faceHash, postHash, sourceUrl, block.timestamp);

        emit Minted(tokenId, to, faceHash, postHash, sourceUrl);
        return tokenId;
    }

    /// @notice Soulbound: transfers always revert.
    function transferFrom(address, address, uint256) external pure {
        revert("soulbound: non-transferable");
    }

    function safeTransferFrom(address, address, uint256) external pure {
        revert("soulbound: non-transferable");
    }

    function approve(address, uint256) external pure {
        revert("soulbound: non-transferable");
    }

    /// @notice Re-verify a badge's data against what was originally minted.
    function verify(uint256 tokenId, bytes32 faceHash, bytes32 postHash) external view returns (bool) {
        Badge storage b = badges[tokenId];
        return b.faceHash == faceHash && b.postHash == postHash;
    }

    function getBadge(uint256 tokenId) external view returns (
        bytes32 faceHash,
        bytes32 postHash,
        string memory sourceUrl,
        uint256 timestamp
    ) {
        Badge storage b = badges[tokenId];
        return (b.faceHash, b.postHash, b.sourceUrl, b.timestamp);
    }
}
