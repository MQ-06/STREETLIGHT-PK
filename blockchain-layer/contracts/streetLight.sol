// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";

contract StreetLight is Ownable {
    constructor() Ownable(msg.sender) {}

    uint256 public TotalComplaints;

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
        uint8 issueType;
        uint256 timestamp;
        bytes32 locationHash;
        VerificationType verificationType;
        Status status;
    }

    mapping(uint256 => Complaint) public complaints;

    event ComplainVerified(
        uint256 indexed complaintID,
        bytes32 imagehash,
        uint8 issueType,
        uint256 timestamp,
        Status s
    );
    event ComplainResolved(
        uint256 indexed complaintID,
        bytes32 imagehash,
        uint8 issueType,
        uint256 timestamp
    );

    function registerComplaint(
        uint256 complaintID,
        bytes32 imagehash,
        uint8 issueType, //Will use category-num like 1-pothole 2-garbage
        bytes32 locationHash,
        VerificationType v
    ) public onlyOwner {
        require(
            complaints[complaintID].complaintId == 0,
            "Complaint already exists"
        );
        complaints[complaintID] = Complaint({
            complaintId: complaintID,
            imageHash: imagehash,
            locationHash: locationHash,
            issueType: issueType,
            timestamp: block.timestamp,
            verificationType: v,
            status: Status.VERIFIED
        });
        TotalComplaints++;

        emit ComplainVerified(
            complaintID,
            imagehash,
            issueType,
            block.timestamp,
            Status.VERIFIED
        );
    }

    function GetComplaint(
        uint256 ComplaintID
    ) public view returns (Complaint memory c) {
        require(
            complaints[ComplaintID].complaintId != 0,
            "Complaint does not exist"
        );
        return complaints[ComplaintID];
    }

    function markResolved(uint256 complaintID) public onlyOwner {
        require(
            complaints[complaintID].complaintId != 0,
            "Complaint does not exist"
        );
        require(
            complaints[complaintID].status != Status.RESOLVED,
            "Already resolved"
        );
        complaints[complaintID].status = Status.RESOLVED;

        emit ComplainResolved(
            complaintID,
            complaints[complaintID].imageHash,
            complaints[complaintID].issueType,
            block.timestamp
        );
    }

    function GetComplaintHash(
        uint256 complainID
    ) public view returns (bytes32 complainHash) {
        require(
            complaints[complainID].complaintId != 0,
            "Complaint does not exist"
        );
        return complaints[complainID].imageHash;
    }
    function getTotalComplaints() public view returns (uint256) {
        return TotalComplaints;
    }
}
