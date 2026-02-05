// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertiChainMaster {
    address public universityAdmin;

    struct Certificate {
        string studentName;
        string studentID;
        string email; // Pudhu Feature
        string department; // Pudhu Feature
        string passingYear; // Pudhu Feature
        string pixelHash; // Digital Fingerprint (SHA-256)
        uint256 issueDate;
        bool exists;
    }

    // Student ID-ah key-ah vachi details-ah save panna mapping
    mapping(string => Certificate) private certificates;

    // Security: Admin mattum thān issue panna mudiyum
    modifier onlyAdmin() {
        require(
            msg.sender == universityAdmin,
            "Unauthorized: Only Admin can issue certificates."
        );
        _;
    }

    constructor() {
        universityAdmin = msg.sender; // Contract deploy pandravanga thān Admin
    }

    // 1. ISSUE CERTIFICATE (Admin Mattum)
    function initiateCertificate(
        string memory _id,
        string memory _name,
        string memory _email,
        string memory _dept,
        string memory _year,
        string memory _pHash
    ) public onlyAdmin {
        require(
            !certificates[_id].exists,
            "Error: Certificate ID already exists!"
        );

        certificates[_id] = Certificate({
            studentName: _name,
            studentID: _id,
            email: _email,
            department: _dept,
            passingYear: _year,
            pixelHash: _pHash,
            issueDate: block.timestamp,
            exists: true
        });
    }

    // 2. VERIFY INTEGRITY (Yār vēnum nālum check pannalām)
    // Intha function-ah use panni thān namma Fake vs Original kandupudikkirom
    function verifyIntegrity(
        string memory _id,
        string memory _inputHash
    ) public view returns (bool, string memory) {
        if (!certificates[_id].exists) {
            return (
                false,
                "Not Found: Certificate record doesn't exist in Blockchain."
            );
        }

        // Blockchain-la irukura hash-um, ippo upload panna image hash-um match aagudhā?
        bool isMatch = (keccak256(
            abi.encodePacked(certificates[_id].pixelHash)
        ) == keccak256(abi.encodePacked(_inputHash)));

        if (isMatch) {
            return (true, "Verified: This is a Genuine Certificate.");
        } else {
            return (
                false,
                "Alert: Pixel Mismatch! This document might be tampered."
            );
        }
    }

    // 3. GET FULL DETAILS (Verification appo display panna)
    function getCertificateDetails(
        string memory _id
    )
        public
        view
        returns (
            string memory name,
            string memory email,
            string memory dept,
            string memory year,
            uint256 date
        )
    {
        require(certificates[_id].exists, "Certificate not found.");
        Certificate memory c = certificates[_id];
        return (
            c.studentName,
            c.email,
            c.department,
            c.passingYear,
            c.issueDate
        );
    }
}


