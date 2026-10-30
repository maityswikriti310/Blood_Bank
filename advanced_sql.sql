USE blood_bank;

DELIMITER $$

CREATE PROCEDURE CountDonors()
BEGIN
    SELECT COUNT(*) AS total_donors
    FROM donor;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE GetRequestsByStatus(
    IN p_status VARCHAR(20)
)
BEGIN
    SELECT *
    FROM blood_request
    WHERE status = p_status;
END $$

DELIMITER ;
DELIMITER $$

CREATE FUNCTION TotalDonors()
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE donor_count INT;

    SELECT COUNT(*) INTO donor_count
    FROM donor;

    RETURN donor_count;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER ValidateRequestInsert
BEFORE INSERT ON blood_request
FOR EACH ROW
BEGIN
    IF NEW.units_needed <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Units needed must be greater than zero';
    END IF;
END $$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER ValidateRequestUpdate
BEFORE UPDATE ON blood_request
FOR EACH ROW
BEGIN
    IF NEW.units_needed <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Units needed must be greater than zero';
    END IF;
END $$

DELIMITER ;

-- Transaction demonstration
START TRANSACTION;

INSERT INTO blood_request
    (patient_name, blood_group, units_needed)
VALUES
    ('Transaction Test', 'O+', 1);

SELECT *
FROM blood_request
WHERE patient_name = 'Transaction Test';

ROLLBACK;