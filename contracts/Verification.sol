// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title Verification
/// @notice Stores tamper-evident records for face-match findings (image hash + source post hash + metadata).
contract Verification {
    struct Record {
        bytes32 faceHash;      // hash of the encoded face vector / input image
        bytes32 postHash;      // hash of the discovered social media post (url + content)
        string  sourceUrl;     // URL where the match was found
        uint256 timestamp;
        address submitter;
    }

    Record[] public records;

    event RecordAdded(
        uint256 indexed id,
        bytes32 faceHash,
        bytes32 postHash,
        string sourceUrl,
        address submitter
    );

    function addRecord(bytes32 faceHash, bytes32 postHash, string calldata sourceUrl) external returns (uint256) {
        records.push(Record(faceHash, postHash, sourceUrl, block.timestamp, msg.sender));
        uint256 id = records.length - 1;
        emit RecordAdded(id, faceHash, postHash, sourceUrl, msg.sender);
        return id;
    }

    function getRecord(uint256 id) external view returns (
        bytes32 faceHash,
        bytes32 postHash,
        string memory sourceUrl,
        uint256 timestamp,
        address submitter
    ) {
        Record storage r = records[id];
        return (r.faceHash, r.postHash, r.sourceUrl, r.timestamp, r.submitter);
    }

    function totalRecords() external view returns (uint256) {
        return records.length;
    }

    /// @notice Re-verify: check whether given (faceHash, postHash) matches what's on-chain for id.
    function verify(uint256 id, bytes32 faceHash, bytes32 postHash) external view returns (bool) {
        Record storage r = records[id];
        return r.faceHash == faceHash && r.postHash == postHash;
    }
}
