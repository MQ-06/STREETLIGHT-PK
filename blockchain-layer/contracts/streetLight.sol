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
    struct Complaint {
        uint256 complaintId;
        bytes32 imageHash;
        string issueType;
        bytes32 locationHash;
        VerificationType verificationType;
        Status status;
    }

    mapping(uint256 => Complaint) public complaints;

    event ComplainVerified(
        uint256 complaintID,
        bytes32 imagehash,
        string issueType,
        uint256 timestamp,
        Status s
    );
    event ComplainResolved(
        uint256 complaintID,
        bytes32 imagehash,
        string issueType,
        uint256 timestamp,
        Status s
    );

    function registerComplaint(
        uint256 complaintID,
        bytes32 imagehash,
        string memory issueType,
        bytes32 locationHash,
        VerificationType v
    ) public {
        complaints[complaintID] = Complaint(
            complaintID,
            imagehash,
            issueType,
            locationHash,
            v,
            Status.VERIFIED
        );
        emit ComplainVerified(
            complaintID,
            imagehash,
            issueType,
            block.timestamp,
            Status.VERIFIED
        );
    }
}
