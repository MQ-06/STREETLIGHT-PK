// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title StreetLight - Civic Issue Accountability Contract
 * @notice Records verified civic complaints permanently on-chain
 * @dev Only backend (owner) can write. Anyone can read/verify.
 *
 * Flow:
 *   User submits report → AI verifies → Backend calls registerComplaint()
 *   Municipality fixes  → Backend calls markResolved()
 */
contract StreetLight is Ownable {

    // STATE VARIABLES
    uint256 public totalComplaints;
    uint256 public totalResolved;

    // ENUMS
    enum Status {
        VERIFIED,   // 0 — Verified, pending resolution
        RESOLVED    // 1 — Issue fixed by municipality
    }

    enum VerificationType {
        AUTO,       // 0 — AI auto-verified (score >= 85)
        OFFICER     // 1 — Manually approved by officer (score 60-84)
    }

    enum IssueCategory {
        POTHOLE,    // 0
        GARBAGE,    // 1
        OTHER       // 2
    }

    // STRUCTS
   
    struct Complaint {
        uint256 complaintId;            // Same as DB complaint ID
        bytes32 imageHash;              // SHA256 hash of image (privacy)
        IssueCategory issueCategory;    // pothole / garbage / other
        uint256 verifiedAt;             // Block timestamp of verification
        uint256 resolvedAt;             // Block timestamp of resolution (0 if not resolved)
        bytes32 locationHash;           // Approximate location hash (privacy)
        VerificationType verificationType; // auto / officer
        Status status;                  // VERIFIED / RESOLVED
        uint8 aiScore;                  // AI confidence score (0-100)
        uint8 finalScore;               // Final weighted score (0-100)
        bool exists;                    // Existence check (safer than ID==0)
    }

    // MAPPINGS

    mapping(uint256 => Complaint) private complaints;

    // EVENTS
   
    /**
     * @notice Emitted when a complaint is verified and recorded
     * Blockchain Event #1 — per system design doc
     */
    event ComplaintVerified(
        uint256 indexed complaintId,
        bytes32 imageHash,
        IssueCategory issueCategory,
        uint256 timestamp,
        VerificationType verificationType,
        uint8 aiScore,
        uint8 finalScore
    );

    /**
     * @notice Emitted when municipality resolves the issue
     * Blockchain Event #2 — per system design doc
     */
    event ComplaintResolved(
        uint256 indexed complaintId,
        uint256 timestamp,
        string resolutionNote
    );

    // CONSTRUCTOR

    constructor() Ownable(msg.sender) {}

    // WRITE FUNCTIONS (onlyOwner = backend wallet)

    /**
     * @notice Register a verified complaint on-chain
     * @dev Called by backend after score >= 85 (auto) or officer approval (60-84)
     *
     * @param complaintId   Exact same ID as in Supabase DB
     * @param imageHash     SHA256(image_bytes) — NOT the actual image
     * @param issueCategory 0=pothole, 1=garbage, 2=other
     * @param locationHash  keccak256(approx_lat, approx_lon) — privacy preserving
     * @param verificationType 0=auto, 1=officer
     * @param aiScore       AI engine confidence score (0-100)
     * @param finalScore    Final weighted score (0-100)
     */
    function registerComplaint(
        uint256 complaintId,
        bytes32 imageHash,
        IssueCategory issueCategory,
        bytes32 locationHash,
        VerificationType verificationType,
        uint8 aiScore,
        uint8 finalScore
    ) external onlyOwner {
        require(
            !complaints[complaintId].exists,
            "StreetLight: Complaint already registered"
        );
        require(aiScore <= 100, "StreetLight: aiScore must be 0-100");
        require(finalScore <= 100, "StreetLight: finalScore must be 0-100");

        complaints[complaintId] = Complaint({
            complaintId:      complaintId,
            imageHash:        imageHash,
            issueCategory:    issueCategory,
            verifiedAt:       block.timestamp,
            resolvedAt:       0,
            locationHash:     locationHash,
            verificationType: verificationType,
            status:           Status.VERIFIED,
            aiScore:          aiScore,
            finalScore:       finalScore,
            exists:           true
        });

        totalComplaints++;

        emit ComplaintVerified(
            complaintId,
            imageHash,
            issueCategory,
            block.timestamp,
            verificationType,
            aiScore,
            finalScore
        );
    }

    /**
     * @notice Mark a complaint as resolved by municipality
     * @dev Called by backend when municipal officer marks issue fixed
     *
     * @param complaintId     The complaint to resolve
     * @param resolutionNote  Short note e.g. "Pothole filled on 2026-03-11"
     */
    function markResolved(
        uint256 complaintId,
        string calldata resolutionNote
    ) external onlyOwner {
        require(
            complaints[complaintId].exists,
            "StreetLight: Complaint does not exist"
        );
        require(
            complaints[complaintId].status != Status.RESOLVED,
            "StreetLight: Already resolved"
        );

        complaints[complaintId].status     = Status.RESOLVED;
        complaints[complaintId].resolvedAt = block.timestamp;

        totalResolved++;

        emit ComplaintResolved(
            complaintId,
            block.timestamp,
            resolutionNote
        );
    }

    // READ FUNCTIONS (public — anyone can verify)
    /**
     * @notice Get full complaint details
     * @dev Flutter app uses this to show blockchain proof to user
     */
    function getComplaint(
        uint256 complaintId
    ) external view returns (Complaint memory) {
        require(
            complaints[complaintId].exists,
            "StreetLight: Complaint does not exist"
        );
        return complaints[complaintId];
    }

    /**
     * @notice Verify if an image matches the stored hash
     * @dev Flutter calls this for tamper-proof verification
     * @return true if image hash matches on-chain record
     */
    function verifyImageHash(
        uint256 complaintId,
        bytes32 imageHash
    ) external view returns (bool) {
        require(
            complaints[complaintId].exists,
            "StreetLight: Complaint does not exist"
        );
        return complaints[complaintId].imageHash == imageHash;
    }

    /**
     * @notice Check if a complaint exists on-chain
     */
    function complaintExists(
        uint256 complaintId
    ) external view returns (bool) {
        return complaints[complaintId].exists;
    }

    /**
     * @notice Get complaint status
     * @return 0 = VERIFIED, 1 = RESOLVED
     */
    function getStatus(
        uint256 complaintId
    ) external view returns (Status) {
        require(
            complaints[complaintId].exists,
            "StreetLight: Complaint does not exist"
        );
        return complaints[complaintId].status;
    }

    /**
     * @notice Get summary stats
     */
    function getStats() external view returns (
        uint256 total,
        uint256 resolved,
        uint256 pending
    ) {
        return (
            totalComplaints,
            totalResolved,
            totalComplaints - totalResolved
        );
    }
}
