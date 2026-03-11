// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract StreetLight {
    enum Status {
        VERIFIED,
        RESOLVED
    }
    enum VerificationType {
        AUTO,
        MANUAL
    }
    struct complaint {
        uint256 complaintId;
        bytes32 imageHash;
        string issueType;
        bytes32 locationHash;
        uint256 timestamp;
        VerificationType verificationType;
        Status status;
    }

    event ComplainVerification(uint256 complaintID, bytes32 imagehash, string issueType, uint256 timestamp, Status s);
    event ComplainResolved(uint256 complaintID, bytes32 imagehash, string issueType, uint256 timestamp, Status s);
}
